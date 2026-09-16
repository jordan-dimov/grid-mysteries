"""Investigation 014 — GB connection slippage, in MW-years.

Pure logic over TEC Register vintages given as rows; no I/O. The
declaration in `investigations/014-gb-connection-slippage/DECLARATION.md`
governs, and every rule below is one it states.

- **Unit**: (identity, stage), 005 Amendment 1. Identity is the normalised
  (project name, customer name, connection site) triple; stage is the
  register's `Stage` with numeric spellings unified. Splits and merges are
  never repaired: a renamed row is a removal and a new entry.
- **Headline**: for every unit present in both a baseline vintage and the
  current vintage with a parseable date in both, the stage's TEC MW in the
  baseline (absolute `MW Increase / Decrease`) times the movement of the
  published effective-from date in years (days / 365.25, later is
  positive), summed. New entries, removals, capacity changes, undated and
  unweighted units are reconciliation items beside it, never inside it.
- **Baselines**: the previous vintage (the increment) and the latest
  vintage at least 365 days earlier in the same regime segment (the
  trailing year, which is the headline).
- **Day-month swap test**: a vintage whose date disagreements with its
  predecessor are mostly explained by exchanging day and month is read
  swapped; the counts are published.
- Vintages from December 2025 form a separate segment (connections-reform
  re-baselining); nothing is chained across the break.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.sources.tec_register import (
    normalise,
    normalise_stage,
    parse_date,
    parse_decimal,
    swap_day_month,
)

REGIME_CUTOFF: Final = date(2025, 12, 1)
DAYS_PER_YEAR: Final = Decimal("365.25")
YEAR_BASELINE_DAYS: Final = 365
HOLE_DAYS: Final = 60
#: Partial-export rule (declaration v2): a copy whose row count falls by more
#: than this share against the previous kept copy is *suspect*; it is
#: excluded from the series only if the next copy recovers by more than the
#: same share against it (a shrink that persists is a real shrink, flagged and kept).
PARTIAL_EXPORT_SHARE: Final = Decimal("0.2")
MW_YEARS_QUANTUM: Final = Decimal("0.001")
MW_QUANTUM: Final = Decimal("0.01")
SWAP_MIN_EXPLAINED: Final = 3
SWAP_MIN_SHARE: Final = Decimal("0.5")
#: F1: removals plus new entries over this share of the baseline's units on one link.
F1_CHURN_SHARE: Final = Decimal("0.2")
#: F2: matched units under this share of the baseline's units on a trailing-year comparison.
F2_THIN_SHARE: Final = Decimal("0.5")
P2_START: Final = date(2026, 5, 19)
P2_FALSIFIER_DATE: Final = date(2027, 6, 30)
ZERO: Final = Decimal(0)


@dataclass(frozen=True)
class Entry:
    key: str
    identity: str
    stage: str
    mw: Decimal | None
    effective: date | None
    raw_effective: str


def identity(row: dict[str, object]) -> str:
    return "name:" + "|".join(
        (
            normalise(row.get("Project Name")),
            normalise(row.get("Customer Name")),
            normalise(row.get("Connection Site")),
        )
    )


def stage_mw(row: dict[str, object]) -> Decimal | None:
    """The stage's TEC MW as published (`MW Increase / Decrease`), signed."""
    return parse_decimal(row.get("MW Increase / Decrease"))


