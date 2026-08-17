from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations.constraint_episodes import (
    Episode,
    ScoredEpisode,
    episodes,
    repeat_curtailment_cycles,
    select,
)


def cost_row(group: str, day: str, cost: str) -> dict:
    return {"Constraint Group": group, "Settlement Date": day, "Daily Cost (GBP)": cost}


def test_episodes_are_maximal_consecutive_nonzero_runs_with_gaps_visible() -> None:
    rows = [
        cost_row("SCOTEX", "2026-05-03", "1000"),
        cost_row("SCOTEX", "2026-05-04", "50.5"),
        cost_row("SCOTEX", "2026-05-05", "0"),  # zero-cost day splits the run
        cost_row("SCOTEX", "2026-05-06", "7"),
        cost_row("ESTEX", "2026-05-04", "-12"),  # literal non-zero: any sign
    ]
    assert episodes(rows) == [
        Episode("ESTEX", ("2026-05-04",)),
        Episode("SCOTEX", ("2026-05-03", "2026-05-04")),
        Episode("SCOTEX", ("2026-05-06",)),
    ]


@given(seed=st.randoms())
def test_episode_detection_is_input_order_invariant(seed):
    rows = [
        cost_row("B1", f"2026-05-{d:02d}", str(c))
        for d, c in [(1, 5), (2, 0), (3, 9), (4, 4), (10, 1)]
    ] + [cost_row("B2", "2026-05-03", "2")]
    shuffled = list(rows)
    seed.shuffle(shuffled)
    assert episodes(shuffled) == episodes(rows)


def key(day: int, period: int) -> tuple[str, int]:
    return (f"2026-05-{day:02d}", period)


def test_cycle_scan_follows_the_frozen_wording() -> None:
    # bid-down p10, export re-presented p20, bid-down p25 -> one cycle
    assert repeat_curtailment_cycles({key(1, 10), key(1, 25)}, {key(1, 20)}) == 1
    # export and the repeat bid-down in the same period counts
    assert repeat_curtailment_cycles({key(1, 10), key(1, 20)}, {key(1, 20)}) == 1
    # an export only alongside the FIRST bid-down does not arm a cycle
    assert repeat_curtailment_cycles({key(1, 10)}, {key(1, 10)}) == 0
    # two bid-downs with no intervening export: no cycle
    assert repeat_curtailment_cycles({key(1, 10), key(1, 12)}, set()) == 0
    # the documented signature limitation: a pre-existing consecutive
    # export schedule produces cycles with no proven re-trade
    assert (
        repeat_curtailment_cycles({key(1, 10), key(1, 11), key(1, 12)}, {key(1, 11), key(1, 12)})
        == 2
    )
    # cycles span days within an episode
    assert repeat_curtailment_cycles({key(1, 40), key(2, 5)}, {key(2, 3)}) == 1


@given(
    bid_downs=st.sets(
        st.tuples(st.integers(1, 3), st.integers(1, 48)).map(lambda t: key(t[0], t[1])),
        max_size=12,
    ),
    exports=st.sets(
        st.tuples(st.integers(1, 3), st.integers(1, 48)).map(lambda t: key(t[0], t[1])),
        max_size=12,
    ),
)
def test_cycles_are_bounded_and_deterministic(bid_downs, exports):
    cycles = repeat_curtailment_cycles(bid_downs, exports)
    assert 0 <= cycles <= max(0, len(bid_downs) - 1)
    assert cycles <= len(exports)
    # duplicate acceptance rows collapse to the same period sets, so
    # re-running with identical sets is trivially identical
    assert repeat_curtailment_cycles(set(bid_downs), set(exports)) == cycles


def test_selection_tie_breaks_are_total_and_none_means_not_evaluable() -> None:
    a = ScoredEpisode(Episode("B", ("2026-05-03",)), 5, Decimal("100"))
    b = ScoredEpisode(Episode("A", ("2026-05-03",)), 5, Decimal("100"))
    c = ScoredEpisode(Episode("C", ("2026-05-01",)), 5, Decimal("200"))
    d = ScoredEpisode(Episode("D", ("2026-05-01",)), 7, Decimal("1"))
    assert select([a, b, c, d]) == d  # score first
    assert select([a, b, c]) == c  # then bid-down MWh
    assert select([a, b]) == b  # then group name (same start)
    assert select([ScoredEpisode(Episode("X", ("2026-05-01",)), 0, Decimal("9"))]) is None
