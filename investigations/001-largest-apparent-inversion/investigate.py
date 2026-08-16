"""Pin and reduce the case evidence for Mystery 001 (2026-08-06 SP29, bids).

Usage:
    uv run python investigations/001-largest-apparent-inversion/investigate.py fetch
    uv run python investigations/001-largest-apparent-inversion/investigate.py report

``fetch`` pins the case-specific artefacts (PN, MELS, BOALF, bid stack,
BM Unit reference) under the same immutability rules as the selection
data, journalled in ``evidence/case-fetch-journal.ndjson`` and summarised
in ``evidence/case-manifest.json``. ``report`` is offline: it reduces the
pinned case artefacts plus the already-pinned window artefacts to the
facts needed by EXPLANATION-PROTOCOL.md and writes
``evidence/case-report.json``. Interpretation happens in the README, not
here; this script only extracts records.
"""

from __future__ import annotations

import json
import sys
import time
from decimal import Decimal
from pathlib import Path

from selection import artefact_paths, load_records, window_dates

from grid_mysteries.hashing import sha256_file
from grid_mysteries.sources import elexon

REPO_ROOT = Path(__file__).resolve().parents[2]
CASE_RAW = REPO_ROOT / "data" / "raw" / "elexon" / "case-001"
EVIDENCE = Path(__file__).resolve().parent / "evidence"
JOURNAL = EVIDENCE / "case-fetch-journal.ndjson"

CASE_DATE = "2026-08-06"
CASE_PERIOD = 29
ACCEPTED_UNIT = "T_LARYW-1"
UNACCEPTED_UNIT = "E_RHEI-1"

CASE_ARTEFACTS = [
    (
        "PN",
        f"{elexon.BASE_URL}/balancing/physical/all"
        f"?dataset=PN&settlementDate={CASE_DATE}&settlementPeriod={CASE_PERIOD}",
        CASE_RAW / "pn_p29.json",
    ),
    (
        "MELS",
        f"{elexon.BASE_URL}/balancing/physical/all"
        f"?dataset=MELS&settlementDate={CASE_DATE}&settlementPeriod={CASE_PERIOD}",
        CASE_RAW / "mels_p29.json",
    ),
    (
        "BOALF",
        f"{elexon.BASE_URL}/balancing/acceptances/all"
        f"?settlementDate={CASE_DATE}&settlementPeriod={CASE_PERIOD}",
        CASE_RAW / "boalf_p29.json",
    ),
    (
        "BID-STACK",
        f"{elexon.BASE_URL}/balancing/settlement/stack/all/bid/{CASE_DATE}/{CASE_PERIOD}",
        CASE_RAW / "stack_bid_p29.json",
    ),
    (
        "BMUNITS",
        f"{elexon.BASE_URL}/reference/bmunits/all",
        CASE_RAW / "bmunits.json",
    ),
]


def fetch() -> None:
    EVIDENCE.mkdir(exist_ok=True)
    journal = {}
    if JOURNAL.exists():
        for line in JOURNAL.read_text().splitlines():
            if line.strip():
                entry = json.loads(line)
                journal[entry["path"]] = entry
    with JOURNAL.open("a") as journal_out:
        for dataset, url, destination in CASE_ARTEFACTS:
            relative_path = str(destination.relative_to(REPO_ROOT))
            if destination.exists():
                entry = journal.get(relative_path)
                if entry is None or sha256_file(destination) != entry["sha256"]:
                    raise RuntimeError(f"{relative_path} exists but fails journal verification")
                continue
            artefact = elexon.fetch_pinned(url=url, destination=destination, dataset=dataset)
            entry = {
                "source": artefact.source,
                "dataset": dataset,
                "url": url,
                "path": relative_path,
                "sha256": artefact.sha256,
                "fetched_at": artefact.fetched_at.isoformat(),
                "bytes": destination.stat().st_size,
            }
            journal_out.write(json.dumps(entry) + "\n")
            journal_out.flush()
            journal[relative_path] = entry
            time.sleep(0.1)
    manifest = sorted(journal.values(), key=lambda entry: entry["path"])
    (EVIDENCE / "case-manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"case manifest: {len(manifest)} artefacts")


def _records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(), parse_float=Decimal)
    return payload["data"] if isinstance(payload, dict) else payload


def report() -> None:
    pn = [r for r in _records(CASE_RAW / "pn_p29.json") if r["bmUnit"] == UNACCEPTED_UNIT]
    mels = [r for r in _records(CASE_RAW / "mels_p29.json") if r["bmUnit"] == UNACCEPTED_UNIT]
    boalf = [
        r
        for r in _records(CASE_RAW / "boalf_p29.json")
        if r["bmUnit"] in (ACCEPTED_UNIT, UNACCEPTED_UNIT)
    ]
    stack = [r for r in _records(CASE_RAW / "stack_bid_p29.json") if r["id"] in (ACCEPTED_UNIT,)]
    reference = {
        r["elexonBmUnit"]: {
            key: r.get(key)
            for key in (
                "bmUnitName",
                "leadPartyName",
                "fuelType",
                "bmUnitType",
                "gspGroupId",
                "gspGroupName",
                "generationCapacity",
                "demandCapacity",
                "fpnFlag",
            )
        }
        for r in _records(CASE_RAW / "bmunits.json")
        if r["elexonBmUnit"] in (ACCEPTED_UNIT, UNACCEPTED_UNIT)
    }

    # Week-wide behaviour of the unaccepted unit, from the already-pinned
    # window artefacts: submitted bid prices/levels and accepted volumes.
    bid_prices: dict[str, int] = {}
    level_bands: dict[str, int] = {}
    periods_submitted = 0
    accepted_rows = []
    for settlement_date in window_dates():
        for period in range(1, 49):
            paths = artefact_paths(settlement_date, period)
            bods = [
                r
                for r in load_records(paths["bod"])
                if r["bmUnit"] == UNACCEPTED_UNIT and int(r["pairId"]) < 0
            ]
            if bods:
                periods_submitted += 1
            for r in bods:
                bid_prices[str(r["bid"])] = bid_prices.get(str(r["bid"]), 0) + 1
                band = f"{r['levelFrom']}..{r['levelTo']}"
                level_bands[band] = level_bands.get(band, 0) + 1
            for r in load_records(paths["disptav_bid"]):
                if (
                    r["bmUnit"] == UNACCEPTED_UNIT
                    and r.get("dataType") == "Original"
                    and r.get("totalVolumeAccepted")
                ):
                    accepted_rows.append(
                        {
                            "settlement_date": settlement_date,
                            "settlement_period": period,
                            "total_volume_accepted": r["totalVolumeAccepted"],
                        }
                    )

    result = {
        "case": {
            "settlement_date": CASE_DATE,
            "settlement_period": CASE_PERIOD,
            "direction": "bid",
        },
        "reference": reference,
        "unaccepted_unit_pn_sp29": pn,
        "unaccepted_unit_mels_sp29": mels,
        "boalf_sp29_both_units": boalf,
        "bid_stack_sp29_accepted_unit": stack,
        "unaccepted_unit_week": {
            "periods_with_bid_pairs_submitted": periods_submitted,
            "distinct_bid_prices_with_counts": bid_prices,
            "distinct_level_bands_with_counts": level_bands,
            "disptav_original_accepted_bid_rows": accepted_rows,
        },
    }
    (EVIDENCE / "case-report.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    print(json.dumps(result, indent=1, default=str))


def main() -> None:
    match sys.argv[1:]:
        case ["fetch"]:
            fetch()
        case ["report"]:
            report()
        case _:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
