from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal as D

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from grid_mysteries.investigations import household_desk as hd
from grid_mysteries.investigations.household_desk import (
    LONDON,
    ZERO,
    BatterySpec,
    Rate,
    Slot,
    backtest,
    backtest_json,
    decision_days,
    export_receipts_in_window,
    free_energy_by_slot,
    optimise_day,
    slots_for,
    spec_from_request,
)


def half_hours(day: hd.DecisionDay, price):
    """Half-hourly rates over one decision day; `price(local_hour) -> Decimal`."""
    rates, t = [], day.start
    while t < day.end:
        e = t + timedelta(minutes=30)
        rates.append(Rate(t, e, price(t.astimezone(LONDON).hour)))
        t = e
    return rates


def slots_with(prices: list[tuple[str, str]], start=datetime(2026, 6, 24, 0, 0, tzinfo=UTC)):
    """Consecutive one-hour slots from (import, export) pence pairs."""
    out = []
    for i, (imp, exp) in enumerate(prices):
        s = start + timedelta(hours=i)
        out.append(Slot(s, s + timedelta(hours=1), D(imp), D(exp)))
    return out


SPEC = BatterySpec(D(200), D(20), D(20), D("0.90"))
EPS = D("1e-12")


# ------------------------------------------------------------- decision days


def test_agile_day_runs_23_to_23_local_and_is_decided_at_16_the_day_before() -> None:
    (summer,) = decision_days(date(2026, 6, 24), date(2026, 6, 24))
    assert summer.day == date(2026, 6, 24)
    assert summer.start == datetime(2026, 6, 23, 22, 0, tzinfo=UTC)  # 23:00 BST
    assert summer.end == datetime(2026, 6, 24, 22, 0, tzinfo=UTC)
    assert summer.decision_at == datetime(2026, 6, 23, 15, 0, tzinfo=UTC)  # 16:00 BST
    (winter,) = decision_days(date(2026, 1, 15), date(2026, 1, 15))
    assert winter.start == datetime(2026, 1, 14, 23, 0, tzinfo=UTC)
    assert winter.decision_at == datetime(2026, 1, 14, 16, 0, tzinfo=UTC)


def test_midnight_days_are_attributed_to_their_own_date() -> None:
    (d,) = decision_days(date(2026, 6, 24), date(2026, 6, 24), day_start=time(0, 0))
    assert d.start == datetime(2026, 6, 23, 23, 0, tzinfo=UTC)
    assert d.end == datetime(2026, 6, 24, 23, 0, tzinfo=UTC)
    assert d.decision_at == datetime(2026, 6, 23, 15, 0, tzinfo=UTC)


def test_window_yields_one_day_per_date_and_clock_change_days_have_23_or_25_hours() -> None:
    days = decision_days(date(2026, 3, 28), date(2026, 3, 30))
    assert [d.day for d in days] == [date(2026, 3, 28), date(2026, 3, 29), date(2026, 3, 30)]
    hours = [(d.end - d.start).total_seconds() / 3600 for d in days]
    assert hours == [24.0, 23.0, 24.0]  # BST starts 2026-03-29 01:00


# --------------------------------------------------------------------- slots


def test_slots_take_the_union_of_boundaries_and_slice_a_fixed_tariff() -> None:
    (day,) = decision_days(date(2026, 6, 24), date(2026, 6, 24))
    imp = [Rate(datetime(2020, 1, 1, tzinfo=UTC), None, D(20))]  # open-ended, known always
    exp = half_hours(day, lambda h: D(15))
    slots, why = slots_for(day, imp, exp)
    assert why is None and len(slots) == 48
    assert all(s.import_p == D(20) and s.hours == D("0.5") for s in slots)


