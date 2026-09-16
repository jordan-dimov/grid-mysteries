"""Investigation 015 — support and storage on the record day.

Pure logic over pinned records; no I/O. The declaration in
`investigations/015-support-and-storage-on-the-record-day/DECLARATION.md`
governs. Column names of the acquired registers reach this module through
`reading`, the role-to-column bindings written after the schema pass, so
the rules here speak of roles (station name, capacity, identifier) and
never of a publisher's header.

Part 1: the wind units paid on bids, each linked to the CfD register by the
publisher's own BM-unit mapping (grade A) and to the RO register by a
declared name-and-capacity test (grade B, or C without capacity), and the
day's bid volume, cashflow and price per scheme.

Part 2: every energy-limited unit (any MDO or MDB record on the day), its
registered capacities, its side of B6 by graded evidence, and its hours of
energy at two vintages, beside the constraint's duration.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.investigations import cover_price as cp
from grid_mysteries.investigations import record_day as rd

ZERO: Final = Decimal(0)
CAPACITY_TOLERANCE: Final = Decimal("0.15")
GENERIC_TOKENS: Final = frozenset(
    {
        "wind",
        "farm",
        "windfarm",
        "wf",
        "offshore",
        "onshore",
        "energy",
        "power",
        "station",
        "limited",
        "ltd",
        "plc",
        "phase",
        "extension",
    }
)
NORTH_GSP_GROUPS: Final = frozenset({"_P", "_N"})
NORTH_TOS: Final = frozenset({"SHET", "SPT"})
SOUTH_TOS: Final = frozenset({"NGET"})


# ------------------------------------------------------------- normalising


def tokens(text: object) -> frozenset[str]:
    """Lower-case alphanumeric tokens with the declared generic words removed."""
    words = re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).split()
    return frozenset(w for w in words if w not in GENERIC_TOKENS)


def name_match(station: object, unit_name: object) -> bool:
    """The station's tokens equal, or are a superset of, the unit's tokens."""
    s, u = tokens(station), tokens(unit_name)
    return bool(u) and (s == u or u <= s)


def decimal(value: object) -> Decimal | None:
    text = str(value if value is not None else "").replace(",", "").strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except ArithmeticError:
        return None


def within_tolerance(a: Decimal | None, b: Decimal | None) -> bool:
    if a is None or b is None or b == ZERO:
        return False
    return abs(a - b) / abs(b) <= CAPACITY_TOLERANCE


def parse_day(value: object) -> date | None:
    text = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(text[: 26 if "T" in fmt else 10], fmt).date()
        except ValueError:
            continue
    return None


# --------------------------------------------------------------- link table


@dataclass(frozen=True)
class Link:
    unit: str
    register: str
    target: str
    grade: str
    basis: str
    extra: dict[str, str] = field(default_factory=dict)


def cfd_links(
    unit: dict[str, Any],
    mapping: list[dict[str, str]],
    portfolio: dict[str, dict[str, str]],
    day: date,
    reading: dict[str, Any],
) -> list[Link]:
    """Grade A: the publisher's own BM-unit id, effective on the day."""
    ids = {str(unit.get("elexonBmUnit") or ""), str(unit.get("nationalGridBmUnit") or "")}
    out = []
    for row in mapping:
        if str(row.get(reading["cfd_map_bmu"]) or "").strip() not in ids:
            continue
        start = parse_day(row.get(reading["cfd_map_from"]))
        end = parse_day(row.get(reading["cfd_map_to"]))
        if (start is not None and start > day) or (end is not None and end < day):
            continue
        cfd_id = str(row.get(reading["cfd_map_id"]) or "").strip()
        contract = portfolio.get(cfd_id, {})
        out.append(
            Link(
                unit["elexonBmUnit"],
                "cfd",
                cfd_id,
                "A",
                "LCCC CfD-to-BM-unit mapping, effective on the day",
                {
                    "name": str(contract.get(reading.get("cfd_name", ""), "") or ""),
                    "technology": str(contract.get(reading.get("cfd_technology", ""), "") or ""),
                    "capacity_mw": str(contract.get(reading.get("cfd_capacity", ""), "") or ""),
                    "status": str(contract.get(reading.get("cfd_status", ""), "") or ""),
                },
            )
        )
    return out


