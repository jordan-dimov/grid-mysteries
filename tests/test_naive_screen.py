from decimal import Decimal

import pytest

from grid_mysteries.investigations.bod_inversion import InversionCandidate
from grid_mysteries.investigations.naive_screen import screen_accepted_actions


def candidate(
    alt_unit: str, alt_price: str, *, accepted_price="100", alt_pair=1
) -> InversionCandidate:
    return InversionCandidate(
        settlement_date="2026-01-05",
        settlement_period=17,
        direction="offer",
        accepted_unit="DEAR",
        accepted_pair_id=1,
        accepted_price_gbp_per_mwh=Decimal(accepted_price),
        accepted_volume_mwh=Decimal("10"),
        unaccepted_unit=alt_unit,
        unaccepted_pair_id=alt_pair,
        unaccepted_price_gbp_per_mwh=Decimal(alt_price),
        unaccepted_max_level_mw=Decimal("5"),
    )


def key(c: InversionCandidate) -> tuple:
    return (
        c.settlement_date,
        c.settlement_period,
        c.direction,
        c.unaccepted_unit,
        c.unaccepted_pair_id,
    )


def test_naive_picks_best_gap_and_filter_falls_back_to_best_survivor() -> None:
    phantom = candidate("PHANTOM", "10")  # gap 90, non-deliverable
    real = candidate("REAL", "60")  # gap 40, survives
    classification = {key(phantom): "non_deliverable", key(real): "not_ruled_out"}

    [action] = screen_accepted_actions([real, phantom], classification)

    assert action.naive_alt_unit == "PHANTOM"
    assert action.naive_gap_gbp_per_mwh == Decimal("90")
    assert action.naive_alt_non_deliverable is True
    assert action.post_gap_gbp_per_mwh == Decimal("40")
    assert action.vanished is False
    assert action.naive_notional_gbp == Decimal("900")
    assert action.post_notional_gbp == Decimal("400")


def test_opportunity_vanishes_when_every_alternative_is_ruled_out() -> None:
    only = candidate("PHANTOM", "10")
    [action] = screen_accepted_actions([only], {key(only): "non_deliverable"})

    assert action.vanished is True
    assert action.post_gap_gbp_per_mwh == Decimal("0")
    assert action.post_notional_gbp == Decimal("0")


def test_equal_gaps_break_ties_by_unit_then_pair() -> None:
    b = candidate("B-UNIT", "10")
    a2 = candidate("A-UNIT", "10", alt_pair=2)
    a1 = candidate("A-UNIT", "10", alt_pair=1)
    classification = dict.fromkeys([key(b), key(a2), key(a1)], "not_ruled_out")

    [action] = screen_accepted_actions([b, a2, a1], classification)

    assert (action.naive_alt_unit, action.naive_alt_pair_id) == ("A-UNIT", 1)


def test_missing_classification_is_an_error_not_deliverable() -> None:
    only = candidate("UNKNOWN", "10")
    with pytest.raises(KeyError):
        screen_accepted_actions([only], {})
