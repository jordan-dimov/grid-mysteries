"""Investigation 013 — the cover price tracker: batches, rows, reconciliation,
record flags and the three propositions.

Pure logic over pinned records; no I/O. The declaration in
`investigations/013-the-cover-price-tracker/DECLARATION.md` governs. The
tracker inherits 012's ledgers (`record_day`) and adds what a standing
instrument needs:

- **Batches**: settlement dates from 2026-09-09 in seven-day batches, each
  fetchable once three full calendar days have passed since its last date.
- **Rows, not selection**: every day in a batch gets a row. A day is
  flagged `record` when its gross paid-out exceeds every earlier row's,
  seed rows included; seed rows are never flagged.
- **Volume gate** (012's instrument lesson, declared here): accepted MWh
  come from the DISPTAV `dataType` whose day totals reconcile with the
  system-prices acceptance totals within 0.1 % in both directions. If no
  type reconciles, volume columns stay blank and no price is computed.
- **Propositions** T1–T3 with a dated falsifier; `None` verdicts when no
  instance exists, never a pass.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from grid_mysteries.investigations import record_day as rd

ZERO = rd.ZERO
PENNY = rd.PENNY
DIRECTIONS = rd.DIRECTIONS

#: Window and cadence (DECLARATION.md, *Window*).
TRACKER_START = date(2026, 9, 9)
BATCH_DAYS = 7
#: Three full calendar days must elapse after a batch's last settlement
#: date before it may be fetched: last + 1, +2, +3 elapse, fetch on +4.
FETCH_LAG_DAYS = 4
SEED_DATES = tuple((date(2026, 9, 1) + timedelta(days=i)).isoformat() for i in range(8))

#: DISPTAV data types as Elexon publishes them; the endpoint description
#: states no semantics for any of them, so the reconciling one is chosen
#: per day by test (DECLARATION.md, *Volume gate*).
DATA_TYPES = ("Original", "Original-Priced", "Re-priced", "Tagged")
RECONCILE_TOLERANCE = Decimal("0.001")

#: Declared thresholds (DECLARATION.md, *Propositions*).
T1_BSAD_SHARE_MIN = Decimal("0.05")
T3_PREMIUM_MIN_GBP_PER_MWH = Decimal("50")
FALSIFIER_DATE = date(2027, 3, 31)
MID_PROVIDER = rd.MID_PROVIDER


# ------------------------------------------------------------------- batches


def batch_dates(index: int) -> list[str]:
    """ISO settlement dates of batch `index` (1-based) from TRACKER_START."""
    if index < 1:
        raise ValueError("batch index is 1-based")
    start = TRACKER_START + timedelta(days=BATCH_DAYS * (index - 1))
    return [(start + timedelta(days=i)).isoformat() for i in range(BATCH_DAYS)]


def batch_index(day: str) -> int:
    """The batch a settlement date belongs to; seed dates raise."""
    offset = (date.fromisoformat(day) - TRACKER_START).days
    if offset < 0:
        raise ValueError(f"{day} precedes the tracker window")
    return offset // BATCH_DAYS + 1


def earliest_fetch_date(index: int) -> date:
    return date.fromisoformat(batch_dates(index)[-1]) + timedelta(days=FETCH_LAG_DAYS)


def eligible_batches(run_date: date) -> list[int]:
    """Batches whose earliest fetch date is on or before `run_date`."""
    out: list[int] = []
    index = 1
    while earliest_fetch_date(index) <= run_date:
        out.append(index)
        index += 1
    return out


# ------------------------------------------------------------ volume gate


def volumes_by_type(records: list[dict]) -> dict[str, dict[str, Decimal]]:
    """dataType -> unit -> summed |pairVolumes| from one period's DISPTAV rows."""
    out: dict[str, dict[str, Decimal]] = {t: defaultdict(lambda: ZERO) for t in DATA_TYPES}
    for record in records:
        kind = record.get("dataType")
        if kind not in out:
            continue
        pairs = record.get("pairVolumes") or {}
        total = sum(
            (abs(v) for v in (rd._decimal(x) for x in pairs.values()) if v is not None), ZERO
        )
        if total:
            out[kind][str(record["bmUnit"])] += total
    return {t: dict(units) for t, units in out.items()}


