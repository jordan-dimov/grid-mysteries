"""Investigation 021: 014's connection-slippage series cut by plant type and
by host transmission owner.

Pure; no I/O. Two parts:

- the **schema pass** (`key_stability`): whether a project-stage's printed
  plant type or host TO changes between consecutive copies of the archive,
  counted over every parsed copy. It is a fact about the archive's columns,
  recorded in the committed schema report before any grouped figure is
  declared; it computes no movement.
- the **cut** (written after the declaration is frozen): each comparison of
  014 version 4, with the same population, split by a grouping key read
  from the register as printed.
"""

from collections import Counter
from datetime import date
from typing import Any, Final

from grid_mysteries.investigations import connection_slippage as cs

#: (report key, register column) of the two grouping keys, as 014's reader
#: canonicalises the column names.
GROUPING: Final = (("plant_type", "Plant Type"), ("host_to", "HOST TO"))
#: How many of the most frequent transitions of a key the SCHEMA.md summary
#: lists; the JSON report keeps every transition.
TRANSITIONS_LISTED: Final = 25


def printed(value: object) -> str:
    """A cell as printed, with runs of whitespace collapsed; blank stays blank."""
    return " ".join(str(value or "").split())


def tags(rows: list[dict[str, object]]) -> dict[str, dict[str, str]]:
    """Each unit's printed grouping keys in one copy, by 014's unit key."""
    out: dict[str, dict[str, str]] = {}
    for key, row in zip(cs.unit_keys(rows), rows, strict=True):
        out[key] = {name: printed(row.get(column)) for name, column in GROUPING}
    return out


def key_stability(copies: list[tuple[date, list[dict[str, object]]]]) -> dict[str, Any]:
    """Over consecutive copies, for units (014's key) printed in both: how
    many change their plant type, how many their host TO, which transitions
    occur, and in which copies. No movement figure is computed."""
    changed: dict[str, Counter[tuple[str, str]]] = {name: Counter() for name, _ in GROUPING}
    per_copy: list[dict[str, Any]] = []
    matched_total = 0
    previous: dict[str, dict[str, str]] | None = None
    previous_date: date | None = None
    for t, rows in copies:
        current = tags(rows)
        if previous is not None:
            both = previous.keys() & current.keys()
            matched_total += len(both)
            counts = {name: 0 for name, _ in GROUPING}
            for key in both:
                for name, _ in GROUPING:
                    before, now = previous[key][name], current[key][name]
                    if before != now:
                        counts[name] += 1
                        changed[name][(before, now)] += 1
            if any(counts.values()):
                per_copy.append(
                    {
                        "previous": previous_date.isoformat() if previous_date else None,
                        "t_public": t.isoformat(),
                        "matched": len(both),
                        **{f"{name}_changed": n for name, n in counts.items()},
                    }
                )
        previous, previous_date = current, t
    return {
        "copies": len(copies),
        "matched_units_over_consecutive_copies": matched_total,
        **{
            name: {
                "units_changed": sum(changed[name].values()),
                "distinct_transitions": len(changed[name]),
                "transitions": [
                    {"from": a, "to": b, "units": n} for (a, b), n in changed[name].most_common()
                ],
            }
            for name, _ in GROUPING
        },
        "copies_with_a_change": per_copy,
    }
