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

import sys
from datetime import date, timedelta
from pathlib import Path

from grid_mysteries.corpus import PERIODS, REPO_ROOT, day_range
from grid_mysteries.evidence import evidence_dir
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.pinning import pin, progress

EVIDENCE = evidence_dir(__file__)
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
    return day_range(JULY_START, JULY_DAYS)


def stream_dates() -> list[str]:
    return day_range(STREAM_START, JULY_DAYS + 1)


def fetch() -> None:
    jobs: list[tuple[str, str, Path]] = [
        (dataset, elexon.day_stream_url(dataset, day), MDX_RAW / f"{dataset.lower()}_{day}.json")
        for dataset in ("MDO", "MDB")
        for day in stream_dates()
    ]
    for day in july_dates():
        jobs.extend(elexon.period_jobs(day, PERIODS, datasets=("BOD", "DISPTAV")))
    pin(
        jobs,
        journal_path=EVIDENCE / "july-journal.ndjson",
        manifest_path=EVIDENCE / "july-manifest.json",
        fetch=elexon.fetch_pinned,
        label="elexon",
        progress=lambda path: progress(path) if "p48" in path else None,
    )
    neso_jobs = [
        (dataset, neso.dump_url(resource_id), neso.NESO_RAW / filename)
        for dataset, resource_id, filename in NESO_JULY_RESOURCES
    ]
    pin(
        neso_jobs,
        journal_path=EVIDENCE / "neso-july-journal.ndjson",
        manifest_path=EVIDENCE / "neso-july-manifest.json",
        fetch=neso.fetch_pinned,
        label="neso",
        sleep_seconds=0.5,
    )


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
