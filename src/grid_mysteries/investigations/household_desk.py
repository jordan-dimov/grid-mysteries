"""010 — the household desk: a pure tariff-pair battery backtest.

Given two price series (import, export), a battery, and a window, compute
for every decision day the exact optimum of the day's grid-facing trades
under the household's true information set, and total the result by
month. No network, no files: sources supply `Rate` lists.

Tariff interface. A tariff is a sorted list of `Rate` intervals of any
length, each carrying `published_at` — the moment the household could
know it (None = known indefinitely). Half-hourly Agile, a fixed
time-of-use schedule, a five-minute wholesale pass-through or an
EPEX-indexed continental tariff all fit this shape; the model never
asks which it is.

Money is Decimal pence throughout; pounds appear only in reporting.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from fractions import Fraction
from typing import Any
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
ZERO = Decimal(0)
ONE = Decimal(1)
PENNY = Decimal("0.01")
RULE = "010/per-day-optimum/v2"
MIN_SCORED_DAYS_PER_MONTH = 25
RESOLUTION = timedelta(minutes=30)
DAYLIGHT = (time(9, 0), time(17, 0))


@dataclass(frozen=True, slots=True)
class Rate:
    valid_from: datetime
    valid_to: datetime | None
    pence_per_kwh: Decimal
    published_at: datetime | None = None

    def __post_init__(self) -> None:
        for moment in (self.valid_from, self.valid_to, self.published_at):
            if moment is not None and moment.tzinfo is None:
                raise ValueError("rate timestamps must be timezone-aware")
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError("rate must end after it starts")

    def covers(self, start: datetime, end: datetime) -> bool:
        return self.valid_from <= start and (self.valid_to is None or self.valid_to >= end)

    def known_at(self, moment: datetime) -> bool:
        return self.published_at is None or self.published_at <= moment


@dataclass(frozen=True, slots=True)
class BatterySpec:
    """The household's plant.

    `inverter_kw` bounds battery-side power in either direction and, per
    slot, the *time* the inverter can spend charging plus discharging
    (Amendment 1). `export_limit_kw` bounds delivered (grid-side) export;
    `import_limit_kw`, if given, bounds grid-side import.
    """

    capacity_kwh: Decimal
    inverter_kw: Decimal
    export_limit_kw: Decimal
    round_trip_efficiency: Decimal
    import_limit_kw: Decimal | None = None
    degradation_p_per_kwh: Decimal = ZERO
    free_energy_kwh_per_day: Decimal = ZERO

    def __post_init__(self) -> None:
        if not ZERO < self.round_trip_efficiency <= ONE:
            raise ValueError("round-trip efficiency must be in (0, 1]")
        for name in ("capacity_kwh", "inverter_kw", "export_limit_kw"):
            if getattr(self, name) < ZERO:
                raise ValueError(f"{name} must be non-negative")
        if self.import_limit_kw is not None and self.import_limit_kw < ZERO:
            raise ValueError("import_limit_kw must be non-negative")
        if self.degradation_p_per_kwh < ZERO or self.free_energy_kwh_per_day < ZERO:
            raise ValueError("degradation and free energy must be non-negative")

    @property
    def charge_kw(self) -> Decimal:
        """Grid-side import power: the inverter unless the connection is tighter."""
        if self.import_limit_kw is None:
            return self.inverter_kw
        return min(self.inverter_kw, self.import_limit_kw)


@dataclass(frozen=True, slots=True)
class Slot:
    start: datetime
    end: datetime
    import_p: Decimal
    export_p: Decimal

    @property
    def hours(self) -> Decimal:
        return Decimal((self.end - self.start).total_seconds()) / Decimal(3600)


@dataclass(frozen=True, slots=True)
class DecisionDay:
    """One scheduling day: prices for [start, end) must be known at `decision_at`."""

    day: date
    decision_at: datetime
    start: datetime
    end: datetime


@dataclass(frozen=True)
class DaySchedule:
    day: date
    imported_kwh: Decimal
    exported_kwh: Decimal
    free_kwh: Decimal
    import_cost_p: Decimal
    export_revenue_p: Decimal
    degradation_p: Decimal
    slot_charge_kwh: tuple[Decimal, ...] = field(repr=False)
    slot_free_kwh: tuple[Decimal, ...] = field(repr=False)
    slot_export_kwh: tuple[Decimal, ...] = field(repr=False)

    @property
    def net_p(self) -> Decimal:
        return self.export_revenue_p - self.import_cost_p - self.degradation_p


@dataclass(frozen=True)
class Totals:
    label: str
    scored_days: int
    dropped_days: int
    imported_kwh: Decimal
    exported_kwh: Decimal
    free_kwh: Decimal
    import_cost_p: Decimal
    export_revenue_p: Decimal
    degradation_p: Decimal

    @property
    def net_p(self) -> Decimal:
        return self.export_revenue_p - self.import_cost_p - self.degradation_p

    @property
    def complete(self) -> bool:
        return self.scored_days >= MIN_SCORED_DAYS_PER_MONTH

    def average_import_p(self) -> Decimal | None:
        return None if self.imported_kwh == ZERO else self.import_cost_p / self.imported_kwh

    def average_export_p(self) -> Decimal | None:
        return None if self.exported_kwh == ZERO else self.export_revenue_p / self.exported_kwh


@dataclass(frozen=True)
class BacktestResult:
    rule: str
    spec: BatterySpec
    days: tuple[DaySchedule, ...]
    dropped: tuple[tuple[date, str], ...]
    months: tuple[Totals, ...]
    window: Totals


def pounds(pence: Decimal) -> Decimal:
    return (pence / Decimal(100)).quantize(PENNY)


# --------------------------------------------------------------------------- days


def decision_days(
    window_from: date,
    window_to: date,
    *,
    tz: ZoneInfo = LONDON,
    day_start: time = time(23, 0),
    decision: time = time(16, 0),
) -> list[DecisionDay]:
    """One decision day per local calendar date in [window_from, window_to].

    A day starting at 23:00 is attributed to the following calendar date
    (it holds 23 of that date's 24 hours); a day starting at midnight to
    its own. Prices are decided at `decision` local time on the calendar
    date the day starts, which for Agile is the 16:00 publication.
    """
    days: list[DecisionDay] = []
    current = window_from
    while current <= window_to:
        start_date = current if day_start == time(0, 0) else current - timedelta(days=1)
        start = datetime.combine(start_date, day_start, tzinfo=tz)
        end = datetime.combine(start_date + timedelta(days=1), day_start, tzinfo=tz)
        decided = datetime.combine(start_date, decision, tzinfo=tz)
        if decided >= start:
            decided -= timedelta(days=1)
        days.append(
            DecisionDay(
                current, decided.astimezone(UTC), start.astimezone(UTC), end.astimezone(UTC)
            )
        )
        current += timedelta(days=1)
    return days


def _covering(rates: Sequence[Rate], start: datetime, end: datetime) -> Rate | None:
    # Rates are sorted by valid_from; the last one starting at or before
    # `start` is the only candidate.
    lo, hi = 0, len(rates)
    while lo < hi:
        mid = (lo + hi) // 2
        if rates[mid].valid_from <= start:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        return None
    candidate = rates[lo - 1]
    return candidate if candidate.covers(start, end) else None


def slots_for(
    day: DecisionDay,
    import_rates: Sequence[Rate],
    export_rates: Sequence[Rate],
    *,
    resolution: timedelta = RESOLUTION,
) -> tuple[list[Slot], str | None]:
    """Slots at the union of both series' boundaries and the settlement grid
    inside the day (Amendment 2), or the reason the day cannot be scored (a
    gap, or a price not yet known). A finer grid never loses value: every
    coarse schedule stays feasible, and free daylight energy lands in the
    half-hours it belongs to rather than in one multi-hour fixed-rate slot."""
    boundaries = {day.start, day.end}
    tick = day.start
    while tick < day.end:
        boundaries.add(tick)
        tick += resolution
    for rates in (import_rates, export_rates):
        for rate in rates:
            for edge in (rate.valid_from, rate.valid_to):
                if edge is not None and day.start < edge < day.end:
                    boundaries.add(edge)
    edges = sorted(boundaries)
    slots: list[Slot] = []
    for start, end in zip(edges, edges[1:], strict=False):
        imp = _covering(import_rates, start, end)
        exp = _covering(export_rates, start, end)
        if imp is None or exp is None:
            side = "import" if imp is None else "export"
            return [], f"no {side} price for {start.isoformat()}"
        for side_name, rate in (("import", imp), ("export", exp)):
            if not rate.known_at(day.decision_at):
                return [], f"{side_name} price for {start.isoformat()} not known at decision"
        slots.append(Slot(start, end, imp.pence_per_kwh, exp.pence_per_kwh))
    return slots, None


def free_energy_by_slot(
    slots: Sequence[Slot], kwh_per_day: Decimal, *, tz: ZoneInfo = LONDON
) -> list[Decimal]:
    """Free (solar) energy spread evenly over the daylight slots by duration."""
    daylight = [
        slot for slot in slots if DAYLIGHT[0] <= slot.start.astimezone(tz).time() < DAYLIGHT[1]
    ]
    hours = sum((slot.hours for slot in daylight), ZERO)
    if kwh_per_day == ZERO or hours == ZERO:
        return [ZERO] * len(slots)
    share = {id(slot): kwh_per_day * slot.hours / hours for slot in daylight}
    return [share.get(id(slot), ZERO) for slot in slots]


# --------------------------------------------------------------------- optimum
#
# The day's problem is a small linear programme: per slot choose grid
# import c, free energy f and stored energy released d (all in stored kWh)
# to maximise Σ (m·d − p·c) with m = η·(export price − degradation), subject
# to c ≤ import cap, f ≤ free cap, d ≤ export cap/η, c + f + d ≤ inverter
# budget (time shared, Amendment 1), and the stored balance staying in
# [0, capacity] and ending at zero. It is solved exactly by dynamic
# programming over the stored balance: the value-to-go is concave and
# piecewise linear, and one slot's reward as a function of its net stored
# change Δ = c + f − d is too, so each step is a sup-convolution of two
# such functions (slopes merged in decreasing order). Exact rationals
# are used inside; Decimal at the boundary.


@dataclass(frozen=True, slots=True)
class _Concave:
    """A concave piecewise-linear function on [xs[0], xs[-1]]."""

    xs: tuple[Fraction, ...]
    ys: tuple[Fraction, ...]

    @property
    def lo(self) -> Fraction:
        return self.xs[0]

    @property
    def hi(self) -> Fraction:
        return self.xs[-1]

    def at(self, x: Fraction) -> Fraction:
        if not self.lo <= x <= self.hi:
            raise ValueError(f"{x} outside [{self.lo}, {self.hi}]")
        lo, hi = 0, len(self.xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        if self.xs[hi] == self.xs[lo]:
            return self.ys[lo]
        t = (x - self.xs[lo]) / (self.xs[hi] - self.xs[lo])
        return self.ys[lo] + t * (self.ys[hi] - self.ys[lo])

    def segments(self) -> list[tuple[Fraction, Fraction]]:
        """(slope, length) per segment, slopes non-increasing."""
        out = []
        for i in range(len(self.xs) - 1):
            length = self.xs[i + 1] - self.xs[i]
            if length > 0:
                out.append(((self.ys[i + 1] - self.ys[i]) / length, length))
        return out

    def reflected(self) -> _Concave:
        """u ↦ f(−u)."""
        return _Concave(tuple(-x for x in reversed(self.xs)), tuple(reversed(self.ys)))

    def truncated(self, lo: Fraction, hi: Fraction) -> _Concave | None:
        lo, hi = max(lo, self.lo), min(hi, self.hi)
        if lo > hi:
            return None
        inner = [x for x in self.xs if lo < x < hi]
        xs = [lo, *inner, hi]
        return _Concave(tuple(xs), tuple(self.at(x) for x in xs))

    @staticmethod
    def from_points(points: list[tuple[Fraction, Fraction]]) -> _Concave:
        points = sorted(set(points))
        xs, ys = tuple(x for x, _ in points), tuple(y for _, y in points)
        f = _Concave(xs, ys)
        slopes = [slope for slope, _ in f.segments()]
        for a, b in zip(slopes, slopes[1:], strict=False):
            if b > a:
                raise ValueError("slot reward is not concave; the closed form is wrong")
        return f


def _sup_convolve(f: _Concave, g: _Concave) -> _Concave:
    """h(x) = max_y f(y) + g(x − y): concave, with the two slope sequences merged."""
    segments = sorted(f.segments() + g.segments(), key=lambda s: s[0], reverse=True)
    xs, ys = [f.lo + g.lo], [f.ys[0] + g.ys[0]]
    for slope, length in segments:
        xs.append(xs[-1] + length)
        ys.append(ys[-1] + slope * length)
    return _Concave(tuple(xs), tuple(ys))


@dataclass(frozen=True, slots=True)
class _SlotLimits:
    """One slot's caps, in stored kWh: grid import G, free energy F,
    release to export D, inverter budget B; and prices per stored kWh:
    import p, export margin m = η·(e − degradation)."""

    G: Fraction
    F: Fraction
    D: Fraction
    B: Fraction
    p: Fraction
    m: Fraction

    def sources(self) -> list[tuple[Fraction, Fraction, str]]:
        """(price per stored kWh, cap, name) of the two inflow sources,
        cheapest first. Grid import can be cheaper than free energy when its
        price is negative (Agile plunge pricing pays the household to import)."""
        return sorted(((self.p, self.G, "grid"), (Fraction(0), self.F, "free")))

    def inflow_cost(self, inflow: Fraction) -> Fraction:
        """Cost of taking `inflow` stored kWh from the cheapest sources first;
        convex piecewise linear in the inflow."""
        cost, remaining = Fraction(0), inflow
        for price, cap, _ in self.sources():
            take = min(cap, remaining)
            cost += price * take
            remaining -= take
        if remaining != 0:
            raise ValueError("inflow exceeds the sources' caps")
        return cost

    def release_for(self, delta: Fraction) -> Fraction:
        """The optimal stored release d for a net stored change Δ = c + f − d."""
        d_lo = max(Fraction(0), -delta)
        d_hi = min(self.D, (self.B - delta) / 2, self.G + self.F - delta)
        if d_lo > d_hi:
            raise ValueError("infeasible net change")
        # Reward m·d − cost(Δ + d) is concave in d, with one knee where the
        # inflow exhausts the cheaper source.
        first_cap = self.sources()[0][1]
        knee = min(max(d_lo, first_cap - delta), d_hi)
        return max((d_lo, knee, d_hi), key=lambda d: self.m * d - self.inflow_cost(delta + d))

    def split(self, delta: Fraction) -> tuple[Fraction, Fraction, Fraction]:
        """(grid import c, free f, release d) realising Δ at best reward."""
        d = self.release_for(delta)
        remaining = delta + d
        taken: dict[str, Fraction] = {}
        for _, cap, name in self.sources():
            taken[name] = min(cap, remaining)
            remaining -= taken[name]
        return taken["grid"], taken["free"], d

    def reward(self) -> _Concave:
        lo, hi = -min(self.D, self.B), min(self.B, self.G + self.F)
        G, F, D, B = self.G, self.F, self.D, self.B
        candidates = {
            lo,
            hi,
            Fraction(0),
            B,
            G + F,
            F,
            G,
            -D,
            -B,
            B - 2 * D,
            G + F - D,
            F - D,
            G - D,
            2 * (G + F) - B,
            2 * F - B,
            2 * G - B,
        }
        points = []
        for delta in candidates:
            if lo <= delta <= hi:
                c, _, d = self.split(delta)
                points.append((delta, self.m * d - self.p * c))
        return _Concave.from_points(points)


def _fraction(value: Decimal) -> Fraction:
    return Fraction(value)


def _decimal_of(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def optimise_day(
    day: date, slots: Sequence[Slot], spec: BatterySpec, free: Sequence[Decimal]
) -> DaySchedule:
    """Exact optimum of one day's trades (see the module-level note above).

    Storage is empty at both ends of the day. Losses fall on discharge:
    one stored kWh delivers η kWh at the export price, the export limit
    applies to delivered kWh, the inverter bounds battery-side power and
    is time-shared within a slot, and degradation is charged per kWh
    delivered.
    """
    eta = _fraction(spec.round_trip_efficiency)
    capacity = _fraction(spec.capacity_kwh)
    limits = []
    for slot, free_kwh in zip(slots, free, strict=True):
        h = Fraction((slot.end - slot.start) // timedelta(seconds=1), 3600)
        limits.append(
            _SlotLimits(
                G=_fraction(spec.charge_kw) * h,
                F=_fraction(free_kwh),
                D=_fraction(spec.export_limit_kw) * h / eta,
                B=_fraction(spec.inverter_kw) * h,
                p=_fraction(slot.import_p),
                m=eta * (_fraction(slot.export_p) - _fraction(spec.degradation_p_per_kwh)),
            )
        )
    rewards = [limit.reward() for limit in limits]
    # value[i](s): best reward from boundary i onward, starting with stored s.
    zero = Fraction(0)
    value: list[_Concave | None] = [None] * (len(slots) + 1)
    value[len(slots)] = _Concave((zero,), (zero,))
    for i in range(len(slots) - 1, -1, -1):
        following = value[i + 1]
        assert following is not None
        value[i] = _sup_convolve(rewards[i].reflected(), following).truncated(zero, capacity)
        if value[i] is None:
            raise ValueError(f"no feasible schedule on {day}")
    # Forward pass: recover the stored trajectory and each slot's split.
    stored = zero
    charged: list[Fraction] = []
    freed: list[Fraction] = []
    released: list[Fraction] = []
    for i, (limit, reward) in enumerate(zip(limits, rewards, strict=True)):
        following = value[i + 1]
        assert following is not None
        candidates = set(following.xs) | {stored - u for u in reward.reflected().xs}
        feasible = [
            s2
            for s2 in candidates
            if following.lo <= s2 <= following.hi and reward.lo <= s2 - stored <= reward.hi
        ]
        best = max(feasible, key=lambda s2: reward.at(s2 - stored) + following.at(s2))
        c, f, d = limit.split(best - stored)
        charged.append(c)
        freed.append(f)
        released.append(d)
        stored = best
    assert stored == zero
    imported = tuple(_decimal_of(c) for c in charged)
    free_used = tuple(_decimal_of(f) for f in freed)
    exported = tuple(_decimal_of(d * eta) for d in released)
    return DaySchedule(
        day=day,
        imported_kwh=sum(imported, ZERO),
        exported_kwh=sum(exported, ZERO),
        free_kwh=sum(free_used, ZERO),
        import_cost_p=sum((q * s.import_p for q, s in zip(imported, slots, strict=True)), ZERO),
        export_revenue_p=sum((q * s.export_p for q, s in zip(exported, slots, strict=True)), ZERO),
        degradation_p=sum(exported, ZERO) * spec.degradation_p_per_kwh,
        slot_charge_kwh=imported,
        slot_free_kwh=free_used,
        slot_export_kwh=exported,
    )


# --------------------------------------------------------------------- backtest


def _totals(label: str, days: Iterable[DaySchedule], dropped: int) -> Totals:
    scheduled = list(days)
    return Totals(
        label=label,
        scored_days=len(scheduled),
        dropped_days=dropped,
        imported_kwh=sum((d.imported_kwh for d in scheduled), ZERO),
        exported_kwh=sum((d.exported_kwh for d in scheduled), ZERO),
        free_kwh=sum((d.free_kwh for d in scheduled), ZERO),
        import_cost_p=sum((d.import_cost_p for d in scheduled), ZERO),
        export_revenue_p=sum((d.export_revenue_p for d in scheduled), ZERO),
        degradation_p=sum((d.degradation_p for d in scheduled), ZERO),
    )


def backtest(
    spec: BatterySpec,
    import_rates: Sequence[Rate],
    export_rates: Sequence[Rate],
    window_from: date,
    window_to: date,
    *,
    tz: ZoneInfo = LONDON,
    day_start: time = time(23, 0),
) -> BacktestResult:
    scheduled: list[DaySchedule] = []
    dropped: list[tuple[date, str]] = []
    for day in decision_days(window_from, window_to, tz=tz, day_start=day_start):
        slots, reason = slots_for(day, import_rates, export_rates)
        if reason is not None:
            dropped.append((day.day, reason))
            continue
        free = free_energy_by_slot(slots, spec.free_energy_kwh_per_day, tz=tz)
        scheduled.append(optimise_day(day.day, slots, spec, free))
    by_month: dict[str, list[DaySchedule]] = defaultdict(list)
    dropped_by_month: dict[str, int] = defaultdict(int)
    for d in scheduled:
        by_month[d.day.strftime("%Y-%m")].append(d)
    for day_date, _ in dropped:
        dropped_by_month[day_date.strftime("%Y-%m")] += 1
    labels = sorted(set(by_month) | set(dropped_by_month))
    months = tuple(_totals(m, by_month.get(m, []), dropped_by_month.get(m, 0)) for m in labels)
    return BacktestResult(
        rule=RULE,
        spec=spec,
        days=tuple(scheduled),
        dropped=tuple(dropped),
        months=months,
        window=_totals(
            f"{window_from.isoformat()}..{window_to.isoformat()}", scheduled, len(dropped)
        ),
    )


def export_receipts_in_window(
    slots: Sequence[Slot],
    *,
    kwh: Decimal,
    discharge_kw: Decimal,
    start: datetime,
    end: datetime,
) -> tuple[Decimal, Decimal, Decimal | None]:
    """Gross receipts from exporting up to `kwh` inside [start, end) at up to
    `discharge_kw`, best-priced slots first: (kWh exported, pence,
    average export price over the window's slots)."""
    inside = [s for s in slots if s.start >= start and s.end <= end]
    if not inside:
        return ZERO, ZERO, None
    remaining, revenue, delivered = kwh, ZERO, ZERO
    for slot in sorted(inside, key=lambda s: s.export_p, reverse=True):
        q = min(remaining, discharge_kw * slot.hours)
        if q <= ZERO:
            break
        remaining -= q
        delivered += q
        revenue += q * slot.export_p
    hours = sum((s.hours for s in inside), ZERO)
    average = sum((s.export_p * s.hours for s in inside), ZERO) / hours
    return delivered, revenue, average


# ---------------------------------------------------------------- JSON contract


def _decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name} must be a number")
    try:
        return Decimal(str(value))
    except Exception as error:
        raise ValueError(f"{name} is not a number: {value!r}") from error


def spec_from_request(request: Mapping[str, Any]) -> BatterySpec:
    import_limit = request.get("import_limit_kw")
    return BatterySpec(
        capacity_kwh=_decimal(request["battery_kwh"], "battery_kwh"),
        inverter_kw=_decimal(request["inverter_kw"], "inverter_kw"),
        export_limit_kw=_decimal(request["export_limit_kw"], "export_limit_kw"),
        round_trip_efficiency=_decimal(request["round_trip_efficiency"], "round_trip_efficiency"),
        import_limit_kw=None if import_limit is None else _decimal(import_limit, "import_limit_kw"),
        degradation_p_per_kwh=_decimal(
            request.get("degradation_p_per_kwh", 0), "degradation_p_per_kwh"
        ),
        free_energy_kwh_per_day=_decimal(
            request.get("free_energy_kwh_per_day", 0), "free_energy_kwh_per_day"
        ),
    )


def _totals_json(t: Totals) -> dict[str, Any]:
    avg_in, avg_out = t.average_import_p(), t.average_export_p()
    return {
        "label": t.label,
        "scored_days": t.scored_days,
        "dropped_days": t.dropped_days,
        "complete": t.complete,
        "imported_kwh": str(t.imported_kwh.quantize(PENNY)),
        "exported_kwh": str(t.exported_kwh.quantize(PENNY)),
        "free_kwh": str(t.free_kwh.quantize(PENNY)),
        "gross_export_receipts_gbp": str(pounds(t.export_revenue_p)),
        "import_cost_gbp": str(pounds(t.import_cost_p)),
        "degradation_cost_gbp": str(pounds(t.degradation_p)),
        "net_gbp": str(pounds(t.net_p)),
        "average_import_p_per_kwh": None if avg_in is None else str(avg_in.quantize(PENNY)),
        "average_export_p_per_kwh": None if avg_out is None else str(avg_out.quantize(PENNY)),
    }


def result_json(
    request: Mapping[str, Any], result: BacktestResult, *, include_days: bool = False
) -> dict[str, Any]:
    complete_months = [m for m in result.months if m.complete]
    monthly_net = (
        None
        if not complete_months
        else pounds(sum((m.net_p for m in complete_months), ZERO) / Decimal(len(complete_months)))
    )
    out: dict[str, Any] = {
        "rule": result.rule,
        "request": dict(request),
        "assumptions": {k: str(v) for k, v in asdict(result.spec).items()},
        "effective_charge_kw": str(result.spec.charge_kw),
        "window": _totals_json(result.window),
        "months": [_totals_json(m) for m in result.months],
        "monthly_net_gbp_over_complete_months": None if monthly_net is None else str(monthly_net),
        "dropped": [{"day": d.isoformat(), "reason": r} for d, r in result.dropped],
    }
    if include_days:
        out["days"] = [
            {
                "day": d.day.isoformat(),
                "imported_kwh": str(d.imported_kwh.quantize(PENNY)),
                "exported_kwh": str(d.exported_kwh.quantize(PENNY)),
                "free_kwh": str(d.free_kwh.quantize(PENNY)),
                "gross_export_receipts_gbp": str(pounds(d.export_revenue_p)),
                "import_cost_gbp": str(pounds(d.import_cost_p)),
                "net_gbp": str(pounds(d.net_p)),
            }
            for d in result.days
        ]
    return out


def backtest_json(
    request: Mapping[str, Any],
    import_rates: Sequence[Rate],
    export_rates: Sequence[Rate],
    *,
    include_days: bool = False,
) -> dict[str, Any]:
    """The one function a public page may call: request per the contract in
    the declaration, rates from a source, JSON-ready result."""
    spec = spec_from_request(request)
    window = request["window"]
    result = backtest(
        spec,
        import_rates,
        export_rates,
        date.fromisoformat(window["from"]),
        date.fromisoformat(window["to"]),
    )
    return result_json(request, result, include_days=include_days)
