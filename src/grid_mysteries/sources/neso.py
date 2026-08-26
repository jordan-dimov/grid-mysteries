"""Adapter for NESO's Data Portal (CKAN) Skip Rates resources.

Dataset semantics: per calendar day x NGC BM unit x Bid/Offer x
methodology stage 0..5, In Merit All Balancing Mechanism carries
available / in-merit / accepted / skipped volumes; Exclusion Reasons
carries per-exclusion rows with stage, reason and the side excluded
(alternative or Accepted). Stage 5 is the final applicable stage.
"""

import csv
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

NESO_RAW = REPO_ROOT / "data" / "raw" / "neso"
FINAL_STAGE = 5
SOURCE = "neso-data-portal"


def dump_url(resource_id: str) -> str:
    return f"https://api.neso.energy/datastore/dump/{resource_id}"


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
