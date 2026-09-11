"""012 — the record day: gated acquisition, R1 selection, the four layers.

    uv run python investigations/012-the-record-day/run.py --seal <prefix> --phase all

Refuses to fetch unless invoked with ``--seal <prefix of DECLARATION.md's
SHA-256>`` so the human seal is on the record in the command that acquired
the data. Order is fixed by the declaration: register → NESO CSVs → EBOCF
for every window day → R1 offline → deep record (DISPTAV, MID, FUELINST,
system prices) for the selected and comparison days only → layers and
propositions. Every response is journalled under data/raw/ before any value
is read into a ledger.
"""

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import DIRECTIONS, PERIODS, REPO_ROOT, day_range, load_records
from grid_mysteries.evidence import write_json
from grid_mysteries.investigations import record_day as rd
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.pinning import pin, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
DECLARATION = HERE / "DECLARATION.md"
RAW_ELEXON = REPO_ROOT / "data" / "raw" / "elexon" / "012"
RAW_NESO = REPO_ROOT / "data" / "raw" / "neso" / "012"

WINDOW = day_range(date(2026, 9, 1), 8)
PREDICTED = ("2026-09-08", "2026-09-04")

NESO_INPUTS = [
    (
        "NESO-DAILY-BALANCING-COSTS-26-27",
        "1d040751-f77f-4641-9130-d49f8cbfe54f",
        "daily_balancing_costs_2026-27.csv",
    ),
    (
        "NESO-DAILY-BALANCING-VOLUME-26-27",
        "e781da74-6c35-4296-81dd-250cee869c19",
        "daily_balancing_volume_2026-27.csv",
    ),
    (
        "NESO-DISAGGREGATED-BSAD-26-27",
        "2be1a4d1-6b10-4c62-a01c-924942a3748f",
        "disaggregated_bsad_2026-27.csv",
    ),
]


def declaration_digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def journal(name: str) -> dict[str, Path]:
    return {
        "journal_path": EVIDENCE / f"{name}-journal.ndjson",
        "manifest_path": EVIDENCE / f"{name}-manifest.json",
    }


# ---------------------------------------------------------------- acquisition


def acquire_register() -> None:
    pin(
        [("BMUNITS", elexon.bmunits_url(), RAW_ELEXON / "bmunits.json")],
        fetch=elexon.fetch_pinned,
        label="register",
        progress=progress,
        **journal("register"),
    )


def acquire_neso() -> None:
    jobs = [
        (dataset, neso.dump_url(resource), RAW_NESO / filename)
        for dataset, resource, filename in NESO_INPUTS
    ]
    pin(
        jobs,
        fetch=neso.fetch_pinned,
        label="neso",
        sleep_seconds=0.5,
        progress=progress,
        **journal("neso"),
    )


def acquire_window() -> None:
    jobs = [
        (
            "EBOCF",
            elexon.cashflows_url(direction, day),
            RAW_ELEXON / day / f"ebocf_{direction}.json",
        )
        for day in WINDOW
        for direction in DIRECTIONS
    ]
    pin(
        jobs,
        fetch=elexon.fetch_pinned,
        label="window EBOCF",
        progress=progress,
        **journal("window"),
    )


def acquire_deep(days: list[str]) -> None:
    jobs: list[tuple[str, str, Path]] = []
    for day in days:
        following = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
        for period in PERIODS:
            for direction in DIRECTIONS:
                jobs.append(
                    (
                        "DISPTAV",
                        elexon.acceptance_volumes_url(direction, day, period),
                        RAW_ELEXON / day / f"disptav_{direction}_p{period:02d}.json",
                    )
                )
        jobs.append(("MID", elexon.day_stream_url("MID", day), RAW_ELEXON / day / "mid.json"))
        jobs.append(
            (
                "FUELINST",
                f"{elexon.BASE_URL}/datasets/FUELINST/stream?publishDateTimeFrom={day}T00:00Z&publishDateTimeTo={following}T00:00Z",
                RAW_ELEXON / day / "fuelinst.json",
            )
        )
        jobs.append(
            (
                "SYSTEM-PRICES",
                elexon.system_prices_url(day),
                RAW_ELEXON / day / "system-prices.json",
            )
        )
    pin(jobs, fetch=elexon.fetch_pinned, label="deep record", progress=progress, **journal("deep"))


