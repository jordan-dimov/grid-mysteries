"""Settlement-period balancing costs, and Investigation 004's selection.

NESO publishes daily balancing costs at settlement-period resolution,
split into categories (`Constraints`, `Energy Imbalance`, reserve, …).
Investigation 004's frozen rule picks one period from a window: the
highest published `Constraints` value, ties by earlier date then lower
period.

Implementation contracts (the declaration in
`investigations/004-most-expensive-half-hour/README.md` governs):

- Costs are `Decimal`; the published CSV carries floats as text and a
  binary float would weaken a monetary claim.
- A row whose `Constraints` cell is blank is *missing*, not zero: it is
  carried as ``None`` and can never win. Treating absence as zero would
  silently let a gap outrank a real period, and treating it as a value
  would invent one.
- "Most expensive" means the highest published `Constraints` category
  value, nothing more — never a cost attributed to any boundary, unit or
  action.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

#: The published category columns, as NESO names them.
CONSTRAINTS_COLUMN = "Constraints"
DATE_COLUMN = "SETT_DATE"
PERIOD_COLUMN = "SETT_PERIOD"


def _decimal(value: object) -> Decimal | None:
    """Published cell -> Decimal; blank or unparseable -> None (missing)."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


@dataclass(frozen=True, slots=True)
class PeriodCost:
    settlement_date: str
    settlement_period: int
    constraints_gbp: Decimal | None
    categories: dict[str, Decimal | None]


def parse_cost_rows(rows: list[dict]) -> list[PeriodCost]:
    """Parse published daily-balancing-cost rows, preserving missingness."""
    parsed = []
    for row in rows:
        categories = {
            key: _decimal(value)
            for key, value in row.items()
            if key not in {"_id", DATE_COLUMN, PERIOD_COLUMN, "rank"}
        }
        parsed.append(
            PeriodCost(
                settlement_date=str(row[DATE_COLUMN])[:10],
                settlement_period=int(row[PERIOD_COLUMN]),
                constraints_gbp=categories.get(CONSTRAINTS_COLUMN),
                categories=categories,
            )
        )
    return parsed


def select_most_expensive(costs: list[PeriodCost], window: set[str]) -> PeriodCost | None:
    """The declared selection: highest `Constraints` in the window.

    Ties break by earlier settlement date, then lower settlement period.
    Periods with a missing `Constraints` value cannot win. ``None`` when
    the window holds no period with a published value — a declared,
    reportable outcome, not an error.
    """
    eligible: list[tuple[Decimal, PeriodCost]] = []
    for cost in costs:
        value = cost.constraints_gbp
        if value is not None and cost.settlement_date in window:
            eligible.append((value, cost))
    if not eligible:
        return None
    _, winner = min(
        eligible,
        key=lambda pair: (-pair[0], pair[1].settlement_date, pair[1].settlement_period),
    )
    return winner
