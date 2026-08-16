from decimal import Decimal

from grid_mysteries.investigations.apparent_dispatch import (
    DispatchCandidate,
    find_apparent_gaps,
)


def test_lower_priced_unaccepted_action_is_a_mystery_not_a_conclusion() -> None:
    candidates = [
        DispatchCandidate("cheap", Decimal("71"), Decimal("18"), accepted=False),
        DispatchCandidate("dear", Decimal("182"), Decimal("20"), accepted=True),
    ]

    gaps = find_apparent_gaps(candidates)

    assert len(gaps) == 1
    assert gaps[0].price_gap_gbp_per_mwh == Decimal("111")