def ro_links(
    unit: dict[str, Any],
    ro: list[dict[str, str]],
    reading: dict[str, Any],
    station_capacity_units: dict[str, Decimal],
) -> list[Link]:
    """Grade A by identifier if the report carries one; else B by name and
    capacity, C by name alone or by lead party."""
    out = []
    unit_id = str(unit.get("elexonBmUnit") or "")
    unit_name = unit.get("bmUnitName")
    lead = unit.get("leadPartyName")
    id_col = reading.get("ro_bmu")
    name_col, cap_col, acc_col = reading["ro_station"], reading.get("ro_capacity"), reading["ro_id"]
    for row in ro:
        acc = str(row.get(acc_col) or "").strip()
        station = row.get(name_col)
        if id_col and str(row.get(id_col) or "").strip() == unit_id:
            out.append(
                Link(
                    unit_id,
                    "ro",
                    acc,
                    "A",
                    "RO report BM-unit identifier",
                    {"station": str(station or "")},
                )
            )
            continue
        if name_match(station, unit_name):
            cap = decimal(row.get(cap_col)) if cap_col else None
            if cap is not None and reading.get("ro_capacity_unit") == "kW":
                cap = cap / Decimal(1000)
            summed = station_capacity_units.get(acc, decimal(unit.get("generationCapacity")))
            if cap_col and within_tolerance(cap, summed):
                out.append(
                    Link(
                        unit_id,
                        "ro",
                        acc,
                        "B",
                        "station name matches unit name; capacity within 15 %",
                        {"station": str(station or ""), "capacity_mw": str(cap)},
                    )
                )
            else:
                basis = "station name matches unit name; capacity outside 15 % or absent"
                out.append(
                    Link(
                        unit_id,
                        "ro",
                        acc,
                        "C",
                        basis,
                        {
                            "station": str(station or ""),
                            "capacity_mw": str(cap) if cap is not None else "",
                        },
                    )
                )
        elif lead and name_match(station, lead):
            out.append(
                Link(
                    unit_id,
                    "ro",
                    acc,
                    "C",
                    "station name matches lead party only",
                    {"station": str(station or "")},
                )
            )
    return out


def scheme_of(links: list[Link]) -> str:
    grades = {(link.register, link.grade) for link in links}
    cfd = ("cfd", "A") in grades
    ro = ("ro", "A") in grades or ("ro", "B") in grades
    if cfd and ro:
        return "both"
    if cfd:
        return "cfd"
    if ro:
        return "ro"
    if ("ro", "C") in grades:
        return "ro-possible"
    return "unmatched"


# ------------------------------------------------------------- volume gate


@dataclass
class Volumes:
    """Accepted MWh by DISPTAV type, per unit and direction, and wind-unit
    bid MWh per period, over the day's 96 period files."""

    totals: dict[str, dict[str, Decimal]] = field(
        default_factory=lambda: {t: {d: ZERO for d in ("offer", "bid")} for t in cp.DATA_TYPES}
    )
    per_unit: dict[str, dict[str, dict[str, Decimal]]] = field(
        default_factory=lambda: {
            t: {d: defaultdict(lambda: ZERO) for d in ("offer", "bid")} for t in cp.DATA_TYPES
        }
    )
    wind_bid_by_period: dict[str, dict[int, Decimal]] = field(
        default_factory=lambda: {t: defaultdict(lambda: ZERO) for t in cp.DATA_TYPES}
    )

    def unit_mwh(self, unit: str, direction: str, kind: str | None) -> Decimal | None:
        if kind is None:
            return None
        return self.per_unit[kind][direction].get(unit, ZERO)


def accepted_volumes(
    disptav: dict[tuple[str, int], list[dict]], prices: list[dict], fuel_of: dict[str, str]
) -> tuple[dict[str, Any], Volumes]:
    """013's gate: the DISPTAV type that reconciles with the settlement totals,
    with the per-unit volumes kept for every type."""
    volumes = Volumes()
    for (direction, period), records in disptav.items():
        for kind, per_unit in cp.volumes_by_type(records).items():
            for unit, mwh in per_unit.items():
                volumes.totals[kind][direction] += mwh
                volumes.per_unit[kind][direction][unit] += mwh
                if direction == "bid" and rd.fuel_class(fuel_of.get(unit)) == "wind":
                    volumes.wind_bid_by_period[kind][period] += mwh
    return cp.reconcile(volumes.totals, cp.settlement_totals(prices)), volumes


