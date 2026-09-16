"""The As-of Connection Record: what the TEC Register published about one
project on given dates, and every change between them.

Pure logic; no I/O. A factual record only: it states what each vintage
published and which vintage first showed each change. It forecasts nothing
and says nothing about entitlement.

Tracking rule: rows are matched to the requested project by the register's
own normalised project name and, where given, stage. Customer name and
connection site are attributes whose changes are recorded, not part of the
match (a certificate follows the project through a change of customer or
site string; the series in `connection_slippage` deliberately does not,
because there the unit is the full identity). A vintage with no matching
row is recorded as an absence; one with several is recorded as ambiguous
and every matching row is kept.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.sources.tec_register import (
    normalise,
    normalise_stage,
    parse_date,
    parse_decimal,
)

#: (label, register column, comparison kind) in the order the certificate prints them.
FIELDS: Final[tuple[tuple[str, str, str], ...]] = (
    ("Project name", "Project Name", "text"),
    ("Customer name", "Customer Name", "text"),
    ("Connection site", "Connection Site", "text"),
    ("Stage", "Stage", "stage"),
    ("MW connected", "MW Connected", "number"),
    ("MW increase / decrease (stage TEC)", "MW Increase / Decrease", "number"),
    ("Cumulative total capacity (MW)", "Cumulative Total Capacity (MW)", "number"),
    ("MW effective from (target date)", "MW Effective From", "date"),
    ("Project status", "Project Status", "text"),
    ("Agreement type", "Agreement Type", "label"),
    ("Host TO", "HOST TO", "text"),
    ("Plant type", "Plant Type", "text"),
    ("Project ID", "Project ID", "salesforce-id"),
    ("Project number", "Project Number", "text"),
    ("Gate", "Gate", "text"),
)


#: Label variants the register has printed for one meaning, declared here and
#: in certificates/README.md; a change between two spellings of one label is
#: not a change of what was published, and the printed values keep their
#: spellings. Keys and values are the whitespace-free, lower-case forms.
LABEL_VARIANTS: Final[dict[str, str]] = {
    "directconnection": "directlyconnected",
}
#: Salesforce record ids come in a 15-character case-sensitive form and an
#: 18-character form that appends a checksum; the first 15 characters name
#: the same record.
SALESFORCE_ID_LENGTH: Final = 15


def comparable(value: object, kind: str) -> object:
    """The value the certificate compares: dates parsed, numbers as Decimal,
    stage numerics unified, text ignoring letter case and whitespace (a
    respelling is not a change; a different word is), labels with declared
    variants unified, Salesforce ids on their 15-character form."""
    if kind == "date":
        return parse_date(value)
    if kind == "number":
        return parse_decimal(value)
    if kind == "stage":
        return normalise_stage(value)
    if kind == "salesforce-id":
        return "".join(str(value or "").split())[:SALESFORCE_ID_LENGTH]
    folded = "".join(str(value or "").split()).lower()
    if kind == "label":
        return LABEL_VARIANTS.get(folded, folded)
    return folded


def shown(value: object, kind: str) -> str:
    """The value as published, for printing (dates keep their spelling)."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return " ".join(str(value if value is not None else "").split())


@dataclass(frozen=True)
class Observation:
    t_public: date
    sha256: str
    path: str
    rows: tuple[dict[str, object], ...]

    @property
    def count(self) -> int:
        return len(self.rows)


def matches(rows: list[dict[str, object]], name: str, stage: str | None) -> list[dict[str, object]]:
    wanted = normalise(name)
    out = []
    for row in rows:
        if normalise(row.get("Project Name")) != wanted:
            continue
        if stage is not None and normalise_stage(row.get("Stage")) != normalise_stage(stage):
            continue
        out.append(row)
    return out


def track(
    vintages: list[tuple[date, list[dict[str, object]], str, str]], name: str, stage: str | None
) -> list[Observation]:
    """One observation per vintage (t_public, rows, sha256, path), in date order."""
    return [
        Observation(t, sha, path, tuple(matches(rows, name, stage)))
        for t, rows, sha, path in sorted(vintages, key=lambda v: v[0])
    ]


