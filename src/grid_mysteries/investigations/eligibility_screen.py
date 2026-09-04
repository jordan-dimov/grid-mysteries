"""011 — who loses eligibility: pure logic for the FPN-eligibility screen.

For each battery BMU and settlement period: was a valid Final Physical
Notification present under a structural rule (present / covering /
non-zero); was the unit holding an accepted response position covering the
period; if both, the period is deemed unavailable. Revenue at stake is
executed MW × clearing price (£/MW/h) × hours, in Decimal, under two
forfeit scopes (the period's payment, or the whole delivery block's).
Every rule and scope is computed in one pass so the choice of primary,
made from the pinned terms, cannot steer the numbers. No network; replays
from plain dict rows.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
ZERO = Decimal(0)
PENNY = Decimal("0.01")
HALF_HOUR = timedelta(minutes=30)
HOURS_PER_PERIOD = Decimal("0.5")
RULE = "011/fpn-eligibility-screen/v1"
VALIDITY_RULES: tuple[str, ...] = ("present", "covering", "non_zero")
FORFEIT_SCOPES: tuple[str, ...] = ("period", "block")
#: EFA blocks start at these local clock hours (EFA 1 = 23:00–03:00).
EFA_BLOCK_START_HOURS: frozenset[int] = frozenset({23, 3, 7, 11, 15, 19})
#: Periods at risk that all fall in one run shorter than a day are an
#: outage, not a bookkeeping exposure (declaration, *Milestone test*).
SINGLE_RUN_PERIODS = 48
MILESTONE_BAR = Decimal("0.01")

Period = tuple[str, int]


# --------------------------------------------------------------------------
# Settlement-period arithmetic (local Europe/London half-hours from 00:00)


def day_start_utc(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=LONDON).astimezone(UTC)


def periods_in_day(day: date) -> int:
    """46, 48 or 50 settlement periods, from the local day's true length."""
    span = day_start_utc(day + timedelta(days=1)) - day_start_utc(day)
    return int(span / HALF_HOUR)


def period_start_utc(day: date, period: int) -> datetime:
    if not 1 <= period <= periods_in_day(day):
        raise ValueError(f"{day} has no settlement period {period}")
    return day_start_utc(day) + HALF_HOUR * (period - 1)


def period_of(instant: datetime) -> Period:
    """The (settlement date, period) containing an aware instant."""
    if instant.tzinfo is None:
        raise ValueError("period_of needs an aware datetime")
    local = instant.astimezone(LONDON)
    day = local.date()
    offset = instant.astimezone(UTC) - day_start_utc(day)
    return day.isoformat(), int(offset / HALF_HOUR) + 1


def window_periods(start: date, end: date) -> list[Period]:
    """Every settlement period of the inclusive day range, in order."""
    out: list[Period] = []
    day = start
    while day <= end:
        out.extend((day.isoformat(), p) for p in range(1, periods_in_day(day) + 1))
        day += timedelta(days=1)
    return out


# --------------------------------------------------------------------------
# Timestamps


def parse_timestamp(text: object) -> datetime:
    """ISO 8601 text to a datetime; a trailing Z becomes UTC. Naive input
    stays naive so the caller can apply the inferred basis."""
    value = str(text).strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def to_utc(moment: datetime, basis: str) -> datetime:
    if moment.tzinfo is not None:
        return moment.astimezone(UTC)
    if basis == "utc":
        return moment.replace(tzinfo=UTC)
    if basis == "local":
        return moment.replace(tzinfo=LONDON).astimezone(UTC)
    raise ValueError(f"unknown timestamp basis {basis!r}")


def infer_timestamp_basis(starts: Iterable[datetime]) -> dict[str, Any]:
    """Which reading of naive delivery-start timestamps puts them on EFA
    block boundaries (local 23:00, 03:00, ...): 'utc', 'local', or
    'undetermined' when neither wins. Aware inputs need no inference."""
    counts = {"utc": 0, "local": 0}
    total = 0
    for start in starts:
        total += 1
        if start.tzinfo is not None:
            counts["utc"] += 1
            counts["local"] += 1
            continue
        for basis in counts:
            local = to_utc(start, basis).astimezone(LONDON)
            if local.minute == 0 and local.hour in EFA_BLOCK_START_HOURS:
                counts[basis] += 1
    if total == 0 or counts["utc"] == counts["local"]:
        basis = "undetermined" if total else "no-rows"
    else:
        basis = max(counts, key=lambda k: counts[k])
    return {"basis": basis, "rows": total, "on_efa_boundary": counts}


# --------------------------------------------------------------------------
# Physical notifications


