"""Identity by content: which row of one publication is which unit of the last.

Rule `tec-identity-content-v1`. Pure; no I/O.

A *project group* is 014's identity: the normalised (project name,
customer name, connection site) triple. A group holding one row in each
publication is one unit, as in 014. Where a group holds several rows (before
November 2021 the register printed no `Stage` or `Project ID`, so one
project could print several rows under the same name, customer and site),
rows are matched to the previous publication's units by **content**: the
assignment that changes least, found exactly (a group never exceeds a
handful of rows), with the costs compared in this order:

1. the register's own stage, where both sides print one and they differ;
2. the stage's MW (`MW Increase / Decrease`);
3. the effective date, as read (014's reading rules, the swap test included);
4. the number of other cells that differ;
5. the days the effective date would move.

A unit whose row is no longer printed is kept as *dormant* for its group.
Rows are matched to the group's live units first; rows left over are then
matched, by the same costs, to its dormant units, and only rows left after
that become new units. A project that drops out of one publication and
returns is the same unit again, as 014's keys are the same key again.

Row order never enters: a publication that prints the same rows in another
order produces no change at all. When a group's row count changes, the
assignment that changes least decides which units leave or arrive. A
group's rows are taken in the order of their content, not of the file,
so a tie that survives all five costs resolves by unit number and content,
the same way however the file is sorted. Units are named `<group>#u<n>`, numbered in order of first
appearance, and never reused.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Final

from grid_mysteries.investigations.connection_slippage import Entry, identity, stage_mw
from grid_mysteries.sources.tec_register import (
    CANONICAL_COLUMNS,
    normalise_stage,
    parse_date,
    swap_day_month,
)
from grid_mysteries.tec import cells

RULE: Final = "tec-identity-content-v1"
Cost = tuple[int, int, int, int, int]
ZERO_COST: Final[Cost] = (0, 0, 0, 0, 0)


@dataclass(frozen=True)
class Unit:
    unit: str
    group: str
    row: dict[str, object]
    stage: str
    mw: Decimal | None
    effective: date | None


def _reading(row: dict[str, object], swapped: bool) -> date | None:
    effective = parse_date(row.get("MW Effective From"))
    if swapped:
        effective = swap_day_month(effective) or effective
    return effective


def cost(
    previous: Unit, row: dict[str, object], stage: str, mw: object, effective: date | None
) -> Cost:
    stage_differs = int(bool(previous.stage and stage and previous.stage != stage))
    mw_differs = int(previous.mw != mw)
    date_differs = int(previous.effective != effective)
    others = sum(
        1
        for column in CANONICAL_COLUMNS
        if column not in ("Stage", "MW Increase / Decrease", "MW Effective From")
        and str(previous.row.get(column) or "") != str(row.get(column) or "")
    )
    days = (
        abs((effective - previous.effective).days)
        if effective is not None and previous.effective is not None
        else 0
    )
    return (stage_differs, mw_differs, date_differs, others, days)


def _add(a: Cost, b: Cost) -> Cost:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3], a[4] + b[4])


def best_assignment(matrix: list[list[Cost]]) -> list[int]:
    """For each row of `matrix` (len n <= columns m), the column it takes, so
    that the columns are distinct and the summed cost is least (compared as
    tuples). Exact, by dynamic programming over subsets of columns."""
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    if n > m:
        raise ValueError("more rows than columns")
    best: dict[int, tuple[Cost, list[int]]] = {0: (ZERO_COST, [])}
    for i in range(n):
        step: dict[int, tuple[Cost, list[int]]] = {}
        for mask, (total, chosen) in best.items():
            for j in range(m):
                if mask & (1 << j):
                    continue
                candidate = (_add(total, matrix[i][j]), [*chosen, j])
                key = mask | (1 << j)
                if key not in step or candidate[0] < step[key][0]:
                    step[key] = candidate
        best = step
    return min(best.values(), key=lambda v: v[0])[1] if best else []


def _match(previous: list[Unit], facts: list[tuple]) -> dict[int, Unit]:
    """Which fact (by index) each previous unit takes, least change first."""
    taken: dict[int, Unit] = {}
    if not previous or not facts:
        return taken
    if len(previous) <= len(facts):
        matrix = [[cost(u, *f) for f in facts] for u in previous]
        for u_index, f_index in enumerate(best_assignment(matrix)):
            taken[f_index] = previous[u_index]
    else:
        matrix = [[cost(u, *f) for u in previous] for f in facts]
        for f_index, u_index in enumerate(best_assignment(matrix)):
            taken[f_index] = previous[u_index]
    return taken


#: Dormant units offered to returning rows, most recently retired first
#: (a bound on the exact search, which is exponential in group size).
DORMANT_LIMIT: Final = 12


@dataclass
class ContentIdentity:
    """Carries the units from one publication to the next."""

    units: dict[str, Unit] = field(default_factory=dict)
    dormant: dict[str, list[Unit]] = field(default_factory=lambda: defaultdict(list))
    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def _new(self, group: str) -> str:
        self.counters[group] += 1
        return f"{group}#u{self.counters[group]}"

    def step(self, rows: list[dict[str, object]], *, swapped: bool = False) -> dict[str, Entry]:
        """The publication's entries keyed by unit, and the carried state updated."""
        by_group_prev: dict[str, list[Unit]] = defaultdict(list)
        for unit in self.units.values():
            by_group_prev[unit.group].append(unit)
        by_group_cur: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            by_group_cur[identity(row)].append(row)
        now: dict[str, Unit] = {}
        for group in by_group_prev.keys() - by_group_cur.keys():
            self.dormant[group] = [*by_group_prev[group], *self.dormant[group]]
        for group, current in by_group_cur.items():
            live = sorted(by_group_prev.get(group, []), key=lambda u: u.unit)
            facts = [
                (row, normalise_stage(row.get("Stage")), stage_mw(row), _reading(row, swapped))
                for row in sorted(current, key=cells.encode)
            ]
            taken = _match(live, facts)
            left = [i for i in range(len(facts)) if i not in taken]
            dormant = self.dormant.get(group, [])[:DORMANT_LIMIT]
            returned = _match(dormant, [facts[i] for i in left])
            for position, unit in returned.items():
                taken[left[position]] = unit
            woken = {u.unit for u in returned.values()}
            kept = {u.unit for u in taken.values()}
            retired = [u for u in live if u.unit not in kept]
            self.dormant[group] = retired + [
                u for u in self.dormant.get(group, []) if u.unit not in woken
            ]
            for index, (row, stage, mw, effective) in enumerate(facts):
                name = taken[index].unit if index in taken else self._new(group)
                now[name] = Unit(name, group, row, stage, mw, effective)
        self.units = now
        return {
            name: Entry(
                key=name,
                identity=u.group,
                stage=u.stage,
                mw=u.mw,
                effective=u.effective,
                raw_effective=str(u.row.get("MW Effective From") or "").strip(),
            )
            for name, u in now.items()
        }
