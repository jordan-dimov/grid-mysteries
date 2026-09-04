"""Pinning of public rules documents (Ofgem, NESO, Elexon, Grid Code pages
and PDFs) as immutable bytes.

A document is evidence of what a rule said at fetch time; nothing here
parses it. Quotation happens by hand in the investigation's write-up,
beside the digest recorded at the pin.
"""

from pathlib import Path

import httpx

from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

SOURCE = "public-document"


def fetch_pinned(*, url: str, destination: Path, dataset: str) -> SourceArtifact:
    return fetch_artifact(url=url, destination=destination, source=SOURCE, dataset=dataset)


def suffix_for(url: str, content_type: str | None = None) -> str:
    """File suffix from the URL's own extension, else the served content
    type (NESO's ``/document/<id>/download`` URLs carry none), else .html."""
    path = url.lower().split("?")[0]
    if path.endswith(".pdf"):
        return ".pdf"
    kind = (content_type or "").lower()
    if "pdf" in kind:
        return ".pdf"
    if "html" in kind:
        return ".html"
    tail = path.rsplit("/", 1)[-1]
    if "." in tail and len(tail.rsplit(".", 1)[-1]) <= 4:
        return "." + tail.rsplit(".", 1)[-1]
    return ".html"


def probe_content_type(url: str, *, timeout_seconds: float = 30.0) -> str | None:
    """The Content-Type a HEAD request reports, or None when the server
    refuses HEAD; it decides only the pinned file's suffix, never its bytes."""
    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            return client.head(url).headers.get("content-type")
    except httpx.HTTPError:
        return None
