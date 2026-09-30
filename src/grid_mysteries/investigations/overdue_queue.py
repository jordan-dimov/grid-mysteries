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

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.sources.tec_register import (
    normalise,
    normalise_stage,
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
    with the rows that carried it and the copies they appeared in.

    `extracts` are the bundle's `extracts.ndjson` lines (one per copy
    consulted, with the matching rows as published); `matches` decides which
    of a copy's rows are the project's. Copies are listed, not just counted,
    because two bundles may consult the same copy — a project split into
    stages has one row per stage — and the copies are what a reader
    aggregates across bundles without double counting.
    """
    trace: dict[str, dict[str, Any]] = {}
    for copy in extracts:
        for row in copy["rows"]:
            if not matches(row):
                continue
            seen = trace.setdefault(row["Project status"], {"rows": 0, "copies": []})
            seen["rows"] += 1
            if copy["t_public"] not in seen["copies"]:
                seen["copies"].append(copy["t_public"])
    for seen in trace.values():
        seen["copies"].sort()
        seen["first_copy"] = seen["copies"][0]
        seen["last_copy"] = seen["copies"][-1]
    return trace


def distinct_copies(traces: list[dict[str, dict[str, Any]]]) -> list[str]:
    """The copies any of these traces saw the project in, each counted once."""
    return sorted({copy for trace in traces for seen in trace.values() for copy in seen["copies"]})


# ----------------------------------------------------------- the Gate column
# Version 2 of the declaration (SHA-256 `82856d65…`). It adds one dimension
# over the copy version 1 already read, and changes nothing version 1 did:
# the selected rows are version 1's, unchanged, and `Row` gains no field, so
# the committed `rows.ndjson` still recomputes byte for byte.

GATE_COLUMN: Final = "Gate"
#: R9. The register prints `1` and `2`; NESO's pinned definition names
#: "Gate 1" and "Gate 2". That mapping is the one interpretation this
#: version makes, and the page says so. Any other non-blank value maps to
#: nothing and is reported under its printed spelling (F4).
GATE_TIERS: Final[dict[str, str]] = {"1": "Gate 1", "2": "Gate 2"}
CONFIRMED_TIER: Final = "2"
#: F5: how much of the overdue Gate 2 MW may sit in rows sharing an id or a
#: name before the figure is published as both readings rather than one.
F5_REPETITION_SHARE: Final = Decimal("0.1")
#: F6: how many of the gated copies must be readable for G6 to be published.
F6_MIN_GATED_COPIES: Final = 3
SHARE_QUANTUM: Final = Decimal("0.0001")


def gate_of(row: dict[str, object]) -> str:
    """The Gate cell as printed, whitespace collapsed (R8). Blank is blank."""
    return text(row.get(GATE_COLUMN))


def tier_of(printed: str) -> str | None:
    """The tier a printed Gate cell names, or None for a blank and for any
    value NESO's definition does not cover (R9, R10)."""
    return GATE_TIERS.get(printed)


def share(part: Decimal | int, whole: Decimal | int) -> Decimal | None:
    """A share as a fraction, or None when the denominator is zero. R11
    forbids one share standing for another, so callers ask for each."""
    if not whole:
        return None
    return (Decimal(part) / Decimal(whole)).quantize(SHARE_QUANTUM)


@dataclass(frozen=True)
class Reading:
    """What one copy of the register published for one row."""

    t_public: str
    found: bool
    gate: str
    status: str
    effective_as_published: str
    effective: date | None


