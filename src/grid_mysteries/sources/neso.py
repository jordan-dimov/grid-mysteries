"""Adapter for NESO's Data Portal (CKAN) Skip Rates resources.

Dataset semantics: per calendar day x NGC BM unit x Bid/Offer x
methodology stage 0..5, In Merit All Balancing Mechanism carries
available / in-merit / accepted / skipped volumes; Exclusion Reasons
carries per-exclusion rows with stage, reason and the side excluded
(alternative or Accepted). Stage 5 is the final applicable stage.
"""

import csv
from pathlib import Path
from urllib.parse import quote

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

NESO_RAW = REPO_ROOT / "data" / "raw" / "neso"
FINAL_STAGE = 5
SOURCE = "neso-data-portal"


CKAN_ACTION = "https://api.neso.energy/api/3/action"


def dump_url(resource_id: str) -> str:
    return f"https://api.neso.energy/datastore/dump/{resource_id}"


def resource_show_url(resource_id: str) -> str:
    """CKAN metadata for one resource, including the package it belongs to."""
    return f"{CKAN_ACTION}/resource_show?id={resource_id}"


def package_show_url(package_id: str) -> str:
    """CKAN listing of every resource in a package (by id or name)."""
    return f"{CKAN_ACTION}/package_show?id={package_id}"


def package_search_url(query: str, *, rows: int = 20) -> str:
    """CKAN full-text search over the portal's packages; listing only."""
    return f"{CKAN_ACTION}/package_search?q={quote(query)}&rows={rows}"


def datastore_fields_url(resource_id: str) -> str:
    """A zero-row datastore query: field names and total without values."""
    return f"{CKAN_ACTION}/datastore_search?resource_id={resource_id}&limit=0"


def read_csv_path(path: Path) -> list[dict]:
    """Read any pinned portal CSV by path; values stay strings."""
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def fetch_pinned(
    *,
    url: str,
    destination: Path,
    dataset: str,
    timeout_seconds: float = 300.0,
) -> SourceArtifact:
    """Pin one data-portal dump. The long default timeout covers the
    multi-month CSV resources the portal serialises on request."""
    return fetch_artifact(
        url=url,
        destination=destination,
        source=SOURCE,
        dataset=dataset,
        timeout_seconds=timeout_seconds,
    )


def read_csv(filename: str) -> list[dict]:
    """Read a pinned Skip Rates CSV. Values stay strings; callers convert
    volumes with Decimal at the point of use."""
    with (NESO_RAW / filename).open(newline="") as handle:
        return list(csv.DictReader(handle))
