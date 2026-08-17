"""BESS Study 001 analysis: the five-rung Benchmark Fragility table.

Implements METHOD-STUDY-BESS-001.md exactly as declared. For each panel
unit, July settlement period and direction: apparent opportunity =
best gap × min(rung bound MWh, worse-priced accepted MWh), where only
the unit's bound changes per rung. Missing duration data is unknown,
never a fallback. Every price and volume is Decimal.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from bench import EVIDENCE, REPO_ROOT, july_dates
from panel import PHYSICAL_RAW, load_envelopes, period_window

from grid_mysteries.corpus import BMUNITS_PATH, load_records, unit_maps
from grid_mysteries.investigations.duration_envelope import energy_bound_mwh
from grid_mysteries.investigations.phantom_liquidity import headroom_upper_bound, level_extremes
from grid_mysteries.sources import neso

RAW = REPO_ROOT / "data" / "raw" / "elexon"
HALF_HOUR = Decimal("0.5")
CUTOFF_MINUTES = 60  # the declared decision cutoff: period start minus 60 minutes
RUNGS = (
    "r1_price_only",
    "r2_power_feasible",
    "r3h_duration_hindsight",
    "r3p_duration_public",
    "r4_context_free",
)


def d(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def unit_bod_and_market(
    bod_records: list[dict], unit: str, direction: str
) -> tuple[Decimal | None, Decimal]:
    """(unit's best price, unit's max band MW) for the direction."""
    price_field = "offer" if direction == "offer" else "bid"
    best_price: Decimal | None = None
    band = Decimal(0)
    for r in bod_records:
        if str(r["bmUnit"]) != unit:
            continue
        pair_id = int(r["pairId"])
        if (direction == "offer") != (pair_id > 0) or r.get(price_field) is None:
            continue
        price = d(r[price_field])
        band = max(band, abs(d(r["levelFrom"])), abs(d(r["levelTo"])))
        if (
            best_price is None
            or (direction == "offer" and price < best_price)
            or (direction == "bid" and price > best_price)
        ):
            best_price = price
    return best_price, band


def accepted_actions(
    disptav_records: list[dict], bod_records: list[dict], unit: str, direction: str
) -> list[tuple[str, Decimal, Decimal]]:
    """(accepted unit, its best pair price, |accepted MWh|) for others' actions."""
    price_field = "offer" if direction == "offer" else "bid"
    prices: dict[str, Decimal] = {}
    for r in bod_records:
        other = str(r["bmUnit"])
        pair_id = int(r["pairId"])
        if other == unit or (direction == "offer") != (pair_id > 0) or r.get(price_field) is None:
            continue
        price = d(r[price_field])
        if (
            other not in prices
            or (direction == "offer" and price < prices[other])
            or (direction == "bid" and price > prices[other])
        ):
            prices[other] = price
    actions = []
    for r in disptav_records:
        other = str(r["bmUnit"])
        if other == unit or r.get("dataType") != "Original" or not r.get("totalVolumeAccepted"):
            continue
        if other in prices:
            actions.append((other, prices[other], abs(d(r["totalVolumeAccepted"]))))
    return actions


def load_physical_by_day() -> dict[tuple[str, str, str], list[dict]]:
    """(dataset, day, unit) -> stream records."""
    physical: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for dataset in ("PN", "MELS", "MILS"):
        for day in july_dates():
            for r in load_records(PHYSICAL_RAW / f"{dataset.lower()}_{day}.json"):
                physical[(dataset, r["settlementDate"], str(r["bmUnit"]))].append(r)
    return physical


def load_context_presence() -> set[tuple[str, str, str]]:
    """(date, direction, NGC unit) with any NESO July exclusion row."""
    present = set()
    for r in neso.read_csv("exclusions_2026-07.csv"):
        present.add((r["date"][:10], r["bid_offer"].lower(), r["bm_unit"]))
    return present