@dataclass(frozen=True)
class GateRow:
    """A selected row in the confirmed tier, with its reading in every copy
    that carries a Gate column (G4, G6)."""

    index: int
    project_name: str
    connection_site: str
    stage: str
    plant_type: str
    status: str
    project_id: str
    project_number: str
    mw: Decimal | None
    effective: date
    effective_as_published: str
    gate: str
    tier: str | None
    readings: tuple[Reading, ...]
    #: The first gated copy whose Gate cell reads the confirmed tier, and what
    #: that copy published as the date then. Arithmetic over `readings`, not a
    #: new selection: it is what R12 asks the four copies.
    first_copy_in_the_tier: str | None
    date_when_first_in_the_tier: date | None
    already_past_when_first_in_the_tier: bool | None
    #: Every distinct date the gated copies published for this row, parsed. More
    #: than one means the register has moved the date or spelled it two ways.
    dates_across_gated_copies: tuple[date, ...]
    #: Those of them that are not past the as-of date. A row with one is a row
    #: some copy of the register says is not overdue at all.
    dates_across_gated_copies_not_past: tuple[date, ...]
    #: True when such a date is exactly the day-month swapped reading of the
    #: date this copy prints, so the disagreement is a spelling, not a move.
    a_not_past_date_is_the_day_month_swap: bool


def identity_key(row: dict[str, object]) -> tuple[str, str]:
    """How a selected row is found again in another copy (G6).

    Version 2 did not pre-name a matching rule, and the page says so. The
    rule used is the only identity this investigation has already declared:
    the project id on its 15-character form (R6) with the register's stage.
    A row with no project id falls back to its normalised name and site with
    the stage; the census records how many selected rows have no id, and on
    this copy that is none, so the fallback does no work here.
    """
    pid = project_id(row)
    if pid:
        return (f"id:{pid}", normalise_stage(row.get("Stage")))
    return (
        "name:" + normalise(row.get("Project Name")) + "|" + normalise(row.get("Connection Site")),
        normalise_stage(row.get("Stage")),
    )


def entered_the_tier(readings: tuple[Reading, ...]) -> dict[str, Any]:
    """When a row's Gate cell first read the confirmed tier, what date it
    carried then, and whether that date had already passed (R12).

    Nothing is inferred from a blank: the question asked is only whether the
    cell read the confirmed tier, which is a fact about the printed value.
    """
    first = next((r for r in readings if r.gate == CONFIRMED_TIER), None)
    if first is None:
        return {
            "first_copy_in_the_tier": None,
            "date_when_first_in_the_tier": None,
            "already_past_when_first_in_the_tier": None,
        }
    published = first.effective
    return {
        "first_copy_in_the_tier": first.t_public,
        "date_when_first_in_the_tier": published,
        "already_past_when_first_in_the_tier": (
            None if published is None else published < date.fromisoformat(first.t_public)
        ),
    }


def readings_across(
    key: tuple[str, str], gated: list[tuple[str, list[dict[str, object]]]]
) -> tuple[Reading, ...]:
    """One reading per gated copy, in date order; a copy with no matching row
    is recorded as an absence, never guessed."""
    out = []
    for t_public, rows in gated:
        match = next((r for r in rows if identity_key(r) == key), None)
        out.append(
            Reading(
                t_public=t_public,
                found=match is not None,
                gate=gate_of(match) if match else "",
                status=status(match) if match else "",
                effective_as_published=text(match.get("MW Effective From")) if match else "",
                effective=parse_date(match.get("MW Effective From")) if match else None,
            )
        )
    return tuple(out)


def _gate_table(
    items: list[tuple[str, Decimal | None]], denominators: dict[str, tuple[int, Decimal]]
) -> list[dict[str, Any]]:
    """Rows and MW per printed Gate value, each with the two shares R11
    requires, against the denominators the caller names."""
    groups: dict[str, list[Decimal | None]] = {}
    for printed, capacity in items:
        groups.setdefault(printed, []).append(capacity)
    out = []
    for printed, capacities in groups.items():
        rows = len(capacities)
        total = sum((c for c in capacities if c is not None), ZERO)
        entry: dict[str, Any] = {
            "gate": printed,
            "tier": tier_of(printed),
            "rows": rows,
            "mw": total,
        }
        for name, (denom_rows, denom_mw) in denominators.items():
            entry[f"row_share_of_{name}"] = share(rows, denom_rows)
            entry[f"capacity_share_of_{name}"] = share(total, denom_mw)
        out.append(entry)
    return sorted(out, key=lambda g: (-g["mw"], g["gate"]))


