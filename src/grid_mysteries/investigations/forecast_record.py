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
    the latest published is read (it supersedes), and the others are
    named beside it by the caller."""
    candidates = index.get((scope, year), [])
    return max(candidates, key=lambda f: (f.published_on, f.figure_id)) if candidates else None


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
