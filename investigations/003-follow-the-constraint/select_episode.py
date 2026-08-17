"""Investigation 003 stage 2: run the frozen selection rule ONCE.

Computes silently over the closed May corpus and reports only the
selected episode and the declared coverage outputs — no leaderboard of
candidates is printed or stored; the code recomputes deterministically
for anyone reproducing the selection.
"""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal

from acquire import EVIDENCE, PN_RAW, RAW, may_dates

from grid_mysteries.corpus import PERIODS, load_records, unit_maps
from grid_mysteries.investigations.constraint_episodes import (
    ScoredEpisode,
    episodes,
    repeat_curtailment_cycles,
    select,
)
from grid_mysteries.sources import neso

MAY = set(may_dates())


def may_episodes():
    rows = [
        r
        for r in neso.read_csv("thermal_constraint_costs_data_26-27.csv")
        if str(r["Settlement Date"])[:10] in MAY
    ]
    return episodes(rows)


def storage_universe() -> tuple[list[str], list[str]]:
    """(mapped elexon ids, unmapped NGC ids) from the pinned NESO list."""
    ngc_units = json.loads((EVIDENCE / "storage-units.json").read_text())
    ngc_to_elexon, _ = unit_maps()
    mapped, unmapped = [], []
    for unit in ngc_units:
        if unit in ngc_to_elexon:
            mapped.append(ngc_to_elexon[unit])
        else:
            unmapped.append(unit)
    return sorted(set(mapped)), sorted(unmapped)


def export_periods_by_unit(units: set[str]) -> dict[str, set]:
    exports: dict[str, set] = defaultdict(set)
    for day in may_dates():
        for r in load_records(PN_RAW / f"pn_{day}.json"):
            unit = str(r["bmUnit"])
            if unit in units and max(Decimal(str(r["levelFrom"])), Decimal(str(r["levelTo"]))) > 0:
                exports[unit].add((str(r["settlementDate"]), int(r["settlementPeriod"])))
    return exports


def bid_downs_by_unit(units: set[str]) -> tuple[dict[str, set], dict[tuple, Decimal]]:
    """Per-unit bid-down period sets, and per (unit, date) bid-down MWh."""
    bid_down: dict[str, set] = defaultdict(set)
    mwh: dict[tuple, Decimal] = defaultdict(Decimal)
    fields = [f"negative{i}" for i in range(1, 7)]
    for day in may_dates():
        for period in PERIODS:
            for r in load_records(RAW / day / f"disptav_bid_p{period:02d}.json"):
                unit = str(r["bmUnit"])
                if unit not in units or r.get("dataType") != "Original":
                    continue
                volumes = r.get("pairVolumes") or {}
                total = sum(
                    (abs(Decimal(str(volumes[f]))) for f in fields if volumes.get(f) is not None),
                    Decimal(0),
                )
                if total > 0:
                    bid_down[unit].add((day, period))
                    mwh[(unit, day)] += total
        print(f"scanned {day}", flush=True)
    return bid_down, mwh


def run() -> None:
    mapped, unmapped = storage_universe()
    units = set(mapped)
    exports = export_periods_by_unit(units)
    bid_down, mwh = bid_downs_by_unit(units)

    scored = []
    for episode in may_episodes():
        dates = set(episode.dates)
        score = 0
        volume = Decimal(0)
        for unit in units:
            bd = {k for k in bid_down.get(unit, ()) if k[0] in dates}
            ex = {k for k in exports.get(unit, ()) if k[0] in dates}
            score += repeat_curtailment_cycles(bd, ex)
            volume += sum((mwh[(unit, day)] for day in dates), Decimal(0))
        scored.append(ScoredEpisode(episode, score, volume))

    winner = select(scored)
    coverage = {
        "storage_units_declared": len(mapped) + len(unmapped),
        "mapped_to_elexon_ids": len(mapped),
        "unmapped_ngc_ids": unmapped,
        "units_with_any_may_export_pn": sum(1 for u in units if exports.get(u)),
        "units_with_any_may_bid_down": sum(1 for u in units if bid_down.get(u)),
        "episodes_in_window": len(scored),
    }
    result = {
        "selected": None
        if winner is None
        else {
            "constraint_group": winner.episode.constraint_group,
            "dates": list(winner.episode.dates),
            "repeat_curtailment_score": winner.score,
            "storage_bid_down_mwh": str(winner.storage_bid_down_mwh),
        },
        "coverage": coverage,
    }
    (EVIDENCE / "selected-episode.json").write_text(json.dumps(result, indent=1) + "\n")
    if winner is None:
        print("Selected: none — no episode has a positive score (not evaluable)")
    else:
        print(
            f"Selected: constraint group {winner.episode.constraint_group}, "
            f"{winner.episode.start} to {winner.episode.end}"
        )
        print(f"repeat-curtailment score: {winner.score}")
        print(f"storage bid-down volume: {winner.storage_bid_down_mwh:.0f} MWh")


if __name__ == "__main__":
    run()
