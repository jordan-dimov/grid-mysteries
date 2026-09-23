"""The analysis layer: claims about the TEC record, each naming its rule.

Pure; the record arrives as `replay.Publication`s (read back out of the
governed record, never from the source files). Three rules:

- `014-v2`: investigation 014's declaration v2, computed by 014's own
  pure module (`investigations.connection_slippage`). Over the
  publications 014 saw, its rows must equal 014's committed rows byte for
  byte (`differential`); that is the test that the record lost nothing
  014 reads.
- `tec-identity-content-v1`: 014 v2's reading rules (dates, the day-month
  swap test, the partial-export rule) and headline arithmetic, with units
  matched by content (`tec.identity`) instead of 014's ordinal rule.
- `spike-positional`: the spike's key (identity, register stage, and a
  counter in file order), kept only to explain the spike's flapping.

`flapping` counts, for any rule, the date moves reversed by the unit's
next move, and whether the published files show the reversal.
"""

import json
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.evidence import dumps
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.sources.tec_register import normalise_stage, parse_date
from grid_mysteries.tec import identity as content
from grid_mysteries.tec.replay import Publication

RULE_014: Final = "014-v2"
RULE_CONTENT: Final = content.RULE
RULE_SPIKE: Final = "spike-positional"
#: 014 reading rule 2: a copy lacking any of these is excluded and listed.
REQUIRED_COLUMNS: Final = (
    "Project Name",
    "Customer Name",
    "Connection Site",
    "MW Increase / Decrease",
    "MW Effective From",
)

Entries = dict[str, cs.Entry]


# ------------------------------------------------------------------ 014-v2


def inputs(
    publications: Iterable[Publication], paths: dict[str, str]
) -> tuple[list[cs.VintageInput], list[dict[str, Any]]]:
    """014's usable copies from the record: (usable, excluded)."""
    usable, excluded = [], []
    for p in publications:
        carried = set(p.columns.split(",")) if p.columns else set()
        missing = [c for c in REQUIRED_COLUMNS if c not in carried]
        if missing:
            excluded.append({"t_public": p.published_on, "vintage": p.vintage, "missing": missing})
            continue
        usable.append(
            cs.VintageInput(
                t_public=p.published_on,
                rows=p.rows,
                sha256=p.sha256,
                path=paths.get(p.sha256, ""),
            )
        )
    return usable, excluded


def series_014(usable: list[cs.VintageInput]) -> dict[str, Any]:
    return cs.series(usable, partial_export_rule=True)


def row_lines(result: dict[str, Any]) -> list[str]:
    """014 v2's rows.ndjson lines, serialised exactly as its runner does."""
    return [
        json.dumps(json.loads(dumps({"regime": s["regime"], **row})), separators=(",", ":"))
        for s in result["segments"]
        for row in s["rows"]
    ]


def differential(engine_lines: list[str], committed_lines: list[str]) -> dict[str, Any]:
    """Line by line, keyed by (t_public, sha256): identical, differing, missing, extra."""

    def keyed(lines: list[str]) -> dict[tuple[str, str], str]:
        out = {}
        for line in lines:
            row = json.loads(line)
            out[(row["t_public"], row["sha256"])] = line
        return out

    engine, committed = keyed(engine_lines), keyed(committed_lines)
    differing = []
    for key in sorted(engine.keys() & committed.keys()):
        if engine[key] != committed[key]:
            a, b = json.loads(engine[key]), json.loads(committed[key])
            fields = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
            differing.append({"t_public": key[0], "sha256": key[1], "fields": fields})
    return {
        "compared": len(engine.keys() & committed.keys()),
        "identical": len(engine.keys() & committed.keys()) - len(differing),
        "differing": differing,
        "missing_from_engine": sorted(k[0] for k in committed.keys() - engine.keys()),
        "extra_in_engine": sorted(k[0] for k in engine.keys() - committed.keys()),
    }


# ------------------------------------------------------ kept publications


@dataclass(frozen=True)
class Kept:
    regime: str
    vintage: cs.VintageInput
    swapped: bool


def kept(usable: list[cs.VintageInput], result_014: dict[str, Any]) -> list[Kept]:
    """014 v2's kept copies per segment (partial-export exclusions removed)
    with its swap-test verdict on each: the reading every rule here shares."""
    flags = {
        (s["regime"], r["t_public"]): bool(r["swap_test"]["flagged"])
        for s in result_014["segments"]
        for r in s["rows"]
    }
    out = []
    for regime, segment in cs.split_segments(usable):
        for v in segment:
            if (regime, v.t_public) in flags:
                out.append(Kept(regime, v, flags[(regime, v.t_public)]))
    return out


