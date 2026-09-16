"""016 — the day-ahead wind forecast on the record day: the data pack's runner.

    uv run python investigations/016-day-ahead-wind-forecast/run.py --phase acquire
    uv run python investigations/016-day-ahead-wind-forecast/run.py --phase export

This is a **data pack, not a sealed result**. It has no declaration and no
seal gate, because it makes no claim: it pins public bytes and flattens them
into CSVs for an outside contributor. Nothing here computes a forecast error
or attributes cost to one — that is the contributor's analysis, and it lands
in ``analysis/``.

``acquire`` pins, once and journalled, only what 012 does not already hold:
every WINDFOR issue published on 7 and 8 September 2026, the day-ahead wind
and solar forecast (DGWS, ex-B1440) for the 8th, one WINDFOR evolution
response as a witness of the publisher's own hour-to-period mapping, and
final PN plus B1610 metered volumes for every wind BM unit that carries an
Elexon id. ``export`` reads only pinned bytes and committed evidence — 012's
register, FUELINST and results, 015's wind-by-scheme, storage and links,
003's CMIS and the TEC vintage — and writes ``data/*.csv``.
"""

import argparse
import csv
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT, load_records
from grid_mysteries.evidence import write_json
from grid_mysteries.hashing import sha256_file
from grid_mysteries.investigations import wind_forecast_pack as pack
from grid_mysteries.sources import elexon
from grid_mysteries.sources.pinning import load_journal, pin, progress

HERE = Path(__file__).parent
DATA = HERE / "data"
EVIDENCE = HERE / "evidence"
DAY = date(2026, 9, 8)
DAY_ISO = DAY.isoformat()

RAW = REPO_ROOT / "data" / "raw" / "elexon" / "016"
RAW_012 = REPO_ROOT / "data" / "raw" / "elexon" / "012"
CMIS = REPO_ROOT / "data" / "raw" / "neso" / "cmis_arming_2026-27.csv"
TEC = REPO_ROOT / "data" / "raw" / "neso" / "tec-history" / "2026-09-15_neso-ckan.csv"
EV_012 = REPO_ROOT / "investigations" / "012-the-record-day" / "evidence"
EV_015 = REPO_ROOT / "investigations" / "015-support-and-storage-on-the-record-day" / "evidence"

#: The publish window for WINDFOR issues: everything NESO put out on the 7th
#: and the 8th. Both bounds are UTC instants, inclusive of the 23:30 issue.
WINDFOR_FROM = "2026-09-07T00:00Z"
WINDFOR_TO = "2026-09-09T00:00Z"
#: One target hour, pinned so the hour-to-period mapping this pack applies is
#: witnessed against the publisher's own, not asserted.
MAPPING_WITNESS_HOUR = "2026-09-08T12:00Z"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        return list(csv.DictReader(handle))


def journal(name: str) -> dict[str, Path]:
    return {
        "journal_path": EVIDENCE / f"{name}-journal.ndjson",
        "manifest_path": EVIDENCE / f"{name}-manifest.json",
    }


def register() -> list[dict]:
    """012's BMUNITS vintage of 2026-09-11, the one 015 also read."""
    return load_records(RAW_012 / "bmunits.json")


def wind_ids() -> list[str]:
    return pack.queryable_units(
        pack.wind_unit_rows(register(), cmis=[], tec=[], bid_paid_by_unit={})
    )


# ---------------------------------------------------------------- acquisition


def acquire() -> None:
    units = wind_ids()
    day_start = pack.day_start_utc(DAY).strftime("%Y-%m-%dT%H:%MZ")
    day_end = pack.period_start(DAY, pack.periods_in_day(DAY)).strftime("%Y-%m-%dT%H:%MZ")
    jobs = [
        (
            "WINDFOR",
            elexon.windfor_stream_url(WINDFOR_FROM, WINDFOR_TO),
            RAW / f"windfor_issues_{WINDFOR_FROM[:10]}_{DAY_ISO}.json",
        ),
        (
            "WINDFOR-EVOLUTION",
            elexon.wind_forecast_evolution_url(MAPPING_WITNESS_HOUR),
            RAW / f"windfor_evolution_{MAPPING_WITNESS_HOUR.replace(':', '')}.json",
        ),
        (
            "DGWS-B1440",
            elexon.wind_solar_day_ahead_url(day_start, day_end),
            RAW / f"b1440_day_ahead_{DAY_ISO}.json",
        ),
        ("PN", elexon.pn_stream_url(DAY_ISO, units), RAW / f"pn_wind_{DAY_ISO}.json"),
        ("B1610", elexon.b1610_stream_url(DAY_ISO, units), RAW / f"b1610_wind_{DAY_ISO}.json"),
    ]
    pin(jobs, fetch=elexon.fetch_pinned, label="016", progress=progress, **journal("elexon"))