def settlement_totals(system_price_rows: list[dict]) -> dict[str, Decimal]:
    """Day totals of accepted offer and bid MWh from the system-prices
    dataset, as absolute values (bid volumes are published negative)."""
    totals = {"offer": ZERO, "bid": ZERO}
    for row in system_price_rows:
        offer = rd._decimal(row.get("totalAcceptedOfferVolume"))
        bid = rd._decimal(row.get("totalAcceptedBidVolume"))
        if offer is not None:
            totals["offer"] += abs(offer)
        if bid is not None:
            totals["bid"] += abs(bid)
    return totals


def deviation(observed: Decimal, reference: Decimal) -> Decimal | None:
    """|observed − reference| / reference; None when the reference is zero."""
    if reference == ZERO:
        return None
    return abs(observed - reference) / reference


def reconcile(
    type_totals: dict[str, dict[str, Decimal]],
    settlement: dict[str, Decimal],
    tolerance: Decimal = RECONCILE_TOLERANCE,
) -> dict[str, Any]:
    """Choose the DISPTAV type whose day totals reconcile with the settlement
    totals in **both** directions within `tolerance`.

    Several reconciling types resolve to the smallest worst-direction
    deviation, then declared order. A zero settlement total reconciles only
    with a zero type total. `chosen` is None when nothing reconciles.
    """
    by_type: dict[str, Any] = {}
    candidates: list[tuple[Decimal, int, str]] = []
    for position, kind in enumerate(DATA_TYPES):
        totals = type_totals.get(kind, {})
        entry: dict[str, Any] = {}
        worst = ZERO
        ok = True
        for direction in DIRECTIONS:
            observed = totals.get(direction, ZERO)
            reference = settlement.get(direction, ZERO)
            dev = deviation(observed, reference)
            entry[f"{direction}_mwh"] = str(observed)
            entry[f"{direction}_deviation"] = (
                None if dev is None else str(dev.quantize(Decimal("0.000001")))
            )
            if dev is None:
                ok = ok and observed == ZERO
            else:
                ok = ok and dev <= tolerance
                worst = max(worst, dev)
        entry["reconciles"] = ok
        by_type[kind] = entry
        if ok:
            candidates.append((worst, position, kind))
    chosen = min(candidates)[2] if candidates else None
    return {
        "tolerance": str(tolerance),
        "settlement_mwh": {d: str(v) for d, v in settlement.items()},
        "by_type": by_type,
        "chosen": chosen,
    }


@dataclass(slots=True)
class VolumePairing:
    """Per data type: day totals by direction, and the gas-offer / wind-bid
    pairings of EBOCF pounds with DISPTAV MWh by period (units with volume
    only, as in 012)."""

    totals: dict[str, dict[str, Decimal]] = field(
        default_factory=lambda: {t: {d: ZERO for d in DIRECTIONS} for t in DATA_TYPES}
    )
    gas_offer_mwh: dict[str, dict[int, Decimal]] = field(
        default_factory=lambda: {t: defaultdict(lambda: ZERO) for t in DATA_TYPES}
    )
    gas_offer_gbp: dict[str, dict[int, Decimal]] = field(
        default_factory=lambda: {t: defaultdict(lambda: ZERO) for t in DATA_TYPES}
    )
    wind_bid_mwh: dict[str, Decimal] = field(
        default_factory=lambda: dict.fromkeys(DATA_TYPES, ZERO)
    )
    wind_bid_gbp: dict[str, Decimal] = field(
        default_factory=lambda: dict.fromkeys(DATA_TYPES, ZERO)
    )

    def add_period(
        self,
        period: int,
        direction: str,
        records: list[dict],
        cash: dict[tuple[str, int, str], Decimal],
        fuel_of: dict[str, str],
    ) -> None:
        for kind, per_unit in volumes_by_type(records).items():
            for unit, mwh in per_unit.items():
                self.totals[kind][direction] += mwh
                cls = rd.fuel_class(fuel_of.get(unit))
                paid = cash.get((unit, period, direction), ZERO)
                if cls == "gas" and direction == "offer":
                    self.gas_offer_mwh[kind][period] += mwh
                    self.gas_offer_gbp[kind][period] += paid
                elif cls == "wind" and direction == "bid":
                    self.wind_bid_mwh[kind] += mwh
                    self.wind_bid_gbp[kind] += paid


