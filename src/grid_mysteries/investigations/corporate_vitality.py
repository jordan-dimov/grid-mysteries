"""009 — corporate vitality of the TEC queue: pure logic.

Resolution of a TEC customer name to a company, the objective state
hierarchy (V1–V5, V0), and the two pre-declared tests. No network.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from grid_mysteries.sources.companies_house import normalise_company_name

DISSOLVED = frozenset({"dissolved", "converted-closed", "closed", "removed"})
INSOLVENCY = frozenset(
    {
        "liquidation",
        "receivership",
        "administration",
        "voluntary-arrangement",
        "insolvency-proceedings",
    }
)
GAZETTE_FIRST = frozenset(
    {"gazette-notice-voluntary", "gazette-notice-compulsory", "gazette-notice-compulsary"}
)
GAZETTE_DISCONTINUED = frozenset({"gazette-filings-brought-up-to-date"})
UP_TO_DATE_TYPES = frozenset({"AA", "CS01", "DS02"})
STRONG = frozenset({"V1", "V2", "V3"})
OVERDUE_DAYS = 183
PORTFOLIO_THRESHOLD = 5
MIN_COVERAGE = Decimal("0.7")


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


def candidates(hits: Iterable[Mapping[str, Any]]) -> list[Candidate]:
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


@dataclass(frozen=True)
class Resolution:
    customer: str
    company_number: str | None
    reason: str
    candidates: tuple[str, ...]


def resolve(
    customer: str,
    primary_hits: Sequence[Mapping[str, Any]],
    advanced_hits: Sequence[Mapping[str, Any]],
    profiles: Mapping[str, Mapping[str, Any]],
    *,
    first_observed: date,
) -> Resolution:
    """Sealed rule: exact normalised title (any status) → advanced search →
    previous names → lifespan containing the project's first TEC appearance."""
    target = normalise_company_name(customer)
    exact = [c for c in candidates(primary_hits) if normalise_company_name(c.title) == target]
    reason = "primary-exact"
    if not exact:
        adv = candidates(advanced_hits)
        exact = [c for c in adv if normalise_company_name(c.title) == target]
        reason = "advanced-exact"
        if not exact:
            for c in adv:
                prev = profiles.get(c.number, {}).get("previous_company_names") or []
                if any(normalise_company_name(p.get("name")) == target for p in prev):
                    exact.append(c)
            reason = "previous-name"
    if not exact:
        return Resolution(customer, None, "no-exact-match", ())
    if len(exact) > 1:
        alive = [
            c
            for c in exact
            if (c.created is None or c.created <= first_observed)
            and (c.ceased is None or c.ceased >= first_observed)
        ]
        # profiles carry the cessation date when the search hit does not
        if len(alive) != 1:
            alive = []
            for c in exact:
                p = profiles.get(c.number, {})
                created = _date(p.get("date_of_creation")) or c.created
                ceased = _date(p.get("date_of_cessation")) or c.ceased
                if (created is None or created <= first_observed) and (
                    ceased is None or ceased >= first_observed
                ):
                    alive.append(c)
        if len(alive) != 1:
            return Resolution(customer, None, "ambiguous", tuple(c.number for c in exact))
        exact = alive
        reason += "+lifespan"
    return Resolution(customer, exact[0].number, reason, tuple(c.number for c in exact))


@dataclass(frozen=True)
class State:
    tier: str  # V0..V5
    on: date | None
    detail: str
    undated: bool = False


