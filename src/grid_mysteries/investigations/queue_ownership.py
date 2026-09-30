"""019 — Who holds the queue: the Companies House join, pure rules.

Reading rules R1 to R6 of `investigations/019-who-holds-the-queue/
DECLARATION.md` (SHA-256 877682f7…) as functions of rows and of pinned
Companies House responses. No I/O; the runner owns files and requests.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.investigations.overdue_queue import project_id, stage_mw, text
from grid_mysteries.sources.companies_house import normalise_company_name

DECLARATION_SHA256: Final = "877682f7bffe52e8b98ff63bf5d14eb1e3d21713e68651d749b94e934b775a6a"
RULE_VERSION: Final = "019-r2-v1"
AS_OF: Final = date(2026, 9, 29)
UNDER_A_YEAR_FROM: Final = AS_OF - timedelta(days=365)
RESOLUTION_THRESHOLD: Final = Decimal("0.70")  # F1
IDENTITY_GUARD_THRESHOLD: Final = Decimal("0.10")  # F2
EVENT_THRESHOLD: Final = Decimal("0.70")  # F3
_SUFFIX: Final = re.compile(
    r"\b(ltd|limited|plc|llp|l\.l\.p\.|lp|cic|c\.i\.c\.|limited liability partnership"
    r"|public limited company)\b\.?",
    re.I,
)
CHARGED_STATUSES: Final = frozenset({"outstanding", "part-satisfied"})


# ------------------------------------------------------------------ R1


def printed_name(row: dict[str, object]) -> str:
    """The customer name as printed, runs of whitespace collapsed, case kept."""
    return text(row.get("Customer Name"))


def has_company_suffix(name: str) -> bool:
    return bool(_SUFFIX.search(name))


@dataclass
class Name:
    name: str
    rows: int = 0
    mw: Decimal = Decimal(0)
    project_ids: set[str] = field(default_factory=set)

    @property
    def no_suffix(self) -> bool:
        return not has_company_suffix(self.name)


def names(rows: list[dict[str, object]]) -> dict[str, Name]:
    """R1: the distinct printed names with their rows, MW and project ids."""
    out: dict[str, Name] = {}
    for row in rows:
        n = out.setdefault(printed_name(row), Name(printed_name(row)))
        n.rows += 1
        n.mw += stage_mw(row) or Decimal(0)
        if pid := project_id(row):
            n.project_ids.add(pid)
    return out


def case_pairs(all_names: dict[str, Name]) -> list[list[str]]:
    """Names that differ only in case (reported, never merged)."""
    groups: dict[str, list[str]] = defaultdict(list)
    for n in all_names:
        groups[n.casefold()].append(n)
    return sorted(g for g in groups.values() if len(g) > 1)


# ------------------------------------------------------------------ R2


def _date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


@dataclass(frozen=True)
class Candidate:
    number: str
    title: str
    status: str
    created: date | None
    ceased: date | None


def candidates(hits: list[dict[str, Any]]) -> list[Candidate]:
    return [
        Candidate(
            number=str(h.get("company_number")),
            title=str(h.get("title") or h.get("company_name") or ""),
            status=str(h.get("company_status") or "").lower(),
            created=_date(h.get("date_of_creation")),
            ceased=_date(h.get("date_of_cessation")),
        )
        for h in hits
        if h.get("company_number")
    ]


def exact_candidates(name: str, hits: list[dict[str, Any]]) -> list[Candidate]:
    target = normalise_company_name(name)
    return [c for c in candidates(hits) if normalise_company_name(c.title) == target]


def previous_name_matches(name: str, profile: dict[str, Any]) -> bool:
    target = normalise_company_name(name)
    return any(
        normalise_company_name(p.get("name")) == target
        for p in profile.get("previous_company_names") or []
    )


@dataclass(frozen=True)
class Link:
    """One line of links.ndjson: a name's resolution as proposed by rule."""

    name: str
    klass: (
        str  # exact | previous-name | ambiguous | unresolved | identity-guard | admitted | refused
    )
    company_number: str | None
    candidates: tuple[str, ...]
    note: str
    rule_version: str = RULE_VERSION

    @property
    def resolved(self) -> bool:
        return self.klass in ("exact", "previous-name", "admitted")


