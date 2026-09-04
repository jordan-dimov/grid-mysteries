"""Pinning of public rules documents (Ofgem, NESO, Elexon, Grid Code pages
and PDFs) as immutable bytes.

A document is evidence of what a rule said at fetch time; nothing here
parses it. Quotation happens by hand in the investigation's write-up,
beside the digest recorded at the pin.
"""

from pathlib import Path

from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

SOURCE = "public-document"


def fetch_pinned(*, url: str, destination: Path, dataset: str) -> SourceArtifact:
    return fetch_artifact(url=url, destination=destination, source=SOURCE, dataset=dataset)


def suffix_for(url: str) -> str:
    return ".pdf" if url.lower().split("?")[0].endswith(".pdf") else ".html"
