"""022 — the Forecast Record: the pure rules that score a published battery
revenue forecast against the published realised figure for the period it
covered.

Vocabulary, as 022's declaration fixes it: a **forecast** is the published
headline figure, a **realised** figure (the outturn) is the published
realised figure, both in pounds per megawatt per year; a **vintage** is
one publication (publisher, date, page); **scope** is the population the
figure describes (``fleet``, a duration such as ``2h``, or a named
portfolio); **basis** is forecast, realised or potential; a figure's
**period** is the calendar years it covers, inclusive.

Nothing here reads a page. The figures arrive already read (by the
reading rule declared against the schema report); this module decides
which comparisons exist, computes each error with Decimal arithmetic, and
judges the propositions. Every verdict is "holds", "fails" or
"undecided"; no figure is adjusted for scope, and a scope mismatch is a
row of its own, never an error.
"""

import re
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Literal

Basis = Literal["forecast", "realised", "potential"]
Status = Literal["scored", "scope mismatch", "not yet scorable", "in-year, never scored"]

PCT_QUANTUM = Decimal("0.1")
GBP_QUANTUM = Decimal("1")
#: P-B's threshold: an absolute error above this share of the realised figure.
P_B_THRESHOLD_PCT = Decimal("20.0")


@dataclass(frozen=True, slots=True)
class Figure:
    """One published figure in GBP per MW per year, as read from one page."""

    figure_id: str
    publisher: str
    published_on: date
    source_url: str
    source_sha256: str
    basis: Basis
    scope: str
    value: Decimal
    period_start: int
    period_end: int
    as_printed: str

    def __post_init__(self) -> None:
        if self.period_end < self.period_start:
            raise ValueError(f"{self.figure_id}: period ends before it starts")
        if self.value < 0:
            raise ValueError(f"{self.figure_id}: a revenue figure below zero is not read")

    @property
    def vintage(self) -> tuple[str, date, str]:
        return (self.publisher, self.published_on, self.source_url)

    @property
    def years(self) -> range:
        return range(self.period_start, self.period_end + 1)

    @property
    def single_year(self) -> bool:
        return self.period_start == self.period_end


@dataclass(frozen=True, slots=True)
class Comparison:
    """One forecast figure against the realised side for one period."""

    forecast_id: str
    vintage: tuple[str, date, str]
    scope: str
    period_start: int
    period_end: int
    status: Status
    forecast: Decimal
    realised: Decimal | None
    realised_ids: tuple[str, ...]
    realised_scope: str | None
    signed_error: Decimal | None
    absolute_error: Decimal | None
    signed_error_pct: Decimal | None
    absolute_error_pct: Decimal | None
    scorable_after: date | None
    note: str


# -------------------------------------------------------------- the rules


def eligible_years(forecast: Figure) -> list[int]:
    """R-S1: a horizon year counts only if the forecast was published
    before the year began. A figure for the year of its own publication
    is in-year and is never scored."""
    return [y for y in forecast.years if y > forecast.published_on.year]


def realised_index(figures: list[Figure]) -> dict[tuple[str, int], list[Figure]]:
    """Single-year realised figures by (scope, year). Several publications
    of the same year and scope (a monthly index page and an annual review,
    say) are all kept; R-S3 decides which is read."""
    out: dict[tuple[str, int], list[Figure]] = defaultdict(list)
    for f in figures:
        if f.basis == "realised" and f.single_year:
            out[(f.scope, f.period_start)].append(f)
    return out


def realised_for(
    scope: str, year: int, index: dict[tuple[str, int], list[Figure]]
) -> Figure | None:
    """R-S3: where several realised figures exist for one scope and year,
    a figure published for the year outranks a twelve-month mean (R-S4),
    then the latest published is read (it supersedes); the others are
    named beside it by the caller."""
    candidates = index.get((scope, year), [])
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda f: (not f.figure_id.startswith("mean-12m:"), f.published_on, f.figure_id),
    )


