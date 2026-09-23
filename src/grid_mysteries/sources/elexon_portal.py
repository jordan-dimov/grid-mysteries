"""Elexon Portal P114 downloads (S0142 settlement reports).

The Portal authenticates by a scripting key in the query string. The key is
read from ``ELEXON_PORTAL_KEY`` at request time and never enters a URL that
is journalled, printed or raised: journals record the key-free identity URL
this module builds, and errors are re-raised with the key redacted.

Licence: P114 data is under the BSC Open Data and Public Data licences;
analysis derived from it may be published, raw files may not be republished.
Raw bytes stay under ``data/raw/`` (gitignored); only digests are committed.
"""

import os
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

import httpx

from grid_mysteries.hashing import sha256_file
from grid_mysteries.models import SourceArtifact

BASE = "https://downloads.elexonportal.co.uk/p114"
KEY_ENV = "ELEXON_PORTAL_KEY"
SOURCE = "elexon-portal"


def list_url(publish_date: str, file_filter: str = "s0142") -> str:
    """Key-free identity of a listing: files published on ``publish_date``."""
    return f"{BASE}/list?{urlencode({'date': publish_date, 'filter': file_filter})}"


def download_url(filename: str) -> str:
    """Key-free identity of one file."""
    return f"{BASE}/download?{urlencode({'filename': filename})}"


def with_key(identity_url: str, key: str) -> str:
    return f"{identity_url}&{urlencode({'key': key})}"


def redact(text: str, key: str) -> str:
    return text.replace(key, "<ELEXON_PORTAL_KEY>") if key else text


def fetch(
    *,
    url: str,
    destination: Path,
    dataset: str,
    attempts: int = 3,
    retry_delay_seconds: float = 5.0,
    timeout_seconds: float = 300.0,
) -> SourceArtifact:
    """Pin one Portal artefact at ``destination``; ``url`` is the key-free identity.

    A pinned artefact is never overwritten. A body that is not what was
    asked for (the Portal answers some errors with HTTP 200 and a short text
    such as "Scripting Error 001") is refused rather than pinned: a download
    must be gzip, a listing must be JSON."""
    if destination.exists():
        raise FileExistsError(
            f"pinned artefact already exists, refusing to overwrite: {destination}"
        )
    key = os.environ.get(KEY_ENV, "")
    if not key:
        raise SystemExit(f"{KEY_ENV} is not set")
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
                response = client.get(with_key(url, key))
                response.raise_for_status()
            body = response.content
            if "/download?" in url and not body.startswith(b"\x1f\x8b"):
                raise ValueError(f"not gzip: {body[:80]!r}")
            if "/list?" in url and not body.lstrip().startswith((b"{", b"[")):
                raise ValueError(f"not JSON: {body[:80]!r}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
            return SourceArtifact(
                source=SOURCE,
                dataset=dataset,
                path=destination,
                sha256=sha256_file(destination),
                fetched_at=datetime.now(UTC),
            )
        except (httpx.TransportError, httpx.HTTPStatusError, ValueError) as error:
            last = error
            if isinstance(error, httpx.HTTPStatusError) and error.response.status_code < 500:
                break
            if attempt < attempts - 1:
                time.sleep(retry_delay_seconds * (attempt + 1))
    raise RuntimeError(redact(f"failed to fetch {url}: {last}", key)) from None
