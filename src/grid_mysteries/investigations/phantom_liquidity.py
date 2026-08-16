"""Conservative public-state deliverability bounds for BM alternatives.

Method Study 001 asks how much of the apparent "better-priced alternative"
liquidity in Bid-Offer data was physically deliverable at all. This module
holds the pure classification logic; the study script feeds it pinned
records.

The test is deliberately one-sided. For a settlement period we compute an
*upper bound* on the unit's deliverable volume in the direction concerned,
using endpoint extremes of the public physical state across the half hour:

- bids (reduce output): ``max FPN − floor``, where the floor is the lowest
  Minimum/Maximum Import Level endpoint (MILS), falling back to the
  unit's registered demand capacity (0 for units that cannot import);
- offers (increase output): ``ceiling − min FPN``, where the ceiling is the
  highest Maximum Export Level endpoint (MELS), falling back to the
  registered generation capacity.

Because the bound pairs the *most generous* endpoints across the period, a
bound of zero or less proves there was no instant with positive headroom:
classification ``non_deliverable`` is airtight. Anything else is
``not_ruled_out`` — explicitly *not* a claim of executability, since
timing, dynamics, prior instructions and constraint location remain
untested. Missing public state always yields ``not_ruled_out``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from grid_mysteries.investigations.bod_inversion import Direction, _decimal

NON_DELIVERABLE: Final = "non_deliverable"
NOT_RULED_OUT: Final = "not_ruled_out"
Classification = Literal["non_deliverable", "not_ruled_out"]


@dataclass(frozen=True, slots=True)
class LevelExtremes:
    minimum: Decimal
    maximum: Decimal


def level_extremes(records: list[dict]) -> dict[str, LevelExtremes]:
    """Per-BMU min/max over all level endpoints of one period's records."""
    extremes: dict[str, LevelExtremes] = {}
    for record in records:
        unit = str(record["bmUnit"])
        low = min(_decimal(record["levelFrom"]), _decimal(record["levelTo"]))
        high = max(_decimal(record["levelFrom"]), _decimal(record["levelTo"]))
        seen = extremes.get(unit)
        if seen is None:
            extremes[unit] = LevelExtremes(low, high)
        else:
            extremes[unit] = LevelExtremes(min(seen.minimum, low), max(seen.maximum, high))
    return extremes


def headroom_upper_bound(
    direction: Direction,
    *,
    fpn: LevelExtremes | None,
    mels: LevelExtremes | None,
    mils: LevelExtremes | None,
    generation_capacity: Decimal | None,
    demand_capacity: Decimal | None,
) -> Decimal | None:
    """Upper bound on deliverable MW in ``direction``; None = unbounded."""
    if fpn is None:
        return None
    if direction == "bid":
        if mils is not None:
            floor = mils.minimum
        elif demand_capacity is not None:
            floor = min(Decimal(0), demand_capacity)
        else:
            return None
        return fpn.maximum - floor
    if mels is not None:
        ceiling = mels.maximum
    elif generation_capacity is not None:
        ceiling = generation_capacity
    else:
        return None
    return ceiling - fpn.minimum


def classify(headroom: Decimal | None) -> Classification:
    """``non_deliverable`` only when the upper bound proves zero headroom."""
    if headroom is not None and headroom <= 0:
        return NON_DELIVERABLE
    return NOT_RULED_OUT