def period_start_utc(day: date, period: int) -> datetime:
    """Start of a settlement period in UTC. 8 September 2026 is in British
    Summer Time, so period 1 starts at 23:00Z the evening before; the
    clock-change days are outside this study."""
    first = datetime(day.year, day.month, day.day, tzinfo=UTC) - timedelta(hours=1)
    return first + timedelta(minutes=30 * (period - 1))


# ------------------------------------------------------------------ part 1


def wind_by_scheme(
    day: date,
    register: dict[str, dict[str, Any]],
    bids: list[dict],
    disptav: dict,
    prices: list[dict],
    mapping: list[dict[str, str]],
    portfolio: list[dict[str, str]],
    ro: list[dict[str, str]],
    reading: dict[str, Any],
) -> tuple[dict[str, Any], list[Link]]:
    fuel_of = {k: (r.get("fuelType") or "") for k, r in register.items()}
    rows = rd.cashflow_rows(bids, "bid")
    wind_units = sorted({r.unit for r in rows if fuel_of.get(r.unit) == "WIND"})
    portfolio_by_id = {str(p.get(reading["cfd_id"]) or "").strip(): p for p in portfolio}
    reconciliation, pairing = accepted_volumes(disptav, prices, fuel_of)
    chosen = reconciliation["chosen"]
    # capacity summed over every wind unit whose name matches the same RO station
    station_units: dict[str, Decimal] = defaultdict(lambda: ZERO)
    for u in wind_units:
        for row in ro:
            if name_match(row.get(reading["ro_station"]), register[u].get("bmUnitName")):
                station_units[str(row.get(reading["ro_id"]) or "").strip()] += (
                    decimal(register[u].get("generationCapacity")) or ZERO
                )
    links: list[Link] = []
    per_unit: list[dict[str, Any]] = []
    for u in wind_units:
        unit = register[u]
        ulinks = cfd_links(unit, mapping, portfolio_by_id, day, reading) + ro_links(
            unit, ro, reading, dict(station_units)
        )
        links += ulinks
        paid = sum((r.gbp for r in rows if r.unit == u and r.gbp > ZERO), ZERO)
        signed = sum((r.gbp for r in rows if r.unit == u), ZERO)
        mwh = pairing.unit_mwh(u, "bid", chosen)
        per_unit.append(
            {
                "unit": u,
                "name": unit.get("bmUnitName"),
                "lead_party": unit.get("leadPartyName"),
                "generation_capacity_mw": unit.get("generationCapacity"),
                "scheme": scheme_of(ulinks),
                "links": [link.__dict__ for link in ulinks],
                "bid_paid_gbp": paid,
                "bid_signed_gbp": signed,
                "bid_mwh": mwh,
            }
        )
    schemes = ("cfd", "ro", "both", "ro-possible", "unmatched")
    total_paid = sum((r["bid_paid_gbp"] for r in per_unit), ZERO)
    table = []
    for scheme in schemes:
        group = [r for r in per_unit if r["scheme"] == scheme]
        paid = sum((r["bid_paid_gbp"] for r in group), ZERO)
        mwh = (
            sum((r["bid_mwh"] for r in group if r["bid_mwh"] is not None), ZERO) if chosen else None
        )
        table.append(
            {
                "scheme": scheme,
                "units": len(group),
                "bid_mwh": mwh,
                "bid_paid_gbp": paid,
                "bid_signed_gbp": sum((r["bid_signed_gbp"] for r in group), ZERO),
                "gbp_per_mwh": (paid / mwh).quantize(Decimal("0.01")) if mwh else None,
                "share_of_wind_bid_gbp": (paid / total_paid).quantize(Decimal("0.0001"))
                if total_paid
                else None,
            }
        )
    return {
        "day": day,
        "wind_units": len(wind_units),
        "reconciliation": reconciliation,
        "disptav_type": chosen,
        "total_wind_bid_paid_gbp": total_paid,
        "table": table,
        "units": per_unit,
    }, links


# ------------------------------------------------------------------ part 2