def entries_014(sequence: list[Kept]) -> list[tuple[Kept, Entries]]:
    return [(k, cs.entries(list(k.vintage.rows), swapped=k.swapped)) for k in sequence]


def entries_content(sequence: list[Kept]) -> list[tuple[Kept, Entries]]:
    out = []
    state: dict[str, content.ContentIdentity] = {}
    for k in sequence:
        carrier = state.setdefault(k.regime, content.ContentIdentity())
        out.append((k, carrier.step(list(k.vintage.rows), swapped=k.swapped)))
    return out


def entries_spike(publications: list[Publication]) -> list[tuple[date, Entries]]:
    """The spike's keys: identity, `|stage:` and the register stage, with a
    `#n` counter in file order for repeats; dates as parsed, never swapped."""
    out = []
    for p in publications:
        keyed: Entries = {}
        for row in p.rows:
            base = f"{cs.identity(row)}|stage:{normalise_stage(row.get('Stage'))}"
            key, n = base, 1
            while key in keyed:
                n += 1
                key = f"{base}#{n}"
            keyed[key] = cs.Entry(
                key=key,
                identity=cs.identity(row),
                stage=normalise_stage(row.get("Stage")),
                mw=cs.stage_mw(row),
                effective=parse_date(row.get("MW Effective From")),
                raw_effective=str(row.get("MW Effective From") or "").strip(),
            )
        out.append((p.published_on, keyed))
    return out


# ------------------------------------------------------------ the series


def series_by(sequence: list[tuple[Kept, Entries]]) -> dict[str, Any]:
    """014 v2's series arithmetic over entries built by any identity rule."""
    segments_out: list[dict[str, Any]] = []
    by_regime: dict[str, list[tuple[Kept, Entries]]] = defaultdict(list)
    for k, e in sequence:
        by_regime[k.regime].append((k, e))
    for regime, items in by_regime.items():
        entries_by_date: dict[date, Entries] = {}
        rows: list[dict[str, Any]] = []
        previous: Entries | None = None
        previous_date: date | None = None
        cumulative = Decimal(0)
        for k, current in items:
            t = k.vintage.t_public
            entries_by_date[t] = current
            row: dict[str, Any] = {"t_public": t, "units": len(current), "vs_previous": None}
            if previous is not None and previous_date is not None:
                pair = cs.compare(previous, current, baseline_date=previous_date, current_date=t)
                cumulative += pair.mw_years_net
                row["vs_previous"] = pair.__dict__
            row["cumulative_mw_years_net"] = cumulative
            baseline = cs.year_earlier_baseline(list(entries_by_date), t)
            row["year_earlier_baseline"] = baseline
            row["vs_year_earlier"] = (
                cs.compare(
                    entries_by_date[baseline], current, baseline_date=baseline, current_date=t
                ).__dict__
                if baseline is not None
                else None
            )
            rows.append(row)
            previous, previous_date = current, t
        segments_out.append(
            {"regime": regime, "annual": cs.annual_windows(entries_by_date), "rows": rows}
        )
    old = next((s for s in segments_out if s["regime"] == "old"), None)
    headline = None
    if old:
        with_headline = [r for r in old["rows"] if r["vs_year_earlier"] is not None]
        if with_headline:
            last = with_headline[-1]
            headline = {
                "t_public": last["t_public"],
                "baseline": last["year_earlier_baseline"],
                "mw_years_net": last["vs_year_earlier"]["mw_years_net"],
                "matched": last["vs_year_earlier"]["matched"],
                "cumulative_mw_years_net": last["cumulative_mw_years_net"],
            }
    return {
        "segments": segments_out,
        "headline": headline,
        "propositions": cs.propositions(segments_out),
    }


# -------------------------------------------------------------- flapping

Sequence = list[tuple[date, Entries]]


@dataclass(frozen=True)
class Move:
    unit: str
    group: str
    at: date
    previous_at: date
    from_date: date
    to_date: date
    from_mw: Decimal | None
    to_mw: Decimal | None
    repeated: bool


