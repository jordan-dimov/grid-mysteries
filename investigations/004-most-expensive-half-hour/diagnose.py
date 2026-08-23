"""Investigation 004: the chronological diagnostic across the episode.

    uv run python investigations/004-most-expensive-half-hour/diagnose.py

Descriptive only — no new selection, no ranking that could become one.
p42 was chosen mechanically; p36..p45 is post-selection context the
reconstruction has to answer to.

FOUR ACCOUNTING LAYERS ARE KEPT VISIBLY SEPARATE, and are never summed
together or reconciled to one another:

1. **NESO published `Constraints` £** — the authoritative category total
   at settlement-period level. NESO's own attribution; the mapping from
   individual acceptances into it is not public.
2. **Published BM acceptance volume and indicative cashflow (EBOCF)** —
   attributable to units, but NOT automatically members of layer 1.
3. **Disaggregated BSAD** — observed non-BM adjustment money. Its
   `TradeFlag` `T` means "system issue such as a constraint", which is
   contextual evidence only, never category membership.
4. **Daily Balancing Volume constraint bid/offer MWh** — published
   physical scale, never a per-unit decomposition of layer 1.

The declaration is explicit that public data may not permit layer 1 to
be rebuilt from layer 2. The question is what physical operation
coincided with it and how much of that is independently reconstructable.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from decimal import Decimal

from acquire import EVIDENCE, RAW

from grid_mysteries.corpus import fuel_types, load_records, window_path
from grid_mysteries.investigations.bod_inversion import accepted_volume_mwh
from grid_mysteries.investigations.period_costs import parse_cost_rows
from grid_mysteries.sources import neso

EPISODE = range(36, 46)
DIRECTIONS = ("offer", "bid")
#: An acceptance is "material" at or above this MWh; declared here as a
#: reporting threshold for the diagnostic, never a selection rule.
MATERIAL_MWH = Decimal("1")


def accepted_volumes(day: str, period: int) -> dict[str, dict[str, Decimal]]:
    """Per-unit accepted MWh by direction, from DISPTAV `Original` rows."""
    volumes: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"offer": Decimal(0), "bid": Decimal(0)}
    )
    for direction in DIRECTIONS:
        for record in load_records(window_path(f"disptav_{direction}", day, period)):
            if record.get("dataType") != "Original":
                continue
            total = accepted_volume_mwh(record)
            if total:
                volumes[str(record["bmUnit"])][direction] += total
    return volumes


def cashflows(day: str) -> dict[int, dict[str, dict[str, Decimal]]]:
    """Per-period, per-unit published indicative BM cashflow by direction."""
    result: dict[int, dict[str, dict[str, Decimal]]] = defaultdict(
        lambda: defaultdict(lambda: {"offer": Decimal(0), "bid": Decimal(0)})
    )
    for direction in DIRECTIONS:
        for record in load_records(RAW / day / f"ebocf_{direction}.json"):
            total = record.get("totalCashflow")
            if total is None:
                continue
            period = int(record["settlementPeriod"])
            result[period][str(record["bmUnit"])][direction] += Decimal(str(total))
    return result


def bsad(day: str) -> dict[int, dict[str, Decimal]]:
    """Non-BM adjustments per period, split by NESO's TradeFlag."""
    result: dict[int, dict[str, Decimal]] = defaultdict(
        lambda: {
            "system_cost": Decimal(0),
            "energy_cost": Decimal(0),
            "system_volume": Decimal(0),
            "energy_volume": Decimal(0),
        }
    )
    with (neso.NESO_RAW / "disaggregated_bsad_2026-27.csv").open() as handle:
        for row in csv.DictReader(handle):
            if row["Date"][:10] != day:
                continue
            period = int(row["SettlementPeriod"])
            kind = "system" if row["TradeFlag"].strip().upper() == "T" else "energy"
            result[period][f"{kind}_cost"] += Decimal(row["DisaggregatedBSADCost"] or "0")
            result[period][f"{kind}_volume"] += Decimal(row["DisaggregatedBSADVolume"] or "0")
    return result


def published_volumes(day: str) -> dict[int, dict[str, Decimal]]:
    """NESO's published constraint bid/offer MWh per period (layer 4)."""
    result = {}
    with (neso.NESO_RAW / "daily_balancing_volume_2026-27.csv").open() as handle:
        for row in csv.DictReader(handle):
            if row["SETT_DATE"][:10] != day:
                continue
            result[int(row["SETT_PERIOD"])] = {
                "constraint_offers_mwh": Decimal(row["Constraint Offers (MWh)"] or "0"),
                "constraint_bids_mwh": Decimal(row["Constraint Bids (MWh)"] or "0"),
            }
    return result


