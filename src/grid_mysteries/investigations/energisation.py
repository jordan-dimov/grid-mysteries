"""020 — Did it energise: the register-only part, pure.

Population P1 and P2 of `investigations/020-did-it-energise/DECLARATION.md`
(SHA-256 fb8a3428…) as functions of the kept copies under 014's content
identity (`tec.identity.ContentIdentity`, rule `tec-identity-content-v1`),
and the register-only measure the sponsor asked for first: for every unit
that moves to `Built`, the last date the register printed before it did.

No I/O. The runner reads the copies, applies 014's reading rules (the
partial-export rule and the day-month swap test through
`connection_slippage.series` and `tec.analysis.kept`) and hands the kept
sequence here.
"""

from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.investigations.connection_slippage import identity as project_group
from grid_mysteries.investigations.overdue_queue import project_id, text
from grid_mysteries.sources.tec_register import parse_decimal
from grid_mysteries.tec import identity as content

DECLARATION_SHA256: Final = "fb8a3428749a73997745e4e852ba64b7a7326afd406528d9fe6315116b13bb2a"
AMENDMENT_1_PREFIX: Final = "cc01e3cf"
AMENDMENT_2_PREFIX: Final = "3ef7240c"
BUILT: Final = "built"
CONFIRMED_GATE: Final = "2"


def is_built(row: dict[str, object]) -> bool:
    return text(row.get("Project Status")).casefold() == BUILT


@dataclass(frozen=True)
class Sighting:
    """One unit in one kept copy."""

    t_public: date
    sha256: str
    status: str
    effective: date | None
    raw_effective: str
    row: dict[str, object]


@dataclass(frozen=True)
class Transition:
    """P1: a unit whose status reads `Built` in a copy and did not in the
    copy before, or `Built` at first sight."""

    regime: str
    unit: str
    klass: str  # transition | built-at-first-sight
    first_built: date
    first_built_sha256: str
    last_before: date | None
    last_before_sha256: str | None
    last_before_status: str | None
    last_date_before_built: date | None
    last_raw_date_before_built: str | None
    first_seen: date
    project_name: str
    customer: str
    site: str
    stage: str
    mw: Decimal | None
    project_id: str
    plant_type: str
    agreement_type: str
    host_to: str
    date_at_first_built: date | None

    @property
    def months_from_last_date_to_built_copy(self) -> Decimal | None:
        """The register-only measure: months from the last date printed
        before `Built` to the first copy printing `Built`. Positive means
        the register said `Built` after the date it had carried; negative
        means before it."""
        if self.last_date_before_built is None:
            return None
        days = (self.first_built - self.last_date_before_built).days
        return (Decimal(days) / Decimal("30.4375")).quantize(Decimal("0.1"))


def sightings(
    kept: list[tuple[str, date, str, list[dict[str, object]], bool]],
) -> dict[str, dict[str, list[Sighting]]]:
    """Step 014's content identity over the kept copies, regime by regime,
    and return every unit's sightings in publication order:
    `{regime: {unit: [Sighting, ...]}}`. `kept` items are
    (regime, t_public, sha256, rows, swapped)."""
    out: dict[str, dict[str, list[Sighting]]] = defaultdict(lambda: defaultdict(list))
    carriers: dict[str, content.ContentIdentity] = {}
    for regime, t_public, sha256, rows, swapped in kept:
        carrier = carriers.setdefault(regime, content.ContentIdentity())
        entries = carrier.step(rows, swapped=swapped)
        for unit_name, unit in carrier.units.items():
            entry = entries[unit_name]
            out[regime][unit_name].append(
                Sighting(
                    t_public,
                    sha256,
                    text(unit.row.get("Project Status")),
                    entry.effective,
                    entry.raw_effective,
                    unit.row,
                )
            )
    return {r: dict(u) for r, u in out.items()}