def _confirmed_row(
    row: Row, printed_gate: str, readings: tuple[Reading, ...], as_of: date
) -> GateRow:
    """One selected row in the confirmed tier, with its reading in every gated
    copy and what those readings say about when it entered the tier."""
    dates = tuple(sorted({x.effective for x in readings if x.effective is not None}))
    not_past = tuple(d for d in dates if d >= as_of)
    return GateRow(
        index=row.index,
        project_name=row.project_name,
        connection_site=row.connection_site,
        stage=row.stage,
        plant_type=row.plant_type,
        status=row.status,
        project_id=row.project_id,
        project_number=row.project_number,
        mw=row.mw,
        effective=row.effective,
        effective_as_published=row.effective_as_published,
        gate=printed_gate,
        tier=tier_of(printed_gate),
        readings=readings,
        dates_across_gated_copies=dates,
        dates_across_gated_copies_not_past=not_past,
        a_not_past_date_is_the_day_month_swap=row.effective_swapped in not_past,
        **entered_the_tier(readings),
    )


def gate_census(
    rows: list[dict[str, object]],
    census_result: dict[str, Any],
    gated: list[tuple[str, list[dict[str, object]]]],
) -> dict[str, Any]:
    """The Gate cross-tab over the copy version 1 read (G1 to G6).

    `rows` is that copy's rows; `census_result` is version 1's census over
    the same rows, whose selection is taken as given and never recomputed;
    `gated` are the copies carrying a Gate column, oldest first.
    """
    selected = census_result["rows"]
    as_of = census_result["as_of"]
    whole = _gate_table([(gate_of(r), stage_mw(r)) for r in rows], {})
    whole_by_gate = {g["gate"]: (g["rows"], g["mw"]) for g in whole}

    overdue_rows = len(selected)
    overdue_mw = total_mw(selected)
    overdue_items = [(gate_of(rows[r.index]), r.mw) for r in selected]
    overdue = _gate_table(overdue_items, {"overdue": (overdue_rows, overdue_mw)})
    for entry in overdue:
        in_copy = whole_by_gate.get(entry["gate"], (0, ZERO))
        entry["rows_in_copy"] = in_copy[0]
        entry["mw_in_copy"] = in_copy[1]
        entry["row_share_of_its_gate"] = share(entry["rows"], in_copy[0])
        entry["capacity_share_of_its_gate"] = share(entry["mw"], in_copy[1])

    by_gate_status: dict[tuple[str, str], list[Decimal | None]] = {}
    for r in selected:
        by_gate_status.setdefault((gate_of(rows[r.index]), r.status), []).append(r.mw)
    cross_entries: list[dict[str, Any]] = [
        {
            "gate": g,
            "tier": tier_of(g),
            "status": st,
            "rows": len(caps),
            "mw": sum((c for c in caps if c is not None), ZERO),
        }
        for (g, st), caps in by_gate_status.items()
    ]
    cross = sorted(cross_entries, key=lambda e: (e["gate"], -Decimal(e["mw"]), e["status"]))

    confirmed = [
        _confirmed_row(
            r,
            gate_of(rows[r.index]),
            readings_across(identity_key(rows[r.index]), gated),
            as_of,
        )
        for r in selected
        if gate_of(rows[r.index]) == CONFIRMED_TIER
    ]
    confirmed = sorted(confirmed, key=lambda g: (-(g.mw or ZERO), g.project_name, g.index))
    confirmed_mw = sum((g.mw for g in confirmed if g.mw is not None), ZERO)

    shared_id = _repeats(confirmed, lambda g: g.project_id)
    shared_name = _repeats(confirmed, lambda g: normalise(g.project_name))
    repeated_mw = sum(
        (g.mw for group in shared_id + shared_name for g in group["rows"] if g.mw is not None),
        ZERO,
    )
    unknown = sorted({g["gate"] for g in whole if g["gate"] and tier_of(g["gate"]) is None})
    # What the four gated copies say, in aggregate (R12). Arithmetic over G6.
    already_past = [g for g in confirmed if g.already_past_when_first_in_the_tier]
    disagree = [g for g in confirmed if len(g.dates_across_gated_copies) > 1]
    not_past_somewhere = [g for g in confirmed if g.dates_across_gated_copies_not_past]
    not_past_mw = sum((g.mw for g in not_past_somewhere if g.mw is not None), ZERO)
    g6_summary = {
        "rows": len(confirmed),
        "rows_seen_in_the_tier_in_a_gated_copy": sum(
            1 for g in confirmed if g.first_copy_in_the_tier
        ),
        "rows_whose_date_had_already_passed_when_first_in_the_tier": len(already_past),
        "mw_whose_date_had_already_passed_when_first_in_the_tier": sum(
            (g.mw for g in already_past if g.mw is not None), ZERO
        ),
        "rows_whose_gated_copies_publish_more_than_one_date": len(disagree),
        "mw_whose_gated_copies_publish_more_than_one_date": sum(
            (g.mw for g in disagree if g.mw is not None), ZERO
        ),
        "rows_a_gated_copy_publishes_as_not_past": len(not_past_somewhere),
        "mw_a_gated_copy_publishes_as_not_past": not_past_mw,
        "mw_if_those_rows_are_read_as_not_past": confirmed_mw - not_past_mw,
        "rows_if_those_rows_are_read_as_not_past": len(confirmed) - len(not_past_somewhere),
    }
    return {
        "g1_copy_by_gate": whole,
        "g2_overdue_by_gate": overdue,
        "g3_overdue_by_gate_and_status": cross,
        "g4_confirmed_tier_overdue": confirmed,
        "g5_repetition": {
            "sharing_a_project_id": shared_id,
            "sharing_a_project_name": shared_name,
            "mw_in_repeated_rows": repeated_mw,
        },
        "g6_gated_copies": [t for t, _r in gated],
        "g6_summary": g6_summary,
        "confirmed_tier_overdue_rows": len(confirmed),
        "confirmed_tier_overdue_mw": confirmed_mw,
        "unknown_gate_values": unknown,
        "falsifiers": {
            "F4 the Gate column carries a value the pinned definition does not cover": bool(
                unknown
            ),
            "F5 repeated ids or names hold more than a tenth of the overdue Gate 2 MW": (
                confirmed_mw > ZERO and repeated_mw / confirmed_mw > F5_REPETITION_SHARE
            ),
            "F6 fewer than three gated copies are readable": len(gated) < F6_MIN_GATED_COPIES,
        },
    }


