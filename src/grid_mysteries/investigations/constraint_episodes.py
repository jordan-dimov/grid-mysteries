"""Published constraint-cost episodes and repeat-curtailment cycles.

The most literal implementation of Investigation 003's frozen
declaration. Implementation contracts (not constitutional amendments):

- **Episode**: per constraint group, a maximal run of consecutive
  settlement dates with non-zero published daily outturn cost (literal
  "non-zero": any sign). Gaps split runs and stay visible as separate
  episodes.
- **Exporting FPN**: a unit presents an export schedule in a period iff
  any final-PN slice overlapping the period reaches a strictly positive
  level at either endpoint — a profile crossing zero counts as export if
  it is positive at any instant.
- **Storage bid-down**: the unit has non-zero accepted DISPTAV
  ``Original`` volume on any negative (bid) pair in the period. Duplicate
  or overlapping acceptance rows cannot double-count: bid-down is a
  per-period boolean, not a row count.
- **Cycle scan**: after a bid-down in period t, the next export period
  strictly after t re-arms the signature; a bid-down in that same or any
  later period completes one cycle and becomes the new t. Deterministic,
  order-canonical, and counts at most ``|bid-down periods| − 1`` cycles.
- **Missing PN** for a classified storage unit means *no observable
  cycles*, never "not storage" — coverage is reported, the unit stays in
  the declared universe.
- **Selection**: highest episode score; ties by greater storage bid-down
  MWh, earlier start date, constraint-group name.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

PeriodKey = tuple[str, int]  # (settlement date, settlement period)


@dataclass(frozen=True, slots=True)
class Episode:
    constraint_group: str
    dates: tuple[str, ...]  # consecutive settlement dates

    @property
    def start(self) -> str:
        return self.dates[0]

    @property
    def end(self) -> str:
        return self.dates[-1]


def episodes(cost_rows: list[dict]) -> list[Episode]:
    """Maximal consecutive-date non-zero-cost runs per constraint group.

    Rows carry ``Settlement Date``, ``Constraint Group`` and
    ``Daily Cost (GBP)`` (strings, as published). Output order is
    canonical (group, start date) regardless of input order.
    """
    costly: dict[str, set[str]] = {}
    for row in cost_rows:
        cost = Decimal(str(row["Daily Cost (GBP)"]).strip() or "0")
        if cost != 0:
            costly.setdefault(str(row["Constraint Group"]), set()).add(
                str(row["Settlement Date"])[:10]
            )
    result = []
    for group in sorted(costly):
        run: list[str] = []
        for day in sorted(costly[group]):
            if run and date.fromisoformat(day) != date.fromisoformat(run[-1]) + timedelta(days=1):
                result.append(Episode(group, tuple(run)))
                run = []
            run.append(day)
        if run:
            result.append(Episode(group, tuple(run)))
    return sorted(result, key=lambda e: (e.constraint_group, e.start))


def repeat_curtailment_cycles(
    bid_down_periods: set[PeriodKey], export_periods: set[PeriodKey]
) -> int:
    """Count repeat-curtailment cycles per the frozen wording.

    (a) bid-down at t; (b) export presented in a strictly later period;
    (c) bid-down again in that period or later. Each (b)+(c) after the
    first bid-down is one cycle. Sets in, so duplicates cannot count.
    """
    timeline = sorted(bid_down_periods | export_periods)
    cycles = 0
    armed = False  # a bid-down has occurred; waiting for a later export
    exported = False  # a later export has occurred; waiting for a bid-down
    for key in timeline:
        is_export = key in export_periods
        is_bid_down = key in bid_down_periods
        if not armed:
            if is_bid_down:
                armed = True
            continue
        if not exported:
            if is_export:
                exported = True
            else:
                continue
        if is_bid_down:
            cycles += 1
            exported = False
    return cycles


@dataclass(frozen=True, slots=True)
class ScoredEpisode:
    episode: Episode
    score: int
    storage_bid_down_mwh: Decimal


def select(scored: list[ScoredEpisode]) -> ScoredEpisode | None:
    """The declared selection: highest score, then greater bid-down MWh,
    then earlier start, then group name. None iff no positive score."""
    positive = [s for s in scored if s.score > 0]
    if not positive:
        return None
    return min(
        positive,
        key=lambda s: (
            -s.score,
            -s.storage_bid_down_mwh,
            s.episode.start,
            s.episode.constraint_group,
        ),
    )
