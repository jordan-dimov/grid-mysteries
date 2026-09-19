"""OpenTimestamps proofs: read their state, upgrade them, check them against
Bitcoin block headers from explorers this project does not run.

A proof is issued pending: calendars promise to anchor the digest in a
Bitcoin block. Until upgraded, the proof depends on those calendars keeping
the promise; upgraded, it depends only on the chain. `sweep` upgrades every
pending proof it is given and keeps an upgrade only when each new block's
Merkle root, as the proof computes it, is what two independent explorers
report for that height. A proof still pending after `MAX_PENDING` is a
fault: calendars normally complete within hours (the 2026-09-15 manifest's
proof was anchored in blocks 967193-967211 when first upgraded on
2026-09-19).

Issued proofs are replaced in place, as `scripts/timestamp --upgrade` always
did, so standard tooling (`ots verify <file>.ots`) keeps working. The
archive's copies stay as issued; `is_upgrade_of` lets the watchdog tell a
local upgrade from a divergence. The proof's own digest must match its
sidecar, so an upgrade can never swap in a proof for other bytes.
"""

import json
import shutil
import subprocess
import tempfile
import urllib.request
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final, Literal

MAX_PENDING: Final = timedelta(hours=48)
EXPLORERS: Final = {
    "blockstream": "https://blockstream.info/api",
    "mempool": "https://mempool.space/api",
}

#: height -> Merkle root (display hex), as one explorer reports it.
MerkleRoot = Callable[[int], str]
#: pending proof bytes -> the bytes after `ots upgrade`.
Upgrader = Callable[[bytes], bytes]


@dataclass(frozen=True)
class Proof:
    digest: str
    #: (block height, Merkle root in display hex) per Bitcoin attestation.
    anchors: tuple[tuple[int, str], ...]

    @property
    def complete(self) -> bool:
        return bool(self.anchors)


def read(ots: bytes) -> Proof:
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
    from opentimestamps.core.serialize import BytesDeserializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    detached = DetachedTimestampFile.deserialize(BytesDeserializationContext(ots))
    anchors = sorted(
        {
            (att.height, msg[::-1].hex())
            for msg, att in detached.timestamp.all_attestations()
            if isinstance(att, BitcoinBlockHeaderAttestation)
        }
    )
    return Proof(detached.file_digest.hex(), tuple(anchors))


def is_upgrade_of(local: bytes, issued: bytes) -> bool:
    """`local` is `issued` upgraded: same digest, Bitcoin-anchored where
    the issued proof was still pending. Anything else is a divergence."""
    try:
        mine, theirs = read(local), read(issued)
    except Exception:  # noqa: BLE001 - an unreadable proof is not an upgrade
        return False
    return mine.digest == theirs.digest and mine.complete and not theirs.complete


Verdict = Literal["confirmed", "contradicted", "unavailable"]


def confirm(proof: Proof, explorers: dict[str, MerkleRoot]) -> tuple[Verdict, str]:
    """Every anchor's Merkle root must be what every explorer reports for its
    height. One disagreement is `contradicted` (a fault: the proof or an
    explorer is wrong); an explorer that cannot be reached is `unavailable`
    (try again later)."""
    if not proof.complete:
        return "unavailable", "no Bitcoin attestation yet"
    missing = []
    for height, root in proof.anchors:
        for name, merkle_root in explorers.items():
            try:
                reported = merkle_root(height)
            except Exception as exc:  # noqa: BLE001 - recorded, retried next sweep
                missing.append(f"{name}@{height}: {type(exc).__name__}")
                continue
            if reported != root:
                return "contradicted", f"{name} reports {reported} at {height}, proof has {root}"
    if missing:
        return "unavailable", "; ".join(missing)
    heights = ", ".join(str(h) for h, _ in proof.anchors)
    return "confirmed", f"blocks {heights} confirmed by {', '.join(explorers)}"


@dataclass
class Line:
    path: Path
    ok: bool
    detail: str
    changed: bool = False


def sweep(
    proofs: Iterable[Path],
    *,
    upgrade: Upgrader,
    explorers: dict[str, MerkleRoot],
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    max_pending: timedelta = MAX_PENDING,
    verify_all: bool = False,
) -> list[Line]:
    """Upgrade each pending `<file>.ots` in place when the upgrade confirms;
    report a proof that stays pending past `max_pending` (from its sidecar's
    stamp time) as a fault. With `verify_all`, complete proofs are
    re-confirmed against the explorers too."""
    lines = []
    for path in proofs:
        sidecar = json.loads(
            path.with_name(path.name[: -len(".ots")] + ".timestamps.json").read_text()
        )
        body = path.read_bytes()
        proof = read(body)
        if proof.digest != sidecar["sha256"]:
            lines.append(Line(path, False, f"proof digest {proof.digest} is not the sidecar's"))
            continue
        if proof.complete:
            if verify_all:
                verdict, detail = confirm(proof, explorers)
                lines.append(Line(path, verdict == "confirmed", f"{verdict}: {detail}"))
            continue
        try:
            upgraded = read(new := upgrade(body))
        except Exception as exc:  # noqa: BLE001 - a failed upgrade is a pending proof
            upgraded, detail = proof, f"upgrade failed: {type(exc).__name__}: {exc}"[:300]
        else:
            detail = "calendars have not anchored it yet"
        if upgraded.complete:
            if upgraded.digest != proof.digest:
                lines.append(Line(path, False, "upgrade changed the proof's digest; not kept"))
                continue
            verdict, detail = confirm(upgraded, explorers)
            if verdict == "confirmed":
                path.write_bytes(new)
                lines.append(Line(path, True, f"upgraded: {detail}", changed=True))
                continue
            if verdict == "contradicted":
                lines.append(Line(path, False, f"upgrade not kept, {verdict}: {detail}"))
                continue
            detail = f"upgrade held, explorers {verdict}: {detail}"
        stamped = datetime.fromisoformat(
            sidecar["stamped_at_utc_local_clock"].replace("Z", "+00:00")
        )
        age = now() - stamped
        stale = age > max_pending
        lines.append(
            Line(
                path,
                not stale,
                f"pending {age.total_seconds() / 3600:.0f} h"
                + (f" (over {max_pending.total_seconds() / 3600:.0f} h)" if stale else "")
                + f"; {detail}",
            )
        )
    return lines


def ots_upgrade(body: bytes) -> bytes:
    """Run `ots upgrade` on a scratch copy; the repository file is only
    written by `sweep`, after the upgrade confirms."""
    ots = shutil.which("ots")
    if ots is None:
        raise RuntimeError("ots not on PATH (uv sync --group capture)")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "proof.ots"
        path.write_bytes(body)
        subprocess.run([ots, "upgrade", str(path)], check=False, capture_output=True, timeout=120)
        return path.read_bytes()


def explorer(base: str, *, timeout: float = 20) -> MerkleRoot:
    """Merkle root at a height from an Esplora-style API (block-height, then block)."""
    cache: dict[int, str] = {}

    def get(url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": "grid-mysteries-proofs"})
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.read()

    def merkle_root(height: int) -> str:
        if height not in cache:
            block = get(f"{base}/block-height/{height}").decode().strip()
            cache[height] = json.loads(get(f"{base}/block/{block}"))["merkle_root"]
        return cache[height]

    return merkle_root
