"""Fetch and deterministically select Mystery 002, per the pre-declared rule.

Usage:
    uv run python investigations/002-hardened-selector/selection.py fetch
    uv run python investigations/002-hardened-selector/selection.py select

``fetch`` performs network I/O against the reserved window and is
**gated on the governed record**: it refuses to run unless the v2 claims
show ``ProtocolSealed(inq-002)``, because the human seal is the only
emitter of ``DataAcquisitionAuthorised``. That check is the machine's own
code enforcing the boundary it is asked to respect — see the
cooperative-machine posture in ``morpholog/V2-LAUNCH-RUNBOOK.md``.

``select`` is offline and deterministic: it reads only pinned artefacts,
applies Amendments A and B from the declaration, and writes the funnel,
the ranked head, and the selected case.

Built blind: this module was written and tested before any artefact of
2026-08-11..17 existed, against synthetic fixtures only
(``tests/test_hardened_selection.py``).
"""

from __future__ import annotations

import dataclasses
import json
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import (
    BMUNITS_PATH,
    DIRECTIONS,
    PERIODS,
    REPO_ROOT,
    load_records,
    physical_path,
    window_path,
)
from grid_mysteries.investigations.bod_inversion import (
    accepted_pairs,
    find_inversion_candidates,
    rank_candidates,
    submitted_pairs,
)
from grid_mysteries.investigations.hardened_selection import (
    alternative_key,
    screen,
)
from grid_mysteries.investigations.hardened_selection import (
    select as select_case,
)
from grid_mysteries.investigations.phantom_liquidity import (
    classify,
    headroom_upper_bound,
    level_extremes,
)
from grid_mysteries.sources import elexon
from grid_mysteries.sources.pinning import fetch_journalled

EVIDENCE = Path(__file__).resolve().parent / "evidence"
RAW = REPO_ROOT / "data" / "raw" / "elexon"

#: The reserved window, fixed by prior commitment (see README.md).
WINDOW_START = date(2026, 8, 11)
WINDOW_DAYS = 7
PHYSICAL_DATASETS = ("PN", "MELS", "MILS")

INQUIRY = "inq-002"
V2_PROGRAMME = str(REPO_ROOT / "morpholog" / "research-v2-draft.morph")


def window_dates() -> list[str]:
    return [(WINDOW_START + timedelta(days=day)).isoformat() for day in range(WINDOW_DAYS)]


def require_acquisition_authorised(inquiry: str = INQUIRY) -> None:
    """Refuse to fetch unless the governed record carries the human seal.

    ``inquiry`` is a parameter only so the control itself can be tested
    against disposable state (scripts/rehearse-v2); production always uses
    the declared default.
    """
    import os

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "refusing to fetch: DATABASE_URL is unset, so the seal cannot be checked. "
            "Acquisition is authorised only by ProtocolSealed(inq-002) in the governed record."
        )
    from morpholog_client import open_session

    with open_session(V2_PROGRAMME, database_url) as session:
        sealed = session.claims_named("ProtocolSealed", where={"inquiry": inquiry})
    if not sealed:
        raise SystemExit(
            f"refusing to fetch: no ProtocolSealed({inquiry}) in the governed record. "
            "Only the human seal emits DataAcquisitionAuthorised; see V2-LAUNCH-RUNBOOK.md."
        )
    print(f"seal present: {inquiry} protocol sealed — acquisition authorised", flush=True)


def fetch() -> None:
    require_acquisition_authorised()
    jobs = []
    for day in window_dates():
        for period in PERIODS:
            jobs.append(("BOD", elexon.bid_offer_url(day, period), window_path("bod", day, period)))
            for direction in DIRECTIONS:
                jobs.append(
                    (
                        "DISPTAV",
                        elexon.acceptance_volumes_url(direction, day, period),
                        window_path(f"disptav_{direction}", day, period),
                    )
                )
            jobs.append(
                (
                    "BOALF",
                    f"{elexon.BASE_URL}/balancing/acceptances/all"
                    f"?settlementDate={day}&settlementPeriod={period}",
                    RAW / day / f"boalf_p{period:02d}.json",
                )
            )
            for dataset in PHYSICAL_DATASETS:
                jobs.append(
                    (
                        dataset,
                        f"{elexon.BASE_URL}/balancing/physical/all"
                        f"?dataset={dataset}&settlementDate={day}&settlementPeriod={period}",
                        physical_path(dataset, day, period),
                    )
                )
    EVIDENCE.mkdir(exist_ok=True)
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "fetch-journal.ndjson",
        manifest_path=EVIDENCE / "manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
        progress=lambda path: print(f"pinned {path}", flush=True),
    )
    print(f"fetched {fetched}, verified and skipped {skipped}")


