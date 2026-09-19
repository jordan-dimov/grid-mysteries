"""T4 (DECLARATION-T4.md): every rule, its boundary and a counterexample."""

import re
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction

from grid_mysteries.investigations import cover_price_t4 as t4

SHA = "0" * 64
DECIDED = date(2027, 3, 31)


def row(day: date, wind_mwh: str, l1: str, *, two_cut="1000000", **extra):
    base = {
        "settlement_date": day.isoformat(),
        "seed": False,
        "available": True,
        "disptav_type": "Tagged",
        "wind_bid_mwh": wind_mwh,
        "reconciliation": {"settlement_mwh": {"bid": "1000", "offer": "900"}},
        "two_cut_gbp": two_cut,
        "outcome": {"vintage": (day + timedelta(days=7)).isoformat(), "l1_constraints_gbp": l1},
    }
    return {**base, **extra}


def monotone(n: int, start=date(2026, 9, 16)):
    """x and y rise together: rho = 1."""
    return [
        row(start + timedelta(days=i), str(10 * (i + 1)), str(500000 + 1000 * i)) for i in range(n)
    ]


def test_x_is_wind_bid_volume_over_settlement_bid_volume_and_needs_the_gate():
    assert t4.wind_volume_share(row(date(2026, 9, 16), "250", "1")) == Fraction(1, 4)
    assert t4.wind_volume_share(row(date(2026, 9, 16), "250", "1", disptav_type=None)) is None
    zero = row(date(2026, 9, 16), "250", "1", reconciliation={"settlement_mwh": {"bid": "0"}})
    assert t4.wind_volume_share(zero) is None
    negative_total = row(
        date(2026, 9, 16), "250", "1", reconciliation={"settlement_mwh": {"bid": "-1000"}}
    )
    assert t4.wind_volume_share(negative_total) == Fraction(1, 4)


def test_y_is_exact_first_vintage_l1_over_the_two_cuts():
    r = row(date(2026, 9, 16), "1", "4130074.237688298916", two_cut="8013673.744717194012226142")
    y = t4.constraint_share(r)
    assert y == Fraction(Decimal("4130074.237688298916")) / Fraction(
        Decimal("8013673.744717194012226142")
    )
    assert t4.constraint_share(dict(r, outcome=None)) is None
    assert t4.constraint_share(dict(r, two_cut_gbp="0")) is None
    late = dict(r, outcome={"vintage": "2027-04-01", "l1_constraints_gbp": "1"})
    assert t4.constraint_share(late) is None  # arrived after the falsifier date
    on_the_day = dict(r, outcome={"vintage": "2027-03-31", "l1_constraints_gbp": "1"})
    assert t4.constraint_share(on_the_day) is not None


def test_no_day_before_2026_09_16_and_no_seed_day_ever_qualifies():
    seen = [row(date(2026, 9, 1) + timedelta(days=i), "5", "5") for i in range(15)]
    assert t4.qualifying(seen) == []
    assert t4.qualifying([row(date(2026, 9, 16), "5", "5", seed=True)]) == []
    assert [d for d, _, _ in t4.qualifying([row(date(2026, 9, 16), "5", "5")])] == ["2026-09-16"]
    assert t4.qualifying([row(date(2027, 4, 1), "5", "5")]) == []
    assert t4.qualifying([row(date(2026, 9, 16), "5", "5", available=False)]) == []


def test_ties_share_the_average_rank():
    assert t4.ranks([Fraction(3), Fraction(1), Fraction(3), Fraction(2)]) == [
        Fraction(7, 2),
        Fraction(1),
        Fraction(7, 2),
        Fraction(2),
    ]


def test_the_threshold_is_exact_at_one_half():
    # Ranks x = 1..4, y = 1 3 2 4: sum d^2 = 2, rho = 1 - 12/60 = 0.8.
    xs = [Fraction(i) for i in (1, 2, 3, 4)]
    assert t4.spearman_at_least(xs, [Fraction(v) for v in (1, 3, 2, 4)], t4.RHO_MIN) == (
        True,
        Decimal("0.8000"),
    )
    # Exactly 0.5: x = 1..5, y = 1 4 2 5 3, sum d^2 = 10, rho = 1 - 60/120. Then 0.3.
    five = [Fraction(i) for i in (1, 2, 3, 4, 5)]
    reaches, rho = t4.spearman_at_least(five, [Fraction(v) for v in (1, 4, 2, 5, 3)], t4.RHO_MIN)
    assert rho == Decimal("0.5000") and reaches is True
    reaches, rho = t4.spearman_at_least(five, [Fraction(v) for v in (2, 4, 1, 5, 3)], t4.RHO_MIN)
    assert rho is not None and rho < Decimal("0.5") and reaches is False
    assert (
        t4.spearman_at_least(five, [Fraction(v) for v in (5, 4, 3, 2, 1)], t4.RHO_MIN)[0] is False
    )


