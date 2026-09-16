"""016 — the day-ahead wind forecast on the record day: the data pack's logic.

This module shapes pinned public bytes into the flat CSV tables an outside
contributor reads. It deliberately computes **no forecast error and no cost
attribution**: that is the contributor's deliverable, and putting a derived
error column here would hand him a conclusion dressed as data.

The one judgement it does make is a reading rule, stated so it can be
challenged: a settlement period is identified by the UTC instant it starts,
and WINDFOR's hourly target time is placed on the period that *starts* at
that instant — the mapping Elexon's own `forecast/generation/wind/evolution`
endpoint publishes (witnessed in ``evidence/period-mapping-witness``).
The hour also covers the following period, which `covers_periods` records
rather than silently interpolating.
"""

from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from grid_mysteries.investigations.support_and_storage import side_of_b6

LONDON = ZoneInfo("Europe/London")
PERIOD = timedelta(minutes=30)
WIND_FUEL_TYPE = "WIND"


def day_start_utc(day: date) -> datetime:
    """The UTC instant settlement period 1 of `day` begins: local midnight."""
    return datetime.combine(day, time(0), tzinfo=LONDON).astimezone(UTC)


def periods_in_day(day: date) -> int:
    """48 on an ordinary day; 46 or 50 across a British clock change."""
    span = day_start_utc(day + timedelta(days=1)) - day_start_utc(day)
    return int(span / PERIOD)


def period_start(day: date, period: int) -> datetime:
    return day_start_utc(day) + (period - 1) * PERIOD


def period_of(day: date, instant: datetime) -> int | None:
    """The settlement period of `day` that *starts* at `instant`, or None if
    `instant` is not a period boundary of that day."""
    offset = instant.astimezone(UTC) - day_start_utc(day)
    if offset % PERIOD or not timedelta(0) <= offset < periods_in_day(day) * PERIOD:
        return None
    return int(offset / PERIOD) + 1


