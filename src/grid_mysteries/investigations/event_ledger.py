"""The event ledger: first module of the grid replay engine.

Born as Investigation 003's reconstruction substrate; the invariants are
structural, not conventional:

- **Deterministic ordering**: a timeline is canonically ordered
  regardless of input order, and period gaps are surfaced, never
  smoothed over.
- **The three-column discipline is a type**: every entry is observed,
  supported inference (which *requires* a stated assumption), or not
  publicly observable — and nothing not-publicly-observable may carry a
  monetary amount, so the missing B in A→?→C cannot be silently
  promoted by attaching money to it.
- **Every pound is labelled**: an amount is either
  ``published_indicative_bm_cashflow`` (reconciled to pinned EBOCF) or
  an ``acceptance_notional`` — an entry with an amount and no label
  refuses to construct.
- **EBOCF semantics**: per-pair cashflows explain composition;
  ``totalCashflow`` is the BMU-period total; the two must reconcile
  exactly and are never summed together. The record preserves its
  ``created`` vintage: EBOCF is the *latest* indicative settlement run
  retrieved at pin time, not necessarily the value observable in-month.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

Column = Literal["observed", "supported_inference", "not_publicly_observable"]
MoneyKind = Literal["published_indicative_bm_cashflow", "acceptance_notional"]

#: EBOCF serialises float-computed values, so the printed pair cashflows
#: and printed total can disagree at the picopound level (observed max
#: ~1.5e-12 GBP on real data). One microgbp is six orders above that
#: noise and four below a penny: anything past it is a real discrepancy.
RECONCILIATION_TOLERANCE_GBP = Decimal("0.000001")


@dataclass(frozen=True, slots=True)
class BmuPeriodCashflow:
    """One EBOCF record: per-pair composition plus the published total."""

    bm_unit: str
    settlement_date: str
    settlement_period: int
    pair_cashflows: dict[int, Decimal]  # pair id -> GBP, non-null pairs only
    total_cashflow: Decimal
    created: str  # publication vintage of the latest settlement run

    def reconciled_total(self) -> Decimal:
        """The published total, after asserting the pairs explain it.

        Composition and total are alternative views of one quantity;
        this is the only sanctioned way to read the number, so the two
        can never be added together.
        """
        composed = sum(self.pair_cashflows.values(), Decimal(0))
        if abs(composed - self.total_cashflow) > RECONCILIATION_TOLERANCE_GBP:
            raise ValueError(
                f"EBOCF pairs do not reconcile to totalCashflow for "
                f"{self.bm_unit} {self.settlement_date} p{self.settlement_period}: "
                f"{composed} != {self.total_cashflow}"
            )
        return self.total_cashflow


def parse_ebocf_record(record: dict) -> BmuPeriodCashflow:
    """Parse one row of a pinned EBOCF artefact (Decimal-loaded)."""
    pairs: dict[int, Decimal] = {}
    for name, value in (record.get("bidOfferPairCashflows") or {}).items():
        if value is None:
            continue
        pair_id = int(name.removeprefix("positive").removeprefix("negative"))
        if name.startswith("negative"):
            pair_id = -pair_id
        pairs[pair_id] = value if isinstance(value, Decimal) else Decimal(str(value))
    total = record["totalCashflow"]
    return BmuPeriodCashflow(
        bm_unit=str(record["bmUnit"]),
        settlement_date=str(record["settlementDate"]),
        settlement_period=int(record["settlementPeriod"]),
        pair_cashflows=pairs,
        total_cashflow=total if isinstance(total, Decimal) else Decimal(str(total)),
        created=str(record.get("createdDateTime", "")),
    )


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """One step of a reconstruction, classified under the three-column
    discipline at construction time and immutable thereafter."""

    settlement_date: str
    settlement_period: int
    actor: str
    description: str
    column: Column
    sequence_time: str = ""  # e.g. BOALF acceptanceTime; empty sorts first
    assumption: str = ""  # required iff column == supported_inference
    amount_gbp: Decimal | None = None
    money_kind: MoneyKind | None = None
    details: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.column == "supported_inference" and not self.assumption.strip():
            raise ValueError("a supported inference must state its assumption at the point of use")
        if self.column != "supported_inference" and self.assumption.strip():
            raise ValueError("only supported inferences carry assumptions")
        if self.amount_gbp is not None and self.money_kind is None:
            raise ValueError(
                "an amount must be labelled published_indicative_bm_cashflow or acceptance_notional"
            )
        if self.column == "not_publicly_observable" and self.amount_gbp is not None:
            raise ValueError(
                "a not-publicly-observable step can never carry a monetary "
                "amount; the question mark is part of the result"
            )


def ordered(entries: list[LedgerEntry]) -> list[LedgerEntry]:
    """Canonical timeline order, independent of input order."""
    return sorted(
        entries,
        key=lambda e: (
            e.settlement_date,
            e.settlement_period,
            e.sequence_time,
            e.actor,
            e.description,
        ),
    )


def period_gaps(entries: list[LedgerEntry]) -> list[tuple[str, int]]:
    """Periods with no entry between the timeline's first and last
    (date, period), inclusive — surfaced, never smoothed over."""
    if not entries:
        return []
    covered = {(e.settlement_date, e.settlement_period) for e in entries}
    dates = sorted({e.settlement_date for e in entries})
    timeline = ordered(entries)
    first = (timeline[0].settlement_date, timeline[0].settlement_period)
    last = (timeline[-1].settlement_date, timeline[-1].settlement_period)
    gaps = []
    for date in dates:
        for period in range(1, 49):
            slot = (date, period)
            if first <= slot <= last and slot not in covered:
                gaps.append(slot)
    return gaps
