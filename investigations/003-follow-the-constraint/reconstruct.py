"""Investigation 003 stage 3: reconstruction of the selected episode.

Usage:
    uv run python investigations/003-follow-the-constraint/reconstruct.py excerpt
    uv run python investigations/003-follow-the-constraint/reconstruct.py ledger

The full 14-day ledger is the result; the illustrative reel is an
excerpt chosen by a MECHANICAL rule declared here before it runs, so the
"vivid afternoon" selects itself:

- **Excerpt day**: the episode settlement date with the highest
  single-day repeat-curtailment cycle count across storage units
  (cycles computed within that date alone); ties by greater storage
  bid-down MWh that day, then earlier date.
- **Focus unit**: on the excerpt day, the storage unit with the most
  cycles; ties by greater bid-down MWh that day, then unit id.

Language contracts, binding on every generated frame: cycles are
"repeat-curtailment cycles consistent with RRT", never re-trades; the
commercial step between two instructions is a not-publicly-observable
frame that can carry no amount; concurrent offer-side acceptances are
described as CONCURRENT — causal substitution is never asserted; the
episode is right-censored by the declared window and says so.
"""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal

from acquire import EVIDENCE, PN_RAW, RAW

from grid_mysteries.corpus import PERIODS, load_records, unit_maps
from grid_mysteries.investigations.constraint_episodes import repeat_curtailment_cycles
from grid_mysteries.investigations.event_ledger import (
    LedgerEntry,
    ordered,
    parse_ebocf_record,
    period_gaps,
)
from grid_mysteries.sources import neso


def selected() -> dict:
    return json.loads((EVIDENCE / "selected-episode.json").read_text())["selected"]


def storage_elexon_units() -> set[str]:
    ngc_units = json.loads((EVIDENCE / "storage-units.json").read_text())
    ngc_to_elexon, _ = unit_maps()
    return {ngc_to_elexon.get(u, u) for u in ngc_units}


def unit_day_signals(dates: list[str], units: set[str]):
    """(bid-down period sets, export period sets, bid-down MWh) per unit,
    restricted to the episode dates."""
    bid_down: dict[str, set] = defaultdict(set)
    exports: dict[str, set] = defaultdict(set)
    mwh: dict[tuple, Decimal] = defaultdict(Decimal)
    fields = [f"negative{i}" for i in range(1, 7)]
    for day in dates:
        for r in load_records(PN_RAW / f"pn_{day}.json"):
            unit = str(r["bmUnit"])
            if (
                unit in units
                and str(r["settlementDate"]) in dates
                and max(Decimal(str(r["levelFrom"])), Decimal(str(r["levelTo"]))) > 0
            ):
                exports[unit].add((str(r["settlementDate"]), int(r["settlementPeriod"])))
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
    return bid_down, exports, mwh


def pick_excerpt() -> None:
    episode = selected()
    dates = episode["dates"]
    units = storage_elexon_units()
    bid_down, exports, mwh = unit_day_signals(dates, units)

    def day_stats(day: str):
        cycles = sum(
            repeat_curtailment_cycles(
                {k for k in bid_down[u] if k[0] == day},
                {k for k in exports[u] if k[0] == day},
            )
            for u in units
        )
        volume = sum((mwh[(u, day)] for u in units), Decimal(0))
        return cycles, volume

    stats = {day: day_stats(day) for day in dates}
    excerpt_day = min(dates, key=lambda d: (-stats[d][0], -stats[d][1], d))

    def unit_stats(unit: str):
        cycles = repeat_curtailment_cycles(
            {k for k in bid_down[unit] if k[0] == excerpt_day},
            {k for k in exports[unit] if k[0] == excerpt_day},
        )
        return cycles, mwh[(unit, excerpt_day)]

    focus_unit = min(sorted(units), key=lambda u: (-unit_stats(u)[0], -unit_stats(u)[1], u))
    result = {
        "rule": "max single-day cycles; ties by bid-down MWh, then date/unit id",
        "excerpt_day": excerpt_day,
        "excerpt_day_cycles": stats[excerpt_day][0],
        "excerpt_day_bid_down_mwh": str(stats[excerpt_day][1]),
        "focus_unit": focus_unit,
        "focus_unit_cycles": unit_stats(focus_unit)[0],
        "focus_unit_bid_down_mwh": str(unit_stats(focus_unit)[1]),
    }
    (EVIDENCE / "excerpt.json").write_text(json.dumps(result, indent=1) + "\n")
    print(f"Excerpt day: {excerpt_day} ({stats[excerpt_day][0]} cycles)")
    print(f"Focus unit: {focus_unit} ({unit_stats(focus_unit)[0]} cycles)")


