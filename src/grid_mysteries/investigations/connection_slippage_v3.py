"""Investigation 014, declarations 3 and 4: every movement figure split into
the part the register's own stage labels determine and the figure under
each of two named identity rules.

The two declarations differ only in the definition of a determined pairing:
version 3 (`definition="ends"`) judges it at the two copies compared, and
refused on its own F4 (AMENDMENTS.md, 2026-09-23); version 4
(`definition="path"`) judges it over every copy the comparison spans, B to
C inclusive, where a copy that does not print the group counts as a change.

Pure; no I/O beyond hashing the content rule's file for F5. Version 2's
series (`connection_slippage.series`) is computed unchanged and every one of
its fields is kept; a `split` object is added beside each figure:

- `determined`: movement over units of groups whose pairing the register
  determines (`tec.analysis.undetermined` names the others), quantised as
  version 2 quantises a net (each gross side to 0.001, then summed);
- `undetermined`: for each rule, that rule's net minus the determined part;
- `total`: each rule's net (version 2's is the figure version 2 publishes);
- `undetermined_groups`: how many groups the register leaves undetermined.

The two rules are named, not bounds: other pairings are possible.

F4: the two rules must give identical movement for every determined group,
or the computation refuses. F5: the content rule's file must hash to the
digest the frozen declaration states, or the computation refuses.
"""

import hashlib
import re
from bisect import bisect_right
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.sources.tec_register import normalise_stage
from grid_mysteries.tec import analysis
from grid_mysteries.tec import identity as content_rule

RULE_V2: Final = "014-v2"
RULE_CONTENT: Final = content_rule.RULE
RULES: Final = (RULE_V2, RULE_CONTENT)
CONTENT_RULE_FILE: Final = Path(content_rule.__file__)
SHARE_QUANTUM: Final = Decimal("0.1")
ZERO: Final = Decimal(0)

Entries = dict[str, cs.Entry]


class RuleDisagreement(RuntimeError):
    """F4: the two rules differ on a group whose pairing is determined."""


class ContentRuleChanged(RuntimeError):
    """F5: the content rule's file no longer hashes to the declared digest."""


# ------------------------------------------------------------------- F5


def declared_rule_digest(declaration: str) -> str:
    """The content rule's SHA-256 as the frozen declaration states it."""
    found = re.search(r"identity\.py`, SHA-256\s+`([0-9a-f]{64})`", declaration)
    if not found:
        raise ContentRuleChanged("the declaration states no digest for the content rule")
    return found[1]


