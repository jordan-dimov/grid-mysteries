"""Investigation 003 acquisition. See README.md (pre-declared, amended
before acquisition).

Usage:
    uv run python investigations/003-follow-the-constraint/acquire.py fetch
    uv run python investigations/003-follow-the-constraint/acquire.py fetch-pn

``fetch`` (phase A) pins the May 2026 corpus: NESO constraint datasets
(day-ahead flows/limits as forecast context; the constraint cost
breakdown resource covering May 2026, discovered by name from the
package listing and recorded in the journal), NESO May Skip Rates, and
Elexon BOALF + BOD + DISPTAV per settlement period. ``fetch-pn``
(phase B) pins PN day streams filtered to the storage units classified
by NESO's May fuel field — classification therefore precedes it.
All journalled, immutable, restart-safe.
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import httpx

from grid_mysteries.corpus import PERIODS, REPO_ROOT
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.http import fetch_artifact
from grid_mysteries.sources.pinning import fetch_journalled

EVIDENCE = Path(__file__).resolve().parent / "evidence"
RAW = REPO_ROOT / "data" / "raw" / "elexon"
PN_RAW = RAW / "pn-2026-05"

MAY_START = date(2026, 5, 1)
MAY_DAYS = 31

FLOWS_RESOURCE = "38a18ec1-9e40-465d-93fb-301e80fd1352"  # Day Ahead Constraint Flows and Limits
NESO_MAY_SKIP = [
    (
        "NESO-SKIP-INMERIT-ALLBM-MAY",
        "0c358c48-72f6-4f65-a738-2fa4ce182692",
        "inmerit_allbm_2026-05.csv",
    ),
    ("NESO-SKIP-EXCLUSIONS-MAY", "6f4319a1-ee65-442a-8081-f6e71713ba7f", "exclusions_2026-05.csv"),
]


def may_dates() -> list[str]:
    return [(MAY_START + timedelta(days=day)).isoformat() for day in range(MAY_DAYS)]


def neso_fetch(*, url: str, destination: Path, dataset: str):
    return fetch_artifact(
        url=url, destination=destination, source=neso.SOURCE, dataset=dataset, timeout_seconds=300.0
    )


def constraint_cost_resources() -> list[tuple[str, str, str]]:
    """Constraint-cost resources covering May 2026 (FY 26-27), discovered
    by name from the official package listings."""
    found = []
    with httpx.Client(timeout=60) as client:
        for package in ("thermal-constraint-costs", "constraint-breakdown"):
            listing = client.get(
                f"https://api.neso.energy/api/3/action/package_show?id={package}"
            ).json()["result"]["resources"]
            for res in listing:
                name = res["name"].lower()
                if "26-27" in name or "2026-2027" in name:
                    slug = res["name"].replace(" ", "_").lower()
                    found.append((f"NESO-{package.upper()}", res["id"], f"{slug}.csv"))
    if not found:
        raise RuntimeError("no constraint-cost resource covering May 2026 found; inspect listings")
    return found


def fetch() -> None:
    EVIDENCE.mkdir(exist_ok=True)
    neso_jobs = [
        (
            "NESO-DA-FLOWS-LIMITS",
            neso.dump_url(FLOWS_RESOURCE),
            neso.NESO_RAW / "da_constraint_flows_limits.csv",
        ),
        *(
            (dataset, neso.dump_url(rid), neso.NESO_RAW / filename)
            for dataset, rid, filename in NESO_MAY_SKIP
        ),
        *(
            (dataset, neso.dump_url(rid), neso.NESO_RAW / filename)
            for dataset, rid, filename in constraint_cost_resources()
        ),
    ]
    fetched, skipped = fetch_journalled(
        neso_jobs,
        journal_path=EVIDENCE / "neso-may-journal.ndjson",
        manifest_path=EVIDENCE / "neso-may-manifest.json",
        repo_root=REPO_ROOT,
        fetch=neso_fetch,
        sleep_seconds=0.5,
    )
    print(f"neso: fetched {fetched}, skipped {skipped}", flush=True)

    jobs = []
    for day in may_dates():
        for period in PERIODS:
            jobs.append(
                (
                    "BOALF",
                    f"{elexon.BASE_URL}/balancing/acceptances/all"
                    f"?settlementDate={day}&settlementPeriod={period}",
                    RAW / day / f"boalf_p{period:02d}.json",
                )
            )
            jobs.append(
                ("BOD", elexon.bid_offer_url(day, period), RAW / day / f"bod_p{period:02d}.json")
            )
            for direction in ("offer", "bid"):
                jobs.append(
                    (
                        "DISPTAV",
                        elexon.acceptance_volumes_url(direction, day, period),
                        RAW / day / f"disptav_{direction}_p{period:02d}.json",
                    )
                )
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "may-journal.ndjson",
        manifest_path=EVIDENCE / "may-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
        progress=lambda path: print(f"pinned {path}", flush=True) if "p48" in path else None,
    )
    print(f"elexon: fetched {fetched}, skipped {skipped}")


def storage_units() -> list[str]:
    """NGC ids classified BATTERY or PS in NESO's May fuel field."""
    units = sorted(
        {
            r["bm_unit"]
            for r in neso.read_csv("inmerit_allbm_2026-05.csv")
            if r.get("fuel", "").upper() in ("BATTERY", "PS", "PUMPED STORAGE")
        }
    )
    (EVIDENCE / "storage-units.json").write_text(json.dumps(units, indent=1) + "\n")
    return units


def fetch_pn() -> None:
    from grid_mysteries.corpus import unit_maps

    ngc_units = storage_units()
    ngc_to_elexon, _ = unit_maps()
    elexon_units = sorted({ngc_to_elexon.get(u, u) for u in ngc_units})
    print(f"{len(elexon_units)} storage units classified by NESO fuel field")
    jobs = []
    for day in may_dates():
        next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
        url = (
            f"{elexon.BASE_URL}/datasets/PN/stream?from={day}T00:00Z&to={next_day}T00:00Z"
            + "".join(f"&bmUnit={u}" for u in elexon_units)
        )
        jobs.append(("PN", url, PN_RAW / f"pn_{day}.json"))
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "pn-may-journal.ndjson",
        manifest_path=EVIDENCE / "pn-may-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
    )
    print(f"pn: fetched {fetched}, skipped {skipped}")


def main() -> None:
    match sys.argv[1:]:
        case ["fetch"]:
            fetch()
        case ["fetch-pn"]:
            fetch_pn()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