def build_ledger() -> None:
    episode = selected()
    excerpt = json.loads((EVIDENCE / "excerpt.json").read_text())
    day, unit = excerpt["excerpt_day"], excerpt["focus_unit"]
    _, elexon_to_ngc = unit_maps()
    ngc = elexon_to_ngc.get(unit, unit)

    entries: list[LedgerEntry] = []

    # Constraint context (day-ahead forecast; daily outturn cost).
    for r in neso.read_csv("thermal_constraint_costs_data_26-27.csv"):
        if (
            str(r["Settlement Date"])[:10] == day
            and r["Constraint Group"] == episode["constraint_group"]
        ):
            entries.append(
                LedgerEntry(
                    day,
                    1,
                    episode["constraint_group"],
                    f"published daily outturn thermal constraint cost for the group: "
                    f"GBP {r['Daily Cost (GBP)']} (daily grain; does not localise cost "
                    "to any period or unit)",
                    "observed",
                )
            )

    # The focus unit's export schedule (final vintages).
    for r in load_records(PN_RAW / f"pn_{day}.json"):
        if str(r["bmUnit"]) == unit and str(r["settlementDate"]) == day:
            level = max(Decimal(str(r["levelFrom"])), Decimal(str(r["levelTo"])))
            if level > 0:
                entries.append(
                    LedgerEntry(
                        day,
                        int(r["settlementPeriod"]),
                        unit,
                        f"final physical notification schedules export "
                        f"(up to {level} MW; final vintage — intra-period "
                        "revision history is not public)",
                        "observed",
                        sequence_time=str(r["timeFrom"]),
                    )
                )

    # Bid-down acceptances with timestamps.
    for period in PERIODS:
        for r in load_records(RAW / day / f"boalf_p{period:02d}.json"):
            if str(r["bmUnit"]) == unit:
                entries.append(
                    LedgerEntry(
                        day,
                        period,
                        unit,
                        f"acceptance {r['acceptanceNumber']} instructs "
                        f"{r['levelFrom']}→{r['levelTo']} MW"
                        + (" (SO-flagged)" if r.get("soFlag") else ""),
                        "observed",
                        sequence_time=str(r["acceptanceTime"]),
                    )
                )

    # Published indicative BM cashflows for the unit's bid pairs.
    for direction in ("bid", "offer"):
        for r in load_records(RAW / day / f"ebocf_{direction}.json"):
            if str(r["bmUnit"]) == unit:
                rec = parse_ebocf_record(r)
                if rec.total_cashflow != 0:
                    entries.append(
                        LedgerEntry(
                            day,
                            rec.settlement_period,
                            unit,
                            f"published indicative BM {direction} cashflow "
                            f"(latest settlement run, vintage {rec.created[:10]})",
                            "observed",
                            amount_gbp=rec.reconciled_total(),
                            money_kind="published_indicative_bm_cashflow",
                        )
                    )

    # The unprovable middle, placed once per reel.
    entries.append(
        LedgerEntry(
            day,
            25,
            unit,
            "whether energy retained through curtailment was re-sold in the "
            "intraday market between instructions — the step Ofgem's mechanism "
            "names — is not in the public record",
            "not_publicly_observable",
        )
    )

    # Concurrent offer-side acceptances by non-storage units (concurrency
    # observed; substitution never asserted).
    storage = storage_elexon_units()
    concurrent: dict[int, Decimal] = defaultdict(Decimal)
    for r in load_records(RAW / day / "ebocf_offer.json"):
        if str(r["bmUnit"]) not in storage:
            rec = parse_ebocf_record(r)
            if rec.total_cashflow != 0:
                concurrent[rec.settlement_period] += rec.reconciled_total()
    for period, total in sorted(concurrent.items()):
        entries.append(
            LedgerEntry(
                day,
                period,
                "non-storage units (aggregate)",
                "CONCURRENT offer-side published indicative BM cashflow across "
                "non-storage units (concurrency observed; causal substitution "
                "for any curtailment is not asserted)",
                "observed",
                amount_gbp=total,
                money_kind="published_indicative_bm_cashflow",
            )
        )

    timeline = ordered(entries)
    gaps = period_gaps(timeline)
    out = {
        "episode": episode,
        "right_censored": "the episode ends at the declared window edge (2026-05-31); "
        "it may continue beyond it",
        "excerpt": excerpt,
        "focus_unit_ngc": ngc,
        "frames": [
            {
                "date": e.settlement_date,
                "period": e.settlement_period,
                "actor": e.actor,
                "column": e.column,
                "description": e.description,
                "sequence_time": e.sequence_time,
                "amount_gbp": str(e.amount_gbp) if e.amount_gbp is not None else None,
                "money_kind": e.money_kind,
            }
            for e in timeline
        ],
        "period_gaps": gaps,
    }
    (EVIDENCE / "episode-ledger.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"ledger: {len(timeline)} frames, {len(gaps)} period gaps surfaced")


def main() -> None:
    import sys

    match sys.argv[1:]:
        case ["excerpt"]:
            pick_excerpt()
        case ["ledger"]:
            build_ledger()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