def _repeats(confirmed: list[GateRow], key: Any) -> list[dict[str, Any]]:
    """Groups of selected confirmed-tier rows that share a key, with the MW
    the group would contribute if its largest row alone were counted (G5)."""
    groups: dict[str, list[GateRow]] = {}
    for row in confirmed:
        k = key(row)
        if k:
            groups.setdefault(k, []).append(row)
    return [
        {
            "key": k,
            "rows": members,
            "mw_summed": sum((g.mw for g in members if g.mw is not None), ZERO),
            "mw_largest": max((g.mw for g in members if g.mw is not None), default=ZERO),
        }
        for k, members in groups.items()
        if len(members) > 1
    ]


# ------------------------------------------------------------- version 3
# Version 3 of the declaration (SHA-256 `dd396986…`). The same method, R3 to
# R12 and G1 to G6, applied to the reference copy (CKAN `last_modified`
# 2026-09-25) and to the first captured copy dated on or after 2026-09-29,
# with one declared comparison between them (D1, D2). Nothing above changes:
# the method check C10 requires this code to reproduce versions 1 and 2 on
# the copy they read, byte for byte.

#: R1′: the next copy is the earliest captured copy dated on or after this day.
NEXT_COPY_FROM: Final = date(2026, 9, 29)
#: R1′: if no such copy is captured by this day, no next census is run.
NEXT_COPY_DEADLINE: Final = date(2026, 10, 31)
#: N0: what the next copy's schema pass must show before its census runs.
N0_STATUSES: Final = frozenset(
    {
        "Awaiting Consents",
        "Built",
        "Consents Approved",
        "Scoping",
        "Under Construction/Commissioning",
    }
)
N0_GATES: Final = frozenset({"", "1", "2"})
N0_DATE_SPELLINGS: Final = frozenset({"uk", "blank"})
#: F9: the share of a copy's selected rows that may be ambiguous or carry no
#: project id before D2 is withheld and the comparison is D1 alone.
F9_UNMATCHABLE_SHARE: Final = Decimal("0.1")
#: F10: the share of a copy's selected MW the filename reading may move
#: before that copy's headline is published as a range.
F10_FILENAME_SHARE: Final = Decimal("0.1")