# -------------------------------------------------------------------- export


def write_csv(name: str, rows: list[dict[str, Any]], columns: list[str]) -> Path:
    path = DATA / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: "" if row.get(c) is None else row[c] for c in columns})
    return path


def bid_paid_by_unit() -> dict[str, str]:
    """015's per-unit bid cashflow, carried across verbatim — never recomputed."""
    scheme = json.loads((EV_015 / "wind-by-scheme.json").read_text())
    return {u["unit"]: u["bid_paid_gbp"] for u in scheme["units"]}


def cost_context_rows() -> list[dict[str, Any]]:
    """Only figures that already sit in a committed evidence file, each named
    with the file it comes from. Ratios of two cited figures are marked
    derived; nothing else is computed."""
    r012 = json.loads((EV_012 / "results.json").read_text())["days"][DAY_ISO]
    l2 = r012["L2"]
    scheme = json.loads((EV_015 / "wind-by-scheme.json").read_text())
    storage = json.loads((EV_015 / "storage.json").read_text())
    summary = json.loads((EV_015 / "summary.json").read_text())

    paid_out = Decimal(l2["paid_out_gbp"])
    wind_bid_paid = Decimal(scheme["total_wind_bid_paid_gbp"])
    wind_bid_mwh = sum(
        (Decimal(row["bid_mwh"]) for row in scheme["table"] if row["scheme"] != "ro_possible"),
        Decimal(0),
    )
    export_mw = sum((Decimal(u["export_capacity_mw"]) for u in storage), Decimal(0))
    north = [u for u in storage if u["side_of_b6"] == "north"]
    north_mw = sum((Decimal(u["export_capacity_mw"]) for u in north), Decimal(0))

    def row(figure: str, value: Any, unit: str, source: str, evidence: str, note: str = "") -> dict:
        return {
            "figure": figure,
            "value": value,
            "unit": unit,
            "source_investigation": source,
            "evidence_file": evidence,
            "note": note,
        }

    e012 = "investigations/012-the-record-day/evidence/results.json"
    e015 = "investigations/015-support-and-storage-on-the-record-day/evidence"
    return [
        row(
            "total_balancing_paid_out",
            paid_out.quantize(Decimal("0.01")),
            "GBP",
            "012",
            e012,
            "L2 paid_out_gbp: EBOCF indicative cashflows, positive rows only. The headline £33.6m.",
        ),
        row(
            "total_balancing_net",
            Decimal(l2["total_gbp"]).quantize(Decimal("0.01")),
            "GBP",
            "012",
            e012,
            "L2 total_gbp: every row signed, so paid-in nets off.",
        ),
        row(
            "wind_bid_paid_out",
            wind_bid_paid.quantize(Decimal("0.01")),
            "GBP",
            "012 and 015",
            f"{e015}/wind-by-scheme.json",
            "Paid out on wind bids across 77 wind units that carried bid cashflow.",
        ),
        row(
            "wind_bid_share_of_paid_out",
            (wind_bid_paid / paid_out).quantize(Decimal("0.0001")),
            "fraction",
            "derived",
            f"{e012}; {e015}/wind-by-scheme.json",
            "Derived: the two rows above divided. No new measurement.",
        ),
        row(
            "gas_offer_paid_out",
            Decimal(l2["paid_out_by_class_gbp"]["gas"]["offer"]).quantize(Decimal("0.01")),
            "GBP",
            "012",
            e012,
            "What replaced the wind that was bid off.",
        ),
        row(
            "wind_accepted_bid_volume",
            wind_bid_mwh.quantize(Decimal("0.001")),
            "MWh",
            "015",
            f"{e015}/wind-by-scheme.json",
            "DISPTAV Tagged, the type that reconciles with the day's settlement "
            "totals. 012's own accepted_mwh used DISPTAV Original, which "
            "under-reads bids; do not mix the two.",
        ),
        row(
            "gas_offer_vwap",
            Decimal(str(l2["gas_offer_price"]["gas_offer_vwap_gbp_per_mwh"])),
            "GBP/MWh",
            "012",
            e012,
            "",
        ),
        row(
            "mid_vwap_same_periods",
            Decimal(str(l2["gas_offer_price"]["mid_vwap_same_periods_gbp_per_mwh"])),
            "GBP/MWh",
            "012",
            e012,
            "Market index price over the same periods.",
        ),
        row(
            "wind_outturn_mean",
            Decimal(str(r012["context"]["mean_mw_by_fuel"]["WIND"])),
            "MW",
            "012",
            e012,
            "FUELINST mean over the day: transmission-visible wind only.",
        ),
        row(
            "constraint_periods",
            summary["constraint"]["periods"],
            "settlement periods",
            "015",
            f"{e015}/summary.json",
            "Periods carrying accepted wind-unit bid volume: all 48.",
        ),
        row(
            "energy_limited_units",
            summary["storage_units"],
            "BM units",
            "015",
            f"{e015}/storage.json",
            "Units publishing a maximum delivery volume (MDO or MDB) on the day.",
        ),
        row(
            "energy_limited_export_capacity",
            export_mw.quantize(Decimal("0.001")),
            "MW",
            "015",
            f"{e015}/storage.json",
            "Registered export capacity of those 28 units.",
        ),
        row(
            "energy_limited_export_capacity_north_of_b6",
            north_mw.quantize(Decimal("0.001")),
            "MW",
            "015",
            f"{e015}/storage.json",
            f"{len(north)} of {len(storage)} units, by 015's graded side-of-B6 ladder.",
        ),
        row(
            "wind_bill_share_north_of_b6",
            "",
            "",
            "not in the record",
            "",
            "015 graded sides of B6 for the 28 energy-limited units only, never "
            "for wind. data/wind_units.csv applies the same ladder to wind, but "
            "no north/south split of the wind bill has been declared, run or "
            "sealed, so none is quoted here. 45 % of the wind bid money sits on "
            "units 015 could not link to any support register at all.",
        ),
    ]