def load_capacities() -> dict[str, tuple[Decimal | None, Decimal | None]]:
    """Registered capacities from the pinned BM-unit reference vintage."""
    capacities = {}
    for record in load_records(BMUNITS_PATH):
        generation = record.get("generationCapacity")
        demand = record.get("demandCapacity")
        capacities[str(record["elexonBmUnit"])] = (
            Decimal(generation) if generation is not None else None,
            Decimal(demand) if demand is not None else None,
        )
    return capacities


def system_flagged_units(day: str, period: int) -> set[tuple[str, int, str]]:
    """(date, period, unit) for every unit with a system-flagged acceptance."""
    flagged = set()
    for record in load_records(RAW / day / f"boalf_p{period:02d}.json"):
        if bool(record.get("soFlag")):
            flagged.add((day, period, str(record["bmUnit"])))
    return flagged


def select() -> None:
    capacities = load_capacities()
    candidates = []
    deliverability: dict[tuple, str] = {}
    system_flagged: set[tuple[str, int, str]] = set()

    for day in window_dates():
        for period in PERIODS:
            bod_records = load_records(window_path("bod", day, period))
            extremes = {
                dataset: level_extremes(load_records(physical_path(dataset, day, period)))
                for dataset in PHYSICAL_DATASETS
            }
            system_flagged |= system_flagged_units(day, period)
            for direction in DIRECTIONS:
                submitted = submitted_pairs(bod_records, direction)
                accepted = accepted_pairs(
                    load_records(window_path(f"disptav_{direction}", day, period)), direction
                )
                period_candidates = find_inversion_candidates(
                    settlement_date=day,
                    settlement_period=period,
                    direction=direction,
                    submitted=submitted,
                    accepted=accepted,
                )
                for candidate in period_candidates:
                    unit = candidate.unaccepted_unit
                    generation, demand = capacities.get(unit, (None, None))
                    bound = headroom_upper_bound(
                        direction,
                        fpn=extremes["PN"].get(unit),
                        mels=extremes["MELS"].get(unit),
                        mils=extremes["MILS"].get(unit),
                        generation_capacity=generation,
                        demand_capacity=demand,
                    )
                    deliverability[alternative_key(candidate)] = classify(bound)
                candidates.extend(period_candidates)
        print(f"scanned {day}", flush=True)

    surviving, funnel = screen(
        candidates, deliverability=deliverability, system_flagged=system_flagged
    )
    chosen = select_case(surviving)

    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "funnel.json").write_text(
        json.dumps(
            {
                "window": [window_dates()[0], window_dates()[-1]],
                "labelling": (
                    "Naive counterfactual notional is arithmetic on public numbers "
                    "(|accepted volume| x best gap, once per accepted action) — never a "
                    "saving, loss or waste. Screens are Amendment A (deliverability) then "
                    "Amendment B (system-flagged accepted action), in that declared order."
                ),
                "system_flagged_unit_periods": len(system_flagged),
                "stages": funnel.as_dict(),
            },
            indent=1,
        )
        + "\n"
    )
    head = [dataclasses.asdict(c) for c in rank_candidates(surviving)[:50]]
    (EVIDENCE / "candidates-top50.json").write_text(json.dumps(head, indent=1, default=str) + "\n")
    (EVIDENCE / "selected.json").write_text(
        json.dumps(
            {
                "selected": dataclasses.asdict(chosen) if chosen else None,
                "outcome": "selected" if chosen else "no_candidate_survived",
            },
            indent=1,
            default=str,
        )
        + "\n"
    )
    for stage in funnel.stages:
        print(f"{stage.name}: {stage.candidates:,} candidates, {stage.accepted_actions:,} actions")
    if chosen is None:
        print("Selected: none — no candidate survived both screens (declared outcome)")
    else:
        print(
            f"Selected: {chosen.settlement_date} period {chosen.settlement_period} "
            f"{chosen.direction}: {chosen.accepted_unit} accepted while "
            f"{chosen.unaccepted_unit} unaccepted, gap £{chosen.gap_gbp_per_mwh}/MWh"
        )


COMMANDS = {"fetch": fetch, "select": select}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit(f"usage: selection.py [{'|'.join(COMMANDS)}]")
    COMMANDS[sys.argv[1]]()