@dataclass(frozen=True, slots=True)
class PNRecord:
    unit: str
    settlement_date: str
    period: int
    time_from: datetime
    time_to: datetime
    level_from: Decimal
    level_to: Decimal


def pn_from_record(record: Mapping[str, Any]) -> PNRecord:
    """An Elexon Insights PN record (physical/all or datasets/PN/stream)."""
    return PNRecord(
        unit=str(record["bmUnit"]),
        settlement_date=str(record["settlementDate"])[:10],
        period=int(record["settlementPeriod"]),
        time_from=to_utc(parse_timestamp(record["timeFrom"]), "utc"),
        time_to=to_utc(parse_timestamp(record["timeTo"]), "utc"),
        level_from=Decimal(str(record["levelFrom"])),
        level_to=Decimal(str(record["levelTo"])),
    )


def fpn_status(records: Sequence[PNRecord], start: datetime, end: datetime) -> dict[str, bool]:
    """The three structural readings of one unit-period's PN records."""
    present = bool(records)
    intervals = sorted(
        (max(r.time_from, start), min(r.time_to, end))
        for r in records
        if r.time_to > start and r.time_from < end
    )
    reached = start
    for a, b in intervals:
        if a > reached:
            break
        reached = max(reached, b)
    covering = present and reached >= end
    non_zero = covering and any(r.level_from != ZERO or r.level_to != ZERO for r in records)
    return {"present": present, "covering": covering, "non_zero": non_zero}


def index_pn(records: Iterable[PNRecord]) -> dict[tuple[str, Period], list[PNRecord]]:
    index: dict[tuple[str, Period], list[PNRecord]] = defaultdict(list)
    for r in records:
        index[(r.unit, (r.settlement_date, r.period))].append(r)
    return index


# --------------------------------------------------------------------------
# Response positions


@dataclass(frozen=True, slots=True)
class Position:
    unit: str
    service: str
    product: str
    family: str
    delivery_start: datetime
    delivery_end: datetime
    mw: Decimal
    price_gbp_per_mw_h: Decimal

    def periods(self) -> list[Period]:
        out: list[Period] = []
        t = self.delivery_start
        while t < self.delivery_end:
            out.append(period_of(t))
            t += HALF_HOUR
        return out


def response_family(service_type: object, auction_product: object = "") -> str | None:
    """DC / DM / DR from the dataset's own service vocabulary, or None for
    anything that is not a Dynamic Response Service (reserve products)."""
    text = f"{service_type} {auction_product}".upper()
    for family, words in (
        ("DC", ("CONTAINMENT",)),
        ("DM", ("MODERATION",)),
        ("DR", ("REGULATION",)),
    ):
        if any(w in text for w in words):
            return family
    code = str(service_type).upper().replace("-", "").replace(" ", "")
    for family in ("DC", "DM", "DR"):
        if code.startswith(family) and (len(code) == 2 or code[2] in "HL"):
            return family
    return None


def positions_from_eac_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    unit_map: Mapping[str, str],
    basis: str,
    unit_field: str = "auctionUnit",
) -> dict[str, Any]:
    """Accepted response positions from EAC result rows. Rows with zero
    executed quantity, non-response services, or units that do not map
    to an Elexon id are counted and listed, never silently dropped."""
    positions: list[Position] = []
    unmapped: set[str] = set()
    skipped = {"zero_quantity": 0, "not_response": 0, "unmapped": 0, "bad_interval": 0}
    services: dict[str, str | None] = {}
    for row in rows:
        service = str(row.get("serviceType", ""))
        product = str(row.get("auctionProduct", ""))
        family = response_family(service, product)
        services.setdefault(f"{service}|{product}", family)
        if family is None:
            skipped["not_response"] += 1
            continue
        mw = Decimal(str(row.get("executedQuantity") or "0"))
        if mw <= ZERO:
            skipped["zero_quantity"] += 1
            continue
        ng_unit = str(row.get(unit_field, ""))
        unit = unit_map.get(ng_unit)
        if unit is None:
            unmapped.add(ng_unit)
            skipped["unmapped"] += 1
            continue
        start = to_utc(parse_timestamp(row["deliveryStart"]), basis)
        end = to_utc(parse_timestamp(row["deliveryEnd"]), basis)
        if end <= start or (end - start) % HALF_HOUR:
            skipped["bad_interval"] += 1
            continue
        positions.append(
            Position(
                unit=unit,
                service=service,
                product=product,
                family=family,
                delivery_start=start,
                delivery_end=end,
                mw=mw,
                price_gbp_per_mw_h=Decimal(str(row.get("clearingPrice") or "0")),
            )
        )
    return {
        "positions": positions,
        "unmapped_units": sorted(unmapped),
        "skipped": skipped,
        "service_vocabulary": dict(sorted(services.items())),
    }


