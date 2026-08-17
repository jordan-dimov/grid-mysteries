"""GC0166 duration-aware delivery envelopes (MDO/MDB) with vintage rules.

BESS Study 001's declared semantics, implemented as pure functions:

- **Vintage resolution**: at any instant, the applicable record among
  those covering it with ``publish_time`` ≤ the vintage cutoff is the one
  with the greatest ``(publish_time, serial_number)``, with a full
  content tie-break making the order total.
- **Projection**: applicable intervals clip to the settlement period; a
  segment contributes ``max(|level_from|, |level_to|) × hours`` — a
  deliberately generous upper bound, so exclusions stay airtight.
- **Reconstructable**: the union of applicable intervals must cover the
  full period, else the period is *unknown* (``None``) — never
  interpolated, never partially credited.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class EnvelopeRecord:
    time_from: datetime
    time_to: datetime
    level_from: Decimal
    level_to: Decimal
    publish_time: datetime
    serial_number: str


def _segment_boundaries(
    records: list[EnvelopeRecord], period_start: datetime, period_end: datetime
) -> list[datetime]:
    boundaries = {period_start, period_end}
    for record in records:
        for instant in (record.time_from, record.time_to):
            if period_start < instant < period_end:
                boundaries.add(instant)
    return sorted(boundaries)


def resolve_segments(
    records: list[EnvelopeRecord],
    period_start: datetime,
    period_end: datetime,
    cutoff: datetime | None,
) -> list[tuple[datetime, datetime, EnvelopeRecord]]:
    """The winning record per sub-interval of the period, under the cutoff.

    Sub-intervals with no applicable record are absent from the result;
    callers decide what a coverage gap means. Output is canonical
    (chronological) regardless of input order.
    """
    applicable = [r for r in records if cutoff is None or r.publish_time <= cutoff]
    boundaries = _segment_boundaries(applicable, period_start, period_end)
    segments = []
    for start, end in zip(boundaries, boundaries[1:], strict=False):
        covering = [r for r in applicable if r.time_from <= start and r.time_to >= end]
        if covering:
            winner = max(
                covering,
                key=lambda r: (
                    r.publish_time,
                    r.serial_number,
                    # Content tie-break keeps the order total even for
                    # pathological duplicate vintage keys (found by
                    # property testing): resolution must never depend on
                    # input order.
                    r.time_from,
                    r.time_to,
                    r.level_from,
                    r.level_to,
                ),
            )
            segments.append((start, end, winner))
    return segments


def _seconds(start: datetime, end: datetime) -> int:
    # Exact integer seconds: coverage equality must never depend on
    # Decimal division rounding.
    return int((end - start).total_seconds())


def coverage_fraction(
    records: list[EnvelopeRecord],
    period_start: datetime,
    period_end: datetime,
    cutoff: datetime | None,
) -> Decimal:
    covered = sum(
        _seconds(start, end)
        for start, end, _ in resolve_segments(records, period_start, period_end, cutoff)
    )
    return Decimal(covered) / Decimal(_seconds(period_start, period_end))


def energy_bound_mwh(
    records: list[EnvelopeRecord],
    period_start: datetime,
    period_end: datetime,
    cutoff: datetime | None,
) -> Decimal | None:
    """Generous upper bound on deliverable energy over the period, or None
    when the period is not fully reconstructable under the cutoff."""
    segments = resolve_segments(records, period_start, period_end, cutoff)
    covered = sum(_seconds(start, end) for start, end, _ in segments)
    if covered != _seconds(period_start, period_end):
        return None
    return sum(
        (
            max(abs(record.level_from), abs(record.level_to))
            * Decimal(_seconds(start, end))
            / Decimal(3600)
            for start, end, record in segments
        ),
        Decimal(0),
    )