def classify(
    profile: Mapping[str, Any], filings: Sequence[Mapping[str, Any]], *, fetch_date: date
) -> State:
    status = str(profile.get("company_status") or "").lower()
    detail = str(profile.get("company_status_detail") or "").lower()
    dated = sorted(
        (
            (d, str(f.get("description") or ""), str(f.get("type") or ""))
            for f in filings
            if (d := _date(f.get("date"))) is not None
        ),
    )
    if status in DISSOLVED:
        on = _date(profile.get("date_of_cessation"))
        return State("V1", on or fetch_date, status, undated=on is None)
    if status in INSOLVENCY:
        liq = [d for d, desc, _ in dated if desc.startswith("liquidation-")]
        return State("V2", liq[0] if liq else fetch_date, status, undated=not liq)
    gazette: date | None = None
    for d, desc, ftype in dated:
        if desc in GAZETTE_FIRST:
            gazette = d
        elif gazette is not None and (desc in GAZETTE_DISCONTINUED or ftype in UP_TO_DATE_TYPES):
            gazette = None
    if detail == "active-proposal-to-strike-off":
        return State("V3", gazette or fetch_date, detail, undated=gazette is None)
    if gazette is not None:
        return State("V3", gazette, "first-gazette-not-discontinued")
    accounts = profile.get("accounts") or {}
    cs = profile.get("confirmation_statement") or {}
    cutoff = fetch_date - timedelta(days=OVERDUE_DAYS)
    for block, label in ((accounts, "accounts-overdue"), (cs, "confirmation-statement-overdue")):
        due = _date(block.get("next_due"))
        if block.get("overdue") and due is not None and due <= cutoff:
            return State("V4", due, label)
    last = accounts.get("last_accounts") or {}
    if str(last.get("type") or "").lower() == "dormant":
        return State("V5", _date(last.get("made_up_to")), "dormant-accounts")
    return State("V0", None, status or "active")


def signal(state: State, *, first_observed: date, as_of: date) -> str:
    """'strong' | 'moderate' | 'none' | 'identity-error' (state dated before the project existed)."""
    if state.tier not in STRONG and state.tier != "V4":
        return "none"
    if state.on is not None and not state.undated and state.on < first_observed:
        return "identity-error"
    if state.on is not None and state.on > as_of:
        return "none"
    return "strong" if state.tier in STRONG else "moderate"


@dataclass(frozen=True)
class ArmShares:
    label: str
    n_stages: int
    mw_total: Decimal
    n_resolved: int
    mw_resolved: Decimal
    n_strong: int
    mw_strong: Decimal
    n_moderate: int
    mw_moderate: Decimal
    n_dormant: int
    n_identity_error: int
    coverage_mw: Decimal | None
    share_strong_mw: Decimal | None
    share_strong_count: Decimal | None
    share_strong_plus_moderate_mw: Decimal | None
    share_strong_floor_mw: Decimal | None


def _ratio(a: Decimal, b: Decimal) -> Decimal | None:
    return (a / b).quantize(Decimal("0.0001")) if b else None


def arm_shares(
    label: str,
    stages: Sequence[Mapping[str, Any]],
    states: Mapping[str, State | None],
    *,
    as_of: date,
) -> ArmShares:
    """`states` maps normalised customer → State (None = unresolved)."""
    mw_total = sum((Decimal(s["mw"]) for s in stages), Decimal(0))
    n_res = n_strong = n_mod = n_dorm = n_ident = 0
    mw_res = mw_strong = mw_mod = Decimal(0)
    for s in stages:
        st = states.get(s["customer_norm"])
        if st is None:
            continue
        sig = signal(st, first_observed=date.fromisoformat(s["first_observed"]), as_of=as_of)
        if sig == "identity-error":
            n_ident += 1
            continue
        n_res += 1
        mw = Decimal(s["mw"])
        mw_res += mw
        if sig == "strong":
            n_strong += 1
            mw_strong += mw
        elif sig == "moderate":
            n_mod += 1
            mw_mod += mw
        if st.tier == "V5":
            n_dorm += 1
    return ArmShares(
        label=label,
        n_stages=len(stages),
        mw_total=mw_total,
        n_resolved=n_res,
        mw_resolved=mw_res,
        n_strong=n_strong,
        mw_strong=mw_strong,
        n_moderate=n_mod,
        mw_moderate=mw_mod,
        n_dormant=n_dorm,
        n_identity_error=n_ident,
        coverage_mw=_ratio(mw_res, mw_total),
        share_strong_mw=_ratio(mw_strong, mw_res),
        share_strong_count=_ratio(Decimal(n_strong), Decimal(n_res)),
        share_strong_plus_moderate_mw=_ratio(mw_strong + mw_mod, mw_res),
        share_strong_floor_mw=_ratio(mw_strong, mw_total),
    )


@dataclass(frozen=True)
class Test1Verdict:
    determinable: bool
    verdict: str
    s_scoping_pct: Decimal | None
    s_built_pct: Decimal | None
    gap_pp: Decimal | None