def test_a_gap_or_an_unpublished_price_drops_the_day_with_a_reason() -> None:
    (day,) = decision_days(date(2026, 6, 24), date(2026, 6, 24))
    imp = half_hours(day, lambda h: D(20))
    exp = half_hours(day, lambda h: D(15))
    _, why = slots_for(day, imp, exp[:-1])
    assert why is not None and why.startswith("no export price for 2026-06-24T21:30")
    late = [
        Rate(r.valid_from, r.valid_to, r.pence_per_kwh, day.decision_at + timedelta(minutes=1))
        for r in imp
    ]
    _, why = slots_for(day, late, exp)
    assert why is not None and "not known at decision" in why
    ok = [Rate(r.valid_from, r.valid_to, r.pence_per_kwh, day.decision_at) for r in imp]
    assert slots_for(day, ok, exp)[1] is None


def test_free_energy_is_spread_over_daylight_slots_by_duration() -> None:
    (day,) = decision_days(date(2026, 6, 24), date(2026, 6, 24))
    slots, _ = slots_for(day, half_hours(day, lambda h: D(1)), half_hours(day, lambda h: D(1)))
    free = free_energy_by_slot(slots, D(40))
    assert sum(free) == D(40)
    lit = [f for f, s in zip(free, slots, strict=True) if f > 0]
    assert len(lit) == 16  # 09:00–17:00 local, half-hourly
    assert all(f == D("2.5") for f in lit)
    assert free_energy_by_slot(slots, ZERO) == [ZERO] * 48


# ------------------------------------------------------------------- optimum


def test_buys_low_then_sells_high_with_losses_on_discharge() -> None:
    s = optimise_day(date(2026, 6, 24), slots_with([("10", "1"), ("50", "40")]), SPEC, [ZERO] * 2)
    assert s.imported_kwh == D(20)  # 20 kW for one hour
    assert s.exported_kwh == D(18)  # 90 % delivered
    assert s.import_cost_p == D(200) and s.export_revenue_p == D(720)
    assert s.net_p == D(520)
    assert s.slot_export_kwh == (ZERO, D(18))


def test_never_sells_before_it_buys_and_a_single_slot_can_only_time_share() -> None:
    reversed_day = slots_with([("50", "40"), ("10", "1")])
    s = optimise_day(date(2026, 6, 24), reversed_day, SPEC, [ZERO] * 2)
    assert s.imported_kwh == ZERO and s.exported_kwh == ZERO
    # One slot, export worth more than import: half the hour charging, half
    # discharging (Amendment 1), never the full 20 kWh each way.
    one_slot = slots_with([("10", "40")])
    s = optimise_day(date(2026, 6, 24), one_slot, SPEC, [ZERO])
    assert s.imported_kwh == D(10) and s.exported_kwh == D(9)


def test_efficiency_wedge_decides_marginal_trades() -> None:
    # 0.9 × 11 = 9.9 < 10: not worth it. 0.9 × 12 = 10.8 > 10: worth it.
    no = optimise_day(date(2026, 6, 24), slots_with([("10", "0"), ("99", "11")]), SPEC, [ZERO] * 2)
    yes = optimise_day(date(2026, 6, 24), slots_with([("10", "0"), ("99", "12")]), SPEC, [ZERO] * 2)
    assert no.exported_kwh == ZERO and yes.exported_kwh == D(18)


def test_degradation_is_charged_per_kwh_delivered_and_can_kill_a_trade() -> None:
    worn = BatterySpec(D(200), D(20), D(20), D("0.90"), degradation_p_per_kwh=D(5))
    day = slots_with([("10", "0"), ("99", "15")])  # 0.9 × (15 − 5) = 9 < 10
    assert optimise_day(date(2026, 6, 24), day, worn, [ZERO] * 2).exported_kwh == ZERO
    day = slots_with([("10", "0"), ("99", "20")])  # 0.9 × (20 − 5) = 13.5 > 10
    s = optimise_day(date(2026, 6, 24), day, worn, [ZERO] * 2)
    assert s.exported_kwh == D(18) and s.degradation_p == D(90)
    assert s.net_p == D(360) - D(200) - D(90)


