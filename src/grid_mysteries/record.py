"""What every record engine shares.

A record engine (`tec/`, `bill/`) holds one governed record in its own
Morpholog database under its own signing key. This module is the part
of an engine that is the same for each: the client pinned to the
engine's programme, the transact guarded by a recovery marker, the
signed and witnessed checkpoint with its anchor file, the exported pack
verified offline against that anchor, and a streaming reader for the
pack. An engine keeps only what is its own: the pure plan over its
state, and the commands that read its record back.

The recovery marker is the safety of the whole thing. It is written
before a transact and cleared only on a positive non-commit: a
rejection, or an error whose stable `code` the runtime documents as
"nothing was recorded" (the generated client raises exactly those as
``MorphologRequestError``). An unknown outcome, including a binary
killed after COMMIT, keeps the marker, and the next run refuses until
someone has read the record and removed it by hand.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from grid_mysteries.capture.timestamp import TSAS
from grid_mysteries.corpus import REPO_ROOT

if TYPE_CHECKING:
    from morpholog_client.adapter import Morpholog

#: The one timestamp authority that countersigns an engine's checkpoints,
#: and the root its tokens are judged against.
DIGICERT: Final = "rfc3161:" + dict(TSAS)["digicert"]
DIGICERT_ROOT: Final = REPO_ROOT / "trust" / "tsa" / "digicert-trusted-root-g4.pem"


@dataclass(frozen=True)
class Record:
    """One engine's identity. Every path and environment variable follows
    from the name and the key id, so a third engine is one line."""

    name: str
    programme: Path  # relative to the repository root
    actor: str
    key_id: str  # `<name>-<year>`

    def url(self) -> str:
        return os.environ.get(
            f"{self.name.upper()}_DATABASE_URL", f"postgres:///grid_mysteries_{self.name}"
        )

    @property
    def signing_key(self) -> Path:
        name, year = self.key_id.rsplit("-", 1)
        default = Path.home() / ".config" / "grid-mysteries" / f"{name}-signing-{year}.pem"
        return Path(os.environ.get(f"{self.name.upper()}_SIGNING_KEY", str(default)))

    @property
    def public_key(self) -> Path:
        return REPO_ROOT / self.name / "trust" / f"{self.key_id}.pub"

    @property
    def anchors(self) -> Path:
        return REPO_ROOT / self.name / "anchors"

    @property
    def packs(self) -> Path:
        return REPO_ROOT / "data" / "derived" / self.name / "packs"

    @property
    def marker_dir(self) -> Path:
        return Path("data") / "derived" / self.name

    def act(self, transformation: str, **args: object) -> dict[str, Any]:
        return {"transformation": transformation, "actor": self.actor, "args_named": args}

    def client(self, repo_root: Path, database_url: str) -> Morpholog:
        """A client that refuses, before its first call, a binary of another
        version than the vendored client was generated for, or a programme
        file whose hash is not the pinned one (`PROGRAMME_HASH.json` beside
        the programme). The pin that CI checks is then also the pin that
        holds when the laptop writes to the record."""
        from morpholog_client import MORPHOLOG_VERSION
        from morpholog_client.adapter import Morpholog

        pin = repo_root / self.programme.parent / "PROGRAMME_HASH.json"
        return Morpholog(
            str(repo_root / self.programme),
            database_url,
            expected_version=MORPHOLOG_VERSION,
            expected_model_hash=json.loads(pin.read_text())["hash"],
        )


def run(*args: str) -> subprocess.CompletedProcess[str]:
    """The `morpholog` on PATH, for the two commands whose exact stdout is
    the artefact (a checkpoint, a verify report)."""
    return subprocess.run(["morpholog", *args], capture_output=True, text=True)


# ------------------------------------------------------------ the transact


class ImportError_(RuntimeError):
    pass


@dataclass
class Outcome:
    status: str  # committed | not-committed | unknown
    detail: str = ""
    transition_ids: list[str] = field(default_factory=list)


def classify(result: object, error: BaseException | None) -> Outcome:
    """committed / not-committed / unknown, from a transact's result or error.

    The generated client raises ``MorphologRequestError`` only for the
    codes the runtime publishes as "nothing was recorded"
    (``envelopes.NOTHING_RECORDED_CODES``); that set is read from the
    client, never copied here. Anything else is unknown."""
    from morpholog_client import envelopes
    from morpholog_client.adapter import MorphologRequestError

    if error is None:
        if isinstance(result, envelopes.AtomicCommitted):
            return Outcome("committed", "", [a.outcome.transition_id for a in result.acts])
        if isinstance(result, envelopes.AtomicRejected):
            return Outcome("not-committed", f"act {result.act} refused [{result.rule}]")
        return Outcome("unknown", f"unrecognised result {result!r}"[:300])
    if isinstance(error, MorphologRequestError) and error.code in envelopes.NOTHING_RECORDED_CODES:
        return Outcome("not-committed", f"{error.code}: {error.error}"[:300])
    return Outcome("unknown", f"{type(error).__name__}: {error}"[:300])


def marker_path(repo_root: Path, record: Record, database_url: str) -> Path:
    """One marker per database, so a test or rehearsal database can never
    block, or be unblocked by, the live record's imports. Credentials are
    left out of the hash, so a changed password does not orphan a marker."""
    name = database_url.rsplit("/", 1)[-1].split("?")[0] or "default"
    ident = hashlib.sha256(database_url.split("@")[-1].encode()).hexdigest()[:12]
    return repo_root / record.marker_dir / f".import-recovery.{name}.{ident}"


def refuse_if_marked(marker: Path, read_back: str) -> None:
    if marker.exists():
        raise ImportError_(
            f"recovery marker {marker} exists: a previous run's outcome is unknown. "
            f"Read the record ({read_back}) and remove the marker by hand."
        )


def guarded_transact(
    api: Any, marker: Path, label: str, acts: list[dict[str, Any]], note: dict[str, Any]
) -> Outcome:
    """One transact under the recovery marker. Returns the committed outcome;
    raises ``ImportError_`` otherwise, clearing the marker only when the
    record is known unchanged."""
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({**note, "acts": len(acts)}) + "\n")
    result: object = None
    error: BaseException | None = None
    try:
        result = api.transact(acts)
    except Exception as exc:  # noqa: BLE001 - classified below
        error = exc
    outcome = classify(result, error)
    if outcome.status == "not-committed":
        marker.unlink()
        raise ImportError_(f"{label} was not committed ({outcome.detail}); record unchanged")
    if outcome.status != "committed":
        raise ImportError_(
            f"{label}: commit outcome UNKNOWN ({outcome.detail}); marker left at {marker}"
        )
    marker.unlink()
    return outcome


# ------------------------------------------------------ checkpoint and pack


def checkpoint_and_export(
    record: Record, database_url: str, *, witness: bool
) -> tuple[Path, dict[str, Any], Path]:
    """Sign a checkpoint over the record's head (DigiCert countersigns it
    with `witness`), keep the anchor under the engine's anchors directory,
    then export the complete pack at that tree size and verify it against
    the anchor. Returns (anchor path, anchor, pack).

    The checkpoint call is raw on purpose: the anchor file is the binary's
    exact bytes, and a failed witness is a nonzero exit with the recorded
    checkpoint still on stdout. The pack is exported either way, so the
    retry only has to witness."""
    argv = ["audit", "checkpoint", "--database-url", database_url]
    argv += ["--signing-key", str(record.signing_key), "--key-id", record.key_id]
    if witness:
        argv += ["--witness", DIGICERT]
    proc = run(*argv)
    if not proc.stdout.strip():
        raise SystemExit(f"checkpoint failed:\n{proc.stderr}")
    anchor = json.loads(proc.stdout)
    path = record.anchors / f"tree-{anchor['tree_size']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    # An unwitnessed head never overwrites a witnessed anchor of the same size.
    if not path.exists() or "witnesses" in anchor:
        path.write_text(proc.stdout if proc.stdout.endswith("\n") else proc.stdout + "\n")
    print(f"anchor {path.relative_to(REPO_ROOT)} ({anchor.get('status', 'witnessed')})")
    anchor = json.loads(path.read_text())
    pack = exported_pack(record, database_url, path, anchor)
    if proc.returncode != 0:
        raise SystemExit(
            "a timestamp authority failed; the checkpoint is recorded. Retry with\n"
            f"  morpholog audit witness --database-url {database_url} "
            f"--tree-size {anchor['tree_size']} --witness {DIGICERT} "
            f"> {path.relative_to(REPO_ROOT)}"
        )
    return path, anchor, pack


def exported_pack(
    record: Record, database_url: str, anchor_path: Path, anchor: dict[str, Any]
) -> Path:
    """The complete pack at the anchor's tree size, exported once and kept,
    verified offline against the anchor with the pinned key and the DigiCert
    root every time it is asked for."""
    from morpholog_client import envelopes

    tree = int(anchor["tree_size"])
    pack = record.packs / f"tree-{tree}.ndjson"
    api = record.client(REPO_ROOT, database_url)
    if not pack.exists():
        pack.parent.mkdir(parents=True, exist_ok=True)
        manifest = api.audit_export(str(pack), tree_size=tree)
        if manifest.tree_size != tree:
            raise SystemExit(
                f"exported a pack of {manifest.tree_size} rows, the anchor says {tree}"
            )
    report = api.audit_verify_pack(
        str(pack),
        anchor_file=str(anchor_path),
        require_signing_key=str(record.public_key),
        trusted_tsa_file=str(DIGICERT_ROOT),
    )
    invalid = [
        w.submitted_to
        for c in (report.witnesses.checkpoints if report.witnesses else [])
        for w in c.witnesses
        if w.status == "invalid"
    ]
    if not isinstance(report.verdict, envelopes.TreeIntact) or invalid:
        raise SystemExit(
            f"the pack does not verify against {anchor_path.name}: {report.verdict!r}"
            + (f"; invalid witness from {', '.join(invalid)}" if invalid else "")
        )
    return pack


class PackError(RuntimeError):
    pass


def pack_rows(pack_path: Path) -> Iterator[dict[str, Any]]:
    """The audit rows of a complete-prefix pack (Morpholog pack format 4: a
    manifest line, `checkpoint_count` checkpoint lines, then one row per
    line), streamed in log order. The row count is checked against the
    manifest once the stream is exhausted."""
    from morpholog_client import envelopes

    with pack_path.open() as handle:
        manifest = envelopes.PrefixPackManifest.from_json(json.loads(handle.readline()))
        lines = (line for line in handle if line.strip())
        for _ in range(manifest.checkpoint_count):
            next(lines)
        count = 0
        for line in lines:
            count += 1
            yield json.loads(line)
    if count != manifest.tree_size:
        raise PackError(f"pack holds {count} rows, its manifest says {manifest.tree_size}")
