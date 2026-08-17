"""BESS Study 001 — benchmark fragility. See METHOD-STUDY-BESS-001.md.

Usage:
    uv run python investigations/bess-study-001-benchmark-fragility/bench.py fetch
    uv run python investigations/bess-study-001-benchmark-fragility/bench.py panel
    uv run python investigations/bess-study-001-benchmark-fragility/bench.py fetch-physical
    uv run python investigations/bess-study-001-benchmark-fragility/bench.py analyse

``fetch`` pins the July 2026 corpus (MDO/MDB day streams with a lead-in
day for intervals crossing midnight, BOD + DISPTAV per period, NESO July
Skip Rates) — journalled, immutable, restart-safe. ``panel`` applies the
declared unit-blind panel rule. ``fetch-physical`` pins PN/MELS/MILS day
streams filtered to the panel units. ``analyse`` computes the five-rung
Benchmark Fragility table. Interpretation belongs in NOTE.md.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from grid_mysteries.corpus import PERIODS, REPO_ROOT
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.http import fetch_artifact
from grid_mysteries.sources.pinning import fetch_journalled

EVIDENCE = Path(__file__).resolve().parent / "evidence"
RAW = REPO_ROOT / "data" / "raw" / "elexon"
MDX_RAW = RAW / "mdx-2026-07"

JULY_START = date(2026, 7, 1)
JULY_DAYS = 31
# One lead-in day so envelope intervals that start before 1 July but
# cover July delivery time are pinned too.
STREAM_START = JULY_START - timedelta(days=1)

NESO_JULY_RESOURCES = [
    (
        "NESO-SKIP-INMERIT-ALLBM-JUL",
        "c12fdef0-0b18-439d-a16c-c97fbd93c45d",
        "inmerit_allbm_2026-07.csv",
    ),
    ("NESO-SKIP-EXCLUSIONS-JUL", "db88ded4-bb64-4b5a-851d-bdd6eabb397d", "exclusions_2026-07.csv"),
]


def july_dates() -> list[str]:
    return [(JULY_START + timedelta(days=day)).isoformat() for day in range(JULY_DAYS)]


def stream_dates() -> list[str]:
    return [(STREAM_START + timedelta(days=day)).isoformat() for day in range(JULY_DAYS + 1)]


def neso_fetch(*, url: str, destination: Path, dataset: str):
    return fetch_artifact(
        url=url, destination=destination, source=neso.SOURCE, dataset=dataset, timeout_seconds=180.0
    )


def day_stream_url(dataset: str, day: str, bm_units: list[str] | None = None) -> str:
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    url = f"{elexon.BASE_URL}/datasets/{dataset}/stream?from={day}T00:00Z&to={next_day}T00:00Z"
    if bm_units:
        url += "".join(f"&bmUnit={unit}" for unit in bm_units)
    return url


def fetch() -> None:
    jobs: list[tuple[str, str, Path]] = []
    for dataset in ("MDO", "MDB"):
        for day in stream_dates():
            jobs.append(
                (dataset, day_stream_url(dataset, day), MDX_RAW / f"{dataset.lower()}_{day}.json")
            )
    for day in july_dates():
        for period in PERIODS:
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
    EVIDENCE.mkdir(exist_ok=True)
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "july-journal.ndjson",
        manifest_path=EVIDENCE / "july-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
        progress=lambda path: print(f"pinned {path}", flush=True) if "p48" in path else None,
    )
    neso_jobs = [
        (dataset, neso.dump_url(resource_id), neso.NESO_RAW / filename)
        for dataset, resource_id, filename in NESO_JULY_RESOURCES
    ]
    neso_fetched, neso_skipped = fetch_journalled(
        neso_jobs,
        journal_path=EVIDENCE / "neso-july-journal.ndjson",
        manifest_path=EVIDENCE / "neso-july-manifest.json",
        repo_root=REPO_ROOT,
        fetch=neso_fetch,
        sleep_seconds=0.5,
    )
    print(f"elexon: fetched {fetched}, skipped {skipped}; neso: {neso_fetched}/{neso_skipped}")


def main() -> None:
    match sys.argv[1:]:
        case ["fetch"]:
            fetch()
        case ["panel"]:
            from panel import run_panel  # added with the panel step

            run_panel()
        case ["fetch-physical"]:
            from panel import fetch_physical

            fetch_physical()
        case ["analyse"]:
            from analyse import run_analyse  # added with the analysis step

            run_analyse()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
