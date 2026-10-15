"""024 — The gas in the spread: the day rule, the spread, Jomaux's three
legs, and the two ratio definitions, on Decimals.

The method is Julien Jomaux's for Germany (GEM Energy Analytics, "The
evolution of the spread: 2026 update", 24/09/2026), carried to Great
Britain with attribution: the daily spread is the highest hourly day-ahead
price minus the lowest (his TB1); the spread divided by the gas price says
how much of it is gas; and each hour's price is split at zero and at a
CCGT cost proxy of twice the gas price plus 0.4 times the carbon price into
a negative, a merit-order and a scarcity part, so that each day's spread is
the sum of three legs. Pure functions; no I/O.
"""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from zoneinfo import ZoneInfo

#: A day is measured when it prints between 23 and 25 prices (a clock-change
#: day has 23 or 25 hours); fewer or more is excluded and counted.
MIN_PRICES, MAX_PRICES = 23, 25
#: Carbon Price Support, GBP per tonne, added to the UK allowance price.
CARBON_PRICE_SUPPORT = Decimal(18)
#: Jomaux's CCGT cost proxy: 2 × gas (a 50 % efficiency) + 0.4 × carbon
#: (0.4 t CO2 per MWh of electricity). His, not calibrated here.
GAS_MULTIPLE = Decimal(2)
CARBON_INTENSITY = Decimal("0.4")
LONDON = ZoneInfo("Europe/London")
ZERO = Decimal(0)
PLACES = Decimal("0.000001")


def local_day(day: date, start_hour: int, tz: ZoneInfo = LONDON) -> date:
    """The local calendar day of an hour printed as a UTC date and start hour."""
    return datetime(day.year, day.month, day.day, start_hour, tzinfo=UTC).astimezone(tz).date()


def day_spread(prices: Sequence[Decimal]) -> Decimal | None:
    """Highest minus lowest price of the day, or None when the day is not measured."""
    if not MIN_PRICES <= len(prices) <= MAX_PRICES:
        return None
    return max(prices) - min(prices)


def ccgt_cost(gas_gbp_per_mwh: Decimal, carbon_gbp_per_t: Decimal) -> Decimal:
    return GAS_MULTIPLE * gas_gbp_per_mwh + CARBON_INTENSITY * carbon_gbp_per_t


@dataclass(frozen=True)
class Legs:
    negative: Decimal
    merit_order: Decimal
    scarcity: Decimal

    @property
    def total(self) -> Decimal:
        return self.negative + self.merit_order + self.scarcity


def _parts(price: Decimal, cost: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """The price split at zero and at the CCGT cost; the parts sum to the price."""
    negative = min(price, ZERO)
    merit = min(max(price, ZERO), cost)
    scarcity = max(price - cost, ZERO)
    return negative, merit, scarcity


def legs(prices: Sequence[Decimal], cost: Decimal) -> Legs:
    """Jomaux's three legs of the day's spread. Each part of the price is a
    non-decreasing function of the price, so the day's highest price has the
    highest value of every part and the lowest the lowest; the legs are the
    differences, each non-negative, and they sum exactly to the spread."""
    hi, lo = _parts(max(prices), cost), _parts(min(prices), cost)
    return Legs(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])


def mean(values: Iterable[Decimal]) -> Decimal | None:
    xs = list(values)
    return sum(xs, ZERO) / len(xs) if xs else None


def ratio_of_means(spreads: Sequence[Decimal], gases: Sequence[Decimal]) -> Decimal | None:
    """Ratio A: the period's mean spread over its mean gas price (the lead)."""
    s, g = mean(spreads), mean(gases)
    return s / g if s is not None and g else None


def mean_of_ratios(pairs: Iterable[tuple[Decimal, Decimal]]) -> Decimal | None:
    """Ratio B: the mean of the daily spread-over-gas ratios."""
    return mean(s / g for s, g in pairs if g)