def cash_index(rows: list[rd.Cashflow]) -> dict[tuple[str, int, str], Decimal]:
    cash: dict[tuple[str, int, str], Decimal] = defaultdict(lambda: ZERO)
    for row in rows:
        cash[(row.unit, row.period, row.direction)] += row.gbp
    return dict(cash)


def volume_columns(
    pairing: VolumePairing, chosen: str | None, mid_by_period: dict[int, Decimal]
) -> dict[str, Any]:
    """The volume-bearing columns under the chosen type; all blank when
    nothing reconciles (the price is then *not computed*, not zero)."""
    blank: dict[str, Any] = {
        "gas_offer_mwh": None,
        "gas_offer_vwap_gbp_per_mwh": None,
        "mid_vwap_same_periods_gbp_per_mwh": None,
        "premium_gbp_per_mwh": None,
        "periods_without_mid": None,
        "gas_offer_paired_gbp": None,
        "wind_bid_mwh": None,
        "wind_bid_paired_gbp": None,
        "wind_bid_vwap_gbp_per_mwh": None,
    }
    if chosen is None:
        return blank
    price = rd.gas_offer_price(
        dict(pairing.gas_offer_gbp[chosen]), dict(pairing.gas_offer_mwh[chosen]), mid_by_period
    )
    wind_mwh = pairing.wind_bid_mwh[chosen]
    wind_gbp = pairing.wind_bid_gbp[chosen]
    wind_vwap = rd.vwap(wind_gbp, wind_mwh)
    return {
        "gas_offer_mwh": price["gas_offer_mwh"],
        "gas_offer_vwap_gbp_per_mwh": price["gas_offer_vwap_gbp_per_mwh"],
        "mid_vwap_same_periods_gbp_per_mwh": price["mid_vwap_same_periods_gbp_per_mwh"],
        "premium_gbp_per_mwh": price["premium_gbp_per_mwh"],
        "periods_without_mid": price["periods_without_mid"],
        "gas_offer_paired_gbp": price["gas_offer_gbp"],
        "wind_bid_mwh": str(wind_mwh),
        "wind_bid_paired_gbp": str(wind_gbp),
        "wind_bid_vwap_gbp_per_mwh": None if wind_vwap is None else str(wind_vwap),
    }


# ---------------------------------------------------------------------- rows