def resolve(
    name: str,
    search_hits: list[dict[str, Any]],
    advanced_hits: list[dict[str, Any]] | None,
    profiles: dict[str, dict[str, Any]],
    first_seen: date | None,
) -> Link:
    """R2 as declared: exactly one exact candidate resolves; none sends the
    name through the advanced search and previous names; several is
    ambiguous; and a rule-resolved company created after the name was first
    printed against one of its current project ids fails the identity guard.
    `advanced_hits` is None when the advanced search was not needed."""
    exact = exact_candidates(name, search_hits)
    if len(exact) == 1:
        return _guarded(name, exact[0], "exact", first_seen, [exact[0].number])
    if len(exact) > 1:
        return Link(
            name,
            "ambiguous",
            None,
            tuple(c.number for c in exact),
            "; ".join(
                f"{c.number} {c.status} created {c.created} ceased {c.ceased}" for c in exact
            ),
        )
    if advanced_hits is None:
        return Link(name, "unresolved", None, (), "advanced search not run")
    by_previous = [
        c
        for c in candidates(advanced_hits)
        if c.number in profiles and previous_name_matches(name, profiles[c.number])
    ]
    if len(by_previous) == 1:
        return _guarded(name, by_previous[0], "previous-name", first_seen, [by_previous[0].number])
    if len(by_previous) > 1:
        return Link(
            name,
            "ambiguous",
            None,
            tuple(c.number for c in by_previous),
            "several companies carry the name among their previous names",
        )
    proposals = tuple(c.number for c in candidates(search_hits)[:3])
    return Link(name, "unresolved", None, proposals, "no exact or previous-name match")


def _guarded(
    name: str, c: Candidate, klass: str, first_seen: date | None, numbers: list[str]
) -> Link:
    if first_seen is not None and c.created is not None and c.created > first_seen:
        return Link(
            name,
            "identity-guard",
            None,
            tuple(numbers),
            f"{c.number} created {c.created}, after the name was first printed {first_seen}",
        )
    return Link(name, klass, c.number, tuple(numbers), f"{c.status} created {c.created}")


def apply_admissions(link: Link, admitted: dict[str, dict[str, Any]]) -> Link:
    """A person's admission or refusal overrides a rule that did not resolve."""
    decision = admitted.get(link.name)
    if decision is None or link.resolved:
        return link
    if decision.get("decision") == "admitted" and decision.get("company_number"):
        return Link(
            link.name,
            "admitted",
            str(decision["company_number"]),
            link.candidates,
            f"admitted {decision.get('on')} by {decision.get('by')}",
        )
    if decision.get("decision") == "refused":
        return Link(
            link.name,
            "refused",
            None,
            link.candidates,
            f"refused {decision.get('on')} by {decision.get('by')}",
        )
    return link


# ------------------------------------------------------------------ R3


def under_a_year_old(profile: dict[str, Any], as_of: date = AS_OF) -> bool | None:
    created = _date(profile.get("date_of_creation"))
    if created is None:
        return None
    return created >= as_of - timedelta(days=365)


def age_years(profile: dict[str, Any], as_of: date = AS_OF) -> Decimal | None:
    created = _date(profile.get("date_of_creation"))
    if created is None:
        return None
    return (Decimal((as_of - created).days) / Decimal(365)).quantize(Decimal("0.1"))


# ------------------------------------------------------------------ R4


@dataclass(frozen=True)
class NameChange:
    project_id: str
    earlier: str
    later: str
    last_copy_with_earlier: str
    first_copy_with_later: str


def name_changes(history: dict[str, list[dict[str, str]]]) -> list[NameChange]:
    """R4: for each project id, consecutive distinct printed names across the
    copies, in publication order. `history[pid]` is a list of
    {t_public, name} covering every copy in which the id printed."""
    out = []
    for pid, seq in sorted(history.items()):
        previous: dict[str, str] | None = None
        for entry in seq:
            if previous is not None and entry["name"] != previous["name"]:
                out.append(
                    NameChange(
                        pid,
                        previous["name"],
                        entry["name"],
                        previous["t_public"],
                        entry["t_public"],
                    )
                )
            previous = entry
    return out