def pct(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    if denominator == 0:
        return None
    return (numerator / denominator * 100).quantize(PCT_QUANTUM, rounding=ROUND_HALF_EVEN)


def mean(values: list[Decimal]) -> Decimal:
    return (sum(values, Decimal(0)) / len(values)).quantize(GBP_QUANTUM, rounding=ROUND_HALF_EVEN)


def compare(
    forecast: Figure, index: dict[tuple[str, int], list[Figure]], *, today: date
) -> Comparison:
    """R-C: forecast minus realised, signed and absolute, in GBP per MW per
    year and as a percentage of the realised figure; one row per forecast
    figure. A multi-year figure is compared with the mean of the realised
    years once every year of its period is realised (R-S2); a figure with
    no realised counterpart of the same scope but one of another scope is a
    scope mismatch (R-M), listed with both values and no error."""

    def row(
        status: Status,
        *,
        realised: Decimal | None = None,
        realised_ids: tuple[str, ...] = (),
        realised_scope: str | None = None,
        signed: Decimal | None = None,
        signed_pct: Decimal | None = None,
        scorable_after: date | None = None,
        note: str = "",
    ) -> Comparison:
        return Comparison(
            forecast_id=forecast.figure_id,
            vintage=forecast.vintage,
            scope=forecast.scope,
            period_start=forecast.period_start,
            period_end=forecast.period_end,
            status=status,
            forecast=forecast.value,
            realised=realised,
            realised_ids=realised_ids,
            realised_scope=realised_scope,
            signed_error=signed,
            absolute_error=abs(signed) if signed is not None else None,
            signed_error_pct=signed_pct,
            absolute_error_pct=abs(signed_pct) if signed_pct is not None else None,
            scorable_after=scorable_after,
            note=note,
        )

    years = eligible_years(forecast)
    if len(years) < len(forecast.years):
        # Some year of the period had begun when the figure was published.
        return row(
            "in-year, never scored",
            note=f"published {forecast.published_on.isoformat()}, inside the period it covers",
        )
    same_scope = [realised_for(forecast.scope, y, index) for y in years]
    if all(same_scope):
        reads = [r for r in same_scope if r is not None]
        values = [r.value for r in reads]
        realised = values[0] if len(values) == 1 else mean(values)
        return row(
            "scored",
            realised=realised,
            realised_ids=tuple(r.figure_id for r in reads),
            realised_scope=forecast.scope,
            signed=(forecast.value - realised).quantize(GBP_QUANTUM, rounding=ROUND_HALF_EVEN),
            signed_pct=pct(forecast.value - realised, realised),
            note="mean of the realised years" if len(values) > 1 else "",
        )
    other_scopes = sorted(
        {s for (s, y), figs in index.items() if y in years and s != forecast.scope and figs}
    )
    complete_other = [s for s in other_scopes if all(realised_for(s, y, index) for y in years)]
    if complete_other:
        s = complete_other[0]
        reads = [r for y in years if (r := realised_for(s, y, index)) is not None]
        values = [r.value for r in reads]
        others = (
            f"; other scopes realised: {', '.join(complete_other[1:])}"
            if complete_other[1:]
            else ""
        )
        return row(
            "scope mismatch",
            realised=values[0] if len(values) == 1 else mean(values),
            realised_ids=tuple(r.figure_id for r in reads),
            realised_scope=s,
            note=(
                f"realised figure published for scope {s!r}, forecast is for "
                f"{forecast.scope!r}; reported, never adjusted{others}"
            ),
        )
    missing = ", ".join(str(y) for y in years if not realised_for(forecast.scope, y, index))
    ends = date(forecast.period_end, 12, 31)
    return row(
        "not yet scorable",
        scorable_after=date(forecast.period_end + 1, 1, 1) if today <= ends else today,
        note=f"no realised figure of scope {forecast.scope!r} for {missing}",
    )


def comparisons(figures: list[Figure], *, today: date) -> list[Comparison]:
    """Every forecast figure, one row each, in publication order."""
    index = realised_index(figures)
    forecasts = sorted(
        (f for f in figures if f.basis == "forecast"),
        key=lambda f: (
            f.published_on,
            f.source_url,
            f.period_start,
            f.period_end,
            f.scope,
            f.figure_id,
        ),
    )
    return [compare(f, index, today=today) for f in forecasts]


# -------------------------------------------------------- propositions


def scorable_vintages(rows: list[Comparison]) -> dict[tuple[str, date, str], list[Comparison]]:
    """A vintage is scorable when at least one of its figures is scored."""
    out: dict[tuple[str, date, str], list[Comparison]] = defaultdict(list)
    for r in rows:
        if r.status == "scored":
            out[r.vintage].append(r)
    return dict(sorted(out.items(), key=lambda kv: (kv[0][1], kv[0][2])))


def first_realised_year_rows(rows: list[Comparison]) -> list[Comparison]:
    """A vintage's rows for its earliest scored period start (the nearest
    year a forecast can be judged on). Multi-year rows count by their start."""
    first = min(r.period_start for r in rows)
    return [r for r in rows if r.period_start == first]


Verdict = Literal["holds", "fails", "undecided"]


def unanimous(
    rows: list[Comparison], test: Callable[[Comparison], bool]
) -> Literal["all", "none", "mixed"]:
    hits = [bool(test(r)) for r in rows]
    if all(hits):
        return "all"
    if not any(hits):
        return "none"
    return "mixed"


def proposition_a(rows: list[Comparison]) -> dict:
    """P-A: every scorable vintage overstated its first realised year
    (every scored row of that year has a positive signed error). A vintage
    with a mixed or negative first year falsifies it."""
    vintages = scorable_vintages(rows)
    per = {}
    for v, vrows in vintages.items():
        first = first_realised_year_rows(vrows)
        per[v] = {
            "first_year": first[0].period_start,
            "signed_errors": [str(r.signed_error) for r in first],
            "reading": {"all": "overstated", "none": "understated or exact", "mixed": "mixed"}[
                unanimous(first, lambda r: r.signed_error is not None and r.signed_error > 0)
            ],
        }
    if not per:
        verdict: Verdict = "undecided"
    elif all(p["reading"] == "overstated" for p in per.values()):
        verdict = "holds"
    else:
        verdict = "fails"
    return {
        "proposition": "P-A",
        "verdict": verdict,
        "scorable_vintages": len(per),
        "per_vintage": {f"{v[0]} {v[1].isoformat()} {v[2]}": p for v, p in per.items()},
        "falsified_by": [
            f"{v[0]} {v[1].isoformat()} {v[2]}"
            for v, p in per.items()
            if p["reading"] != "overstated"
        ],
    }


def proposition_b(rows: list[Comparison], threshold_pct: Decimal = P_B_THRESHOLD_PCT) -> dict:
    """P-B: the absolute error of the nearest-year forecast exceeds the
    threshold in more than half of the scorable vintages. A vintage
    exceeds when every first-year row exceeds; a mixed vintage counts as
    not exceeding."""
    vintages = scorable_vintages(rows)
    per = {}
    for v, vrows in vintages.items():
        first = first_realised_year_rows(vrows)
        reading = unanimous(
            first,
            lambda r: r.absolute_error_pct is not None and r.absolute_error_pct > threshold_pct,
        )
        per[v] = {
            "first_year": first[0].period_start,
            "absolute_errors_pct": [str(r.absolute_error_pct) for r in first],
            "exceeds": reading == "all",
            "reading": {"all": "exceeds", "none": "within", "mixed": "mixed"}[reading],
        }
    n = len(per)
    exceeding = sum(1 for p in per.values() if p["exceeds"])
    if n == 0:
        verdict: Verdict = "undecided"
    else:
        verdict = "holds" if exceeding * 2 > n else "fails"
    return {
        "proposition": "P-B",
        "threshold_pct": str(threshold_pct),
        "verdict": verdict,
        "scorable_vintages": n,
        "exceeding": exceeding,
        "per_vintage": {f"{v[0]} {v[1].isoformat()} {v[2]}": p for v, p in per.items()},
    }


def revisions(figures: list[Figure]) -> list[dict]:
    """R-V: for one publisher, consecutive vintages (by publication date)
    that both print a forecast for the same scope and period; the later
    value against the earlier, as down, up or unchanged. Every forecast
    figure takes part, scorable or not."""
    forecasts = [f for f in figures if f.basis == "forecast"]
    by_key: dict[tuple[str, str, int, int], list[Figure]] = defaultdict(list)
    for f in forecasts:
        by_key[(f.publisher, f.scope, f.period_start, f.period_end)].append(f)
    out = []
    for key, figs in sorted(by_key.items()):
        ordered = sorted(figs, key=lambda f: (f.published_on, f.source_url, f.figure_id))
        # One value per vintage: several figures of one key on one page is a
        # fact the schema pass will have shown; the first by id is read and
        # the others are listed.
        per_vintage: dict[tuple[str, date, str], list[Figure]] = defaultdict(list)
        for f in ordered:
            per_vintage[f.vintage].append(f)
        vintages = list(per_vintage.items())
        for (va, fa), (vb, fb) in zip(vintages, vintages[1:], strict=False):
            a, b = fa[0], fb[0]
            direction = (
                "down" if b.value < a.value else ("up" if b.value > a.value else "unchanged")
            )
            out.append(
                {
                    "publisher": key[0],
                    "scope": key[1],
                    "period_start": key[2],
                    "period_end": key[3],
                    "earlier": {
                        "published_on": va[1].isoformat(),
                        "url": va[2],
                        "figure_id": a.figure_id,
                        "value": str(a.value),
                    },
                    "later": {
                        "published_on": vb[1].isoformat(),
                        "url": vb[2],
                        "figure_id": b.figure_id,
                        "value": str(b.value),
                    },
                    "change": str(
                        (b.value - a.value).quantize(GBP_QUANTUM, rounding=ROUND_HALF_EVEN)
                    ),
                    "direction": direction,
                    "duplicates_on_page": [x.figure_id for x in fa[1:] + fb[1:]],
                }
            )
    return out


def proposition_c(figures: list[Figure]) -> dict:
    """P-C: successive vintages revised downward more often than upward.
    Holds when down > up over every revision pair; fails when up >= down;
    undecided with no pair."""
    pairs = revisions(figures)
    counts = Counter(p["direction"] for p in pairs)
    down, up = counts.get("down", 0), counts.get("up", 0)
    if not pairs:
        verdict: Verdict = "undecided"
    else:
        verdict = "holds" if down > up else "fails"
    return {
        "proposition": "P-C",
        "verdict": verdict,
        "pairs": len(pairs),
        "down": down,
        "up": up,
        "unchanged": counts.get("unchanged", 0),
        "revisions": pairs,
    }


def propositions(figures: list[Figure], rows: list[Comparison]) -> dict[str, dict]:
    return {
        "P-A": proposition_a(rows),
        "P-B": proposition_b(rows),
        "P-C": proposition_c(figures),
    }


def not_yet_scorable_table(rows: list[Comparison]) -> list[dict]:
    """The 'not yet scorable' table is a result, not a gap: each unscored
    forecast with the date it becomes scorable or why it never will."""
    out = []
    for r in rows:
        if r.status in ("not yet scorable", "in-year, never scored"):
            out.append(
                {
                    "forecast_id": r.forecast_id,
                    "publisher": r.vintage[0],
                    "published_on": r.vintage[1].isoformat(),
                    "url": r.vintage[2],
                    "scope": r.scope,
                    "period": f"{r.period_start}"
                    if r.period_start == r.period_end
                    else f"{r.period_start}-{r.period_end}",
                    "status": r.status,
                    "scorable_after": r.scorable_after.isoformat() if r.scorable_after else None,
                    "note": r.note,
                }
            )
    return out


def require_unchanged(committed: dict[str, str], recomputed: dict[str, str]) -> list[str]:
    """F3: keys committed under this rule version whose line would differ
    on recompute. The caller refuses if any."""
    return sorted(k for k, line in committed.items() if k in recomputed and recomputed[k] != line)


# ---------------------------------------------------------- the reader
# R-R1 to R-R7 of 022's declaration: a schema-report page (its URL, title,
# dates and figure-looking strings with their sentences) becomes figures,
# monthly index readings, or declined strings, each naming the rule that
# decided. Nothing is read from a page that is not in the schema report.

MONTHS = {
    m: n
    for n, m in enumerate(
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
MONTH_RE = "|".join(MONTHS)
FIGURE_RE = re.compile(
    r"£\s?(?P<amount>\d[\d,]*(?:\.\d+)?)\s?(?P<mult>k|m|bn)?"
    r"(?P<range>\s?(?:-|–|—|to)\s?£?\s?\d[\d,]*(?:\.\d+)?\s?(?:k|m|bn)?)?"
    r"\s?(?:/|per)\s?(?P<unit>MWh|kWh|MW|kW)"
    r"(?:\s?(?:/|per)\s?(?P<period>year|yr|y\b|annum|a\b|month|mo\b|hour|hr|h\b))?",
    re.IGNORECASE,
)
CLAUSE_SPLIT = re.compile(r"[,;:]|\s[-–—]\s")
COMPONENT_WORDS = (
    "wholesale",
    "balancing mechanism",
    "frequency response",
    "reserve",
    "capacity market",
    "imbalance",
    "dynamic containment",
    "dynamic regulation",
    "dynamic moderation",
    "ancillary",
    "trading revenue",
    "merchant markets",
    "arbitrage",
    "in the service",
    "reactive power",
    "offer dispatch",
    "duos",
    "tnuos",
    "auction",
    "clearing price",
    "cleared at",
    "t-4",
    "t-1",
)
SUBSET_WORDS = (
    "highest-earning",
    "top-performing",
    "top performing",
    "top quartile",
    "best ",
    "beat ",
    "one battery",
    "one system",
    "some batteries",
    "four batteries",
    "individual batter",
    "upwards of",
    "jamesfield",
    "wishaw",
    "coventry",
    "capenhurst",
    "wormald green",
    "basis risk",
    "fixed leg",
    "floating leg",
    "swap",
    "perfect forecasting",
    "would've",
    "would have",
)
DAY_WORDS = (
    "single-day",
    "daily",
    "on the day",
    "for the day",
    "weekend",
    "bank holiday",
    "some days",
)
ORDINAL_DAY = re.compile(r"\b\d{1,2}(?:st|nd|rd|th)\b")
POTENTIAL_WORDS = (
    "potential",
    "must increase",
    "required",
    "worth ",
    "toll",
    "agreement",
    "contract",
    "viable",
    "scenario",
    "sensitivity",
    "assumed",
    "assuming",
    "estimate",
    "could be",
    "could generate",
    "capex",
    "cost",
    "valu",
    "minimum",
    "floor",
)
FORECAST_WORDS = (
    "forecast",
    "project",
    "outlook",
    "expect",
    "will ",
    "would ",
    "out to",
    "by 20",
    "end of 20",
    "long term",
    "long-term",
    "horizon",
)
CHANGE_RE = re.compile(
    r"\bby\s*(?:a\s+|an\s+|around\s+|c\.\s*)?£|"
    r"\b(?:rose|fell|up|down|increased|decreased|reduced|dropped|dropping|rising|subtracting|"
    r"contributing|added|adding|jumped|surged|grew)\s+(?:a\s+)?(?:further\s+)?(?:massive\s+)?"
    r"(?:another\s+)?£|"
    r"£[\d.,]+k?\s?/\s?[^\s]+\s+(?:higher|lower|more|less|up|down|uplift|reduction|increase|"
    r"decrease|swing|boost|drop|fall|loss)\b|"
    r"\b(?:reduction|uplift|boost|swing|increase|drop|fall|rise|decline)\s+(?:of|in)\s+"
    r"(?:around\s+|about\s+|c\.\s*)?£|\bup to £|\bover £|\bmore than £|\bexceed(?:ed|s)? this by",
    re.IGNORECASE,
)
ANNUALISED = re.compile(r"annuali[sz]ed", re.IGNORECASE)
STARTING_POINT_RE = re.compile(
    r"\bfrom\s+(?:around\s+|about\s+|c\.\s*|roughly\s+)?£$", re.IGNORECASE
)
YEAR_RE = re.compile(r"\b(20[2-5]\d)\b")
MONTH_YEAR_RE = re.compile(
    rf"(?<!\d\s)(?<!\d)\b(?P<month>{MONTH_RE})\s+(?P<year>20[2-5]\d)\b", re.IGNORECASE
)
MONTH_ONLY_RE = re.compile(
    rf"(?<!\d\s)(?<!\d)\b(?P<month>{MONTH_RE})\b(?!\s+20[2-5]\d)", re.IGNORECASE
)
ANNUAL_RE = re.compile(
    r"\b(?:in|for all of|across|throughout|during|over|for)\s+"
    r"(?:the (?:whole|full|calendar) year\s+)?(?P<year>20[2-5]\d)\b"
    r"|\b(?:the\s+)?(?P<year2>20[2-5]\d)\s+(?:average|revenues|calendar year|as a whole)\b"
    r"|\bFY\s?(?P<year3>20[2-5]\d)\b"
    r"|\baverage\s+(?P<year4>20[2-5]\d)\s+revenues\b",
    re.IGNORECASE,
)
HORIZON_RE = re.compile(
    r"\b(?:out to|through to|through|until|towards|to)\s+(?P<year>20[2-5]\d)\b", re.IGNORECASE
)
END_YEAR_RE = re.compile(
    r"\b(?:by|at the end of|by the end of|in|for)\s+(?P<year>20[2-5]\d)\b", re.IGNORECASE
)
PARTIAL_RE = re.compile(
    r"\b(?:h[12]\s+20\d\d|q[1-4](?:\s+20\d\d)?|first half|second half|half[- ]year|winter|summer|"
    r"so far|to date|year to date|last (?:four|six|twelve|12|two|three) (?:months|years)|"
    r"past (?:two|three) years|the three months|four months prior|(?:this|last) winter|"
    rf"(?:{MONTH_RE})\s+(?:to|through|-)\s+(?:{MONTH_RE})|the period|the reporting period|"
    r"the year's average|this year|last year|the year to)\b",
    re.IGNORECASE,
)
FY_TITLE_RE = re.compile(r"31 December (?P<year>20\d\d)")
FUND_YEAR_WORDS = ("for the year", "during the year", "the portfolio generated", "over the year")
DURATION_RE = re.compile(
    r"\b(?P<n>1|2|4|8|one|two|four|eight)[- ]?(?:h\b|hr\b|hour\b|hours\b)", re.IGNORECASE
)
DURATION_WORDS = {"one": "1", "two": "2", "four": "4", "eight": "8"}
EXCL_CM = re.compile(r"excluding (?:the )?capacity market|ex[- ]?cm\b", re.IGNORECASE)
INCL_CM = re.compile(r"(?:with|including) (?:the )?capacity market", re.IGNORECASE)
FLEET_WORDS = (
    "great britain",
    " gb ",
    "gb bess",
    "me bess",
    "index",
    "batteries",
    "battery energy storage",
    "battery revenues",
    "battery storage revenues",
    "bess",
    "fleet",
    "the benchmark",
    "modo benchmark",
)
TITLE_MONTH_RE = re.compile(
    rf"\b(?P<month>{MONTH_RE})\b(?:\s+(?P<year>20[2-5]\d)\b)?", re.IGNORECASE
)


@dataclass(frozen=True, slots=True)
class Reading:
    """One figure-looking string's fate under the reading rules."""

    page_url: str
    page_sha256: str
    published_on: date | None
    as_printed: str
    sentence: str
    rule: str
    outcome: Literal["figure", "monthly", "declined"]
    figure: Figure | None = None
    monthly: tuple[int, int, Decimal, str] | None = None  # year, month, value, scope
    offset: int = 0

    @property
    def key(self) -> str:
        return f"{self.page_sha256[:12]}|{self.offset}"


@dataclass(frozen=True, slots=True)
class Period:
    kind: Literal["month", "annual", "horizon", "endyear", "partial"]
    start: int
    end: int
    month: int | None
    at: int  # character position in the sentence


def clause_of(sentence: str, at: int, length: int) -> str:
    """The clause the figure sits in: between the clause separators
    (comma, semicolon, colon, spaced dash, bracket) on either side."""
    before, after = sentence[:at], sentence[at + length :]
    starts = [m.end() for m in CLAUSE_SPLIT.finditer(before)]
    lo = starts[-1] if starts else 0
    ends = [m.start() for m in CLAUSE_SPLIT.finditer(after)]
    hi = at + length + (ends[0] if ends else len(after))
    return sentence[lo:hi].strip()


def amount_of(match: re.Match[str], sentence: str) -> Decimal | str:
    """R-R2: the value in pounds per MW per year, or the rule that declines."""
    if match.group("range"):
        return "R-R2 range, not a point figure"
    unit = match.group("unit").lower()
    if unit in ("mwh", "kwh"):
        return "R-R2 a price per MWh, not a revenue per MW"
    period = (match.group("period") or "").lower()
    if period in ("hour", "hr", "h"):
        return "R-R2 an hourly rate"
    if period in ("month", "mo"):
        return "R-R2 a monthly rate"
    value = Decimal(match.group("amount").replace(",", ""))
    mult = (match.group("mult") or "").lower()
    if mult == "k":
        value *= 1000
    elif mult:
        return "R-R2 a multiplier other than k"
    if unit == "kw":
        value *= 1000
    if not period and not ANNUALISED.search(sentence):
        return "R-R2 no period unit"
    return value.quantize(GBP_QUANTUM) if value == value.to_integral_value() else value


def publication_date(page: dict) -> date | None:
    """R-R1: article:published_time, else datePublished, else the RNS
    listing's dateCreated; the first ten characters as an ISO date."""
    dates = page.get("dates") or {}
    for key in ("meta:article:published_time", "json:datePublished", "json:dateCreated"):
        if dates.get(key):
            try:
                return date.fromisoformat(dates[key][0][:10])
            except ValueError:
                return None
    return None


def title_month(title: str | None, published: date | None) -> tuple[int, int] | None:
    """A monthly index post names its month in its title, with or without
    the year; without it, the year is the month's most recent occurrence
    at or before publication."""
    m = TITLE_MONTH_RE.search(title or "")
    if not m or published is None:
        return None
    mo = MONTHS[m.group("month").lower()]
    if m.group("year"):
        return (int(m.group("year")), mo)
    return (published.year if mo <= published.month else published.year - 1, mo)


def months_before(later: tuple[int, int], earlier: tuple[int, int]) -> int:
    return (later[0] - earlier[0]) * 12 + (later[1] - earlier[1])


def periods_in(
    sentence: str, *, published: date, page_month: tuple[int, int] | None
) -> list[Period]:
    """R-R5: every period the sentence names, with where it names it."""
    out: list[Period] = []
    for m in PARTIAL_RE.finditer(sentence):
        out.append(Period("partial", 0, 0, None, m.start()))
    for m in MONTH_YEAR_RE.finditer(sentence):
        y, mo = int(m.group("year")), MONTHS[m.group("month").lower()]
        out.append(Period("month", y, y, mo, m.start()))
    anchor = page_month or (published.year, published.month)
    for m in MONTH_ONLY_RE.finditer(sentence):
        mo = MONTHS[m.group("month").lower()]
        # the most recent occurrence of that month at or before the anchor
        y = anchor[0] if mo <= anchor[1] else anchor[0] - 1
        out.append(Period("month", y, y, mo, m.start()))
    for m in ANNUAL_RE.finditer(sentence):
        y = int(m.group("year") or m.group("year2") or m.group("year3") or m.group("year4"))
        out.append(Period("annual", y, y, None, m.start()))
    for m in HORIZON_RE.finditer(sentence):
        y = int(m.group("year"))
        if y > published.year:
            out.append(Period("horizon", published.year + 1, y, None, m.start()))
    for m in END_YEAR_RE.finditer(sentence):
        y = int(m.group("year"))
        if y >= published.year and not any(p.kind == "annual" and p.at == m.start() for p in out):
            out.append(Period("endyear", y, y, None, m.start()))
    return out


def nearest(periods: list[Period], at: int, length: int) -> Period | None:
    def distance(p: Period) -> int:
        return min(abs(p.at - (at + length)), abs(at - p.at))

    return min(periods, key=distance) if periods else None


def scope_of(clause: str, sentence: str, *, default_fleet: bool) -> str | None:
    """R-R3: a duration in the clause, else the fleet when the clause (or,
    failing that, a sentence with no component or subset word anywhere)
    names it; on a monthly index post the fleet is the page's population."""
    low = f" {clause.lower()} "
    low_sentence = f" {sentence.lower()} "
    m = DURATION_RE.search(clause)
    if m:
        n = m.group("n").lower()
        scope = f"{DURATION_WORDS.get(n, n)}h"
    else:
        in_clause = any(w in low for w in FLEET_WORDS) or default_fleet
        in_sentence = any(w in low_sentence for w in FLEET_WORDS) and not any(
            w in low_sentence for w in COMPONENT_WORDS + SUBSET_WORDS
        )
        if not (in_clause or in_sentence):
            return None
        scope = "fleet"
    if EXCL_CM.search(sentence):
        scope += "-excl-cm"
    elif INCL_CM.search(sentence):
        scope += "-incl-cm"
    return scope


def read_page(page: dict, *, publisher: str, portfolio_scope: str | None = None) -> list[Reading]:
    """R-R1 to R-R7 over one schema-report page. ``portfolio_scope`` names
    a fund's own scope for RNS pages; Modo's pages get fleet or duration
    scopes. On a monthly index post (a month and year in the title) only
    the page's own month is read, and only when every string read for it
    agrees."""
    url, sha = page["url"], page["sha256"]
    published = publication_date(page)
    title = (page.get("title") or "").strip()
    page_month = title_month(title, published) if portfolio_scope is None else None
    fund_year = FY_TITLE_RE.search(title) if portfolio_scope else None
    out: list[Reading] = []
    seen: set[tuple[str, str]] = set()
    monthly_candidates: list[tuple[Decimal, str, dict, str]] = []

    def declined(f: dict, rule: str) -> Reading:
        return Reading(
            url,
            sha,
            published,
            f["as_printed"],
            f["sentence"],
            rule,
            "declined",
            offset=f["offset"],
        )

    for f in page.get("figures") or []:
        sentence = " ".join(f["sentence"].split())
        printed = f["as_printed"]
        if str(page.get("format", "")).startswith("pdf"):
            out.append(
                declined(
                    f, "R-R0 PDF: layout text interleaves columns; the RNS text is read instead"
                )
            )
            continue
        if published is None:
            out.append(declined(f, "R-R1 no publication date declared"))
            continue
        if published < date(2023, 1, 1):
            out.append(declined(f, "R-R6 published before 2023"))
            continue
        if sentence.startswith("{") or '":"' in sentence:
            out.append(declined(f, "R-R0 JSON payload"))
            continue
        if sentence.startswith("Back ") or (
            title and sentence.lower().startswith(title.lower()[:40])
        ):
            out.append(declined(f, "R-R0 title or navigation duplicate"))
            continue
        key = (printed, sentence.lower())
        if key in seen:
            out.append(declined(f, "R-R0 duplicate string in the same sentence"))
            continue
        seen.add(key)
        m = FIGURE_RE.search(printed)
        if not m:
            out.append(declined(f, "R-R2 unparsed"))
            continue
        value = amount_of(m, sentence)
        if isinstance(value, str):
            out.append(declined(f, value))
            continue
        at = sentence.find(printed)
        if at < 0:
            at, printed_len = 0, 0
        else:
            printed_len = len(printed)
        clause = clause_of(sentence, at, printed_len)
        low_clause, low_sentence = clause.lower(), sentence.lower()
        clause_at = sentence.find(clause)
        preceding = sentence[:clause_at].lower()
        preceding = preceding[preceding.rfind(",", 0, max(0, len(preceding) - 2)) + 1 :]
        unqualified = INCL_CM.sub("", EXCL_CM.sub("", low_clause))
        if any(w in unqualified for w in COMPONENT_WORDS):
            out.append(declined(f, "R-R3 a revenue component, not the total"))
            continue
        if any(w in low_clause or w in preceding for w in SUBSET_WORDS):
            out.append(declined(f, "R-R3 a named asset or subset, not the population"))
            continue
        if PARTIAL_RE.search(clause) or PARTIAL_RE.search(preceding):
            out.append(declined(f, "R-R5 a partial period (half, quarter, season or to date)"))
            continue
        if any(w in low_sentence for w in DAY_WORDS) or ORDINAL_DAY.search(sentence):
            out.append(declined(f, "R-R5 a day, not a month or a year"))
            continue
        if CHANGE_RE.search(clause):
            out.append(declined(f, "R-R2 a change, not a level"))
            continue
        if STARTING_POINT_RE.search(sentence[max(0, at - 16) : at + 1]):
            out.append(declined(f, "R-R2 the starting point of a stated change, not its level"))
            continue
        if any(w in low_sentence for w in POTENTIAL_WORDS):
            out.append(
                declined(
                    f,
                    "R-R4 potential, required, contracted or assumed, not a forecast or an outturn",
                )
            )
            continue
        scope = portfolio_scope or scope_of(clause, sentence, default_fleet=page_month is not None)
        if scope is None:
            out.append(declined(f, "R-R3 no population named in the clause"))
            continue
        candidates = periods_in(sentence, published=published, page_month=page_month)
        in_clause = [c for c in candidates if clause_at <= c.at < clause_at + len(clause)]
        if in_clause:
            period = nearest(in_clause, at, printed_len)
        elif portfolio_scope:
            # a fund's headline takes its year from the RNS title, never
            # from another clause of the sentence (R-R5)
            period = None
            if fund_year and any(w in low_sentence for w in FUND_YEAR_WORDS):
                y = int(fund_year.group("year"))
                period = Period("annual", y, y, None, 0)
        else:
            period = nearest(candidates, at, printed_len)
        if period is None:
            out.append(declined(f, "R-R5 period not stated"))
            continue
        if period.kind == "partial":
            out.append(declined(f, "R-R5 a partial period (half, quarter, season or to date)"))
            continue
        if period.kind == "month":
            if portfolio_scope:
                out.append(declined(f, "R-R5 a fund figure dated by a month, not a calendar year"))
                continue
            if page_month and (period.start, period.month) != page_month:
                out.append(declined(f, "R-R5 another month than the page's own"))
                continue
            assert period.month is not None
            gap = months_before((published.year, published.month), (period.start, period.month))
            if page_month is None and not 0 <= gap <= 3:
                out.append(declined(f, "R-R5 a month not current to the page"))
                continue
            assert period.month is not None
            monthly_candidates.append((value, scope, f, sentence))
            out.append(
                Reading(
                    url,
                    sha,
                    published,
                    printed,
                    sentence,
                    "R-R5 monthly figure",
                    "monthly",
                    monthly=(period.start, period.month, value, scope),
                    offset=f["offset"],
                )
            )
            continue
        is_forecast = any(w in low_sentence for w in FORECAST_WORDS)
        if period.kind in ("horizon", "endyear") or period.start > published.year:
            basis: Basis = "forecast"
        elif period.start == published.year:
            if is_forecast:
                basis = "forecast"  # an in-year forecast: listed, never scored (R-S1)
            else:
                out.append(declined(f, "R-R5 the year of publication, not complete"))
                continue
        else:
            basis = "realised"
        if basis == "forecast" and not is_forecast:
            out.append(declined(f, "R-R4 a future year with no forecast word"))
            continue
        if (
            basis == "realised"
            and is_forecast
            and period.kind == "annual"
            and "average" not in low_clause
        ):
            out.append(declined(f, "R-R4 a past year in a forecast sentence"))
            continue
        figure = Figure(
            figure_id=f"{sha[:12]}:{f['offset']}",
            publisher=publisher,
            published_on=published,
            source_url=url,
            source_sha256=sha,
            basis=basis,
            scope=scope,
            value=value,
            period_start=period.start,
            period_end=period.end,
            as_printed=printed,
        )
        out.append(
            Reading(
                url,
                sha,
                published,
                printed,
                sentence,
                f"R-R5 {period.kind} figure, basis {basis}",
                "figure",
                figure=figure,
                offset=f["offset"],
            )
        )
    # R-R7 on a monthly post: the page's month is read only if every string
    # read for it agrees to the nearest thousand pounds; the most precise is read.
    if page_month:
        thousands: dict[str, set[Decimal]] = defaultdict(set)
        for value, scope, _f, _s in monthly_candidates:
            thousands[scope].add(value.quantize(Decimal("1E3"), rounding=ROUND_HALF_EVEN))
        disagreeing = {s for s, vs in thousands.items() if len(vs) > 1}
        most_precise: dict[str, tuple[int, Decimal]] = {}
        for value, scope, f, _s in monthly_candidates:
            if scope not in disagreeing:
                best = most_precise.get(scope)
                digits = precision(f["as_printed"])
                if best is None or digits > best[0]:
                    most_precise[scope] = (digits, value)
        rewritten = []
        for r in out:
            if r.outcome == "monthly" and r.monthly:
                scope = r.monthly[3]
                if scope in disagreeing:
                    rewritten.append(
                        Reading(
                            r.page_url,
                            r.page_sha256,
                            r.published_on,
                            r.as_printed,
                            r.sentence,
                            "R-R7 the page prints figures for its own month that differ by more "
                            "than rounding; none read",
                            "declined",
                            offset=r.offset,
                        )
                    )
                    continue
                if r.monthly[2] != most_precise[scope][1]:
                    rewritten.append(
                        Reading(
                            r.page_url,
                            r.page_sha256,
                            r.published_on,
                            r.as_printed,
                            r.sentence,
                            "R-R7 the same month's figure, printed less precisely than another "
                            "string on the page",
                            "declined",
                            offset=r.offset,
                        )
                    )
                    continue
            rewritten.append(r)
        out = rewritten
    return out


def precision(printed: str) -> int:
    """Significant digits in the amount as printed: 3 for £55.6k, 2 for
    £56k, 5 for £61,500; the more, the more precise the print."""
    m = FIGURE_RE.search(printed)
    return len(re.sub(r"[^0-9]", "", m.group("amount"))) if m else 0


def choose_months(
    readings: list[Reading],
) -> tuple[dict[tuple[str, int, int], Reading], list[dict]]:
    """R-S4's choice per scope, year and month: where every string read
    for the month agrees to the nearest thousand pounds, the most precise
    (then the latest published); where they differ beyond rounding, the
    latest published is read and the difference is listed (F4)."""
    groups: dict[tuple[str, int, int], list[Reading]] = defaultdict(list)
    for r in readings:
        if r.outcome == "monthly" and r.monthly is not None and r.published_on is not None:
            year, month, _value, scope = r.monthly
            groups[(scope, year, month)].append(r)
    chosen: dict[tuple[str, int, int], Reading] = {}
    restated: list[dict] = []
    for k, rs in groups.items():
        values = [r.monthly[2] for r in rs if r.monthly]
        thousands = {v.quantize(Decimal("1E3"), rounding=ROUND_HALF_EVEN) for v in values}
        if len(thousands) == 1:
            chosen[k] = max(
                rs,
                key=lambda r: (
                    precision(r.as_printed),
                    r.published_on or date.min,
                    r.page_url,
                ),
            )
        else:
            chosen[k] = max(rs, key=lambda r: (r.published_on or date.min, r.page_url))
            read = chosen[k].monthly
            restated.append(
                {
                    "scope": k[0],
                    "year": k[1],
                    "month": k[2],
                    "read": str(read[2]) if read else None,
                    "read_from": chosen[k].page_url,
                    "others": [
                        {
                            "value": str(r.monthly[2]),
                            "page": r.page_url,
                            "published_on": r.published_on.isoformat() if r.published_on else None,
                        }
                        for r in rs
                        if r is not chosen[k] and r.monthly
                    ],
                }
            )
    return chosen, restated


def annual_from_months(
    readings: list[Reading], *, publisher: str
) -> tuple[list[Figure], list[dict], list[dict]]:
    """R-S4: for each scope and calendar year with all twelve months read
    (the latest published figure per month), the mean of the twelve, as a
    realised figure whose id names its derivation; the months beside it."""
    latest, restated = choose_months(readings)
    figures, detail = [], []
    by_year: dict[tuple[str, int], list[Reading]] = defaultdict(list)
    for (scope, year, _month), r in latest.items():
        by_year[(scope, year)].append(r)
    for (scope, year), rs in sorted(by_year.items()):
        rs.sort(key=lambda r: r.monthly[1] if r.monthly else 0)
        months = [r.monthly[1] for r in rs if r.monthly]
        values = [r.monthly[2] for r in rs if r.monthly]
        complete = months == list(range(1, 13))
        detail.append(
            {
                "scope": scope,
                "year": year,
                "months_read": months,
                "complete": complete,
                "values": [str(v) for v in values],
                "pages": [r.page_url for r in rs],
                "mean": str(mean(values)) if complete else None,
            }
        )
        if complete:
            last = max(r.published_on for r in rs if r.published_on)
            figures.append(
                Figure(
                    figure_id=f"mean-12m:{scope}:{year}",
                    publisher=publisher,
                    published_on=last,
                    source_url="twelve pages, listed in evidence/months.json",
                    source_sha256="",
                    basis="realised",
                    scope=scope,
                    value=mean(values),
                    period_start=year,
                    period_end=year,
                    as_printed="mean of twelve monthly figures as published",
                )
            )
    return figures, detail, restated


PER_YEAR_UNIT = re.compile(r"(?:/|per)\s?(?:year|yr|y\b|annum)", re.IGNORECASE)
UNEXPLAINED_RULES = ("R-R5 period not stated", "R-R3 no population named in the clause")
F2_THRESHOLD_PCT = Decimal("33.3")


def falsifier_f2(readings: list[Reading], *, publisher: str) -> dict:
    """F2: of the per-year strings on the publisher's pages, the share
    declined for a period or population the rules could not find."""
    per_year = [
        r
        for r in readings
        if (r.figure.publisher if r.figure else None) == publisher
        or r.page_url
        and publisher == "Modo Energy"
        and "modoenergy.com" in r.page_url
    ]
    per_year = [r for r in per_year if PER_YEAR_UNIT.search(r.as_printed)]
    unexplained = [r for r in per_year if r.rule in UNEXPLAINED_RULES]
    share = pct(Decimal(len(unexplained)), Decimal(len(per_year))) if per_year else Decimal(0)
    return {
        "per_year_strings": len(per_year),
        "unexplained": len(unexplained),
        "share_pct": str(share),
        "threshold_pct": str(F2_THRESHOLD_PCT),
        "fires": share is not None and share > F2_THRESHOLD_PCT,
    }


def pipeline(
    modo_pages: list[dict],
    rns_pages: list[dict],
    *,
    today: date,
    language_path: str = "/research/en/",
) -> dict:
    """The whole computation, pure: readings, figures, months, rows,
    revisions, propositions and falsifiers, from schema-report pages."""
    readings: list[Reading] = []
    for page in modo_pages:
        if language_path in page["url"]:
            readings += read_page(page, publisher="Modo Energy")
    for page in rns_pages:
        url = page["url"].lower()
        ticker = (
            "GRID"
            if ("grid" in url or "greshamhouse" in url)
            else ("GSF" if "gsf" in url else "HEIT")
        )
        readings += read_page(
            page, publisher=f"{ticker} (fund RNS)", portfolio_scope=f"{ticker} portfolio"
        )
    means, detail, restated = annual_from_months(readings, publisher="Modo Energy")
    figures = [r.figure for r in readings if r.outcome == "figure" and r.figure] + means
    rows = comparisons(figures, today=today)
    revision_rows = revisions(figures)
    props = propositions(figures, rows)
    f1 = not scorable_vintages(rows)
    return {
        "readings": readings,
        "figures": figures,
        "months": {"detail": detail, "restated": restated},
        "comparisons": rows,
        "revisions": revision_rows,
        "propositions": props,
        "not_yet_scorable": not_yet_scorable_table(rows),
        "falsifiers": {
            "F1": f1,
            "F2": falsifier_f2(readings, publisher="Modo Energy"),
            "F4_restated_months": len(restated),
        },
    }
