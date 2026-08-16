"""Accepted-action-level screening for Method Study 001B.

Groups Investigation-001-rule inversion candidates by their accepted
action and, per action, picks the naive best-priced alternative and the
best alternative surviving Method Study 001's deliverability
classification. Pure logic; the study script feeds it candidates and the
classification map and computes aggregates.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from grid_mysteries.investigations.bod_inversion import InversionCandidate
from grid_mysteries.investigations.phantom_liquidity import NON_DELIVERABLE

AlternativeKey = tuple[str, int, str, str, int]  # date, period, direction, unit, pair


@dataclass(frozen=True, slots=True)
class ScreenedAction:
    settlement_date: str
    settlement_period: int
    direction: str
    accepted_unit: str
    accepted_pair_id: int
    accepted_volume_mwh: Decimal
    naive_gap_gbp_per_mwh: Decimal
    naive_alt_unit: str
    naive_alt_pair_id: int
    naive_alt_non_deliverable: bool
    post_gap_gbp_per_mwh: Decimal  # zero when every alternative is ruled out
    post_alt_unit: str | None  # best surviving alternative, None when vanished
    post_alt_pair_id: int | None

    @property
    def vanished(self) -> bool:
        return self.post_gap_gbp_per_mwh == 0

    @property
    def naive_notional_gbp(self) -> Decimal:
        return abs(self.accepted_volume_mwh) * self.naive_gap_gbp_per_mwh

    @property
    def post_notional_gbp(self) -> Decimal:
        return abs(self.accepted_volume_mwh) * self.post_gap_gbp_per_mwh


def _preference(candidate: InversionCandidate) -> tuple:
    """Sort key for 'best alternative': largest gap, ties by unit then pair."""
    return (-candidate.gap_gbp_per_mwh, candidate.unaccepted_unit, candidate.unaccepted_pair_id)


def screen_accepted_actions(
    candidates: list[InversionCandidate],
    classification: dict[AlternativeKey, str],
) -> list[ScreenedAction]:
    """One ScreenedAction per accepted action appearing in ``candidates``.

    Every alternative must be present in ``classification``; a missing key
    is an error, never silently treated as deliverable.
    """
    by_action: dict[tuple, list[InversionCandidate]] = {}
    for candidate in candidates:
        action = (
            candidate.settlement_date,
            candidate.settlement_period,
            candidate.direction,
            candidate.accepted_unit,
            candidate.accepted_pair_id,
        )
        by_action.setdefault(action, []).append(candidate)

    actions = []
    for action, alternatives in sorted(by_action.items()):
        ranked = sorted(alternatives, key=_preference)
        naive = ranked[0]

        def alt_key(candidate: InversionCandidate) -> AlternativeKey:
            return (
                candidate.settlement_date,
                candidate.settlement_period,
                candidate.direction,
                candidate.unaccepted_unit,
                candidate.unaccepted_pair_id,
            )

        surviving = [c for c in ranked if classification[alt_key(c)] != NON_DELIVERABLE]
        actions.append(
            ScreenedAction(
                settlement_date=action[0],
                settlement_period=action[1],
                direction=action[2],
                accepted_unit=action[3],
                accepted_pair_id=action[4],
                accepted_volume_mwh=naive.accepted_volume_mwh,
                naive_gap_gbp_per_mwh=naive.gap_gbp_per_mwh,
                naive_alt_unit=naive.unaccepted_unit,
                naive_alt_pair_id=naive.unaccepted_pair_id,
                naive_alt_non_deliverable=classification[alt_key(naive)] == NON_DELIVERABLE,
                post_gap_gbp_per_mwh=(surviving[0].gap_gbp_per_mwh if surviving else Decimal(0)),
                post_alt_unit=surviving[0].unaccepted_unit if surviving else None,
                post_alt_pair_id=surviving[0].unaccepted_pair_id if surviving else None,
            )
        )
    return actions
