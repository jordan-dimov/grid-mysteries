"""Property-based tests: mechanised counterexample search over the
analytical rules. The doctrine asks for boundary cases and
counterexamples; Hypothesis generates them adversarially instead of
relying on the examples we thought of. Permutation-invariance properties
are here deliberately — the 001D determinism defect was exactly a
violation of one."""

from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations.bod_inversion import (
    AcceptedPair,
    SubmittedPair,
    find_inversion_candidates,
)
from grid_mysteries.investigations.exclusion_attribution import (
    ATOMIC_REASON_CATEGORY,
    categorise,
    split_reasons,
)
from grid_mysteries.investigations.naive_screen import screen_accepted_actions
from grid_mysteries.investigations.neso_cells import intensity_by_cell
from grid_mysteries.investigations.phantom_liquidity import (
    LevelExtremes,
    classify,
    headroom_upper_bound,
)
from grid_mysteries.stats import percentile

decimals = st.integers(-10_000, 10_000).map(lambda n: Decimal(n) / 100)
unit_names = st.sampled_from(["U1", "U2", "U3", "U4"])


@st.composite
def unique_submitted_offer_pairs(draw):
    """Unique per (unit, pair) — the contract submitted_pairs() guarantees
    and find_inversion_candidates() now enforces."""
    keys = draw(st.lists(st.tuples(unit_names, st.integers(1, 3)), unique=True, max_size=12))
    return [
        SubmittedPair(
            bm_unit=unit,
            pair_id=pair_id,
            price_gbp_per_mwh=draw(decimals),
            max_level_mw=draw(st.integers(0, 50).map(Decimal)),
        )
        for unit, pair_id in keys
    ]


@given(
    submitted=unique_submitted_offer_pairs(),
    accepted=st.lists(
        st.tuples(unit_names, st.integers(1, 3), decimals).map(
            lambda t: AcceptedPair(t[0], t[1], t[2])
        ),
        max_size=8,
    ),
    seed=st.randoms(),
)
def test_inversion_candidates_are_well_formed_and_order_invariant(submitted, accepted, seed):
    def run(sub, acc):
        return find_inversion_candidates(
            settlement_date="2026-01-05",
            settlement_period=1,
            direction="offer",
            submitted=sub,
            accepted=acc,
        )

    candidates = run(submitted, accepted)
    for c in candidates:
        assert c.gap_gbp_per_mwh > 0
        assert c.accepted_unit != c.unaccepted_unit
        assert c.unaccepted_max_level_mw >= 1

    shuffled_submitted, shuffled_accepted = list(submitted), list(accepted)
    seed.shuffle(shuffled_submitted)
    seed.shuffle(shuffled_accepted)
    # List equality, not set equality: output order itself is canonical.
    assert run(shuffled_submitted, shuffled_accepted) == candidates


@given(
    rows=st.lists(
        st.tuples(unit_names, st.integers(1, 6), decimals, st.booleans()).map(
            lambda t: {
                "settlement_date": "2026-08-06",
                "settlement_period": t[1],
                "direction": "bid",
                "bm_unit": t[0],
                "max_gap_gbp_per_mwh": str(t[2]),
                "classification": "non_deliverable" if t[3] else "not_ruled_out",
            }
        ),
        max_size=15,
    ),
    seed=st.randoms(),
)
def test_cell_intensity_is_permutation_invariant_and_post_never_exceeds_naive(rows, seed):
    naive, post = intensity_by_cell(rows, {})
    for cell, value in post.items():
        assert value <= naive[cell]

    shuffled = list(rows)
    seed.shuffle(shuffled)
    assert intensity_by_cell(shuffled, {}) == (naive, post)


@given(reasons=st.lists(st.sampled_from(sorted(ATOMIC_REASON_CATEGORY)), min_size=1, max_size=4))
def test_compound_reason_strings_round_trip_through_the_splitter(reasons):
    compound = ", ".join(reasons)
    assert split_reasons(compound) == reasons
    assert len(categorise(compound)) == len(reasons)


@given(
    fpn_low=decimals,
    fpn_span=st.integers(0, 100).map(Decimal),
    floor=decimals,
    raise_by=st.integers(0, 100).map(Decimal),
)
def test_bid_headroom_bound_is_monotone_in_fpn(fpn_low, fpn_span, floor, raise_by):
    def bound(extra):
        return headroom_upper_bound(
            "bid",
            fpn=LevelExtremes(fpn_low, fpn_low + fpn_span + extra),
            mels=None,
            mils=LevelExtremes(floor, floor),
            generation_capacity=None,
            demand_capacity=None,
        )

    lower, higher = bound(Decimal(0)), bound(raise_by)
    assert higher >= lower
    # Raising the FPN ceiling can never turn a survivor into non-deliverable.
    if classify(lower) == "not_ruled_out":
        assert classify(higher) == "not_ruled_out"