def check_rule_file(path: Path, digest: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise ContentRuleChanged(
            f"F5: {path.name} hashes to {actual[:16]}…, the declaration states {digest[:16]}…; "
            "a changed rule is a new declaration"
        )


# ------------------------------------------------------------ the split


def _net(values: list[Decimal]) -> Decimal:
    """Version 2's quantisation: each gross side to 0.001, then summed."""
    pos = sum((v for v in values if v > ZERO), ZERO)
    neg = sum((v for v in values if v <= ZERO), ZERO)
    return pos.quantize(cs.MW_YEARS_QUANTUM) + neg.quantize(cs.MW_YEARS_QUANTUM)


def _unit_movements(baseline: Entries, current: Entries) -> list[tuple[str, Decimal]]:
    """(group, |MW at baseline| x years moved) for every unit dated on both sides."""
    out = []
    for key in baseline.keys() & current.keys():
        b, c = baseline[key], current[key]
        if b.effective is None or c.effective is None:
            continue
        weight = abs(b.mw) if b.mw is not None else ZERO
        out.append((b.identity, weight * cs.years_between(b.effective, c.effective)))
    return out


Labels = tuple[tuple[str, int], ...]


def labels(rows: list[dict[str, object]]) -> dict[str, Labels]:
    """Each group's printed stage labels in one copy, as a multiset."""
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[cs.identity(row)][normalise_stage(row.get("Stage"))] += 1
    return {g: tuple(sorted(c.items())) for g, c in out.items()}


class Determinacy:
    """Version 4's definition over one segment's copies, in order: for each
    group, the copies at which its labels differ from the copy before (a
    missing group included) and the copies at which a label repeats."""

    def __init__(self, copies: list[list[dict[str, object]]]) -> None:
        self.labels = [labels(rows) for rows in copies]
        self.changes: dict[str, list[int]] = defaultdict(list)
        self.repeats: dict[str, list[int]] = defaultdict(list)
        for k, now in enumerate(self.labels):
            for g, lab in now.items():
                if any(n > 1 for _, n in lab):
                    self.repeats[g].append(k)
            if k == 0:
                continue
            before = self.labels[k - 1]
            for g in before.keys() | now.keys():
                if before.get(g) != now.get(g):
                    self.changes[g].append(k)

    @staticmethod
    def _any_in(indexes: list[int], low: int, high: int) -> bool:
        """Is any index in (low - 1, high], i.e. low <= index <= high?"""
        at = bisect_right(indexes, low - 1)
        return at < len(indexes) and indexes[at] <= high

    def undetermined(self, i: int, j: int) -> set[str]:
        """Groups printed in copies i and j whose pairing is undetermined over
        copies i..j inclusive: a label change after i, or a repeat anywhere."""
        return {
            g
            for g in self.labels[i].keys() & self.labels[j].keys()
            if self._any_in(self.changes.get(g, []), i + 1, j)
            or self._any_in(self.repeats.get(g, []), i, j)
        }


def split(
    v2: tuple[Entries, Entries],
    content: tuple[Entries, Entries],
    undetermined: set[str],
    *,
    baseline: date,
    current: date,
) -> dict[str, Any]:
    """One comparison, split. `v2` and `content` are each rule's (baseline,
    current) entries; `undetermined` names the groups whose pairing the
    declaration's definition leaves undetermined."""
    moves = {RULE_V2: _unit_movements(*v2), RULE_CONTENT: _unit_movements(*content)}
    # Each group's movements summed in sorted order: the same values then
    # give the same Decimal sum whatever order the units arrive in (a sum's
    # last digit depends on the order at 28 significant digits).
    per_group: dict[str, dict[str, Decimal]] = {}
    for rule, pairs in moves.items():
        values: dict[str, list[Decimal]] = defaultdict(list)
        for group, value in pairs:
            if group not in undetermined:
                values[group].append(value)
        per_group[rule] = {g: sum(sorted(v), ZERO) for g, v in values.items()}
    groups = per_group[RULE_V2].keys() | per_group[RULE_CONTENT].keys()
    for group in sorted(groups):
        a = per_group[RULE_V2].get(group, ZERO)
        b = per_group[RULE_CONTENT].get(group, ZERO)
        if a != b:
            raise RuleDisagreement(
                f"F4: {baseline} -> {current}: the rules differ on determined group {group!r} "
                f"({a} under {RULE_V2}, {b} under {RULE_CONTENT}); the definition is wrong"
            )
    determined = _net([v for g, v in moves[RULE_V2] if g not in undetermined])
    total = {
        RULE_V2: cs.compare(*v2, baseline_date=baseline, current_date=current).mw_years_net,
        RULE_CONTENT: cs.compare(
            *content, baseline_date=baseline, current_date=current
        ).mw_years_net,
    }
    return {
        "undetermined_groups": len(undetermined),
        "determined": determined,
        "undetermined": {rule: total[rule] - determined for rule in RULES},
        "total": total,
    }


def share(chained: dict[str, Decimal], determined: Decimal) -> dict[str, Decimal | None]:
    """The undetermined share of a chained total under each rule, in percent."""
    return {
        rule: (
            ((chained[rule] - determined) * 100 / chained[rule]).quantize(SHARE_QUANTUM)
            if chained[rule]
            else None
        )
        for rule in RULES
    }


# ------------------------------------------------------------- the series


def series(
    usable: list[cs.VintageInput],
    *,
    rule_digest: str,
    definition: str = "path",
    rule_file: Path = CONTENT_RULE_FILE,
    content_entries: Any = analysis.entries_content,
) -> dict[str, Any]:
    """Version 2's series with the split beside every figure, under version
    3's definition (`"ends"`) or version 4's (`"path"`).

    `content_entries` is the content rule over the kept copies; a test
    substitutes a rule that re-pairs a determined group to prove F4 refuses.
    """
    check_rule_file(rule_file, rule_digest)
    result = cs.series(usable, partial_export_rule=True)
    kept = analysis.kept(usable, result)
    v2_entries = dict(((k.regime, k.vintage.t_public), e) for k, e in analysis.entries_014(kept))
    content = dict(((k.regime, k.vintage.t_public), e) for k, e in content_entries(kept))
    if definition not in ("ends", "path"):
        raise ValueError(f"unknown definition {definition!r}")
    rows_of = {(k.regime, k.vintage.t_public): list(k.vintage.rows) for k in kept}
    position: dict[tuple[str, date], int] = {}
    determinacy: dict[str, Determinacy] = {}
    for regime in dict.fromkeys(k.regime for k in kept):
        copies = [k for k in kept if k.regime == regime]
        position.update({(regime, k.vintage.t_public): n for n, k in enumerate(copies)})
        determinacy[regime] = Determinacy([list(k.vintage.rows) for k in copies])

    def pair(regime: str, b: date, c: date) -> dict[str, Any]:
        undetermined = (
            analysis.undetermined(rows_of[(regime, b)], rows_of[(regime, c)])
            if definition == "ends"
            else determinacy[regime].undetermined(position[(regime, b)], position[(regime, c)])
        )
        return split(
            (v2_entries[(regime, b)], v2_entries[(regime, c)]),
            (content[(regime, b)], content[(regime, c)]),
            undetermined,
            baseline=b,
            current=c,
        )

    chains: dict[str, dict[str, Any]] = {}
    for segment in result["segments"]:
        regime = segment["regime"]
        determined = ZERO
        chained = {rule: ZERO for rule in RULES}
        for row in segment["rows"]:
            t = row["t_public"]
            increment = None
            if row["vs_previous"] is not None:
                increment = pair(regime, row["vs_previous"]["baseline"], t)
                determined += increment["determined"]
                for rule in RULES:
                    chained[rule] += increment["total"][rule]
            year = (
                pair(regime, row["year_earlier_baseline"], t)
                if row["year_earlier_baseline"] is not None
                else None
            )
            if chained[RULE_V2] != row["cumulative_mw_years_net"]:
                raise RuleDisagreement(f"{t}: version 2's chain does not add up")
            row["split"] = {
                "vs_previous": increment,
                "vs_year_earlier": year,
                "chained": {
                    "determined": determined,
                    "total": dict(chained),
                    "undetermined_share_percent": share(chained, determined),
                },
            }
        for window in segment["annual"]:
            window["split"] = pair(regime, window["baseline"], window["current"])
        chains[regime] = {
            "determined": determined,
            "total": dict(chained),
            "undetermined_share_percent": share(chained, determined),
        }
    headline = result.get("headline")
    if headline:
        old = next(s for s in result["segments"] if s["regime"] == "old")
        row = next(r for r in old["rows"] if r["t_public"] == headline["t_public"])
        headline["split"] = {"vs_year_earlier": row["split"]["vs_year_earlier"], **chains["old"]}
    result["split"] = {
        "definition": definition,
        "rules": list(RULES),
        "content_rule_file": str(rule_file.name),
        "content_rule_sha256": rule_digest,
        "chained": chains,
    }
    return result
