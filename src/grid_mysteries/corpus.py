"""The consumed research corpus: settlement window 2026-08-04..2026-08-10.

Investigation 001 fetched and pinned this seven-day window; Method
Studies 001, 001B, 001C and 001D consumed it. This module is the single
description of that corpus — its dates, its on-disk artefact layout, and
the Decimal-strict way its records are read — so study code never
re-declares them. Per the research doctrine, an amended selection rule
never re-runs against this corpus; new windows belong to new
investigations with their own declarations.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = REPO_ROOT / "data" / "raw" / "elexon"
BMUNITS_PATH = RAW_ROOT / "case-001" / "bmunits.json"

WINDOW_START = date(2026, 8, 4)
WINDOW_DAYS = 7
PERIODS = range(1, 49)
DIRECTIONS = ("offer", "bid")
TOTAL_PERIODS = WINDOW_DAYS * len(PERIODS)


def window_dates() -> list[str]:
    return [(WINDOW_START + timedelta(days=day)).isoformat() for day in range(WINDOW_DAYS)]


def window_path(kind: str, settlement_date: str, period: int) -> Path:
    """A pinned per-period window artefact: kind is bod, disptav_offer or
    disptav_bid."""
    return RAW_ROOT / settlement_date / f"{kind}_p{period:02d}.json"


def physical_path(dataset: str, settlement_date: str, period: int) -> Path:
    """A pinned per-period physical-state artefact: PN, MELS or MILS."""
    return RAW_ROOT / "physical" / settlement_date / f"{dataset.lower()}_p{period:02d}.json"


def load_records(path: Path) -> list[dict]:
    """Read a pinned artefact's records with floats parsed as Decimal, so
    binary floating-point never enters an analytical path."""
    payload = json.loads(path.read_text(), parse_float=Decimal)
    return payload["data"] if isinstance(payload, dict) else payload


def unit_maps() -> tuple[dict[str, str], dict[str, str]]:
    """(NGC -> Elexon, Elexon -> NGC) BM-unit id maps from the pinned
    reference vintage."""
    records = load_records(BMUNITS_PATH)
    ngc_to_elexon = {
        str(r["nationalGridBmUnit"]): str(r["elexonBmUnit"])
        for r in records
        if r.get("nationalGridBmUnit")
    }
    return ngc_to_elexon, {v: k for k, v in ngc_to_elexon.items()}
