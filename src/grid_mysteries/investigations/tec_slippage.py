"""Investigation 005: connection-date slippage across TEC register vintages.

Pure logic for the pre-declared method in
`investigations/005-connection-date-credibility/DECLARATION.md`. Vintages
are lists of register rows with a publication date; this module builds
per-project timelines, computes the declared metrics, and evaluates the
three declared questions against their frozen thresholds. It reads no
files and knows nothing about where a vintage came from.

Contracts:

- Project identity is `Project ID` when present, otherwise the normalised
  (project name, customer, connection site) triple. Splits and merges are
  never repaired; the match report exposes them.
- Slip is signed months between effective dates, so advances are visible.
- Disappearance is reported separately from slip and never pooled with it.
- Rates are `Decimal`; months are integers. A threshold is met only when
  the declared inequality holds exactly as written.
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from statistics import median
from typing import Final

DATE_PATTERNS: Final = (
    re.compile(r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})"),
    re.compile(r"^(?P<d>\d{1,2})/(?P<m>\d{1,2})/(?P<y>\d{4})"),
)

CAPACITY_BANDS: Final = (
    ("<50", 0, 50),
    ("50-200", 50, 200),
    ("200-500", 200, 500),
    (">=500", 500, None),
)
LEAD_TIME_BANDS: Final = (("<3y", 0, 3), ("3-5y", 3, 5), (">5y", 5, None))
SLIP_THRESHOLD_MONTHS: Final = 24
Q1_MIN_IQR_MONTHS: Final = 12
Q1_MIN_SHARE: Final = Decimal("0.20")
Q1_ADVANCE_OR_SMALL_MONTHS: Final = 6
Q2_MIN_STRATUM_N: Final = 30
Q2_MIN_RATIO: Final = Decimal("2")
Q3_MIN_GAP: Final = Decimal("0.15")
COHORT_A: Final = (date(2019, 1, 1), date(2022, 1, 1))
COHORT_B: Final = (date(2022, 1, 1), date(2025, 1, 1))


def parse_date(value: object) -> date | None:
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    for pattern in DATE_PATTERNS:
        found = pattern.match(text)
        if found:
            try:
                return date(int(found["y"]), int(found["m"]), int(found["d"]))
            except ValueError:
                return None
    return None


def months_between(earlier: date, later: date) -> int:
    return (later.year - earlier.year) * 12 + (later.month - earlier.month)


def normalise(text: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


def identity(row: dict[str, object], *, use_project_id: bool = True) -> str:
    """Project ID when allowed and present, else the normalised name triple.

    Project ID exists only from November 2021, so a span that crosses that
    boundary must key on the triple throughout (`use_project_id=False`);
    the declaration permits the ID only where present in both vintages.
    """
    project_id = str(row.get("Project ID") or "").strip() if use_project_id else ""
    if project_id:
        return f"id:{project_id}"
    triple = (
        normalise(row.get("Project Name")),
        normalise(row.get("Customer Name")),
        normalise(row.get("Connection Site")),
    )
    return "name:" + "|".join(triple)


@dataclass(frozen=True)
class Observation:
    t_public: date
    effective: date | None
    status: str
    mw: Decimal | None
    plant_type: str
    host_to: str
    site: str


@dataclass(frozen=True)
class Vintage:
    t_public: date
    rows: tuple[dict[str, object], ...]


def _decimal(value: object) -> Decimal | None:
    text = str(value or "").replace(",", "").strip()
    try:
        return Decimal(text) if text else None
    except ArithmeticError:
        return None


def stage_keys(rows: tuple[dict[str, object], ...], *, use_project_id: bool) -> list[str]:
    """One key per register row: identity plus the register's own Stage.

    The register's grain is project-stage — from 2023 a project can carry
    several rows with different effective dates. Pooling them under one
    identity would manufacture revisions, so the unit is (identity, stage).
    The register's `Stage` value is used where present; rows sharing an
    identity without a usable Stage are ordered by effective date and MW.
    """
    groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[identity(row, use_project_id=use_project_id)].append(index)
    keys = [""] * len(rows)
    for key, indices in groups.items():
        stages = [str(rows[i].get("Stage") or "").strip() for i in indices]
        if len(indices) == 1 or (all(stages) and len(set(stages)) == len(stages)):
            for i, stage in zip(indices, stages, strict=True):
                keys[i] = f"{key}#{stage or '1'}"
            continue
        ordered = sorted(
            indices,
            key=lambda i: (
                parse_date(rows[i].get("MW Effective From")) or date.max,
                _decimal(rows[i].get("Cumulative Total Capacity (MW)")) or Decimal(0),
            ),
        )
        for ordinal, i in enumerate(ordered, start=1):
            keys[i] = f"{key}#{ordinal}"
    return keys


def build_timelines(
    vintages: list[Vintage], *, use_project_id: bool = True
) -> dict[str, list[Observation]]:
    timelines: dict[str, list[Observation]] = defaultdict(list)
    for vintage in sorted(vintages, key=lambda v: v.t_public):
        keys = stage_keys(vintage.rows, use_project_id=use_project_id)
        for key, row in zip(keys, vintage.rows, strict=True):
            timelines[key].append(
                Observation(
                    t_public=vintage.t_public,
                    effective=parse_date(row.get("MW Effective From")),
                    status=str(row.get("Project Status") or "").strip(),
                    mw=_decimal(
                        row.get("Cumulative Total Capacity (MW)") or row.get("MW Connected")
                    ),
                    plant_type=str(row.get("Plant Type") or "").strip(),
                    host_to=str(row.get("HOST TO") or "").strip(),
                    site=str(row.get("Connection Site") or "").strip(),
                )
            )
    return dict(timelines)


@dataclass(frozen=True)
class ProjectMetrics:
    key: str
    first_observed: date
    last_observed: date
    observation_span_years: Decimal
    first_effective: date | None
    last_effective: date | None
    revisions: int
    net_slip_months: int | None
    max_single_revision_months: int | None
    disappeared: bool
    first_status: str
    plant_type: str
    host_to: str
    capacity_band: str
    initial_lead_time_band: str
    status_transitions: tuple[tuple[str, str], ...]


def _band(value: Decimal | None, bands: tuple[tuple[str, int, int | None], ...]) -> str:
    if value is None:
        return "unknown"
    for label, low, high in bands:
        if value >= low and (high is None or value < high):
            return label
    return "unknown"


def project_metrics(key: str, timeline: list[Observation], last_vintage: date) -> ProjectMetrics:
    dated = [o for o in timeline if o.effective is not None]
    revisions = 0
    max_single: int | None = None
    transitions: list[tuple[str, str]] = []
    for previous, current in zip(timeline, timeline[1:], strict=False):
        if previous.effective and current.effective and current.effective != previous.effective:
            revisions += 1
            delta = months_between(previous.effective, current.effective)
            max_single = delta if max_single is None or abs(delta) > abs(max_single) else max_single
        if previous.status != current.status:
            transitions.append((previous.status, current.status))
    first, last = timeline[0], timeline[-1]
    span_days = (last.t_public - first.t_public).days
    net = months_between(dated[0].effective, dated[-1].effective) if len(dated) >= 2 else None  # type: ignore[arg-type]
    lead_years = (
        Decimal((dated[0].effective - first.t_public).days) / Decimal(365) if dated else None  # type: ignore[operator]
    )
    return ProjectMetrics(
        key=key,
        first_observed=first.t_public,
        last_observed=last.t_public,
        observation_span_years=Decimal(span_days) / Decimal(365),
        first_effective=dated[0].effective if dated else None,
        last_effective=dated[-1].effective if dated else None,
        revisions=revisions,
        net_slip_months=net,
        max_single_revision_months=max_single,
        disappeared=last.t_public < last_vintage,
        first_status=first.status,
        plant_type=first.plant_type,
        host_to=first.host_to,
        capacity_band=_band(first.mw, CAPACITY_BANDS),
        initial_lead_time_band=_band(lead_years, LEAD_TIME_BANDS),
        status_transitions=tuple(transitions),
    )


def all_metrics(
    timelines: dict[str, list[Observation]], last_vintage: date
) -> list[ProjectMetrics]:
    return [project_metrics(key, timeline, last_vintage) for key, timeline in timelines.items()]


def population(metrics: list[ProjectMetrics]) -> list[ProjectMetrics]:
    """The declared Q1-Q3 population: span >= 2 years, first observed before 2025, with a slip."""
    return [
        m
        for m in metrics
        if m.observation_span_years >= 2
        and m.first_observed < date(2025, 1, 1)
        and m.net_slip_months is not None
    ]


@dataclass(frozen=True)
class Q1Result:
    n: int
    median_months: int | None
    iqr_months: int | None
    share_slipped_ge_24: Decimal | None
    share_lt_6: Decimal | None
    passes: bool


def _share(numerator: int, denominator: int) -> Decimal | None:
    return Decimal(numerator) / Decimal(denominator) if denominator else None


def q1_dispersion(pop: list[ProjectMetrics]) -> Q1Result:
    slips = sorted(m.net_slip_months for m in pop if m.net_slip_months is not None)
    n = len(slips)
    if n == 0:
        return Q1Result(0, None, None, None, None, False)
    q1 = slips[(n - 1) // 4]
    q3 = slips[(3 * (n - 1)) // 4]
    ge_24 = sum(1 for s in slips if s >= SLIP_THRESHOLD_MONTHS)
    lt_6 = sum(1 for s in slips if s < Q1_ADVANCE_OR_SMALL_MONTHS)
    share_ge, share_lt = _share(ge_24, n), _share(lt_6, n)
    passes = (
        (q3 - q1) >= Q1_MIN_IQR_MONTHS
        and share_ge is not None
        and share_ge >= Q1_MIN_SHARE
        and share_lt is not None
        and share_lt >= Q1_MIN_SHARE
    )
    return Q1Result(n, int(median(slips)), q3 - q1, share_ge, share_lt, passes)


STRATIFICATIONS: Final = {
    "first_status": lambda m: m.first_status or "unknown",
    "plant_type": lambda m: m.plant_type or "unknown",
    "host_to": lambda m: m.host_to or "unknown",
    "initial_lead_time_band": lambda m: m.initial_lead_time_band,
    "capacity_band": lambda m: m.capacity_band,
}


@dataclass(frozen=True)
class StratumRate:
    stratum: str
    n: int
    rate_ge_24: Decimal


@dataclass(frozen=True)
class StratificationResult:
    name: str
    rates: tuple[StratumRate, ...]
    best_ratio: Decimal | None
    high: str | None
    low: str | None
    holds_in_both_cohorts: bool
    passes: bool


def _rates(pop: list[ProjectMetrics], key) -> list[StratumRate]:
    counts: Counter[str] = Counter()
    hits: Counter[str] = Counter()
    for m in pop:
        stratum = key(m)
        counts[stratum] += 1
        if m.net_slip_months is not None and m.net_slip_months >= SLIP_THRESHOLD_MONTHS:
            hits[stratum] += 1
    return [
        StratumRate(s, counts[s], Decimal(hits[s]) / Decimal(counts[s])) for s in sorted(counts)
    ]


def _direction(pop: list[ProjectMetrics], key, high: str, low: str) -> bool | None:
    rates = {r.stratum: r for r in _rates(pop, key)}
    if high not in rates or low not in rates:
        return None
    return rates[high].rate_ge_24 > rates[low].rate_ge_24


def q2_predictability(pop: list[ProjectMetrics]) -> list[StratificationResult]:
    results = []
    for name, key in STRATIFICATIONS.items():
        rates = _rates(pop, key)
        eligible = [r for r in rates if r.n >= Q2_MIN_STRATUM_N]
        best_ratio = high = low = None
        for a in eligible:
            for b in eligible:
                if b.rate_ge_24 > 0 and a.rate_ge_24 / b.rate_ge_24 > (best_ratio or Decimal(0)):
                    best_ratio, high, low = a.rate_ge_24 / b.rate_ge_24, a.stratum, b.stratum
        cohort_a = [m for m in pop if COHORT_A[0] <= m.first_observed < COHORT_A[1]]
        cohort_b = [m for m in pop if COHORT_B[0] <= m.first_observed < COHORT_B[1]]
        holds = bool(
            high
            and low
            and _direction(cohort_a, key, high, low) is True
            and _direction(cohort_b, key, high, low) is True
        )
        passes = best_ratio is not None and best_ratio >= Q2_MIN_RATIO and holds
        results.append(
            StratificationResult(name, tuple(rates), best_ratio, high, low, holds, passes)
        )
    return results


@dataclass(frozen=True)
class Q3Result:
    pooled_rate: Decimal | None
    materially_different: tuple[tuple[str, str, Decimal], ...]
    passes: bool


def q3_materiality(pop: list[ProjectMetrics], q2: list[StratificationResult]) -> Q3Result:
    n = len(pop)
    if n == 0:
        return Q3Result(None, (), False)
    pooled = Decimal(
        sum(1 for m in pop if m.net_slip_months is not None and m.net_slip_months >= 24)
    ) / Decimal(n)
    found = []
    for result in q2:
        if not result.passes:
            continue
        for rate in result.rates:
            if rate.n >= Q2_MIN_STRATUM_N and abs(rate.rate_ge_24 - pooled) >= Q3_MIN_GAP:
                found.append((result.name, rate.stratum, rate.rate_ge_24))
    return Q3Result(pooled, tuple(found), bool(found))


@dataclass(frozen=True)
class MatchReport:
    identities: int
    by_project_id: int
    by_name_triple: int
    single_vintage_only: int


def match_report(timelines: dict[str, list[Observation]]) -> MatchReport:
    keys = list(timelines)
    return MatchReport(
        identities=len(keys),
        by_project_id=sum(1 for k in keys if k.startswith("id:")),
        by_name_triple=sum(1 for k in keys if k.startswith("name:")),
        single_vintage_only=sum(1 for t in timelines.values() if len(t) == 1),
    )
