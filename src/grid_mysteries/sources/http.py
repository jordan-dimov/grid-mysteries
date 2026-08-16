from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import httpx

from grid_mysteries.hashing import sha256_file
from grid_mysteries.models import SourceArtifact


def fetch_artifact(
    *,
    url: str,
    destination: Path,
    source: str,
    dataset: str,
    timeout_seconds: float = 30.0,
) -> SourceArtifact:
    """Fetch one immutable public artefact (JSON, CSV, any bytes) and return its content address.

    Dataset-specific adapters should construct the URL and validate semantics.
    This low-level function deliberately knows nothing about Elexon or NESO.

    A pinned artefact is immutable: an existing destination is never
    overwritten, because the same URL can legitimately serve a revised
    vintage later (e.g. a newer settlement run). A deliberately acquired
    later vintage belongs at a new path, recorded as a new artefact.
    """
    if destination.exists():
        raise FileExistsError(
            f"pinned artefact already exists, refusing to overwrite: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        destination.write_bytes(response.content)

    return SourceArtifact(
        source=source,
        dataset=dataset,
        path=destination,
        sha256=sha256_file(destination),
        fetched_at=datetime.now(UTC),
    )