def export() -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    manifest = load_journal(journal("elexon")["journal_path"])
    written: dict[str, int] = {}

    def emit(name: str, rows: list[dict[str, Any]], columns: list[str]) -> None:
        write_csv(name, rows, columns)
        written[name] = len(rows)

    windfor = load_records(RAW / f"windfor_issues_{WINDFOR_FROM[:10]}_{DAY_ISO}.json")
    emit(
        "forecast_issues.csv",
        pack.forecast_issue_rows(windfor, DAY),
        [
            "publish_time_utc",
            "target_start_utc",
            "settlement_date",
            "settlement_period",
            "covers_periods",
            "forecast_mw",
            "dataset",
        ],
    )

    b1440 = load_records(RAW / f"b1440_day_ahead_{DAY_ISO}.json")
    emit(
        "b1440_day_ahead.csv",
        pack.b1440_rows(b1440, DAY),
        [
            "publish_time_utc",
            "process_type",
            "business_type",
            "psr_type",
            "settlement_date",
            "settlement_period",
            "target_start_utc",
            "quantity_mw",
        ],
    )

    units = pack.wind_unit_rows(
        register(),
        cmis=read_csv(CMIS),
        tec=read_csv(TEC),
        bid_paid_by_unit=bid_paid_by_unit(),
    )
    emit(
        "wind_units.csv",
        units,
        [
            "bm_unit",
            "national_grid_bm_unit",
            "eic",
            "bm_unit_name",
            "lead_party",
            "bm_unit_type",
            "generation_capacity_mw",
            "gsp_group_id",
            "north_of_b6",
            "side_of_b6",
            "side_grade",
            "side_basis",
            "queryable",
            "bid_paid_gbp_015",
        ],
    )

    emit(
        "pn_final.csv",
        pack.pn_rows(load_records(RAW / f"pn_wind_{DAY_ISO}.json"), DAY),
        [
            "bm_unit",
            "national_grid_bm_unit",
            "settlement_date",
            "settlement_period",
            "time_from_utc",
            "time_to_utc",
            "level_from_mw",
            "level_to_mw",
        ],
    )

    emit(
        "b1610_actuals.csv",
        pack.b1610_rows(load_records(RAW / f"b1610_wind_{DAY_ISO}.json"), DAY),
        [
            "bm_unit",
            "national_grid_bm_unit",
            "settlement_date",
            "settlement_period",
            "half_hour_end_utc",
            "settlement_run_type",
            "psr_type",
            "quantity_mwh",
        ],
    )

    emit(
        "fuelinst_wind_5min.csv",
        pack.fuelinst_wind_rows(load_records(RAW_012 / DAY_ISO / "fuelinst.json"), DAY),
        [
            "publish_time_utc",
            "start_time_utc",
            "settlement_date",
            "settlement_period",
            "fuel_type",
            "generation_mw",
        ],
    )

    emit(
        "cost_context.csv",
        cost_context_rows(),
        ["figure", "value", "unit", "source_investigation", "evidence_file", "note"],
    )

    reused = [
        "data/raw/elexon/012/bmunits.json",
        f"data/raw/elexon/012/{DAY_ISO}/fuelinst.json",
        "data/raw/neso/cmis_arming_2026-27.csv",
        "data/raw/neso/tec-history/2026-09-15_neso-ckan.csv",
    ]
    sides: dict[str, int] = {}
    for unit in units:
        sides[str(unit["side_of_b6"])] = sides.get(str(unit["side_of_b6"]), 0) + 1
    asked = set(pack.queryable_units(units))
    served = {
        name: {str(row["bm_unit"]) for row in rows}
        for name, rows in (
            ("pn_final.csv", pack.pn_rows(load_records(RAW / f"pn_wind_{DAY_ISO}.json"), DAY)),
            (
                "b1610_actuals.csv",
                pack.b1610_rows(load_records(RAW / f"b1610_wind_{DAY_ISO}.json"), DAY),
            ),
        )
    }

    pack_record = {
        "day": DAY_ISO,
        "kind": "data pack (no declaration, no sealed result)",
        "exported_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "csv_rows": written,
        "csv_sha256": {path.name: sha256_file(path) for path in sorted(DATA.glob("*.csv"))},
        "wind_register_rows": len(units),
        "wind_units_queryable": sum(1 for u in units if u["queryable"]),
        "wind_units_by_side_of_b6": sides,
        "duplicate_bm_units": pack.duplicate_bm_units(units),
        "units_asked_for": len(asked),
        "units_served": {name: len(ids) for name, ids in served.items()},
        "units_asked_for_but_not_served": {
            name: sorted(asked - ids) for name, ids in served.items()
        },
        "acquired": [
            {"dataset": e["dataset"], "url": e["url"], "path": e["path"], "sha256": e["sha256"]}
            for e in sorted(manifest.values(), key=lambda e: e["path"])
        ],
        "reused_pinned": [{"path": p, "sha256": sha256_file(REPO_ROOT / p)} for p in reused],
        "reused_evidence": [
            {"path": str(p.relative_to(REPO_ROOT)), "sha256": sha256_file(p)}
            for p in [
                EV_012 / "results.json",
                EV_012 / "deep-manifest.json",
                EV_012 / "register-manifest.json",
                EV_015 / "wind-by-scheme.json",
                EV_015 / "storage.json",
                EV_015 / "summary.json",
                EV_015 / "links.json",
            ]
        ],
    }
    write_json(EVIDENCE / "pack.json", pack_record)
    for name, count in written.items():
        print(f"{name}: {count} rows")
    print(
        f"wind register rows {len(units)}, queryable {pack_record['wind_units_queryable']}, "
        f"sides {sides}"
    )
    for name, ids in served.items():
        missing = sorted(asked - ids)
        print(f"{name}: {len(ids)} of {len(asked)} units served; not served: {missing or 'none'}")
    return pack_record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("acquire", "export", "all"), default="all")
    args = parser.parse_args()
    if args.phase in ("acquire", "all"):
        acquire()
    if args.phase in ("export", "all"):
        export()


if __name__ == "__main__":
    main()