def test_a_constant_variable_cannot_rise():
    xs = [Fraction(1)] * 5
    assert t4.spearman_at_least(xs, [Fraction(i) for i in range(5)], t4.RHO_MIN) == (False, None)


def test_before_the_falsifier_date_only_the_count_is_reported():
    block = t4.evaluate(monotone(25), date(2027, 3, 30), SHA)
    assert block["n"] == 25 and block["decided"] is False
    assert block["rho"] is None and block["holds"] is None


def test_the_verdict_on_the_falsifier_date():
    holds = t4.evaluate(monotone(20), DECIDED, SHA)
    assert holds["holds"] is True and holds["rho"] == "1.0000" and holds["n"] == 20
    undecided = t4.evaluate(monotone(19), DECIDED, SHA)
    assert undecided["holds"] is None and undecided["rho"] is None and undecided["n"] == 19
    falling = monotone(20)
    for i, r in enumerate(falling):
        r["outcome"]["l1_constraints_gbp"] = str(900000 - 1000 * i)
    fails = t4.evaluate(falling, DECIDED, SHA)
    assert fails["holds"] is False and fails["rho"] == "-1.0000"
    assert fails["declaration_sha256"] == SHA and fails["window_start"] == "2026-09-16"


def test_a_later_run_reaches_the_same_verdict():
    rows = monotone(20)
    late = row(date(2026, 12, 1), "1", "1")
    late["outcome"]["vintage"] = "2027-04-15"  # published after the falsifier date
    on_the_day = t4.evaluate([*rows, late], date(2027, 3, 31), SHA)
    months_later = t4.evaluate([*rows, late], date(2027, 6, 1), SHA)
    assert on_the_day == months_later and on_the_day["n"] == 20


def test_describe_shows_only_the_count_before_the_date_and_both_renderers_use_it():
    from grid_mysteries.rendering import balancing_bill as bb

    early = t4.evaluate(monotone(3), date(2026, 10, 1), SHA)
    assert t4.describe(early) == ("undecided", "3 qualifying days; decided once on 2027-03-31")
    assert t4.describe(t4.evaluate(monotone(1), DECIDED, SHA)) == (
        "undecided",
        "1 qualifying day, fewer than 20",
    )
    assert t4.describe(t4.evaluate(monotone(20), DECIDED, SHA)) == (
        "holds",
        "rho 1.0000 over 20 qualifying days",
    )
    props = {
        "falsifier_date": "2027-03-31",
        **{k: {"claim": k, "instances": [], "holds": None} for k in ("T1", "T2", "T3")},
        "T4": early,
    }
    html = bb.render_propositions(props)
    assert "<strong>T4</strong>" in html and "3 qualifying days; decided once" in html
    assert not re.search(r"rho -?\d", html)  # the claim names rho; no computed value appears


def test_context_is_reported_only_with_the_verdict_and_never_changes_it():
    rows = monotone(20)
    for i, r in enumerate(rows):
        r["wind_bid_share"] = str(Decimal("0.3") - Decimal(i) / 100)  # falls as x rises
        r["sign_convention_holds"] = i % 2 == 0
    early = t4.evaluate(rows, date(2027, 3, 30), SHA)
    assert "context" not in early
    block = t4.evaluate(rows, DECIDED, SHA)
    assert block["holds"] is True and block["rho"] == "1.0000"
    ctx = block["context"]
    assert ctx["rho_with_gbp_wind_bid_share"] == "-1.0000"  # reported, not deciding
    assert ctx["rho_on_sign_check_holds_days"] == "1.0000" and ctx["sign_check_holds_days"] == 10
    assert len(ctx["points"]) == 20 and ctx["points"][0]["settlement_date"] == "2026-09-16"
