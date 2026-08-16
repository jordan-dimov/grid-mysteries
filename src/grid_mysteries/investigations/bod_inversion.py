"""Deterministic selection of apparent Bid-Offer price-order inversions.

Inputs are records from two official Elexon datasets for one settlement
period:

- **BOD** (bid-offer data): the pairs each BM Unit submitted, with a bid
  price and an offer price in GBP/MWh and a MW level band.
- **DISPTAV** (derived BM Unit total acceptance volumes): the accepted
  volume per bid-offer pair, in MWh, as computed by settlement.

An *apparent inversion* is a pair of actions in the same settlement period
and same direction where the economically better-priced submitted pair was
not accepted at all while a worse-priced pair was accepted:

- offers (pair id >= 1, priced at the offer price, NESO pays): an accepted
  offer priced above an entirely unaccepted cheaper offer;
- bids (pair id <= -1, priced at the bid price, NESO is paid): an accepted
  bid priced below an entirely unaccepted higher-priced bid.

This module makes no claim that an inversion is an error. Location,
dynamics, prior instructions, system needs and non-public state can all
explain one. The output is a deterministically ranked queue of mysteries.

All prices and volumes must arrive as `Decimal`, `int` or numeric strings.
Binary floats are rejected so a lossy JSON load cannot weaken a claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Literal

Direction = Literal["bid", "offer"]

#: Accepted volumes smaller than this (MWh, absolute) are treated as
#: settlement noise, not as an acceptance. Declared before any data was seen.
DEFAULT_MIN_ACCEPTED_MWH = Decimal("0.01")

#: Submitted pairs whose level band never reaches this many MW (absolute) do
#: not qualify as an available alternative. Declared before any data was seen.
DEFAULT_MIN_AVAILABLE_MW = Decimal("1")


def _decimal(value: object) -> Decimal:
    if isinstance(value, float):
        raise TypeError(
            "binary float rejected; load JSON with parse_float=Decimal so prices stay exact"
        )
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | str):
        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise ValueError(f"not a decimal value: {value!r}") from error
    raise TypeError(f"not a decimal value: {value!r}")


@dataclass(frozen=True, slots=True)
class SubmittedPair:
    bm_unit: str
    pair_id: int
    price_gbp_per_mwh: Decimal
    max_level_mw: Decimal


@dataclass(frozen=True, slots=True)
class AcceptedPair:
    bm_unit: str
    pair_id: int
    volume_mwh: Decimal


@dataclass(frozen=True, slots=True)
class InversionCandidate:
    settlement_date: str
    settlement_period: int
    direction: Direction
    accepted_unit: str
    accepted_pair_id: int
    accepted_price_gbp_per_mwh: Decimal
    accepted_volume_mwh: Decimal
    unaccepted_unit: str
    unaccepted_pair_id: int
    unaccepted_price_gbp_per_mwh: Decimal
    unaccepted_max_level_mw: Decimal

    @property
    def gap_gbp_per_mwh(self) -> Decimal:
        """Positive price advantage of the unaccepted pair, in GBP/MWh."""
        if self.direction == "offer":
            return self.accepted_price_gbp_per_mwh - self.unaccepted_price_gbp_per_mwh
        return self.unaccepted_price_gbp_per_mwh - self.accepted_price_gbp_per_mwh


def submitted_pairs(bod_records: list[dict], direction: Direction) -> list[SubmittedPair]:
    """Parse one period's BOD records for one direction.

    A record may appear once per level slice within the period; the pair's
    availability is the largest absolute level across slices. A pair whose
    price differs between slices of the same period is malformed and dropped.
    """
    price_field = "offer" if direction == "offer" else "bid"
    by_pair: dict[tuple[str, int], SubmittedPair] = {}
    malformed: set[tuple[str, int]] = set()

    for record in bod_records:
        pair_id = int(record["pairId"])
        if (direction == "offer") != (pair_id > 0):
            continue
        if record.get(price_field) is None:
            continue
        key = (str(record["bmUnit"]), pair_id)
        price = _decimal(record[price_field])
        level = max(abs(_decimal(record["levelFrom"])), abs(_decimal(record["levelTo"])))
        seen = by_pair.get(key)
        if seen is None:
            by_pair[key] = SubmittedPair(key[0], pair_id, price, level)
        elif seen.price_gbp_per_mwh != price:
            malformed.add(key)
        elif level > seen.max_level_mw:
            by_pair[key] = SubmittedPair(key[0], pair_id, price, level)

    return [pair for key, pair in by_pair.items() if key not in malformed]


_PAIR_VOLUME_FIELDS = {
    "offer": [(pair_id, f"positive{pair_id}") for pair_id in range(1, 7)],
    "bid": [(-pair_id, f"negative{pair_id}") for pair_id in range(1, 7)],
}


def accepted_pairs(disptav_records: list[dict], direction: Direction) -> list[AcceptedPair]:
    """Parse one period's DISPTAV records for one direction.

    Only ``dataType == "Original"`` rows are used: total accepted volumes
    before tagging and repricing, which is the acceptance fact itself.
    """
    accepted = []
    for record in disptav_records:
        if record.get("dataType") != "Original":
            continue
        pair_volumes = record.get("pairVolumes") or {}
        for pair_id, field in _PAIR_VOLUME_FIELDS[direction]:
            volume = pair_volumes.get(field)
            if volume is None:
                continue
            volume = _decimal(volume)
            if volume != 0:
                accepted.append(AcceptedPair(str(record["bmUnit"]), pair_id, volume))
    return accepted


def find_inversion_candidates(
    *,
    settlement_date: str,
    settlement_period: int,
    direction: Direction,
    submitted: list[SubmittedPair],
    accepted: list[AcceptedPair],
    min_accepted_mwh: Decimal = DEFAULT_MIN_ACCEPTED_MWH,
    min_available_mw: Decimal = DEFAULT_MIN_AVAILABLE_MW,
) -> list[InversionCandidate]:
    """Enumerate apparent inversions for one settlement period and direction."""
    accepted_volume_by_pair = {(a.bm_unit, a.pair_id): a.volume_mwh for a in accepted}
    accepted_units_pairs = {
        key for key, volume in accepted_volume_by_pair.items() if abs(volume) >= min_accepted_mwh
    }
    price_by_pair = {(p.bm_unit, p.pair_id): p for p in submitted}

    # A pair is unaccepted only if its accepted volume is absent or exactly
    # zero; volumes below the de-minimis threshold qualify as neither side.
    unaccepted = [
        pair
        for pair in submitted
        if accepted_volume_by_pair.get((pair.bm_unit, pair.pair_id), Decimal(0)) == 0
        and pair.max_level_mw >= min_available_mw
    ]

    candidates = []
    for accepted_key in sorted(accepted_units_pairs):
        accepted_pair = price_by_pair.get(accepted_key)
        if accepted_pair is None:
            continue
        for unaccepted_pair in unaccepted:
            if unaccepted_pair.bm_unit == accepted_pair.bm_unit:
                continue
            candidate = InversionCandidate(
                settlement_date=settlement_date,
                settlement_period=settlement_period,
                direction=direction,
                accepted_unit=accepted_pair.bm_unit,
                accepted_pair_id=accepted_pair.pair_id,
                accepted_price_gbp_per_mwh=accepted_pair.price_gbp_per_mwh,
                accepted_volume_mwh=accepted_volume_by_pair[accepted_key],
                unaccepted_unit=unaccepted_pair.bm_unit,
                unaccepted_pair_id=unaccepted_pair.pair_id,
                unaccepted_price_gbp_per_mwh=unaccepted_pair.price_gbp_per_mwh,
                unaccepted_max_level_mw=unaccepted_pair.max_level_mw,
            )
            if candidate.gap_gbp_per_mwh > 0:
                candidates.append(candidate)
    return candidates


def rank_candidates(candidates: list[InversionCandidate]) -> list[InversionCandidate]:
    """Deterministic ranking: largest gap first, ties broken by chronology
    then unit identifiers, so the same inputs always select the same case."""
    return sorted(
        candidates,
        key=lambda c: (
            -c.gap_gbp_per_mwh,
            c.settlement_date,
            c.settlement_period,
            c.direction,
            c.accepted_unit,
            c.accepted_pair_id,
            c.unaccepted_unit,
            c.unaccepted_pair_id,
        ),
    )
