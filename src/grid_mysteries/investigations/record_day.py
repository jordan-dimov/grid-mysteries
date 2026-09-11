"""Investigation 012 — the record day: ledgers, selection and propositions.

Pure logic over pinned records; no I/O. The declaration in
`investigations/012-the-record-day/DECLARATION.md` governs:

- **R1** selects the window day with the highest total published
  indicative BM cashflow (EBOCF `totalCashflow`, both directions, all
  periods); ties by earlier date. Days without rows are unavailable and
  never selected.
- **Sign**: a positive `totalCashflow` is money to the unit, negative is
  money from the unit. Checked on wind-unit bids, never assumed.
- **Classes**: wind = `WIND`; gas = `CCGT`/`OCGT`; everything else,
  including units with no fuel type, is `other`. Nothing is guessed.
- **Thresholds** (P1–P3) are the declared ones; changing them here
  without an amendment would be a protocol breach.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

ZERO = Decimal(0)
PENNY = Decimal("0.01")
CLASSES = ("wind", "gas", "other")
DIRECTIONS = ("offer", "bid")

#: Declared thresholds (DECLARATION.md, *Propositions*).
P1_WIND_BID_SHARE_MAX = Decimal("0.25")
P1_GAS_OFFER_SHARE_MIN = Decimal("0.50")
P2_BSAD_SHARE_MIN = Decimal("0.05")
P3_REFERENCE_GBP_PER_MWH = Decimal("231")
P3_TOLERANCE = Decimal("0.15")
MID_PROVIDER = "APXMIDP"


def _decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def fuel_class(fuel_type: str | None) -> str:
    """Register `fuelType` -> declared class. Unknown and missing are `other`."""
    code = (fuel_type or "").strip().upper()
    if code == "WIND":
        return "wind"
    if code in {"CCGT", "OCGT"}:
        return "gas"
    return "other"


@dataclass(frozen=True, slots=True)
class Cashflow:
    period: int
    unit: str
    direction: str
    gbp: Decimal


def cashflow_rows(records: list[dict], direction: str) -> list[Cashflow]:
    """EBOCF records for one direction -> rows with a published total.

    Records without a `totalCashflow` are skipped (absent, not zero), as in 004.
    """
    rows: list[Cashflow] = []
    for record in records:
        total = _decimal(record.get("totalCashflow"))
        if total is None:
            continue
        period = record.get("settlementPeriod")
        unit = record.get("bmUnit")
        if period is None or unit is None:
            continue
        rows.append(Cashflow(int(period), str(unit), direction, total))
    return rows


def _class_grid() -> dict[str, dict[str, Decimal]]:
    return {cls: {direction: ZERO for direction in DIRECTIONS} for cls in CLASSES}


@dataclass(slots=True)
class DayLedger:
    settlement_date: str
    available: bool
    periods_with_rows: int
    units: int
    total: Decimal
    paid_out: Decimal
    paid_in: Decimal
    by_class: dict[str, dict[str, Decimal]] = field(default_factory=_class_grid)
    #: Positive-only money by class and direction (money to units).
    paid_out_by_class: dict[str, dict[str, Decimal]] = field(default_factory=_class_grid)
    wind_bid_positive_rows: int = 0
    wind_bid_negative_rows: int = 0

    def as_json(self) -> dict:
        return {
            "settlement_date": self.settlement_date,
            "available": self.available,
            "periods_with_rows": self.periods_with_rows,
            "units": self.units,
            "total_gbp": str(self.total),
            "paid_out_gbp": str(self.paid_out),
            "paid_in_gbp": str(self.paid_in),
            "by_class_gbp": {
                c: {d: str(v) for d, v in g.items()} for c, g in self.by_class.items()
            },
            "paid_out_by_class_gbp": {
                c: {d: str(v) for d, v in g.items()} for c, g in self.paid_out_by_class.items()
            },
            "wind_bid_rows": {
                "positive": self.wind_bid_positive_rows,
                "negative": self.wind_bid_negative_rows,
            },
        }


def ledger(day: str, rows: list[Cashflow], fuel_of: dict[str, str]) -> DayLedger:
    """One day's L2 ledger from its EBOCF rows and the register's fuel map."""
    result = DayLedger(day, bool(rows), 0, 0, ZERO, ZERO, ZERO)
    periods: set[int] = set()
    units: set[str] = set()
    for row in rows:
        cls = fuel_class(fuel_of.get(row.unit))
        periods.add(row.period)
        units.add(row.unit)
        result.total += row.gbp
        result.by_class[cls][row.direction] += row.gbp
        if row.gbp > ZERO:
            result.paid_out += row.gbp
            result.paid_out_by_class[cls][row.direction] += row.gbp
        elif row.gbp < ZERO:
            result.paid_in += row.gbp
        if cls == "wind" and row.direction == "bid":
            if row.gbp > ZERO:
                result.wind_bid_positive_rows += 1
            elif row.gbp < ZERO:
                result.wind_bid_negative_rows += 1
    result.periods_with_rows = len(periods)
    result.units = len(units)
    return result


def select_day(ledgers: dict[str, DayLedger]) -> tuple[str | None, str | None]:
    """R1: (selected, runner-up) by highest `total`; ties by earlier date;
    unavailable days excluded."""
    ranked = sorted(
        (led for led in ledgers.values() if led.available),
        key=lambda led: (-led.total, led.settlement_date),
    )
    selected = ranked[0].settlement_date if ranked else None
    runner_up = ranked[1].settlement_date if len(ranked) > 1 else None
    return selected, runner_up


def share(part: Decimal, whole: Decimal) -> Decimal | None:
    """Exact ratio (verdicts compare this); `shown` rounds it for the report."""
    if whole == ZERO:
        return None
    return part / whole


def shown(ratio: Decimal | None) -> str | None:
    return None if ratio is None else str(ratio.quantize(Decimal("0.0001")))


def accepted_mwh(records: list[dict]) -> dict[str, Decimal]:
    """Per-unit accepted MWh from one period's DISPTAV `Original` rows."""
    volumes: dict[str, Decimal] = defaultdict(lambda: ZERO)
    for record in records:
        if record.get("dataType") != "Original":
            continue
        pairs = record.get("pairVolumes") or {}
        total = sum((abs(v) for v in (_decimal(x) for x in pairs.values()) if v is not None), ZERO)
        if total:
            volumes[str(record["bmUnit"])] += total
    return dict(volumes)


