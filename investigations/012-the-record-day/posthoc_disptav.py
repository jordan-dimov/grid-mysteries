"""012 — post-hoc, not part of the sealed run: DISPTAV `dataType` sensitivity.

The declaration bound accepted MWh to DISPTAV `Original` rows. After the
run, those rows were found to carry a fraction of the day's accepted bid
volume, while `Tagged` rows sum to the settlement total published in the
system-prices dataset. This script reads only artefacts the sealed run
already pinned, recomputes the volume-bearing figures under every
`dataType`, and writes `evidence/posthoc-disptav.json`, labelled post-hoc.
No proposition verdict is changed by it; the declared rule stands as run.

    uv run python investigations/012-the-record-day/posthoc_disptav.py
"""

import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import DIRECTIONS, PERIODS, REPO_ROOT, load_records
from grid_mysteries.evidence import write_json
from grid_mysteries.investigations import record_day as rd

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
RAW = REPO_ROOT / "data" / "raw" / "elexon" / "012"
DATA_TYPES = ("Original", "Original-Priced", "Re-priced", "Tagged")


def volumes_by_type(records: list[dict]) -> dict[str, dict[str, Decimal]]:
    """dataType -> unit -> summed |pairVolumes| (the run's rule, per type)."""
    out: dict[str, dict[str, Decimal]] = {t: defaultdict(lambda: rd.ZERO) for t in DATA_TYPES}
    for record in records:
        kind = record.get("dataType")
        if kind not in out:
            continue
        pairs = record.get("pairVolumes") or {}
        total = sum(
            (abs(v) for v in (rd._decimal(x) for x in pairs.values()) if v is not None), rd.ZERO
        )
        if total:
            out[kind][str(record["bmUnit"])] += total
    return out


def main() -> None:
    register = load_records(RAW / "bmunits.json")
    fuel_of = {str(r["elexonBmUnit"]): (r.get("fuelType") or "") for r in register}
    selection = json.loads((EVIDENCE / "selection.json").read_text())
    days = [d for d in (selection["selected"], selection["runner_up"]) if d]
    out: dict = {
        "post_hoc": True,
        "note": (
            "Computed after the sealed run from pinned artefacts only. The declared "
            "rule (DISPTAV `Original`) stands; these figures are a sensitivity, not a verdict."
        ),
        "days": {},
    }
    for day in days:
        cash: dict[tuple[str, int, str], Decimal] = defaultdict(lambda: rd.ZERO)
        rows = []
        for direction in DIRECTIONS:
            rows.extend(
                rd.cashflow_rows(load_records(RAW / day / f"ebocf_{direction}.json"), direction)
            )
        for row in rows:
            cash[(row.unit, row.period, row.direction)] += row.gbp
        prices = load_records(RAW / day / "system-prices.json")
        settlement_total = {
            "offer_mwh": str(
                sum(
                    (rd._decimal(r.get("totalAcceptedOfferVolume")) or rd.ZERO for r in prices),
                    rd.ZERO,
                )
            ),
            "bid_mwh": str(
                sum(
                    (rd._decimal(r.get("totalAcceptedBidVolume")) or rd.ZERO for r in prices),
                    rd.ZERO,
                )
            ),
        }
        mwh_all = {t: {d: rd.ZERO for d in DIRECTIONS} for t in DATA_TYPES}
        mwh_cls = {t: {c: {d: rd.ZERO for d in DIRECTIONS} for c in rd.CLASSES} for t in DATA_TYPES}
        paired_gbp = {t: {"gas_offer": rd.ZERO, "wind_bid": rd.ZERO} for t in DATA_TYPES}
        paired_mwh = {t: {"gas_offer": rd.ZERO, "wind_bid": rd.ZERO} for t in DATA_TYPES}
        for period in PERIODS:
            for direction in DIRECTIONS:
                path = RAW / day / f"disptav_{direction}_p{period:02d}.json"
                for kind, per_unit in volumes_by_type(load_records(path)).items():
                    for unit, mwh in per_unit.items():
                        cls = rd.fuel_class(fuel_of.get(unit))
                        mwh_all[kind][direction] += mwh
                        mwh_cls[kind][cls][direction] += mwh
                        key = f"{cls}_{direction}"
                        if key in paired_gbp[kind]:
                            paired_mwh[kind][key] += mwh
                            paired_gbp[kind][key] += cash.get((unit, period, direction), rd.ZERO)
        mid = rd.mid_prices(load_records(RAW / day / "mid.json"), settlement_date=day)
        p3_by_type = {}
        for kind in DATA_TYPES:
            gas_gbp: dict[int, Decimal] = defaultdict(lambda: rd.ZERO)
            gas_mwh: dict[int, Decimal] = defaultdict(lambda: rd.ZERO)
            for period in PERIODS:
                for unit, mwh in volumes_by_type(
                    load_records(RAW / day / f"disptav_offer_p{period:02d}.json")
                )[kind].items():
                    if rd.fuel_class(fuel_of.get(unit)) == "gas":
                        gas_mwh[period] += mwh
                        gas_gbp[period] += cash.get((unit, period, "offer"), rd.ZERO)
            p3_by_type[kind] = rd.gas_offer_price(dict(gas_gbp), dict(gas_mwh), mid)
        out["days"][day] = {
            "settlement_total_accepted_volume_from_system_prices": settlement_total,
            "disptav_mwh_by_data_type": {
                t: {d: str(v) for d, v in g.items()} for t, g in mwh_all.items()
            },
            "disptav_mwh_by_data_type_and_class": {
                t: {c: {d: str(v) for d, v in g.items()} for c, g in cls.items()}
                for t, cls in mwh_cls.items()
            },
            "paired_by_data_type": {
                t: {
                    k: {
                        "gbp": str(paired_gbp[t][k]),
                        "mwh": str(paired_mwh[t][k]),
                        "vwap_gbp_per_mwh": None
                        if rd.vwap(paired_gbp[t][k], paired_mwh[t][k]) is None
                        else str(rd.vwap(paired_gbp[t][k], paired_mwh[t][k])),
                    }
                    for k in ("gas_offer", "wind_bid")
                }
                for t in DATA_TYPES
            },
            "gas_offer_price_by_data_type": p3_by_type,
        }
        # "other" class: who is in it, by the register's own label
        other = defaultdict(lambda: rd.ZERO)
        for row in rows:
            if (
                row.direction == "offer"
                and row.gbp > rd.ZERO
                and rd.fuel_class(fuel_of.get(row.unit)) == "other"
            ):
                other[fuel_of.get(row.unit) or "(no fuelType)"] += row.gbp
        out["days"][day]["other_offer_paid_out_by_register_label_gbp"] = {
            k: str(v) for k, v in sorted(other.items(), key=lambda kv: -kv[1])
        }
    write_json(EVIDENCE / "posthoc-disptav.json", out)
    for day, block in out["days"].items():
        print(
            day, "settlement totals", block["settlement_total_accepted_volume_from_system_prices"]
        )
        for t in DATA_TYPES:
            print(f"  {t:16s} mwh {block['disptav_mwh_by_data_type'][t]}")
            print(f"  {'':16s} paired {block['paired_by_data_type'][t]}")
            print(f"  {'':16s} gas P3 {block['gas_offer_price_by_data_type'][t]}")
        print("  other offers by label", block["other_offer_paid_out_by_register_label_gbp"])


if __name__ == "__main__":
    main()