# ------------------------------------------------------------------- reading


def fuel_map() -> dict[str, str]:
    return {
        str(r["elexonBmUnit"]): (r.get("fuelType") or "")
        for r in load_records(RAW_ELEXON / "bmunits.json")
    }


def gsp_map() -> dict[str, str]:
    return {
        str(r["elexonBmUnit"]): (r.get("gspGroupId") or "")
        for r in load_records(RAW_ELEXON / "bmunits.json")
    }


def day_rows(day: str) -> list[rd.Cashflow]:
    rows: list[rd.Cashflow] = []
    for direction in DIRECTIONS:
        path = RAW_ELEXON / day / f"ebocf_{direction}.json"
        rows.extend(rd.cashflow_rows(load_records(path), direction))
    return rows


def neso_rows(filename: str, day: str, date_col: str) -> list[dict]:
    path = RAW_NESO / filename
    with path.open() as handle:
        return [row for row in csv.DictReader(handle) if row[date_col][:10] == day]


def layer1(day: str) -> dict[str, Any]:
    rows = neso_rows("daily_balancing_costs_2026-27.csv", day, "SETT_DATE")
    constraints = [Decimal(r["Constraints"]) for r in rows if (r.get("Constraints") or "").strip()]
    return {
        "rows": len(rows),
        "constraints_gbp": str(sum(constraints, rd.ZERO)) if constraints else None,
    }


def layer3(day: str) -> dict[str, Any]:
    rows = neso_rows("disaggregated_bsad_2026-27.csv", day, "Date")
    out = {
        "rows": len(rows),
        "system_cost_gbp": rd.ZERO,
        "energy_cost_gbp": rd.ZERO,
        "system_volume_mwh": rd.ZERO,
        "energy_volume_mwh": rd.ZERO,
    }
    for row in rows:
        kind = "system" if row["TradeFlag"].strip().upper() == "T" else "energy"
        out[f"{kind}_cost_gbp"] += Decimal(row["DisaggregatedBSADCost"] or "0")
        out[f"{kind}_volume_mwh"] += Decimal(row["DisaggregatedBSADVolume"] or "0")
    net = out["system_cost_gbp"] + out["energy_cost_gbp"]
    return {k: (str(v) if isinstance(v, Decimal) else v) for k, v in out.items()} | {
        "net_cost_gbp": str(net),
        "available": bool(rows),
    }


def layer4(day: str) -> dict[str, Any]:
    rows = neso_rows("daily_balancing_volume_2026-27.csv", day, "SETT_DATE")
    offers = sum((Decimal(r["Constraint Offers (MWh)"] or "0") for r in rows), rd.ZERO)
    bids = sum((Decimal(r["Constraint Bids (MWh)"] or "0") for r in rows), rd.ZERO)
    return {
        "rows": len(rows),
        "constraint_offers_mwh": str(offers) if rows else None,
        "constraint_bids_mwh": str(bids) if rows else None,
    }