def quantise(x: Decimal | None, places: Decimal = PLACES) -> Decimal | None:
    return None if x is None else x.quantize(places, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class DayRow:
    """One measured or excluded day: its prices' count, spread, gas, carbon
    and legs (None where an input is missing or the day is not measured)."""

    day: date
    prices: int
    spread: Decimal | None
    gas: Decimal | None
    carbon: Decimal | None
    ccgt: Decimal | None
    negative: Decimal | None
    merit_order: Decimal | None
    scarcity: Decimal | None


def build_rows(
    days: Mapping[date, Sequence[Decimal]],
    gas: Mapping[date, Decimal],
    monthly_allowance: Mapping[tuple[int, int], Decimal],
) -> list[DayRow]:
    rows = []
    for day in sorted(days):
        prices = days[day]
        spread = day_spread(prices)
        g = gas.get(day)
        uka = monthly_allowance.get((day.year, day.month))
        carbon = uka + CARBON_PRICE_SUPPORT if uka is not None else None
        cost = ccgt_cost(g, carbon) if g is not None and carbon is not None else None
        lg = legs(prices, cost) if spread is not None and cost is not None else None
        rows.append(
            DayRow(
                day,
                len(prices),
                spread,
                g,
                carbon,
                cost,
                lg.negative if lg else None,
                lg.merit_order if lg else None,
                lg.scarcity if lg else None,
            )
        )
    return rows


def _month_end(year: int, month: int) -> date:
    return date(year + (month == 12), month % 12 + 1, 1).fromordinal(
        date(year + (month == 12), month % 12 + 1, 1).toordinal() - 1
    )


def periods(fetch_date: date, last_month: tuple[int, int]) -> list[tuple[str, date, date]]:
    """(label, first day, last day): calendar years 2022 to 2025, 2026 to the
    fetch date, the same dates in 2025, and every calendar month from
    January 2022 to `last_month`."""
    out = [(str(y), date(y, 1, 1), date(y, 12, 31)) for y in range(2022, 2026)]
    out.append(("2026 to date", date(2026, 1, 1), fetch_date))
    out.append(("2025 same dates", date(2025, 1, 1), fetch_date.replace(year=2025)))
    y, m = 2022, 1
    while (y, m) <= last_month:
        out.append((f"{y}-{m:02d}", date(y, m, 1), _month_end(y, m)))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def summarise(rows: Sequence[DayRow], first: date, last: date) -> dict:
    """The period's counts, means, both ratios, the legs and their shares."""
    inside = [r for r in rows if first <= r.day <= last]
    measured = [r for r in inside if r.spread is not None]
    with_gas = [r for r in inside if r.gas is not None]
    both = [r for r in measured if r.gas is not None]
    with_legs = [r for r in both if r.negative is not None]
    spread_mean = mean(r.spread for r in measured if r.spread is not None)
    spreads_both = [r.spread for r in both if r.spread is not None]
    gases_both = [r.gas for r in both if r.gas is not None]
    leg_means = {
        name: mean(getattr(r, name) for r in with_legs)
        for name in ("negative", "merit_order", "scarcity")
    }
    spread_mean_legs = mean(r.spread for r in with_legs if r.spread is not None)
    return {
        "first": first,
        "last": last,
        "calendar_days": (last - first).days + 1,
        "days_printed": len(inside),
        "days_measured": len(measured),
        "days_excluded_by_price_count": len(inside) - len(measured),
        "spread_mean": quantise(spread_mean),
        "days_with_gas": len(with_gas),
        "gas_mean": quantise(mean(r.gas for r in with_gas if r.gas is not None)),
        "days_with_both": len(both),
        "spread_mean_both": quantise(mean(spreads_both)),
        "gas_mean_both": quantise(mean(gases_both)),
        "ratio_of_means": quantise(ratio_of_means(spreads_both, gases_both)),
        "mean_of_ratios": quantise(mean_of_ratios(zip(spreads_both, gases_both, strict=True))),
        "days_with_legs": len(with_legs),
        "spread_mean_legs": quantise(spread_mean_legs),
        "legs_mean": {k: quantise(v) for k, v in leg_means.items()},
        "legs_share": {
            k: quantise(v / spread_mean_legs) if v is not None and spread_mean_legs else None
            for k, v in leg_means.items()
        },
    }


def f1_fires(ratio_2026: Decimal | None, ratio_2025: Decimal | None) -> bool | None:
    """F1: the 2026-to-date ratio is not below 2025's same dates by more than 5 %."""
    if ratio_2026 is None or ratio_2025 is None:
        return None
    return ratio_2026 >= ratio_2025 * Decimal("0.95")


def f2_fires(
    september_2026_spread: Decimal | None,
    published: Decimal = Decimal(122),
    tolerance: Decimal = Decimal(2),
) -> bool | None:
    """F2: the September 2026 spread does not reproduce Modo's GBP 122 within GBP 2."""
    if september_2026_spread is None:
        return None
    return abs(september_2026_spread - published) > tolerance


# ---- Amendment 2: the forward record -------------------------------------

#: The yearly ratio A values that bound the band, as the amendment names them.
BAND_PERIODS = ("2023", "2024", "2025", "2026 to date")
CENTRAL_PERIOD = "2026 to date"


@dataclass(frozen=True)
class Band:
    low: Decimal
    high: Decimal
    central: Decimal
    low_period: str
    high_period: str


def ratio_band(results: Mapping) -> Band:
    """Low, high and central ratio A from 024's results.json (printed unit),
    never typed: the min and max of the four yearly means, and 2026 to date."""
    periods = results["units"]["printed"]["periods"]
    values = {p: Decimal(str(periods[p]["ratio_of_means"])) for p in BAND_PERIODS}
    low_period = min(values, key=lambda p: values[p])
    high_period = max(values, key=lambda p: values[p])
    return Band(
        values[low_period], values[high_period], values[CENTRAL_PERIOD], low_period, high_period
    )


def implied_spread(gas_gbp_per_mwh: Decimal, band: Band) -> dict[str, Decimal]:
    """The forward gas price times each band edge and the central case."""
    return {
        "low": gas_gbp_per_mwh * band.low,
        "central": gas_gbp_per_mwh * band.central,
        "high": gas_gbp_per_mwh * band.high,
    }


def season_mean(values: Sequence[Decimal]) -> Decimal:
    """A season's forward gas as the simple mean of its printed contracts."""
    return sum(values, ZERO) / len(values)
