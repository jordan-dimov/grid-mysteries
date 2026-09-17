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
