"""Investigation 021: 014's connection-slippage series cut by plant type and
by host transmission owner.

Pure; no I/O. Two parts:

- the **schema pass** (`key_stability`): whether a project-stage's printed
  plant type or host TO changes between consecutive copies of the archive,
  counted over every parsed copy. It is a fact about the archive's columns,
  recorded in the committed schema report before any grouped figure is
  declared; it computes no movement.
- the **cut** (written after the declaration is frozen): each comparison of
  014 version 4, with the same population, split by a grouping key read
  from the register as printed.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import connection_slippage_v3 as v3

#: (report key, register column) of the two grouping keys, as 014's reader
#: canonicalises the column names.
GROUPING: Final = (("plant_type", "Plant Type"), ("host_to", "HOST TO"))
#: How many of the most frequent transitions of a key the SCHEMA.md summary
#: lists; the JSON report keeps every transition.
TRANSITIONS_LISTED: Final = 25


def printed(value: object) -> str:
    """A cell as printed, with runs of whitespace collapsed; blank stays blank."""
    return " ".join(str(value or "").split())


def tags(rows: list[dict[str, object]]) -> dict[str, dict[str, str]]:
    """Each unit's printed grouping keys in one copy, by 014's unit key."""
    out: dict[str, dict[str, str]] = {}
    for key, row in zip(cs.unit_keys(rows), rows, strict=True):
        out[key] = {name: printed(row.get(column)) for name, column in GROUPING}
    return out


def key_stability(copies: list[tuple[date, list[dict[str, object]]]]) -> dict[str, Any]:
    """Over consecutive copies, for units (014's key) printed in both: how
    many change their plant type, how many their host TO, which transitions
    occur, and in which copies. No movement figure is computed."""
    changed: dict[str, Counter[tuple[str, str]]] = {name: Counter() for name, _ in GROUPING}
    per_copy: list[dict[str, Any]] = []
    matched_total = 0
    previous: dict[str, dict[str, str]] | None = None
    previous_date: date | None = None
    for t, rows in copies:
        current = tags(rows)
        if previous is not None:
            both = previous.keys() & current.keys()
            matched_total += len(both)
            counts = {name: 0 for name, _ in GROUPING}
            for key in both:
                for name, _ in GROUPING:
                    before, now = previous[key][name], current[key][name]
                    if before != now:
                        counts[name] += 1
                        changed[name][(before, now)] += 1
            if any(counts.values()):
                per_copy.append(
                    {
                        "previous": previous_date.isoformat() if previous_date else None,
                        "t_public": t.isoformat(),
                        "matched": len(both),
                        **{f"{name}_changed": n for name, n in counts.items()},
                    }
                )
        previous, previous_date = current, t
    return {
        "copies": len(copies),
        "matched_units_over_consecutive_copies": matched_total,
        **{
            name: {
                "units_changed": sum(changed[name].values()),
                "distinct_transitions": len(changed[name]),
                "transitions": [
                    {"from": a, "to": b, "units": n} for (a, b), n in changed[name].most_common()
                ],
            }
            for name, _ in GROUPING
        },
        "copies_with_a_change": per_copy,
    }


# ---------------------------------------------------------------- the cut
#
# Everything below implements DECLARATION.md (SHA-256 76ad7dc3…) of
# investigation 021, frozen before any of it was written: R1 to R9, checks
# C3 and C4, F-G2 and F-G4, and the propositions. The population and the
# movement arithmetic are 014's (`connection_slippage`, `connection_slippage_v3`).

RULES: Final = v3.RULES
RULE_V2: Final = v3.RULE_V2
SEPARATOR: Final = ";"
KEY_CHANGED: Final = "key changed"
BLANK_GROUP: Final = "(blank)"
#: R1: a spelling the register replaced by its own expansion or later
#: spelling, per `;`-separated component of a plant type.
PLANT_SPELLING: Final[dict[str, str]] = {
    "CCGT": "CCGT (Combined Cycle Gas Turbine)",
    "OCGT": "OCGT (Open Cycle Gas Turbine)",
    "CHP": "CHP (Combined Heat and Power)",
    "PV Array": "PV Array (Photo Voltaic/solar)",
    "Oil & AGT": "Oil & AGT (Advanced Gas Turbine)",
    "Oil + AGT": "Oil & AGT (Advanced Gas Turbine)",
    "HYBRID": "Hybrid",
    "Onshore Wind": "Wind Onshore",
    "Energy storage system": "Energy Storage System",
}
HOST_SPELLING: Final[dict[str, str]] = {"SHE": "SHET", "SPTL": "SPT", "OFFSHORE": "OFTO"}
#: R8: the register's label for energy storage, and its predecessor.
STORAGE_LABELS: Final = ("Energy Storage System", "Battery Storage")
#: R9: shares of a net within this many MW-years of zero are not read.
SMALL_NET: Final = Decimal(1000)
#: F-G4: a "key changed" bucket above this share of dated capacity is unfit.
UNFIT_SHARE: Final = Decimal("0.2")
#: P-A, P-B and P-C's thresholds, as declared.
PA_NET_SHARE: Final = Decimal("66.7")
PA_CAPACITY_SHARE: Final = Decimal("50.0")
PB_MIN_DATED: Final = 30
PC_POINTS: Final = Decimal("15.0")
SHARE_QUANTUM: Final = Decimal("0.1")
MW_QUANTUM: Final = cs.MW_QUANTUM
MW_YEARS_QUANTUM: Final = cs.MW_YEARS_QUANTUM
ZERO: Final = Decimal(0)
Entries = dict[str, cs.Entry]


class RuleDisagreement(RuntimeError):
    """F-G2 (C3): the determined part of a group differs between the rules."""


def read_key(name: str, value: object) -> tuple[str, str]:
    """R1: (the key as printed under the whitespace rule, the key under the
    spelling table) for one cell of the `name` dimension."""
    text = printed(value)
    if name == "plant_type":
        parts = [p.strip() for p in text.split(SEPARATOR)]
        return SEPARATOR.join(parts), SEPARATOR.join(PLANT_SPELLING.get(p, p) for p in parts)
    return text, HOST_SPELLING.get(text, text)


def group_name(unified: str) -> str:
    """R3: a blank key is the group '(blank)'."""
    return unified or BLANK_GROUP


def is_storage(group: str, *, including_compounds: bool) -> bool:
    """R8: storage alone is the label itself; including compounds, any
    `;`-separated component is the label. Buckets are neither."""
    if group in (KEY_CHANGED, BLANK_GROUP):
        return False
    parts = group.split(SEPARATOR)
    if including_compounds:
        return any(p in STORAGE_LABELS for p in parts)
    return len(parts) == 1 and parts[0] in STORAGE_LABELS


Keys = dict[str, dict[str, tuple[str, str]]]


def keys_from_rows(rows: list[dict[str, object]]) -> Keys:
    """Each 014 unit's (as printed, unified) key per dimension, in one copy."""
    out: Keys = {}
    for key, row in zip(cs.unit_keys(rows), rows, strict=True):
        out[key] = {name: read_key(name, row.get(column)) for name, column in GROUPING}
    return out


def keys_from_units(units: dict[str, Any]) -> Keys:
    """The same for the content rule's units (`tec.identity.Unit`, which
    carry their row)."""
    return {
        name: {dim: read_key(dim, unit.row.get(column)) for dim, column in GROUPING}
        for name, unit in units.items()
    }


@dataclass
class Acc:
    """One bucket of one comparison and dimension, accumulating."""

    units_baseline: int = 0
    matched: int = 0
    dated_both: int = 0
    later: int = 0
    earlier: int = 0
    unchanged: int = 0
    capacity_baseline: Decimal = ZERO
    capacity_current: Decimal = ZERO
    pos: dict[str, Decimal] = field(default_factory=lambda: dict.fromkeys(RULES, ZERO))
    neg: dict[str, Decimal] = field(default_factory=lambda: dict.fromkeys(RULES, ZERO))
    pos_det: dict[str, Decimal] = field(default_factory=lambda: dict.fromkeys(RULES, ZERO))
    neg_det: dict[str, Decimal] = field(default_factory=lambda: dict.fromkeys(RULES, ZERO))


def _bucket(dimension: str, kb: dict[str, tuple[str, str]], kc: dict[str, tuple[str, str]]) -> str:
    """R2: the group when both readings agree under the table, else the bucket."""
    b, c = kb[dimension][1], kc[dimension][1]
    return group_name(b) if b == c else KEY_CHANGED


def _q(value: Decimal, quantum: Decimal) -> Decimal:
    return value.quantize(quantum)


def accumulate(
    acc: dict[str, Acc],
    rule: str,
    baseline: Entries,
    current: Entries,
    keys_b: Keys,
    keys_c: Keys,
    undetermined: set[str],
    dimension: str,
) -> int:
    """One rule's pass over a comparison: movements per bucket, and under
    version 2's rule the counts and capacities too. Returns the number of
    dated units whose keys differ as printed but agree under the table."""
    unified_only = 0
    counting = rule == RULE_V2
    if counting:
        for key, kb in keys_b.items():
            if key in baseline:
                acc.setdefault(group_name(kb[dimension][1]), Acc()).units_baseline += 1
    for key in sorted(baseline.keys() & current.keys()):
        kb, kc = keys_b[key], keys_c[key]
        bucket = _bucket(dimension, kb, kc)
        a = acc.setdefault(bucket, Acc())
        b, c = baseline[key], current[key]
        if counting:
            a.matched += 1
        if b.effective is None or c.effective is None:
            continue
        if kb[dimension][0] != kc[dimension][0] and bucket != KEY_CHANGED:
            unified_only += 1
        weight = abs(b.mw) if b.mw is not None else ZERO
        movement = weight * cs.years_between(b.effective, c.effective)
        determined = b.identity not in undetermined
        side = a.pos if movement > ZERO else a.neg
        side[rule] += movement
        if determined:
            (a.pos_det if movement > ZERO else a.neg_det)[rule] += movement
        if counting:
            a.dated_both += 1
            if movement > ZERO:
                a.later += 1
            elif movement < ZERO:
                a.earlier += 1
            else:
                a.unchanged += 1
            a.capacity_baseline += weight
            a.capacity_current += abs(c.mw) if c.mw is not None else ZERO
    return unified_only


def _share(part: Decimal, whole: Decimal) -> Decimal | None:
    return _q(part * 100 / whole, SHARE_QUANTUM) if whole else None


def finish(
    bucket: str,
    a: Acc,
    *,
    comparison_net: Decimal,
    comparison_determined: Decimal,
    comparison_capacity: Decimal,
) -> dict[str, Any]:
    """R5 and R6 for one bucket; C3 (F-G2) on its determined part."""
    total = {r: _q(a.pos[r], MW_YEARS_QUANTUM) + _q(a.neg[r], MW_YEARS_QUANTUM) for r in RULES}
    det = {
        r: _q(a.pos_det[r], MW_YEARS_QUANTUM) + _q(a.neg_det[r], MW_YEARS_QUANTUM) for r in RULES
    }
    if len(set(det.values())) != 1:
        raise RuleDisagreement(
            f"F-G2: the determined part of {bucket!r} differs between the rules: {det}"
        )
    determined = det[RULE_V2]
    share_net = _share(total[RULE_V2], comparison_net)
    share_capacity = _share(a.capacity_baseline, comparison_capacity)
    return {
        "group": bucket,
        "bucket": bucket in (KEY_CHANGED, BLANK_GROUP),
        "units_baseline": a.units_baseline,
        "matched": a.matched,
        "dated_both": a.dated_both,
        "later": a.later,
        "earlier": a.earlier,
        "unchanged": a.unchanged,
        "capacity_baseline_mw": _q(a.capacity_baseline, MW_QUANTUM),
        "capacity_current_mw": _q(a.capacity_current, MW_QUANTUM),
        "mw_years_later": _q(a.pos[RULE_V2], MW_YEARS_QUANTUM),
        "mw_years_earlier": _q(a.neg[RULE_V2], MW_YEARS_QUANTUM),
        "determined": determined,
        "undetermined": {r: total[r] - determined for r in RULES},
        "total": total,
        "share_of_net_percent": share_net,
        "share_of_determined_percent": _share(determined, comparison_determined),
        "share_of_capacity_percent": share_capacity,
        "concentration_points": (
            share_net - share_capacity
            if share_net is not None and share_capacity is not None
            else None
        ),
        # R7, F2 on the group's own population; not applied to a bucket.
        "thin": (
            None
            if bucket == KEY_CHANGED
            else Decimal(a.matched) < cs.F2_THIN_SHARE * Decimal(a.units_baseline)
        ),
    }


def cut(
    *,
    dimension: str,
    v2: tuple[Entries, Entries],
    content: tuple[Entries, Entries],
    keys_v2: tuple[Keys, Keys],
    keys_content: tuple[Keys, Keys],
    undetermined: set[str],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    """One comparison cut along one dimension. `comparison` carries 014's
    figures for it (`mw_years_net`, `determined`, `weighted_mw` as Decimal),
    which the shares are taken over."""
    acc: dict[str, Acc] = {}
    unified = accumulate(acc, RULE_V2, *v2, *keys_v2, undetermined, dimension)
    accumulate(acc, v3.RULE_CONTENT, *content, *keys_content, undetermined, dimension)
    net, determined, capacity = (
        comparison["mw_years_net"],
        comparison["determined"],
        comparison["weighted_mw"],
    )
    groups = [
        finish(
            bucket,
            a,
            comparison_net=net,
            comparison_determined=determined,
            comparison_capacity=capacity,
        )
        for bucket, a in sorted(acc.items())
    ]
    groups.sort(key=lambda g: (g["bucket"], -g["capacity_baseline_mw"], g["group"]))
    changed = next((g for g in groups if g["group"] == KEY_CHANGED), None)
    changed_capacity = changed["capacity_baseline_mw"] if changed else ZERO
    residual = sum((g["total"][RULE_V2] for g in groups), ZERO) - net
    # C4: counts and capacities sum exactly (capacities on the unquantised
    # values, quantised once as 014 quantises `weighted_mw`; the printed
    # 0.01 figures can differ from their sum by rounding); nets within 0.001
    # per bucket.
    checks = {
        "dated_both": sum(g["dated_both"] for g in groups),
        "capacity_baseline_mw": _q(
            sum((a.capacity_baseline for a in acc.values()), ZERO), MW_QUANTUM
        ),
        "rounding_residual": residual,
        "within_rounding": abs(residual) <= MW_YEARS_QUANTUM * len(groups),
    }
    return {
        "dimension": dimension,
        "groups": groups,
        "key_changed": {
            "units": changed["matched"] if changed else 0,
            "dated_both": changed["dated_both"] if changed else 0,
            "capacity_baseline_mw": changed_capacity,
            "mw_years_net": changed["total"][RULE_V2] if changed else ZERO,
        },
        "unified_by_spelling_table": unified,
        "rounding_residual": residual,
        "not_read": abs(net) <= SMALL_NET,
        "unfit": capacity > ZERO and changed_capacity > UNFIT_SHARE * capacity,
        "thin_groups": [g["group"] for g in groups if g["thin"]],
        "storage": (
            {
                reading: storage_reading(groups, including_compounds=(reading == "including"))
                for reading in ("alone", "including")
            }
            if dimension == "plant_type"
            else None
        ),
        "sums": checks,
    }


def storage_reading(groups: list[dict[str, Any]], *, including_compounds: bool) -> dict[str, Any]:
    """R8: one reading's groups, summed, with its two shares."""
    chosen = [g for g in groups if is_storage(g["group"], including_compounds=including_compounds)]
    net = sum((g["total"][RULE_V2] for g in chosen), ZERO)
    share_net = (
        sum((g["share_of_net_percent"] for g in chosen), ZERO)
        if chosen and all(g["share_of_net_percent"] is not None for g in chosen)
        else None
    )
    share_capacity = (
        sum((g["share_of_capacity_percent"] for g in chosen), ZERO)
        if chosen and all(g["share_of_capacity_percent"] is not None for g in chosen)
        else None
    )
    return {
        "groups": [g["group"] for g in chosen],
        "dated_both": sum(g["dated_both"] for g in chosen),
        "capacity_baseline_mw": sum((g["capacity_baseline_mw"] for g in chosen), ZERO),
        "mw_years_net": net,
        "determined": sum((g["determined"] for g in chosen), ZERO),
        "share_of_net_percent": share_net,
        "share_of_capacity_percent": share_capacity,
        "concentration_points": (
            share_net - share_capacity
            if share_net is not None and share_capacity is not None
            else None
        ),
    }


# ---------------------------------------------------------- propositions


def _d(value: Any) -> Decimal | None:
    """A figure as computed (Decimal) or as read back from the evidence (str)."""
    return None if value is None else Decimal(value)


def _usable(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Named groups, with their figures as Decimals whichever way they arrived."""
    out = []
    for g in groups:
        if g["bucket"]:
            continue
        h = dict(g)
        for k in (
            "share_of_net_percent",
            "share_of_determined_percent",
            "share_of_capacity_percent",
            "determined",
        ):
            h[k] = _d(g[k])
        h["total"] = {r: _d(v) for r, v in g["total"].items()}
        out.append(h)
    return out


def propositions(
    headline_by_host: dict[str, Any], headline_by_plant: dict[str, Any]
) -> dict[str, Any]:
    """P-A, P-B and P-C on the headline window, under version 2's rule, each
    decided by its instances, with the determined reading beside."""
    not_read = headline_by_host["not_read"]
    hosts = _usable(headline_by_host["groups"])

    def decide(failing: list[str], considered: list[str]) -> str:
        if not_read or not considered:
            return "undecided"
        return "fails" if failing else "holds"

    pa_failing = [
        g["group"]
        for g in hosts
        if g["share_of_net_percent"] is not None
        and g["share_of_net_percent"] > PA_NET_SHARE
        and g["share_of_capacity_percent"] < PA_CAPACITY_SHARE
    ]
    pa_failing_det = [
        g["group"]
        for g in hosts
        if g["share_of_determined_percent"] is not None
        and g["share_of_determined_percent"] > PA_NET_SHARE
        and g["share_of_capacity_percent"] < PA_CAPACITY_SHARE
    ]
    pa_considered = [g["group"] for g in hosts if not g["thin"]]
    pb_named = [g for g in hosts if g["dated_both"] >= PB_MIN_DATED]
    pb_failing = [g["group"] for g in pb_named if g["total"][RULE_V2] <= ZERO]
    pb_failing_det = [g["group"] for g in pb_named if g["determined"] <= ZERO]
    pb_considered = [g["group"] for g in pb_named if not g["thin"]]
    storage = headline_by_plant["storage"]
    including, alone = storage["including"], storage["alone"]
    pc_points = _d(including["concentration_points"])
    pc_fails = pc_points is not None and abs(pc_points) > PC_POINTS
    pc_considered = [
        g
        for g in _usable(headline_by_plant["groups"])
        if g["group"] in including["groups"] and not g["thin"]
    ]
    det_share = (
        sum(
            (
                g["share_of_determined_percent"]
                for g in _usable(headline_by_plant["groups"])
                if g["group"] in including["groups"]
                and g["share_of_determined_percent"] is not None
            ),
            ZERO,
        )
        if including["groups"]
        else None
    )
    return {
        "P-A": {
            "statement": (
                "no single host TO carries more than two thirds of the headline window's net "
                "movement while holding less than half of its dated capacity"
            ),
            "groups": [
                {
                    "group": g["group"],
                    "share_of_net_percent": g["share_of_net_percent"],
                    "share_of_determined_percent": g["share_of_determined_percent"],
                    "share_of_capacity_percent": g["share_of_capacity_percent"],
                    "thin": g["thin"],
                }
                for g in hosts
            ],
            "failing": pa_failing,
            "failing_on_determined": pa_failing_det,
            "verdict": decide(pa_failing, pa_considered),
        },
        "P-B": {
            "statement": (
                "in the headline window the net movement is positive in every host TO with at "
                "least thirty dated project-stages"
            ),
            "groups": [
                {
                    "group": g["group"],
                    "dated_both": g["dated_both"],
                    "mw_years_net": g["total"][RULE_V2],
                    "determined": g["determined"],
                    "thin": g["thin"],
                }
                for g in pb_named
            ],
            "failing": pb_failing,
            "failing_on_determined": pb_failing_det,
            "verdict": decide(pb_failing, pb_considered),
        },
        "P-C": {
            "statement": (
                "energy storage including compounds carries a share of net movement within "
                "fifteen points of its share of dated capacity in the headline window"
            ),
            "including_compounds": including,
            "storage_alone": alone,
            "share_of_determined_percent": det_share,
            "points": pc_points,
            "verdict": (
                "undecided"
                if not_read or pc_points is None or not pc_considered
                else ("fails" if pc_fails else "holds")
            ),
        },
    }


# ------------------------------------------------------- append-only rows


def require_unchanged(committed: dict[str, str], recomputed: dict[str, str]) -> list[str]:
    """F-G3: keys whose committed line differs from its recomputation; the
    caller refuses on any. Keys not yet committed are the lines to append."""
    return [k for k, line in recomputed.items() if k in committed and committed[k] != line]
