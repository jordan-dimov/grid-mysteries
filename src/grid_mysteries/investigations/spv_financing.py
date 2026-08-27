"""008 · J2 stage 1 — pure logic for the SPV-financing screen.

Everything here is replayable from fixtures: cohort arms from 005's
project-metrics rows, the name-resolution rule, charge facts per company,
and the pre-declared kill test. No network.
"""

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from statistics import median
from typing import Any

from grid_mysteries.sources.companies_house import normalise_company_name

ADVANCED: frozenset[str] = frozenset({"Built", "Under Construction/Commissioning"})
ELIGIBLE_FIRST: frozenset[str] = frozenset({"Awaiting Consents", "Consents Approved", "Scoping"})
PORTFOLIO_THRESHOLD = 5
MIN_ARM = 40
KILL_GAP_PP = Decimal(15)
MIN_RESOLVED_SHARE = Decimal("0.6")


def customer_of(key: str) -> str:
    """005 keys look like ``name:<project>|<customer>|<site>#n``."""
    body = key.split(":", 1)[1] if ":" in key else key
    parts = body.split("|")
    return parts[1] if len(parts) >= 2 else ""


def last_status(row: dict[str, str]) -> str:
    transitions = row.get("status_transitions") or ""
    if not transitions:
        return row.get("first_status", "")
    return transitions.split(";")[-1].split("->")[-1]


def in_population(row: dict[str, str]) -> bool:
    """005's Q1–Q3 population as run: span >= 2 years, first seen before 2023-12."""
    return Decimal(row["observation_span_years"]) >= 2 and row["first_observed"] < "2023-12"


def arms(
    rows: list[dict[str, str]], *, storage_only: bool = True
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """(Built arm, Scoping arm) under the sealed Stage-1 cohort rules."""
    pop = [r for r in rows if in_population(r)]
    if storage_only:
        pop = [r for r in pop if "Storage" in r.get("plant_type", "")]
    eligible = [r for r in pop if r["first_status"] in ELIGIBLE_FIRST]
    built = [r for r in eligible if last_status(r) in ADVANCED]
    scoping = [
        r
        for r in eligible
        if r["first_status"] == "Scoping"
        and not r.get("status_transitions")
        and Decimal(r["observation_span_years"]) >= 3
    ]
    return built, scoping


def portfolio_customers(all_rows: list[dict[str, str]]) -> frozenset[str]:
    counts = Counter(customer_of(r["key"]) for r in all_rows)
    return frozenset(c for c, n in counts.items() if n >= PORTFOLIO_THRESHOLD)


@dataclass(frozen=True)
class Resolution:
    customer: str
    company_number: str | None
    reason: str
    candidates: tuple[str, ...]


def resolve(customer: str, hits: Sequence[Mapping[str, Any]]) -> Resolution:
    """Exactly one *active* company whose title normalises to the customer name."""
    target = normalise_company_name(customer)
    exact = [
        h
        for h in hits
        if normalise_company_name(h.get("title")) == target
        and str(h.get("company_status", "")).lower() == "active"
    ]
    numbers = tuple(str(h.get("company_number")) for h in exact)
    if len(exact) == 1:
        return Resolution(customer, numbers[0], "unique-active-exact", numbers)
    if not exact:
        any_exact = [h for h in hits if normalise_company_name(h.get("title")) == target]
        reason = "exact-but-not-active" if any_exact else "no-exact-match"
        return Resolution(
            customer, None, reason, tuple(str(h.get("company_number")) for h in any_exact)
        )
    return Resolution(customer, None, "ambiguous-active", numbers)


@dataclass(frozen=True)
class ChargeFacts:
    company_number: str
    incorporated: date | None
    n_charges: int
    n_after_first_observed: int
    first_created: date | None
    first_created_after_first_observed: date | None


def _date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def charge_facts(
    company_number: str,
    profile: Mapping[str, Any],
    charges: Mapping[str, Any],
    *,
    first_observed: date,
    last_observed: date,
) -> ChargeFacts:
    items: list[Mapping[str, Any]] = list(charges.get("items") or [])
    created = sorted(d for d in (_date(i.get("created_on")) for i in items) if d)
    # The Stage-2 clock: created after the project appeared in TEC and
    # while it was still observed.
    after = [d for d in created if first_observed < d <= last_observed]
    return ChargeFacts(
        company_number=company_number,
        incorporated=_date(profile.get("date_of_creation")),
        n_charges=len(created),
        n_after_first_observed=len(after),
        first_created=created[0] if created else None,
        first_created_after_first_observed=after[0] if after else None,
    )


@dataclass(frozen=True)
class ArmSummary:
    label: str
    n_projects: int
    n_resolved: int
    resolved_share: Decimal | None
    n_with_charge: int
    incidence: Decimal | None
    n_with_charge_after_first_observed: int
    incidence_after_first_observed: Decimal | None
    median_company_age_years: Decimal | None


def _share(num: int, den: int) -> Decimal | None:
    return (Decimal(num) / Decimal(den)).quantize(Decimal("0.0001")) if den else None


def summarise_arm(
    label: str,
    projects: list[dict[str, str]],
    facts_by_customer: dict[str, ChargeFacts | None],
) -> ArmSummary:
    resolved: list[tuple[dict[str, str], ChargeFacts]] = []
    for p in projects:
        f = facts_by_customer.get(customer_of(p["key"]))
        if f is not None:
            resolved.append((p, f))
    with_charge = [f for _, f in resolved if f.n_charges > 0]
    after = [f for _, f in resolved if f.n_after_first_observed > 0]
    ages = [
        Decimal((date.fromisoformat(p["last_observed"]) - f.incorporated).days) / Decimal(365)
        for p, f in resolved
        if f.incorporated is not None
    ]
    return ArmSummary(
        label=label,
        n_projects=len(projects),
        n_resolved=len(resolved),
        resolved_share=_share(len(resolved), len(projects)),
        n_with_charge=len(with_charge),
        incidence=_share(len(with_charge), len(resolved)),
        n_with_charge_after_first_observed=len(after),
        incidence_after_first_observed=_share(len(after), len(resolved)),
        median_company_age_years=median(ages).quantize(Decimal("0.1")) if ages else None,
    )


@dataclass(frozen=True)
class Stage1Verdict:
    determinable: bool
    resolved_ok: bool
    gap_pp: Decimal | None
    survives: bool
    note: str


def stage1_verdict(built: ArmSummary, scoping: ArmSummary) -> Stage1Verdict:
    """The sealed kill: < 15 pp gap or < 60 % resolved kills; n < 40 per arm is not determinable.

    Survival is a screen only (age/timing guard); it never carries a decision.
    """
    if built.n_projects < MIN_ARM or scoping.n_projects < MIN_ARM:
        return Stage1Verdict(False, False, None, False, "arm below n >= 40: not determinable")
    resolved_ok = all(
        s.resolved_share is not None and s.resolved_share >= MIN_RESOLVED_SHARE
        for s in (built, scoping)
    )
    if built.incidence is None or scoping.incidence is None:
        return Stage1Verdict(True, resolved_ok, None, False, "no resolved companies in an arm")
    gap = ((built.incidence - scoping.incidence) * 100).quantize(Decimal("0.1"))
    survives = resolved_ok and gap >= KILL_GAP_PP
    note = (
        "screen survives: Stage 2 runs next, no interpretation attached"
        if survives
        else "killed: charge incidence carries no usable information at SPV level"
    )
    if not resolved_ok:
        note = "killed: resolved share below 60 % in an arm"
    return Stage1Verdict(True, resolved_ok, gap, survives, note)
