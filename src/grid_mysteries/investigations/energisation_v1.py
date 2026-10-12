"""020 version 1 — the join at project level (amendment 3, B2 and B3), pure.

`investigations/020-did-it-energise/DECLARATION-amendment-3.md` (SHA-256
f84367c3…) completes amendments 1 and 2 for the realised delay: J1 proposes
Elexon BM units (S1, the 30/09/2026 vintage) for each project version 0.2
measured, by counted shared tokens and capacity, a unit or a set of units
under one `nationalGridBmUnit` stem; a person admits. No I/O.
"""

import math
import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
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