def test_export_limit_binds_the_g98_household_and_capacity_binds_a_small_battery() -> None:
    g98 = BatterySpec(D(200), D(20), D("3.68"), D("0.90"))
    day = slots_with([("10", "0")] * 10 + [("99", "40")] * 5)
    s = optimise_day(date(2026, 6, 24), day, g98, [ZERO] * 15)
    assert s.exported_kwh == D("18.40")  # 3.68 kW × 5 h
    small = BatterySpec(D(5), D(20), D(20), D("1"))
    s = optimise_day(date(2026, 6, 24), day, small, [ZERO] * 15)
    assert s.exported_kwh == D(5) and s.imported_kwh == D(5)


def test_a_slot_cannot_import_and_export_at_full_power_at_once() -> None:
    # Export beats import inside the same slot: a pass-through is worth
    # doing, but only by sharing the inverter's time, so 20 kW for an hour
    # buys c and sells d/η with c + d/η ≤ 20 kWh, not 20 kWh each way.
    day = slots_with([("7", "12")])
    s = optimise_day(date(2026, 6, 24), day, SPEC, [ZERO])
    assert s.imported_kwh == D(10) and s.exported_kwh == D(9)
    assert s.net_p == D(9) * D(12) - D(10) * D(7)
    # With a 3.68 kW export limit the export edge binds first.
    g98 = BatterySpec(D(200), D(20), D("3.68"), D("0.90"))
    s = optimise_day(date(2026, 6, 24), day, g98, [ZERO])
    assert s.exported_kwh == D("3.68")


def test_storage_is_empty_at_both_ends_of_the_day() -> None:
    day = slots_with([("10", "0"), ("5", "0"), ("99", "40"), ("30", "35"), ("99", "20")])
    s = optimise_day(date(2026, 6, 24), day, SPEC, [ZERO] * 5)
    assert abs(s.exported_kwh - SPEC.round_trip_efficiency * (s.imported_kwh + s.free_kwh)) < EPS


def test_free_energy_is_exported_whenever_it_clears_degradation() -> None:
    worn = BatterySpec(D(200), D(20), D(20), D("0.90"), degradation_p_per_kwh=D(2))
    day = slots_with([("99", "0"), ("99", "3")])
    s = optimise_day(date(2026, 6, 24), day, worn, [D(10), ZERO])
    assert s.imported_kwh == ZERO and s.free_kwh == D(10) and s.exported_kwh == D(9)
    assert s.net_p == D(9) * D(3) - D(9) * D(2)


@settings(max_examples=40, deadline=None)
@given(
    st.lists(
        st.tuples(st.integers(0, 60), st.integers(0, 60)),
        min_size=1,
        max_size=12,
    )
)
def test_optimum_is_never_negative_and_beats_a_single_pair_greedy(prices) -> None:
    day = slots_with([(str(i), str(e)) for i, e in prices])
    s = optimise_day(date(2026, 6, 24), day, SPEC, [ZERO] * len(day))
    assert s.net_p >= ZERO
    assert abs(s.exported_kwh - SPEC.round_trip_efficiency * s.imported_kwh) < EPS
    # The best single buy-then-sell pair, at full power, is a feasible plan.
    best = ZERO
    for i, buy in enumerate(day):
        for sell in day[i + 1 :]:
            q = SPEC.inverter_kw  # one hour each way, within the inverter budget
            best = max(best, q * (SPEC.round_trip_efficiency * sell.export_p - buy.import_p))
    assert s.net_p >= best


# ------------------------------------------------------------------ backtest


def month_rates(price_import, price_export):
    days = decision_days(date(2026, 6, 1), date(2026, 7, 31))
    imp = [r for d in days for r in half_hours(d, price_import)]
    exp = [r for d in days for r in half_hours(d, price_export)]
    return imp, exp


