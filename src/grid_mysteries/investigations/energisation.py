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
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.investigations.overdue_queue import project_id, text
from grid_mysteries.sources.tec_register import parse_decimal
from grid_mysteries.tec import identity as content

DECLARATION_SHA256: Final = "fb8a3428749a73997745e4e852ba64b7a7326afd406528d9fe6315116b13bb2a"
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