def transitions(seen: dict[str, dict[str, list[Sighting]]]) -> list[Transition]:
    """P1 over every regime. A unit can transition once per regime: its
    first sighting reading `Built` after a sighting that did not. A unit
    `Built` at its first sighting is labelled, not measured. A unit that
    reads `Built`, then not, then `Built` again is one transition (the
    first), and the later flap is left to the sightings."""
    out: list[Transition] = []
    for regime, units in seen.items():
        for unit_name, seq in units.items():
            first_built_index = next(
                (i for i, s in enumerate(seq) if s.status.casefold() == BUILT), None
            )
            if first_built_index is None:
                continue
            first = seq[first_built_index]
            before = seq[first_built_index - 1] if first_built_index > 0 else None
            row = first.row
            out.append(
                Transition(
                    regime=regime,
                    unit=unit_name,
                    klass="transition" if before is not None else "built-at-first-sight",
                    first_built=first.t_public,
                    first_built_sha256=first.sha256,
                    last_before=before.t_public if before else None,
                    last_before_sha256=before.sha256 if before else None,
                    last_before_status=before.status if before else None,
                    last_date_before_built=before.effective if before else None,
                    last_raw_date_before_built=before.raw_effective if before else None,
                    first_seen=seq[0].t_public,
                    project_name=text(row.get("Project Name")),
                    customer=text(row.get("Customer Name")),
                    site=text(row.get("Connection Site")),
                    stage=text(row.get("Stage")),
                    mw=parse_decimal(row.get("MW Increase / Decrease")),
                    project_id=project_id(row),
                    plant_type=text(row.get("Plant Type")),
                    agreement_type=text(row.get("Agreement Type")),
                    host_to=text(row.get("HOST TO")),
                    date_at_first_built=first.effective,
                )
            )
    return sorted(out, key=lambda t: (t.first_built, t.regime, t.unit))


def gate_two_rows(rows: list[dict[str, object]]) -> list[dict[str, Any]]:
    """P2: the rows whose Gate cell prints `2` in the copy, as printed."""
    return [
        {
            "index": i,
            "project_id": project_id(r),
            "project_name": text(r.get("Project Name")),
            "customer": text(r.get("Customer Name")),
            "site": text(r.get("Connection Site")),
            "stage": text(r.get("Stage")),
            "mw": parse_decimal(r.get("MW Increase / Decrease")),
            "effective": text(r.get("MW Effective From")),
            "status": text(r.get("Project Status")),
            "plant_type": text(r.get("Plant Type")),
            "agreement_type": text(r.get("Agreement Type")),
            "host_to": text(r.get("HOST TO")),
        }
        for i, r in enumerate(rows)
        if text(r.get("Gate")) == CONFIRMED_GATE
    ]


def quantiles(values: list[Decimal]) -> dict[str, Decimal | int | None]:
    if not values:
        return {"n": 0, "min": None, "p25": None, "median": None, "p75": None, "max": None}
    s = sorted(values)
    n = len(s)

    def q(p: float) -> Decimal:
        return s[min(n - 1, int(p * (n - 1)))]

    return {"n": n, "min": s[0], "p25": q(0.25), "median": q(0.5), "p75": q(0.75), "max": s[-1]}


def summary(found: list[Transition]) -> dict[str, Any]:
    """The register-only figures: counts by class and regime, the months
    from the last printed date to the first `Built` copy (distribution, by
    year of the transition and by plant type), and the units whose printed
    date never moved before `Built`."""
    by_class: defaultdict[str, int] = defaultdict(int)
    by_regime: defaultdict[str, int] = defaultdict(int)
    measured = [
        t for t in found if t.klass == "transition" and t.last_date_before_built is not None
    ]
    undated = [t for t in found if t.klass == "transition" and t.last_date_before_built is None]
    months: list[Decimal] = [
        m for t in measured if (m := t.months_from_last_date_to_built_copy) is not None
    ]
    by_year: dict[str, list[Decimal]] = defaultdict(list)
    by_plant: dict[str, list[Decimal]] = defaultdict(list)
    for t in measured:
        m = t.months_from_last_date_to_built_copy
        if m is None:
            continue
        by_year[str(t.first_built.year)].append(m)
        by_plant[t.plant_type or "(blank)"].append(m)
    for t in found:
        by_class[t.klass] += 1
        by_regime[f"{t.regime}|{t.klass}"] += 1
    before = sum(1 for m in months if m < 0)
    within_six = sum(1 for m in months if 0 <= m <= 6)
    later = sum(1 for m in months if m > 6)
    mw_measured = sum((t.mw or Decimal(0)) for t in measured)
    return {
        "transitions": len(found),
        "by_class": dict(by_class),
        "by_regime_and_class": dict(sorted(by_regime.items())),
        "measured": len(measured),
        "measured_mw": mw_measured,
        "undated_before_built": len(undated),
        "months_last_date_to_built_copy": quantiles(months),
        "built_copy_before_the_date": before,
        "built_copy_within_six_months_after": within_six,
        "built_copy_later_than_six_months": later,
        "by_year_of_built_copy": {y: quantiles(v) for y, v in sorted(by_year.items())},
        "by_plant_type": {
            p: quantiles(v) for p, v in sorted(by_plant.items(), key=lambda kv: -len(kv[1]))
        },
    }


# ------------------------------------------------- amendment 1, A1: projects