def money_columns(led: rd.DayLedger) -> dict[str, Any]:
    """The L2 columns from a day ledger: gross out, net, the two cuts, the
    residual, shares, and the sign check by rows and by pounds (012
    Amendment 2)."""
    wind_bid = led.paid_out_by_class["wind"]["bid"]
    gas_offer = led.paid_out_by_class["gas"]["offer"]
    other = led.paid_out - wind_bid - gas_offer
    signed = led.by_class["wind"]["bid"]
    sign_ok = led.wind_bid_positive_rows > led.wind_bid_negative_rows and signed > ZERO
    # Inverted reading, reported when the convention fails (F2): money on
    # negative wind-unit bid rows as a share of money paid in.
    negative_wind_bid = wind_bid - signed
    return {
        "available": led.available,
        "periods_with_rows": led.periods_with_rows,
        "units": led.units,
        "paid_out_gbp": str(led.paid_out),
        "net_gbp": str(led.total),
        "paid_in_gbp": str(led.paid_in),
        "wind_bid_gbp": str(wind_bid),
        "wind_bid_share": rd.shown(rd.share(wind_bid, led.paid_out)),
        "gas_offer_gbp": str(gas_offer),
        "gas_offer_share": rd.shown(rd.share(gas_offer, led.paid_out)),
        "other_gbp": str(other),
        "other_share": rd.shown(rd.share(other, led.paid_out)),
        "two_cut_gbp": str(wind_bid + gas_offer),
        "sign_convention_holds": sign_ok,
        "wind_bid_rows": {
            "positive": led.wind_bid_positive_rows,
            "negative": led.wind_bid_negative_rows,
        },
        "wind_bid_signed_gbp": str(signed),
        "wind_bid_inverted_gbp": str(negative_wind_bid),
        "wind_bid_inverted_share_of_paid_in": rd.shown(
            rd.share(negative_wind_bid, abs(led.paid_in))
        ),
    }


def bsad_columns(summary: dict[str, Any] | None, paid_out: Decimal) -> dict[str, Any]:
    """L3 columns; an unpopulated (all-zero) or absent day is blank, never zero
    (012 Amendment 1)."""
    if summary is None or not summary.get("available"):
        return {
            "bsad_available": False,
            "bsad_placeholder_only": bool(summary and summary.get("placeholder_only")),
            "bsad_rows": None if summary is None else summary.get("rows"),
            "bsad_net_gbp": None,
            "bsad_share": None,
        }
    net = Decimal(summary["net_cost_gbp"])
    return {
        "bsad_available": True,
        "bsad_placeholder_only": False,
        "bsad_rows": summary["rows"],
        "bsad_net_gbp": str(net),
        "bsad_share": rd.shown(rd.share(net, paid_out)),
    }


def outcome_columns(
    constraints_gbp: Decimal | None,
    constraint_offers_mwh: Decimal | None,
    constraint_bids_mwh: Decimal | None,
    vintage: str,
    two_cut_gbp: Decimal,
    paid_out_gbp: Decimal,
) -> dict[str, Any] | None:
    """NESO's L1/L4 for the day once its files reach it, appended with the
    vintage date; None while absent. The ratio is L1 over the two cuts."""
    if constraints_gbp is None and constraint_offers_mwh is None and constraint_bids_mwh is None:
        return None
    ratio = None if constraints_gbp is None else rd.share(constraints_gbp, two_cut_gbp)
    ratio_out = None if constraints_gbp is None else rd.share(constraints_gbp, paid_out_gbp)
    return {
        "vintage": vintage,
        "l1_constraints_gbp": None if constraints_gbp is None else str(constraints_gbp),
        "l4_constraint_offers_mwh": None
        if constraint_offers_mwh is None
        else str(constraint_offers_mwh),
        "l4_constraint_bids_mwh": None if constraint_bids_mwh is None else str(constraint_bids_mwh),
        "ratio_l1_to_two_cut": rd.shown(ratio),
        "ratio_l1_to_paid_out": rd.shown(ratio_out),
    }


