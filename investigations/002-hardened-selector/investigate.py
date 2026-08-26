"""Investigate Mystery 002 under the explanation protocol.

    uv run python investigations/002-hardened-selector/investigate.py case
    uv run python investigations/002-hardened-selector/investigate.py crosscheck

`case` reduces the selected case to pinned facts: both units' reference
data, their whole-day physical state and submissions, the full acceptance
chain the accepted action belongs to, and NESO's own published exclusion
reasons for both sides. `crosscheck` is the declared post-selection
comparison with NESO's skip-rate data over the surviving candidate set.

Both read only pinned artefacts and write evidence; neither changes the
selection, which is closed.
"""

import csv
import json
import sys
from collections import Counter
from decimal import Decimal

from selection import EVIDENCE, governed_thresholds, scan

from grid_mysteries.corpus import (
    BMUNITS_PATH,
    PERIODS,
    load_records,
    physical_path,
    unit_maps,
    window_path,
)
from grid_mysteries.evidence import write_json
from grid_mysteries.investigations.bod_inversion import accepted_volume_mwh
from grid_mysteries.investigations.exclusion_attribution import categorise
from grid_mysteries.investigations.hardened_selection import screen
from grid_mysteries.sources import neso

#: The post-selection cross-check vintage, pinned in evidence/neso-manifest.json.
EXCLUSIONS_CSV = "exclusions_2026-08_v2026-08-22.csv"
PHYSICAL = ("PN", "MELS", "MILS")


def selected_case() -> dict:
    return json.loads((EVIDENCE / "selected.json").read_text())["selected"]


def reference(units: set[str]) -> dict:
    keep = (
        "elexonBmUnit",
        "nationalGridBmUnit",
        "bmUnitType",
        "leadPartyName",
        "fuelType",
        "generationCapacity",
        "demandCapacity",
    )
    return {
        str(r["elexonBmUnit"]): {k: r.get(k) for k in keep if k in r}
        for r in load_records(BMUNITS_PATH)
        if str(r.get("elexonBmUnit")) in units
    }


def day_profile(unit: str, day: str) -> dict:
    """Whole-day physical state, submissions and acceptances for one unit."""
    periods, zero_offer, accepted_periods = [], 0, 0
    for period in PERIODS:
        levels = {}
        for dataset in PHYSICAL:
            rows = [
                r
                for r in load_records(physical_path(dataset, day, period))
                if str(r["bmUnit"]) == unit
            ]
            if rows:
                levels[dataset] = [str(rows[0]["levelFrom"]), str(rows[0]["levelTo"])]
        offers = [
            r
            for r in load_records(window_path("bod", day, period))
            if str(r["bmUnit"]) == unit and int(r["pairId"]) >= 1
        ]
        if offers and offers[0].get("offer") is not None and Decimal(str(offers[0]["offer"])) == 0:
            zero_offer += 1
        volume = Decimal(0)
        for r in load_records(window_path("disptav_offer", day, period)):
            if str(r["bmUnit"]) == unit and r.get("dataType") == "Original":
                volume += accepted_volume_mwh(r)
        if volume:
            accepted_periods += 1
        acceptances = [
            {
                "acceptance": int(r["acceptanceNumber"]),
                "level_from": str(r["levelFrom"]),
                "level_to": str(r["levelTo"]),
                "time_from": r.get("timeFrom"),
                "time_to": r.get("timeTo"),
                "acceptance_time": r.get("acceptanceTime"),
                "so_flag": bool(r["soFlag"]),
            }
            for r in load_records(window_path("boalf", day, period))
            if str(r["bmUnit"]) == unit
        ]
        periods.append(
            {
                "period": period,
                "levels": levels,
                "offer_price": str(offers[0]["offer"]) if offers else None,
                "accepted_offer_mwh": str(volume),
                "acceptances": acceptances,
            }
        )
    return {
        "periods_with_zero_priced_offer": zero_offer,
        "periods_with_accepted_offer_volume": accepted_periods,
        "periods": periods,
    }


