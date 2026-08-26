"""Journalled, restart-safe pinning of immutable source artefacts.

Every successful fetch is journalled immediately (NDJSON, one line per
artefact) so a partial run loses nothing. On resume, an existing
destination is verified against its journalled digest and skipped —
never refetched, never overwritten. The manifest is derived from the
journal, not rebuilt from scratch.
"""

import json
import time
from collections.abc import Callable, Iterable
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.hashing import sha256_file
from grid_mysteries.models import SourceArtifact


def progress(relative_path: str) -> None:
    """The per-artefact progress line fetch scripts print."""
    print(f"pinned {relative_path}", flush=True)


def load_journal(journal_path: Path) -> dict[str, dict]:
    if not journal_path.exists():
        return {}
    entries = [json.loads(line) for line in journal_path.read_text().splitlines() if line.strip()]
    return {entry["path"]: entry for entry in entries}


def fetch_journalled(
    jobs: Iterable[tuple[str, str, Path]],
    *,
    journal_path: Path,
    manifest_path: Path,
    repo_root: Path,
    fetch: Callable[..., SourceArtifact],
    sleep_seconds: float = 0.1,
    progress: Callable[[str], None] | None = None,
) -> tuple[int, int]:
    """Pin every (dataset, url, destination) job; return (fetched, skipped)."""
    journal_path.parent.mkdir(parents=True, exist_ok=True)
    journal = load_journal(journal_path)
    fetched = skipped = 0
    with journal_path.open("a") as journal_out:
        for dataset, url, destination in jobs:
            relative_path = str(destination.relative_to(repo_root))
            if destination.exists():
                entry = journal.get(relative_path)
                if entry is None:
                    raise RuntimeError(
                        f"{relative_path} exists but is not journalled; refusing to touch"
                    )
                if sha256_file(destination) != entry["sha256"]:
                    raise RuntimeError(f"{relative_path} no longer matches its journalled digest")
                skipped += 1
                continue
            artefact = fetch(url=url, destination=destination, dataset=dataset)
            entry = {
                "source": artefact.source,
                "dataset": dataset,
                "url": url,
                "path": relative_path,
                "sha256": artefact.sha256,
                "fetched_at": artefact.fetched_at.isoformat(),
                "bytes": destination.stat().st_size,
            }
            journal_out.write(json.dumps(entry) + "\n")
            journal_out.flush()
            journal[relative_path] = entry
            fetched += 1
            if progress is not None:
                progress(relative_path)
            if sleep_seconds:
                time.sleep(sleep_seconds)

    manifest = sorted(journal.values(), key=lambda entry: entry["path"])
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")
    return fetched, skipped


def pin(
    jobs: Iterable[tuple[str, str, Path]],
    *,
    journal_path: Path,
    manifest_path: Path,
    fetch: Callable[..., SourceArtifact],
    label: str | None = None,
    sleep_seconds: float = 0.1,
    progress: Callable[[str], None] | None = None,
) -> tuple[int, int]:
    """`fetch_journalled` against the repository root, with the summary an
    acquisition script prints once the batch is pinned."""
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=journal_path,
        manifest_path=manifest_path,
        repo_root=REPO_ROOT,
        fetch=fetch,
        sleep_seconds=sleep_seconds,
        progress=progress,
    )
    prefix = f"{label}: " if label else ""
    print(f"{prefix}fetched {fetched}, verified and skipped {skipped}", flush=True)
    return fetched, skipped
