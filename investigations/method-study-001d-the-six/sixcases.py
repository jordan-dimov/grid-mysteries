"""Method Study 001D — the six unmatched cells. See METHOD-STUDY-001D.md.

``fetch`` pins BOALF for the settlement periods in which a case's unit
qualified as an alternative (journalled, immutable, consumed dates only).
``analyse`` is offline: per-cell period profiles, accepted-side exclusion
evidence and NESO stage profiles into ``evidence/six-anatomy.json``.
Interpretation belongs in NOTE.md.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import load_records, unit_maps, window_path
from grid_mysteries.investigations.bod_inversion import (
    accepted_pairs,
    find_inversion_candidates,
    submitted_pairs,
)
from grid_mysteries.investigations.neso_cells import load_alternative_rows
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.pinning import fetch_journalled

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent / "evidence"
MS1_EVIDENCE = REPO_ROOT / "investigations" / "method-study-001-phantom-liquidity" / "evidence"
MS1C_EVIDENCE = REPO_ROOT / "investigations" / "method-study-001c-disagreement-anatomy" / "evidence"
BMUNITS_PATH = REPO_ROOT / "data" / "raw" / "elexon" / "case-001" / "bmunits.json"
BOALF_RAW = REPO_ROOT / "data" / "raw" / "elexon" / "sixcases-001d"


def read_neso_csv(filename: str) -> list[dict]:
    return neso.read_csv(filename)


def cases() -> list[dict]:
    analysis = json.loads((MS1C_EVIDENCE / "disagreement-analysis.json").read_text())
    return analysis["unmatched_cell_list"]


def qualifying_periods(elexon_unit: str, date: str) -> list[dict]:
    rows = load_alternative_rows(MS1_EVIDENCE / "alternatives.parquet")
    return sorted(
        (
            r
            for r in rows
            if r["settlement_date"] == date
            and r["direction"] == "bid"
            and r["bm_unit"] == elexon_unit
        ),
        key=lambda r: (r["settlement_period"], r["pair_id"]),
    )


def cell_period_set() -> dict[tuple, list[int]]:
    ngc_to_elexon, _ = unit_maps()
    result = {}
    for cell in cases():
        unit = ngc_to_elexon.get(cell["ngc_unit"], cell["ngc_unit"])
        periods = sorted({r["settlement_period"] for r in qualifying_periods(unit, cell["date"])})
        result[(cell["date"], cell["ngc_unit"], unit)] = periods
    return result


def boalf_path(date: str, period: int) -> Path:
    return BOALF_RAW / f"boalf_{date}_p{period:02d}.json"


def fetch() -> None:
    jobs = []
    seen = set()
    for (date, _ngc, _unit), periods in cell_period_set().items():
        for period in periods:
            destination = boalf_path(date, period)
            if destination in seen:
                continue
            seen.add(destination)
            jobs.append(
                (
                    "BOALF",
                    f"{elexon.BASE_URL}/balancing/acceptances/all"
                    f"?settlementDate={date}&settlementPeriod={period}",
                    destination,
                )
            )
    EVIDENCE.mkdir(exist_ok=True)
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "boalf-journal.ndjson",
        manifest_path=EVIDENCE / "boalf-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
    )
    print(f"fetched {fetched}, verified and skipped {skipped}")


def analyse() -> None:
    ngc_to_elexon, elexon_to_ngc = unit_maps()
    exclusions = read_neso_csv("exclusions_2026-08.csv")
    inmerit = read_neso_csv("inmerit_allbm_2026-08.csv")

    out_cases = []
    for cell in cases():
        date, ngc = cell["date"], cell["ngc_unit"]
        unit = ngc_to_elexon.get(ngc, ngc)
        rows = qualifying_periods(unit, date)
        periods = sorted({r["settlement_period"] for r in rows})

        # Which accepted bids did our screen compare this unit against, and
        # what does public data say about those accepted actions?
        accepted_counterparts = Counter()
        accepted_side_exclusions = Counter()
        accepted_so_flags = Counter()
        for period in periods:
            bod_records = load_records(window_path("bod", date, period))
            candidates = find_inversion_candidates(
                settlement_date=date,
                settlement_period=period,
                direction="bid",
                submitted=submitted_pairs(bod_records, "bid"),
                accepted=accepted_pairs(
                    load_records(window_path("disptav_bid", date, period)), "bid"
                ),
            )
            counterpart_units = {c.accepted_unit for c in candidates if c.unaccepted_unit == unit}
            boalf = load_records(boalf_path(date, period))
            for accepted_unit in sorted(counterpart_units):
                accepted_counterparts[accepted_unit] += 1
                accepted_ngc = elexon_to_ngc.get(accepted_unit, accepted_unit)
                for r in exclusions:
                    if (
                        r["date"][:10] == date
                        and r["bid_offer"].lower() == "bid"
                        and r["bm_unit"] == accepted_ngc
                        and r["excluded_from_accepted_or_feasible_merit_stack"] == "Accepted"
                    ):
                        accepted_side_exclusions[r["exclusion_reason"]] += 1
                for r in boalf:
                    if r["bmUnit"] == accepted_unit and r["soFlag"]:
                        accepted_so_flags[accepted_unit] += 1

        neso_stages = {}
        for r in inmerit:
            if r["date"][:10] == date and r["bid_offer"].lower() == "bid" and r["bm_unit"] == ngc:
                stage = int(r["stage"])
                bucket = neso_stages.setdefault(
                    stage, {"available": Decimal(0), "in_merit": Decimal(0), "skipped": Decimal(0)}
                )
                bucket["available"] += abs(Decimal(r["available_volume_MWh"] or "0"))
                bucket["in_merit"] += abs(Decimal(r["in_merit_volume_MWh"] or "0"))
                bucket["skipped"] += abs(Decimal(r["skipped_volume_MWh"] or "0"))

        out_cases.append(
            {
                "cell": cell,
                "elexon_unit": unit,
                "qualifying_periods": periods,
                "period_detail": [
                    {
                        "period": r["settlement_period"],
                        "pair_id": r["pair_id"],
                        "price": r["price_gbp_per_mwh"],
                        "max_gap": r["max_gap_gbp_per_mwh"],
                        "headroom_ub_mw": r["headroom_ub_mw"],
                        "classification": r["classification"],
                    }
                    for r in rows
                ],
                "accepted_counterparts_period_counts": dict(accepted_counterparts.most_common()),
                "accepted_side_exclusion_reasons": dict(accepted_side_exclusions.most_common()),
                "accepted_counterparts_with_so_flag": dict(accepted_so_flags.most_common()),
                "neso_stage_profile": {
                    str(stage): {k: str(v) for k, v in bucket.items()}
                    for stage, bucket in sorted(neso_stages.items())
                },
            }
        )
        print(f"analysed {date} {ngc}", flush=True)

    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "six-anatomy.json").write_text(
        json.dumps({"cases": out_cases}, indent=1, default=str) + "\n"
    )
    for case in out_cases:
        print(
            case["cell"]["date"],
            case["cell"]["ngc_unit"],
            "periods:",
            len(case["qualifying_periods"]),
            "| accepted-side exclusions:",
            sum(case["accepted_side_exclusion_reasons"].values()),
            "| so-flagged counterparts:",
            len(case["accepted_counterparts_with_so_flag"]),
        )


def main() -> None:
    match sys.argv[1:]:
        case ["fetch"]:
            fetch()
        case ["analyse"]:
            analyse()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