def entries(rows: list[dict[str, object]], *, swapped: bool = False) -> dict[str, Entry]:
    """One entry per (identity, stage) key for a vintage's rows.

    Where an identity has one row, or every row carries a distinct stage,
    the key is identity plus stage (blank stage reads as `1`). Otherwise
    the identity's rows are ordered by effective date then cumulative MW
    and numbered, as 005 Amendment 1 does.
    """
    groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[identity(row)].append(index)
    out: dict[str, Entry] = {}
    for ident, indices in groups.items():
        stages = [normalise_stage(rows[i].get("Stage")) for i in indices]
        if len(indices) == 1 or (all(stages) and len(set(stages)) == len(stages)):
            keyed = [(i, s or "1") for i, s in zip(indices, stages, strict=True)]
        else:
            ordered = sorted(
                indices,
                key=lambda i: (
                    parse_date(rows[i].get("MW Effective From")) or date.max,
                    parse_decimal(rows[i].get("Cumulative Total Capacity (MW)")) or ZERO,
                ),
            )
            keyed = [(i, str(n)) for n, i in enumerate(ordered, start=1)]
        for i, stage in keyed:
            row = rows[i]
            effective = parse_date(row.get("MW Effective From"))
            if swapped:
                effective = swap_day_month(effective) or effective
            key = f"{ident}#{stage}"
            out[key] = Entry(
                key=key,
                identity=ident,
                stage=stage,
                mw=stage_mw(row),
                effective=effective,
                raw_effective=str(row.get("MW Effective From") or "").strip(),
            )
    return out


# --------------------------------------------------------------- swap test


@dataclass(frozen=True)
class SwapTest:
    disagreements: int
    swap_explained: int
    flagged: bool


def swap_test(previous: dict[str, Entry], current: dict[str, Entry]) -> SwapTest:
    """Is this vintage's effective-date column day-month swapped?

    Over units present in both vintages with a date on both sides, count
    those whose dates differ, and those among them whose current date
    equals the previous date once day and month are exchanged. The vintage
    is flagged when at least SWAP_MIN_EXPLAINED disagreements are explained
    that way and they are at least SWAP_MIN_SHARE of all disagreements.
    """
    disagreements = explained = 0
    for key, cur in current.items():
        prev = previous.get(key)
        if prev is None or prev.effective is None or cur.effective is None:
            continue
        if cur.effective == prev.effective:
            continue
        disagreements += 1
        if swap_day_month(cur.effective) == prev.effective:
            explained += 1
    flagged = explained >= SWAP_MIN_EXPLAINED and Decimal(explained) >= SWAP_MIN_SHARE * Decimal(
        disagreements
    )
    return SwapTest(disagreements, explained, flagged)


# ----------------------------------------------------------------- pairwise


@dataclass(frozen=True)
class Pairwise:
    baseline: date
    current: date
    baseline_units: int
    current_units: int
    matched: int
    new_entries: int
    new_mw: Decimal
    removed: int
    removed_mw: Decimal
    dated_both: int
    undated: int
    unweighted: int
    unchanged: int
    later: int
    earlier: int
    weighted_mw: Decimal
    mw_years_net: Decimal
    mw_years_later: Decimal
    mw_years_earlier: Decimal
    capacity_changed: int
    capacity_delta_mw: Decimal
    f1_churn: bool
    f2_thin: bool


def _q(value: Decimal, quantum: Decimal) -> Decimal:
    return value.quantize(quantum)


def _abs_mw(entries_by_key: dict[str, Entry], keys: set[str]) -> Decimal:
    total = ZERO
    for key in keys:
        mw = entries_by_key[key].mw
        if mw is not None:
            total += abs(mw)
    return total


def years_between(earlier: date, later: date) -> Decimal:
    return Decimal((later - earlier).days) / DAYS_PER_YEAR


