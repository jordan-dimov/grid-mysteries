from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import httpx

from grid_mysteries.hashing import sha256_file
from grid_mysteries.models import SourceArtifact


def fetch_json(
    *,
    url: str,
    destination: Path,
    source: str,
    dataset: str,
    timeout_seconds: float = 30.0,
) -> SourceArtifact:
    """Fetch one immutable public JSON artefact and return its content address.

    Dataset-specific adapters should construct the URL and validate semantics.
    This low-level function deliberately knows nothing about Elexon or NESO.
    """
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
