"""023 — Did projects that changed hands slip more? Pure.

The exposure is 019's own R4 rule (`queue_ownership.classify_change`, as
019's amendment 2 restates it) applied to the customer name a Project ID
prints at a window's two ends; the outcome is the movement of each
capacity-bearing stage's printed date between those ends, read as 014 v4
reads dates. No I/O.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.investigations import queue_ownership as qo

#: Exposure classes at a window's ends.
TRANSFER: Final = "transfer"
RENAME: Final = "rename"
SAME_NAME: Final = "same-name"
NOT_DETERMINABLE: Final = "not-determinable"
SEVERAL_NAMES: Final = "several-names"


def boundaries(runs: list[dict[str, Any]], b: date, c: date) -> list[tuple[str, str, str]]:
    """The name changes of one Project ID between copies *b* and *c*, from
    019's run-length history: consecutive runs whose earlier run was still
    printed on or after *b* and whose later run began on or before *c*, as
    (earlier name, later name, first copy with the later name)."""
    out = []
    for prev, nxt in zip(runs, runs[1:], strict=False):
        last = date.fromisoformat(prev.get("last_t_public") or prev["t_public"])
        first = date.fromisoformat(nxt["t_public"])
        if last >= b and first <= c and prev["name"] != nxt["name"]:
            out.append((prev["name"], nxt["name"], nxt["t_public"]))
    return out


def ends_class(
    pid: str,
    names_b: set[str],
    names_c: set[str],
    b: date,
    c: date,
    links: dict[str, qo.Link],
    admitted: dict[str, dict[str, Any]],
    profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """The exposure of one Project ID over a window: the printed customer
    name at each end, and 019's R4 verdict on the pair. A name admitted
    with several holders (019's copy-date rule) resolves at the end that
    prints it."""
    if len(names_b) != 1 or len(names_c) != 1:
        return {"class": SEVERAL_NAMES, "earlier": sorted(names_b), "later": sorted(names_c)}
    (name_b,), (name_c,) = names_b, names_c
    if name_b == name_c:
        return {"class": SAME_NAME, "earlier": name_b, "later": name_c}
    on = dict(links)
    for name, when in ((name_b, b), (name_c, c)):
        if name in on and admitted.get(name, {}).get("holders"):
            on[name] = qo.apply_admissions(on[name], admitted, on=when)
    change = qo.NameChange(pid, name_b, name_c, b.isoformat(), c.isoformat())
    verdict = qo.classify_change(change, on, profiles)
    return {
        "class": verdict["class"],
        "earlier": name_b,
        "later": name_c,
        "earlier_company": verdict["earlier_company"],
        "later_company": verdict["later_company"],
    }


@dataclass(frozen=True)
class StageMove:
    """One capacity-bearing stage of a Project ID dated at both ends."""

    project_id: str
    stage: str
    mw: Decimal
    status_b: str
    plant_type_b: str
    date_b: date
    date_c: date

    @property
    def days(self) -> int:
        return (self.date_c - self.date_b).days

    @property
    def months(self) -> Decimal:
        return (Decimal(self.days) / Decimal("30.4375")).quantize(Decimal("0.1"))

    @property
    def mw_years(self) -> Decimal:
        return (self.mw * Decimal(self.days) / Decimal("365.25")).quantize(Decimal("0.001"))

    @property
    def direction(self) -> str:
        return "later" if self.days > 0 else "earlier" if self.days < 0 else "unchanged"


Reader = Callable[[dict[str, object]], date | None]