def test_backtest_totals_by_month_and_flags_incomplete_months() -> None:
    imp, exp = month_rates(lambda h: D(10), lambda h: D(30) if 16 <= h < 21 else D(2))
    result = backtest(SPEC, imp, exp, date(2026, 6, 1), date(2026, 7, 31))
    assert [m.label for m in result.months] == ["2026-06", "2026-07"]
    june = result.months[0]
    assert june.scored_days == 30 and june.complete and june.dropped_days == 0
    # Five peak hours at 20 kW battery-side: 100 kWh stored a day from the
    # grid at 10p, 90 kWh delivered at 30p.
    assert june.imported_kwh == D(3000) and june.exported_kwh == D(2700)
    assert hd.pounds(june.net_p) == D("510.00")
    short = backtest(SPEC, imp, exp, date(2026, 6, 1), date(2026, 6, 10))
    assert not short.months[0].complete and short.window.scored_days == 10


def test_backtest_drops_days_with_gaps_and_reports_them() -> None:
    imp, exp = month_rates(lambda h: D(10), lambda h: D(30))
    missing = [r for r in exp if r.valid_from.date() != date(2026, 6, 15)]
    result = backtest(SPEC, imp, missing, date(2026, 6, 1), date(2026, 6, 30))
    dropped = dict(result.dropped)
    assert set(dropped) == {date(2026, 6, 15), date(2026, 6, 16)}  # both Agile days touched
    assert result.months[0].scored_days == 28 and result.months[0].dropped_days == 2


def test_export_receipts_in_window_fill_the_best_slots_first_within_the_power_limit() -> None:
    (day,) = decision_days(date(2026, 6, 24), date(2026, 6, 24))
    exp = half_hours(day, lambda h: D(40) if h == 17 else (D(30) if 16 <= h < 21 else D(5)))
    slots, _ = slots_for(day, half_hours(day, lambda h: D(10)), exp)
    start = datetime(2026, 6, 24, 16, 0, tzinfo=LONDON).astimezone(UTC)
    end = datetime(2026, 6, 24, 21, 0, tzinfo=LONDON).astimezone(UTC)
    kwh, pence, average = export_receipts_in_window(
        slots, kwh=D(200), discharge_kw=D(20), start=start, end=end
    )
    assert kwh == D(100) and pence == D(20) * D(40) + D(80) * D(30)
    assert average == D(32)
    kwh, pence, _ = export_receipts_in_window(
        slots, kwh=D(200), discharge_kw=D("3.68"), start=start, end=end
    )
    assert kwh == D("18.40") and pence == D("3.68") * D(40) + D("14.72") * D(30)


# ------------------------------------------------------------- JSON contract


REQUEST = {
    "battery_kwh": 200,
    "inverter_kw": "20",
    "export_limit_kw": 3.68,
    "round_trip_efficiency": "0.90",
    "degradation_p_per_kwh": 2,
    "import_tariff": {"product": "AGILE-24-10-01", "region": "E"},
    "export_tariff": {"product": "AGILE-OUTGOING-19-05-13", "region": "E"},
    "window": {"from": "2026-06-01", "to": "2026-06-30"},
}


def test_request_numbers_become_decimals_and_limits_take_the_minimum() -> None:
    spec = spec_from_request(REQUEST)
    assert spec.capacity_kwh == D(200) and spec.charge_kw == D(20)
    assert spec.export_limit_kw == D("3.68") and spec.degradation_p_per_kwh == D(2)
    assert spec.free_energy_kwh_per_day == ZERO
    capped = spec_from_request({**REQUEST, "import_limit_kw": 7})
    assert capped.charge_kw == D(7) and capped.inverter_kw == D(20)
    with pytest.raises(ValueError):
        spec_from_request({**REQUEST, "round_trip_efficiency": "1.2"})
    with pytest.raises(ValueError):
        spec_from_request({**REQUEST, "battery_kwh": None})


