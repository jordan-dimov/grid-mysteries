"""Witness a daily manifest against roots this project does not control.

The same three proofs `scripts/timestamp` writes for a declaration: an
OpenTimestamps proof (Bitcoin-anchored once upgraded) and RFC 3161 tokens
from two authorities. Subprocesses (`openssl`, `ots`) and the HTTP posts
are injected so the orchestration is testable without either.
"""

import hashlib
import json
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from grid_mysteries.capture.fetch import Fetcher
from grid_mysteries.capture.store import ObjectStore

TSAS: Final[tuple[tuple[str, str], ...]] = (
    ("freetsa", "https://freetsa.org/tsr"),
    ("digicert", "http://timestamp.digicert.com"),
)
TIMESTAMP_QUERY: Final = "application/timestamp-query"
Runner = Callable[[list[str]], subprocess.CompletedProcess[bytes]]


def run_checked(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, check=True, capture_output=True)


def witness(
    data: bytes,
    name: str,
    workdir: Path,
    *,
    fetcher: Fetcher,
    run: Runner = run_checked,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, bytes]:
    """Proof files for `data`, keyed by file name (`<name>.tsq`,
    `<name>.<tsa>.tsr`, `<name>.ots`, `<name>.timestamps.json`).

    A TSA that fails is recorded in the sidecar and skipped; a failed
    `ots stamp` likewise. The sidecar lists what succeeded, so a missing
    proof is visible rather than silent.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    target = workdir / name
    target.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    proofs: dict[str, bytes] = {}
    sidecar: dict[str, object] = {
        "file": name,
        "sha256": digest,
        "stamped_at_utc_local_clock": now().isoformat(timespec="seconds"),
        "proofs": [],
        "failures": [],
    }
    query_path = workdir / f"{name}.tsq"
    try:
        run(
            [
                "openssl",
                "ts",
                "-query",
                "-data",
                str(target),
                "-sha256",
                "-cert",
                "-out",
                str(query_path),
            ]
        )
        query = query_path.read_bytes()
        proofs[f"{name}.tsq"] = query
    except Exception as exc:  # noqa: BLE001 - recorded, not hidden
        query = b""
        sidecar["failures"].append(f"openssl ts -query: {type(exc).__name__}: {exc}"[:300])  # type: ignore[attr-defined]
    for tsa, url in TSAS:
        if not query:
            break
        try:
            response = fetcher.get(url, data=query, content_type=TIMESTAMP_QUERY)
            if not response.ok or not response.body:
                raise RuntimeError(f"HTTP {response.status}")
            proofs[f"{name}.{tsa}.tsr"] = response.body
            sidecar["proofs"].append(  # type: ignore[attr-defined]
                {"kind": "rfc3161", "tsa": url, "path": f"{name}.{tsa}.tsr"}
            )
        except Exception as exc:  # noqa: BLE001
            sidecar["failures"].append(f"{tsa}: {type(exc).__name__}: {exc}"[:300])  # type: ignore[attr-defined]
    try:
        run(["ots", "stamp", str(target)])
        proofs[f"{name}.ots"] = (workdir / f"{name}.ots").read_bytes()
        sidecar["proofs"].append(  # type: ignore[attr-defined]
            {"kind": "opentimestamps", "path": f"{name}.ots", "status": "pending until upgraded"}
        )
    except Exception as exc:  # noqa: BLE001
        sidecar["failures"].append(f"ots stamp: {type(exc).__name__}: {exc}"[:300])  # type: ignore[attr-defined]
    proofs[f"{name}.timestamps.json"] = (json.dumps(sidecar, indent=1) + "\n").encode()
    return proofs


def proof_key(name: str) -> str:
    return f"proofs/{name}"


def upload_proofs(store: ObjectStore, proofs: dict[str, bytes]) -> list[str]:
    keys = []
    for name, body in proofs.items():
        key = proof_key(name)
        store.put(key, body, content_type="application/octet-stream")
        keys.append(key)
    return keys
