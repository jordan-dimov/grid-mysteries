"""Investigation 004: acquire the June window and select the half-hour.

    uv run python investigations/004-most-expensive-half-hour/acquire.py costs
    uv run python investigations/004-most-expensive-half-hour/acquire.py select
    uv run python investigations/004-most-expensive-half-hour/acquire.py day

Acquisition is two-phase by design. `costs` pins only the small
selection input (NESO's settlement-period cost series) and its declared
companions; `select` then applies the frozen rule offline; `day` pins the
deep Elexon record for the selected settlement day. Fetching a whole
month of per-period market data to choose one half-hour would be waste,
and would expose far more of the window than the declaration needs.

Both fetch phases are gated on the governed record: they refuse without
`ProtocolSealed(inq-004)`, because the human seal is the only emitter of
`DataAcquisitionAuthorised`.

Built blind: the selection logic lives in
`grid_mysteries.investigations.period_costs` and was written and tested
against synthetic fixtures before any June row was read.
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from functools import partial
from pathlib import Path

from grid_mysteries.corpus import DIRECTIONS, PERIODS, REPO_ROOT, physical_path, window_path
from grid_mysteries.governance import require_acquisition_authorised
from grid_mysteries.investigations.period_costs import (
    CONSTRAINTS_COLUMN,
    parse_cost_rows,
    select_most_expensive,
)
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.http import fetch_artifact
from grid_mysteries.sources.pinning import fetch_journalled

EVIDENCE = Path(__file__).resolve().parent / "evidence"
RAW = REPO_ROOT / "data" / "raw" / "elexon"
INQUIRY = "inq-004"

WINDOW_START = date(2026, 6, 1)
WINDOW_DAYS = 30
PHYSICAL_DATASETS = ("PN", "MELS", "MILS")

#: Declared selection input and its companions (NESO data-portal resources).
SELECTION_INPUTS = [
    (
        "NESO-DAILY-BALANCING-COSTS-26-27",
        "1d040751-f77f-4641-9130-d49f8cbfe54f",
        "daily_balancing_costs_2026-27.csv",
    ),
    (
        "NESO-DAILY-BALANCING-VOLUME-26-27",
        "e781da74-6c35-4296-81dd-250cee869c19",
        "daily_balancing_volume_2026-27.csv",
    ),
    (
        "NESO-DISAGGREGATED-BSAD-26-27",
        "2be1a4d1-6b10-4c62-a01c-924942a3748f",
        "disaggregated_bsad_2026-27.csv",
    ),
]


def window_dates() -> list[str]:
    return [(WINDOW_START + timedelta(days=day)).isoformat() for day in range(WINDOW_DAYS)]


def neso_fetch(**kwargs):
    return fetch_artifact(source=neso.SOURCE, timeout_seconds=300.0, **kwargs)


def costs() -> None:
    """Phase A: pin the selection input and its declared companions."""
    require_acquisition_authorised(INQUIRY)
    EVIDENCE.mkdir(exist_ok=True)
    jobs = [
        (dataset, neso.dump_url(resource), neso.NESO_RAW / filename)
        for dataset, resource, filename in SELECTION_INPUTS
    ]
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "neso-journal.ndjson",
        manifest_path=EVIDENCE / "neso-manifest.json",
        repo_root=REPO_ROOT,
        fetch=partial(neso_fetch),
        sleep_seconds=0.5,
        progress=lambda path: print(f"pinned {path}", flush=True),
    )
    print(f"selection inputs: fetched {fetched}, verified and skipped {skipped}")


def select() -> None:
    """Apply the frozen rule offline: highest published Constraints value."""
    window = set(window_dates())
    rows = neso.read_csv("daily_balancing_costs_2026-27.csv")
    costs_parsed = parse_cost_rows(rows)
    chosen = select_most_expensive(costs_parsed, window)
    in_window = [c for c in costs_parsed if c.settlement_date in window]
    published = [c for c in in_window if c.constraints_gbp is not None]

    result = {
        "labelling": (
            "'Most expensive' means the highest published Constraints category value "
            "for a settlement period, nothing more. The category split is NESO's own "
            "attribution; no cost here is attributed to a boundary, unit or action."
        ),
        "window": [window_dates()[0], window_dates()[-1]],
        "periods_in_window": len(in_window),
        "periods_with_a_published_constraints_value": len(published),
        "selected": None
        if chosen is None
        else {
            "settlement_date": chosen.settlement_date,
            "settlement_period": chosen.settlement_period,
            "constraints_gbp": str(chosen.constraints_gbp),
            "all_categories_gbp": {k: str(v) for k, v in chosen.categories.items()},
        },
    }
    (EVIDENCE / "selected-period.json").write_text(json.dumps(result, indent=1) + "\n")
    if chosen is None:
        print("Selected: none — no June period carries a published Constraints value")
        return
    print(f"periods in window: {len(in_window)} ({len(published)} with a published value)")
    print(
        f"Selected: {chosen.settlement_date} settlement period "
        f"{chosen.settlement_period} — {CONSTRAINTS_COLUMN} £{chosen.constraints_gbp:,.0f}"
    )


def day() -> None:
    """Phase B: pin the deep Elexon record for the selected settlement day."""
    require_acquisition_authorised(INQUIRY)
    selected = json.loads((EVIDENCE / "selected-period.json").read_text())["selected"]
    if selected is None:
        raise SystemExit("no period selected; run `select` first")
    target = selected["settlement_date"]
    jobs = []
    for period in PERIODS:
        jobs.append(
            ("BOD", elexon.bid_offer_url(target, period), window_path("bod", target, period))
        )
        for direction in DIRECTIONS:
            jobs.append(
                (
                    "DISPTAV",
                    elexon.acceptance_volumes_url(direction, target, period),
                    window_path(f"disptav_{direction}", target, period),
                )
            )
        jobs.append(
            (
                "BOALF",
                f"{elexon.BASE_URL}/balancing/acceptances/all"
                f"?settlementDate={target}&settlementPeriod={period}",
                RAW / target / f"boalf_p{period:02d}.json",
            )
        )
        for dataset in PHYSICAL_DATASETS:
            jobs.append(
                (
                    dataset,
                    f"{elexon.BASE_URL}/balancing/physical/all"
                    f"?dataset={dataset}&settlementDate={target}&settlementPeriod={period}",
                    physical_path(dataset, target, period),
                )
            )
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "day-journal.ndjson",
        manifest_path=EVIDENCE / "day-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
        progress=lambda path: print(f"pinned {path}", flush=True),
    )
    print(f"{target}: fetched {fetched}, verified and skipped {skipped}")


COMMANDS = {"costs": costs, "select": select, "day": day}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit(f"usage: acquire.py [{'|'.join(COMMANDS)}]")
    COMMANDS[sys.argv[1]]()