_MONTHS: Final = {
    name: number
    for number, name in enumerate(
        (
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ),
        start=1,
    )
}


def filename_date(filename: str) -> date | None:
    """The date NESO's filename names (`tec-register-24-september-2026.csv`),
    or None when the filename names none. R2′ reports it; it never sets the
    as-of date, which is the copy's CKAN `last_modified` date."""
    match = re.search(r"(\d{1,2})-([a-z]+)-(\d{4})", filename.casefold())
    if not match or match.group(2) not in _MONTHS:
        return None
    try:
        return date(int(match.group(3)), _MONTHS[match.group(2)], int(match.group(1)))
    except ValueError:
        return None


def filename_sensitivity(census_result: dict[str, Any], named: date | None) -> dict[str, Any]:
    """R2′: the selected rows that are past on the as-of reading and not on
    the filename's, i.e. dated on or after the filename's date and before the
    as-of date. Empty when the two dates agree or the filename names none."""
    as_of = census_result["as_of"]
    moved = (
        [r for r in census_result["rows"] if named <= r.effective < as_of]
        if named is not None and named < as_of
        else []
    )
    mw = total_mw(moved)
    selected_mw = census_result["selected_mw"]
    return {
        "filename_date": named,
        "as_of": as_of,
        "differs": named is not None and named != as_of,
        "rows": len(moved),
        "mw": mw,
        "moved": sorted(moved, key=lambda r: (r.effective, r.project_name, r.index)),
        "F10 the filename reading moves more than a tenth of the selected MW": (
            selected_mw > ZERO and mw / selected_mw > F10_FILENAME_SHARE
        ),
    }


def next_copy(entries: list[dict[str, Any]], on_or_after: date = NEXT_COPY_FROM) -> dict | None:
    """R1′: the captured copy with the earliest `t_public` on or after the
    date, or None. `entries` are `tec_register.capture_entries`."""
    later = [e for e in entries if date.fromisoformat(e["t_public"]) >= on_or_after]
    return min(later, key=lambda e: (e["t_public"], e["fetched_at"]), default=None)


def capture_gaps(days_with_a_record: set[date], first: date, last: date) -> list[date]:
    """R1′: the days from `first` to `last` inclusive on which the capture's
    manifests hold no TEC record at all, neither a copy nor the metadata
    record of an unchanged day."""
    gaps = []
    day_ = first
    while day_ <= last:
        if day_ not in days_with_a_record:
            gaps.append(day_)
        day_ = date.fromordinal(day_.toordinal() + 1)
    return gaps