def run_analyse() -> None:
    panel = json.loads((EVIDENCE / "panel.json").read_text())["panel"]
    envelopes = load_envelopes()
    physical = load_physical_by_day()
    context = load_context_presence()
    _ngc_to_elexon, elexon_to_ngc = unit_maps()
    capacities = {
        str(r["elexonBmUnit"]): (
            Decimal(r["generationCapacity"]) if r.get("generationCapacity") is not None else None,
            Decimal(r["demandCapacity"]) if r.get("demandCapacity") is not None else None,
        )
        for r in load_records(BMUNITS_PATH)
    }

    totals: dict[tuple, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    unknown_public: dict[tuple, int] = defaultdict(int)
    unknown_carried_r2: dict[tuple, Decimal] = defaultdict(Decimal)
    hindsight_gt_public_periods: dict[tuple, int] = defaultdict(int)
    context_present_gbp: dict[tuple, Decimal] = defaultdict(Decimal)
    opportunity_periods: dict[tuple, int] = defaultdict(int)

    for day in july_dates():
        for period in range(1, 49):
            bod_records = load_records(RAW / day / f"bod_p{period:02d}.json")
            start, end = period_window(day, period)
            cutoff = start - timedelta(minutes=CUTOFF_MINUTES)
            for direction in ("offer", "bid"):
                disptav = load_records(RAW / day / f"disptav_{direction}_p{period:02d}.json")
                for unit in panel:
                    key = (unit, direction)
                    best_price, band = unit_bod_and_market(bod_records, unit, direction)
                    if best_price is None or band < 1:
                        continue
                    actions = accepted_actions(disptav, bod_records, unit, direction)
                    if direction == "offer":
                        worse = [(u, p, v) for u, p, v in actions if p > best_price]
                        gap = max((p - best_price for _, p, _ in worse), default=Decimal(0))
                    else:
                        worse = [(u, p, v) for u, p, v in actions if p < best_price]
                        gap = max((best_price - p for _, p, _ in worse), default=Decimal(0))
                    if gap <= 0:
                        continue
                    worse_mwh = sum((v for _, _, v in worse), Decimal(0))
                    opportunity_periods[key] += 1

                    r1 = band * HALF_HOUR
                    pn_recs = physical.get(("PN", day, unit), [])
                    mels_recs = physical.get(("MELS", day, unit), [])
                    mils_recs = physical.get(("MILS", day, unit), [])

                    def period_slice(recs, period=period):
                        return [r for r in recs if int(r["settlementPeriod"]) == period]

                    fpn_e = level_extremes(period_slice(pn_recs)).get(unit)
                    mels_e = level_extremes(period_slice(mels_recs)).get(unit)
                    mils_e = level_extremes(period_slice(mils_recs)).get(unit)
                    generation, demand = capacities.get(unit, (None, None))
                    bound = headroom_upper_bound(
                        direction,
                        fpn=fpn_e,
                        mels=mels_e,
                        mils=mils_e,
                        generation_capacity=generation,
                        demand_capacity=demand,
                    )
                    r2 = max(bound, Decimal(0)) * HALF_HOUR if bound is not None else None
                    dataset = "MDO" if direction == "offer" else "MDB"
                    env = envelopes.get((unit, dataset), [])
                    relevant = [r for r in env if r.time_from < end and r.time_to > start]
                    e_hind = energy_bound_mwh(relevant, start, end, None)
                    e_pub = energy_bound_mwh(relevant, start, end, cutoff)

                    def opportunity(
                        bound_mwh: Decimal | None, gap=gap, worse_mwh=worse_mwh
                    ) -> Decimal | None:
                        if bound_mwh is None:
                            return None
                        return gap * min(bound_mwh, worse_mwh)

                    values = {
                        "r1_price_only": opportunity(r1),
                        "r2_power_feasible": opportunity(r2) if r2 is not None else None,
                        "r3h_duration_hindsight": opportunity(min(r2, e_hind))
                        if r2 is not None and e_hind is not None
                        else None,
                        "r3p_duration_public": opportunity(min(r2, e_pub))
                        if r2 is not None and e_pub is not None
                        else None,
                    }
                    for rung, value in values.items():
                        if value is not None:
                            totals[key][rung] += value
                    if values["r3p_duration_public"] is None:
                        unknown_public[key] += 1
                        if values["r2_power_feasible"] is not None:
                            unknown_carried_r2[key] += values["r2_power_feasible"]
                    elif (
                        values["r3h_duration_hindsight"] is not None
                        and values["r3h_duration_hindsight"] > values["r3p_duration_public"]
                    ):
                        hindsight_gt_public_periods[key] += 1
                    if values["r3p_duration_public"] is not None:
                        ngc = elexon_to_ngc.get(unit, unit)
                        flagged = (day, direction, ngc) in context or any(
                            (day, direction, elexon_to_ngc.get(u, u)) in context
                            for u, _, _ in worse
                        )
                        if flagged:
                            context_present_gbp[key] += values["r3p_duration_public"]
                        else:
                            totals[key]["r4_context_free"] += values["r3p_duration_public"]
        print(f"analysed {day}", flush=True)

    def serialise(mapping):
        return {f"{unit}|{direction}": str(v) for (unit, direction), v in mapping.items()}

    result = {
        "panel": panel,
        "per_unit_direction": {
            f"{unit}|{direction}": {
                rung: str(totals[(unit, direction)].get(rung, Decimal(0))) for rung in RUNGS
            }
            for (unit, direction) in sorted(totals)
        },
        "pooled": {
            rung: str(sum((t.get(rung, Decimal(0)) for t in totals.values()), Decimal(0)))
            for rung in RUNGS
        },
        "opportunity_periods": {
            f"{u}|{dn}": n for (u, dn), n in sorted(opportunity_periods.items())
        },
        "unknown_public_periods": {f"{u}|{dn}": n for (u, dn), n in sorted(unknown_public.items())},
        "unknown_carried_r2_gbp": serialise(unknown_carried_r2),
        "hindsight_exceeds_public_periods": {
            f"{u}|{dn}": n for (u, dn), n in sorted(hindsight_gt_public_periods.items())
        },
        "r3p_context_present_gbp": serialise(context_present_gbp),
    }
    (EVIDENCE / "fragility-analysis.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result["pooled"], indent=1))


if __name__ == "__main__":
    run_analyse()