@given(values=st.lists(decimals, min_size=1, max_size=30), fraction=st.floats(0, 0.999))
def test_percentile_returns_a_member_and_is_monotone(values, fraction):
    ordered = sorted(values)
    result = percentile(ordered, fraction)
    assert result in values
    assert percentile(ordered, 0.999) >= result >= percentile(ordered, 0.0)


@given(
    candidates_seed=st.lists(
        st.tuples(unit_names, unit_names, decimals, decimals, st.booleans()),
        max_size=10,
    ),
    seed=st.randoms(),
)
def test_screen_post_gap_never_exceeds_naive_gap_and_is_order_invariant(candidates_seed, seed):
    from grid_mysteries.investigations.bod_inversion import InversionCandidate

    candidates, classification = [], {}
    for accepted_unit, alt_unit, price, gap_extra, phantom in candidates_seed:
        if accepted_unit == alt_unit:
            continue
        candidate = InversionCandidate(
            settlement_date="2026-01-05",
            settlement_period=1,
            direction="offer",
            accepted_unit=accepted_unit,
            accepted_pair_id=1,
            accepted_price_gbp_per_mwh=price + abs(gap_extra) + 1,
            accepted_volume_mwh=Decimal("10"),
            unaccepted_unit=alt_unit,
            unaccepted_pair_id=1,
            unaccepted_price_gbp_per_mwh=price,
            unaccepted_max_level_mw=Decimal("5"),
        )
        candidates.append(candidate)
        classification[("2026-01-05", 1, "offer", alt_unit, 1)] = (
            "non_deliverable" if phantom else "not_ruled_out"
        )

    actions = screen_accepted_actions(candidates, classification)
    for action in actions:
        assert Decimal(0) <= action.post_gap_gbp_per_mwh <= action.naive_gap_gbp_per_mwh

    shuffled = list(candidates)
    seed.shuffle(shuffled)
    assert screen_accepted_actions(shuffled, classification) == actions


def test_duplicate_submitted_pairs_are_refused_not_silently_resolved():
    import pytest

    pair = SubmittedPair("U1", 1, Decimal("50"), Decimal("10"))
    with pytest.raises(ValueError, match="unique per"):
        find_inversion_candidates(
            settlement_date="2026-01-05",
            settlement_period=1,
            direction="offer",
            submitted=[pair, pair],
            accepted=[],
        )


@given(
    submitted=unique_submitted_offer_pairs(),
    accepted=st.lists(
        st.tuples(unit_names, st.integers(1, 3), decimals).map(
            lambda t: AcceptedPair(t[0], t[1], t[2])
        ),
        max_size=8,
    ),
    seed=st.randoms(),
)
def test_ranking_is_invariant_under_candidate_permutation(submitted, accepted, seed):
    from grid_mysteries.investigations.bod_inversion import rank_candidates

    candidates = find_inversion_candidates(
        settlement_date="2026-01-05",
        settlement_period=1,
        direction="offer",
        submitted=submitted,
        accepted=accepted,
    )
    shuffled = list(candidates)
    seed.shuffle(shuffled)
    assert rank_candidates(shuffled) == rank_candidates(candidates)


@given(price_int=st.integers(-1000, 1000), scale=st.integers(0, 4))
def test_decimal_scale_variants_cannot_alter_conclusions(price_int, scale):
    """1.0 and 1.00 are the same price; no analytical path may distinguish
    them."""
    from grid_mysteries.investigations.bod_inversion import submitted_pairs

    plain = Decimal(price_int)
    rescaled = plain.quantize(Decimal(1).scaleb(-scale)) if scale else plain

    def bod(price):
        return [
            {"bmUnit": "U1", "pairId": 1, "bid": 0, "offer": price, "levelFrom": 10, "levelTo": 10},
            {
                "bmUnit": "U1",
                "pairId": 1,
                "bid": 0,
                "offer": rescaled,
                "levelFrom": 12,
                "levelTo": 12,
            },
        ]

    # Same-value, different-scale slices must not be treated as a price
    # conflict (which would silently drop the pair).
    assert submitted_pairs(bod(plain), "offer") == submitted_pairs(bod(rescaled), "offer")
    assert len(submitted_pairs(bod(plain), "offer")) == 1