def moves(sequence: Sequence) -> list[Move]:
    """Every date move between consecutive publications of one sequence. A
    move is on a *repeated key* when its group printed more than one row in
    either publication."""
    out = []
    for (t0, before), (t1, after) in zip(sequence, sequence[1:], strict=False):
        sizes0 = Counter(e.identity for e in before.values())
        sizes1 = Counter(e.identity for e in after.values())
        for key, cur in after.items():
            prev = before.get(key)
            if prev is None or prev.effective is None or cur.effective is None:
                continue
            if prev.effective != cur.effective:
                out.append(
                    Move(
                        key,
                        cur.identity,
                        t1,
                        t0,
                        prev.effective,
                        cur.effective,
                        prev.mw,
                        cur.mw,
                        sizes0[cur.identity] > 1 or sizes1[cur.identity] > 1,
                    )
                )
    return out


PrintedRows = dict[date, dict[str, Counter[tuple[Decimal | None, date]]]]


def printed(sequence: Sequence) -> PrintedRows:
    """Per publication, per group, the (MW, date) pairs it printed, as read.
    This is a fact about the files, not about identity."""
    out: PrintedRows = {}
    for t, entries in sequence:
        groups: dict[str, Counter[tuple[Decimal | None, date]]] = defaultdict(Counter)
        for e in entries.values():
            if e.effective is not None:
                groups[e.identity][(e.mw, e.effective)] += 1
        out[t] = groups
    return out


def file_shows(rows: PrintedRows, move: Move) -> bool:
    """Do the group's printed rows themselves move this way: one fewer row of
    the old MW at the old date, and one more of the new MW at the new date?"""
    before = rows[move.previous_at].get(move.group, Counter())
    after = rows[move.at].get(move.group, Counter())
    old, new = (move.from_mw, move.from_date), (move.to_mw, move.to_date)
    return after[old] < before[old] and after[new] > before[new]


def flapping(segments: list[Sequence], rule: str) -> dict[str, Any]:
    """Moves reversed by the same unit's next move, split by whether both
    publications' files show the reversal (the group's printed MW and dates
    moved that way) or only the identity rule does. Each segment is a
    sequence of its own; nothing pairs across a regime break."""
    all_moves: list[Move] = []
    rows: PrintedRows = {}
    for sequence in segments:
        all_moves += moves(sequence)
        rows.update(printed(sequence))
    by_unit: dict[tuple[str, str], list[Move]] = defaultdict(list)
    for index, sequence in enumerate(segments):
        for m in moves(sequence):
            by_unit[(str(index), m.unit)].append(m)
    reversed_, file_backed, manufactured = [], [], []
    for unit_moves in by_unit.values():
        for first, second in zip(unit_moves, unit_moves[1:], strict=False):
            if second.to_date != first.from_date or second.from_date != first.to_date:
                continue
            reversed_.append((first, second))
            if file_shows(rows, first) and file_shows(rows, second):
                file_backed.append((first, second))
            else:
                manufactured.append((first, second))

    def example(pair: tuple[Move, Move]) -> dict[str, Any]:
        a, b = pair
        return {
            "unit": a.unit,
            "moves": [
                [a.previous_at, a.at, a.from_date, a.to_date, a.from_mw, a.to_mw],
                [b.previous_at, b.at, b.from_date, b.to_date, b.from_mw, b.to_mw],
            ],
        }

    return {
        "rule": rule,
        "segments": len(segments),
        "publications": sum(len(s) for s in segments),
        "moves": len(all_moves),
        "moves_on_repeated_keys": sum(1 for m in all_moves if m.repeated),
        "reversed_by_next": len(reversed_),
        "reversed_on_repeated_keys": sum(1 for a, _ in reversed_ if a.repeated),
        "reversed_file_backed": len(file_backed),
        "reversed_not_in_files": len(manufactured),
        "reversed_not_in_files_on_repeated_keys": sum(1 for a, _ in manufactured if a.repeated),
        "examples_not_in_files": [example(p) for p in manufactured[:10]],
        "examples_file_backed": [example(p) for p in file_backed[:3]],
    }


def by_segment(sequence: list[tuple[Kept, Entries]]) -> list[Sequence]:
    out: dict[str, Sequence] = {}
    for k, e in sequence:
        out.setdefault(k.regime, []).append((k.vintage.t_public, e))
    return list(out.values())