def test_backtest_json_is_strings_and_carries_the_rule_and_assumptions() -> None:
    imp, exp = month_rates(lambda h: D(10), lambda h: D(30) if 16 <= h < 21 else D(2))
    out = backtest_json(REQUEST, imp, exp, include_days=True)
    assert out["rule"] == hd.RULE
    assert out["assumptions"]["export_limit_kw"] == "3.68" and out["effective_charge_kw"] == "20"
    june = out["months"][0]
    assert june["label"] == "2026-06" and june["complete"] is True
    # 3.68 kW × 5 h × 30 days = 552 kWh at 30p = £165.60 gross.
    assert june["exported_kwh"] == "552.00"
    assert june["gross_export_receipts_gbp"] == "165.60"
    assert june["average_export_p_per_kwh"] == "30.00"
    assert out["monthly_net_gbp_over_complete_months"] == june["net_gbp"]
    assert len(out["days"]) == 30 and out["dropped"] == []


def _check_feasible_and_valued(slots, spec, s: hd.DaySchedule, free) -> None:
    """The recovered schedule must respect every constraint and its money
    must equal the sum over slots — the DP's value and its backtrack agree."""
    eta = spec.round_trip_efficiency
    stored = ZERO
    for i, slot in enumerate(slots):
        c, f, e = s.slot_charge_kwh[i], s.slot_free_kwh[i], s.slot_export_kwh[i]
        d = e / eta  # stored kWh released
        assert c >= ZERO and f >= ZERO and d >= ZERO
        assert c <= spec.charge_kw * slot.hours + EPS
        assert f <= free[i] + EPS
        assert e <= spec.export_limit_kw * slot.hours + EPS
        assert c + f + d <= spec.inverter_kw * slot.hours + EPS  # Amendment 1
        assert d <= stored + c + f + EPS  # nothing sold before it is bought (fluid limit)
        stored = stored + c + f - d
        assert -EPS <= stored <= spec.capacity_kwh + EPS
    assert abs(stored) < EPS


@settings(max_examples=60, deadline=None)
@given(
    st.lists(st.tuples(st.integers(-5, 60), st.integers(0, 60)), min_size=1, max_size=8),
    st.sampled_from(["3.68", "11.04", "20"]),
    st.integers(0, 3),
    st.integers(0, 30),
)
def test_schedule_is_feasible_and_reproduces_the_optimum(prices, limit, degradation, free_kwh):
    spec = BatterySpec(D(30), D(20), D(limit), D("0.90"), degradation_p_per_kwh=D(degradation))
    day = slots_with([(str(i), str(e)) for i, e in prices])
    free = [D(free_kwh)] + [ZERO] * (len(day) - 1)
    s = optimise_day(date(2026, 6, 24), day, spec, free)
    _check_feasible_and_valued(day, spec, s, free)
    # Raising the export limit or the capacity can never lose money.
    roomier = BatterySpec(D(60), D(20), D(20), D("0.90"), degradation_p_per_kwh=D(degradation))
    assert optimise_day(date(2026, 6, 24), day, roomier, free).net_p >= s.net_p - EPS


def test_optimum_matches_a_brute_force_over_a_small_grid() -> None:
    # Two one-hour slots, η = 1, inverter 2 kW, capacity 3 kWh. Brute force
    # over quarter-kWh steps hits every vertex of this little polytope.
    from itertools import product

    spec = BatterySpec(D(3), D(2), D(2), D(1))
    for prices in ([("4", "9"), ("1", "6")], [("2", "5"), ("3", "1")], [("5", "6"), ("5", "6")]):
        day = slots_with(prices)
        s = optimise_day(date(2026, 6, 24), day, spec, [ZERO, ZERO])
        steps = [D(k) / 4 for k in range(9)]
        best = None
        for c0, d0, c1, d1 in product(steps, repeat=4):
            if c0 + d0 > 2 or c1 + d1 > 2 or d0 > c0:
                continue  # a slot may release only what it holds or takes in
            soc1 = c0 - d0
            if soc1 > 3 or d1 > soc1 + c1 or soc1 + c1 - d1 != 0:
                continue
            value = (
                d0 * D(prices[0][1])
                + d1 * D(prices[1][1])
                - c0 * D(prices[0][0])
                - c1 * D(prices[1][0])
            )
            best = value if best is None else max(best, value)
        assert s.net_p == best
