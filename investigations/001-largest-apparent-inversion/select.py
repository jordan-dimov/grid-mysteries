"""Fetch and deterministically select Mystery 001, per the pre-declared rule.

Usage:
    uv run python investigations/001-largest-apparent-inversion/select.py fetch
    uv run python investigations/001-largest-apparent-inversion/select.py select

``fetch`` performs network I/O and pins immutable raw artefacts under
``data/raw/elexon/``, recording digests in ``evidence/manifest.json``.
``select`` is offline and deterministic: it reads only pinned artefacts and
writes ``evidence/candidates-top50.json`` and ``evidence/selected.json``.
"""

from __future__ import annotations

import dataclasses
import json
import sys
import time
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from grid_mysteries.investigations.bod_inversion import (
    find_inversion_candidates,
    rank_candidates,
    accepted_pairs,
    submitted_pairs,
)
from grid_mysteries.sources import elexon

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = REPO_ROOT / "data" / "raw" / "elexon"
EVIDENCE = Path(__file__).resolve().parent / "evidence"

WINDOW_START = date(2026, 8, 4)
WINDOW_DAYS = 7
PERIODS = range(1, 49)
DIRECTIONS = ("offer", "bid")


def window_dates() -> list[str]:
    return [(WINDOW_START + timedelta(days=day)).isoformat() for day in range(WINDOW_DAYS)]


def artefact_paths(settlement_date: str, period: int) -> dict[str, Path]:
    day_dir = RAW_ROOT / settlement_date
    paths = {"bod": day_dir / f"bod_p{period:02d}.json"}
    for direction in DIRECTIONS:
        paths[f"disptav_{direction}"] = day_dir / f"disptav_{direction}_p{period:02d}.json"
    return paths


def fetch() -> None:
    manifest = []
    for settlement_date in window_dates():
        for period in PERIODS:
            paths = artefact_paths(settlement_date, period)
            jobs = [
                ("BOD", elexon.bid_offer_url(settlement_date, period), paths["bod"]),
                *(
                    (
                        "DISPTAV",
                        elexon.acceptance_volumes_url(direction, settlement_date, period),
                        paths[f"disptav_{direction}"],
                    )
                    for direction in DIRECTIONS
                ),
            ]
            for dataset, url, destination in jobs:
                artefact = elexon.fetch_pinned(url=url, destination=destination, dataset=dataset)
                manifest.append(
                    {
                        "source": artefact.source,
                        "dataset": artefact.dataset,
                        "url": url,
                        "path": str(destination.relative_to(REPO_ROOT)),
                        "sha256": artefact.sha256,
                        "fetched_at": artefact.fetched_at.isoformat(),
                        "bytes": destination.stat().st_size,
                    }
                )
                time.sleep(0.1)
            print(f"fetched {settlement_date} period {period}", flush=True)

    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"pinned {len(manifest)} artefacts")


def load_records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(), parse_float=Decimal)
    return payload["data"] if isinstance(payload, dict) else payload


def select() -> None:
    candidates = []
    for settlement_date in window_dates():
        for period in PERIODS:
            paths = artefact_paths(settlement_date, period)
            bod_records = load_records(paths["bod"])
            for direction in DIRECTIONS:
                candidates.extend(
                    find_inversion_candidates(
                        settlement_date=settlement_date,
                        settlement_period=period,
                        direction=direction,
                        submitted=submitted_pairs(bod_records, direction),
                        accepted=accepted_pairs(
                            load_records(paths[f"disptav_{direction}"]), direction
                        ),
                    )
                )

    ranked = rank_candidates(candidates)

    def row(candidate) -> dict:
        data = dataclasses.asdict(candidate)
        data["gap_gbp_per_mwh"] = candidate.gap_gbp_per_mwh
        return data

    EVIDENCE.mkdir(exist_ok=True)
    top50 = [row(c) for c in ranked[:50]]
    (EVIDENCE / "candidates-top50.json").write_text(
        json.dumps({"total_candidates": len(ranked), "top50": top50}, indent=1, default=str) + "\n"
    )
    (EVIDENCE / "selected.json").write_text(
        json.dumps(row(ranked[0]), indent=1, default=str) + "\n"
    )
    print(f"candidates={len(ranked)}")
    print(json.dumps(row(ranked[0]), indent=1, default=str))


def main() -> None:
    match sys.argv[1:]:
        case ["fetch"]:
            fetch()
        case ["select"]:
            select()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
