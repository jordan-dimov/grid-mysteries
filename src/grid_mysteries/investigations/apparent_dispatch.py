from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DispatchCandidate:
    unit: str
    price_gbp_per_mwh: Decimal
    volume_mw: Decimal
    accepted: bool


@dataclass(frozen=True, slots=True)
class ApparentDispatchGap:
    cheaper: DispatchCandidate
    dearer: DispatchCandidate

    @property
    def price_gap_gbp_per_mwh(self) -> Decimal:
        return self.dearer.price_gbp_per_mwh - self.cheaper.price_gbp_per_mwh


def find_apparent_gaps(candidates: list[DispatchCandidate]) -> list[ApparentDispatchGap]:
    """Return price-order inversions only.

    This is deliberately *not* a claim of inefficient dispatch. Location,
    dynamics, prior instructions, system needs and missing public state can all
    explain an apparent inversion. The output is a queue of mysteries to test.
    """
    accepted = [candidate for candidate in candidates if candidate.accepted]
    skipped = [candidate for candidate in candidates if not candidate.accepted]

    return [
        ApparentDispatchGap(cheaper=cheap, dearer=dear)
        for cheap in skipped
        for dear in accepted
        if cheap.price_gbp_per_mwh < dear.price_gbp_per_mwh
    ]