def n0(copy_report: dict[str, Any], columns: list[str]) -> dict[str, bool]:
    """N0: the conditions the next copy's schema pass must meet before its
    census is computed. `copy_report` is that copy's entry in the capture
    schema report; `columns` are the fifteen of the current era."""
    spellings = {k for k, v in copy_report["date_spellings"].items() if v}
    return {
        "N0 the same fifteen columns": sorted(copy_report["columns"]) == sorted(columns),
        "N0 date spellings only uk and blank": spellings <= N0_DATE_SPELLINGS,
        "N0 only the five Project Status spellings": (
            set(copy_report["project_status"]) <= N0_STATUSES
        ),
        "N0 only 1, 2 and blank under Gate": set(copy_report.get("gate") or {}) <= N0_GATES,
        "N0 no flag": not copy_report["flags"],
    }


#: Amendment 1 to version 3 (`35b74e13…`), A1: for the next copy, N0's
#: spelling condition is met by `iso-dash` and blank.
A1_DATE_SPELLINGS: Final = frozenset({"iso-dash", "blank"})
A1_SPELLING_CONDITION: Final = "N0 date spellings only iso-dash and blank (amendment 1, A1)"


def n0_amended(copy_report: dict[str, Any], columns: list[str]) -> dict[str, bool]:
    """N0 as amendment 1 reads it for the next copy: the spelling condition is
    met by `iso-dash` and blank; the other four conditions stand unchanged."""
    verdict = n0(copy_report, columns)
    del verdict["N0 date spellings only uk and blank"]
    spellings = {k for k, v in copy_report["date_spellings"].items() if v}
    return {A1_SPELLING_CONDITION: spellings <= A1_DATE_SPELLINGS, **verdict}


