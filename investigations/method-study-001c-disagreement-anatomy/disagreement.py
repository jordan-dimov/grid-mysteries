"""Method Study 001C — disagreement anatomy. See METHOD-STUDY-001C.md.

Entirely offline: reuses 001B's cell definitions and pinned NESO CSVs.
``analyse`` writes ``evidence/disagreement-analysis.json``; ``charts``
renders ``evidence/waterfall.svg``. Interpretation belongs in NOTE.md.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import unit_maps, window_dates
from grid_mysteries.investigations.exclusion_attribution import (
    LAYER_ORDER,
    categorise,
    primary_category,
)
from grid_mysteries.investigations.neso_cells import intensity_by_cell, load_alternative_rows
from grid_mysteries.sources import neso

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent / "evidence"
MS001_EVIDENCE = REPO_ROOT / "investigations" / "method-study-001-phantom-liquidity" / "evidence"

NESO_FINAL_STAGE = neso.FINAL_STAGE


def read_neso_csv(filename: str) -> list[dict]:
    return neso.read_csv(filename)


def our_intensity_by_cell() -> tuple[dict, dict]:
    _ngc_to_elexon, elexon_to_ngc = unit_maps()
    rows = load_alternative_rows(MS001_EVIDENCE / "alternatives.parquet")
    return intensity_by_cell(rows, elexon_to_ngc)


def build_state() -> dict:
    """Everything both subcommands need, computed once from pinned inputs."""
    window = set(window_dates())
    naive, post = our_intensity_by_cell()

    inmerit = read_neso_csv("inmerit_allbm_2026-08.csv")
    neso_skip: dict[tuple, Decimal] = {}
    neso_accepted: dict[tuple, Decimal] = {}
    neso_in_merit: dict[tuple, Decimal] = {}
    for r in inmerit:
        date = r["date"][:10]
        if date not in window or int(r["stage"]) != NESO_FINAL_STAGE:
            continue
        key = (date, r["bid_offer"].lower(), r["bm_unit"])
        neso_skip[key] = neso_skip.get(key, Decimal(0)) + Decimal(r["skipped_volume_MWh"] or "0")
        neso_accepted[key] = neso_accepted.get(key, Decimal(0)) + abs(
            Decimal(r["accepted_volume_MWh"] or "0")
        )
        neso_in_merit[key] = neso_in_merit.get(key, Decimal(0)) + abs(
            Decimal(r["in_merit_volume_MWh"] or "0")
        )

    exclusion_rows: dict[tuple, list[dict]] = {}
    for r in read_neso_csv("exclusions_2026-08.csv"):
        date = r["date"][:10]
        if date in window:
            exclusion_rows.setdefault((date, r["bid_offer"].lower(), r["bm_unit"]), []).append(r)

    naive_flagged = {cell for cell, intensity in naive.items() if intensity > 0}
    flagged = {cell for cell, intensity in post.items() if intensity > 0}
    return {
        "post": post,
        "naive_flagged": naive_flagged,
        "flagged": flagged,
        "neso_skip": neso_skip,
        "neso_accepted": neso_accepted,
        "neso_in_merit": neso_in_merit,
        "exclusion_rows": exclusion_rows,
        # Correction (recorded in METHOD-STUDY-001C.md): the comparison
        # universe is 001B's fixed universe — naive-flagged cells union the
        # NESO stage-5 universe — so every layer's rate is comparable.
        "cells": naive_flagged | set(neso_skip),
    }


def agreement(flagged: set, state: dict) -> dict:
    neso_skip = state["neso_skip"]
    cells = state["cells"]
    catches = sum(1 for c in cells if c in flagged and neso_skip.get(c, Decimal(0)) > 0)
    false_alarms = sum(1 for c in cells if c in flagged and neso_skip.get(c, Decimal(0)) == 0)
    silent_no_skip = sum(1 for c in cells if c not in flagged and neso_skip.get(c, Decimal(0)) == 0)
    total_skips = sum(1 for c in cells if neso_skip.get(c, Decimal(0)) > 0)
    return {
        "agreement_rate": (catches + silent_no_skip) / len(cells),
        "neso_skips_caught": catches,
        "neso_skips_total": total_skips,
        "false_alarms": false_alarms,
    }


def analyse() -> None:
    state = build_state()
    flagged, neso_skip = state["flagged"], state["neso_skip"]
    exclusion_rows = state["exclusion_rows"]

    disagreement = sorted(c for c in flagged if neso_skip.get(c, Decimal(0)) == 0)

    primary = Counter()
    any_presence = Counter()
    by_direction = Counter()
    unmatched_cells = []
    for cell in disagreement:
        by_direction[cell[1]] += 1
        rows = exclusion_rows.get(cell, [])
        category = primary_category(rows)
        if category is None:
            in_merit = state["neso_in_merit"].get(cell)
            if in_merit is None:
                category = "absent_from_neso_universe"
            elif state["neso_accepted"].get(cell, Decimal(0)) >= in_merit:
                category = "fully_accepted_in_merit"
            else:
                category = "unmatched"
                unmatched_cells.append(cell)
        primary[category] += 1
        for row in rows:
            for cat in set(categorise(row["exclusion_reason"])):
                any_presence[cat] += 1

    waterfall = [{"layer": "naive_price_screen", **agreement(state["naive_flagged"], state)}]
    current = set(flagged)
    waterfall.append({"layer": "physical_deliverability", **agreement(current, state)})
    for category in LAYER_ORDER:
        removed = {
            cell
            for cell in current
            if any(
                category in categorise(row["exclusion_reason"])
                for row in exclusion_rows.get(cell, [])
            )
        }
        if not removed:
            continue
        current -= removed
        waterfall.append(
            {
                "layer": f"minus_{category}",
                "cells_unflagged": len(removed),
                **agreement(current, state),
            }
        )

    residual_flagged = sorted(current, key=lambda c: -state["post"][c])
    analysis = {
        "corpus": {"window": [window_dates()[0], window_dates()[-1]]},
        "disagreement_cells": len(disagreement),
        "by_direction": dict(by_direction),
        "primary_attribution": dict(primary.most_common()),
        "any_presence_of_category": dict(any_presence.most_common()),
        "unmatched_cells": len(unmatched_cells),
        "unmatched_cell_list": [
            {
                "date": c[0],
                "direction": c[1],
                "ngc_unit": c[2],
                "intensity": str(state["post"][c]),
            }
            for c in unmatched_cells
        ],
        "waterfall": waterfall,
        "final_layer_flagged_cells": len(current),
        "final_layer_top10_by_intensity": [
            {
                "date": c[0],
                "direction": c[1],
                "ngc_unit": c[2],
                "intensity": str(state["post"][c]),
                "neso_skip": str(neso_skip.get(c, Decimal(0))),
            }
            for c in residual_flagged[:10]
        ],
    }
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "disagreement-analysis.json").write_text(
        json.dumps(analysis, indent=1, default=str) + "\n"
    )
    print(json.dumps({k: analysis[k] for k in list(analysis)[1:6]}, indent=1, default=str))
    print(json.dumps(analysis["waterfall"], indent=1, default=str))


def main() -> None:
    match sys.argv[1:]:
        case ["analyse"]:
            analyse()
        case ["charts"]:
            from render_waterfall import render  # added with the results

            render()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