def deep_layers(day: str, fuel_of: dict[str, str], gsp_of: dict[str, str]) -> dict[str, Any]:
    """L2 with volumes, by class and direction; the gas-offer price; wind bids by GSP group."""
    rows = day_rows(day)
    cash_by_unit_period: dict[tuple[str, int, str], Decimal] = defaultdict(lambda: rd.ZERO)
    for row in rows:
        cash_by_unit_period[(row.unit, row.period, row.direction)] += row.gbp
    mwh_by_class: dict[str, dict[str, Decimal]] = {
        c: {d: rd.ZERO for d in DIRECTIONS} for c in rd.CLASSES
    }
    gas_offer_gbp: dict[int, Decimal] = defaultdict(lambda: rd.ZERO)
    gas_offer_mwh: dict[int, Decimal] = defaultdict(lambda: rd.ZERO)
    wind_bid_gbp: dict[int, Decimal] = defaultdict(lambda: rd.ZERO)
    wind_bid_mwh: dict[int, Decimal] = defaultdict(lambda: rd.ZERO)
    for period in PERIODS:
        for direction in DIRECTIONS:
            path = RAW_ELEXON / day / f"disptav_{direction}_p{period:02d}.json"
            if not path.exists():
                continue
            for unit, mwh in rd.accepted_mwh(load_records(path)).items():
                cls = rd.fuel_class(fuel_of.get(unit))
                mwh_by_class[cls][direction] += mwh
                if cls == "gas" and direction == "offer":
                    gas_offer_mwh[period] += mwh
                    gas_offer_gbp[period] += cash_by_unit_period.get(
                        (unit, period, direction), rd.ZERO
                    )
                if cls == "wind" and direction == "bid":
                    wind_bid_mwh[period] += mwh
                    wind_bid_gbp[period] += cash_by_unit_period.get(
                        (unit, period, direction), rd.ZERO
                    )
    mid = rd.mid_prices(load_records(RAW_ELEXON / day / "mid.json"))
    price = rd.gas_offer_price(dict(gas_offer_gbp), dict(gas_offer_mwh), mid)
    wind_gbp = sum(wind_bid_gbp.values(), rd.ZERO)
    wind_mwh = sum(wind_bid_mwh.values(), rd.ZERO)
    by_gsp: dict[str, Decimal] = defaultdict(lambda: rd.ZERO)
    for row in rows:
        if (
            row.direction == "bid"
            and rd.fuel_class(fuel_of.get(row.unit)) == "wind"
            and row.gbp > rd.ZERO
        ):
            by_gsp[gsp_of.get(row.unit) or "unknown"] += row.gbp
    return {
        "accepted_mwh_by_class": {
            c: {d: str(v) for d, v in g.items()} for c, g in mwh_by_class.items()
        },
        "gas_offer_price": price,
        "wind_bid": {
            "gbp": str(wind_gbp),
            "mwh": str(wind_mwh),
            "vwap_gbp_per_mwh": None
            if rd.vwap(wind_gbp, wind_mwh) is None
            else str(rd.vwap(wind_gbp, wind_mwh)),
        },
        "wind_bid_paid_by_gsp_group_gbp": {k: str(v) for k, v in sorted(by_gsp.items())},
        "mid_periods": len(mid),
    }


def fuel_context(day: str) -> dict[str, Any]:
    path = RAW_ELEXON / day / "fuelinst.json"
    if not path.exists():
        return {"available": False}
    acc: dict[str, list[Decimal]] = defaultdict(list)
    for record in load_records(path):
        fuel, gen = record.get("fuelType"), record.get("generation")
        if fuel is None or gen is None:
            continue
        acc[str(fuel)].append(Decimal(str(gen)))
    return {
        "available": True,
        "mean_mw_by_fuel": {
            f: str((sum(v) / len(v)).quantize(Decimal("1"))) for f, v in sorted(acc.items()) if v
        },
    }


# --------------------------------------------------------------------- phases


def select() -> tuple[str | None, str | None]:
    fuel_of = fuel_map()
    ledgers = {day: rd.ledger(day, day_rows(day), fuel_of) for day in WINDOW}
    selected, runner_up = rd.select_day(ledgers)
    write_json(
        EVIDENCE / "selection.json",
        {
            "rule": (
                "R1: highest total published indicative BM cashflow (EBOCF, both "
                "directions); ties earlier date; unavailable days excluded"
            ),
            "window": [WINDOW[0], WINDOW[-1]],
            "predicted": list(PREDICTED),
            "selected": selected,
            "runner_up": runner_up,
            "P0_holds": (selected, runner_up) == PREDICTED,
            "F0_unavailable_days": [d for d, led in ledgers.items() if not led.available],
            "ledgers": {day: led.as_json() for day, led in ledgers.items()},
            "window_paid_out_gbp": str(sum((led.paid_out for led in ledgers.values()), rd.ZERO)),
            "window_total_gbp": str(sum((led.total for led in ledgers.values()), rd.ZERO)),
        },
    )
    print(f"R1 selected {selected}, runner-up {runner_up}; predicted {PREDICTED}")
    return selected, runner_up


