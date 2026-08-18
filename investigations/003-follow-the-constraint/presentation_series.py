"""Presentation series for Publication Pack 003.

Post-selection description only: no new analytical claim, no new rule.
Produces evidence/presentation-series.json holding (a) the per-day
14-day series — NESO's published daily SSE-SP outturn cost (observed,
boundary-specific) beside the GB-wide single-day repeat-curtailment
cycle count and bid-down MWh (concurrence, never attribution) — and
(b) the focus unit's excerpt-day trajectory: per-period final-PN
schedule extremes, deepest instructed level, acceptance and SO-flag
counts. Rendering reads this file and never recomputes.
"""

from __future__ import annotations

import json
from decimal import Decimal

from acquire import EVIDENCE, PN_RAW, RAW
from reconstruct import selected, storage_elexon_units, unit_day_signals

from grid_mysteries.corpus import PERIODS, load_records
from grid_mysteries.investigations.constraint_episodes import repeat_curtailment_cycles
from grid_mysteries.sources import neso


def daily_costs(group: str, dates: list[str]) -> dict[str, str]:
    costs = {}
    for r in neso.read_csv("thermal_constraint_costs_data_26-27.csv"):
        day = str(r["Settlement Date"])[:10]
        if str(r["Constraint Group"]) == group and day in dates:
            costs[day] = str(Decimal(str(r["Daily Cost (GBP)"]).strip() or "0"))
    return costs


def day_series(dates: list[str], units: set[str]) -> list[dict]:
    bid_down, exports, mwh = unit_day_signals(dates, units)
    series = []
    for day in dates:
        cycles = sum(
            repeat_curtailment_cycles(
                {k for k in bid_down[u] if k[0] == day},
                {k for k in exports[u] if k[0] == day},
            )
            for u in units
        )
        volume = sum((mwh[(u, day)] for u in units), Decimal(0))
        series.append({"date": day, "gb_cycles": cycles, "gb_bid_down_mwh": str(volume)})
    return series


def focus_trajectory(day: str, unit: str) -> list[dict]:
    schedule: dict[int, list[Decimal]] = {p: [] for p in PERIODS}
    for r in load_records(PN_RAW / f"pn_{day}.json"):
        if str(r["bmUnit"]) == unit and str(r["settlementDate"]) == day:
            schedule[int(r["settlementPeriod"])] += [
                Decimal(str(r["levelFrom"])),
                Decimal(str(r["levelTo"])),
            ]
    trajectory = []
    for period in PERIODS:
        accepted: list[Decimal] = []
        acceptances: set[int] = set()
        so_flagged: set[int] = set()
        for r in load_records(RAW / day / f"boalf_p{period:02d}.json"):
            if str(r["bmUnit"]) == unit:
                accepted += [Decimal(str(r["levelFrom"])), Decimal(str(r["levelTo"]))]
                acceptances.add(int(r["acceptanceNumber"]))
                if bool(r["soFlag"]):
                    so_flagged.add(int(r["acceptanceNumber"]))
        levels = schedule[period]
        trajectory.append(
            {
                "period": period,
                "fpn_max_mw": str(max(levels)) if levels else None,
                "fpn_min_mw": str(min(levels)) if levels else None,
                "instructed_min_mw": str(min(accepted)) if accepted else None,
                "acceptances": len(acceptances),
                "so_flagged": len(so_flagged),
            }
        )
    return trajectory


def run() -> None:
    episode = selected()
    excerpt = json.loads((EVIDENCE / "excerpt.json").read_text())
    units = storage_elexon_units()
    dates = list(episode["dates"])
    costs = daily_costs(episode["constraint_group"], dates)
    series = day_series(dates, units)
    for row in series:
        row["published_group_cost_gbp"] = costs.get(row["date"], "0")
    out = {
        "labelling": (
            "Daily published cost is NESO's outturn for the constraint group "
            "(observed, boundary-specific, daily grain). Cycle counts and MWh are "
            "GB-wide storage activity on the same dates — concurrence, not "
            "attribution to the boundary. Single-day cycles are computed within "
            "each date alone, so they need not sum to the episode score."
        ),
        "constraint_group": episode["constraint_group"],
        "days": series,
        "focus": {
            "unit": excerpt["focus_unit"],
            "day": excerpt["excerpt_day"],
            "trajectory": focus_trajectory(excerpt["excerpt_day"], excerpt["focus_unit"]),
        },
    }
    (EVIDENCE / "presentation-series.json").write_text(json.dumps(out, indent=1) + "\n")
    total = sum(Decimal(r["published_group_cost_gbp"]) for r in series)
    print(f"days: {len(series)}, group cost total: {total:.0f} GBP")
    active = sum(1 for t in out["focus"]["trajectory"] if t["acceptances"])
    print(f"focus periods with acceptances: {active}")


if __name__ == "__main__":
    run()
