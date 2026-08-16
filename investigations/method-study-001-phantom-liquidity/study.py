"""Method Study 001 — phantom liquidity. See METHOD-STUDY-001.md.

Usage:
    uv run python investigations/method-study-001-phantom-liquidity/study.py fetch
    uv run python investigations/method-study-001-phantom-liquidity/study.py analyse
    uv run python investigations/method-study-001-phantom-liquidity/study.py charts

``fetch`` pins per-period PN/MELS/MILS for the consumed window (journalled,
immutable, restart-safe). ``analyse`` is offline and deterministic: it
recomputes the Investigation 001 candidate set, applies the declared
funnel and deliverability bound, and writes ``evidence/analysis.json`` and
the alternatives table. ``charts`` renders the two SVGs from
``analysis.json``. Interpretation belongs in NOTE.md, not here.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import (
    BMUNITS_PATH,
    DIRECTIONS,
    PERIODS,
    REPO_ROOT,
    TOTAL_PERIODS,
    load_records,
    physical_path,
    window_dates,
    window_path,
)
from grid_mysteries.investigations.bod_inversion import (
    accepted_pairs,
    find_inversion_candidates,
    submitted_pairs,
)
from grid_mysteries.investigations.phantom_liquidity import (
    NON_DELIVERABLE,
    classify,
    headroom_upper_bound,
    level_extremes,
)
from grid_mysteries.sources import elexon
from grid_mysteries.sources.pinning import fetch_journalled
from grid_mysteries.stats import percentile

EVIDENCE = Path(__file__).resolve().parent / "evidence"
PHYSICAL_DATASETS = ("PN", "MELS", "MILS")


def fetch() -> None:
    jobs = [
        (
            dataset,
            f"{elexon.BASE_URL}/balancing/physical/all"
            f"?dataset={dataset}&settlementDate={settlement_date}&settlementPeriod={period}",
            physical_path(dataset, settlement_date, period),
        )
        for settlement_date in window_dates()
        for period in PERIODS
        for dataset in PHYSICAL_DATASETS
    ]
    EVIDENCE.mkdir(exist_ok=True)
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "physical-fetch-journal.ndjson",
        manifest_path=EVIDENCE / "physical-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
        progress=lambda path: print(f"pinned {path}", flush=True),
    )
    print(f"fetched {fetched}, verified and skipped {skipped}")


def load_capacities() -> dict[str, tuple[Decimal | None, Decimal | None]]:
    capacities = {}
    for record in load_records(BMUNITS_PATH):
        generation = record.get("generationCapacity")
        demand = record.get("demandCapacity")
        capacities[str(record["elexonBmUnit"])] = (
            Decimal(generation) if generation is not None else None,
            Decimal(demand) if demand is not None else None,
        )
    return capacities


def analyse() -> None:
    capacities = load_capacities()
    total_raw = 0
    raw_by_direction = Counter()
    episodes: set[tuple[str, int, str]] = set()
    alternatives: dict[tuple, dict] = {}
    concentration = Counter()
    persistence = Counter()

    for settlement_date in window_dates():
        for period in PERIODS:
            bod_records = load_records(window_path("bod", settlement_date, period))
            extremes = {
                dataset: level_extremes(
                    load_records(physical_path(dataset, settlement_date, period))
                )
                for dataset in PHYSICAL_DATASETS
            }
            for direction in DIRECTIONS:
                submitted = submitted_pairs(bod_records, direction)
                for pair in submitted:
                    persistence[(pair.bm_unit, pair.pair_id, str(pair.price_gbp_per_mwh))] += 1
                accepted = accepted_pairs(
                    load_records(window_path(f"disptav_{direction}", settlement_date, period)),
                    direction,
                )
                candidates = find_inversion_candidates(
                    settlement_date=settlement_date,
                    settlement_period=period,
                    direction=direction,
                    submitted=submitted,
                    accepted=accepted,
                )
                if not candidates:
                    continue
                episodes.add((settlement_date, period, direction))
                total_raw += len(candidates)
                raw_by_direction[direction] += len(candidates)
                period_alternatives = set()
                for candidate in candidates:
                    key = (
                        settlement_date,
                        period,
                        direction,
                        candidate.unaccepted_unit,
                        candidate.unaccepted_pair_id,
                    )
                    period_alternatives.add(key)
                    alt = alternatives.get(key)
                    if alt is None:
                        alt = alternatives[key] = {
                            "price": candidate.unaccepted_price_gbp_per_mwh,
                            "band_mw": candidate.unaccepted_max_level_mw,
                            "n_inversions": 0,
                            "max_gap": candidate.gap_gbp_per_mwh,
                        }
                    alt["n_inversions"] += 1
                    alt["max_gap"] = max(alt["max_gap"], candidate.gap_gbp_per_mwh)
                    concentration[
                        (
                            candidate.unaccepted_unit,
                            str(candidate.unaccepted_price_gbp_per_mwh),
                            direction,
                        )
                    ] += 1
                for key in period_alternatives:
                    _, _, _, unit, _ = key
                    generation, demand = capacities.get(unit, (None, None))
                    bound = headroom_upper_bound(
                        direction,
                        fpn=extremes["PN"].get(unit),
                        mels=extremes["MELS"].get(unit),
                        mils=extremes["MILS"].get(unit),
                        generation_capacity=generation,
                        demand_capacity=demand,
                    )
                    alternatives[key]["headroom_ub"] = bound
                    alternatives[key]["classification"] = classify(bound)
        print(f"analysed {settlement_date}", flush=True)

    for key, alt in alternatives.items():
        _, _, _, unit, pair_id = key
        alt["persistence"] = persistence[(unit, pair_id, str(alt["price"]))] / TOTAL_PERIODS

    ruled_out = {k: a for k, a in alternatives.items() if a["classification"] == NON_DELIVERABLE}
    residual = {k: a for k, a in alternatives.items() if a["classification"] != NON_DELIVERABLE}
    ruled_out_pairwise = sum(a["n_inversions"] for a in ruled_out.values())
    residual_episodes = {(k[0], k[1], k[2]) for k in residual}

    groups = concentration.most_common()
    # The full cumulative curve, reported on a dense log-spaced rank grid
    # (every rank up to 10, then ~12 ranks per decade) plus the final rank.
    grid = sorted(
        {
            *range(1, 11),
            *(
                round(10 ** (exponent / 12))
                for exponent in range(12, 12 * 6)
                if round(10 ** (exponent / 12)) <= len(groups)
            ),
            len(groups),
        }
    )
    cumulative, shares_at = 0, {}
    grid_index = 0
    for rank, (_, count) in enumerate(groups, start=1):
        cumulative += count
        if grid_index < len(grid) and rank == grid[grid_index]:
            shares_at[rank] = cumulative / total_raw
            grid_index += 1
    weighted_persistence = (
        sum(a["n_inversions"] * a["persistence"] for a in alternatives.values()) / total_raw
    )
    residual_gaps = sorted(a["max_gap"] for a in residual.values())

    analysis = {
        "corpus": {"window": [window_dates()[0], window_dates()[-1]], "periods": TOTAL_PERIODS},
        "funnel": {
            "f1_raw_pairwise_inversions": total_raw,
            "f1_by_direction": dict(raw_by_direction),
            "f2_episodes": len(episodes),
            "f3_unique_alternatives": len(alternatives),
            "f6_non_deliverable_alternatives": len(ruled_out),
            "f6_pairwise_inversions_carried": ruled_out_pairwise,
            "f7_residual_alternatives": len(residual),
            "f7_residual_pairwise_inversions": total_raw - ruled_out_pairwise,
            "f7_residual_episodes": len(residual_episodes),
        },
        "f4_concentration": {
            "n_groups": len(groups),
            "cumulative_share_of_f1_at_group_rank": shares_at,
            "top20": [
                {"bm_unit": unit, "price": price, "direction": direction, "count": count}
                for (unit, price, direction), count in groups[:20]
            ],
        },
        "f5_persistence": {
            "f1_weighted_mean_fraction": weighted_persistence,
            "alternative_deciles": [
                str(percentile(sorted(a["persistence"] for a in alternatives.values()), q / 10))
                for q in range(11)
            ],
        },
        "f7_residual_max_gap_percentiles": {
            "p50": str(percentile(residual_gaps, 0.50)),
            "p90": str(percentile(residual_gaps, 0.90)),
            "p99": str(percentile(residual_gaps, 0.99)),
            "max": str(residual_gaps[-1]),
        },
        "residual_top10_by_carried_inversions": [
            {
                "bm_unit": k[3],
                "pair_id": k[4],
                "direction": k[2],
                "price": str(a["price"]),
                "n_inversions": a["n_inversions"],
                "persistence": a["persistence"],
            }
            for k, a in sorted(residual.items(), key=lambda kv: -kv[1]["n_inversions"])[:10]
        ],
    }
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "analysis.json").write_text(json.dumps(analysis, indent=1, default=str) + "\n")

    import polars as pl

    table = pl.DataFrame(
        [
            {
                "settlement_date": k[0],
                "settlement_period": k[1],
                "direction": k[2],
                "bm_unit": k[3],
                "pair_id": k[4],
                "price_gbp_per_mwh": str(a["price"]),
                "band_mw": str(a["band_mw"]),
                "headroom_ub_mw": None if a["headroom_ub"] is None else str(a["headroom_ub"]),
                "classification": a["classification"],
                "n_inversions": a["n_inversions"],
                "max_gap_gbp_per_mwh": str(a["max_gap"]),
                "persistence_fraction": a["persistence"],
            }
            for k, a in sorted(alternatives.items())
        ]
    )
    table.write_parquet(EVIDENCE / "alternatives.parquet")
    print(json.dumps(analysis["funnel"], indent=1))
    print(f"alternatives table: {table.height} rows")


def main() -> None:
    match sys.argv[1:]:
        case ["fetch"]:
            fetch()
        case ["analyse"]:
            analyse()
        case ["charts"]:
            from render_charts import render  # sibling module, added with the results

            render()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
