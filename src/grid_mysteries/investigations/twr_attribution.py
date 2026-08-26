"""Investigation 006: attributing TEC connection-date slips to enabling works.

Pure logic for `investigations/006-connection-slippage-attribution/DECLARATION.md`
as amended (Amendment 1): the disclosed Transmission Works Register carries
the *project's* connection date on every project → scheme row, so a
scheme's effective completion date is proxied by the earliest connection
date among its dependent projects in each vintage. Everything here is
deterministic over in-memory records; the runner does the I/O.

Contracts:

- Scheme identity is the normalised identifier (`SHETL-` → `SHET-`,
  placeholders dropped); TEC identity is the 005 key
  (`name:<name>|<customer>|<site>#<stage>`), so both sides share one
  `normalise`.
- Attribution windows are asymmetric by declaration: a works move counts
  if published within 180 days before or 90 days after the TEC revision.
- Thresholds are the declared ones and are met only when the inequality
  holds as written.
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from statistics import median
from typing import Final

from grid_mysteries.investigations.tec_slippage import (
    COHORT_A,
    COHORT_B,
    Observation,
    ProjectMetrics,
    months_between,
    normalise,
    parse_date,
)

WORKS_MOVE_MONTHS: Final = 6
WINDOW_BEFORE_DAYS: Final = 180
WINDOW_AFTER_DAYS: Final = 90
FLAG_HORIZON_DAYS: Final = 365
T1_MIN_VINTAGES: Final = 5
T1_MIN_SPAN_YEARS: Final = 3
T1_MIN_MATCH_RATE: Final = Decimal("0.5")
T2_MIN_GAP: Final = Decimal("0.20")
MIN_CELL_N: Final = 30
T3_MIN_RECLASSIFIED: Final = Decimal("0.20")
BAND_HALF_WIDTH: Final = Decimal("0.10")
PLACEHOLDER_SCHEMES: Final = frozenset({"BLANK", "WORKS", "N A", "NA", "TBC", ""})


def normalise_scheme(value: object) -> str | None:
    text = " ".join(str(value or "").upper().split()).replace("SHETL-", "SHET-")
    text = re.sub(r"\s*&\s*|\s+AND\s+", " & ", text)
    return None if text.strip(" &") in PLACEHOLDER_SCHEMES else text


@dataclass(frozen=True)
class TwrRow:
    project_name: str
    customer: str
    site: str
    project_number: str
    scheme: str
    connection_date: date | None


@dataclass(frozen=True)
class TwrVintage:
    t_public: date
    rows: tuple[TwrRow, ...]


def scheme_completion_by_vintage(vintages: list[TwrVintage]) -> dict[str, list[tuple[date, date]]]:
    """Per scheme, (t_public, earliest dependent connection date) per vintage — the proxy."""
    timelines: dict[str, list[tuple[date, date]]] = defaultdict(list)
    for vintage in sorted(vintages, key=lambda v: v.t_public):
        earliest: dict[str, date] = {}
        for row in vintage.rows:
            scheme = normalise_scheme(row.scheme)
            if scheme is None or row.connection_date is None:
                continue
            if scheme not in earliest or row.connection_date < earliest[scheme]:
                earliest[scheme] = row.connection_date
        for scheme, d in earliest.items():
            timelines[scheme].append((vintage.t_public, d))
    return dict(timelines)


def works_moves(timeline: list[tuple[date, date]]) -> list[tuple[date, int]]:
    """(t_public, signed months) for every change in the proxy completion date."""
    moves = []
    for (_, previous), (t_public, current) in zip(timeline, timeline[1:], strict=False):
        if current != previous:
            moves.append((t_public, months_between(previous, current)))
    return moves


def slipped_before(timeline: list[tuple[date, date]], t: date) -> bool:
    return any(
        t_public < t and months >= WORKS_MOVE_MONTHS for t_public, months in works_moves(timeline)
    )


def _keys(project_name: object, customer: object, site: object) -> tuple[str, str]:
    return (
        f"{normalise(customer)}|{normalise(site)}",
        f"{normalise(project_name)}|{normalise(site)}",
    )


def project_schemes(vintages: list[TwrVintage]) -> dict[str, set[str]]:
    """Every join key (customer|site, name|site, number) → the schemes ever attached."""
    index: dict[str, set[str]] = defaultdict(set)
    for vintage in vintages:
        for row in vintage.rows:
            scheme = normalise_scheme(row.scheme)
            if scheme is None:
                continue
            by_customer, by_name = _keys(row.project_name, row.customer, row.site)
            index[f"cs:{by_customer}"].add(scheme)
            index[f"ns:{by_name}"].add(scheme)
            if row.project_number:
                index[f"pn:{row.project_number.strip().upper()}"].add(scheme)
    return dict(index)


def tec_key_parts(key: str) -> tuple[str, str, str]:
    """(name, customer, site) from a 005 identity key `name:<n>|<c>|<s>#<stage>`."""
    body = key.split("#", 1)[0].removeprefix("name:")
    name, customer, site = (body.split("|") + ["", "", ""])[:3]
    return name, customer, site


def match_schemes(
    key: str, index: dict[str, set[str]], project_number: str | None = None
) -> set[str]:
    """Declared join order: exact project number, then customer|site, then name|site."""
    if project_number:
        found = index.get(f"pn:{project_number.strip().upper()}")
        if found:
            return set(found)
    name, customer, site = tec_key_parts(key)
    found = index.get(f"cs:{customer}|{site}")
    if found:
        return set(found)
    return set(index.get(f"ns:{name}|{site}", set()))


@dataclass(frozen=True)
class Attribution:
    t_public: date
    months: int
    outcome: str  # works_led | project_led | unattributable
    schemes_moved: tuple[str, ...]


def attribute_revisions(
    timeline: list[Observation],
    schemes: set[str],
    scheme_timelines: dict[str, list[tuple[date, date]]],
) -> list[Attribution]:
    results = []
    for previous, current in zip(timeline, timeline[1:], strict=False):
        if (
            not (previous.effective and current.effective)
            or previous.effective == current.effective
        ):
            continue
        months = months_between(previous.effective, current.effective)
        if not schemes:
            results.append(Attribution(current.t_public, months, "unattributable", ()))
            continue
        lo = current.t_public - timedelta(days=WINDOW_BEFORE_DAYS)
        hi = current.t_public + timedelta(days=WINDOW_AFTER_DAYS)
        moved = tuple(
            sorted(
                scheme
                for scheme in schemes
                for t_public, delta in works_moves(scheme_timelines.get(scheme, []))
                if lo <= t_public <= hi
                and abs(delta) >= WORKS_MOVE_MONTHS
                and (delta > 0) == (months > 0)
            )
        )
        results.append(
            Attribution(current.t_public, months, "works_led" if moved else "project_led", moved)
        )
    return results


def works_flag(
    metrics: ProjectMetrics, schemes: set[str], scheme_timelines: dict[str, list[tuple[date, date]]]
) -> bool | None:
    """slipped_before(first observation + 12 months) over the matched schemes; None if unmatched."""
    if not schemes:
        return None
    horizon = metrics.first_observed + timedelta(days=FLAG_HORIZON_DAYS)
    return any(slipped_before(scheme_timelines.get(s, []), horizon) for s in schemes)


@dataclass(frozen=True)
class T1Result:
    vintages: int
    span_years: Decimal
    population: int
    matched: int
    match_rate: Decimal | None
    passes: bool


def t1_measurability(
    vintages: list[TwrVintage], population: list[ProjectMetrics], flags: dict[str, bool | None]
) -> T1Result:
    dates = sorted(v.t_public for v in vintages)
    span = Decimal((dates[-1] - dates[0]).days) / Decimal(365) if len(dates) > 1 else Decimal(0)
    matched = sum(1 for m in population if flags.get(m.key) is not None)
    rate = Decimal(matched) / Decimal(len(population)) if population else None
    passes = (
        len(dates) >= T1_MIN_VINTAGES
        and span >= T1_MIN_SPAN_YEARS
        and rate is not None
        and rate >= T1_MIN_MATCH_RATE
    )
    return T1Result(len(dates), span, len(population), matched, rate, passes)


def _slipped(m: ProjectMetrics) -> bool:
    return m.net_slip_months is not None and m.net_slip_months >= 24


def _rate(items: list[ProjectMetrics]) -> Decimal | None:
    return Decimal(sum(1 for m in items if _slipped(m))) / Decimal(len(items)) if items else None


@dataclass(frozen=True)
class T2Result:
    n_flagged: int
    n_unflagged: int
    rate_flagged: Decimal | None
    rate_unflagged: Decimal | None
    gap: Decimal | None
    holds_in_both_cohorts: bool
    passes: bool


def t2_discrimination(matched: list[ProjectMetrics], flags: dict[str, bool | None]) -> T2Result:
    flagged = [m for m in matched if flags.get(m.key) is True]
    unflagged = [m for m in matched if flags.get(m.key) is False]
    rf, ru = _rate(flagged), _rate(unflagged)
    gap = rf - ru if rf is not None and ru is not None else None

    def direction(cohort: tuple[date, date]) -> bool | None:
        f = [m for m in flagged if cohort[0] <= m.first_observed < cohort[1]]
        u = [m for m in unflagged if cohort[0] <= m.first_observed < cohort[1]]
        a, b = _rate(f), _rate(u)
        return None if a is None or b is None else a > b

    holds = direction(COHORT_A) is True and direction(COHORT_B) is True
    passes = (
        len(flagged) >= MIN_CELL_N
        and len(unflagged) >= MIN_CELL_N
        and gap is not None
        and gap >= T2_MIN_GAP
        and holds
    )
    return T2Result(len(flagged), len(unflagged), rf, ru, gap, holds, passes)


def _band(rate: Decimal, pooled: Decimal) -> str:
    if rate < pooled - BAND_HALF_WIDTH:
        return "low"
    if rate > pooled + BAND_HALF_WIDTH:
        return "high"
    return "mid"


@dataclass(frozen=True)
class T3Result:
    pooled: Decimal | None
    bands_status_only: dict[str, str]
    bands_status_x_flag: dict[str, str]
    reclassified: int
    share_reclassified: Decimal | None
    passes: bool


def t3_reclassification(matched: list[ProjectMetrics], flags: dict[str, bool | None]) -> T3Result:
    if not matched:
        return T3Result(None, {}, {}, 0, None, False)
    pooled = _rate(matched) or Decimal(0)
    by_status: dict[str, list[ProjectMetrics]] = defaultdict(list)
    by_cell: dict[str, list[ProjectMetrics]] = defaultdict(list)
    for m in matched:
        status = m.first_status or "unknown"
        by_status[status].append(m)
        by_cell[f"{status}|{'works_slipped' if flags.get(m.key) else 'works_clean'}"].append(m)
    status_bands = {
        s: _band(_rate(v) or Decimal(0), pooled)
        for s, v in by_status.items()
        if len(v) >= MIN_CELL_N
    }
    cell_bands = {
        c: _band(_rate(v) or Decimal(0), pooled) for c, v in by_cell.items() if len(v) >= MIN_CELL_N
    }
    reclassified = 0
    for m in matched:
        status = m.first_status or "unknown"
        cell = f"{status}|{'works_slipped' if flags.get(m.key) else 'works_clean'}"
        before = status_bands.get(status)
        after = cell_bands.get(cell, before)  # a thin cell inherits the status-only band
        if before is not None and after is not None and before != after:
            reclassified += 1
    share = Decimal(reclassified) / Decimal(len(matched))
    return T3Result(
        pooled, status_bands, cell_bands, reclassified, share, share >= T3_MIN_RECLASSIFIED
    )


@dataclass(frozen=True)
class T4Result:
    attribution_of_big_slips: dict[str, int]
    attribution_by_status: dict[str, dict[str, int]]
    works_moves_total: int
    works_moves_top_vintage_share: Decimal | None
    twr_median_gap_days: int | None
    attribution_resolvable: bool


def t4_descriptive(
    attributions: dict[str, list[Attribution]],
    status_of: dict[str, str],
    scheme_timelines: dict[str, list[tuple[date, date]]],
    vintages: list[TwrVintage],
) -> T4Result:
    big: Counter[str] = Counter()
    by_status: dict[str, Counter[str]] = defaultdict(Counter)
    for key, items in attributions.items():
        for a in items:
            if a.months >= 24:
                big[a.outcome] += 1
                by_status[status_of.get(key, "unknown")][a.outcome] += 1
    move_dates: Counter[date] = Counter()
    for timeline in scheme_timelines.values():
        for t_public, delta in works_moves(timeline):
            if abs(delta) >= WORKS_MOVE_MONTHS:
                move_dates[t_public] += 1
    total = sum(move_dates.values())
    top_share = Decimal(move_dates.most_common(1)[0][1]) / Decimal(total) if total else None
    dates = sorted(v.t_public for v in vintages)
    gaps = [(b - a).days for a, b in zip(dates, dates[1:], strict=False)]
    median_gap = int(median(gaps)) if gaps else None
    return T4Result(
        dict(big),
        {s: dict(c) for s, c in by_status.items()},
        total,
        top_share,
        median_gap,
        median_gap is not None and median_gap <= WINDOW_BEFORE_DAYS,
    )


def parse_twr_row(record: dict[str, object]) -> TwrRow:
    """Map an era's column names onto TwrRow; unknown columns are ignored."""
    get = lambda *names: next((record[n] for n in names if record.get(n) not in (None, "")), "")  # noqa: E731
    return TwrRow(
        project_name=str(get("Project Name", "Project", "Generator Name")),
        customer=str(get("Account Name", "Customer", "Company Name")),
        site=str(get("Connection Site", "Site")),
        project_number=str(get("Project Number")),
        scheme=str(get("Scheme Name", "Scheme Number")),
        connection_date=parse_date(
            get("Mw Effective From", "MW Effective From", "Connection Date")
        ),
    )