def side_of_b6(
    unit: dict[str, Any], cmis: list[dict[str, str]], tec: list[dict[str, str]]
) -> tuple[str, str, str]:
    """(side, grade, basis) by the declared ladder; never by name alone."""
    uid = str(unit.get("elexonBmUnit") or "")
    ngid = str(unit.get("nationalGridBmUnit") or "")
    for row in cmis:
        if (
            str(row.get("BMU ID") or "").strip() in {uid, ngid}
            and str(row.get("B6/EC5") or "").strip().upper() == "B6"
        ):
            return "north", "A", "CMIS intertrip arming lists the unit against B6"
    cap = decimal(unit.get("generationCapacity"))
    for row in tec:
        if name_match(row.get("Project Name"), unit.get("bmUnitName")) and within_tolerance(
            decimal(row.get("Cumulative Total Capacity (MW)")), cap
        ):
            host = str(row.get("HOST TO") or "").strip().upper()
            if host in NORTH_TOS:
                return (
                    "north",
                    "B",
                    f"TEC register row '{row.get('Project Name')}' hosted by {host}",
                )
            if host in SOUTH_TOS:
                return (
                    "south",
                    "B",
                    f"TEC register row '{row.get('Project Name')}' hosted by {host}",
                )
    gsp = str(unit.get("gspGroupId") or "")
    if gsp:
        return ("north" if gsp in NORTH_GSP_GROUPS else "south"), "C", f"GSP group {gsp}"
    return "unknown", "-", "no graded evidence"


def energy_bound(records: list[dict], unit: str, before: datetime | None) -> Decimal | None:
    """The unit's largest published level on the day by magnitude (MWh; MDB
    levels are negative as published); with `before`, only records
    published before that instant (public-as-of)."""
    best: Decimal | None = None
    for r in records:
        if r.get("bmUnit") != unit:
            continue
        if before is not None:
            published = datetime.fromisoformat(str(r["publishTime"]).replace("Z", "+00:00"))
            if published >= before:
                continue
        for key in ("levelFrom", "levelTo"):
            level = decimal(r.get(key))
            if level is not None and (best is None or abs(level) > abs(best)):
                best = level
    return best


def hours(energy: Decimal | None, capacity: Decimal | None) -> Decimal | None:
    """Hours at the registered capacity. MDB levels are published negative
    (import), as is the import capacity; both are taken by magnitude."""
    if energy is None or capacity is None or capacity == ZERO:
        return None
    return (abs(energy) / abs(capacity)).quantize(Decimal("0.01"))


def constraint_duration(volumes: Volumes, chosen: str | None) -> dict[str, Any]:
    """Periods with accepted wind-unit bid volume under the gate; longest run."""
    if not chosen:
        return {"periods": None, "hours": None, "longest_run_periods": None, "first_period": None}
    periods = sorted(p for p in range(1, 49) if volumes.wind_bid_by_period[chosen][p] > ZERO)
    longest = run = 0
    previous = None
    for p in periods:
        run = run + 1 if previous is not None and p == previous + 1 else 1
        longest = max(longest, run)
        previous = p
    return {
        "periods": len(periods),
        "hours": Decimal(len(periods)) / 2,
        "longest_run_periods": longest,
        "longest_run_hours": Decimal(longest) / 2,
        "first_period": periods[0] if periods else None,
        "period_list": periods,
    }