def flag_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Set `record` on every row: True when a non-seed, available day's gross
    paid-out exceeds every earlier row's (seeds included). Rows are returned
    sorted by date; the flag is recomputed from scratch each time so it
    depends only on the rows, never on when they were appended."""
    ordered = sorted(rows, key=lambda r: r["settlement_date"])
    running: Decimal | None = None
    for row in ordered:
        available = row.get("available", False)
        paid_out = Decimal(row["paid_out_gbp"]) if available else None
        row["record"] = bool(
            not row.get("seed") and paid_out is not None and (running is None or paid_out > running)
        )
        row["prior_max_paid_out_gbp"] = None if running is None else str(running)
        if paid_out is not None and (running is None or paid_out > running):
            running = paid_out
    return ordered


# -------------------------------------------------------------- propositions


def _instance(row: dict[str, Any], value: str | None, holds: bool | None) -> dict[str, Any]:
    return {
        "settlement_date": row["settlement_date"],
        "seed": bool(row.get("seed")),
        "value": value,
        "holds": holds,
    }


def _verdict(instances: list[dict[str, Any]]) -> bool | None:
    decided = [i["holds"] for i in instances if i["holds"] is not None]
    if not decided:
        return None
    return all(decided)


def evaluate(rows: list[dict[str, Any]], as_of: date) -> dict[str, Any]:
    """T1–T3 over the rows as they stand. Each is decided by its instances:
    True when every instance holds, False on any counterexample, None when
    no instance exists yet. Seed rows never decide T1 or T3 (they are not
    record days) and are shown as context for T2, which is decided on
    tracked days only."""
    records = [r for r in rows if r.get("record")]
    t1 = [
        _instance(
            r,
            r.get("bsad_share"),
            None if r.get("bsad_share") is None else Decimal(r["bsad_share"]) > T1_BSAD_SHARE_MIN,
        )
        for r in records
    ]
    t3 = [
        _instance(
            r,
            r.get("premium_gbp_per_mwh"),
            None
            if r.get("premium_gbp_per_mwh") is None
            else Decimal(r["premium_gbp_per_mwh"]) > T3_PREMIUM_MIN_GBP_PER_MWH,
        )
        for r in records
    ]
    t2_all: list[dict[str, Any]] = []
    for r in rows:
        outcome = r.get("outcome") or {}
        l1 = outcome.get("l1_constraints_gbp")
        if l1 is None or not r.get("available"):
            continue
        holds = Decimal(l1) > Decimal(r["two_cut_gbp"])
        t2_all.append(_instance(r, l1, holds))
    t2_deciding = [i for i in t2_all if not i["seed"]]
    falsifier_passed = as_of >= FALSIFIER_DATE
    return {
        "as_of": as_of.isoformat(),
        "falsifier_date": FALSIFIER_DATE.isoformat(),
        "falsifier_date_reached": falsifier_passed,
        "record_days": [r["settlement_date"] for r in records],
        "T1": {
            "claim": "on record days the Disaggregated BSAD net share of paid-out exceeds 5 %",
            "threshold": str(T1_BSAD_SHARE_MIN),
            "instances": t1,
            "holds": _verdict(t1),
        },
        "T2": {
            "claim": (
                "NESO's Constraints figure, when published, exceeds the two cuts "
                "(wind-unit bids + gas-unit offers paid) for the same day"
            ),
            "instances": t2_all,
            "deciding_instances": len(t2_deciding),
            "holds": _verdict(t2_deciding),
        },
        "T3": {
            "claim": "on record days the gas-offer premium over APXMIDP exceeds £50/MWh",
            "threshold_gbp_per_mwh": str(T3_PREMIUM_MIN_GBP_PER_MWH),
            "instances": t3,
            "holds": _verdict(t3),
        },
    }


# ---------------------------------------------------------------- rendering


def _m(value: str | None) -> str:
    if value is None:
        return ""
    return f"{(Decimal(value) / Decimal(1_000_000)).quantize(PENNY):,.2f}"


def _pct(value: str | None) -> str:
    if value is None:
        return ""
    return f"{(Decimal(value) * 100).quantize(Decimal('0.1'))} %"


def _price(value: str | None) -> str:
    return "" if value is None else f"{Decimal(value):,.2f}"


TABLE_HEADER = (
    "| Day | Flag | Paid out £m | Net £m | Wind bids £m (share) | Gas offers £m (share) "
    "| Other £m (share) | Gas offer £/MWh | Premium £/MWh | DISPTAV type | BSAD net £m (share) "
    "| Sign | NESO Constraints £m (vintage) | L1 ÷ two cuts |\n"
    "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|"
)


#: Display-only cautions (sponsor, 2026-09-19); they never change a value in
#: tracker.json or a verdict. Wind bids are marked ‡ on any row whose sign
#: check fails. BSAD is marked § on days that are populated under the declared
#: rule but look unfinished; the set is named, not inferred, so no later day
#: is marked by a rule nobody declared.
WIND_AMBIGUOUS = "‡"
BSAD_PROVISIONAL = "§"
PROVISIONAL_BSAD_DAYS = frozenset({"2026-09-12", "2026-09-13"})
BSAD_PROVISIONAL_CAUTION = (
    "The declared rule treats a day with rows as populated, so this is a caution, "
    "not a reclassification."
)


def wind_ambiguous(row: dict[str, Any]) -> bool:
    return row.get("available", False) and row.get("sign_convention_holds") is False


def bsad_provisional(row: dict[str, Any]) -> bool:
    return (
        row.get("settlement_date") in PROVISIONAL_BSAD_DAYS and row.get("bsad_net_gbp") is not None
    )


def render_row(row: dict[str, Any]) -> str:
    flag = "seed (012)" if row.get("seed") else ("**record**" if row.get("record") else "")
    if not row.get("available"):
        return f"| {row['settlement_date']} | {flag or 'unavailable'} | | | | | | | | | | | | |"
    kind = row.get("disptav_type") or ("none reconciles" if row.get("reconciliation") else "")
    if row.get("seed") and kind:
        kind = f"{kind} †"
    outcome = row.get("outcome") or {}
    l1 = outcome.get("l1_constraints_gbp")
    l1_cell = f"{_m(l1)} ({outcome['vintage']})" if l1 is not None else ""
    sign = (
        ""
        if row.get("sign_convention_holds") is None
        else ("holds" if row["sign_convention_holds"] else "**fails**")
    )
    bsad = (
        f"{_m(row['bsad_net_gbp'])} ({_pct(row['bsad_share'])})"
        if row.get("bsad_net_gbp") is not None
        else ("unpopulated" if row.get("bsad_placeholder_only") else "")
    )
    if bsad_provisional(row):
        bsad += f" {BSAD_PROVISIONAL}"
    wind_mark = f" {WIND_AMBIGUOUS}" if wind_ambiguous(row) else ""
    return (
        f"| {row['settlement_date']} | {flag} | {_m(row['paid_out_gbp'])} | {_m(row['net_gbp'])} "
        f"| {_m(row['wind_bid_gbp'])} ({_pct(row['wind_bid_share'])}){wind_mark} "
        f"| {_m(row['gas_offer_gbp'])} ({_pct(row['gas_offer_share'])}) "
        f"| {_m(row['other_gbp'])} ({_pct(row['other_share'])}) "
        f"| {_price(row.get('gas_offer_vwap_gbp_per_mwh'))} "
        f"| {_price(row.get('premium_gbp_per_mwh'))} | {kind} | {bsad} | {sign} "
        f"| {l1_cell} | {_pct(outcome.get('ratio_l1_to_two_cut'))} |"
    )


def render_table(rows: list[dict[str, Any]]) -> str:
    notes = []
    if any(wind_ambiguous(r) for r in rows):
        notes.append(
            f"{WIND_AMBIGUOUS} The sign check on wind-unit bids failed on the marked days, so "
            "the wind-bids figure on those days is ambiguous; each row in "
            "`evidence/tracker.json` carries both readings."
        )
    if any(bsad_provisional(r) for r in rows):
        notes.append(
            f"{BSAD_PROVISIONAL} BSAD provisional: NESO may not have finished filling the "
            f"marked days. {BSAD_PROVISIONAL_CAUTION}"
        )
    table = "\n".join([TABLE_HEADER, *(render_row(r) for r in rows)])
    return table + "".join(f"\n\n{n}" for n in notes)
