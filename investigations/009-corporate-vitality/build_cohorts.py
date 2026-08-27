"""009 step A — build the four cohorts from the TEC archive only (no Companies House).

Writes evidence/cohorts.json. Needs openpyxl/xlrd for the xlsx vintages:
    uv run --with openpyxl --with xlrd python investigations/009-corporate-vitality/build_cohorts.py
"""

import csv
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.investigations.tec_slippage import identity, normalise

sys.path.insert(0, str(REPO_ROOT / "investigations/005-connection-date-credibility"))
import run as r005  # noqa: E402

LATEST = REPO_ROOT / "data/raw/neso/tec_register_2026-08-22.csv"
METRICS = REPO_ROOT / "data/derived/tec-history/project-metrics.csv"
EVIDENCE = Path(__file__).parent / "evidence"
LATEST_DATE = date(2026, 8, 22)
THREE_YEARS_BEFORE = date(2023, 8, 22)
REGIME_START = date(2024, 4, 1)
ADVANCED = {"Built", "Under Construction/Commissioning"}


def stage_mw(row: dict) -> str:
    for k in ("MW Increase / Decrease", "MW Connected", "Cumulative Total Capacity (MW)"):
        try:
            v = abs(Decimal(str(row.get(k) or "").replace(",", "")))
        except Exception:  # noqa: BLE001
            continue
        if v:
            return str(v)
    return "0"


def get(row: dict, needle: str):
    for k in row:
        if k and needle in str(k).lower().replace("_", " "):
            return row[k]
    return None


def main() -> None:
    latest = list(csv.DictReader(LATEST.open()))
    metrics = {}
    for m in csv.DictReader(METRICS.open()):
        metrics.setdefault(m["key"].split("#")[0], []).append(m)

    scoping, built, excluded = [], [], {"scoping_lt3y_or_advanced": 0, "scoping_no_archive": 0}
    for x in latest:
        k = identity(x, use_project_id=False)
        ms = metrics.get(k.split("#")[0], [])
        first = min((m["first_observed"] for m in ms), default=None)
        rec = {
            "key": k,
            "customer": x["Customer Name"],
            "customer_norm": normalise(x["Customer Name"]),
            "mw": stage_mw(x),
            "plant_type": x["Plant Type"],
            "host_to": x["HOST TO"],
            "status": x["Project Status"],
            "first_observed": first or LATEST_DATE.isoformat(),
            "archive_matched": bool(ms),
        }
        if x["Project Status"] == "Scoping":
            if not ms:
                excluded["scoping_no_archive"] += 1
                continue
            m = min(ms, key=lambda m: m["first_observed"])
            if (
                m["first_observed"] <= THREE_YEARS_BEFORE.isoformat()
                and not m["status_transitions"]
            ):
                scoping.append(rec)
            else:
                excluded["scoping_lt3y_or_advanced"] += 1
        elif x["Project Status"] in ADVANCED:
            built.append(rec)

    journal = [
        json.loads(line)
        for line in (r005.RAW / "journal.ndjson").read_text().splitlines()
        if line.strip()
    ]
    by = {}
    for e in journal:
        if e.get("duplicate_of"):
            continue
        d = e["t_public"][:10]
        if d < REGIME_START.isoformat():
            continue
        if d not in by or (e.get("row_count") or 0) > (by[d].get("row_count") or 0):
            by[d] = e
    vintages = []
    for d, e in sorted(by.items()):
        rows = r005.read_vintage(REPO_ROOT / e["path"], e.get("format", ""))
        if rows:
            vintages.append((date.fromisoformat(d), rows))
    seen: dict[tuple[str, str], dict] = {}
    for d, rows in vintages:
        for row in rows:
            pid = str(get(row, "project id") or "").strip()
            if not pid:
                continue
            stat = str(get(row, "project status") or "").strip()
            cust = str(get(row, "customer") or "")
            rec = seen.setdefault(
                (pid, stat), {"project_id": pid, "status": stat, "first_seen": d.isoformat()}
            )
            rec.update(
                last_seen=d.isoformat(),
                customer=cust,
                customer_norm=normalise(cust),
                mw=stage_mw(
                    {
                        "MW Increase / Decrease": get(row, "increase"),
                        "MW Connected": get(row, "connected"),
                        "Cumulative Total Capacity (MW)": get(row, "cumulative"),
                    }
                ),
                plant_type=str(get(row, "plant") or ""),
            )
    last_date, last_rows = vintages[-1]
    present_ids = {str(get(r, "project id") or "").strip() for r in last_rows}
    gone = [
        s
        for (pid, st), s in seen.items()
        if pid not in present_ids
        and st == "Scoping"
        and s["first_seen"] >= REGIME_START.isoformat()
        and s["last_seen"] >= "2024-06-01"
    ]
    for s in gone:
        s["observed_days"] = (
            date.fromisoformat(s["last_seen"]) - date.fromisoformat(s["first_seen"])
        ).days
    gone_scored = [s for s in gone if s["observed_days"] >= 180]
    gone_short = [s for s in gone if s["observed_days"] < 180]
    present = sorted(
        (
            s
            for (pid, st), s in seen.items()
            if pid in present_ids and st == "Scoping" and s["last_seen"] == last_date.isoformat()
        ),
        key=lambda s: (s["customer_norm"], s["project_id"]),
    )
    control = present[::6][:150]

    EVIDENCE.mkdir(exist_ok=True)
    out = {
        "built_from": {
            "latest_register": LATEST.name,
            "metrics": METRICS.name,
            "regime_vintages": [d.isoformat() for d, _ in vintages],
        },
        "arms": {
            "scoping_3y": scoping,
            "built_uc": built,
            "gone_scoping": gone_scored,
            "gone_scoping_short": gone_short,
            "control_present_scoping": control,
        },
        "excluded": excluded,
    }
    (EVIDENCE / "cohorts.json").write_text(json.dumps(out, indent=1) + "\n")
    for name, arm in out["arms"].items():
        print(
            name,
            len(arm),
            "stages",
            f"{sum(Decimal(s['mw']) for s in arm):,.0f}",
            "MW",
            len({s["customer_norm"] for s in arm}),
            "customers",
        )
    print("excluded", excluded)


if __name__ == "__main__":
    main()