def storage_table(
    day: date,
    register: dict[str, dict[str, Any]],
    bids: list[dict],
    offers: list[dict],
    pairing: Volumes,
    chosen: str | None,
    mdo: list[dict],
    mdb: list[dict],
    cmis: list[dict[str, str]],
    tec: list[dict[str, str]],
    first_period: int | None,
) -> list[dict[str, Any]]:
    units = sorted({str(r.get("bmUnit")) for r in mdo} | {str(r.get("bmUnit")) for r in mdb})
    cash = {d: rd.cashflow_rows(rows, d) for d, rows in (("bid", bids), ("offer", offers))}
    # public-as-of instant: the start of the first constrained period (UTC)
    before = period_start_utc(day, first_period) if first_period else None
    out = []
    for u in units:
        unit = register.get(u, {"elexonBmUnit": u})
        gen, dem = decimal(unit.get("generationCapacity")), decimal(unit.get("demandCapacity"))
        side, grade, basis = side_of_b6(unit, cmis, tec)
        row: dict[str, Any] = {
            "unit": u,
            "name": unit.get("bmUnitName"),
            "lead_party": unit.get("leadPartyName"),
            "bm_unit_type": unit.get("bmUnitType"),
            "fuel_type": unit.get("fuelType"),
            "export_capacity_mw": gen,
            "import_capacity_mw": dem,
            "side_of_b6": side,
            "side_grade": grade,
            "side_basis": basis,
            "mdo_max_mwh_r3h": energy_bound(mdo, u, None),
            "mdb_max_mwh_r3h": energy_bound(mdb, u, None),
            "mdo_max_mwh_r3p": energy_bound(mdo, u, before),
            "mdb_max_mwh_r3p": energy_bound(mdb, u, before),
        }
        row["export_hours_r3h"] = hours(row["mdo_max_mwh_r3h"], gen)
        row["export_hours_r3p"] = hours(row["mdo_max_mwh_r3p"], gen)
        row["import_hours_r3h"] = hours(row["mdb_max_mwh_r3h"], dem)
        row["import_hours_r3p"] = hours(row["mdb_max_mwh_r3p"], dem)
        for direction in ("bid", "offer"):
            rows = [r for r in cash[direction] if r.unit == u]
            row[f"{direction}_paid_gbp"] = (
                sum((r.gbp for r in rows if r.gbp > ZERO), ZERO) if rows else None
            )
            row[f"{direction}_mwh"] = pairing.unit_mwh(u, direction, chosen)
            row[f"{direction}_rows"] = len(rows)
        out.append(row)
    return out


# --------------------------------------------------------------------- run


def run(
    *,
    day: date,
    register: dict[str, dict[str, Any]],
    bids: list[dict],
    offers: list[dict],
    disptav: dict,
    prices: list[dict],
    mapping: list[dict[str, str]],
    portfolio: list[dict[str, str]],
    ro: list[dict[str, str]],
    cmis: list[dict[str, str]],
    tec: list[dict[str, str]],
    mdo: list[dict],
    mdb: list[dict],
    reading: dict[str, Any],
) -> dict[str, Any]:
    wind, links = wind_by_scheme(
        day, register, bids, disptav, prices, mapping, portfolio, ro, reading
    )
    fuel_of = {k: (r.get("fuelType") or "") for k, r in register.items()}
    reconciliation, pairing = accepted_volumes(disptav, prices, fuel_of)
    chosen = reconciliation["chosen"]
    constraint = constraint_duration(pairing, chosen)
    storage = storage_table(
        day,
        register,
        bids,
        offers,
        pairing,
        chosen,
        mdo,
        mdb,
        cmis,
        tec,
        constraint.get("first_period"),
    )
    by_scheme = {row["scheme"]: row for row in wind["table"]}
    s1 = None
    if by_scheme["unmatched"]["bid_paid_gbp"] > max(
        by_scheme["ro"]["bid_paid_gbp"], by_scheme["cfd"]["bid_paid_gbp"]
    ):
        s1 = "not determinable"
    else:
        s1 = (
            "holds"
            if by_scheme["ro"]["bid_paid_gbp"] > by_scheme["cfd"]["bid_paid_gbp"]
            else "fails"
        )
    s2 = "undecided"
    if by_scheme["ro"]["gbp_per_mwh"] is not None and by_scheme["cfd"]["gbp_per_mwh"] is not None:
        s2 = (
            "holds" if by_scheme["ro"]["gbp_per_mwh"] > by_scheme["cfd"]["gbp_per_mwh"] else "fails"
        )
    b1 = "undecided"
    if constraint.get("longest_run_hours") is not None:
        deciders = [
            r
            for r in storage
            if r["side_of_b6"] == "north"
            and r["side_grade"] in ("A", "B")
            and r["export_hours_r3p"] is not None
        ]
        covering = [
            r["unit"] for r in deciders if r["export_hours_r3p"] >= constraint["longest_run_hours"]
        ]
        b1 = "fails" if covering else ("holds" if deciders else "undecided")
        constraint["b1_deciding_units"] = len(deciders)
        constraint["b1_covering_units"] = covering
    return {
        "day": day,
        "links": [link.__dict__ for link in links],
        "wind": wind,
        "storage": storage,
        "constraint": constraint,
        "storage_units": len(storage),
        "propositions": {"S1": s1, "S2": s2, "B1": b1},
        "reconciliation": reconciliation,
    }