def contributions(entries: Entries, baseline: Entries) -> dict[str, Decimal]:
    """Per group, the headline's MW-years between a baseline and a current
    publication (014's arithmetic: |MW at baseline| x years moved)."""
    out: dict[str, Decimal] = defaultdict(Decimal)
    for key in baseline.keys() & entries.keys():
        b, c = baseline[key], entries[key]
        if b.effective is None or c.effective is None:
            continue
        weight = abs(b.mw) if b.mw is not None else Decimal(0)
        out[b.identity] += weight * cs.years_between(b.effective, c.effective)
    return out


def restructured(baseline: list[dict[str, object]], current: list[dict[str, object]]) -> set[str]:
    """Groups whose printed stage labels (as a multiset, so row count
    included) differ between the two publications: a split, a merge or a
    renumbering. 014 never repairs these, so any pairing inside them is the
    identity rule's choice, not a published move."""

    def stages(rows: list[dict[str, object]]) -> dict[str, Counter[str]]:
        out: dict[str, Counter[str]] = defaultdict(Counter)
        for row in rows:
            out[cs.identity(row)][normalise_stage(row.get("Stage"))] += 1
        return out

    a, b = stages(baseline), stages(current)
    return {g for g in a.keys() & b.keys() if a[g] != b[g]}


def headline_difference(
    a: list[tuple[Kept, Entries]], b: list[tuple[Kept, Entries]], baseline: date, current: date
) -> dict[str, Any]:
    """Where two identity rules' headlines differ, group by group, and the
    headline each gives once restructured groups are set aside."""
    ea = {k.vintage.t_public: e for k, e in a}
    eb = {k.vintage.t_public: e for k, e in b}
    ca = contributions(ea[current], ea[baseline])
    cb = contributions(eb[current], eb[baseline])
    moved = restructured(_rows(a, baseline), _rows(a, current))
    groups: list[dict[str, Any]] = []
    for g in sorted(ca.keys() | cb.keys()):
        x, y = ca.get(g, Decimal(0)), cb.get(g, Decimal(0))
        if x.quantize(cs.MW_YEARS_QUANTUM) != y.quantize(cs.MW_YEARS_QUANTUM):
            groups.append(
                {
                    "group": g,
                    "a": x.quantize(cs.MW_YEARS_QUANTUM),
                    "b": y.quantize(cs.MW_YEARS_QUANTUM),
                    "restructured": g in moved,
                }
            )
    groups.sort(key=lambda r: -abs(Decimal(r["b"]) - Decimal(r["a"])))
    kept_a = sum((v for g, v in ca.items() if g not in moved), Decimal(0))
    kept_b = sum((v for g, v in cb.items() if g not in moved), Decimal(0))
    return {
        "baseline": baseline,
        "current": current,
        "a_total": sum(ca.values(), Decimal(0)).quantize(cs.MW_YEARS_QUANTUM),
        "b_total": sum(cb.values(), Decimal(0)).quantize(cs.MW_YEARS_QUANTUM),
        "groups_differing": len(groups),
        "groups_differing_restructured": sum(1 for r in groups if r["restructured"]),
        "restructured_groups": len(moved),
        "a_without_restructured": kept_a.quantize(cs.MW_YEARS_QUANTUM),
        "b_without_restructured": kept_b.quantize(cs.MW_YEARS_QUANTUM),
        "groups": groups,
    }


def _rows(sequence: list[tuple[Kept, Entries]], t: date) -> list[dict[str, object]]:
    return next(list(k.vintage.rows) for k, _ in sequence if k.vintage.t_public == t)


def compare_series(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Headline and calendar-year windows of two series side by side."""

    def windows(result: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
        return {(s["regime"], w["year"]): w for s in result["segments"] for w in s["annual"]}

    wa, wb = windows(a), windows(b)
    rows = []
    for key in sorted(wa.keys() | wb.keys()):
        x, y = wa.get(key), wb.get(key)
        rows.append(
            {
                "regime": key[0],
                "year": key[1],
                "partial": (x or y or {}).get("partial"),
                "a_mw_years_net": x and x["mw_years_net"],
                "b_mw_years_net": y and y["mw_years_net"],
                "a_matched": x and x["matched"],
                "b_matched": y and y["matched"],
            }
        )
    return {"headline_a": a["headline"], "headline_b": b["headline"], "annual": rows}


Loader = Callable[[], list[Publication]]
