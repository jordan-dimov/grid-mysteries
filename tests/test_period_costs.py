from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations.period_costs import (
    PeriodCost,
    parse_cost_rows,
    select_most_expensive,
)

JUNE = {f"2026-06-{day:02d}" for day in range(1, 31)}


def row(date: str, period: int, constraints, **other) -> dict:
    return {
        "_id": 1,
        "SETT_DATE": date,
        "SETT_PERIOD": period,
        "Constraints": constraints,
        "Energy Imbalance": other.get("imbalance", "0"),
    }


def test_parses_decimals_and_preserves_missingness() -> None:
    costs = parse_cost_rows([row("2026-06-01", 5, "333554.6637471651"), row("2026-06-01", 6, "")])
    assert costs[0].constraints_gbp == Decimal("333554.6637471651")
    assert costs[1].constraints_gbp is None  # blank is MISSING, never zero
    assert costs[0].categories["Energy Imbalance"] == Decimal("0")


def test_selects_the_highest_published_constraints_value() -> None:
    costs = parse_cost_rows(
        [
            row("2026-06-02", 10, "500"),
            row("2026-06-03", 20, "9000"),
            row("2026-06-04", 30, "700"),
        ]
    )
    chosen = select_most_expensive(costs, JUNE)
    assert chosen is not None
    assert (chosen.settlement_date, chosen.settlement_period) == ("2026-06-03", 20)


def test_ties_break_by_earlier_date_then_lower_period() -> None:
    costs = parse_cost_rows(
        [
            row("2026-06-09", 3, "1000"),
            row("2026-06-08", 40, "1000"),
            row("2026-06-08", 12, "1000"),
        ]
    )
    chosen = select_most_expensive(costs, JUNE)
    assert chosen is not None
    assert (chosen.settlement_date, chosen.settlement_period) == ("2026-06-08", 12)


def test_a_missing_value_can_never_win_even_against_a_smaller_one() -> None:
    costs = parse_cost_rows([row("2026-06-05", 1, ""), row("2026-06-06", 2, "1")])
    chosen = select_most_expensive(costs, JUNE)
    assert chosen is not None
    assert (chosen.settlement_date, chosen.settlement_period) == ("2026-06-06", 2)


def test_window_is_respected_and_an_empty_window_is_a_declared_outcome() -> None:
    costs = parse_cost_rows([row("2026-05-31", 1, "999999"), row("2026-07-01", 1, "999999")])
    assert select_most_expensive(costs, JUNE) is None  # neither is in June


def test_negative_constraints_values_are_eligible_as_published() -> None:
    # The published series can carry negative category values; the rule
    # says "highest", so a negative one wins only if nothing beats it.
    costs = parse_cost_rows([row("2026-06-01", 1, "-500"), row("2026-06-02", 1, "-100")])
    chosen = select_most_expensive(costs, JUNE)
    assert chosen is not None
    assert chosen.constraints_gbp == Decimal("-100")


@given(seed=st.randoms())
def test_selection_is_input_order_invariant(seed) -> None:
    rows = [
        row(f"2026-06-{d:02d}", p, str(v))
        for d, p, v in [(1, 1, 10), (2, 5, 990), (3, 7, 990), (4, 2, 5)]
    ]
    shuffled = list(rows)
    seed.shuffle(shuffled)
    a = select_most_expensive(parse_cost_rows(rows), JUNE)
    b = select_most_expensive(parse_cost_rows(shuffled), JUNE)
    assert a is not None and b is not None
    assert (a.settlement_date, a.settlement_period) == (b.settlement_date, b.settlement_period)
    assert (a.settlement_date, a.settlement_period) == ("2026-06-02", 5)  # earlier date wins tie


@given(
    values=st.lists(
        st.tuples(st.integers(1, 30), st.integers(1, 48), st.integers(-10_000, 10_000)),
        min_size=1,
        max_size=40,
        unique_by=lambda t: (t[0], t[1]),
    )
)
def test_winner_is_maximal_and_from_the_input(values) -> None:
    costs = parse_cost_rows([row(f"2026-06-{d:02d}", p, str(v)) for d, p, v in values])
    chosen = select_most_expensive(costs, JUNE)
    assert chosen is not None
    best = chosen.constraints_gbp
    assert best is not None
    assert all(c.constraints_gbp is not None and c.constraints_gbp <= best for c in costs)
    assert chosen in costs


def test_period_cost_is_hashable_and_frozen() -> None:
    cost = PeriodCost("2026-06-01", 1, Decimal("1"), {})
    assert cost.settlement_date == "2026-06-01"
