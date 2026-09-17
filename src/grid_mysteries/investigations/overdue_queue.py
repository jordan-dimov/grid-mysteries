"""Investigation 017 — the entries of the TEC Register that are past their
own date, counted over one copy.

Pure logic over one vintage's rows; no I/O. The declaration in
`investigations/017-the-overdue-queue/DECLARATION.md` (SHA-256
`400b42f7…`) governs, and every rule below is one it states.

- **R1/R2 — as-of.** One copy only. A row is *past its date* when its
  parsed `MW Effective From` is strictly earlier than that copy's own
  publication date; not earlier than the day the run happens.
- **R3 — dates.** Every spelling the register has used parses; a cell that
  does not parse is undated, never guessed, and outside the census. The
  series' day-month swap correction is a test between two copies and is
  not applied to one; instead the swap sensitivity is published.
- **R4 — not Built.** Status with whitespace collapsed and case ignored is
  not `built`. The selected rows are also published by status as printed.
- **R5 — the measure.** `MW Increase / Decrease` as published, as
  `Decimal`. A blank or unparseable cell is *no* capacity, not zero, and
  is excluded from every total; a parseable `0` is a row with zero
  capacity and is counted as a row.
- **R6 — the unit.** The register row. Beside the row totals, a second
  reading counts each distinct project id once (15-character Salesforce
  form) and keeps the largest MW among its rows; a row with no id cannot
  be shown to share one, so it stands alone.
- **R7 — the breakdowns.** Exactly four, fixed before the run: by status
  as printed, by plant type as printed (compound types kept whole), by
  calendar year of the effective date, and the ten earliest rows. For
  scale, outside the selection: the MW dated on or after the as-of date,
  and of that the MW whose status is `Scoping`.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.sources.tec_register import (
    parse_date,
    parse_decimal,
    swap_day_month,
)

#: Salesforce record ids come in a 15-character form and an 18-character form
#: that appends a checksum; the first 15 characters name the same record
#: (014's declared unification, `connection_record.SALESFORCE_ID_LENGTH`).
SALESFORCE_ID_LENGTH: Final = 15
BUILT: Final = "built"
SCOPING: Final = "scoping"
EARLIEST_SHOWN: Final = 10
#: F1: the share of selected MW that may sit in rows whose day-month swapped
#: reading would be in the future before the headline stops being one number.
F1_SWAP_SHARE: Final = Decimal("0.2")
#: F3: how far the two readings of R6 may differ before neither is "the" figure.
F3_READING_SHARE: Final = Decimal("0.1")
ZERO: Final = Decimal(0)


def text(value: object) -> str:
    """A cell as printed, with runs of whitespace collapsed."""
    return " ".join(str(value if value is not None else "").split())


def status(row: dict[str, object]) -> str:
    return text(row.get("Project Status"))


def is_built(row: dict[str, object]) -> bool:
    return status(row).casefold() == BUILT


def project_id(row: dict[str, object]) -> str:
    """The row's project id on its 15-character form; blank stays blank."""
    return "".join(str(row.get("Project ID") or "").split())[:SALESFORCE_ID_LENGTH]


def stage_mw(row: dict[str, object]) -> Decimal | None:
    """The stage's TEC MW as published; None when the cell says nothing."""
    return parse_decimal(row.get("MW Increase / Decrease"))


@dataclass(frozen=True)
class Row:
    """One selected register row, as published."""

    index: int
    project_name: str
    customer_name: str
    connection_site: str
    stage: str
    project_id: str
    project_number: str
    plant_type: str
    status: str
    mw: Decimal | None
    effective: date
    effective_as_published: str
    #: The day-month swapped reading of the date, where one exists (R3).
    effective_swapped: date | None


def selected_row(index: int, row: dict[str, object], effective: date) -> Row:
    return Row(
        index=index,
        project_name=text(row.get("Project Name")),
        customer_name=text(row.get("Customer Name")),
        connection_site=text(row.get("Connection Site")),
        stage=text(row.get("Stage")),
        project_id=project_id(row),
        project_number=text(row.get("Project Number")),
        plant_type=text(row.get("Plant Type")),
        status=status(row),
        mw=stage_mw(row),
        effective=effective,
        effective_as_published=text(row.get("MW Effective From")),
        effective_swapped=swap_day_month(effective),
    )


def total_mw(rows: list[Row]) -> Decimal:
    """The MW of rows that carry a parseable capacity; the rest are not zero,
    they are absent, and take no part in a total (R5)."""
    return sum((r.mw for r in rows if r.mw is not None), ZERO)


def _group(rows: list[Row], key: Any, label: str) -> list[dict[str, Any]]:
    """Rows grouped by `key`, heaviest first, ties by label; the label is the
    value as printed, so a grouping is never a re-spelling."""
    groups: dict[Any, list[Row]] = {}
    for row in rows:
        groups.setdefault(key(row), []).append(row)
    out = [
        {label: k, "rows": len(members), "mw": total_mw(members)} for k, members in groups.items()
    ]
    return sorted(out, key=lambda g: (-g["mw"], str(g[label])))


def by_id(rows: list[Row]) -> list[tuple[str, list[Row]]]:
    """Selected rows grouped by project id, in first-seen order. A row with
    no id stands alone: it cannot be shown to share one (R6)."""
    groups: dict[str, list[Row]] = {}
    for row in rows:
        key = row.project_id or f"(no id) row {row.index}"
        groups.setdefault(key, []).append(row)
    return list(groups.items())


def mw_by_largest_per_id(rows: list[Row]) -> Decimal:
    """The second reading of R6: each distinct project id once, keeping the
    largest published capacity among its rows."""
    total = ZERO
    for _key, members in by_id(rows):
        capacities = [r.mw for r in members if r.mw is not None]
        if capacities:
            total += max(capacities)
    return total


