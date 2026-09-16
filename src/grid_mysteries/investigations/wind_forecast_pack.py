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
from typing import Any, Final
from zoneinfo import ZoneInfo

from grid_mysteries.investigations.support_and_storage import (
    NORTH_GSP_GROUPS,
    NORTH_TOS,
    SOUTH_TOS,
    decimal,
    tokens,
)

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
    ofto_verified: Mapping[str, str] | None = None,
    reviewed: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """The wind BM unit table, with the corrected side-of-B6 ladder
    (``side_of_b6_corrected``) applied and 015's own bid cashflow carried
    across where it exists. ``ofto_verified`` and ``reviewed`` are the two
    committed evidence files the corrected ladder reads; omitting them runs
    the rule alone, which is the classification a reader who trusts no human
    review and no per-vintage OFTO enumeration should get."""
    rows: list[dict[str, Any]] = []
    units = list(wind_register_rows(register))
    for unit in units:
        uid = unit.get("elexonBmUnit")
        side, grade, basis = side_of_b6_corrected(
            unit,
            cmis=cmis,
            tec=tec,
            units=units,
            ofto_verified=ofto_verified or {},
            reviewed=reviewed or {},
        )
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


# ------------------------------------------------- the corrected B6 ladder
#
# 015's ``side_of_b6`` is left byte-identical: it is the rule that ran under
# 015's sealed declaration, and a sealed result is never re-run under a rule
# it did not use. What follows is 016's corrected reading of the same three
# sources, with four defects of the 015 rule named and fixed. The defects
# were surfaced by an external classifier's disagreements (see
# ``evidence/reviewed-links.json``); each is recorded and fixed here as a
# defect of the rule, so the corrected reading reproduces without the model.
#
#   D1  First match wins.  015 walks the register in file order and takes the
#       first row passing name and capacity.  ``Baillie Wind Farm`` therefore
#       matched ``Baillie Greener Grid Park`` (a storage and reactive
#       compensation project, 48 MW, within tolerance of 52.5) because that
#       row sorts first, with the exact-name 52.5 MW wind row two lines below.
#       Fixed: every passing row is collected; the side is taken only when all
#       of them agree, and the cited row is the one whose capacity is closest.
#   D2  No plant type test.  ``Rothes Windfarm`` (54.501 MW wind) matched
#       ``Markinch (Rothes) Biomass CHP Plant`` (55 MW biomass) on a shared
#       name token and a coincident capacity.  Fixed: a wind BM unit may only
#       link to a register row whose plant type names wind.
#   D3  OFTO falls through in silence.  ``HOST TO`` is in neither the north
#       nor the south set for the 15 offshore-transmission-owner rows, so
#       units that matched one were left ungraded rather than placed.  OFTO
#       carries no geography of its own, so it is resolved from a committed,
#       per-vintage enumeration of those rows checked by hand against their
#       connection site; a row absent from the enumeration is never placed.
#   D4  The name test cannot see a roman numeral.  ``WALNEY_1`` and ``Walney I
#       Offshore Wind Farm`` are the same project written two ways.  Fixed by
#       normalising i to x to digits on both sides — a normalisation of the
#       existing test, not a loosening of it: the rule still never matches on
#       a name the unit's tokens are not wholly contained in.
#
# Deliberately NOT fixed here: the unit-index suffix (``Ormonde Energy
# Limited 1``, ``Farr Unit 1``).  Stripping a trailing index would let the
# rule match names the unit does not contain, which is the one thing 015's
# ladder promised never to do.  Those units are placed, if at all, through a
# reviewed link.

ROMAN: Final = {
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
    "vi": "6",
    "vii": "7",
    "viii": "8",
    "ix": "9",
    "x": "10",
}
OFTO: Final = "OFTO"
CAPACITY_TOLERANCE: Final = Decimal("0.15")


def normalised_tokens(text: object) -> frozenset[str]:
    """015's tokens with roman numerals i to x read as digits (D4)."""
    return frozenset(ROMAN.get(token, token) for token in tokens(text))


def name_matches(station: object, unit_name: object) -> bool:
    """The unit's tokens are contained in the station's, after D4."""
    station_tokens, unit_tokens = normalised_tokens(station), normalised_tokens(unit_name)
    return bool(unit_tokens) and unit_tokens <= station_tokens


def is_wind_row(row: Mapping[str, str]) -> bool:
    """The register row's plant type names wind (D2)."""
    return "wind" in str(row.get("Plant Type") or "").lower()


def within_capacity_tolerance(a: Decimal | None, b: Decimal | None) -> bool:
    if a is None or b is None or b == Decimal(0):
        return False
    return abs(a - b) / abs(b) <= CAPACITY_TOLERANCE


def row_side(row: Mapping[str, str], ofto_verified: Mapping[str, str]) -> str | None:
    """The side of B6 the row's host transmission owner implies, or None.

    SHET and SPT are north, NGET south. OFTO is not a geography: an offshore
    transmission owner's licence says nothing about which side of the
    Anglo-Scottish boundary the cable lands. Those rows are placed only from
    ``ofto_verified``, the committed per-vintage enumeration checked by hand
    against each row's connection site (D3).
    """
    host = str(row.get("HOST TO") or "").strip().upper()
    if host in NORTH_TOS:
        return "north"
    if host in SOUTH_TOS:
        return "south"
    if host == OFTO:
        return ofto_verified.get(str(row.get("Project Name") or "").strip())
    return None