@dataclass(frozen=True)
class ProjectTransition:
    """A1: a project (014's group) whose units first print `Built` in a kept
    copy, with the last dated capacity-bearing stage of the copy before."""

    regime: str
    project: str
    klass: (
        str  # transition | built-at-first-sight | undated-before-built | not-sighted-in-copy-before
    )
    first_built: date
    first_built_sha256: str
    copy_before: date | None
    copy_before_sha256: str | None
    reference_date: date | None
    earliest_date: date | None
    capacity_mw: Decimal
    stages_capacity_dated: int
    stages_capacity_undated: int
    stages_zero_mw: int
    stages_not_built_in_first_built_copy: int
    first_seen: date
    project_name: str
    customer: str
    site: str
    plant_type: str
    agreement_type: str
    host_to: str
    units: tuple[str, ...]

    def months(self, from_date: date | None) -> Decimal | None:
        if from_date is None:
            return None
        return (Decimal((self.first_built - from_date).days) / Decimal("30.4375")).quantize(
            Decimal("0.1")
        )

    @property
    def months_reference(self) -> Decimal | None:
        return self.months(self.reference_date)

    @property
    def months_earliest(self) -> Decimal | None:
        return self.months(self.earliest_date)


Copies = dict[date, list[tuple[str, Sighting]]]


def _projects(
    seen: dict[str, dict[str, list[Sighting]]], kept_order: dict[str, list[date]]
) -> Iterator[tuple[str, str, list[date], Copies, date, date | None]]:
    """Every project (014's group) with a first `Built` copy, regime by
    regime: (regime, project, its copy dates, its sightings per copy, the
    first `Built` copy, the kept copy immediately before it or None)."""
    for regime, units in seen.items():
        order = kept_order[regime]
        position = {t: i for i, t in enumerate(order)}
        by_project: dict[str, Copies] = defaultdict(lambda: defaultdict(list))
        for unit_name, seq in units.items():
            for s in seq:
                by_project[project_group(s.row)][s.t_public].append((unit_name, s))
        for project, copies in by_project.items():
            dates = sorted(copies)
            first_built = next(
                (t for t in dates if any(s.status.casefold() == BUILT for _, s in copies[t])), None
            )
            if first_built is None:
                continue
            previous_index = position[first_built] - 1
            before = order[previous_index] if previous_index >= 0 else None
            yield regime, project, dates, copies, first_built, before


def _mw(s: Sighting) -> Decimal:
    return parse_decimal(s.row.get("MW Increase / Decrease")) or Decimal(0)


def project_transitions(
    seen: dict[str, dict[str, list[Sighting]]], kept_order: dict[str, list[date]]
) -> list[ProjectTransition]:
    """A1 over every regime. `kept_order[regime]` is the publication order of
    the kept copies, so "the copy immediately before" is well defined."""
    out: list[ProjectTransition] = []
    for regime, project, dates, copies, first_built, before_date in _projects(seen, kept_order):
        here = copies[first_built]
        row = here[0][1].row
        sha = here[0][1].sha256
        not_built = sum(1 for _, s in here if s.status.casefold() != BUILT)
        common: dict[str, Any] = {
            "regime": regime,
            "project": project,
            "first_built": first_built,
            "first_built_sha256": sha,
            "first_seen": dates[0],
            "project_name": text(row.get("Project Name")),
            "customer": text(row.get("Customer Name")),
            "site": text(row.get("Connection Site")),
            "plant_type": text(row.get("Plant Type")),
            "agreement_type": text(row.get("Agreement Type")),
            "host_to": text(row.get("HOST TO")),
            "stages_not_built_in_first_built_copy": not_built,
            "units": tuple(sorted(u for u, _ in here)),
        }
        if first_built == dates[0]:
            out.append(
                ProjectTransition(
                    klass="built-at-first-sight",
                    copy_before=None,
                    copy_before_sha256=None,
                    reference_date=None,
                    earliest_date=None,
                    capacity_mw=Decimal(0),
                    stages_capacity_dated=0,
                    stages_capacity_undated=0,
                    stages_zero_mw=0,
                    **common,
                )
            )
            continue
        if before_date is None or before_date not in copies:
            out.append(
                ProjectTransition(
                    klass="not-sighted-in-copy-before",
                    copy_before=before_date,
                    copy_before_sha256=None,
                    reference_date=None,
                    earliest_date=None,
                    capacity_mw=Decimal(0),
                    stages_capacity_dated=0,
                    stages_capacity_undated=0,
                    stages_zero_mw=0,
                    **common,
                )
            )
            continue
        before = copies[before_date]
        capacity = [s for _, s in before if _mw(s) > 0]
        dated = [s.effective for s in capacity if s.effective is not None]
        zero = len(before) - len(capacity)
        cap_mw = sum((_mw(s) for s in capacity), Decimal(0))
        out.append(
            ProjectTransition(
                klass="transition" if dated else "undated-before-built",
                copy_before=before_date,
                copy_before_sha256=before[0][1].sha256,
                reference_date=max(dated) if dated else None,
                earliest_date=min(dated) if dated else None,
                capacity_mw=cap_mw,
                stages_capacity_dated=len(dated),
                stages_capacity_undated=len(capacity) - len(dated),
                stages_zero_mw=zero,
                **common,
            )
        )
    return sorted(out, key=lambda t: (t.first_built, t.regime, t.project))


