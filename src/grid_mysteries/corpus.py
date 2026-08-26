"""The consumed research corpus: settlement window 2026-08-04..2026-08-10.

Investigation 001 fetched and pinned this seven-day window; Method
Studies 001, 001B, 001C and 001D consumed it. This module is the single
description of that corpus — its dates, its on-disk artefact layout, and
the Decimal-strict way its records are read — so study code never
re-declares them. Per the research doctrine, an amended selection rule
never re-runs against this corpus; new windows belong to new
investigations with their own declarations.
"""

import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = REPO_ROOT / "data" / "raw" / "elexon"
BMUNITS_PATH = RAW_ROOT / "case-001" / "bmunits.json"

Direction = Literal["offer", "bid"]

WINDOW_START = date(2026, 8, 4)
WINDOW_DAYS = 7
PERIODS = range(1, 49)
DIRECTIONS: tuple[Direction, ...] = ("offer", "bid")
TOTAL_PERIODS = WINDOW_DAYS * len(PERIODS)


def day_range(start: date, days: int) -> list[str]:
    """ISO dates of `days` consecutive calendar days from `start` inclusive."""
    return [(start + timedelta(days=offset)).isoformat() for offset in range(days)]


def window_dates() -> list[str]:
    return day_range(WINDOW_START, WINDOW_DAYS)


def window_path(kind: str, settlement_date: str, period: int) -> Path:
    """A pinned per-period window artefact: kind is bod, disptav_offer,
    disptav_bid or boalf."""
    return RAW_ROOT / settlement_date / f"{kind}_p{period:02d}.json"


def physical_path(dataset: str, settlement_date: str, period: int) -> Path:
    """A pinned per-period physical-state artefact: PN, MELS or MILS."""
    return RAW_ROOT / "physical" / settlement_date / f"{dataset.lower()}_p{period:02d}.json"


def load_records(path: Path) -> list[dict]:
    """Read a pinned artefact's records with floats parsed as Decimal, so
    binary floating-point never enters an analytical path."""
    payload = json.loads(path.read_text(), parse_float=Decimal)
    return payload["data"] if isinstance(payload, dict) else payload


def load_table_rows(parquet_path: Path) -> list[dict]:
    """Named rows of a committed evidence table (e.g. Method Study 001's
    classified alternatives). Parquet I/O stays here, outside the pure
    investigation modules, so those replay from plain rows."""
    import polars as pl

    return list(pl.read_parquet(parquet_path).iter_rows(named=True))


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


def registered_capacities() -> dict[str, tuple[Decimal | None, Decimal | None]]:
    """(generation, demand) capacity per unit from the pinned BM-unit vintage.

    The headroom bounds in `investigations.phantom_liquidity` fall back to
    these when MELS/MILS are absent, so every study that screens
    deliverability needs them; one reader, one vintage.
    """
    capacities = {}
    for record in load_records(BMUNITS_PATH):
        generation = record.get("generationCapacity")
        demand = record.get("demandCapacity")
        capacities[str(record["elexonBmUnit"])] = (
            Decimal(generation) if generation is not None else None,
            Decimal(demand) if demand is not None else None,
        )
    return capacities


def fuel_types() -> dict[str, str]:
    """Unit -> NESO fuel classification from the pinned BM-unit vintage.

    Units absent from the vintage are reported by the caller as
    `unclassified` rather than guessed; aggregator and virtual units
    frequently carry no fuel type at all.
    """
    return {
        str(record["elexonBmUnit"]): (record.get("fuelType") or "unclassified")
        for record in load_records(BMUNITS_PATH)
    }
