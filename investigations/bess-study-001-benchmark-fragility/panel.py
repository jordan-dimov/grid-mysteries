"""BESS Study 001 panel step: the declared, unit-blind coverage rule.

A candidate is any unit with an MDO or MDB record in the pinned July
streams. A unit enters the panel iff at least 80% of July's settlement
periods are reconstructable (full-period envelope coverage under
hindsight vintages, per ``duration_envelope``) in BOTH directions.
Settlement periods follow the GB local day (BST in July), so period 1 of
date D starts at D 00:00 Europe/London.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from bench import EVIDENCE, MDX_RAW, REPO_ROOT, day_stream_url, july_dates, stream_dates

from grid_mysteries.corpus import load_records
from grid_mysteries.investigations.duration_envelope import EnvelopeRecord, energy_bound_mwh
from grid_mysteries.sources import elexon
from grid_mysteries.sources.pinning import fetch_journalled

LONDON = ZoneInfo("Europe/London")
PANEL_THRESHOLD = Decimal("0.8")  # displays the governed value; see METHOD-STUDY-BESS-001.md
PERIODS_IN_JULY = 31 * 48
PHYSICAL_RAW = REPO_ROOT / "data" / "raw" / "elexon" / "physical-2026-07"


def period_window(settlement_date: str, period: int) -> tuple[datetime, datetime]:
    local_midnight = datetime.fromisoformat(settlement_date).replace(tzinfo=LONDON)
    start = local_midnight + timedelta(minutes=30 * (period - 1))
    return start, start + timedelta(minutes=30)


def load_envelopes() -> dict[tuple[str, str], list[EnvelopeRecord]]:
    """(unit, dataset) -> records, from every pinned MDX stream file."""
    envelopes: dict[tuple[str, str], list[EnvelopeRecord]] = {}
    for dataset in ("MDO", "MDB"):
        for day in stream_dates():
            for r in load_records(MDX_RAW / f"{dataset.lower()}_{day}.json"):
                envelopes.setdefault((str(r["bmUnit"]), dataset), []).append(
                    EnvelopeRecord(
                        time_from=datetime.fromisoformat(r["timeFrom"]),
                        time_to=datetime.fromisoformat(r["timeTo"]),
                        level_from=Decimal(str(r["levelFrom"]))
                        if not isinstance(r["levelFrom"], Decimal)
                        else r["levelFrom"],
                        level_to=Decimal(str(r["levelTo"]))
                        if not isinstance(r["levelTo"], Decimal)
                        else r["levelTo"],
                        publish_time=datetime.fromisoformat(r["publishTime"]),
                        serial_number=str(r["serialNumber"]),
                    )
                )
    return envelopes


def reconstructable_periods(records: list[EnvelopeRecord]) -> int:
    ordered = sorted(records, key=lambda r: r.time_from)
    count = 0
    for day in july_dates():
        for period in range(1, 49):
            start, end = period_window(day, period)
            relevant = [r for r in ordered if r.time_from < end and r.time_to > start]
            if relevant and energy_bound_mwh(relevant, start, end, None) is not None:
                count += 1
    return count


def run_panel() -> None:
    envelopes = load_envelopes()
    units = sorted({unit for unit, _ in envelopes})
    rows = []
    for unit in units:
        offer_ok = reconstructable_periods(envelopes.get((unit, "MDO"), []))
        bid_ok = reconstructable_periods(envelopes.get((unit, "MDB"), []))
        coverage_offer = Decimal(offer_ok) / Decimal(PERIODS_IN_JULY)
        coverage_bid = Decimal(bid_ok) / Decimal(PERIODS_IN_JULY)
        rows.append(
            {
                "bm_unit": unit,
                "reconstructable_offer": offer_ok,
                "reconstructable_bid": bid_ok,
                "coverage_offer": str(coverage_offer),
                "coverage_bid": str(coverage_bid),
                "in_panel": coverage_offer >= PANEL_THRESHOLD and coverage_bid >= PANEL_THRESHOLD,
            }
        )
        print(
            f"{unit}: offer {offer_ok}/{PERIODS_IN_JULY}, bid {bid_ok}/{PERIODS_IN_JULY}"
            f" -> {'IN' if rows[-1]['in_panel'] else 'out'}",
            flush=True,
        )
    panel = [r["bm_unit"] for r in rows if r["in_panel"]]
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "panel.json").write_text(
        json.dumps(
            {
                "rule": "coverage >= 0.8 of July periods reconstructable in BOTH directions",
                "periods_in_july": PERIODS_IN_JULY,
                "candidates": rows,
                "panel": panel,
            },
            indent=1,
        )
        + "\n"
    )
    print(f"panel: {panel}")


def fetch_physical() -> None:
    panel = json.loads((EVIDENCE / "panel.json").read_text())["panel"]
    if not panel:
        print("empty panel; nothing to fetch")
        return
    jobs = [
        (
            dataset,
            day_stream_url(dataset, day, panel),
            PHYSICAL_RAW / f"{dataset.lower()}_{day}.json",
        )
        for dataset in ("PN", "MELS", "MILS")
        for day in july_dates()
    ]
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=EVIDENCE / "physical-july-journal.ndjson",
        manifest_path=EVIDENCE / "physical-july-manifest.json",
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
    )
    print(f"fetched {fetched}, verified and skipped {skipped}")
