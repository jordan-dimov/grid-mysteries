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

import sys
from datetime import date

import httpx

from grid_mysteries.corpus import DIRECTIONS, PERIODS, REPO_ROOT, day_range
from grid_mysteries.evidence import evidence_dir, write_json
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.pinning import pin, progress

EVIDENCE = evidence_dir(__file__)
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
    return day_range(MAY_START, MAY_DAYS)


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
    pin(
        neso_jobs,
        journal_path=EVIDENCE / "neso-may-journal.ndjson",
        manifest_path=EVIDENCE / "neso-may-manifest.json",
        fetch=neso.fetch_pinned,
        label="neso",
        sleep_seconds=0.5,
    )
    jobs = [
        job
        for day in may_dates()
        for job in elexon.period_jobs(day, PERIODS, datasets=("BOALF", "BOD", "DISPTAV"))
    ]
    pin(
        jobs,
        journal_path=EVIDENCE / "may-journal.ndjson",
        manifest_path=EVIDENCE / "may-manifest.json",
        fetch=elexon.fetch_pinned,
        label="elexon",
        progress=lambda path: progress(path) if "p48" in path else None,
    )


def storage_units() -> list[str]:
    """NGC ids classified BATTERY or PS in NESO's May fuel field."""
    units = sorted(
        {
            r["bm_unit"]
            for r in neso.read_csv("inmerit_allbm_2026-05.csv")
            if r.get("fuel", "").upper() in ("BATTERY", "PS", "PUMPED STORAGE")
        }
    )
    write_json(EVIDENCE / "storage-units.json", units)
    return units


def fetch_pn() -> None:
    from grid_mysteries.corpus import unit_maps

    ngc_units = storage_units()
    ngc_to_elexon, _ = unit_maps()
    elexon_units = sorted({ngc_to_elexon.get(u, u) for u in ngc_units})
    print(f"{len(elexon_units)} storage units classified by NESO fuel field")
    jobs = [
        ("PN", elexon.day_stream_url("PN", day, elexon_units), PN_RAW / f"pn_{day}.json")
        for day in may_dates()
    ]
    pin(
        jobs,
        journal_path=EVIDENCE / "pn-may-journal.ndjson",
        manifest_path=EVIDENCE / "pn-may-manifest.json",
        fetch=elexon.fetch_pinned,
        label="pn",
    )


def fetch_ebocf() -> None:
    """EBOCF: published indicative BM cashflows, per date and direction
    (one request covers all 48 periods, per-pair, TLM-inclusive)."""
    jobs = [
        ("EBOCF", elexon.cashflows_url(direction, day), RAW / day / f"ebocf_{direction}.json")
        for day in may_dates()
        for direction in DIRECTIONS
    ]
    pin(
        jobs,
        journal_path=EVIDENCE / "ebocf-may-journal.ndjson",
        manifest_path=EVIDENCE / "ebocf-may-manifest.json",
        fetch=elexon.fetch_pinned,
        label="ebocf",
    )


def main() -> None:
    match sys.argv[1:]:
        case ["fetch"]:
            fetch()
        case ["fetch-ebocf"]:
            fetch_ebocf()
        case ["fetch-pn"]:
            fetch_pn()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