def project_summary(found: list[ProjectTransition]) -> dict[str, Any]:
    by_class: defaultdict[str, int] = defaultdict(int)
    by_regime: defaultdict[str, int] = defaultdict(int)
    for t in found:
        by_class[t.klass] += 1
        by_regime[f"{t.regime}|{t.klass}"] += 1
    measured = [t for t in found if t.klass == "transition"]
    months: list[Decimal] = [m for t in measured if (m := t.months_reference) is not None]
    earliest: list[Decimal] = [m for t in measured if (m := t.months_earliest) is not None]
    by_year: dict[str, list[Decimal]] = defaultdict(list)
    by_plant: dict[str, list[Decimal]] = defaultdict(list)
    for t in measured:
        m = t.months_reference
        if m is None:
            continue
        by_year[str(t.first_built.year)].append(m)
        by_plant[t.plant_type or "(blank)"].append(m)
    return {
        "projects_with_a_built_sighting": len(found),
        "by_class": dict(by_class),
        "by_regime_and_class": dict(sorted(by_regime.items())),
        "measured": len(measured),
        "measured_capacity_mw": sum((t.capacity_mw for t in measured), Decimal(0)),
        "measured_with_a_split_status": sum(
            1 for t in measured if t.stages_not_built_in_first_built_copy
        ),
        "months_reference_to_built_copy": quantiles(months),
        "months_earliest_to_built_copy_sensitivity": quantiles(earliest),
        "built_copy_before_the_date": sum(1 for m in months if m < 0),
        "built_copy_within_six_months_after": sum(1 for m in months if 0 <= m <= 6),
        "built_copy_later_than_six_months": sum(1 for m in months if m > 6),
        "by_year_of_built_copy": {y: quantiles(v) for y, v in sorted(by_year.items())},
        "by_plant_type": {
            p: quantiles(v) for p, v in sorted(by_plant.items(), key=lambda kv: -len(kv[1]))
        },
    }


# ------------------------------------------------------------ amendment 2


def _months(to: date, from_date: date | None) -> Decimal | None:
    if from_date is None:
        return None
    return (Decimal((to - from_date).days) / Decimal("30.4375")).quantize(Decimal("0.1"))


@dataclass(frozen=True)
class Stage:
    """One capacity-bearing (MW > 0), dated stage of a project in the kept
    copy before its first `Built` copy."""

    unit: str
    stage: str
    mw: Decimal
    effective: date
    #: Dated strictly after the publication date of the first `Built` copy.
    later: bool


@dataclass(frozen=True)
class ProjectStages:
    """A1′ and A1″ (amendment 2): a measured project's capacity-bearing dated
    stages split by their date against the first `Built` copy's date, and
    the per-project measure twice: with the later stages (amendment 1's A1
    exactly) and without them."""

    regime: str
    project: str
    project_name: str
    plant_type: str
    first_built: date
    first_built_sha256: str
    copy_before: date
    copy_before_sha256: str
    capacity_mw: Decimal
    stages: tuple[Stage, ...]

    @property
    def later(self) -> tuple[Stage, ...]:
        return tuple(s for s in self.stages if s.later)

    @property
    def on_or_before(self) -> tuple[Stage, ...]:
        return tuple(s for s in self.stages if not s.later)

    @property
    def klass(self) -> str:
        return "only-later-stages" if not self.on_or_before else "transition"

    @property
    def later_mw(self) -> Decimal:
        return sum((s.mw for s in self.later), Decimal(0))

    @property
    def reference_with(self) -> date:
        return max(s.effective for s in self.stages)

    @property
    def earliest_with(self) -> date:
        return min(s.effective for s in self.stages)

    @property
    def reference_without(self) -> date | None:
        return max((s.effective for s in self.on_or_before), default=None)

    @property
    def earliest_without(self) -> date | None:
        return min((s.effective for s in self.on_or_before), default=None)

    @property
    def months_with(self) -> Decimal | None:
        return _months(self.first_built, self.reference_with)

    @property
    def months_without(self) -> Decimal | None:
        return _months(self.first_built, self.reference_without)

    @property
    def months_earliest_with(self) -> Decimal | None:
        return _months(self.first_built, self.earliest_with)

    @property
    def months_earliest_without(self) -> Decimal | None:
        return _months(self.first_built, self.earliest_without)


