"""020 version 1 — the join at project level (amendment 3, B2 and B3), pure.

`investigations/020-did-it-energise/DECLARATION-amendment-3.md` (SHA-256
f84367c3…) completes amendments 1 and 2 for the realised delay: J1 proposes
Elexon BM units (S1, the 30/09/2026 vintage) for each project version 0.2
measured, by counted shared tokens and capacity, a unit or a set of units
under one `nationalGridBmUnit` stem; a person admits. No I/O.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.sources.tec_register import normalise, parse_decimal

AMENDMENT_3_PREFIX: Final = "f84367c3"
TOKEN_MIN: Final = 4
#: A token counts only if fewer than this share of S1's units carry it.
COMMON_SHARE: Final = Decimal("0.01")
CAPACITY_TOLERANCE: Final = Decimal("0.25")
EXACT_TOLERANCE: Final = Decimal("0.05")
EMBEDDED_AGREEMENTS: Final = frozenset({"embedded", "bega"})

#: B5's plant families, and the S1 `fuelType` values each implies (B2's
#: fuel agreement). A family with no fuel type implied scores `unknown`.
FAMILY_FUELS: Final[dict[str, frozenset[str]]] = {
    "offshore wind": frozenset({"WIND"}),
    "onshore wind": frozenset({"WIND"}),
    "thermal": frozenset({"CCGT", "OCGT", "BIOMASS", "COAL", "NUCLEAR"}),
    "storage": frozenset({"PS"}),
    "solar": frozenset(),
    "hybrid": frozenset(),
    "other": frozenset(),
}
_THERMAL: Final = ("ccgt", "ocgt", "chp", "thermal", "biomass", "gas", "coal", "nuclear")


def tokens(text: object) -> frozenset[str]:
    """Words of the normalised text (005's rule), four characters or more,
    at least one a letter."""
    return frozenset(
        w for w in normalise(text).split() if len(w) >= TOKEN_MIN and any(c.isalpha() for c in w)
    )


def unit_tokens(unit: dict[str, Any]) -> frozenset[str]:
    return tokens(unit.get("bmUnitName")) | tokens(unit.get("leadPartyName"))


def common_tokens(units: list[dict[str, Any]]) -> frozenset[str]:
    """Tokens carried by 1 % or more of S1's units: never counted."""
    df: Counter[str] = Counter()
    for unit in units:
        df.update(unit_tokens(unit))
    n = Decimal(len(units))
    return frozenset(t for t, k in df.items() if Decimal(k) >= COMMON_SHARE * n)


def stem(national_grid_id: object) -> str:
    """`CARR-1` and `CARR-2` are stem `CARR`: a trailing `-<digits>` or
    trailing digits removed."""
    return re.sub(r"-?\d+$", "", str(national_grid_id or "").strip())


def family(plant_type: object) -> str:
    """B5's plant family of a `Plant Type` as printed."""
    parts = [p.strip().casefold() for p in str(plant_type or "").split(";") if p.strip()]
    found: set[str] = set()
    storage = False
    for p in parts:
        if "wind offshore" in p:
            found.add("offshore wind")
        elif "wind onshore" in p:
            found.add("onshore wind")
        elif "pv array" in p or "solar" in p:
            found.add("solar")
        elif "energy storage" in p or "battery storage" in p:
            storage = True
        elif p == "hybrid":
            found.add("hybrid")
        elif any(t in p for t in _THERMAL):
            found.add("thermal")
        elif p in ("demand", "reactive compensation"):
            continue
        else:
            found.add("other")
    if storage:
        return "hybrid" if found - {"other"} else "storage"
    if len(found) > 1:
        return "hybrid"
    return next(iter(found), "other")


def is_storage(plant_type: object) -> bool:
    text = str(plant_type or "").casefold()
    return "energy storage" in text or "battery storage" in text


def _capacities(unit: dict[str, Any], storage: bool) -> list[Decimal]:
    out = []
    generation = parse_decimal(unit.get("generationCapacity"))
    if generation is not None:
        out.append(generation)
    demand = parse_decimal(unit.get("demandCapacity"))
    if storage and demand is not None:
        out.append(abs(demand))
    return out


def _within(value: Decimal, target: Decimal | None, tolerance: Decimal) -> bool:
    return target is not None and target > 0 and abs(value - target) <= tolerance * target


def fuel_agreement(plant_family: str, units: Iterable[dict[str, Any]]) -> str:
    implied = FAMILY_FUELS.get(plant_family, frozenset())
    printed = {str(u.get("fuelType")) for u in units if u.get("fuelType")}
    if not implied or not printed:
        return "unknown"
    return "match" if printed <= implied else "differs"


@dataclass(frozen=True)
class Project:
    """A B1 project, as J1 sees it."""

    key: str
    name: str
    customer: str
    site: str
    plant_type: str
    capacity_mw: Decimal
    cumulative_mw: Decimal | None

    @property
    def tokens(self) -> frozenset[str]:
        return tokens(self.name) | tokens(self.customer) | tokens(self.site)


def project_from_key(
    key: str, plant_type: str, capacity_mw: Decimal, cumulative_mw: Decimal | None
) -> Project:
    """The project's text is its key's normalised (name, customer, site)."""
    triple = key.split("|", 1)[1]
    name, customer, site = (triple.removeprefix("name:").split("|") + ["", "", ""])[:3]
    return Project(key, name, customer, site, plant_type, capacity_mw, cumulative_mw)


def _candidate(
    kind: str,
    units: list[dict[str, Any]],
    project: Project,
    shared: frozenset[str],
    capacity: Decimal,
) -> dict[str, Any]:
    ratio = (capacity / project.capacity_mw).quantize(Decimal("0.001"))
    fuel = fuel_agreement(family(project.plant_type), units)
    names = {normalise(u.get("bmUnitName")) for u in units} | {
        normalise(u.get("leadPartyName")) for u in units
    }
    exact = (
        normalise(project.name) in names
        and _within(capacity, project.capacity_mw, EXACT_TOLERANCE)
        and fuel == "match"
    )
    return {
        "kind": kind,
        "units": [u["elexonBmUnit"] for u in units],
        "national_grid_units": [u.get("nationalGridBmUnit") for u in units],
        "names": [u.get("bmUnitName") for u in units],
        "lead_parties": sorted({str(u.get("leadPartyName")) for u in units}),
        "fuel_types": sorted({str(u.get("fuelType")) for u in units if u.get("fuelType")}),
        "capacity_mw": str(capacity),
        "capacity_ratio": str(ratio),
        "shared_tokens": sorted(shared),
        "fuel": fuel,
        "exact": exact,
    }


def candidates(
    project: Project, units: list[dict[str, Any]], common: frozenset[str]
) -> list[dict[str, Any]]:
    """B2: every unit candidate and set candidate for one project, ordered by
    counted tokens shared (more first), then by the capacity ratio's
    distance from 1."""
    storage = is_storage(project.plant_type)
    wanted = project.tokens - common
    targets = (project.capacity_mw, project.cumulative_mw)
    matched: list[tuple[dict[str, Any], frozenset[str]]] = []
    for unit in units:
        if not unit.get("elexonBmUnit"):
            continue
        shared = unit_tokens(unit) & wanted
        if shared:
            matched.append((unit, shared))
    out = []
    for unit, shared in matched:
        hits = [
            c
            for c in _capacities(unit, storage)
            if any(_within(c, t, CAPACITY_TOLERANCE) for t in targets)
        ]
        if hits:
            out.append(_candidate("unit", [unit], project, shared, hits[0]))
    by_stem: dict[str, list[tuple[dict[str, Any], frozenset[str]]]] = defaultdict(list)
    for unit, shared in matched:
        by_stem[stem(unit.get("nationalGridBmUnit"))].append((unit, shared))
    for group in by_stem.values():
        if len(group) < 2:
            continue
        group_units = sorted((u for u, _ in group), key=lambda u: str(u["elexonBmUnit"]))
        shared = frozenset().union(*(s for _, s in group))
        sums = []
        generation = [parse_decimal(u.get("generationCapacity")) for u in group_units]
        if all(g is not None for g in generation):
            sums.append(sum((g for g in generation if g is not None), Decimal(0)))
        if storage:
            demand = [parse_decimal(u.get("demandCapacity")) for u in group_units]
            if all(d is not None for d in demand):
                sums.append(sum((abs(d) for d in demand if d is not None), Decimal(0)))
        hits = [s for s in sums if any(_within(s, t, CAPACITY_TOLERANCE) for t in targets)]
        if hits:
            out.append(_candidate("set", group_units, project, shared, hits[0]))
    return sorted(
        out,
        key=lambda c: (
            -len(c["shared_tokens"]),
            abs(Decimal(c["capacity_ratio"]) - 1),
            c["kind"],
            c["units"],
        ),
    )


def embedded(agreement_types: list[str]) -> bool | None:
    """J3 (B3): True when every capacity-bearing stage of the copy before
    prints `Embedded` or `BEGA`; None when the copy prints no
    `Agreement Type` for them (not determinable from the register)."""
    values = [str(a or "").strip().casefold() for a in agreement_types]
    values = ["" if v == "null" else v for v in values]
    if not any(values):
        return None
    return all(v in EMBEDDED_AGREEMENTS for v in values)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[Decimal, Decimal] | None:
    """The 95 % Wilson interval of k in n (B5)."""
    if n == 0:
        return None
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (
        Decimal(max(0.0, centre - half)).quantize(Decimal("0.001")),
        Decimal(min(1.0, centre + half)).quantize(Decimal("0.001")),
    )


# ------------------------------------------------------------- B4: the walk

B1610_FIELDS: Final = (
    "dataset",
    "psrType",
    "bmUnit",
    "settlementDate",
    "settlementPeriod",
    "halfHourEndTime",
    "settlementRunType",
    "quantity",
)
WALK_FLOOR: Final = date(2015, 1, 1)
WINDOW_DAYS: Final = 7
SEED: Final = 20261012
RESAMPLES: Final = 10_000


def windows_back(run_date: date, floor: date = WALK_FLOOR) -> Iterator[tuple[date, date]]:
    """Seven-settlement-day windows (from, to), walking back from the run
    date; the last one stops at the floor."""
    to = run_date
    while to >= floor:
        start = max(to - timedelta(days=WINDOW_DAYS - 1), floor)
        yield start, to
        to = start - timedelta(days=1)


def format_check(raw: bytes, units: set[str]) -> list[str]:
    """B4's format check, before any value is read: UTF-8 without a BOM,
    JSON, an array (or an object's `data` array), every record carrying the
    S2 report's always-present fields, `bmUnit` among the requested units."""
    problems = []
    if raw.startswith(b"\xef\xbb\xbf"):
        problems.append("byte-order mark")
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return [*problems, f"not UTF-8 JSON: {error}"[:120]]
    data = document.get("data") if isinstance(document, dict) else document
    if not isinstance(data, list):
        return [*problems, f"top level is {type(document).__name__}, not an array"]
    for i, record in enumerate(data):
        if not isinstance(record, dict):
            problems.append(f"record {i} is not an object")
            break
        missing = [f for f in B1610_FIELDS if f not in record]
        if missing:
            problems.append(f"record {i} lacks {missing}")
            break
        if record["bmUnit"] not in units:
            problems.append(f"record {i} names unit {record['bmUnit']!r}, not requested")
            break
    return problems


def records(raw: bytes) -> list[dict[str, Any]]:
    document = json.loads(raw.decode("utf-8"))
    data = document.get("data") if isinstance(document, dict) else document
    return list(data or [])


def proxy(windows: list[list[dict[str, Any]]]) -> tuple[date, str] | None:
    """The earliest settlement day with `quantity` > 0 for any admitted
    unit, over every run type, with the run type of that record."""
    best: tuple[date, str] | None = None
    for recs in windows:
        for r in recs:
            q = parse_decimal(r.get("quantity"))
            if q is None or q <= 0:
                continue
            day = date.fromisoformat(str(r["settlementDate"])[:10])
            if best is None or day < best[0]:
                best = (day, str(r.get("settlementRunType")))
    return best


@dataclass(frozen=True)
class Walk:
    """The outcome of one project's walk: whether any window held records,
    whether the floor window did (left-censored), and the proxy."""

    windows: int
    any_records: bool
    floor_has_records: bool
    proxy: tuple[date, str] | None


def label(admitted: bool, j3: str, had_candidates: bool, walk: Walk | None) -> str:
    """B4's labels; every project of B1 lands in exactly one (C4)."""
    if not admitted:
        if j3 == "embedded-or-distribution":
            return "embedded-or-distribution"
        return "unmatched" if had_candidates else "no-candidate"
    assert walk is not None
    if walk.floor_has_records:
        return "metered-before-the-walk"
    if walk.proxy is not None:
        return "metered"
    return "registered-not-metered" if walk.any_records else "no-metered-record"


def months(to: date, from_date: date) -> Decimal:
    return (Decimal((to - from_date).days) / Decimal("30.4375")).quantize(Decimal("0.1"))


def bootstrap_median(values: list[Decimal], rng: random.Random) -> list[str] | None:
    """B5: 95 % percentile interval of the `quantiles` median over 10,000
    resamples with replacement; none below n = 5."""
    from grid_mysteries.investigations.energisation import quantiles

    n = len(values)
    if n < 5:
        return None
    medians = []
    for _ in range(RESAMPLES):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        m = quantiles(sample)["median"]
        assert isinstance(m, Decimal)
        medians.append(m)
    medians.sort()
    return [str(medians[int(0.025 * (RESAMPLES - 1))]), str(medians[int(0.975 * (RESAMPLES - 1))])]


def distribution(values: list[Decimal], rng: random.Random) -> dict[str, Any]:
    """n, quantiles, the median's interval, and the shares before (< 0),
    within six months after (0 to 6.0) and later, with Wilson intervals."""
    from grid_mysteries.investigations.energisation import quantiles

    n = len(values)
    q: dict[str, Any] = dict(quantiles(values))
    q["median_ci95"] = bootstrap_median(values, rng)
    q["median_ci95_note"] = None if n >= 5 else "n < 5, no interval"
    for name, test in (
        ("before", lambda v: v < 0),
        ("within_six_months", lambda v: 0 <= v <= Decimal("6.0")),
        ("later", lambda v: v > Decimal("6.0")),
    ):
        k = sum(1 for v in values if test(v))
        interval = wilson(k, n)
        q[name] = {"k": k, "wilson95": [str(x) for x in interval] if interval else None}
    return q


# ------------------------------------------------------------- amendment 4

AMENDMENT_4_PREFIX: Final = "fab5665e"


def effective_floor(walks: dict[str, list[dict[str, Any]]]) -> date | None:
    """A2: the first window in which the walk found records for any project."""
    starts = [
        date.fromisoformat(w["from"]) for windows in walks.values() for w in windows if w["records"]
    ]
    return min(starts) if starts else None


def censored(windows: list[dict[str, Any]], floor: date | None) -> bool:
    """A2: a project whose earliest record falls in the effective floor's
    window has output the walk cannot date."""
    with_records = [date.fromisoformat(w["from"]) for w in windows if w["records"]]
    return floor is not None and bool(with_records) and min(with_records) == floor


def second_sightings(admitted: Sequence[tuple[str, date, tuple[str, ...]]]) -> dict[str, str]:
    """A3: {later key: earlier key} for projects whose admitted unit or set is
    also admitted for a project with an earlier first `Built` copy.
    `admitted` holds (key, first Built copy, units)."""
    first: dict[tuple[str, ...], tuple[date, str]] = {}
    for key, built, units in sorted(admitted, key=lambda a: (a[1], a[0])):
        first.setdefault(units, (built, key))
    return {
        key: first[units][1]
        for key, built, units in admitted
        if first[units][1] != key and first[units][0] < built
    }


def first_appearances(
    seen_first: dict[str, tuple[str, str, date]], kept_dates: list[date]
) -> dict[str, tuple[date, int]]:
    """A1: for each `<regime>|<group>` key, the group's earliest kept copy in
    either regime and the days since the kept copy before it in the combined
    sequence. `seen_first` maps each key to (regime, group, first copy in
    that regime)."""
    earliest: dict[str, date] = {}
    for _, group, first in seen_first.values():
        earliest[group] = min(first, earliest.get(group, first))
    order = sorted(set(kept_dates))
    out = {}
    for key, (_, group, _) in seen_first.items():
        d = earliest[group]
        i = order.index(d)
        out[key] = (d, (d - order[i - 1]).days if i > 0 else 0)
    return out


# ---- amendment 5: the population over the filled hole ------------------------

#: Filled in after DECLARATION-amendment-5.md is frozen.
AMENDMENT_5_PREFIX: Final = "63b7e7e9"
#: F5: the amendment-4 bootstrap intervals of the register-lag medians for
#: the two years the hole bounded (year of the first Built copy).
F5_YEARS: Final = ("2025", "2026")
#: F6: the realised-delay median (with later stages, overall) may move by
#: at most this many months from the amendment-4 figure.
F6_TOLERANCE: Final = Decimal("1.0")


def carry_over(
    earlier_decisions: dict[str, dict[str, Any]],
    earlier_candidates: dict[str, list[list[str]]],
    proposals: dict[str, list[list[str]]],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """A5.2: which earlier decisions stand under the new proposals.

    `earlier_decisions` maps a project key to its amendment-4 decision
    (with `decision` and `units`); `earlier_candidates` and `proposals`
    map keys to the candidate unit sets J1 proposed then and now. Returns
    the carried decisions (marked `carried_from_amendment_4`) and the keys
    that need a pre-screen: every key with a candidate now that has no
    decision, an admitted unit set no longer proposed, or a refusal whose
    candidate set changed."""
    carried: dict[str, dict[str, Any]] = {}
    prescreen: list[str] = []
    for key, now in proposals.items():
        if not now:
            continue
        d = earlier_decisions.get(key)
        same_candidates = sorted(map(tuple, earlier_candidates.get(key, []))) == sorted(
            map(tuple, now)
        )
        stands = d is not None and (
            (d["decision"] == "admitted" and d["units"] in now)
            or (d["decision"] != "admitted" and same_candidates)
        )
        if stands and d is not None:
            carried[key] = {**d, "carried_from_amendment_4": True}
        else:
            prescreen.append(key)
    return carried, prescreen


def f5_fires(
    earlier_register_lag: dict[str, Any], later_register_lag: dict[str, Any]
) -> dict[str, Any]:
    """F5: a 2025 or 2026 register-lag median outside its amendment-4 interval."""
    out: dict[str, Any] = {"fires": False, "years": {}}
    for y in F5_YEARS:
        before = earlier_register_lag.get(f"year {y}") or {}
        after = later_register_lag.get(f"year {y}") or {}
        ci = before.get("median_ci95")
        median = after.get("median")
        outside = None
        if ci and median is not None:
            lo, hi = Decimal(str(ci[0])), Decimal(str(ci[1]))
            outside = not (lo <= Decimal(str(median)) <= hi)
        out["years"][y] = {
            "before": before.get("median"),
            "before_ci95": ci,
            "before_n": before.get("n"),
            "after": median,
            "after_ci95": after.get("median_ci95"),
            "after_n": after.get("n"),
            "outside": outside,
        }
        out["fires"] = out["fires"] or bool(outside)
    return out


def f6_fires(earlier_overall: dict[str, Any], later_overall: dict[str, Any]) -> dict[str, Any]:
    """F6: the overall realised-delay median (with later stages) moved by more than 1.0 month."""
    before, after = earlier_overall.get("median"), later_overall.get("median")
    moved = (
        abs(Decimal(str(after)) - Decimal(str(before)))
        if before is not None and after is not None
        else None
    )
    return {
        "before": before,
        "after": after,
        "moved": str(moved) if moved is not None else None,
        "tolerance": str(F6_TOLERANCE),
        "fires": bool(moved is not None and moved > F6_TOLERANCE),
    }