def compare(
    baseline: dict[str, Entry],
    current: dict[str, Entry],
    *,
    baseline_date: date,
    current_date: date,
) -> Pairwise:
    """The headline and its reconciliation items for one (baseline, current) pair.

    The two gross sides (later, earlier) are each quantised to 0.001
    MW-years and the net is their sum, so net always equals later plus
    earlier as printed.
    """
    matched_keys = baseline.keys() & current.keys()
    new_keys = current.keys() - baseline.keys()
    removed_keys = baseline.keys() - current.keys()
    dated_both = undated = unweighted = unchanged = later = earlier = 0
    weighted_mw = pos = neg = ZERO
    capacity_changed = 0
    capacity_delta = ZERO
    for key in matched_keys:
        b, c = baseline[key], current[key]
        if b.mw is not None and c.mw is not None and b.mw != c.mw:
            capacity_changed += 1
            capacity_delta += c.mw - b.mw
        if b.effective is None or c.effective is None:
            undated += 1
            continue
        dated_both += 1
        weight = abs(b.mw) if b.mw is not None else ZERO
        if weight == ZERO:
            unweighted += 1
        movement = years_between(b.effective, c.effective)
        if movement > ZERO:
            later += 1
        elif movement < ZERO:
            earlier += 1
        else:
            unchanged += 1
        weighted_mw += weight
        contribution = weight * movement
        if contribution > ZERO:
            pos += contribution
        else:
            neg += contribution
    return Pairwise(
        baseline=baseline_date,
        current=current_date,
        baseline_units=len(baseline),
        current_units=len(current),
        matched=len(matched_keys),
        new_entries=len(new_keys),
        new_mw=_q(_abs_mw(current, new_keys), MW_QUANTUM),
        removed=len(removed_keys),
        removed_mw=_q(_abs_mw(baseline, removed_keys), MW_QUANTUM),
        dated_both=dated_both,
        undated=undated,
        unweighted=unweighted,
        unchanged=unchanged,
        later=later,
        earlier=earlier,
        weighted_mw=_q(weighted_mw, MW_QUANTUM),
        mw_years_net=_q(pos, MW_YEARS_QUANTUM) + _q(neg, MW_YEARS_QUANTUM),
        mw_years_later=_q(pos, MW_YEARS_QUANTUM),
        mw_years_earlier=_q(neg, MW_YEARS_QUANTUM),
        capacity_changed=capacity_changed,
        capacity_delta_mw=_q(capacity_delta, MW_QUANTUM),
        f1_churn=Decimal(len(new_keys) + len(removed_keys))
        > F1_CHURN_SHARE * Decimal(len(baseline)),
        f2_thin=Decimal(len(matched_keys)) < F2_THIN_SHARE * Decimal(len(baseline)),
    )


# ------------------------------------------------------------------- series


@dataclass(frozen=True)
class VintageInput:
    t_public: date
    rows: tuple[dict[str, object], ...]
    sha256: str
    path: str


def year_earlier_baseline(dates: list[date], current: date) -> date | None:
    """The latest date in `dates` at least YEAR_BASELINE_DAYS before `current`."""
    cutoff = current - timedelta(days=YEAR_BASELINE_DAYS)
    earlier = [d for d in dates if d <= cutoff]
    return max(earlier) if earlier else None


@dataclass(frozen=True)
class SuspectCopy:
    t_public: date
    rows: int
    previous_rows: int
    next_rows: int | None
    excluded: bool

    @property
    def note(self) -> str:
        fell = (Decimal(self.previous_rows - self.rows) / Decimal(self.previous_rows)) * 100
        return (
            f"{self.rows} rows against {self.previous_rows} in the previous copy "
            f"({fell:.0f}% fewer)"
        )


def partial_exports(counts: list[tuple[date, int]]) -> list[SuspectCopy]:
    """The partial-export rule over (t_public, row count) pairs in date order.

    A copy is suspect when its count falls by more than PARTIAL_EXPORT_SHARE
    against the previous *kept* copy. It is excluded when the following copy
    recovers by more than PARTIAL_EXPORT_SHARE against it; otherwise it is
    flagged and kept, and becomes the baseline for the next comparison.
    """
    out: list[SuspectCopy] = []
    previous: int | None = None
    for index, (t, n) in enumerate(counts):
        if previous is None or previous == 0:
            previous = n
            continue
        fell = Decimal(previous - n) / Decimal(previous) > PARTIAL_EXPORT_SHARE
        if not fell:
            previous = n
            continue
        following = counts[index + 1][1] if index + 1 < len(counts) else None
        recovers = (
            following is not None
            and n > 0
            and (Decimal(following - n) / Decimal(n) > PARTIAL_EXPORT_SHARE)
        )
        out.append(SuspectCopy(t, n, previous, following, excluded=bool(recovers)))
        if not recovers:
            previous = n
    return out


