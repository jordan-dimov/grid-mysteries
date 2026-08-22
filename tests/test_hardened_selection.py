from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations.bod_inversion import InversionCandidate
from grid_mysteries.investigations.hardened_selection import (
    STAGE_AFTER_DELIVERABILITY,
    STAGE_AFTER_SYSTEM_FLAG,
    STAGE_RAW,
    alternative_key,
    naive_notional_gbp,
    screen,
    select,
)
from grid_mysteries.investigations.phantom_liquidity import NON_DELIVERABLE, NOT_RULED_OUT


def candidate(
    *,
    date: str = "2026-08-11",
    period: int = 20,
    direction: str = "bid",
    accepted_unit: str = "T_ACC-1",
    accepted_pair: int = -1,
    accepted_price: str = "-100",
    volume: str = "-10",
    alt_unit: str = "E_ALT-1",
    alt_pair: int = -1,
    alt_price: str = "500",
) -> InversionCandidate:
    return InversionCandidate(
        settlement_date=date,
        settlement_period=period,
        direction=direction,  # type: ignore[arg-type]
        accepted_unit=accepted_unit,
        accepted_pair_id=accepted_pair,
        accepted_price_gbp_per_mwh=Decimal(accepted_price),
        accepted_volume_mwh=Decimal(volume),
        unaccepted_unit=alt_unit,
        unaccepted_pair_id=alt_pair,
        unaccepted_price_gbp_per_mwh=Decimal(alt_price),
        unaccepted_max_level_mw=Decimal("20"),
    )


def deliverable(candidates, *, non_deliverable=()) -> dict:
    return {
        alternative_key(c): (
            NON_DELIVERABLE if alternative_key(c) in non_deliverable else NOT_RULED_OUT
        )
        for c in candidates
    }


def test_amendment_a_removes_the_001_failure_mode() -> None:
    # 001 selected a case whose alternative had FPN 0 / MEL 0: proved
    # non-deliverable, so under the amended rule it never reaches selection.
    phantom = candidate(alt_unit="E_RHEI-LIKE", alt_price="9949")
    real = candidate(alt_unit="E_REAL-1", alt_price="200", accepted_unit="T_ACC-2")
    candidates = [phantom, real]
    survivors, funnel = screen(
        candidates,
        deliverability=deliverable(candidates, non_deliverable={alternative_key(phantom)}),
        system_flagged=set(),
    )
    assert survivors == [real]
    assert select(survivors) == real
    assert [s.name for s in funnel.stages] == [
        STAGE_RAW,
        STAGE_AFTER_DELIVERABILITY,
        STAGE_AFTER_SYSTEM_FLAG,
    ]
    assert [s.candidates for s in funnel.stages] == [2, 1, 1]


def test_amendment_b_removes_system_flagged_accepted_actions() -> None:
    flagged = candidate(accepted_unit="T_CURTAILED-1")
    clean = candidate(accepted_unit="T_ENERGY-1", alt_price="300")
    candidates = [flagged, clean]
    survivors, funnel = screen(
        candidates,
        deliverability=deliverable(candidates),
        system_flagged={("2026-08-11", 20, "T_CURTAILED-1")},
    )
    assert survivors == [clean]
    assert [s.candidates for s in funnel.stages] == [2, 2, 1]


def test_system_flag_is_keyed_by_unit_period_not_pair() -> None:
    # BOALF has no pair id: a flagged unit-period removes every accepted
    # pair of that unit in that period (the conservative reading).
    one = candidate(accepted_pair=-1)
    two = candidate(accepted_pair=-2, accepted_price="-90")
    candidates = [one, two]
    survivors, _ = screen(
        candidates,
        deliverability=deliverable(candidates),
        system_flagged={("2026-08-11", 20, "T_ACC-1")},
    )
    assert survivors == []
    assert select(survivors) is None  # the declared not-evaluable outcome


def test_missing_deliverability_is_an_error_never_deliverable() -> None:
    c = candidate()
    try:
        screen([c], deliverability={}, system_flagged=set())
    except KeyError as error:
        assert "not_ruled_out" in str(error)
    else:
        raise AssertionError("a missing classification must raise, never pass as deliverable")


def test_notional_counts_each_accepted_action_once() -> None:
    # Two alternatives for ONE accepted action: notional uses the best gap
    # once, not the sum, so a crowded period cannot inflate the funnel.
    a = candidate(alt_unit="E_A", alt_price="400")  # gap 500
    b = candidate(alt_unit="E_B", alt_price="300")  # gap 400
    assert naive_notional_gbp([a, b]) == Decimal("10") * Decimal("500")


@given(seed=st.randoms())
def test_screening_is_input_order_invariant(seed) -> None:
    candidates = [
        candidate(accepted_unit=f"T_{i}", alt_unit=f"E_{i}", alt_price=str(100 + i * 10))
        for i in range(6)
    ]
    flagged = {("2026-08-11", 20, "T_2")}
    non_deliverable = {alternative_key(candidates[4])}
    shuffled = list(candidates)
    seed.shuffle(shuffled)
    expected, funnel_a = screen(
        candidates,
        deliverability=deliverable(candidates, non_deliverable=non_deliverable),
        system_flagged=flagged,
    )
    actual, funnel_b = screen(
        shuffled,
        deliverability=deliverable(shuffled, non_deliverable=non_deliverable),
        system_flagged=flagged,
    )
    assert select(actual) == select(expected)
    assert sorted(map(str, actual)) == sorted(map(str, expected))
    assert funnel_a.as_dict() == funnel_b.as_dict()


@given(
    flagged_units=st.sets(st.sampled_from(["T_0", "T_1", "T_2"]), max_size=3),
    dead_alts=st.sets(st.sampled_from([0, 1, 2]), max_size=3),
)
def test_funnel_is_monotone_and_selection_comes_from_survivors(flagged_units, dead_alts) -> None:
    candidates = [
        candidate(accepted_unit=f"T_{i}", alt_unit=f"E_{i}", alt_price=str(200 + i * 10))
        for i in range(3)
    ]
    non_deliverable = {alternative_key(candidates[i]) for i in dead_alts}
    survivors, funnel = screen(
        candidates,
        deliverability=deliverable(candidates, non_deliverable=non_deliverable),
        system_flagged={("2026-08-11", 20, u) for u in flagged_units},
    )
    counts = [s.candidates for s in funnel.stages]
    notionals = [s.naive_notional_gbp for s in funnel.stages]
    assert counts == sorted(counts, reverse=True)  # screens only remove
    assert notionals == sorted(notionals, reverse=True)
    assert counts[-1] == len(survivors)
    chosen = select(survivors)
    assert (chosen is None) == (not survivors)
    if chosen is not None:
        assert chosen in survivors
        assert all(c.gap_gbp_per_mwh <= chosen.gap_gbp_per_mwh for c in survivors)
