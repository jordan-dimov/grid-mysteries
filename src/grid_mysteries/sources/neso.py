"""Adapter for NESO's Data Portal (CKAN) Skip Rates resources.

Dataset semantics: per calendar day x NGC BM unit x Bid/Offer x
methodology stage 0..5, In Merit All Balancing Mechanism carries
available / in-merit / accepted / skipped volumes; Exclusion Reasons
carries per-exclusion rows with stage, reason and the side excluded
(alternative or Accepted). Stage 5 is the final applicable stage.
"""

from __future__ import annotations

import csv

from grid_mysteries.corpus import REPO_ROOT

NESO_RAW = REPO_ROOT / "data" / "raw" / "neso"
FINAL_STAGE = 5
SOURCE = "neso-data-portal"


def dump_url(resource_id: str) -> str:
    return f"https://api.neso.energy/datastore/dump/{resource_id}"


def read_csv(filename: str) -> list[dict]:
    """Read a pinned Skip Rates CSV. Values stay strings; callers convert
    volumes with Decimal at the point of use."""
    with (NESO_RAW / filename).open(newline="") as handle:
        return list(csv.DictReader(handle))
