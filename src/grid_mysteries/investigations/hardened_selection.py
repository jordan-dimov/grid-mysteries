"""Investigation 002's hardened selection: the amended 001 rule.

Pure logic for the two amendments 2026-08-04..10 taught, applied to a week
that taught neither. `bod_inversion` still enumerates and ranks candidates;
this module screens them and reports the declared funnel.

- **Amendment A — deliverability enters selection.** An unaccepted
  alternative proved non-deliverable by the one-sided headroom bound
  (`phantom_liquidity`) is removed. 001 selected a case whose "cheaper"
  alternative had FPN 0 and MEL 0.
- **Amendment B — the accepted side is screened.** A candidate whose
  accepted action is system-flagged in BOALF is removed: comparing a
  system-driven curtailment against an energy-priced alternative is the
  category error behind all six of 001D's residual cases.

Implementation contracts (not constitutional amendments — the declaration
in `investigations/002-hardened-selector/README.md` governs):

- Every alternative must carry a deliverability classification. A missing
  key is an error, never silently treated as deliverable — absent public
  state must reach here as `not_ruled_out`, which the classifier already
  guarantees.
- The system flag is keyed `(date, period, accepted unit)`: BOALF records
  acceptances per unit and period, not per bid-offer pair, so a unit with
  any system-flagged acceptance in a period has that period's accepted
  actions treated as system-driven. This is the conservative reading — it
  removes candidates rather than keeping doubtful ones.
- Funnel notional is `|accepted volume| x best surviving gap`, summed per
  distinct accepted action, so many candidates sharing one action cannot
  inflate it. It is **naive counterfactual notional** — arithmetic on
  public numbers, never a saving.
- Screening and selection are order-independent and total: identical
  inputs always yield identical output.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final

from grid_mysteries.investigations.bod_inversion import InversionCandidate, rank_candidates
from grid_mysteries.investigations.phantom_liquidity import NON_DELIVERABLE

#: date, period, direction, unit, pair — one submitted alternative.
AlternativeKey = tuple[str, int, str, str, int]
#: date, period, direction, unit, pair — one accepted action.
AcceptedActionKey = tuple[str, int, str, str, int]
#: date, period, unit — BOALF's grain for the system flag.
SystemFlagKey = tuple[str, int, str]

STAGE_RAW: Final = "raw"
STAGE_AFTER_DELIVERABILITY: Final = "after_deliverability"
STAGE_AFTER_SYSTEM_FLAG: Final = "after_system_flag"


def alternative_key(candidate: InversionCandidate) -> AlternativeKey:
    return (
        candidate.settlement_date,
        candidate.settlement_period,
        candidate.direction,
        candidate.unaccepted_unit,
        candidate.unaccepted_pair_id,
    )


def accepted_action_key(candidate: InversionCandidate) -> AcceptedActionKey:
    return (
        candidate.settlement_date,
        candidate.settlement_period,
        candidate.direction,
        candidate.accepted_unit,
        candidate.accepted_pair_id,
    )


def system_flag_key(candidate: InversionCandidate) -> SystemFlagKey:
    return (
        candidate.settlement_date,
        candidate.settlement_period,
        candidate.accepted_unit,
    )


@dataclass(frozen=True, slots=True)
class Stage:
    """One rung of the declared funnel."""

    name: str
    candidates: int
    accepted_actions: int
    naive_notional_gbp: Decimal


@dataclass(frozen=True, slots=True)
class Funnel:
    stages: tuple[Stage, ...]

    def as_dict(self) -> list[dict]:
        return [
            {
                "stage": s.name,
                "candidates": s.candidates,
                "accepted_actions": s.accepted_actions,
                "naive_counterfactual_notional_gbp": str(s.naive_notional_gbp),
            }
            for s in self.stages
        ]


def naive_notional_gbp(candidates: list[InversionCandidate]) -> Decimal:
    """Per accepted action, |volume| x its best gap; summed. Never a saving."""
    best: dict[AcceptedActionKey, tuple[Decimal, Decimal]] = {}
    for candidate in candidates:
        key = accepted_action_key(candidate)
        gap = candidate.gap_gbp_per_mwh
        volume = abs(candidate.accepted_volume_mwh)
        current = best.get(key)
        if current is None or gap > current[0]:
            best[key] = (gap, volume)
    return sum((gap * volume for gap, volume in best.values()), Decimal(0))


def summarise(name: str, candidates: list[InversionCandidate]) -> Stage:
    return Stage(
        name=name,
        candidates=len(candidates),
        accepted_actions=len({accepted_action_key(c) for c in candidates}),
        naive_notional_gbp=naive_notional_gbp(candidates),
    )


def screen(
    candidates: list[InversionCandidate],
    *,
    deliverability: dict[AlternativeKey, str],
    system_flagged: set[SystemFlagKey],
) -> tuple[list[InversionCandidate], Funnel]:
    """Apply Amendment A then Amendment B; return survivors and the funnel.

    Raises ``KeyError`` if any alternative lacks a deliverability
    classification: unknown state must never pass as deliverable.
    """
    missing = {alternative_key(c) for c in candidates} - set(deliverability)
    if missing:
        raise KeyError(
            f"{len(missing)} alternative(s) lack a deliverability classification, "
            f"e.g. {sorted(missing)[0]}; unknown state must arrive as not_ruled_out"
        )
    after_a = [c for c in candidates if deliverability[alternative_key(c)] != NON_DELIVERABLE]
    after_b = [c for c in after_a if system_flag_key(c) not in system_flagged]
    funnel = Funnel(
        stages=(
            summarise(STAGE_RAW, candidates),
            summarise(STAGE_AFTER_DELIVERABILITY, after_a),
            summarise(STAGE_AFTER_SYSTEM_FLAG, after_b),
        )
    )
    return after_b, funnel


def select(surviving: list[InversionCandidate]) -> InversionCandidate | None:
    """The declared selection: highest price gap under 001's tie-breaks.

    ``None`` when nothing survives — a declared, publishable outcome, not
    an error to work around.
    """
    if not surviving:
        return None
    return rank_candidates(surviving)[0]