# --------------------------------------------------------------------------
# The screen


def money(value: Decimal) -> str:
    return str(value.quantize(PENNY))


def ratio(numerator: Decimal | int, denominator: Decimal | int) -> str | None:
    if not denominator:
        return None
    return str((Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.0001")))


def contiguous_runs(indices: Iterable[int]) -> list[int]:
    """Lengths of maximal runs of consecutive integers."""
    runs: list[int] = []
    previous: int | None = None
    for i in sorted(set(indices)):
        if previous is not None and i == previous + 1:
            runs[-1] += 1
        else:
            runs.append(1)
        previous = i
    return runs


def screen(
    request: Mapping[str, Any],
    pn_records: Iterable[PNRecord],
    positions: Iterable[Position],
) -> dict[str, Any]:
    """The JSON contract. `request` carries `window: {from, to}` (inclusive
    ISO dates), `units` (Elexon ids in the population), `validity_rule`
    (the primary structural rule) and `forfeit_scope` (the primary scope);
    every rule and scope is computed and the primary is labelled."""
    primary_rule = str(request.get("validity_rule", "covering"))
    primary_scope = str(request.get("forfeit_scope", "period"))
    if primary_rule not in VALIDITY_RULES or primary_scope not in FORFEIT_SCOPES:
        raise ValueError("unknown validity rule or forfeit scope")
    hours = Decimal(str(request.get("hours_per_period", HOURS_PER_PERIOD)))
    start = date.fromisoformat(request["window"]["from"])
    end = date.fromisoformat(request["window"]["to"])
    periods = window_periods(start, end)
    index_of = {p: i for i, p in enumerate(periods)}
    population = set(request.get("units") or ())
    pn_index = index_pn(pn_records)

    per_unit: dict[str, dict[str, Any]] = {}
    for pos in positions:
        if population and pos.unit not in population:
            continue
        # The block is the position's own delivery interval, clipped to the window.
        block = [p for p in pos.periods() if p in index_of]
        if not block:
            continue
        unit = per_unit.setdefault(
            pos.unit,
            {
                "held": {},  # Period -> set of family
                "status": {},  # Period -> fpn status
                "revenue_held": ZERO,
                "at_stake": {r: {s: ZERO for s in FORFEIT_SCOPES} for r in VALIDITY_RULES},
                "by_family": defaultdict(lambda: {"periods_held": 0, "revenue_held": ZERO}),
            },
        )
        fee = pos.mw * pos.price_gbp_per_mw_h * hours
        unit["revenue_held"] += fee * len(block)
        fam = unit["by_family"][pos.family]
        fam["periods_held"] += len(block)
        fam["revenue_held"] += fee * len(block)
        failed = {r: 0 for r in VALIDITY_RULES}
        for p in block:
            unit["held"].setdefault(p, set()).add(pos.family)
            if p not in unit["status"]:
                day = date.fromisoformat(p[0])
                p_start = period_start_utc(day, p[1])
                unit["status"][p] = fpn_status(
                    pn_index.get((pos.unit, p), []), p_start, p_start + HALF_HOUR
                )
            for r in VALIDITY_RULES:
                if not unit["status"][p][r]:
                    failed[r] += 1
        for r in VALIDITY_RULES:
            unit["at_stake"][r]["period"] += fee * failed[r]
            if failed[r]:
                unit["at_stake"][r]["block"] += fee * len(block)

    units_out: dict[str, Any] = {}
    totals_by_rule: dict[str, dict[str, Any]] = {
        r: {
            "units_with_any_unavailable": 0,
            "periods_at_risk": 0,
            "revenue_at_stake_gbp": {s: ZERO for s in FORFEIT_SCOPES},
        }
        for r in VALIDITY_RULES
    }
    revenue_held_total = ZERO
    for unit_id in sorted(per_unit):
        u = per_unit[unit_id]
        held = sorted(u["held"], key=lambda p: index_of[p])
        revenue_held_total += u["revenue_held"]
        unavailable: dict[str, list[Period]] = {
            r: [p for p in held if not u["status"][p][r]] for r in VALIDITY_RULES
        }
        for r in VALIDITY_RULES:
            if unavailable[r]:
                totals_by_rule[r]["units_with_any_unavailable"] += 1
            totals_by_rule[r]["periods_at_risk"] += len(unavailable[r])
            for s in FORFEIT_SCOPES:
                totals_by_rule[r]["revenue_at_stake_gbp"][s] += u["at_stake"][r][s]
        primary_unavailable = unavailable[primary_rule]
        units_out[unit_id] = {
            "periods_held": len(held),
            "revenue_held_gbp": money(u["revenue_held"]),
            "by_family": {
                f: {"periods_held": v["periods_held"], "revenue_held_gbp": money(v["revenue_held"])}
                for f, v in sorted(u["by_family"].items())
            },
            "by_rule": {
                r: {
                    "periods_deemed_unavailable": len(unavailable[r]),
                    "share_of_held_periods": ratio(len(unavailable[r]), len(held)),
                    "revenue_at_stake_gbp": {s: money(u["at_stake"][r][s]) for s in FORFEIT_SCOPES},
                }
                for r in VALIDITY_RULES
            },
            "primary": {
                "periods_deemed_unavailable": len(primary_unavailable),
                "share_of_held_periods": ratio(len(primary_unavailable), len(held)),
                "revenue_at_stake_gbp": money(u["at_stake"][primary_rule][primary_scope]),
                "share_of_revenue_held": ratio(
                    u["at_stake"][primary_rule][primary_scope], u["revenue_held"]
                ),
                "runs": contiguous_runs(index_of[p] for p in primary_unavailable),
            },
            "unavailable_periods": [
                {
                    "settlement_date": p[0],
                    "period": p[1],
                    "families": sorted(u["held"][p]),
                    "fpn": u["status"][p],
                }
                for p in primary_unavailable
            ],
        }
    primary_totals = totals_by_rule[primary_rule]
    at_stake_primary = primary_totals["revenue_at_stake_gbp"][primary_scope]
    return {
        "rule": RULE,
        "request": {
            **dict(request),
            "validity_rule": primary_rule,
            "forfeit_scope": primary_scope,
            "hours_per_period": str(hours),
        },
        "window": {"from": start.isoformat(), "to": end.isoformat(), "periods": len(periods)},
        "totals": {
            "units_holding": len(units_out),
            "units_with_any_unavailable": primary_totals["units_with_any_unavailable"],
            "periods_at_risk": primary_totals["periods_at_risk"],
            "revenue_held_gbp": money(revenue_held_total),
            "revenue_at_stake_gbp": money(at_stake_primary),
            "share_of_revenue_held": ratio(at_stake_primary, revenue_held_total),
            "by_rule": {
                r: {
                    "units_with_any_unavailable": t["units_with_any_unavailable"],
                    "periods_at_risk": t["periods_at_risk"],
                    "revenue_at_stake_gbp": {
                        s: money(v) for s, v in t["revenue_at_stake_gbp"].items()
                    },
                }
                for r, t in totals_by_rule.items()
            },
        },
        "units": units_out,
    }


# --------------------------------------------------------------------------
# Concentration and the milestone test


def concentration(result: Mapping[str, Any], unit_to_party: Mapping[str, str]) -> list[dict]:
    """Revenue held and at stake (primary rule and scope) by lead party,
    largest exposure first. Units without a party are grouped as 'unknown'."""
    groups: dict[str, dict[str, Any]] = {}
    for unit_id, u in result["units"].items():
        party = unit_to_party.get(unit_id, "unknown")
        g = groups.setdefault(
            party, {"party": party, "units": [], "held": ZERO, "at_stake": ZERO, "runs": []}
        )
        g["units"].append(unit_id)
        g["held"] += Decimal(u["revenue_held_gbp"])
        g["at_stake"] += Decimal(u["primary"]["revenue_at_stake_gbp"])
        g["runs"].extend(u["primary"]["runs"])
    out = []
    for g in sorted(groups.values(), key=lambda g: (-g["at_stake"], g["party"])):
        out.append(
            {
                "party": g["party"],
                "units": sorted(g["units"]),
                "revenue_held_gbp": money(g["held"]),
                "revenue_at_stake_gbp": money(g["at_stake"]),
                "share_of_revenue_held": ratio(g["at_stake"], g["held"]),
                "runs": g["runs"],
            }
        )
    return out


def milestone(parties: Sequence[Mapping[str, Any]], *, bar: Decimal = MILESTONE_BAR) -> list[dict]:
    """Parties whose exposure clears the declared bar: at-stake share of
    response income ≥ `bar`, and the periods at risk not all in one run
    shorter than a settlement day."""
    cleared = []
    for p in parties:
        share = p["share_of_revenue_held"]
        runs = list(p["runs"])
        single_outage = len(runs) == 1 and runs[0] < SINGLE_RUN_PERIODS
        if share is not None and Decimal(share) >= bar and runs and not single_outage:
            cleared.append({"party": p["party"], "share_of_revenue_held": share, "runs": runs})
    return cleared