def classify_change(
    change: NameChange, links: dict[str, Link], profiles: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    a, b = links.get(change.earlier), links.get(change.later)
    na = a.company_number if a and a.resolved else None
    nb = b.company_number if b and b.resolved else None
    out: dict[str, Any] = {**change.__dict__, "earlier_company": na, "later_company": nb}
    ch_date = None
    if nb and previous_name_matches(change.earlier, profiles.get(nb, {})):
        for p in profiles[nb].get("previous_company_names") or []:
            if normalise_company_name(p.get("name")) == normalise_company_name(change.earlier):
                ch_date = p.get("ceased_on")
    same_company = bool(na and nb and na == nb)
    later_is_previous_of_earlier = bool(
        na and previous_name_matches(change.later, profiles.get(na, {}))
    )
    if same_company or ch_date is not None or later_is_previous_of_earlier:
        out["class"] = "rename"
    elif na and nb:
        out["class"] = "transfer"
    else:
        out["class"] = "not-determinable"
    out["companies_house_date"] = ch_date
    if out["class"] == "rename" and ch_date:
        d = _date(ch_date)
        first = _date(change.first_copy_with_later)
        out["register_lag_days"] = (first - d).days if d and first else None
    else:
        out["register_lag_days"] = None
    return out


# ------------------------------------------------------------------ R5


def psc_summary(psc: dict[str, Any], statements: dict[str, Any]) -> dict[str, Any]:
    """Counts only; no name leaves this function."""
    items = psc.get("items") or []
    current = [i for i in items if not i.get("ceased_on")]
    return {
        "psc_total": len(items),
        "psc_current": len(current),
        "psc_current_corporate": sum(
            1 for i in current if str(i.get("kind") or "").startswith("corporate-entity")
        ),
        "psc_current_individual": sum(
            1 for i in current if str(i.get("kind") or "").startswith("individual")
        ),
        "psc_corporate_outside_uk": sum(
            1
            for i in current
            if str(i.get("kind") or "").startswith("corporate-entity")
            and str((i.get("identification") or {}).get("country_registered") or "").strip()
            and not _uk((i.get("identification") or {}).get("country_registered"))
        ),
        "psc_earliest_notified_on": min(
            (str(i.get("notified_on")) for i in current if i.get("notified_on")), default=None
        ),
        "statements": sorted(
            {
                str(s.get("statement"))
                for s in statements.get("items") or []
                if not s.get("ceased_on")
            }
        ),
    }


def _uk(country: object) -> bool:
    c = str(country or "").strip().lower()
    return c in (
        "united kingdom",
        "uk",
        "england",
        "england and wales",
        "scotland",
        "wales",
        "northern ireland",
        "great britain",
        "england & wales",
    )


# ------------------------------------------------------------------ R6


def charge_facts(charges: dict[str, Any]) -> dict[str, Any]:
    items = charges.get("items") or []
    live = [i for i in items if str(i.get("status") or "").lower() in CHARGED_STATUSES]
    chargees = sorted(
        {str(p.get("name")) for i in live for p in i.get("persons_entitled") or [] if p.get("name")}
    )
    return {
        "charges_total": len(items),
        "charges_live": len(live),
        "charged": bool(live),
        "earliest_live_created_on": min(
            (str(i.get("created_on")) for i in live if i.get("created_on")), default=None
        ),
        "latest_live_created_on": max(
            (str(i.get("created_on")) for i in live if i.get("created_on")), default=None
        ),
        "chargees": chargees,
    }


# ------------------------------------------------------------- figures


def share(part: Decimal | int, whole: Decimal | int) -> Decimal | None:
    if not whole:
        return None
    return (Decimal(part) / Decimal(whole)).quantize(Decimal("0.001"))


def resolution_figure(all_names: dict[str, Name], links: dict[str, Link]) -> dict[str, Any]:
    by_class: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"names": 0, "rows": 0, "mw": Decimal(0)}
    )
    for n in all_names.values():
        klass = "no-suffix" if n.no_suffix and not links[n.name].resolved else links[n.name].klass
        by_class[klass]["names"] += 1
        by_class[klass]["rows"] += n.rows
        by_class[klass]["mw"] += n.mw
    total_names = len(all_names)
    total_mw = sum((n.mw for n in all_names.values()), Decimal(0))
    resolved_names = sum(1 for n in all_names.values() if links[n.name].resolved)
    resolved_mw = sum((n.mw for n in all_names.values() if links[n.name].resolved), Decimal(0))
    guard = sum(1 for lk in links.values() if lk.klass == "identity-guard")
    rule_resolved = sum(1 for lk in links.values() if lk.klass in ("exact", "previous-name"))
    return {
        "names": total_names,
        "rows": sum(n.rows for n in all_names.values()),
        "mw": total_mw,
        "by_class": dict(sorted(by_class.items())),
        "resolved_names": resolved_names,
        "resolved_share_of_names": share(resolved_names, total_names),
        "resolved_mw": resolved_mw,
        "resolved_share_of_mw": share(resolved_mw, total_mw),
        "identity_guard_share_of_rule_resolved": share(guard, rule_resolved + guard),
        "F1_fires": (share(resolved_names, total_names) or Decimal(0)) < RESOLUTION_THRESHOLD
        or (share(resolved_mw, total_mw) or Decimal(0)) < RESOLUTION_THRESHOLD,
        "F2_fires": (share(guard, rule_resolved + guard) or Decimal(0)) > IDENTITY_GUARD_THRESHOLD,
    }