def run() -> None:
    selected = json.loads((EVIDENCE / "selected-period.json").read_text())["selected"]
    day = selected["settlement_date"]
    costs = {
        c.settlement_period: c
        for c in parse_cost_rows(neso.read_csv("daily_balancing_costs_2026-27.csv"))
        if c.settlement_date == day
    }
    cash = cashflows(day)
    fuel = fuel_types()
    adjustments = bsad(day)
    volumes4 = published_volumes(day)

    periods = []
    for period in EPISODE:
        accepted = accepted_volumes(day, period)
        period_cash = cash.get(period, {})
        units = sorted(
            accepted,
            key=lambda u: -(accepted[u]["offer"] + accepted[u]["bid"]),
        )
        material = [u for u in units if accepted[u]["offer"] + accepted[u]["bid"] >= MATERIAL_MWH]
        by_cash = sorted(
            period_cash,
            key=lambda u: -abs(period_cash[u]["offer"] + period_cash[u]["bid"]),
        )
        fuels: dict[str, Decimal] = defaultdict(Decimal)
        for unit, sides in accepted.items():
            fuels[fuel.get(unit, "unclassified")] += sides["offer"] + sides["bid"]
        total_energy = sum(fuels.values(), Decimal(0))
        ranked = sorted((accepted[u]["offer"] + accepted[u]["bid"] for u in accepted), reverse=True)
        top5 = (sum(ranked[:5], Decimal(0)) / total_energy) if total_energy else Decimal(0)
        periods.append(
            {
                "period": period,
                "accepted_energy_by_fuel_mwh": {
                    k: str(v) for k, v in sorted(fuels.items(), key=lambda kv: -kv[1])
                },
                "concentration_top5_share_of_accepted_energy": str(round(top5, 4)),
                "layer1_published_constraints_gbp": str(costs[period].constraints_gbp),
                "layer2_accepted_offer_mwh": str(
                    sum((accepted[u]["offer"] for u in accepted), Decimal(0))
                ),
                "layer2_accepted_bid_mwh": str(
                    sum((accepted[u]["bid"] for u in accepted), Decimal(0))
                ),
                "layer2_bm_cashflow_offer_gbp": str(
                    sum((period_cash[u]["offer"] for u in period_cash), Decimal(0))
                ),
                "layer2_bm_cashflow_bid_gbp": str(
                    sum((period_cash[u]["bid"] for u in period_cash), Decimal(0))
                ),
                "layer2_units_with_accepted_volume": len(accepted),
                "layer2_materially_instructed_units": len(material),
                "layer3_bsad": {k: str(v) for k, v in adjustments.get(period, {}).items()},
                "layer4_published_volumes_mwh": {
                    k: str(v) for k, v in volumes4.get(period, {}).items()
                },
                "top_units_by_accepted_energy": [
                    {
                        "unit": u,
                        "offer_mwh": str(accepted[u]["offer"]),
                        "bid_mwh": str(accepted[u]["bid"]),
                    }
                    for u in units[:5]
                ],
                "top_units_by_absolute_bm_cashflow": [
                    {
                        "unit": u,
                        "offer_gbp": str(period_cash[u]["offer"]),
                        "bid_gbp": str(period_cash[u]["bid"]),
                    }
                    for u in by_cash[:5]
                ],
            }
        )

    out = {
        "labelling": __doc__.split("FOUR ACCOUNTING LAYERS")[1].strip(),
        "selected_period": selected["settlement_period"],
        "episode_context_periods": [EPISODE.start, EPISODE.stop - 1],
        "material_threshold_mwh": str(MATERIAL_MWH),
        "periods": periods,
    }
    (EVIDENCE / "episode-diagnostic.json").write_text(json.dumps(out, indent=1) + "\n")

    print(
        f"{'p':>4}  {'layer1 Constraints':>19}  {'L2 offer MWh':>13}  {'L2 bid MWh':>11}  "
        f"{'L2 cashflow net':>16}  {'units':>6}"
    )
    for row in periods:
        net = Decimal(row["layer2_bm_cashflow_offer_gbp"]) + Decimal(
            row["layer2_bm_cashflow_bid_gbp"]
        )
        mark = " <-- SELECTED" if row["period"] == selected["settlement_period"] else ""
        print(
            f"{row['period']:>4}  £{Decimal(row['layer1_published_constraints_gbp']):>18,.0f}  "
            f"{Decimal(row['layer2_accepted_offer_mwh']):>13,.0f}  "
            f"{Decimal(row['layer2_accepted_bid_mwh']):>11,.0f}  "
            f"£{net:>15,.0f}  {row['layer2_materially_instructed_units']:>6}{mark}"
        )


if __name__ == "__main__":
    run()