def vwap(gbp: Decimal, mwh: Decimal) -> Decimal | None:
    if mwh == ZERO:
        return None
    return (gbp / mwh).quantize(PENNY)


def mid_prices(records: list[dict], provider: str = MID_PROVIDER) -> dict[int, Decimal]:
    """Settlement period -> volume-weighted MID price for one provider."""
    cash: dict[int, Decimal] = defaultdict(lambda: ZERO)
    volume: dict[int, Decimal] = defaultdict(lambda: ZERO)
    for record in records:
        if record.get("dataProvider") != provider:
            continue
        price = _decimal(record.get("price"))
        vol = _decimal(record.get("volume"))
        period = record.get("settlementPeriod")
        if price is None or vol is None or period is None or vol <= ZERO:
            continue
        cash[int(period)] += price * vol
        volume[int(period)] += vol
    return {p: (cash[p] / volume[p]).quantize(PENNY) for p in cash if volume[p] > ZERO}


def gas_offer_price(
    gas_offer_gbp_by_period: dict[int, Decimal],
    gas_offer_mwh_by_period: dict[int, Decimal],
    mid_by_period: dict[int, Decimal],
) -> dict:
    """P3 inputs: gas-offer VWAP, the MID price weighted by the same gas MWh
    in the same periods, and the premium. Periods lacking a MID price are
    excluded from the premium (counted), never filled."""
    gbp = sum(gas_offer_gbp_by_period.values(), ZERO)
    mwh = sum(gas_offer_mwh_by_period.values(), ZERO)
    gas_vwap = vwap(gbp, mwh)
    mid_cash = ZERO
    mid_mwh = ZERO
    missing = 0
    for period, volume in gas_offer_mwh_by_period.items():
        if volume <= ZERO:
            continue
        price = mid_by_period.get(period)
        if price is None:
            missing += 1
            continue
        mid_cash += price * volume
        mid_mwh += volume
    mid_vwap = vwap(mid_cash, mid_mwh)
    premium = (
        (gas_vwap - mid_vwap).quantize(PENNY)
        if gas_vwap is not None and mid_vwap is not None
        else None
    )
    return {
        "gas_offer_gbp": str(gbp),
        "gas_offer_mwh": str(mwh),
        "gas_offer_vwap_gbp_per_mwh": None if gas_vwap is None else str(gas_vwap),
        "mid_vwap_same_periods_gbp_per_mwh": None if mid_vwap is None else str(mid_vwap),
        "premium_gbp_per_mwh": None if premium is None else str(premium),
        "periods_without_mid": missing,
    }


def evaluate(led: DayLedger, bsad_net_cost: Decimal | None, gas_vwap: Decimal | None) -> dict:
    """P1–P3 against the declared thresholds. `None` inputs give `None`
    verdicts, never a pass."""
    wind_bid = led.paid_out_by_class["wind"]["bid"]
    gas_offer = led.paid_out_by_class["gas"]["offer"]
    wind_share = share(wind_bid, led.paid_out)
    gas_share = share(gas_offer, led.paid_out)
    p1 = (
        None
        if wind_share is None or gas_share is None
        else wind_share < P1_WIND_BID_SHARE_MAX and gas_share > P1_GAS_OFFER_SHARE_MIN
    )
    bsad_share = None if bsad_net_cost is None else share(bsad_net_cost, led.paid_out)
    p2 = None if bsad_share is None else bsad_share >= P2_BSAD_SHARE_MIN
    p3 = None
    if gas_vwap is not None:
        band = P3_REFERENCE_GBP_PER_MWH * P3_TOLERANCE
        p3 = abs(gas_vwap - P3_REFERENCE_GBP_PER_MWH) <= band
    sign_ok = led.wind_bid_positive_rows > led.wind_bid_negative_rows
    return {
        "sign_convention_holds": sign_ok,
        "P1": {
            "wind_bid_share_of_paid_out": shown(wind_share),
            "gas_offer_share_of_paid_out": shown(gas_share),
            "thresholds": {
                "wind_bid_share_max": str(P1_WIND_BID_SHARE_MAX),
                "gas_offer_share_min": str(P1_GAS_OFFER_SHARE_MIN),
            },
            "holds": p1,
        },
        "P2": {
            "bsad_net_cost_gbp": None if bsad_net_cost is None else str(bsad_net_cost),
            "bsad_share_of_paid_out": shown(bsad_share),
            "threshold_min": str(P2_BSAD_SHARE_MIN),
            "holds": p2,
        },
        "P3": {
            "gas_offer_vwap_gbp_per_mwh": None if gas_vwap is None else str(gas_vwap),
            "reference_gbp_per_mwh": str(P3_REFERENCE_GBP_PER_MWH),
            "tolerance": str(P3_TOLERANCE),
            "holds": p3,
        },
    }
