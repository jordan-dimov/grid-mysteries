from decimal import Decimal

from grid_mysteries.investigations.phantom_liquidity import (
    NON_DELIVERABLE,
    NOT_RULED_OUT,
    LevelExtremes,
    classify,
    headroom_upper_bound,
    level_extremes,
)


def ext(low: str, high: str) -> LevelExtremes:
    return LevelExtremes(Decimal(low), Decimal(high))


def test_level_extremes_span_all_slices_and_endpoints() -> None:
    records = [
        {"bmUnit": "U", "levelFrom": Decimal("5"), "levelTo": Decimal("3")},
        {"bmUnit": "U", "levelFrom": Decimal("3"), "levelTo": Decimal("8")},
        {"bmUnit": "V", "levelFrom": Decimal("0"), "levelTo": Decimal("0")},
    ]
    extremes = level_extremes(records)
    assert extremes["U"] == ext("3", "8")
    assert extremes["V"] == ext("0", "0")


def test_bid_with_zero_fpn_and_zero_import_floor_is_non_deliverable() -> None:
    bound = headroom_upper_bound(
        "bid",
        fpn=ext("0", "0"),
        mels=ext("0", "0"),
        mils=ext("0", "0"),
        generation_capacity=Decimal("50"),
        demand_capacity=Decimal("0"),
    )
    assert bound == Decimal("0")
    assert classify(bound) == NON_DELIVERABLE


def test_bid_with_running_unit_is_not_ruled_out() -> None:
    bound = headroom_upper_bound(
        "bid",
        fpn=ext("0", "5"),
        mels=None,
        mils=ext("0", "0"),
        generation_capacity=None,
        demand_capacity=None,
    )
    assert bound == Decimal("5")
    assert classify(bound) == NOT_RULED_OUT


def test_bid_missing_mils_falls_back_to_demand_capacity() -> None:
    # A unit that can import (negative demand capacity) keeps downward room
    # even at FPN 0: the conservative floor widens, never narrows.
    bound = headroom_upper_bound(
        "bid",
        fpn=ext("0", "0"),
        mels=None,
        mils=None,
        generation_capacity=None,
        demand_capacity=Decimal("-10"),
    )
    assert bound == Decimal("10")
    assert classify(bound) == NOT_RULED_OUT


def test_offer_at_full_export_limit_is_non_deliverable() -> None:
    bound = headroom_upper_bound(
        "offer",
        fpn=ext("50", "50"),
        mels=ext("50", "50"),
        mils=None,
        generation_capacity=Decimal("60"),
        demand_capacity=None,
    )
    assert bound == Decimal("0")
    assert classify(bound) == NON_DELIVERABLE


def test_offer_missing_mels_falls_back_to_generation_capacity() -> None:
    bound = headroom_upper_bound(
        "offer",
        fpn=ext("30", "40"),
        mels=None,
        mils=None,
        generation_capacity=Decimal("50"),
        demand_capacity=None,
    )
    assert bound == Decimal("20")
    assert classify(bound) == NOT_RULED_OUT


def test_missing_public_state_never_rules_out() -> None:
    assert (
        headroom_upper_bound(
            "bid",
            fpn=None,
            mels=None,
            mils=ext("0", "0"),
            generation_capacity=None,
            demand_capacity=Decimal("0"),
        )
        is None
    )
    assert (
        headroom_upper_bound(
            "offer",
            fpn=ext("0", "0"),
            mels=None,
            mils=None,
            generation_capacity=None,
            demand_capacity=None,
        )
        is None
    )
    assert classify(None) == NOT_RULED_OUT
