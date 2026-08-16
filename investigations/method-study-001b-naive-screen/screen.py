"""Method Study 001B — the naive opportunity screen. See METHOD-STUDY-001B.md.

Usage:
    uv run python investigations/method-study-001b-naive-screen/screen.py analyse
    uv run python investigations/method-study-001b-naive-screen/screen.py fetch-anatomy
    uv run python investigations/method-study-001b-naive-screen/screen.py anatomy
    uv run python investigations/method-study-001b-naive-screen/screen.py charts

``analyse`` is offline and deterministic: it recomputes the Investigation
001 candidate set from the pinned window, reuses Method Study 001's
deliverability classification verbatim, and writes
``evidence/screen-analysis.json`` + ``evidence/screen.parquet``.
``fetch-anatomy`` pins BOALF for the settlement periods of the top-20
surviving actions (journalled, immutable). ``anatomy`` is offline.
Interpretation belongs in NOTE.md.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

import polars as pl

from grid_mysteries.corpus import (
    BMUNITS_PATH,
    DIRECTIONS,
    PERIODS,
    REPO_ROOT,
    load_records,
    unit_maps,
    window_dates,
    window_path,
)
from grid_mysteries.investigations.bod_inversion import (
    accepted_pairs,
    find_inversion_candidates,
    submitted_pairs,
)
from grid_mysteries.investigations.naive_screen import screen_accepted_actions
from grid_mysteries.investigations.neso_cells import intensity_by_cell, load_alternative_rows
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.pinning import fetch_journalled
from grid_mysteries.stats import percentile

RAW_ROOT = REPO_ROOT / "data" / "raw" / "elexon"
EVIDENCE = Path(__file__).resolve().parent / "evidence"
MS001_EVIDENCE = REPO_ROOT / "investigations" / "method-study-001-phantom-liquidity" / "evidence"
ANATOMY_RAW = RAW_ROOT / "anatomy-001b"

TOP_NS = (10, 100, 1000)
ANATOMY_N = 20


def load_classification() -> dict[tuple, str]:
    table = pl.read_parquet(MS001_EVIDENCE / "alternatives.parquet")
    return {
        (
            r["settlement_date"],
            r["settlement_period"],
            r["direction"],
            r["bm_unit"],
            r["pair_id"],
        ): r["classification"]
        for r in table.iter_rows(named=True)
    }


def screened_actions() -> list:
    classification = load_classification()
    actions = []
    for settlement_date in window_dates():
        for period in PERIODS:
            bod_records = load_records(window_path("bod", settlement_date, period))
            for direction in DIRECTIONS:
                candidates = find_inversion_candidates(
                    settlement_date=settlement_date,
                    settlement_period=period,
                    direction=direction,
                    submitted=submitted_pairs(bod_records, direction),
                    accepted=accepted_pairs(
                        load_records(window_path(f"disptav_{direction}", settlement_date, period)),
                        direction,
                    ),
                )
                if candidates:
                    actions.extend(screen_accepted_actions(candidates, classification))
        print(f"screened {settlement_date}", flush=True)
    return actions


def action_key(action) -> tuple:
    return (
        action.settlement_date,
        action.settlement_period,
        action.direction,
        action.accepted_unit,
        action.accepted_pair_id,
    )


def top_n_distortion(actions: list, naive_metric, post_metric) -> dict:
    raw_ranked = sorted(actions, key=lambda a: (-naive_metric(a), action_key(a)))
    post_ranked = sorted(
        (a for a in actions if not a.vanished), key=lambda a: (-post_metric(a), action_key(a))
    )
    result = {}
    for n in TOP_NS:
        raw_top = raw_ranked[:n]
        post_top_keys = {action_key(a) for a in post_ranked[:n]}
        result[str(n)] = {
            "naive_top1_alternative_non_deliverable": sum(
                1 for a in raw_top if a.naive_alt_non_deliverable
            ),
            "vanished_entirely": sum(1 for a in raw_top if a.vanished),
            "overlap_with_post_filter_top_n": sum(
                1 for a in raw_top if action_key(a) in post_top_keys
            ),
        }
    return result


def analyse() -> None:
    actions = screened_actions()
    total = len(actions)
    by_direction = Counter(a.direction for a in actions)
    naive_top1_phantom = [a for a in actions if a.naive_alt_non_deliverable]
    vanished = [a for a in actions if a.vanished]
    reductions = sorted(a.naive_gap_gbp_per_mwh - a.post_gap_gbp_per_mwh for a in actions)
    raw_notional = sum(a.naive_notional_gbp for a in actions)
    post_notional = sum(a.post_notional_gbp for a in actions)
    phantom_top1_notional = sum(a.naive_notional_gbp for a in naive_top1_phantom)

    reference = {
        str(r["elexonBmUnit"]): (r.get("fuelType"), r.get("gspGroupName"))
        for r in load_records(BMUNITS_PATH)
    }
    surviving_ranked = sorted(
        (a for a in actions if not a.vanished),
        key=lambda a: (-a.post_gap_gbp_per_mwh, action_key(a)),
    )
    top100_fuel = Counter(
        reference.get(a.post_alt_unit, (None, None))[0] or "unknown" for a in surviving_ranked[:100]
    )
    top100_gsp = Counter(
        reference.get(a.post_alt_unit, (None, None))[1] or "unknown" for a in surviving_ranked[:100]
    )

    analysis = {
        "corpus": {"window": [window_dates()[0], window_dates()[-1]]},
        "accepted_actions_with_apparent_alternative": total,
        "by_direction": dict(by_direction),
        "naive_top1_non_deliverable": {
            "count": len(naive_top1_phantom),
            "share": len(naive_top1_phantom) / total,
        },
        "opportunity_vanishes_entirely": {
            "count": len(vanished),
            "share": len(vanished) / total,
        },
        "gap_reduction_gbp_per_mwh": {
            "median": str(percentile(reductions, 0.50)),
            "p75": str(percentile(reductions, 0.75)),
            "p90": str(percentile(reductions, 0.90)),
            "p99": str(percentile(reductions, 0.99)),
        },
        "top_n_distortion_by_gap": top_n_distortion(
            actions,
            lambda a: a.naive_gap_gbp_per_mwh,
            lambda a: a.post_gap_gbp_per_mwh,
        ),
        "top_n_distortion_by_notional": top_n_distortion(
            actions,
            lambda a: a.naive_notional_gbp,
            lambda a: a.post_notional_gbp,
        ),
        "naive_counterfactual_notional_gbp": {
            "labelling": (
                "Arithmetic on public numbers: |accepted MWh| x apparent GBP/MWh gap. "
                "Not a saving, cost, missed revenue or achievable value; the post-filter "
                "figure remains unadjudicated for timing, dynamics and location."
            ),
            "raw_total": str(raw_notional),
            "post_filter_total": str(post_notional),
            "vanished_share": str((raw_notional - post_notional) / raw_notional),
            "attached_to_non_deliverable_naive_top1": str(phantom_top1_notional),
        },
        "surviving_top100_alternative_fuel_types": dict(top100_fuel.most_common()),
        "surviving_top100_alternative_gsp_groups": dict(top100_gsp.most_common()),
    }
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "screen-analysis.json").write_text(json.dumps(analysis, indent=1) + "\n")

    table = pl.DataFrame(
        [
            {
                "settlement_date": a.settlement_date,
                "settlement_period": a.settlement_period,
                "direction": a.direction,
                "accepted_unit": a.accepted_unit,
                "accepted_pair_id": a.accepted_pair_id,
                "accepted_volume_mwh": str(a.accepted_volume_mwh),
                "naive_gap_gbp_per_mwh": str(a.naive_gap_gbp_per_mwh),
                "naive_alt_unit": a.naive_alt_unit,
                "naive_alt_pair_id": a.naive_alt_pair_id,
                "naive_alt_non_deliverable": a.naive_alt_non_deliverable,
                "post_gap_gbp_per_mwh": str(a.post_gap_gbp_per_mwh),
                "post_alt_unit": a.post_alt_unit,
                "post_alt_pair_id": a.post_alt_pair_id,
                "naive_notional_gbp": str(a.naive_notional_gbp),
                "post_notional_gbp": str(a.post_notional_gbp),
            }
            for a in sorted(actions, key=action_key)
        ]
    )
    table.write_parquet(EVIDENCE / "screen.parquet")
    print(json.dumps({k: analysis[k] for k in list(analysis)[1:7]}, indent=1, default=str))
    print(f"screen table: {table.height} accepted actions")


def top_survivors(n: int = ANATOMY_N) -> list[dict]:
    table = pl.read_parquet(EVIDENCE / "screen.parquet")
    rows = [r for r in table.iter_rows(named=True) if Decimal(r["post_gap_gbp_per_mwh"]) > 0]
    rows.sort(
        key=lambda r: (
            -Decimal(r["post_gap_gbp_per_mwh"]),
            r["settlement_date"],
            r["settlement_period"],
            r["direction"],
            r["accepted_unit"],
            r["accepted_pair_id"],
        )
    )
    return rows[:n]


def boalf_path(settlement_date: str, period: int) -> Path:
    return ANATOMY_RAW / f"boalf_{settlement_date}_p{period:02d}.json"


def fetch_anatomy() -> None:
    jobs = []
    for row in top_survivors():
        date, period = row["settlement_date"], row["settlement_period"]
        destination = boalf_path(date, period)
        if all(job[2] != destination for job in jobs):
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
        journal_path=EVIDENCE / "case-boalf-journal.ndjson",
        manifest_path=EVIDENCE / "case-boalf-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
    )
    print(f"fetched {fetched}, verified and skipped {skipped}")


def anatomy() -> None:
    ms001 = pl.read_parquet(MS001_EVIDENCE / "alternatives.parquet")
    headroom = {
        (
            r["settlement_date"],
            r["settlement_period"],
            r["direction"],
            r["bm_unit"],
            r["pair_id"],
        ): r["headroom_ub_mw"]
        for r in ms001.iter_rows(named=True)
    }
    reference = {
        str(r["elexonBmUnit"]): {
            "fuel": r.get("fuelType"),
            "gsp": r.get("gspGroupName"),
            "type": r.get("bmUnitType"),
        }
        for r in load_records(BMUNITS_PATH)
    }
    cases = []
    for row in top_survivors():
        date, period = row["settlement_date"], row["settlement_period"]
        acceptances = [
            {
                "acceptanceNumber": r["acceptanceNumber"],
                "soFlag": r["soFlag"],
                "storFlag": r["storFlag"],
                "rrFlag": r["rrFlag"],
                "deemedBoFlag": r["deemedBoFlag"],
            }
            for r in load_records(boalf_path(date, period))
            if r["bmUnit"] == row["accepted_unit"]
        ]
        cases.append(
            {
                "action": {
                    k: row[k]
                    for k in (
                        "settlement_date",
                        "settlement_period",
                        "direction",
                        "accepted_unit",
                        "accepted_pair_id",
                    )
                },
                "post_gap_gbp_per_mwh": row["post_gap_gbp_per_mwh"],
                "accepted_unit_reference": reference.get(row["accepted_unit"]),
                "accepted_unit_boalf": acceptances,
                "accepted_any_so_flag": any(a["soFlag"] for a in acceptances),
                "surviving_alt_unit": row["post_alt_unit"],
                "surviving_alt_reference": reference.get(row["post_alt_unit"]),
                "surviving_alt_headroom_ub_mw": headroom.get(
                    (date, period, row["direction"], row["post_alt_unit"], row["post_alt_pair_id"])
                ),
            }
        )
    summary = {
        "cases": len(cases),
        "accepted_actions_with_any_so_flag": sum(1 for c in cases if c["accepted_any_so_flag"]),
        "accepted_unit_fuel_types": dict(
            Counter((c["accepted_unit_reference"] or {}).get("fuel") or "unknown" for c in cases)
        ),
        "surviving_alt_fuel_types": dict(
            Counter((c["surviving_alt_reference"] or {}).get("fuel") or "unknown" for c in cases)
        ),
        "surviving_alt_gsp_groups": dict(
            Counter((c["surviving_alt_reference"] or {}).get("gsp") or "unknown" for c in cases)
        ),
    }
    (EVIDENCE / "anatomy.json").write_text(
        json.dumps({"summary": summary, "cases": cases}, indent=1, default=str) + "\n"
    )
    print(json.dumps(summary, indent=1))


# --- External validation against NESO's Skip Rates dataset (declared in
# --- METHOD-STUDY-001B.md; resource ids from the official data portal).

NESO_RESOURCES = [
    (
        "NESO-SKIP-INMERIT-ALLBM",
        "ce31e61b-ebc5-4c6f-846f-d5a971e019a0",
        "inmerit_allbm_2026-08.csv",
    ),
    ("NESO-SKIP-EXCLUSIONS", "a82a2a20-6f08-4d7d-a2ed-221527ba75c2", "exclusions_2026-08.csv"),
]


def neso_fetch(*, url: str, destination: Path, dataset: str):
    from grid_mysteries.sources.http import fetch_artifact

    return fetch_artifact(
        url=url,
        destination=destination,
        source=neso.SOURCE,
        dataset=dataset,
        timeout_seconds=180.0,
    )


def fetch_neso() -> None:
    jobs = [
        (dataset, neso.dump_url(resource_id), neso.NESO_RAW / filename)
        for dataset, resource_id, filename in NESO_RESOURCES
    ]
    EVIDENCE.mkdir(exist_ok=True)
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "neso-journal.ndjson",
        manifest_path=EVIDENCE / "neso-manifest.json",
        repo_root=REPO_ROOT,
        fetch=neso_fetch,
        sleep_seconds=0.5,
    )
    print(f"fetched {fetched}, verified and skipped {skipped}")


def spearman(pairs: list[tuple]) -> float | None:
    def ranks(values: list) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranked = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            average = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranked[order[k]] = average
            i = j + 1
        return ranked

    if len(pairs) < 3:
        return None
    xs, ys = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    n = len(pairs)
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    return cov / (var_x * var_y) ** 0.5 if var_x and var_y else None


def neso_compare() -> None:
    window = set(window_dates())
    _ngc_to_elexon, elexon_to_ngc = unit_maps()
    rows = load_alternative_rows(MS001_EVIDENCE / "alternatives.parquet")
    naive, post = intensity_by_cell(rows, elexon_to_ngc)

    inmerit = neso.read_csv("inmerit_allbm_2026-08.csv")
    coverage = Counter(r["date"][:10] for r in inmerit)
    neso_skip: dict[tuple, Decimal] = {}
    for r in inmerit:
        date = r["date"][:10]
        if date not in window or int(r["stage"]) != neso.FINAL_STAGE:
            continue
        key = (date, r["bid_offer"].lower(), r["bm_unit"])
        neso_skip[key] = neso_skip.get(key, Decimal(0)) + Decimal(r["skipped_volume_MWh"] or "0")

    covered_dates = sorted(d for d in window if coverage.get(d))
    cells = {c for c in set(naive) | set(neso_skip) if c[0] in covered_dates}

    def matrix(ours: dict) -> dict:
        counts = Counter(
            (
                "screen_flags" if cell in ours and ours[cell] > 0 else "screen_silent",
                "neso_skip" if neso_skip.get(cell, Decimal(0)) > 0 else "neso_no_skip",
            )
            for cell in cells
        )
        return {
            f"{a}__{b}": counts.get((a, b), 0)
            for a in ("screen_flags", "screen_silent")
            for b in ("neso_skip", "neso_no_skip")
        }

    neso_universe = [c for c in cells if c in neso_skip]
    correlations = {
        "universe": "cells present at NESO stage 5 on covered dates",
        "n_cells": len(neso_universe),
        "naive_intensity_vs_neso_skipped_volume": spearman(
            [(float(naive.get(c, 0)), float(neso_skip[c])) for c in neso_universe]
        ),
        "post_filter_intensity_vs_neso_skipped_volume": spearman(
            [(float(post.get(c, 0)), float(neso_skip[c])) for c in neso_universe]
        ),
    }

    disagreements = sorted(
        (c for c in cells if post.get(c, Decimal(0)) > 0 and neso_skip.get(c, Decimal(0)) == 0),
        key=lambda c: -post[c],
    )
    exclusions = neso.read_csv("exclusions_2026-08.csv")
    exclusion_rows: dict[tuple, list[dict]] = {}
    for r in exclusions:
        key = (r["date"][:10], r["bid_offer"].lower(), r["bm_unit"])
        exclusion_rows.setdefault(key, []).append(r)
    top20 = []
    reason_counter = Counter()
    for cell in disagreements[:20]:
        rows = exclusion_rows.get(cell, [])
        reasons = Counter(r["exclusion_reason"] for r in rows)
        reason_counter.update(reasons)
        top20.append(
            {
                "date": cell[0],
                "direction": cell[1],
                "ngc_unit": cell[2],
                "post_filter_intensity_gbp_per_mwh_periods": str(post[cell]),
                "in_neso_stage5_universe": cell in neso_skip,
                "neso_exclusion_reasons": dict(reasons.most_common()),
                "neso_excluded_volume_mwh": str(
                    sum(Decimal(r["excluded_volume_MWh"] or "0") for r in rows)
                ),
            }
        )

    converse = sum(
        1 for c in cells if neso_skip.get(c, Decimal(0)) > 0 and naive.get(c, Decimal(0)) == 0
    )
    result = {
        "labelling": (
            "NESO's skip methodology is the authoritative external reference, not ground "
            "truth; definitions differ (daily aggregation, availability-based in-merit "
            "stacks), so these are agreement counts, never precision/recall."
        ),
        "window_dates_covered_by_neso": covered_dates,
        "window_dates_missing_from_neso": sorted(window - set(covered_dates)),
        "cells_compared": len(cells),
        "agreement_matrix_naive": matrix(naive),
        "agreement_matrix_post_filter": matrix(post),
        "magnitude_relationship_spearman": correlations,
        "top20_disagreements_post_filter_vs_neso": top20,
        "top20_disagreement_exclusion_reason_totals": dict(reason_counter.most_common()),
        "converse_disagreement_neso_skip_but_naive_silent": converse,
    }
    (EVIDENCE / "neso-comparison.json").write_text(json.dumps(result, indent=1) + "\n")
    summary = {k: result[k] for k in list(result)[1:7]}
    print(json.dumps(summary, indent=1, default=str))


def main() -> None:
    match sys.argv[1:]:
        case ["analyse"]:
            analyse()
        case ["fetch-neso"]:
            fetch_neso()
        case ["neso-compare"]:
            neso_compare()
        case ["fetch-anatomy"]:
            fetch_anatomy()
        case ["anatomy"]:
            anatomy()
        case ["charts"]:
            from render_screen_charts import render  # added with the results

            render()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