def project_stages(
    seen: dict[str, dict[str, list[Sighting]]], kept_order: dict[str, list[date]]
) -> list[ProjectStages]:
    """A1′ over every regime: the projects A1 measures (a kept copy before
    the first `Built` copy, with at least one capacity-bearing dated
    stage), each with its stages split by date against the first `Built`
    copy's publication date."""
    out: list[ProjectStages] = []
    for regime, project, dates, copies, first_built, before_date in _projects(seen, kept_order):
        if first_built == dates[0] or before_date is None or before_date not in copies:
            continue
        before = copies[before_date]
        stages = tuple(
            Stage(
                unit=unit,
                stage=text(s.row.get("Stage")),
                mw=_mw(s),
                effective=s.effective,
                later=s.effective > first_built,
            )
            for unit, s in before
            if _mw(s) > 0 and s.effective is not None
        )
        if not stages:
            continue
        row = copies[first_built][0][1].row
        out.append(
            ProjectStages(
                regime=regime,
                project=project,
                project_name=text(row.get("Project Name")),
                plant_type=text(row.get("Plant Type")),
                first_built=first_built,
                first_built_sha256=copies[first_built][0][1].sha256,
                copy_before=before_date,
                copy_before_sha256=before[0][1].sha256,
                capacity_mw=sum((_mw(s) for _, s in before if _mw(s) > 0), Decimal(0)),
                stages=stages,
            )
        )
    return sorted(out, key=lambda t: (t.first_built, t.regime, t.project))


def _measure(
    found: list[ProjectStages], months_of: Callable[[ProjectStages], Decimal | None]
) -> dict[str, Any]:
    pairs = [(t, m) for t in found if (m := months_of(t)) is not None]
    months = [m for _, m in pairs]
    by_year: dict[str, list[Decimal]] = defaultdict(list)
    by_plant: dict[str, list[Decimal]] = defaultdict(list)
    for t, m in pairs:
        by_year[str(t.first_built.year)].append(m)
        by_plant[t.plant_type or "(blank)"].append(m)
    return {
        "measured": len(pairs),
        "months_reference_to_built_copy": quantiles(months),
        "built_copy_before_the_date": sum(1 for m in months if m < 0),
        "built_copy_within_six_months_after": sum(1 for m in months if 0 <= m <= 6),
        "built_copy_later_than_six_months": sum(1 for m in months if m > 6),
        "by_year_of_built_copy": {y: quantiles(v) for y, v in sorted(by_year.items())},
        "by_plant_type": {
            p: quantiles(v) for p, v in sorted(by_plant.items(), key=lambda kv: -len(kv[1]))
        },
    }


def stages_summary(found: list[ProjectStages]) -> dict[str, Any]:
    """A1′ counted and A1″ side by side."""
    with_later = _measure(found, lambda t: t.months_with)
    with_later["sensitivity_earliest"] = quantiles(
        [m for t in found if (m := t.months_earliest_with) is not None]
    )
    without = _measure(found, lambda t: t.months_without)
    without["sensitivity_earliest"] = quantiles(
        [m for t in found if (m := t.months_earliest_without) is not None]
    )
    mw, mo = (
        with_later["months_reference_to_built_copy"]["median"],
        without["months_reference_to_built_copy"]["median"],
    )
    moved = [
        f"{t.regime}|{t.project}"
        for t in found
        if (a := t.months_with) is not None
        and a < 0
        and (b := t.months_without) is not None
        and b >= 0
    ]
    return {
        "projects_measured": len(found),
        "projects_with_later_stages": sum(1 for t in found if t.later),
        "later_stages": sum(len(t.later) for t in found),
        "later_stages_mw": sum((t.later_mw for t in found), Decimal(0)),
        "only_later_stages": sum(1 for t in found if t.klass == "only-later-stages"),
        "with_later_stages": with_later,
        "without_later_stages": without,
        "median_difference_without_minus_with": (
            mo - mw if isinstance(mo, Decimal) and isinstance(mw, Decimal) else None
        ),
        "moved_from_negative_to_non_negative": moved,
    }