def _figures(census_result: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    scale = census_result["scale"]
    return {
        "as_of": census_result["as_of"],
        "selected_rows": census_result["selected_rows"],
        "selected_mw": census_result["selected_mw"],
        "distinct_project_ids": census_result["distinct_project_ids"],
        "selected_mw_largest_per_id": census_result["selected_mw_largest_per_id"],
        "gate2_overdue_rows": gate["confirmed_tier_overdue_rows"],
        "gate2_overdue_mw": gate["confirmed_tier_overdue_mw"],
        "mw_dated_on_or_after_as_of": scale["mw_dated_on_or_after_as_of"],
        "mw_scoping_dated_on_or_after_as_of": scale["mw_scoping_dated_on_or_after_as_of"],
        "rows_dated_on_or_after_as_of": scale["rows_dated_on_or_after_as_of"],
        "rows_scoping_dated_on_or_after_as_of": scale["rows_scoping_dated_on_or_after_as_of"],
    }


def side_by_side(
    reference: tuple[dict[str, Any], dict[str, Any]], later: tuple[dict[str, Any], dict[str, Any]]
) -> dict[str, Any]:
    """D1: each copy's figures and the difference, next minus reference, each
    printed with both as-of dates. `reference` and `later` are (census, gate)."""
    ref, nxt = _figures(*reference), _figures(*later)
    return {
        "reference": ref,
        "next": nxt,
        "difference_next_minus_reference": {k: nxt[k] - ref[k] for k in ref if k != "as_of"},
        "as_of_dates": [ref["as_of"], nxt["as_of"]],
        "days_between": (nxt["as_of"] - ref["as_of"]).days,
    }


def _keyed(rows: list[dict[str, object]]) -> dict[tuple[str, str], list[int]]:
    keys: dict[tuple[str, str], list[int]] = {}
    for index, r in enumerate(rows):
        keys.setdefault(identity_key(r), []).append(index)
    return keys


@dataclass(frozen=True)
class Transition:
    """One selected row in D2: its key, the class it fell in, and what each
    copy printed for it (None where the copy carries no row with that key)."""

    key: str
    stage: str
    klass: str
    reference: Row | None
    next: Row | None
    #: What the other copy printed, as published, when that copy's row is not
    #: selected: status, date as printed and parsed, and MW.
    other_status: str
    other_effective_as_published: str
    other_effective: date | None
    other_mw: Decimal | None


def _as_row(index: int, row: dict[str, object]) -> Row | None:
    effective = parse_date(row.get("MW Effective From"))
    return selected_row(index, row, effective) if effective is not None else None


def transitions(
    ref_rows: list[dict[str, object]],
    ref: dict[str, Any],
    next_rows: list[dict[str, object]],
    nxt: dict[str, Any],
) -> dict[str, Any]:
    """D2: selected rows in either copy, matched by `identity_key`, classed.

    Reference only: the next copy has no row with the key; it prints `Built`;
    it prints a date on or after the next as-of date; or other. Next only:
    (a) the reference copy has no row with the key; (b) both copies print the
    same date, on or after the reference as-of date and before the next one,
    *the date arrived*; (c) other. A key on more than one row of either copy
    is ambiguous and in no class. C11 holds when the classes, with the
    ambiguous rows listed beside them, sum to each census's own totals.
    """
    ref_keys, next_keys = _keyed(ref_rows), _keyed(next_rows)
    ref_sel = {identity_key(ref_rows[r.index]): r for r in ref["rows"]}
    next_sel = {identity_key(next_rows[r.index]): r for r in nxt["rows"]}
    ambiguous_keys = {
        k
        for k in set(ref_sel) | set(next_sel)
        if len(ref_keys.get(k, [])) > 1 or len(next_keys.get(k, [])) > 1
    }
    # A key on two selected rows of one copy collapses in the dicts above, so
    # the ambiguous rows are read from the selections themselves.
    ambiguous_ref = [r for r in ref["rows"] if identity_key(ref_rows[r.index]) in ambiguous_keys]
    ambiguous_next = [r for r in nxt["rows"] if identity_key(next_rows[r.index]) in ambiguous_keys]

    out: list[Transition] = []

    def other(row: dict[str, object] | None) -> dict[str, Any]:
        if row is None:
            return {
                "other_status": "",
                "other_effective_as_published": "",
                "other_effective": None,
                "other_mw": None,
            }
        return {
            "other_status": status(row),
            "other_effective_as_published": text(row.get("MW Effective From")),
            "other_effective": parse_date(row.get("MW Effective From")),
            "other_mw": stage_mw(row),
        }

    for key in sorted(set(ref_sel) | set(next_sel)):
        if key in ambiguous_keys:
            continue
        r, n = ref_sel.get(key), next_sel.get(key)
        label = key[0]
        if r and n:
            out.append(Transition(label, key[1], "in both", r, n, **other(None)))
            continue
        if r:
            match = next_keys.get(key)
            there = next_rows[match[0]] if match else None
            if there is None:
                klass = "reference only: no row with that key"
            elif is_built(there):
                klass = "reference only: Built"
            elif (d := parse_date(there.get("MW Effective From"))) is not None and d >= nxt[
                "as_of"
            ]:
                klass = "reference only: date on or after the next as-of date"
            else:
                klass = "reference only: other"
            out.append(Transition(label, key[1], klass, r, None, **other(there)))
            continue
        assert n is not None
        match = ref_keys.get(key)
        before = ref_rows[match[0]] if match else None
        if before is None:
            klass = "next only: (a) no row with that key in the reference copy"
        elif (
            parse_date(before.get("MW Effective From")) == n.effective
            and ref["as_of"] <= n.effective < nxt["as_of"]
        ):
            klass = "next only: (b) the date arrived"
        else:
            klass = "next only: (c) other"
        out.append(Transition(label, key[1], klass, None, n, **other(before)))

    classes: dict[str, dict[str, Any]] = {}
    for t in out:
        entry = classes.setdefault(
            t.klass, {"rows": 0, "mw_reference": ZERO, "mw_next": ZERO, "members": []}
        )
        entry["rows"] += 1
        if t.reference and t.reference.mw is not None:
            entry["mw_reference"] += t.reference.mw
        if t.next and t.next.mw is not None:
            entry["mw_next"] += t.next.mw
        entry["members"].append(t)

    def side(which: str) -> tuple[int, Decimal]:
        members = [t for t in out if getattr(t, which) is not None]
        return len(members), sum(
            (getattr(t, which).mw for t in members if getattr(t, which).mw is not None), ZERO
        )

    ref_classed = side("reference")
    next_classed = side("next")
    c11 = (
        ref_classed[0] + len(ambiguous_ref) == ref["selected_rows"]
        and ref_classed[1] + total_mw(ambiguous_ref) == ref["selected_mw"]
        and next_classed[0] + len(ambiguous_next) == nxt["selected_rows"]
        and next_classed[1] + total_mw(ambiguous_next) == nxt["selected_mw"]
    )
    unmatchable_ref = {r.index for r in ambiguous_ref} | {
        r.index for r in ref["rows"] if not r.project_id
    }
    unmatchable_next = {r.index for r in ambiguous_next} | {
        r.index for r in nxt["rows"] if not r.project_id
    }
    f9 = (
        ref["selected_rows"] > 0
        and Decimal(len(unmatchable_ref)) / ref["selected_rows"] > F9_UNMATCHABLE_SHARE
    ) or (
        nxt["selected_rows"] > 0
        and Decimal(len(unmatchable_next)) / nxt["selected_rows"] > F9_UNMATCHABLE_SHARE
    )
    return {
        "classes": dict(sorted(classes.items())),
        "ambiguous": {
            "keys": sorted(f"{k[0]} | stage {k[1] or '(blank)'}" for k in ambiguous_keys),
            "reference_rows": ambiguous_ref,
            "next_rows": ambiguous_next,
        },
        "unmatchable_rows": {"reference": len(unmatchable_ref), "next": len(unmatchable_next)},
        "classed_totals": {
            "reference": {"rows": ref_classed[0], "mw": ref_classed[1]},
            "next": {"rows": next_classed[0], "mw": next_classed[1]},
        },
        "checks": {"C11 D2's classes sum to each census's selected rows and MW": c11},
        "falsifiers": {
            "F9 more than a tenth of either copy's selected rows are ambiguous or have no id": f9
        },
    }


def gated_copies_for(
    journalled: list[dict[str, Any]], captured: list[dict[str, Any]], since: date, as_of: date
) -> list[dict[str, Any]]:
    """G6′: the gated copies version 2 read (`journalled`), then each captured
    copy dated later than `since` and no later than the copy under census,
    one reading per distinct digest, oldest first. Each copy is a dict with
    at least `t_public` (ISO date) and `sha256`."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for copy in journalled:
        if copy["sha256"] not in seen:
            out.append(copy)
            seen.add(copy["sha256"])
    for copy in captured:
        t_public = date.fromisoformat(copy["t_public"])
        if since < t_public <= as_of and copy["sha256"] not in seen:
            out.append(copy)
            seen.add(copy["sha256"])
    return sorted(out, key=lambda c: c["t_public"])


def settles_entry_into_the_tier(row: dict[str, Any]) -> dict[str, Any]:
    """R12 over one committed G4 row (its evidence line, readings included):
    the last copy held before the first copy whose Gate cell reads the
    confirmed tier, and whether the date was already past in that copy. If it
    was, the row entered the tier already past in the copies held; if not, or
    if no earlier copy is held, the copies do not settle it (the correction of
    2026-09-24). A blank Gate cell in the earlier copy is not interpreted."""
    first = row.get("first_copy_in_the_tier")
    published = row.get("date_when_first_in_the_tier")
    copies = [r["t_public"] for r in row["readings"]]
    if not first or not published or first not in copies or copies.index(first) == 0:
        return {"previous_copy": None, "days_between": None, "settled": False}
    previous = copies[copies.index(first) - 1]
    return {
        "previous_copy": previous,
        "days_between": (date.fromisoformat(first) - date.fromisoformat(previous)).days,
        "settled": date.fromisoformat(str(published)) < date.fromisoformat(previous),
    }
