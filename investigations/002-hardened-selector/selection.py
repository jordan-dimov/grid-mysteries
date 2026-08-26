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

import dataclasses
import sys
from datetime import date
from decimal import Decimal

from grid_mysteries.corpus import (
    DIRECTIONS,
    PERIODS,
    REPO_ROOT,
    day_range,
    load_records,
    physical_path,
    registered_capacities,
    window_path,
)
from grid_mysteries.evidence import evidence_dir, write_json
from grid_mysteries.governance import require_acquisition_authorised
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
from grid_mysteries.sources.elexon import PHYSICAL_DATASETS
from grid_mysteries.sources.pinning import pin, progress

EVIDENCE = evidence_dir(__file__)

#: The reserved window, fixed by prior commitment (see README.md).
WINDOW_START = date(2026, 8, 11)
WINDOW_DAYS = 7

INQUIRY = "inq-002"
V2_PROGRAMME = str(REPO_ROOT / "morpholog" / "research-v2-draft.morph")

#: The declared Decimal parameters. These can change which evidence is
#: selected, so the governed record holds their one authoritative value
#: (RESEARCH-V2-DESIGN.md item 8) and analysis reads it from there —
#: never from a module default, never from prose.
PARAM_MIN_ACCEPTED_MWH = "min_accepted_volume_mwh"
PARAM_MIN_AVAILABLE_MW = "min_available_level_mw"


def window_dates() -> list[str]:
    return day_range(WINDOW_START, WINDOW_DAYS)


def governed_thresholds() -> tuple[Decimal, Decimal]:
    """The sealed selection thresholds, read from the governed record.

    Refuses rather than defaulting: a run that cannot see the governed
    value must not quietly substitute the module constant.
    """
    import os

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "refusing to select: DATABASE_URL is unset, so the sealed thresholds "
            "cannot be read. Declared parameters are authoritative, not code defaults."
        )
    from grid_mysteries.governance import declared_parameter
    from morpholog_client import open_session

    with open_session(V2_PROGRAMME, database_url) as session:
        return (
            declared_parameter(session, INQUIRY, PARAM_MIN_ACCEPTED_MWH),
            declared_parameter(session, INQUIRY, PARAM_MIN_AVAILABLE_MW),
        )


def fetch() -> None:
    require_acquisition_authorised(INQUIRY)
    jobs = [job for day in window_dates() for job in elexon.period_jobs(day, PERIODS)]
    pin(
        jobs,
        journal_path=EVIDENCE / "fetch-journal.ndjson",
        manifest_path=EVIDENCE / "manifest.json",
        fetch=elexon.fetch_pinned,
        progress=progress,
    )


def system_flagged_units(day: str, period: int) -> set[tuple[str, int, str]]:
    """(date, period, unit) for every unit with a system-flagged acceptance."""
    flagged = set()
    for record in load_records(window_path("boalf", day, period)):
        if bool(record.get("soFlag")):
            flagged.add((day, period, str(record["bmUnit"])))
    return flagged


def scan(min_accepted_mwh: Decimal, min_available_mw: Decimal):
    """One pass over the pinned window: candidates, deliverability, flags.

    Shared by `select` and the post-selection cross-check so both see the
    identical candidate set; the screens themselves live in
    `grid_mysteries.investigations.hardened_selection`.
    """
    capacities = registered_capacities()
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
                    min_accepted_mwh=min_accepted_mwh,
                    min_available_mw=min_available_mw,
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
    return candidates, deliverability, system_flagged


def select() -> None:
    min_accepted_mwh, min_available_mw = governed_thresholds()
    print(
        f"governed thresholds: {PARAM_MIN_ACCEPTED_MWH}={min_accepted_mwh}, "
        f"{PARAM_MIN_AVAILABLE_MW}={min_available_mw}",
        flush=True,
    )
    candidates, deliverability, system_flagged = scan(min_accepted_mwh, min_available_mw)
    surviving, funnel = screen(
        candidates, deliverability=deliverability, system_flagged=system_flagged
    )
    chosen = select_case(surviving)

    write_json(
        EVIDENCE / "funnel.json",
        {
            "window": [window_dates()[0], window_dates()[-1]],
            "governed_parameters": {
                PARAM_MIN_ACCEPTED_MWH: str(min_accepted_mwh),
                PARAM_MIN_AVAILABLE_MW: str(min_available_mw),
            },
            "labelling": (
                "Naive counterfactual notional is arithmetic on public numbers "
                "(|accepted volume| x best gap, once per accepted action) — never a "
                "saving, loss or waste. Screens are Amendment A (deliverability) then "
                "Amendment B (system-flagged accepted action), in that declared order."
            ),
            "system_flagged_unit_periods": len(system_flagged),
            "stages": funnel.as_dict(),
        },
    )
    head = [dataclasses.asdict(c) for c in rank_candidates(surviving)[:50]]
    write_json(EVIDENCE / "candidates-top50.json", head)
    write_json(
        EVIDENCE / "selected.json",
        {
            "selected": dataclasses.asdict(chosen) if chosen else None,
            "outcome": "selected" if chosen else "no_candidate_survived",
        },
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