def as_of(observations: list[Observation], on: date) -> Observation | None:
    """The vintage in force on a date: the latest published on or before it."""
    candidates = [o for o in observations if o.t_public <= on]
    return candidates[-1] if candidates else None


@dataclass(frozen=True)
class Change:
    field: str
    previous: str
    current: str
    first_shown: date
    first_shown_sha256: str
    last_previous: date


def _state(observation: Observation) -> dict[str, tuple[object, str]] | str:
    if observation.count == 0:
        return "absent"
    if observation.count > 1:
        return f"ambiguous ({observation.count} rows)"
    row = observation.rows[0]
    return {
        label: (comparable(row.get(col), kind), shown(row.get(col), kind))
        for label, col, kind in FIELDS
    }


def changes(observations: list[Observation], start: date, end: date) -> list[Change]:
    """Every change between the vintage in force on `start` and the one in
    force on `end`, inclusive, each with the vintage that first showed it.

    Compared values are the `comparable` forms, so a date respelled
    (30/10/2025 to 2025-10-30) is not a change; the printed values are the
    published spellings. Absence and ambiguity are changes of presence.
    """
    first = as_of(observations, start)
    last = as_of(observations, end)
    if first is None or last is None:
        return []
    window = [o for o in observations if first.t_public <= o.t_public <= last.t_public]
    out: list[Change] = []
    previous = window[0]
    prev_state = _state(previous)
    for current in window[1:]:
        cur_state = _state(current)
        if isinstance(prev_state, str) or isinstance(cur_state, str):
            if prev_state != cur_state:
                out.append(
                    Change(
                        "Presence",
                        prev_state if isinstance(prev_state, str) else "present (one row)",
                        cur_state if isinstance(cur_state, str) else "present (one row)",
                        current.t_public,
                        current.sha256,
                        previous.t_public,
                    )
                )
        else:
            for label, _col, _kind in FIELDS:
                before, after = prev_state[label], cur_state[label]
                if before[0] != after[0]:
                    out.append(
                        Change(
                            label,
                            before[1],
                            after[1],
                            current.t_public,
                            current.sha256,
                            previous.t_public,
                        )
                    )
        previous, prev_state = current, cur_state
    return out


def record(
    observations: list[Observation], name: str, stage: str | None, dates: tuple[date, date]
) -> dict[str, Any]:
    """The certificate's content: the as-of state on each date, the changes
    between them, and the vintages consulted. Nothing else."""
    start, end = dates
    states: list[dict[str, Any]] = []
    for on in (start, end):
        observation = as_of(observations, on)
        if observation is None:
            states.append(
                {"as_of": on, "vintage": None, "state": "no vintage on or before this date"}
            )
            continue
        state = _state(observation)
        states.append(
            {
                "as_of": on,
                "vintage": observation.t_public,
                "sha256": observation.sha256,
                "path": observation.path,
                "state": state
                if isinstance(state, str)
                else {label: v[1] for label, v in state.items()},
                "rows_as_published": [
                    {label: shown(r.get(col), kind) for label, col, kind in FIELDS}
                    for r in observation.rows
                ],
            }
        )
    first, last = as_of(observations, start), as_of(observations, end)
    consulted = (
        [o for o in observations if first.t_public <= o.t_public <= last.t_public]
        if first and last
        else []
    )
    return {
        "project": name,
        "stage": stage,
        "dates": [start, end],
        "as_of": states,
        "changes": [c.__dict__ for c in changes(observations, start, end)],
        "vintages_consulted": len(consulted),
        "vintages_absent": sum(1 for o in consulted if o.count == 0),
        "vintages_ambiguous": sum(1 for o in consulted if o.count > 1),
        "first_vintage": consulted[0].t_public if consulted else None,
        "last_vintage": consulted[-1].t_public if consulted else None,
    }