def parse_instant(value: str) -> datetime:
    """An Elexon timestamp. Naive values are UTC: every Insights datetime is
    published in UTC, and only some fields carry the trailing Z."""
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _decimal(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


# ------------------------------------------------------------------ the tables


def forecast_issue_rows(records: Iterable[Mapping[str, Any]], day: date) -> list[dict[str, Any]]:
    """WINDFOR issues, one row per (publish time, target hour), kept only
    where the target hour falls inside `day`'s settlement day."""
    rows: list[dict[str, Any]] = []
    last = periods_in_day(day)
    for record in records:
        start = parse_instant(record["startTime"])
        period = period_of(day, start)
        if period is None:
            continue
        rows.append(
            {
                "publish_time_utc": parse_instant(record["publishTime"]).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "target_start_utc": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "settlement_date": day.isoformat(),
                "settlement_period": period,
                "covers_periods": f"{period}-{period + 1}" if period < last else str(period),
                "forecast_mw": _decimal(record["generation"]),
                "dataset": record.get("dataset") or "WINDFOR",
            }
        )
    rows.sort(key=lambda r: (r["publish_time_utc"], r["settlement_period"]))
    return rows


def b1440_rows(records: Iterable[Mapping[str, Any]], day: date) -> list[dict[str, Any]]:
    """Day-ahead wind and solar forecast rows for `day`, as published."""
    rows: list[dict[str, Any]] = []
    for record in records:
        if str(record.get("settlementDate")) != day.isoformat():
            continue
        rows.append(
            {
                "publish_time_utc": parse_instant(record["publishTime"]).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "process_type": record.get("processType"),
                "business_type": record.get("businessType"),
                "psr_type": record.get("psrType"),
                "settlement_date": day.isoformat(),
                "settlement_period": int(record["settlementPeriod"]),
                "target_start_utc": parse_instant(record["startTime"]).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "quantity_mw": _decimal(record["quantity"]),
            }
        )
    rows.sort(key=lambda r: (r["settlement_period"], str(r["psr_type"])))
    return rows


def fuelinst_wind_rows(records: Iterable[Mapping[str, Any]], day: date) -> list[dict[str, Any]]:
    """FUELINST wind readings for `day`, five-minutely, as pinned by 012."""
    rows = [
        {
            "publish_time_utc": parse_instant(r["publishTime"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_time_utc": parse_instant(r["startTime"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "settlement_date": day.isoformat(),
            "settlement_period": int(r["settlementPeriod"]),
            "fuel_type": r["fuelType"],
            "generation_mw": _decimal(r["generation"]),
        }
        for r in records
        if r.get("fuelType") == WIND_FUEL_TYPE and str(r.get("settlementDate")) == day.isoformat()
    ]
    rows.sort(key=lambda r: r["start_time_utc"])
    return rows


def pn_rows(records: Iterable[Mapping[str, Any]], day: date) -> list[dict[str, Any]]:
    """PN point-MW segments, as published: two points bound each segment, and
    a period may carry several. No integration is done here."""
    rows = [
        {
            "bm_unit": r["bmUnit"],
            "national_grid_bm_unit": r.get("nationalGridBmUnit"),
            "settlement_date": day.isoformat(),
            "settlement_period": int(r["settlementPeriod"]),
            "time_from_utc": parse_instant(r["timeFrom"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "time_to_utc": parse_instant(r["timeTo"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level_from_mw": _decimal(r["levelFrom"]),
            "level_to_mw": _decimal(r["levelTo"]),
        }
        for r in records
        if str(r.get("settlementDate")) == day.isoformat()
    ]
    rows.sort(key=lambda r: (r["bm_unit"], r["settlement_period"], r["time_from_utc"]))
    return rows


def b1610_rows(records: Iterable[Mapping[str, Any]], day: date) -> list[dict[str, Any]]:
    """B1610 metered half-hourly volumes, as published."""
    rows = [
        {
            "bm_unit": r["bmUnit"],
            "national_grid_bm_unit": r.get("nationalGridBmUnitId"),
            "settlement_date": day.isoformat(),
            "settlement_period": int(r["settlementPeriod"]),
            "half_hour_end_utc": parse_instant(r["halfHourEndTime"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "settlement_run_type": r.get("settlementRunType"),
            "psr_type": r.get("psrType"),
            "quantity_mwh": _decimal(r["quantity"]),
        }
        for r in records
        if str(r.get("settlementDate")) == day.isoformat()
    ]
    rows.sort(key=lambda r: (r["bm_unit"], r["settlement_period"]))
    return rows


def wind_register_rows(register: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Every wind row of the BM unit register, in id order. Rows with no Elexon
    BM unit id sort last: no per-unit dataset in this pack can carry them.

    Rows are neither merged nor dropped. The 2026-09-11 vintage carries
    `T_WLNYO-4` twice — same unit, two EIC registrations — so the `eic` column
    is exported and `duplicate_bm_units` reports the collision. Anyone joining
    this table to `pn_final.csv` or `b1610_actuals.csv` on `bm_unit` must
    de-duplicate first, or Walney 4's 330 MW counts twice.
    """
    wind = [dict(r) for r in register if (r.get("fuelType") or "") == WIND_FUEL_TYPE]
    return sorted(
        wind,
        key=lambda r: (
            r.get("elexonBmUnit") is None,
            r.get("elexonBmUnit") or "",
            r.get("nationalGridBmUnit") or "",
            r.get("eic") or "",
        ),
    )


def duplicate_bm_units(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    """Elexon BM unit ids carried by more than one row of the table."""
    seen: dict[str, int] = {}
    for row in rows:
        uid = row.get("bm_unit") or row.get("elexonBmUnit")
        if uid:
            seen[str(uid)] = seen.get(str(uid), 0) + 1
    return sorted(uid for uid, count in seen.items() if count > 1)


def wind_unit_rows(
    register: Iterable[Mapping[str, Any]],
    *,
    cmis: Sequence[dict[str, str]],
    tec: Sequence[dict[str, str]],
    bid_paid_by_unit: Mapping[str, str],
) -> list[dict[str, Any]]:
    """The wind BM unit table, with 015's graded side-of-B6 ladder applied
    unchanged and 015's own bid cashflow carried across where it exists."""
    rows: list[dict[str, Any]] = []
    for unit in wind_register_rows(register):
        uid = unit.get("elexonBmUnit")
        side, grade, basis = side_of_b6(unit, list(cmis), list(tec))
        rows.append(
            {
                "bm_unit": uid,
                "national_grid_bm_unit": unit.get("nationalGridBmUnit"),
                "eic": unit.get("eic"),
                "bm_unit_name": unit.get("bmUnitName"),
                "lead_party": unit.get("leadPartyName"),
                "bm_unit_type": unit.get("bmUnitType"),
                "generation_capacity_mw": _decimal(unit.get("generationCapacity")),
                "gsp_group_id": unit.get("gspGroupId"),
                "north_of_b6": side == "north",
                "side_of_b6": side,
                "side_grade": grade,
                "side_basis": basis,
                "queryable": uid is not None,
                "bid_paid_gbp_015": bid_paid_by_unit.get(uid or ""),
            }
        )
    return rows


def queryable_units(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    """The wind BM unit ids the per-unit datasets can be asked for, one per
    register row and in row order — so `T_WLNYO-4`, registered twice, is
    asked for twice. The repeat is left in deliberately: it costs nothing at
    the API, and collapsing it would stop the pinned request URLs being
    reproducible from the register vintage they were built from."""
    return sorted(str(r["bm_unit"]) for r in rows if r["bm_unit"])