def census(rows: list[dict[str, object]], as_of: date) -> dict[str, Any]:
    """The census of one copy: what it says is past its date and not Built."""
    selected: list[Row] = []
    dated = undated = built_dated = future_not_built = 0
    future_mw = scoping_mw = ZERO
    future_rows = scoping_rows = 0
    for index, row in enumerate(rows):
        effective = parse_date(row.get("MW Effective From"))
        if effective is None:
            undated += 1
            continue
        dated += 1
        if effective >= as_of:
            future_rows += 1
            capacity = stage_mw(row)
            if capacity is not None:
                future_mw += capacity
                if status(row).casefold() == SCOPING:
                    scoping_mw += capacity
            if status(row).casefold() == SCOPING:
                scoping_rows += 1
        if is_built(row):
            built_dated += 1
            continue
        if effective >= as_of:
            future_not_built += 1
            continue
        selected.append(selected_row(index, row, effective))

    mw = total_mw(selected)
    ids = by_id(selected)
    repeated = [{"project_id": key, "rows": members} for key, members in ids if len(members) > 1]
    mw_ids = mw_by_largest_per_id(selected)
    swapped = [r for r in selected if r.effective_swapped is not None]
    swapped_future = [
        r for r in swapped if r.effective_swapped is not None and r.effective_swapped >= as_of
    ]
    swapped_future_mw = total_mw(swapped_future)
    checks = {
        "C2 dated plus undated is every row": dated + undated == len(rows),
        "C3 the four classes partition every row": (
            len(selected) + future_not_built + built_dated + undated == len(rows)
        ),
    }
    falsifiers = {
        "F1 swapped dates could move more than a fifth of the selected MW to the future": (
            mw > ZERO and swapped_future_mw / mw > F1_SWAP_SHARE
        ),
        "F3 the two readings of the unit differ by more than a tenth": (
            mw > ZERO and abs(mw - mw_ids) / mw > F3_READING_SHARE
        ),
    }
    return {
        "as_of": as_of,
        "rows_total": len(rows),
        "undated": undated,
        "dated": dated,
        "dated_built": built_dated,
        "dated_not_built_future": future_not_built,
        "selected_rows": len(selected),
        "selected_mw": mw,
        "selected_rows_without_capacity": sum(1 for r in selected if r.mw is None),
        "selected_rows_zero_capacity": sum(1 for r in selected if r.mw == ZERO),
        "selected_rows_negative_capacity": sum(
            1 for r in selected if r.mw is not None and r.mw < ZERO
        ),
        "selected_mw_negative": sum(
            (r.mw for r in selected if r.mw is not None and r.mw < ZERO), ZERO
        ),
        "selected_rows_without_project_id": sum(1 for r in selected if not r.project_id),
        "distinct_project_ids": len(ids),
        "selected_mw_largest_per_id": mw_ids,
        "repeated_project_ids": repeated,
        "by_status": _group(selected, lambda r: r.status, "status"),
        "by_plant_type": _group(selected, lambda r: r.plant_type, "plant_type"),
        "by_year": sorted(
            _group(selected, lambda r: r.effective.year, "year"), key=lambda g: g["year"]
        ),
        "earliest": sorted(selected, key=lambda r: (r.effective, r.project_name, r.index))[
            :EARLIEST_SHOWN
        ],
        "swap_sensitivity": {
            "rows_with_a_swapped_reading": len(swapped),
            "mw_with_a_swapped_reading": total_mw(swapped),
            "rows_swapped_reading_not_past": len(swapped_future),
            "mw_swapped_reading_not_past": swapped_future_mw,
        },
        "scale": {
            "rows_dated_on_or_after_as_of": future_rows,
            "mw_dated_on_or_after_as_of": future_mw,
            "rows_scoping_dated_on_or_after_as_of": scoping_rows,
            "mw_scoping_dated_on_or_after_as_of": scoping_mw,
        },
        "checks": checks,
        "falsifiers": falsifiers,
        "rows": selected,
    }


# --------------------------------------------------------------- the exhibit
# Below takes no part in the census. It reads the evidence of certificates
# already issued under 014 and states one categorical fact about it.

#: What separates the exhibit project's row, in the copies where it shared a
#: name, from the coal station beside it (plant type "Coal") and from the
#: storage project that took the name in January 2024 (plant type "Energy
#: Storage System; PV Array"): its published plant type names a gas turbine
#: plant, or the hybrid label the register used for it in 2020 and 2021.
THERMAL_MARKERS: Final = ("ccgt", "ocgt", "hybrid")


def names_a_gas_turbine_plant(plant_type: object) -> bool:
    """Whether a published plant type names a gas turbine plant or the
    register's hybrid label. A selection over certificate evidence, stated
    openly so that a reader can change it and rerun."""
    printed = text(plant_type).casefold()
    return any(marker in printed for marker in THERMAL_MARKERS)


def status_trace(extracts: list[dict[str, Any]], matches: Any) -> dict[str, dict[str, Any]]:
    """Every status a certificate bundle's matching rows were published under,
    with how many rows carried it and the first and last copy that did.

    `extracts` are the bundle's `extracts.ndjson` lines (one per copy
    consulted, with the matching rows as published); `matches` decides which
    of a copy's rows are the project's.
    """
    trace: dict[str, dict[str, Any]] = {}
    for copy in extracts:
        for row in copy["rows"]:
            if not matches(row):
                continue
            seen = trace.setdefault(
                row["Project status"],
                {"rows": 0, "first_copy": copy["t_public"], "last_copy": copy["t_public"]},
            )
            seen["rows"] += 1
            seen["last_copy"] = copy["t_public"]
    return trace