def split_segments(vintages: list[VintageInput]) -> list[tuple[str, list[VintageInput]]]:
    ordered = sorted(vintages, key=lambda v: v.t_public)
    old = [v for v in ordered if v.t_public < REGIME_CUTOFF]
    new = [v for v in ordered if v.t_public >= REGIME_CUTOFF]
    return [(label, seg) for label, seg in (("old", old), ("new", new)) if seg]


def holes(dates: list[date]) -> list[dict[str, Any]]:
    out = []
    for a, b in zip(dates, dates[1:], strict=False):
        if (b - a).days > HOLE_DAYS:
            out.append({"from": a, "to": b, "days": (b - a).days})
    return out


def annual_windows(entries_by_date: dict[date, dict[str, Entry]]) -> list[dict[str, Any]]:
    """Calendar-year windows: the first vintage on or after 1 January of a
    year to the first vintage on or after 1 January of the next; the last
    year closes on the segment's last vintage and is marked partial."""
    dates = sorted(entries_by_date)
    if not dates:
        return []
    out = []
    for year in range(dates[0].year, dates[-1].year + 1):
        start = next((d for d in dates if d >= date(year, 1, 1)), None)
        if start is None or start.year != year:
            continue
        end = next((d for d in dates if d >= date(year + 1, 1, 1)), None)
        partial = end is None
        end = end if end is not None else dates[-1]
        if end <= start:
            continue
        pair = compare(
            entries_by_date[start], entries_by_date[end], baseline_date=start, current_date=end
        )
        out.append({"year": year, "partial": partial, **pair.__dict__})
    return out


def propositions(segments_out: list[dict[str, Any]]) -> dict[str, Any]:
    """P1 and P2 as declared: decided by their instances, never rounded."""
    old = next((s for s in segments_out if s["regime"] == "old"), None)
    complete = [a for a in (old["annual"] if old else []) if not a["partial"]]
    failing = [a["year"] for a in complete if a["mw_years_net"] <= ZERO]
    p1 = {
        "statement": (
            "every complete calendar-year window of the old regime has positive net movement"
        ),
        "windows": [a["year"] for a in complete],
        "failing_years": failing,
        "verdict": ("undecided" if not complete else ("fails" if failing else "holds")),
    }
    new = next((s for s in segments_out if s["regime"] == "new"), None)
    p2: dict[str, Any] = {
        "statement": (
            "chained net movement of the reformed regime from its first copy to the first copy "
            "at least 365 days later is positive"
        ),
        "start": P2_START,
        "falsifier_date": P2_FALSIFIER_DATE,
        "verdict": "undecided",
        "decided_on": None,
        "chained_mw_years_net": None,
    }
    if new and new["rows"] and new["rows"][0]["t_public"] == P2_START:
        deciding = [r for r in new["rows"] if (r["t_public"] - P2_START).days >= YEAR_BASELINE_DAYS]
        if deciding:
            first = deciding[0]
            p2["decided_on"] = first["t_public"]
            p2["chained_mw_years_net"] = first["cumulative_mw_years_net"]
            p2["verdict"] = "holds" if first["cumulative_mw_years_net"] > ZERO else "fails"
    return {"P1": p1, "P2": p2}


