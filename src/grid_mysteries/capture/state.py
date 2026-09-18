"""Instrument state in the archive: the pinned artefacts and journals an
unattended runner produces, kept under `state/<instrument>/<repo-relative
path>` so the laptop can sync them into the repository.

`push` uploads every file under the given repository paths that the bucket
does not already hold with the same bytes; `pull` downloads the instrument's
state into the repository. Files that only grow (journals, regenerated
manifests) may be replaced by a longer version that starts with the local
bytes; anything else that differs is reported, never overwritten, unless
the caller says the archive wins (`overwrite=True`). The laptop never says
so: a difference there means the repository and the archive have diverged
and a person should look. The unattended job always says so: its working
copy is the Docker image's snapshot of the repository at build time, which
is stale the moment the job's previous run has pushed state, and refusing
to replace it fails the job on every run after the first (tracker-013,
2026-09-18 09:00 UTC). The runner's own idempotency (verify pinned bytes
against the journal, skip) then makes acquisition resumable from any machine.
"""

import fnmatch
import hashlib
from pathlib import Path

from grid_mysteries.capture.store import ObjectStore


def state_key(instrument: str, relative: str) -> str:
    return f"state/{instrument}/{relative}"


def _same(store: ObjectStore, key: str, body: bytes) -> bool:
    existing = store.get(key)
    return (
        existing is not None and hashlib.sha256(existing).digest() == hashlib.sha256(body).digest()
    )


def push(
    store: ObjectStore,
    repo_root: Path,
    instrument: str,
    paths: list[Path],
    *,
    include: list[str] | None = None,
) -> list[str]:
    """Upload files under `paths` (repo-relative) into the instrument's state.

    `include` restricts uploads to file names matching one of the glob
    patterns, so a computed file such as an instrument's `tracker.json`
    (which the laptop recomputes and commits) is never pushed as if it were
    acquisition state."""
    uploaded = []
    for base in paths:
        root = repo_root / base
        if not root.exists():
            continue
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for path in files:
            if include and not any(fnmatch.fnmatch(path.name, pattern) for pattern in include):
                continue
            relative = path.relative_to(repo_root).as_posix()
            key = state_key(instrument, relative)
            body = path.read_bytes()
            if _same(store, key, body):
                continue
            store.put(key, body)
            uploaded.append(key)
    return uploaded


def pull(
    store: ObjectStore, repo_root: Path, instrument: str, *, overwrite: bool = False
) -> list[str]:
    """Download the instrument's state into the repository; growth-only
    replacement, and a report line for anything that differs otherwise.
    With `overwrite`, a differing local file is replaced by the archive's and
    reported as `replaced` rather than `MISMATCH`."""
    prefix = f"state/{instrument}/"
    report = []
    for key in store.keys(prefix):
        relative = key[len(prefix) :]
        target = repo_root / relative
        body = store.get(key)
        if body is None:
            continue
        if target.exists():
            local = target.read_bytes()
            if local == body:
                continue
            if body.startswith(local):
                target.write_bytes(body)
                report.append(f"grew {key} -> {target}")
                continue
            if overwrite:
                target.write_bytes(body)
                report.append(f"replaced {key} -> {target}")
                continue
            report.append(f"MISMATCH {key} -> {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        report.append(f"{key} -> {target}")
    return report