def evaluate(selected: str, runner_up: str | None) -> None:
    fuel_of, gsp_of = fuel_map(), gsp_map()
    out: dict[str, Any] = {"declaration_sha256": declaration_digest(), "days": {}}
    for day in [d for d in (selected, runner_up) if d]:
        led = rd.ledger(day, day_rows(day), fuel_of)
        l3 = layer3(day)
        deep = deep_layers(day, fuel_of, gsp_of)
        price = deep["gas_offer_price"]["gas_offer_vwap_gbp_per_mwh"]
        verdicts = rd.evaluate(
            led,
            Decimal(l3["net_cost_gbp"]) if l3["available"] else None,
            Decimal(price) if price is not None else None,
        )
        out["days"][day] = {
            "role": "selected" if day == selected else "comparison",
            "L1": layer1(day),
            "L2": led.as_json() | deep,
            "L3": l3,
            "L4": layer4(day),
            "context": fuel_context(day),
            "propositions": verdicts,
        }
    write_json(EVIDENCE / "results.json", out)
    for day, block in out["days"].items():
        p = block["propositions"]
        paid_out = Decimal(block["L2"]["paid_out_gbp"])
        print(f"{day} ({block['role']}): paid_out £{paid_out:,.0f}")
        print(
            f"  wind bid share {p['P1']['wind_bid_share_of_paid_out']}, "
            f"gas offer share {p['P1']['gas_offer_share_of_paid_out']} -> P1 {p['P1']['holds']}"
        )
        print(
            f"  BSAD net {p['P2']['bsad_net_cost_gbp']} "
            f"({p['P2']['bsad_share_of_paid_out']}) -> P2 {p['P2']['holds']}"
        )
        print(
            f"  gas VWAP {p['P3']['gas_offer_vwap_gbp_per_mwh']} -> P3 {p['P3']['holds']}; "
            f"sign ok {p['sign_convention_holds']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seal", required=True, help="prefix (≥ 8 hex) of DECLARATION.md's SHA-256"
    )
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    parser.add_argument(
        "--phase", choices=("acquire", "select", "deep", "evaluate", "all"), default="all"
    )
    parser.add_argument("--note", action="append", default=[])
    args = parser.parse_args()

    digest = declaration_digest()
    if len(args.seal) < 8 or not digest.startswith(args.seal.lower()):
        print(
            f"seal {args.seal!r} does not match DECLARATION.md sha256 {digest}; refusing",
            file=sys.stderr,
        )
        return 2
    date.fromisoformat(args.run_date)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    log_path = EVIDENCE / "acquisition-log.json"
    log: dict[str, Any] = json.loads(log_path.read_text()) if log_path.exists() else {}
    log.update({"declaration_sha256": digest, "seal": args.seal, "run_date": args.run_date})
    if args.note:
        log.setdefault("notes", []).extend(args.note)
    log.setdefault("phases", []).append({"phase": args.phase, "at": datetime.now(UTC).isoformat()})
    write_json(log_path, log)

    selected = runner_up = None
    if args.phase in ("acquire", "all"):
        acquire_register()
        acquire_neso()
        acquire_window()
    if args.phase in ("select", "all"):
        selected, runner_up = select()
    if args.phase in ("deep", "evaluate") and selected is None:
        sel = json.loads((EVIDENCE / "selection.json").read_text())
        selected, runner_up = sel["selected"], sel["runner_up"]
    if selected is None:
        print("F0: no window day carries EBOCF rows; no selection made", file=sys.stderr)
        return 1
    if args.phase in ("deep", "all"):
        acquire_deep([d for d in (selected, runner_up) if d])
    if args.phase in ("evaluate", "all"):
        evaluate(selected, runner_up)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