def series(vintages: list[VintageInput], *, partial_export_rule: bool = False) -> dict[str, Any]:
    """Every row of the series, segment by segment, from parsed vintages.

    With `partial_export_rule` (declaration v2) suspect copies are found
    per segment before any comparison; excluded ones take no part in the
    links and are listed, flagged ones stay and are listed.
    """
    segments_out: list[dict[str, Any]] = []
    suspects: list[dict[str, Any]] = []
    for label, segment in split_segments(vintages):
        if partial_export_rule:
            found = partial_exports([(v.t_public, len(v.rows)) for v in segment])
            excluded = {s.t_public for s in found if s.excluded}
            suspects += [{"regime": label, **s.__dict__, "note": s.note} for s in found]
            segment = [v for v in segment if v.t_public not in excluded]
        entries_by_date: dict[date, dict[str, Entry]] = {}
        rows: list[dict[str, Any]] = []
        previous: dict[str, Entry] | None = None
        previous_date: date | None = None
        cumulative = ZERO
        for vintage in segment:
            current = entries(list(vintage.rows))
            test = SwapTest(0, 0, False)
            if previous is not None:
                test = swap_test(previous, current)
                if test.flagged:
                    current = entries(list(vintage.rows), swapped=True)
            entries_by_date[vintage.t_public] = current
            row: dict[str, Any] = {
                "t_public": vintage.t_public,
                "sha256": vintage.sha256,
                "path": vintage.path,
                "rows": len(vintage.rows),
                "units": len(current),
                "dated": sum(1 for e in current.values() if e.effective is not None),
                "weighted": sum(1 for e in current.values() if e.mw not in (None, ZERO)),
                "swap_test": test.__dict__,
                "vs_previous": None,
                "year_earlier_baseline": None,
                "vs_year_earlier": None,
            }
            if previous is not None and previous_date is not None:
                pair = compare(
                    previous, current, baseline_date=previous_date, current_date=vintage.t_public
                )
                cumulative += pair.mw_years_net
                row["vs_previous"] = pair.__dict__
            row["cumulative_mw_years_net"] = cumulative
            baseline_date = year_earlier_baseline(list(entries_by_date), vintage.t_public)
            if baseline_date is not None:
                row["year_earlier_baseline"] = baseline_date
                row["vs_year_earlier"] = compare(
                    entries_by_date[baseline_date],
                    current,
                    baseline_date=baseline_date,
                    current_date=vintage.t_public,
                ).__dict__
            rows.append(row)
            previous, previous_date = current, vintage.t_public
        segments_out.append(
            {
                "regime": label,
                "first": segment[0].t_public,
                "last": segment[-1].t_public,
                "vintages": len(segment),
                "swapped_vintages": [r["t_public"] for r in rows if r["swap_test"]["flagged"]],
                "holes": holes([v.t_public for v in segment]),
                "annual": annual_windows(entries_by_date),
                "rows": rows,
            }
        )
    out: dict[str, Any] = {
        "segments": segments_out,
        "regime_break": None,
        "headline": None,
        "suspect_copies": suspects,
        "propositions": propositions(segments_out),
        "f1_links": [
            r["t_public"]
            for s in segments_out
            for r in s["rows"]
            if r["vs_previous"] and r["vs_previous"]["f1_churn"]
        ],
        "f2_rows": [
            r["t_public"]
            for s in segments_out
            for r in s["rows"]
            if r["vs_year_earlier"] and r["vs_year_earlier"]["f2_thin"]
        ],
    }
    labels = [s["regime"] for s in segments_out]
    if "old" in labels and "new" in labels:
        old = next(s for s in segments_out if s["regime"] == "old")
        new = next(s for s in segments_out if s["regime"] == "new")
        out["regime_break"] = {
            "last_old": old["last"],
            "first_new": new["first"],
            "days": (new["first"] - old["last"]).days,
        }
    old_rows: list[dict[str, Any]] = next(
        (s["rows"] for s in segments_out if s["regime"] == "old"), []
    )
    with_headline = [r for r in old_rows if r["vs_year_earlier"] is not None]
    if with_headline:
        last = with_headline[-1]
        out["headline"] = {
            "t_public": last["t_public"],
            "baseline": last["year_earlier_baseline"],
            "mw_years_net": last["vs_year_earlier"]["mw_years_net"],
            "mw_years_later": last["vs_year_earlier"]["mw_years_later"],
            "mw_years_earlier": last["vs_year_earlier"]["mw_years_earlier"],
            "matched": last["vs_year_earlier"]["matched"],
            "dated_both": last["vs_year_earlier"]["dated_both"],
            "cumulative_mw_years_net": last["cumulative_mw_years_net"],
        }
    return out