def test1_verdict(scoping: ArmShares, built: ArmShares) -> Test1Verdict:
    covered = all(
        a.coverage_mw is not None and a.coverage_mw >= MIN_COVERAGE for a in (scoping, built)
    )
    if not covered or scoping.share_strong_mw is None or built.share_strong_mw is None:
        return Test1Verdict(False, "not determinable (coverage < 70 % of MW)", None, None, None)
    s = (scoping.share_strong_mw * 100).quantize(Decimal("0.1"))
    b = (built.share_strong_mw * 100).quantize(Decimal("0.1"))
    gap = s - b
    if s >= 10 and gap >= 8:
        verdict = "material"
    elif s <= 3:
        verdict = "live"
    else:
        verdict = "indeterminate"
    return Test1Verdict(True, verdict, s, b, gap)


@dataclass(frozen=True)
class Test2Result:
    n_gone: int
    n_gone_resolved: int
    n_gone_strong: int
    i_gone_count: Decimal | None
    i_gone_mw: Decimal | None
    n_control_resolved: int
    n_control_strong: int
    i_present_count: Decimal | None
    i_present_mw: Decimal | None
    n_leading: int
    leading_share: Decimal | None
    n_strong_excl_hole: int
    n_leading_excl_hole: int
    leading_share_excl_hole: Decimal | None
    verdict: str


def test2(
    gone: Sequence[Mapping[str, Any]],
    control: Sequence[Mapping[str, Any]],
    states: Mapping[str, State | None],
    *,
    as_of: date,
    hole_last_seen: str = "2025-07-22",
) -> Test2Result:
    def strong_stages(
        stages: Sequence[Mapping[str, Any]],
    ) -> tuple[list, list, Decimal, Decimal]:
        resolved, strong = [], []
        mw_res = mw_strong = Decimal(0)
        for s in stages:
            st = states.get(s["customer_norm"])
            if st is None:
                continue
            sig = signal(st, first_observed=date.fromisoformat(s["first_seen"]), as_of=as_of)
            if sig == "identity-error":
                continue
            resolved.append(s)
            mw_res += Decimal(s["mw"])
            if sig == "strong":
                strong.append((s, st))
                mw_strong += Decimal(s["mw"])
        return resolved, strong, mw_res, mw_strong

    g_res, g_strong, g_mw, g_mw_strong = strong_stages(gone)
    c_res, c_strong, c_mw, c_mw_strong = strong_stages(control)
    leading = [
        (s, st)
        for s, st in g_strong
        if st.on is not None and not st.undated and st.on < date.fromisoformat(s["last_seen"])
    ]
    strong_x = [(s, st) for s, st in g_strong if s["last_seen"] != hole_last_seen]
    leading_x = [(s, st) for s, st in leading if s["last_seen"] != hole_last_seen]
    i_gone = _ratio(Decimal(len(g_strong)), Decimal(len(g_res)))
    i_pres = _ratio(Decimal(len(c_strong)), Decimal(len(c_res)))
    lshare = _ratio(Decimal(len(leading)), Decimal(len(g_strong)))
    if len(g_strong) < 10 or i_gone is None or i_gone < Decimal("0.05"):
        verdict = "not determinable (< 10 signal-bearing disappeared stages or I_gone < 5 %)"
    elif (
        i_pres is not None
        and lshare is not None
        and i_gone >= 3 * i_pres
        and lshare >= Decimal("0.5")
    ):
        verdict = "leading"
    elif lshare is not None and lshare < Decimal("0.25"):
        verdict = "label, not signal"
    else:
        verdict = "indeterminate"
    return Test2Result(
        n_gone=len(gone),
        n_gone_resolved=len(g_res),
        n_gone_strong=len(g_strong),
        i_gone_count=i_gone,
        i_gone_mw=_ratio(g_mw_strong, g_mw),
        n_control_resolved=len(c_res),
        n_control_strong=len(c_strong),
        i_present_count=i_pres,
        i_present_mw=_ratio(c_mw_strong, c_mw),
        n_leading=len(leading),
        leading_share=lshare,
        n_strong_excl_hole=len(strong_x),
        n_leading_excl_hole=len(leading_x),
        leading_share_excl_hole=_ratio(Decimal(len(leading_x)), Decimal(len(strong_x))),
        verdict=verdict,
    )


def portfolio_customers(
    arms: Mapping[str, Sequence[Mapping[str, Any]]], all_register_rows: Iterable[str]
) -> frozenset[str]:
    counts: dict[str, int] = defaultdict(int)
    for c in all_register_rows:
        counts[c] += 1
    return frozenset(c for c, n in counts.items() if n >= PORTFOLIO_THRESHOLD)