def name_group(
    row: Mapping[str, str], units: Sequence[Mapping[str, Any]]
) -> list[Mapping[str, Any]]:
    """The distinct wind BM units whose name test passes against `row`.

    **One register row, many BM units.** A TEC row is a connection, not a
    meter: Dudgeon's 400 MW row faces four BM units, Farr's 92 MW row two.
    The group is defined by the row, not by a guess at a name stem, and is
    de-duplicated on the Elexon id so a unit registered twice (``T_WLNYO-4``)
    is not counted twice.
    """
    seen: set[str] = set()
    group: list[Mapping[str, Any]] = []
    for unit in units:
        uid = str(unit.get("elexonBmUnit") or unit.get("nationalGridBmUnit") or "")
        if uid in seen or not uid:
            continue
        if name_matches(row.get("Project Name"), unit.get("bmUnitName")):
            seen.add(uid)
            group.append(unit)
    return group


def capacity_matches(
    row: Mapping[str, str], unit: Mapping[str, Any], units: Sequence[Mapping[str, Any]]
) -> str | None:
    """Which capacity limb the row passes for this unit: per-unit, group, none.

    Declared before it was applied (016 ``AMENDMENTS.md``, 2026-09-16): the
    row's cumulative total capacity must sit within 15 % of **either** the
    unit's own registered capacity **or** the sum over the row's name group.
    Where the group is the unit alone the two limbs are the same test, so
    015's rule is the special case and single-unit stations are unaffected.
    """
    registered = decimal(row.get("Cumulative Total Capacity (MW)"))
    own = decimal(unit.get("generationCapacity"))
    if within_capacity_tolerance(registered, own):
        return "per-unit"
    group = name_group(row, units)
    if len(group) > 1:
        total = sum((decimal(u.get("generationCapacity")) or Decimal(0) for u in group), Decimal(0))
        if within_capacity_tolerance(registered, total):
            return "group"
    return None


def _capacity_distance(row: Mapping[str, str], unit: Mapping[str, Any]) -> Decimal:
    registered = decimal(row.get("Cumulative Total Capacity (MW)"))
    own = decimal(unit.get("generationCapacity"))
    if registered is None or own is None or own == Decimal(0):
        return Decimal(10**6)
    return abs(registered - own) / abs(own)


def tec_link(
    unit: Mapping[str, Any],
    tec: Sequence[Mapping[str, str]],
    units: Sequence[Mapping[str, Any]],
    ofto_verified: Mapping[str, str],
) -> tuple[str, str] | None:
    """(side, basis) from the TEC register, or None where the rule declines.

    Every wind row passing the name and capacity tests is collected (D1). The
    side is returned only where all of them agree; where they disagree the
    rule declines rather than resolving the disagreement by file order.
    """
    passing = [
        (row, limb)
        for row in tec
        if is_wind_row(row)
        and name_matches(row.get("Project Name"), unit.get("bmUnitName"))
        and (limb := capacity_matches(row, unit, units))
    ]
    sides = {side for row, _ in passing if (side := row_side(row, ofto_verified))}
    if len(sides) != 1:
        return None
    side = sides.pop()
    placed = [(row, limb) for row, limb in passing if row_side(row, ofto_verified) == side]
    row, limb = min(placed, key=lambda pair: _capacity_distance(pair[0], unit))
    host = str(row.get("HOST TO") or "").strip().upper()
    extra = "" if len(placed) == 1 else f", {len(placed)} matching rows all {side}"
    limbed = "" if limb == "per-unit" else ", capacity matched over the row's BM unit group"
    return side, f"TEC register row '{row.get('Project Name')}' hosted by {host}{limbed}{extra}"


def side_of_b6_corrected(
    unit: Mapping[str, Any],
    *,
    cmis: Sequence[Mapping[str, str]],
    tec: Sequence[Mapping[str, str]],
    units: Sequence[Mapping[str, Any]],
    ofto_verified: Mapping[str, str],
    reviewed: Mapping[str, Mapping[str, Any]],
) -> tuple[str, str, str]:
    """(side, grade, basis) — 015's ladder with D1 to D4 fixed, plus grade R.

    A CMIS intertrip arming; B the corrected TEC register rule; R a reviewed
    link, proposed by a named model and admitted by a named human against the
    same register evidence the rule reads; C the GSP group; otherwise
    unknown. R sits below the rule and above the GSP group: it is a direct
    reading of the register, which the GSP group is not, but it carries a
    human in the loop, which the rule does not. Dropping every grade R row
    recovers a rule-only classification.
    """
    uid = str(unit.get("elexonBmUnit") or "")
    ngid = str(unit.get("nationalGridBmUnit") or "")
    for row in cmis:
        if (
            str(row.get("BMU ID") or "").strip() in {uid, ngid}
            and str(row.get("B6/EC5") or "").strip().upper() == "B6"
        ):
            return "north", "A", "CMIS intertrip arming lists the unit against B6"
    link = tec_link(unit, tec, units, ofto_verified)
    if link is not None:
        return link[0], "B", link[1]
    entry = reviewed.get(uid)
    if entry is not None and entry.get("verdict") == "accepted":
        return (
            str(entry["side"]),
            "R",
            f"reviewed link to TEC register row '{entry['project_name']}' hosted by "
            f"{entry['host_to']} (proposed by {entry['proposer']} at p {entry['p_same']}, "
            f"accepted on review {entry['reviewed_on']})",
        )
    gsp = str(unit.get("gspGroupId") or "")
    if gsp:
        return ("north" if gsp in NORTH_GSP_GROUPS else "south"), "C", f"GSP group {gsp}"
    return "unknown", "-", "no graded evidence"
