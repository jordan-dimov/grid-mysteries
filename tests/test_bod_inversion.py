from decimal import Decimal

import pytest

from grid_mysteries.investigations.bod_inversion import (
    accepted_pairs,
    find_inversion_candidates,
    rank_candidates,
    submitted_pairs,
)


def bod(bm_unit: str, pair_id: int, *, bid: str, offer: str, level: str) -> dict:
    return {
        "bmUnit": bm_unit,
        "pairId": pair_id,
        "bid": Decimal(bid),
        "offer": Decimal(offer),
        "levelFrom": Decimal(level),
        "levelTo": Decimal(level),
    }


def disptav(bm_unit: str, data_type: str = "Original", **volumes: str) -> dict:
    return {
        "bmUnit": bm_unit,
        "dataType": data_type,
        "pairVolumes": {field: Decimal(value) for field, value in volumes.items()},
    }


def test_offer_inversion_is_found_with_exact_decimal_gap() -> None:
    submitted = submitted_pairs(
        [
            bod("DEAR", 1, bid="10", offer="182.50", level="50"),
            bod("CHEAP", 1, bid="5", offer="71.25", level="30"),
        ],
        "offer",
    )
    accepted = accepted_pairs([disptav("DEAR", positive1="12.5")], "offer")

    candidates = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=17,
        direction="offer",
        submitted=submitted,
        accepted=accepted,
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.accepted_unit == "DEAR"
    assert candidate.unaccepted_unit == "CHEAP"
    assert candidate.gap_gbp_per_mwh == Decimal("111.25")


def test_bid_inversion_uses_bid_prices_and_reversed_ordering() -> None:
    # For bids NESO is paid; accepting a lower-priced bid while a
    # higher-priced bid sat unaccepted is the apparent inversion.
    submitted = submitted_pairs(
        [
            bod("LOWPAY", -1, bid="-5", offer="99", level="40"),
            bod("HIGHPAY", -1, bid="45", offer="99", level="40"),
        ],
        "bid",
    )
    accepted = accepted_pairs([disptav("LOWPAY", negative1="-8")], "bid")

    candidates = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=17,
        direction="bid",
        submitted=submitted,
        accepted=accepted,
    )

    assert len(candidates) == 1
    assert candidates[0].accepted_unit == "LOWPAY"
    assert candidates[0].unaccepted_unit == "HIGHPAY"
    assert candidates[0].gap_gbp_per_mwh == Decimal("50")


def test_explicit_zero_volume_still_counts_as_unaccepted() -> None:
    submitted = submitted_pairs(
        [
            bod("DEAR", 1, bid="10", offer="100", level="50"),
            bod("CHEAP", 1, bid="5", offer="40", level="30"),
        ],
        "offer",
    )
    accepted_records = [
        disptav("DEAR", positive1="10"),
        disptav("CHEAP", positive1="0"),
    ]
    accepted = accepted_pairs(accepted_records, "offer")

    candidates = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=1,
        direction="offer",
        submitted=submitted,
        accepted=accepted,
    )

    assert [c.unaccepted_unit for c in candidates] == ["CHEAP"]


def test_de_minimis_acceptance_qualifies_as_neither_side() -> None:
    submitted = submitted_pairs(
        [
            bod("DEAR", 1, bid="10", offer="100", level="50"),
            bod("TRACE", 1, bid="5", offer="40", level="30"),
        ],
        "offer",
    )
    accepted = accepted_pairs(
        [disptav("DEAR", positive1="10"), disptav("TRACE", positive1="0.001")],
        "offer",
    )

    candidates = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=1,
        direction="offer",
        submitted=submitted,
        accepted=accepted,
    )

    assert candidates == []


def test_small_level_band_does_not_qualify_as_available() -> None:
    submitted = submitted_pairs(
        [
            bod("DEAR", 1, bid="10", offer="100", level="50"),
            bod("TINY", 1, bid="5", offer="40", level="0.4"),
        ],
        "offer",
    )
    accepted = accepted_pairs([disptav("DEAR", positive1="10")], "offer")

    candidates = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=1,
        direction="offer",
        submitted=submitted,
        accepted=accepted,
    )

    assert candidates == []


def test_same_unit_ladder_is_not_an_inversion() -> None:
    submitted = submitted_pairs(
        [
            bod("UNIT", 1, bid="10", offer="40", level="50"),
            bod("UNIT", 2, bid="10", offer="100", level="50"),
        ],
        "offer",
    )
    accepted = accepted_pairs([disptav("UNIT", positive2="10")], "offer")

    candidates = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=1,
        direction="offer",
        submitted=submitted,
        accepted=accepted,
    )

    assert candidates == []


def test_ranking_is_deterministic_gap_then_chronology_then_units() -> None:
    submitted_a = submitted_pairs(
        [
            bod("DEAR", 1, bid="10", offer="100", level="50"),
            bod("CHEAP-B", 1, bid="5", offer="40", level="30"),
            bod("CHEAP-A", 1, bid="5", offer="40", level="30"),
        ],
        "offer",
    )
    accepted_a = accepted_pairs([disptav("DEAR", positive1="10")], "offer")
    later = find_inversion_candidates(
        settlement_date="2026-01-06",
        settlement_period=1,
        direction="offer",
        submitted=submitted_a,
        accepted=accepted_a,
    )
    earlier = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=30,
        direction="offer",
        submitted=submitted_a,
        accepted=accepted_a,
    )

    ranked = rank_candidates(later + earlier)

    assert [(c.settlement_date, c.unaccepted_unit) for c in ranked] == [
        ("2026-01-05", "CHEAP-A"),
        ("2026-01-05", "CHEAP-B"),
        ("2026-01-06", "CHEAP-A"),
        ("2026-01-06", "CHEAP-B"),
    ]


def test_binary_floats_are_rejected() -> None:
    with pytest.raises(TypeError, match="parse_float=Decimal"):
        submitted_pairs(
            [{"bmUnit": "U", "pairId": 1, "offer": 100.1, "levelFrom": 0, "levelTo": 0}],
            "offer",
        )


def test_null_priced_and_wrong_direction_pairs_are_skipped() -> None:
    submitted = submitted_pairs(
        [
            {"bmUnit": "U", "pairId": 1, "offer": None, "levelFrom": 5, "levelTo": 5},
            bod("V", -1, bid="5", offer="40", level="30"),
        ],
        "offer",
    )
    assert submitted == []


def test_inconsistent_price_slices_drop_the_pair() -> None:
    records = [
        bod("U", 1, bid="10", offer="40", level="50"),
        bod("U", 1, bid="10", offer="45", level="60"),
        bod("W", 1, bid="10", offer="80", level="20"),
    ]
    pairs = submitted_pairs(records, "offer")
    assert [(p.bm_unit, str(p.price_gbp_per_mwh)) for p in pairs] == [("W", "80")]