def neso_exclusions(units: set[str], day: str) -> dict:
    """NESO's own published exclusion reasons, per unit, for the day."""
    _, elexon_to_ngc = unit_maps()
    ngc = {elexon_to_ngc.get(u, u): u for u in units}
    found: dict[str, Counter] = {u: Counter() for u in units}
    volumes: dict[str, Decimal] = {u: Decimal(0) for u in units}
    path = neso.NESO_RAW / EXCLUSIONS_CSV
    with path.open() as handle:
        for row in csv.DictReader(handle):
            if row["date"][:10] != day or row["bm_unit"] not in ngc:
                continue
            unit = ngc[row["bm_unit"]]
            for category in categorise(row["exclusion_reason"]):
                found[unit][category] += 1
            volumes[unit] += Decimal(row["excluded_volume_MWh"] or "0")
    return {
        unit: {
            "ngc_unit": elexon_to_ngc.get(unit, unit),
            "excluded_rows_by_category": dict(found[unit]),
            "total_excluded_volume_mwh": str(volumes[unit]),
        }
        for unit in units
    }


def case() -> None:
    selected = selected_case()
    day = selected["settlement_date"]
    units = {selected["accepted_unit"], selected["unaccepted_unit"]}
    report = {
        "selected": selected,
        "reference": reference(units),
        "day_profile": {unit: day_profile(unit, day) for unit in sorted(units)},
        "neso_published_exclusions": neso_exclusions(units, day),
        "labelling": (
            "Facts only, from pinned artefacts. NESO's exclusion data is daily-grain "
            "(no settlement period column), so its reasons are day-level statements "
            "about a unit's pair, not per-period ones."
        ),
    }
    write_json(EVIDENCE / "case-report.json", report)
    print(f"wrote case-report.json for {day} period {selected['settlement_period']}")
    for unit, block in report["neso_published_exclusions"].items():
        print(
            f"  NESO exclusions {unit} ({block['ngc_unit']}): {block['excluded_rows_by_category']}"
        )


def exclusion_index(day_range: list[str]) -> dict:
    """(ngc unit, date, direction) -> set of NESO exclusion categories.

    Day-grain: NESO's exclusion export carries no settlement period, so a
    category here is a statement about the unit's day, never the period.
    """
    index: dict[tuple[str, str, str], set[str]] = {}
    with (neso.NESO_RAW / EXCLUSIONS_CSV).open() as handle:
        for row in csv.DictReader(handle):
            day = row["date"][:10]
            if day not in day_range:
                continue
            key = (row["bm_unit"], day, row["bid_offer"].lower())
            index.setdefault(key, set()).update(categorise(row["exclusion_reason"]))
    return index


def crosscheck() -> None:
    """Declared post-selection comparison with NESO's published skip data."""
    min_accepted_mwh, min_available_mw = governed_thresholds()
    candidates, deliverability, system_flagged = scan(min_accepted_mwh, min_available_mw)
    surviving, _ = screen(candidates, deliverability=deliverability, system_flagged=system_flagged)
    _, elexon_to_ngc = unit_maps()
    days = sorted({c.settlement_date for c in surviving})
    index = exclusion_index(days)

    accepted_side: Counter = Counter()
    alternative_side: Counter = Counter()
    either_side = 0
    for candidate in surviving:
        key = (candidate.settlement_date, candidate.direction)
        acc = index.get(
            (elexon_to_ngc.get(candidate.accepted_unit, candidate.accepted_unit), *key), set()
        )
        alt = index.get(
            (elexon_to_ngc.get(candidate.unaccepted_unit, candidate.unaccepted_unit), *key), set()
        )
        for category in acc or {"(none)"}:
            accepted_side[category] += 1
        for category in alt or {"(none)"}:
            alternative_side[category] += 1
        if acc or alt:
            either_side += 1

    result = {
        "labelling": (
            "NESO's published exclusion reasons are DAY-grain and VOLUMETRIC; this is an "
            "attribution of the surviving disagreement, never an accuracy score, and the "
            "categories were deliberately NOT used as selection filters (Method Study 001C "
            "showed binarising them degrades agreement)."
        ),
        "surviving_candidates": len(surviving),
        "candidates_with_a_published_exclusion_on_either_side": either_side,
        "accepted_side_categories": dict(accepted_side.most_common()),
        "alternative_side_categories": dict(alternative_side.most_common()),
    }
    write_json(EVIDENCE / "neso-crosscheck.json", result)
    share = either_side / len(surviving) * 100 if surviving else 0
    print(f"surviving candidates: {len(surviving):,}")
    print(f"with a NESO-published exclusion on either side: {either_side:,} ({share:.1f}%)")
    print("accepted side:", dict(accepted_side.most_common(5)))
    print("alternative side:", dict(alternative_side.most_common(5)))


COMMANDS = {"case": case, "crosscheck": crosscheck}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit(f"usage: investigate.py [{'|'.join(COMMANDS)}]")
    COMMANDS[sys.argv[1]]()
