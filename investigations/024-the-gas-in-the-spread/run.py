# ruff: noqa: E501
"""024 — The gas in the spread: gated runner.

    uv run --group registers python investigations/024-the-gas-in-the-spread/run.py --phase acquire
    uv run --group registers python investigations/024-the-gas-in-the-spread/run.py --phase schema
    uv run --group registers python investigations/024-the-gas-in-the-spread/run.py --phase format
    uv run --group registers python investigations/024-the-gas-in-the-spread/run.py --phase compute --seal <prefix>
    uv run --group registers python investigations/024-the-gas-in-the-spread/run.py --phase render
    uv run --group registers --with matplotlib python investigations/024-the-gas-in-the-spread/run.py --phase figures

- ``acquire`` pins the two source files once (NESO N2EX day-ahead dump,
  ONS daily SAP workbook) under ``data/raw/<publisher>/024/`` with a
  journal and ``evidence/sources-manifest.json`` (digests, fetch times);
  a pinned file is never refetched or overwritten.
- ``schema`` (before any declaration) supplements the archive schema
  reports with the facts the day rule needs and no value: rows per printed
  date, the distinct period labels, duplicate keys, date ranges.
- ``format`` profiles each pinned file's format as the readers depend on it
  (encoding, byte-order mark, header, field counts, sheet names) against
  the schema pass, reading no value, into ``evidence/format-check.json``.
- ``compute`` (under the frozen DECLARATION.md) reads pinned bytes only,
  each checked against the manifest, and writes ``evidence/days.ndjson``
  (append-only: a committed line that would change stops the run) and
  ``evidence/results.json``; ``render`` writes RESULTS.md; ``figures``
  draws the charts (out of git) and ``figures/captions.md``.
"""

import argparse
import csv
import hashlib
import html as html_lib
import json
import re
import sys
from collections import Counter
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import jsonable, write_json
from grid_mysteries.investigations import gas_in_the_spread as gs
from grid_mysteries.sources import (
    catalyst_report,
    n2ex_day_ahead,
    ofgem_wmi,
    ons_sap,
    ukets_monthly,
)
from grid_mysteries.sources.http import fetch_artifact
from grid_mysteries.sources.pinning import pin, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
DECLARATION = HERE / "DECLARATION.md"
ACQUISITION_LOG = EVIDENCE / "acquisition-log.json"
SOURCES_JOURNAL = EVIDENCE / "sources-journal.ndjson"
SOURCES_MANIFEST = EVIDENCE / "sources-manifest.json"
FORMAT_CHECK = EVIDENCE / "format-check.json"
RUN_LOG = EVIDENCE / "run-log.json"
ARCHIVE_POWER = REPO_ROOT / "archives" / "024-n2ex-day-ahead"
ARCHIVE_GAS = REPO_ROOT / "archives" / "024-ons-sap-gas"
ARCHIVE_CARBON = REPO_ROOT / "archives" / "024-govuk-ukets-monthly-prices"

FETCH_DATE = "2026-10-15"
POWER_RESOURCE = "4f27eea5-7038-4f73-9740-e3e4ad47c26a"
POWER_URL = f"https://api.neso.energy/datastore/dump/{POWER_RESOURCE}"
POWER_FILE = REPO_ROOT / "data" / "raw" / "neso" / "024" / f"n2ex-day-ahead-dump-{FETCH_DATE}.csv"
GAS_EDITION = "systemaveragepriceofgasdataset151026.xlsx"
GAS_URL = (
    "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/"
    f"systemaveragepricesapofgas/2026/{GAS_EDITION}"
)
GAS_FILE = REPO_ROOT / "data" / "raw" / "ons" / "024" / GAS_EDITION
CARBON_URL = (
    "https://www.gov.uk/government/publications/taking-part-in-the-uk-emissions-trading-scheme-markets/"
    "cost-containment-mechanism-ccm-trigger-prices-and-average-monthly-prices-full-table"
)
CARBON_FILE = (
    REPO_ROOT
    / "data"
    / "raw"
    / "govuk"
    / "024"
    / "ccm-trigger-prices-and-average-monthly-prices-full-table-2026-10-15.html"
)
POWER_META_URL = f"https://api.neso.energy/api/3/action/resource_show?id={POWER_RESOURCE}"
POWER_META_FILE = (
    REPO_ROOT
    / "data"
    / "raw"
    / "neso"
    / "024"
    / f"resource-show-{POWER_RESOURCE}-{FETCH_DATE}.json"
)
GAS_PAGE_URL = "https://www.ons.gov.uk/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas"
GAS_PAGE_FILE = (
    REPO_ROOT
    / "data"
    / "raw"
    / "ons"
    / "024"
    / f"systemaveragepricesapofgas-dataset-page-{FETCH_DATE}.html"
)
CARBON_GUIDE_URL = (
    "https://www.gov.uk/government/publications/uk-emissions-trading-scheme-markets/"
    "uk-emissions-trading-scheme-markets"
)
CARBON_GUIDE_FILE = (
    REPO_ROOT
    / "data"
    / "raw"
    / "govuk"
    / "024"
    / f"uk-emissions-trading-scheme-markets-{FETCH_DATE}.html"
)
OFGEM_CHART_KEY = "YFsS4g98P"
OFGEM_CHART_URL = f"https://app.everviz.com/inject/{OFGEM_CHART_KEY}"
OFGEM_CHART_FILE = (
    REPO_ROOT
    / "data"
    / "raw"
    / "ofgem"
    / "024"
    / f"wmi-gas-day-ahead-monthly-everviz-inject-{OFGEM_CHART_KEY}-{FETCH_DATE}.js"
)
OFGEM_PAGE_URL = (
    "https://www.ofgem.gov.uk/energy-data-and-research/data-portal/wholesale-market-indicators"
)
OFGEM_PAGE_FILE = (
    REPO_ROOT
    / "data"
    / "raw"
    / "ofgem"
    / "024"
    / f"wholesale-market-indicators-page-{FETCH_DATE}.html"
)
#: dataset -> (publisher, url, destination). The three data files and, for
#: vintage and licence, the publishers' own metadata pages.
SOURCES = {
    "neso-n2ex-day-ahead": ("neso", POWER_URL, POWER_FILE),
    "ons-sap-gas-daily": ("ons", GAS_URL, GAS_FILE),
    "govuk-ukets-ccm-monthly-average-prices": ("govuk", CARBON_URL, CARBON_FILE),
    "neso-n2ex-day-ahead-resource-metadata": ("neso", POWER_META_URL, POWER_META_FILE),
    "ons-sap-gas-dataset-page": ("ons", GAS_PAGE_URL, GAS_PAGE_FILE),
    "govuk-ukets-markets-guidance": ("govuk", CARBON_GUIDE_URL, CARBON_GUIDE_FILE),
    # Amendment 1 (cross-check): Ofgem's monthly day-ahead gas chart, served by everviz.
    "ofgem-wmi-gas-day-ahead-monthly-chart": ("ofgem", OFGEM_CHART_URL, OFGEM_CHART_FILE),
    "ofgem-wmi-page": ("ofgem", OFGEM_PAGE_URL, OFGEM_PAGE_FILE),
}
ARCHIVE_OFGEM = REPO_ROOT / "archives" / "024-ofgem-gas-day-ahead-monthly"
# Amendment 2 (forward record): Catalyst Commercial's daily report, the only free dated print of the NBP curve found.
CATALYST_URL = (
    "https://www.catalyst-commercial.co.uk/works/uk-energy-market-report-15-october-2026/"
)
CATALYST_FILE = (
    REPO_ROOT / "data" / "raw" / "catalyst" / "024" / "uk-energy-market-report-15-october-2026.html"
)
SOURCES["catalyst-uk-energy-market-report-2026-10-15"] = ("catalyst", CATALYST_URL, CATALYST_FILE)
ARCHIVE_CATALYST = REPO_ROOT / "archives" / "024-catalyst-report-2026-10-15"
AMENDMENT_2 = HERE / "AMENDMENT-2.md"
FORWARD = EVIDENCE / "forward.json"
AMENDMENT_1 = HERE / "AMENDMENT-1.md"
CROSS_CHECK = EVIDENCE / "cross-check.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def log_run(phase: str, **facts: Any) -> None:
    try:
        log = json.loads(RUN_LOG.read_text())
    except OSError, json.JSONDecodeError:
        log = {"runs": []}
    log["runs"].append(
        {"phase": phase, "at": datetime.now(UTC).isoformat(timespec="seconds"), **facts}
    )
    write_json(RUN_LOG, log)


def phase_acquire() -> None:
    """Pin both sources once. Authorised by the sponsor's handover of
    15/10/2026 (etrmbiz notes/2026-10-15-grid-mysteries-prompt-024-gas-in-the-spread.md:
    "to be pinned and schema-reported before the declaration")."""

    def fetch(*, url: str, destination: Path, dataset: str) -> Any:
        publisher = SOURCES[dataset][0]
        return fetch_artifact(
            url=url, destination=destination, source=publisher, dataset=dataset, timeout_seconds=300
        )

    jobs = [(dataset, url, dest) for dataset, (_, url, dest) in SOURCES.items()]
    fetched, skipped = pin(
        jobs,
        journal_path=SOURCES_JOURNAL,
        manifest_path=SOURCES_MANIFEST,
        fetch=fetch,
        label="024 sources",
        progress=progress,
    )
    try:
        log = json.loads(ACQUISITION_LOG.read_text())
    except OSError, json.JSONDecodeError:
        log = {"acquisitions": []}
    log["acquisitions"].append(
        {
            "at": datetime.now(UTC).isoformat(),
            "authorised_by": "sponsor handover 15/10/2026 (etrmbiz notes/2026-10-15-grid-mysteries-prompt-024-gas-in-the-spread.md)",
            "fetched": fetched,
            "verified_and_skipped": skipped,
            "files": {
                d: {"path": str(p.relative_to(REPO_ROOT)), "sha256": sha(p)}
                for d, (_, _, p) in SOURCES.items()
            },
        }
    )
    write_json(ACQUISITION_LOG, log)


def md_table(header: list[str], rows: list[list[Any]]) -> list[str]:
    tidy = lambda v: " ".join(str(v).split())  # noqa: E731
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + [
        "| " + " | ".join(tidy(c) for c in r) + " |" for r in rows
    ]


def cell_form(v: str) -> str:
    """The shape of a printed cell, never its value."""
    v = v.strip()
    if not v:
        return "blank"
    if re.fullmatch(r"£\s?-?\d+(\.\d+)?", v):
        return "pounds-decimal"
    if re.fullmatch(r"-?\d+(\.\d+)?", v):
        return "decimal"
    if re.fullmatch(r"[A-Z][a-z]{2}-\d{2}", v):
        return "mon-yy"
    if re.fullmatch(r"[A-Z][a-z]{2}-\d{2}\s*(to|-|–)\s*[A-Z][a-z]{2}-\d{2}", v):
        return "mon-yy-range"
    if v in ("Yes", "No", "Yes*", "No*"):
        return "yes-no"
    return "text"


def power_day_structure() -> dict[str, Any]:
    """Rows per printed date and the period labels, for the day rule. No price is read."""
    with POWER_FILE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    per_date: dict[str, list[str]] = {}
    for r in rows:
        per_date.setdefault(r["Date"], []).append(r["Delivery Period"])
    labels_in_order: list[str] = []
    for lab in (r["Delivery Period"] for r in rows):
        if lab not in labels_in_order:
            labels_in_order.append(lab)
    counts = Counter(len(v) for v in per_date.values())
    odd = []
    for d in sorted(per_date):
        labs = per_date[d]
        if len(labs) == 24 and len(set(labs)) == 24:
            continue
        c = Counter(labs)
        odd.append(
            {
                "date": d,
                "rows": len(labs),
                "missing_labels": [x for x in labels_in_order if x not in c],
                "repeated_labels": sorted(x for x, n in c.items() if n > 1),
            }
        )
    dup_keys = sum(1 for v in per_date.values() for n in Counter(v).values() if n > 1)
    return {
        "file": str(POWER_FILE.relative_to(REPO_ROOT)),
        "sha256": sha(POWER_FILE),
        "rows": len(rows),
        "columns": list(rows[0].keys()),
        "first_date": min(per_date),
        "last_date": max(per_date),
        "dates": len(per_date),
        "rows_per_date": {str(k): v for k, v in sorted(counts.items())},
        "period_labels_in_first_appearance_order": labels_in_order,
        "dates_not_24_distinct_labels": odd,
        "repeated_date_label_keys": dup_keys,
        "dates_missing_inside_range": [
            d.isoformat()
            for d in (
                date.fromordinal(o)
                for o in range(
                    date.fromisoformat(min(per_date)).toordinal(),
                    date.fromisoformat(max(per_date)).toordinal() + 1,
                )
            )
            if d.isoformat() not in per_date
        ],
    }


def gas_date_structure() -> dict[str, Any]:
    """The daily sheet's dates and cell forms. No price is read."""
    from openpyxl import load_workbook

    wb = load_workbook(GAS_FILE, read_only=True, data_only=True)
    ws = wb["1.Daily SAP Gas"]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(c) for c in rows[4] if c is not None]
    body = [r for r in rows[5:] if any(c is not None for c in r)]
    dates = [r[0] for r in body if isinstance(r[0], datetime | date)]
    iso = sorted(d.date().isoformat() if isinstance(d, datetime) else d.isoformat() for d in dates)
    ordinals = {date.fromisoformat(x).toordinal() for x in iso}
    forms = Counter(
        "blank"
        if r[1] is None
        else "number"
        if isinstance(r[1], int | float)
        else f"text:{r[1]}"
        if str(r[1]).strip() in ("[x]", "[z]", "[c]")
        else "text"
        for r in body
    )
    return {
        "file": str(GAS_FILE.relative_to(REPO_ROOT)),
        "sha256": sha(GAS_FILE),
        "sheet": "1.Daily SAP Gas",
        "header_row": 5,
        "header": header,
        "rows": len(body),
        "rows_with_date_in_column_a": len(dates),
        "first_date": iso[0],
        "last_date": iso[-1],
        "duplicate_dates": len(iso) - len(set(iso)),
        "dates_missing_inside_range": [
            date.fromordinal(o).isoformat()
            for o in range(min(ordinals), max(ordinals) + 1)
            if o not in ordinals
        ],
        "sap_actual_day_cell_forms": dict(forms),
        "times_on_date_cells": sorted(
            {d.strftime("%H:%M:%S") for d in dates if isinstance(d, datetime)}
        ),
    }


def carbon_table_structure() -> dict[str, Any]:
    """The gov.uk page's tables: headers, row labels, monitoring-period strings and cell forms. No price is read."""
    text = CARBON_FILE.read_text(encoding="utf-8")
    body = text[text.find('<div class="govspeak">') :]
    body = body[: body.find("</main>")]
    updated = re.search(r'name="govuk:updated-at" content="([^"]+)"', text)
    published = re.search(r'name="govuk:first-published-at" content="([^"]+)"', text)
    tables = []
    for tb in re.findall(r"<table.*?</table>", body, re.S):
        rows = re.findall(r"<tr.*?</tr>", tb, re.S)
        parsed = [
            [
                html_lib.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)
            ]
            for row in rows
        ]
        header, data = parsed[0], parsed[1:]
        period_col = next(i for i, h in enumerate(header) if "monitoring period" in h)
        price_cols = [i for i, h in enumerate(header) if h.endswith("average price")]
        tables.append(
            {
                "header": header,
                "rows": len(data),
                "first_row_label": data[0][0],
                "last_row_label": data[-1][0],
                "row_label_forms": dict(Counter(cell_form(r[0]) for r in data)),
                "monitoring_period_strings": [r[period_col] for r in data],
                "cells_per_row": dict(Counter(len(r) for r in data)),
                "average_price_cell_forms": dict(
                    Counter(cell_form(r[i]) for r in data for i in price_cols if i < len(r))
                ),
                "trigger_price_cell_forms": dict(Counter(cell_form(r[2]) for r in data)),
            }
        )
    return {
        "file": str(CARBON_FILE.relative_to(REPO_ROOT)),
        "sha256": sha(CARBON_FILE),
        "first_published_at": published.group(1) if published else None,
        "updated_at": updated.group(1) if updated else None,
        "licence_statement_present": "Open Government Licence v3.0" in text,
        "tables": tables,
    }


def phase_schema() -> None:
    """Supplements beside the archive schema reports: the structure the readers depend on, no value."""
    ARCHIVE_CARBON.mkdir(parents=True, exist_ok=True)
    power = power_day_structure()
    write_json(ARCHIVE_POWER / "day-structure.json", power)
    lines = [
        "# Day structure: 024-n2ex-day-ahead",
        "",
        f"`{power['file']}` (SHA-256 `{power['sha256']}`): {power['rows']:,} rows, columns {', '.join(f'`{c}`' for c in power['columns'])}; "
        f"{power['dates']:,} printed dates from {power['first_date']} to {power['last_date']}, none missing inside the range: {not power['dates_missing_inside_range']}. "
        "Written by `run.py --phase schema`; no price is read.",
        "",
        "Rows per printed date: "
        + ", ".join(f"{n} rows on {k} dates" for n, k in power["rows_per_date"].items())
        + ".",
        "",
        f"Period labels, in order of first appearance ({len(power['period_labels_in_first_appearance_order'])}): "
        + ", ".join(f"`{x}`" for x in power["period_labels_in_first_appearance_order"])
        + ".",
        "",
        f"Repeated (date, label) keys: {power['repeated_date_label_keys']}.",
        "",
        "Dates without exactly 24 distinct labels:",
        "",
    ] + md_table(
        ["date", "rows", "missing labels", "repeated labels"],
        [
            [
                o["date"],
                o["rows"],
                ", ".join(o["missing_labels"]) or "none",
                ", ".join(o["repeated_labels"]) or "none",
            ]
            for o in power["dates_not_24_distinct_labels"]
        ],
    )
    (ARCHIVE_POWER / "DAY-STRUCTURE.md").write_text("\n".join(lines) + "\n")

    gas = gas_date_structure()
    write_json(ARCHIVE_GAS / "date-structure.json", gas)
    lines = [
        "# Date structure: 024-ons-sap-gas",
        "",
        f"`{gas['file']}` (SHA-256 `{gas['sha256']}`), sheet `{gas['sheet']}`, header on row {gas['header_row']}: {', '.join(f'`{h}`' for h in gas['header'])}. "
        f"{gas['rows']:,} body rows, {gas['rows_with_date_in_column_a']:,} with a date cell in column A, from {gas['first_date']} to {gas['last_date']}; "
        f"duplicate dates {gas['duplicate_dates']}; dates missing inside the range: {', '.join(gas['dates_missing_inside_range']) or 'none'}; "
        f"times on the date cells: {', '.join(gas['times_on_date_cells'])}. Written by `run.py --phase schema`; no price is read.",
        "",
        "Forms of the `SAP actual day` cells: "
        + ", ".join(f"{k} {v}" for k, v in gas["sap_actual_day_cell_forms"].items())
        + ".",
        "",
    ]
    (ARCHIVE_GAS / "DATE-STRUCTURE.md").write_text("\n".join(lines) + "\n")

    carbon = carbon_table_structure()
    write_json(ARCHIVE_CARBON / "schema-report.json", carbon)
    lines = [
        "# Schema report: 024-govuk-ukets-monthly-prices",
        "",
        f"`{carbon['file']}` (SHA-256 `{carbon['sha256']}`), gov.uk page first published {carbon['first_published_at']}, updated {carbon['updated_at']}; "
        f"Open Government Licence v3.0 statement present: {carbon['licence_statement_present']}. {len(carbon['tables'])} tables. Written by `run.py --phase schema`; no price is read.",
        "",
    ]
    for i, t in enumerate(carbon["tables"]):
        lines += [
            f"## Table {i}: {t['rows']} rows, rows {t['first_row_label']} to {t['last_row_label']}",
            "",
            "Header: " + ", ".join(f"`{h}`" for h in t["header"]) + ".",
            "",
            f"Row label forms: {t['row_label_forms']}; cells per row: {t['cells_per_row']}; trigger price cell forms: {t['trigger_price_cell_forms']}; average price cell forms: {t['average_price_cell_forms']}.",
            "",
            "Monitoring period strings, in row order: "
            + "; ".join(f"`{x}`" for x in t["monitoring_period_strings"])
            + ".",
            "",
        ]
    (ARCHIVE_CARBON / "SCHEMA.md").write_text("\n".join(lines) + "\n")
    log_run(
        "schema",
        power=sha(ARCHIVE_POWER / "day-structure.json"),
        gas=sha(ARCHIVE_GAS / "date-structure.json"),
        carbon=sha(ARCHIVE_CARBON / "schema-report.json"),
    )
    print("schema supplements written")


DAYS = EVIDENCE / "days.ndjson"
RESULTS_JSON = EVIDENCE / "results.json"
RESULTS_MD = HERE / "RESULTS.md"
FIGURES = HERE / "figures"
FETCH = date.fromisoformat(FETCH_DATE)
UNITS = ("printed", "local")
MODO_SEPTEMBER = {"spread": Decimal(122), "gas": Decimal(64)}
#: The scratch figures of 15/10/2026 (prior exposure, never results), for
#: the comparison table etrmbiz checks against.
SCRATCH = [
    ("September 2026 spread", "121.7", "2026-09"),
    ("September 2026 gas", "64.5", "2026-09"),
    ("2026 to 14/10 spread", "77.5", "2026 to date"),
    ("2025 same dates spread", "71.4", "2025 same dates"),
    ("2026 to 14/10 ratio A", "1.79", "2026 to date"),
    ("2025 same dates ratio A", "2.25", "2025 same dates"),
    ("September 2026 ratio A", "1.89", "2026-09"),
    ("September 2025 ratio A", "2.81", "2025-09"),
]
#: The formats the schema pass recorded (archives/024-*); the format check
#: refuses a departure no frozen amendment reads.
EXPECTED_FORMAT: dict[str, Any] = {
    "neso-n2ex-day-ahead": {
        "leading_byte_order_mark": False,
        "carriage_returns": False,
        "header": ["Date", "Delivery Period", "Price"],
        "rows": 44448,
        "field_counts": {"3": 44448},
        "forms": {
            "date": {"iso": 44448, "other": 0},
            "label": {"hour-range": 44448, "other": 0},
            "price": {"decimal-6": 44448, "other": 0},
        },
    },
    "ons-sap-gas-daily": {
        "sheets": ["Cover", "Contents", "Notes", "1.Daily SAP Gas", "2.Monthly SAP Gas"],
        "header_row": 5,
        "header": ["Date", "SAP actual day", "SAP seven-day rolling average"],
        "rows": 3206,
        "forms": {
            "date": {"date-cell": 3206, "other": 0},
            "sap": {"number": 3206, "blank": 0, "other": 0},
        },
    },
    "govuk-ukets-ccm-monthly-average-prices": {
        "tables": [
            {
                "header": [
                    "Month",
                    "2-year reference period",
                    "Trigger price",
                    "3-month monitoring period",
                    "Month 1 average price",
                    "Month 2 average price",
                    "Month 3 average price",
                    "CCM triggered? Yes or No",
                ],
                "rows": 18,
                "row_labels_mon_yy": 18,
                "average_price_forms": {"pounds": 54, "other": 0},
            },
            {
                "header": [
                    "Month",
                    "2-year reference period",
                    "Trigger price",
                    "6-month monitoring period",
                    "Month 1 average price",
                    "Month 2 average price",
                    "Month 3 average price",
                    "Month 4 average price",
                    "Month 5 average price",
                    "Month 6 average price",
                    "CCM triggered? Yes or No",
                ],
                "rows": 51,
                "row_labels_mon_yy": 51,
                "average_price_forms": {"pounds": 285, "other": 21},
            },
        ]
    },
}
PROFILERS = {
    "neso-n2ex-day-ahead": n2ex_day_ahead.format_profile,
    "ons-sap-gas-daily": ons_sap.format_profile,
    "govuk-ukets-ccm-monthly-average-prices": ukets_monthly.format_profile,
}


def differences(expected: Any, actual: Any, at: str = "") -> list[str]:
    if isinstance(expected, dict) and isinstance(actual, dict):
        out = []
        for k in sorted(set(expected) | set(actual)):
            if k not in actual:
                out.append(f"{at}/{k}: missing")
            elif k not in expected:
                out.append(f"{at}/{k}: unexpected")
            else:
                out += differences(expected[k], actual[k], f"{at}/{k}")
        return out
    if isinstance(expected, list) and isinstance(actual, list) and len(expected) == len(actual):
        return [
            d
            for i, (e, a) in enumerate(zip(expected, actual, strict=True))
            for d in differences(e, a, f"{at}[{i}]")
        ]
    return [] if expected == actual else [f"{at}: expected {expected!r}, found {actual!r}"]


def check_manifest() -> dict[str, dict[str, Any]]:
    """C1: every pinned file hashes to its manifest digest."""
    manifest = {e["dataset"]: e for e in json.loads(SOURCES_MANIFEST.read_text())}
    for dataset, (_, _, path) in SOURCES.items():
        if dataset not in manifest:
            sys.exit(f"C1: {dataset} is not in the manifest")
        if sha(path) != manifest[dataset]["sha256"]:
            sys.exit(f"C1: {path} no longer matches its manifest digest")
    return manifest


def format_check() -> dict[str, Any]:
    check_manifest()
    files = {}
    for dataset, profiler in PROFILERS.items():
        path = SOURCES[dataset][2]
        profile = profiler(path)
        files[dataset] = {
            "path": str(path.relative_to(REPO_ROOT)),
            "sha256": sha(path),
            "profile": profile,
            "differences": differences(EXPECTED_FORMAT[dataset], profile),
        }
    report = {
        "checked_at": datetime.now(UTC).isoformat(),
        "expected": EXPECTED_FORMAT,
        "files": files,
    }
    write_json(FORMAT_CHECK, report)
    return report


def phase_format() -> None:
    report = format_check()
    bad = {k: v["differences"] for k, v in report["files"].items() if v["differences"]}
    for k, v in bad.items():
        print(f"format: {k} departs from the schema pass: {v}")
    print(
        f"format check: {len(report['files'])} files, {len(bad)} with differences -> {FORMAT_CHECK.relative_to(REPO_ROOT)}"
    )
    if bad:
        sys.exit(1)


def sealed_declaration(seal: str | None) -> str:
    digest = sha(DECLARATION)
    if not seal or not digest.startswith(seal):
        sys.exit(f"compute needs --seal, the prefix of DECLARATION.md's SHA-256 ({digest[:8]}…)")
    if not (HERE / "DECLARATION.md.timestamps.json").exists():
        sys.exit("DECLARATION.md is not frozen (no proof sidecar)")
    return digest


def day_line(unit: str, r: gs.DayRow) -> dict[str, Any]:
    return {
        "unit": unit,
        "day": r.day,
        "prices": r.prices,
        "spread": r.spread,
        "gas": r.gas,
        "carbon": r.carbon,
        "ccgt": r.ccgt,
        "negative": r.negative,
        "merit_order": r.merit_order,
        "scarcity": r.scarcity,
    }


def append_only(lines: list[dict[str, Any]]) -> tuple[int, int]:
    """C5: an existing line is never changed; new keys are appended."""
    existing: dict[tuple[str, str], str] = {}
    if DAYS.exists():
        for raw in DAYS.read_text().splitlines():
            if raw.strip():
                d = json.loads(raw)
                existing[d["unit"], d["day"]] = raw
    kept = added = 0
    with DAYS.open("a") as out:
        for line in lines:
            text = json.dumps(line, default=jsonable)
            key = (line["unit"], line["day"].isoformat())
            if key in existing:
                if existing[key] != text:
                    sys.exit(
                        f"C5: committed line for {key} would change:\n {existing[key]}\n {text}"
                    )
                kept += 1
            else:
                out.write(text + "\n")
                added += 1
    return kept, added


def phase_compute(seal: str | None) -> None:
    digest = sealed_declaration(seal)
    manifest = check_manifest()
    report = format_check()
    if any(v["differences"] for v in report["files"].values()):
        sys.exit(
            "C2: a pinned file departs from the schema pass's format; see evidence/format-check.json"
        )
    hours = list(n2ex_day_ahead.read(POWER_FILE))
    gas = ons_sap.read(GAS_FILE)
    carbon = ukets_monthly.read(CARBON_FILE)  # C3 inside
    days: dict[str, dict[date, list[Decimal]]] = {u: {} for u in UNITS}
    for h in hours:
        days["printed"].setdefault(h.day, []).append(h.price)
        days["local"].setdefault(gs.local_day(h.day, h.start_hour), []).append(h.price)
    rows = {u: gs.build_rows(days[u], gas, carbon) for u in UNITS}
    for u in UNITS:
        for r in rows[u]:
            if r.negative is not None and r.negative + r.merit_order + r.scarcity != r.spread:  # type: ignore[operator]
                sys.exit(f"C4: legs do not sum to the spread on {u} {r.day}")
    kept, added = append_only([day_line(u, r) for u in UNITS for r in rows[u]])
    last_measured = max(r.day for r in rows["printed"] if r.spread is not None)
    period_list = gs.periods(FETCH, (last_measured.year, last_measured.month))
    results: dict[str, Any] = {
        "declaration_sha256": digest,
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "fetch_date": FETCH,
        "sources": {
            k: {"path": v["path"], "sha256": v["sha256"], "fetched_at": v["fetched_at"]}
            for k, v in manifest.items()
        },
        "format_check": {k: v["differences"] for k, v in report["files"].items()},
        "hours": len(hours),
        "power_dates": {"first": min(days["printed"]), "last": max(days["printed"])},
        "gas_dates": {"first": min(gas), "last": max(gas), "days": len(gas)},
        "carbon_months": {
            "first": f"{min(carbon)[0]}-{min(carbon)[1]:02d}",
            "last": f"{max(carbon)[0]}-{max(carbon)[1]:02d}",
            "months": len(carbon),
            "values": {f"{y}-{m:02d}": v for (y, m), v in sorted(carbon.items())},
        },
        "last_measured_printed_day": last_measured,
        "days_ndjson": {"kept": kept, "added": added},
        "units": {},
    }
    for u in UNITS:
        excluded = [{"day": r.day, "prices": r.prices} for r in rows[u] if r.spread is None]
        results["units"][u] = {
            "days": len(rows[u]),
            "excluded": excluded,
            "periods": {label: gs.summarise(rows[u], a, b) for label, a, b in period_list},
        }
    p = results["units"]["printed"]["periods"]
    r26, r25 = p["2026 to date"]["ratio_of_means"], p["2025 same dates"]["ratio_of_means"]
    sept = p["2026-09"]["spread_mean"]
    results["falsifiers"] = {
        "F1": {
            "ratio_2026_to_date": r26,
            "ratio_2025_same_dates": r25,
            "change": gs.quantise((r26 / r25 - 1) if r26 and r25 else None),
            "fires": gs.f1_fires(r26, r25),
        },
        "F2": {
            "september_2026_spread": sept,
            "published": MODO_SEPTEMBER["spread"],
            "tolerance": Decimal(2),
            "fires": gs.f2_fires(sept),
        },
    }
    s26, s25 = p["2026-09"]["spread_mean"], p["2025-09"]["spread_mean"]
    results["september_year_on_year"] = {
        "2026-09": s26,
        "2025-09": s25,
        "change": gs.quantise(s26 / s25 - 1) if s26 and s25 else None,
        "bloomberg_says": "0.80",
        "modo_45_wider_implies": gs.quantise(Decimal(45) / (s26 - Decimal(45))) if s26 else None,
    }
    results["negative_leg_share_by_year"] = {
        y: p[y]["legs_share"]["negative"] for y in ("2022", "2023", "2024", "2025", "2026 to date")
    }
    results["scratch_comparison"] = [
        {
            "figure": name,
            "scratch": Decimal(value),
            "declared": p[label]["gas_mean"]
            if "gas" in name
            else p[label]["ratio_of_means"]
            if "ratio" in name
            else p[label]["spread_mean"],
            "period": label,
        }
        for name, value, label in SCRATCH
    ]
    write_json(RESULTS_JSON, results)
    log_run(
        "compute",
        seal=seal,
        declaration_sha256=digest,
        results_sha256=sha(RESULTS_JSON),
        days_kept=kept,
        days_added=added,
    )
    f = results["falsifiers"]
    print(
        f"computed under {digest[:8]}…: F1 fires {f['F1']['fires']} (ratio A {r26} vs {r25}), F2 fires {f['F2']['fires']} (September 2026 {sept})"
    )


def fmt(x: Any, places: str = "0.01") -> str:
    if x is None:
        return "—"
    return str(Decimal(str(x)).quantize(Decimal(places), rounding=ROUND_HALF_EVEN))


def pct(x: Any) -> str:
    return (
        "—"
        if x is None
        else f"{(Decimal(str(x)) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_EVEN)} %"
    )


def period_row(label: str, s: dict[str, Any], legs: bool = True) -> list[str]:
    row = [
        label,
        str(s["days_measured"]),
        fmt(s["spread_mean"]),
        str(s["days_with_gas"]),
        fmt(s["gas_mean"]),
        str(s["days_with_both"]),
        fmt(s["ratio_of_means"], "0.001"),
        fmt(s["mean_of_ratios"], "0.001"),
    ]
    if legs:
        row += [
            str(s["days_with_legs"]),
            fmt(s["legs_mean"]["negative"]),
            fmt(s["legs_mean"]["merit_order"]),
            fmt(s["legs_mean"]["scarcity"]),
            pct(s["legs_share"]["negative"]),
            pct(s["legs_share"]["merit_order"]),
            pct(s["legs_share"]["scarcity"]),
        ]
    return row


PERIOD_HEADER = [
    "period",
    "days measured",
    "spread mean GBP/MWh",
    "days with gas",
    "gas mean GBP/MWh",
    "days with both",
    "ratio A",
    "ratio B",
    "days with legs",
    "negative leg",
    "merit-order leg",
    "scarcity leg",
    "negative share",
    "merit-order share",
    "scarcity share",
]


def excluded_text(excluded: list[dict[str, Any]]) -> str:
    return ", ".join(f"{e['day']} ({e['prices']} prices)" for e in excluded) or "none"


def phase_render() -> None:
    R = json.loads(RESULTS_JSON.read_text())
    P = R["units"]["printed"]["periods"]
    L = R["units"]["local"]["periods"]
    f1, f2 = R["falsifiers"]["F1"], R["falsifiers"]["F2"]
    yoy = R["september_year_on_year"]
    years = ["2022", "2023", "2024", "2025", "2026 to date", "2025 same dates"]
    months = [k for k in P if len(k) == 7]
    lines = (
        [
            "# 024 — The gas in the spread: Results",
            "",
            f"Computed {R['computed_at'][:10]} under the frozen declaration `{R['declaration_sha256'][:8]}…` (`DECLARATION.md`, proofs beside it) from the files pinned 15/10/2026 (`evidence/sources-manifest.json`). "
            f'Method: Julien Jomaux\'s for Germany (GEM Energy Analytics, "The evolution of the spread: 2026 update", 24/09/2026), carried to Great Britain with attribution. '
            f"Power: NESO N2EX GB day-ahead hourly price, {R['hours']:,} hours from {R['power_dates']['first']} to {R['power_dates']['last']}. Gas: ONS daily SAP times ten, {R['gas_dates']['days']:,} days to {R['gas_dates']['last']}. "
            f"Carbon: gov.uk UK ETS monthly average UKA price, {R['carbon_months']['months']} months {R['carbon_months']['first']} to {R['carbon_months']['last']}, plus Carbon Price Support GBP 18/t. Every figure is a simple mean over the days counted beside it; ratios are 3 d.p., money 2 d.p.",
            "",
            "## Falsifiers",
            "",
            f"- **F1** ({'FIRES' if f1['fires'] else 'does not fire'}): ratio A for 2026 to date {fmt(f1['ratio_2026_to_date'], '0.001')} against {fmt(f1['ratio_2025_same_dates'], '0.001')} for the same dates of 2025, a change of {pct(f1['change'])}; the rule fires if the 2026 ratio is not below 2025's by more than 5 %.",
            f"- **F2** ({'FIRES' if f2['fires'] else 'does not fire'}): September 2026 mean spread on the printed day {fmt(f2['september_2026_spread'])} against Modo's published {fmt(f2['published'])}, tolerance {fmt(f2['tolerance'])}.",
            "",
            "## The headline measure (printed day)",
            "",
            f'September 2026 against September 2025: spread {fmt(yoy["2026-09"])} against {fmt(yoy["2025-09"])}, up {pct(yoy["change"])}. Bloomberg says 80 %; Modo\'s "GBP 45/MWh wider" implies {pct(yoy["modo_45_wider_implies"])} on this September. **The difference is not resolved here** (caveat 5).',
            "",
        ]
        + md_table(PERIOD_HEADER, [period_row(y, P[y]) for y in years])
        + [
            "",
            "Days: `days measured` are the period's printed dates with 23 to 25 prices; `days with gas` its dates with an ONS SAP; `days with both` the dates entering the ratios (gas ends 11/10/2026); `days with legs` those with a carbon month too (October 2026 has none yet). Legs are means over the days with legs, in GBP/MWh; shares are each leg's mean over the spread's mean on those days and sum to 100 %.",
            "",
            "## The same on the local day (each printed hour read as UTC, assigned to its Europe/London date)",
            "",
        ]
        + md_table(PERIOD_HEADER, [period_row(y, L[y]) for y in years])
        + [
            "",
            f"Excluded on the local unit: {excluded_text(R['units']['local']['excluded'])}; on the printed unit: {excluded_text(R['units']['printed']['excluded'])}. The local figures rest on the UTC reading of the file's hours, which NESO does not document (declaration, 'what a day is'). **Departure from the declaration's expectation, recorded:** the declaration said the last local day would be partial and excluded; the reconstructed local 2026-10-16 holds 23 hours (23:00 UTC of 15/10 and 00:00 to 21:00 UTC of 16/10, the file's last hour), so the 23-to-25 rule measured it. It lies outside '2026 to date' (which ends 15/10) and inside the partial local October 2026 only; no figure above is affected, and the rule, not the sentence, governs.",
            "",
            "## Every month, printed day",
            "",
        ]
        + md_table(PERIOD_HEADER, [period_row(m, P[m]) for m in months])
        + [
            "",
            "October 2026 is partial (to 15/10 for the spread, 11/10 for gas) and has no carbon month.",
            "",
            "## Explanations tested",
            "",
            "- **Gas-shock artefact.** Monthly ratio A against monthly gas, 2025 and 2026:",
            "",
        ]
        + md_table(
            ["month", "gas mean", "spread mean", "ratio A"],
            [
                [
                    m,
                    fmt(P[m]["gas_mean"]),
                    fmt(P[m]["spread_mean"]),
                    fmt(P[m]["ratio_of_means"], "0.001"),
                ]
                for m in months
                if m >= "2025-01"
            ],
        )
        + [
            "",
            "  Read: where gas jumps month on month and the ratio falls in the same month and recovers after, the fall is the artefact Jomaux describes; the table is the record, the reading is etrmbiz's.",
            "",
            "- **Solar depth.** The negative leg's share of the spread by year: "
            + "; ".join(f"{y} {pct(v)}" for y, v in R["negative_leg_share_by_year"].items())
            + ". Whether that shows GB's lower ratio to be a solar-depth effect is a reading, not a finding, unless the share is material and rising.",
            "",
            "## Scratch comparison (prior exposure, not results)",
            "",
        ]
        + md_table(
            [
                "figure",
                "scratch 15/10 (unsealed, outside this repository)",
                "declared measure",
                "period here",
            ],
            [
                [
                    c["figure"],
                    c["scratch"],
                    fmt(c["declared"], "0.001" if "ratio" in c["figure"] else "0.01"),
                    c["period"],
                ]
                for c in R["scratch_comparison"]
            ],
        )
        + [
            "",
            "The scratch 2026 window ended 14/10; the declared one ends 15/10 (spread) and 11/10 (ratio, where gas ends). The scratch read took the printed day.",
            "",
            *cross_check_section(),
            *forward_section(),
            "## Caveats, in the order the piece must carry them",
            "",
            "1. SAP is a within-day system price (National Gas Transmission's On-the-Day Commodity Market), not the NBP day-ahead assessment; no free daily NBP day-ahead series was found.",
            "2. The N2EX hourly auction is one of two GB day-ahead auctions.",
            "3. 2022 is the first full year of the file and includes the crisis.",
            "4. The merit-order proxy (2 × gas + 0.4 × carbon) is Jomaux's, uncalibrated for GB, on a monthly carbon price (gov.uk's CCM monthly average of the December UKA future's daily settlements) plus CPS 18; the boundary is coarse.",
            f'5. September 2026 on this measure is up {pct(yoy["change"])} on September 2025; Bloomberg says 80 %, Modo\'s "GBP 45 wider" implies {pct(yoy["modo_45_wider_implies"])}. Unresolved; not resolved by picking the measure that matches Bloomberg.',
            "",
            "## Expert corner",
            "",
            f"- Declaration `{R['declaration_sha256']}`; sources: "
            + "; ".join(
                f"`{k}` `{v['sha256'][:12]}…` fetched {v['fetched_at'][:19]}Z"
                for k, v in R["sources"].items()
            )
            + ".",
            "- The file prints 24 hours on every date including clock-change dates; the printed date is the primary unit, the local day the secondary. Hour labels `HH:00 - HH:00`; prices to six decimals, read as Decimals.",
            f"- Carbon months read: {R['carbon_months']['first']} to {R['carbon_months']['last']} ({R['carbon_months']['months']}); every month printed in several rows of the gov.uk tables printed one value (C3).",
            f"- `evidence/days.ndjson`: one line per unit and day ({R['days_ndjson']['kept']} kept, {R['days_ndjson']['added']} added this run; C5 append-only). `evidence/format-check.json`: no departure from the schema pass.",
            "- Reproduce: `uv run --group registers python investigations/024-the-gas-in-the-spread/run.py --phase compute --seal "
            + R["declaration_sha256"][:8]
            + "`; tests `uv run pytest tests/test_gas_in_the_spread.py`; rule map `evidence/rule-sources.json`.",
            "",
        ]
    )
    RESULTS_MD.write_text("\n".join(lines) + "\n")
    log_run("render", results_sha256=sha(RESULTS_JSON), results_md_sha256=sha(RESULTS_MD))
    print(f"rendered {RESULTS_MD.relative_to(REPO_ROOT)}")


def phase_figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    R = json.loads(RESULTS_JSON.read_text())
    P = R["units"]["printed"]["periods"]
    months = [k for k in P if len(k) == 7]
    FIGURES.mkdir(exist_ok=True)
    SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4e0"
    BLUE, BLUE_LIGHT, ORANGE, AQUA, RED = "#2a78d6", "#86b6ef", "#eb6834", "#1baf7a", "#e34948"
    footer = (
        "Copyright (c) 2026, A115. Grid Mysteries investigation 024. Sources: NESO Data Portal, "
        "N2EX GB day-ahead price (resource 4f27eea5…); ONS, System Average Price of gas "
        "(15/10/2026 edition); gov.uk, UK ETS monthly average prices.\n"
        f"Computed {R['computed_at'][:10]} under declaration {R['declaration_sha256'][:8]}."
    )
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 12,
            "text.color": INK,
            "axes.edgecolor": GRID,
            "axes.labelcolor": INK_2,
            "xtick.color": INK_2,
            "ytick.color": INK_2,
            "axes.facecolor": SURFACE,
            "figure.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "svg.fonttype": "none",
        }
    )
    printed: dict[str, Any] = {}
    x = list(range(len(months)))
    ticks = [i for i, m in enumerate(months) if m.endswith("-01")]
    tick_labels = [m[:4] for m in months if m.endswith("-01")]

    def finish(fig, ax, stem, title, subtitle):
        fig.text(0.03, 0.955, title, fontsize=20, fontweight=600, color=INK)
        fig.text(0.03, 0.915, subtitle, fontsize=12.5, color=INK_2)
        fig.text(0.03, 0.018, footer, fontsize=8.5, color=INK_2, ha="left", va="bottom")
        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels)
        ax.set_xlim(-0.5, len(months) - 0.5)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        fig.savefig(FIGURES / f"{stem}.png", dpi=100)
        fig.savefig(FIGURES / f"{stem}.svg")
        plt.close(fig)

    # chart 1: monthly spread and monthly gas, two axes, both GBP/MWh
    spread = [float(P[m]["spread_mean"]) for m in months]
    gas = [
        float(P[m]["gas_mean"]) if P[m]["gas_mean"] is not None else float("nan") for m in months
    ]
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.92, top=0.86, bottom=0.14)
    ax.plot(x, spread, color=BLUE, linewidth=2.4, label="monthly mean daily spread (left axis)")
    ax2 = ax.twinx()
    ax2.plot(x, gas, color=ORANGE, linewidth=2.4, label="monthly mean gas price, SAP (right axis)")
    ax.set_ylabel("Mean daily spread, pounds per megawatt-hour", labelpad=10)
    ax2.set_ylabel("Mean gas price, pounds per megawatt-hour", labelpad=10)
    ax.set_ylim(0, max(spread) * 1.08)
    ax2.set_ylim(0, max(v for v in gas if v == v) * 1.08)
    ax2.spines["top"].set_visible(False)
    ax.set_xlabel("Calendar month, January 2022 to " + months[-1], labelpad=10)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False, fontsize=11)
    for m in ("2022-01", "2025-09", "2026-09", months[-1]):
        printed[f"chart 1 spread {m}"] = P[m]["spread_mean"]
        printed[f"chart 1 gas {m}"] = P[m]["gas_mean"]
    finish(
        fig,
        ax,
        "chart-1-monthly-spread-and-gas",
        "Monthly mean daily day-ahead spread and monthly mean gas price, Great Britain",
        "Spread: N2EX hourly day-ahead, highest minus lowest hour of each printed day. Gas: ONS daily SAP. Both in pounds per megawatt-hour, each on its own axis.",
    )

    # chart 2: monthly ratio A as a line, yearly means as steps
    ratio = [
        float(P[m]["ratio_of_means"]) if P[m]["ratio_of_means"] is not None else float("nan")
        for m in months
    ]
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.14)
    ax.plot(
        x,
        ratio,
        color=BLUE_LIGHT,
        linewidth=2,
        marker="o",
        markersize=4,
        label="monthly ratio A (mean spread over mean gas)",
    )
    for y in ("2022", "2023", "2024", "2025", "2026 to date"):
        idx = [i for i, m in enumerate(months) if m.startswith(y[:4])]
        v = float(P[y]["ratio_of_means"])
        ax.plot(
            [idx[0] - 0.5, idx[-1] + 0.5],
            [v, v],
            color=ORANGE,
            linewidth=3,
            solid_capstyle="butt",
            label="yearly ratio A (2026: to date)" if y == "2022" else None,
        )
        ax.text(
            idx[-1] + 0.4,
            v + 0.07,
            fmt(v, "0.01"),
            fontsize=11.5,
            color=ORANGE,
            ha="right",
            va="bottom",
            fontweight=600,
        )
        printed[f"chart 2 yearly ratio {y}"] = P[y]["ratio_of_means"]
    ax.set_ylabel(
        "Spread divided by gas price, both in pounds per megawatt-hour (dimensionless)", labelpad=10
    )
    ax.set_xlabel("Calendar month, January 2022 to " + months[-1], labelpad=10)
    ax.set_ylim(0, max(v for v in ratio if v == v) * 1.12)
    ax.legend(loc="upper right", frameon=False, fontsize=11)
    for m in ("2025-09", "2026-09"):
        printed[f"chart 2 monthly ratio {m}"] = P[m]["ratio_of_means"]
    finish(
        fig,
        ax,
        "chart-2-monthly-ratio-with-yearly-steps",
        "Monthly spread-to-gas ratio with the yearly means as steps, Great Britain",
        "Ratio A: the month's mean daily spread divided by its mean SAP gas price, over the days with both. Steps: the same ratio over each calendar year.",
    )

    # chart 3: the three legs, stacked monthly bars
    leg_months = [m for m in months if P[m]["days_with_legs"]]
    xl = [months.index(m) for m in leg_months]
    neg = [float(P[m]["legs_mean"]["negative"]) for m in leg_months]
    mer = [float(P[m]["legs_mean"]["merit_order"]) for m in leg_months]
    sca = [float(P[m]["legs_mean"]["scarcity"]) for m in leg_months]
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.14)
    ax.bar(xl, neg, color=AQUA, width=0.8, label="negative leg (below zero)")
    ax.bar(
        xl, mer, bottom=neg, color=BLUE, width=0.8, label="merit-order leg (zero to the CCGT proxy)"
    )
    ax.bar(
        xl,
        sca,
        bottom=[a + b for a, b in zip(neg, mer, strict=True)],
        color=RED,
        width=0.8,
        label="scarcity leg (above the proxy)",
    )
    ax.set_ylabel(
        "Mean daily spread, pounds per megawatt-hour, split into Jomaux's three legs", labelpad=10
    )
    ax.set_xlabel(
        "Calendar month, January 2022 to "
        + leg_months[-1]
        + " (months with a published carbon price)",
        labelpad=10,
    )
    ax.legend(loc="upper right", frameon=False, fontsize=11)
    for y in ("2022", "2023", "2024", "2025", "2026 to date"):
        for leg in ("negative", "merit_order", "scarcity"):
            printed[f"chart 3 caption {y} {leg} share"] = P[y]["legs_share"][leg]
            printed[f"chart 3 caption {y} {leg} mean"] = P[y]["legs_mean"][leg]
    finish(
        fig,
        ax,
        "chart-3-three-legs-stacked-monthly",
        "The monthly mean daily spread split into negative, merit-order and scarcity legs, Great Britain",
        "Each hour's price split at zero and at 2 × gas + 0.4 × carbon (Jomaux's CCGT proxy, uncalibrated); the three legs of each day sum to its spread. Means over the month's days.",
    )

    if FORWARD.exists():
        tokens = {
            "SURFACE": SURFACE,
            "INK": INK,
            "INK_2": INK_2,
            "GRID": GRID,
            "BLUE": BLUE,
            "BLUE_LIGHT": BLUE_LIGHT,
            "ORANGE": ORANGE,
        }
        printed.update(chart_4(R, plt, tokens, footer))
    captions = (
        [
            "# 024 figures",
            "",
            f"Drawn by `run.py --phase figures` from `evidence/results.json` as computed {R['computed_at'][:10]} under declaration `{R['declaration_sha256'][:8]}…`. Read only: nothing recomputed. PNG 1600 pixels wide, SVG beside. Every number printed on a chart is in RESULTS.md's tables.",
            "",
            "## Chart 1 — `chart-1-monthly-spread-and-gas`",
            "",
            f"**Caption.** Monthly mean of the daily day-ahead spread (N2EX hourly auction, highest minus lowest hour of each printed day; left axis) and monthly mean gas price (ONS daily SAP times ten; right axis), both in GBP/MWh, January 2022 to {months[-1]} (partial). September 2026: spread {fmt(P['2026-09']['spread_mean'])}, gas {fmt(P['2026-09']['gas_mean'])}; September 2025: {fmt(P['2025-09']['spread_mean'])} and {fmt(P['2025-09']['gas_mean'])}. It shows the two series moving together, and how far the 2026 rise in the spread tracks the rise in gas.",
            "",
            "## Chart 2 — `chart-2-monthly-ratio-with-yearly-steps`",
            "",
            f"**Caption.** The monthly ratio A (mean daily spread over mean gas price, over the days with both) as a line, with each calendar year's ratio as a step: 2022 {fmt(P['2022']['ratio_of_means'], '0.01')}, 2023 {fmt(P['2023']['ratio_of_means'], '0.01')}, 2024 {fmt(P['2024']['ratio_of_means'], '0.01')}, 2025 {fmt(P['2025']['ratio_of_means'], '0.01')}, 2026 to 15/10 {fmt(P['2026 to date']['ratio_of_means'], '0.01')} (the same dates of 2025: {fmt(P['2025 same dates']['ratio_of_means'], '0.01')}). September 2026 {fmt(P['2026-09']['ratio_of_means'], '0.01')} against September 2025 {fmt(P['2025-09']['ratio_of_means'], '0.01')}. It shows how many pounds of spread each pound of gas bought, month by month, and that 2026's ratio sits below every earlier year's step.",
            "",
            "## Chart 3 — `chart-3-three-legs-stacked-monthly`",
            "",
            "**Caption.** The monthly mean daily spread split into Jomaux's three legs: the part of the spread below zero (negative), between zero and the CCGT proxy of 2 × gas + 0.4 × carbon (merit-order), and above it (scarcity); the legs sum to the spread on every day. Carbon is gov.uk's monthly average UKA price plus CPS 18, so the boundary is coarse; months without a published carbon price are not drawn. Shares by year:",
            "",
        ]
        + md_table(
            ["period", "negative", "merit-order", "scarcity", "days with legs"],
            [
                [
                    y,
                    pct(P[y]["legs_share"]["negative"]),
                    pct(P[y]["legs_share"]["merit_order"]),
                    pct(P[y]["legs_share"]["scarcity"]),
                    P[y]["days_with_legs"],
                ]
                for y in ("2022", "2023", "2024", "2025", "2026 to date", "2025 same dates")
            ],
        )
        + (
            [
                "## Chart 4 — `chart-4-implied-forward-spread`",
                "",
                "**Caption.** The realised monthly mean daily spread (024, printed day) and mean SAP gas from January 2024 to the latest month as lines; from November 2026 to March 2028 a shaded corridor, the forward NBP gas price as printed by Catalyst Commercial on 15/10/2026 (settlement 14/10/2026) times 024's yearly ratio band, with the central case (the 2026-to-date ratio) dashed and the forward gas itself dashed in the same units. **The corridor is the forward gas curve times a historical ratio band, not a forecast of gas**; the falsifiers F3 and F4 and the three watch dates are in RESULTS.md's forward record.",
                "",
            ]
            if FORWARD.exists()
            else []
        )
        + [
            "",
            "## Every number printed on a chart",
            "",
        ]
        + md_table(["chart and number", "value"], [[k, v] for k, v in printed.items()])
        + [""]
    )
    (FIGURES / "captions.md").write_text("\n".join(captions) + "\n")
    write_json(FIGURES / "printed-numbers.json", printed)
    print(f"figures -> {FIGURES.relative_to(REPO_ROOT)}")


def phase_schema_cross_check() -> None:
    """Schema supplement for amendment 1's source: header, rows, forms, chart facts; no value."""
    ARCHIVE_OFGEM.mkdir(parents=True, exist_ok=True)
    profile = ofgem_wmi.format_profile(OFGEM_CHART_FILE)
    text = OFGEM_CHART_FILE.read_text(encoding="utf-8")
    body = ofgem_wmi.rows(text)[1:]
    page = OFGEM_PAGE_FILE.read_text(encoding="utf-8")
    m = re.search(r"data-js-chart-modal-data='(\{[^']*Gas prices: day-ahead[^']*\})'", page)
    modal = json.loads(html_lib.unescape(m.group(1))) if m else None
    report = {
        "file": str(OFGEM_CHART_FILE.relative_to(REPO_ROOT)),
        "sha256": sha(OFGEM_CHART_FILE),
        "page": str(OFGEM_PAGE_FILE.relative_to(REPO_ROOT)),
        "page_sha256": sha(OFGEM_PAGE_FILE),
        "page_chart_node": {k: modal[k] for k in ("id", "name", "chart")} if modal else None,
        "page_chart_description": re.sub(r"<[^>]+>", " ", modal["content"]).replace("&nbsp;", " ")
        if modal
        else None,
        **profile,
        "first_category": body[0][0],
        "last_category": body[-1][0],
    }
    write_json(ARCHIVE_OFGEM / "schema-report.json", report)
    lines = [
        "# Schema report: 024-ofgem-gas-day-ahead-monthly",
        "",
        f"`{report['file']}` (SHA-256 `{report['sha256']}`), the everviz inject script Ofgem's data portal renders for chart node {report['page_chart_node']['id'] if modal else '?'} "
        f"(`{report['page']}`, SHA-256 `{report['page_sha256']}`, chart key `{report['page_chart_node']['chart'] if modal else '?'}`). "
        f"Chart title as printed: {report['title']!r}; credits: {report['credits']!r}; y-axis title: {report['y_axis_title']!r}. "
        f"Written by `run.py --phase schema-cross-check`; no value is read.",
        "",
        f"Embedded CSV: header {', '.join(f'`{h}`' for h in report['header'])}; {report['rows']} rows from `{report['first_category']}` to `{report['last_category']}` "
        f"(month/day/year, the month's first day); date forms {report['forms']['date']}; price forms {report['forms']['price']}.",
        "",
        "Ofgem's description of the chart, from the page:",
        "",
        f"    {' '.join((report['page_chart_description'] or '').split())}",
        "",
    ]
    (ARCHIVE_OFGEM / "SCHEMA.md").write_text("\n".join(lines) + "\n")
    log_run("schema-cross-check", ofgem=sha(ARCHIVE_OFGEM / "schema-report.json"))
    print("cross-check schema supplement written")


MATERIAL = Decimal("0.05")
CROSS_CHECK_MONTHS = (
    "2025-01",
    "2025-06",
    "2026-01",
    "2026-06",
)  # the two half-years the F1 cross-check compares


def sealed_amendment(seal: str | None) -> str:
    digest = sha(AMENDMENT_1)
    if not seal or not digest.startswith(seal):
        sys.exit(
            f"cross-check needs --seal, the prefix of AMENDMENT-1.md's SHA-256 ({digest[:8]}…)"
        )
    if not (HERE / "AMENDMENT-1.md.timestamps.json").exists():
        sys.exit("AMENDMENT-1.md is not frozen (no proof sidecar)")
    return digest


def phase_cross_check(seal: str | None) -> None:
    """Amendment 1: Ofgem's monthly day-ahead gas price against the SAP monthly means of results.json."""
    digest = sealed_amendment(seal)
    manifest = check_manifest()
    profile = ofgem_wmi.format_profile(OFGEM_CHART_FILE)
    expected = json.loads((ARCHIVE_OFGEM / "schema-report.json").read_text())
    diffs = differences(
        {k: expected[k] for k in ("header", "rows", "forms")},
        {k: profile[k] for k in ("header", "rows", "forms")},
    )
    if diffs:
        sys.exit(f"C2 (amendment 1): the Ofgem chart departs from the schema pass: {diffs}")
    R = json.loads(RESULTS_JSON.read_text())
    P = R["units"]["printed"]["periods"]
    ofgem = ofgem_wmi.read(OFGEM_CHART_FILE)
    months = [k for k in P if len(k) == 7]
    rows_out, missing = [], []
    for m in months:
        key = (int(m[:4]), int(m[5:]))
        if key not in ofgem or P[m]["gas_mean"] is None:
            missing.append(m)
            continue
        o = gs.quantise(ofgem_wmi.to_gbp_per_mwh(ofgem[key]))
        sap = Decimal(P[m]["gas_mean"])
        spread = Decimal(P[m]["spread_mean"])
        rows_out.append(
            {
                "month": m,
                "ofgem_pence_per_therm": ofgem[key],
                "ofgem_gbp_per_mwh": o,
                "sap_gbp_per_mwh": sap,
                "difference": gs.quantise(o - sap),
                "difference_share_of_sap": gs.quantise((o - sap) / sap),
                "spread_mean": spread,
                "ratio_on_sap": gs.quantise(spread / sap),
                "ratio_on_ofgem": gs.quantise(spread / o),
            }
        )

    def half(first: str, last: str) -> dict[str, Any]:
        sel = [r for r in rows_out if first <= r["month"] <= last]
        n = len(sel)
        mean = lambda k: gs.quantise(sum(r[k] for r in sel) / n) if n else None  # noqa: E731
        s_, o_, sp = mean("sap_gbp_per_mwh"), mean("ofgem_gbp_per_mwh"), mean("spread_mean")
        return {
            "months": n,
            "first": first,
            "last": last,
            "spread_mean_of_months": sp,
            "sap_mean_of_months": s_,
            "ofgem_mean_of_months": o_,
            "ratio_on_sap": gs.quantise(sp / s_) if sp and s_ else None,
            "ratio_on_ofgem": gs.quantise(sp / o_) if sp and o_ else None,
        }

    h25, h26 = (
        half(CROSS_CHECK_MONTHS[0], CROSS_CHECK_MONTHS[1]),
        half(CROSS_CHECK_MONTHS[2], CROSS_CHECK_MONTHS[3]),
    )
    change_sap = (
        gs.quantise(h26["ratio_on_sap"] / h25["ratio_on_sap"] - 1)
        if h26["ratio_on_sap"] and h25["ratio_on_sap"]
        else None
    )
    change_ofgem = (
        gs.quantise(h26["ratio_on_ofgem"] / h25["ratio_on_ofgem"] - 1)
        if h26["ratio_on_ofgem"] and h25["ratio_on_ofgem"]
        else None
    )
    recent = [r for r in rows_out if r["month"] >= "2025-01"]
    material = [r["month"] for r in recent if abs(r["difference_share_of_sap"]) > MATERIAL]
    years: dict[str, Any] = {}
    for y in ("2022", "2023", "2024", "2025", "2026"):
        sel = [r for r in rows_out if r["month"].startswith(y)]
        if sel:
            n = len(sel)
            years[y] = {
                "months": n,
                "sap_mean_of_months": gs.quantise(sum(r["sap_gbp_per_mwh"] for r in sel) / n),
                "ofgem_mean_of_months": gs.quantise(sum(r["ofgem_gbp_per_mwh"] for r in sel) / n),
                "ratio_on_sap": gs.quantise(
                    sum(r["spread_mean"] for r in sel) / sum(r["sap_gbp_per_mwh"] for r in sel)
                ),
                "ratio_on_ofgem": gs.quantise(
                    sum(r["spread_mean"] for r in sel) / sum(r["ofgem_gbp_per_mwh"] for r in sel)
                ),
            }
    out = {
        "amendment_1_sha256": digest,
        "declaration_sha256": R["declaration_sha256"],
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "results_sha256": sha(RESULTS_JSON),
        "source": {
            k: manifest[k] for k in ("ofgem-wmi-gas-day-ahead-monthly-chart", "ofgem-wmi-page")
        },
        "ofgem_months": {
            "first": f"{min(ofgem)[0]}-{min(ofgem)[1]:02d}",
            "last": f"{max(ofgem)[0]}-{max(ofgem)[1]:02d}",
            "count": len(ofgem),
        },
        "kwh_per_therm": ofgem_wmi.KWH_PER_THERM,
        "months_compared": len(rows_out),
        "months_missing": missing,
        "months": rows_out,
        "years": years,
        "material_threshold": MATERIAL,
        "material_months_2025_on": material,
        "largest_difference_2025_on": max(recent, key=lambda r: abs(r["difference_share_of_sap"]))[
            "month"
        ]
        if recent
        else None,
        "f1_cross_check": {
            "half_2025": h25,
            "half_2026": h26,
            "change_on_sap": change_sap,
            "change_on_ofgem": change_ofgem,
            "verdict_stands": (change_ofgem is not None and change_ofgem < -MATERIAL),
        },
    }
    write_json(CROSS_CHECK, out)
    log_run(
        "cross-check", seal=seal, amendment_1_sha256=digest, cross_check_sha256=sha(CROSS_CHECK)
    )
    print(
        f"cross-check under {digest[:8]}…: {len(rows_out)} months, material months 2025 on: {material or 'none'}; F1 change on SAP {change_sap}, on Ofgem {change_ofgem}, verdict stands {out['f1_cross_check']['verdict_stands']}"
    )


def cross_check_section() -> list[str]:
    if not CROSS_CHECK.exists():
        return []
    X = json.loads(CROSS_CHECK.read_text())
    f = X["f1_cross_check"]
    h25, h26 = f["half_2025"], f["half_2026"]
    lines = (
        [
            "## Cross-check: Ofgem's monthly day-ahead gas price against SAP (amendment 1)",
            "",
            f'Computed {X["computed_at"][:10]} under amendment 1 `{X["amendment_1_sha256"][:8]}…` from Ofgem\'s wholesale market indicators chart "Gas prices: day-ahead contracts – monthly average (Great Britain)" '
            f"(data portal node 175055, served by everviz, pinned 15/10/2026, `{X['source']['ofgem-wmi-gas-day-ahead-monthly-chart']['sha256'][:12]}…`): a volume-weighted monthly average of broker-traded day-ahead gas from March 2021, in pence per therm, converted at {X['kwh_per_therm']} kWh per therm. "
            f"Ofgem's series runs {X['ofgem_months']['first']} to {X['ofgem_months']['last']}, so the comparison covers {X['months_compared']} months to {X['ofgem_months']['last']} and **cannot test September 2026**; months without both: {', '.join(X['months_missing']) or 'none'}. Nothing computed under the declaration changes.",
            "",
            f"- **Materiality** (threshold {pct(X['material_threshold'])} of SAP in any month from January 2025): {'material in ' + ', '.join(X['material_months_2025_on']) if X['material_months_2025_on'] else 'no month from January 2025 differs by more than the threshold'}; the largest difference since January 2025 is in {X['largest_difference_2025_on']}.",
            f"- **F1 on Ofgem's gas**, January to June of each year (the months both series share in 2026): ratio A on SAP {fmt(h26['ratio_on_sap'], '0.001')} against {fmt(h25['ratio_on_sap'], '0.001')} ({pct(f['change_on_sap'])}); on Ofgem's day-ahead price {fmt(h26['ratio_on_ofgem'], '0.001')} against {fmt(h25['ratio_on_ofgem'], '0.001')} ({pct(f['change_on_ofgem'])}). The F1 verdict {'stands' if f['verdict_stands'] else 'does not stand'} on the cross-check series over those months.",
            "",
        ]
        + md_table(
            [
                "year",
                "months",
                "SAP mean of months",
                "Ofgem mean of months",
                "ratio A on SAP",
                "ratio A on Ofgem",
            ],
            [
                [
                    y,
                    v["months"],
                    fmt(v["sap_mean_of_months"]),
                    fmt(v["ofgem_mean_of_months"]),
                    fmt(v["ratio_on_sap"], "0.001"),
                    fmt(v["ratio_on_ofgem"], "0.001"),
                ]
                for y, v in X["years"].items()
            ],
        )
        + [
            "",
            "Yearly ratios here are the sum of monthly mean spreads over the sum of monthly mean gas prices (months weighted equally), so the SAP column differs in the third decimal from the day-weighted ratio A above.",
            "",
        ]
        + md_table(
            [
                "month",
                "Ofgem p/therm",
                "Ofgem GBP/MWh",
                "SAP GBP/MWh",
                "difference",
                "share of SAP",
                "ratio A on SAP",
                "ratio A on Ofgem",
            ],
            [
                [
                    r["month"],
                    fmt(r["ofgem_pence_per_therm"]),
                    fmt(r["ofgem_gbp_per_mwh"]),
                    fmt(r["sap_gbp_per_mwh"]),
                    fmt(r["difference"]),
                    pct(r["difference_share_of_sap"]),
                    fmt(r["ratio_on_sap"], "0.001"),
                    fmt(r["ratio_on_ofgem"], "0.001"),
                ]
                for r in X["months"]
            ],
        )
        + [""]
    )
    return lines


def phase_schema_forward() -> None:
    """Schema supplement for amendment 2's source: the tables' layout; no value."""
    ARCHIVE_CATALYST.mkdir(parents=True, exist_ok=True)
    profile = catalyst_report.format_profile(CATALYST_FILE)
    text = CATALYST_FILE.read_text(encoding="utf-8")
    title = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    attribution = re.search(r"[^<>]*may be quoted with attribution[^<>]*", text)
    report = {
        "file": str(CATALYST_FILE.relative_to(REPO_ROOT)),
        "sha256": sha(CATALYST_FILE),
        "url": CATALYST_URL,
        "title": html_lib.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip()
        if title
        else None,
        "attribution_sentence": html_lib.unescape(attribution.group(0)).strip()
        if attribution
        else None,
        **profile,
    }
    write_json(ARCHIVE_CATALYST / "schema-report.json", report)
    lines = [
        "# Schema report: 024-catalyst-report-2026-10-15",
        "",
        f"`{report['file']}` (SHA-256 `{report['sha256']}`), `{report['url']}`, title {report['title']!r}; settlement line as printed: {report['settlement_line']!r}; "
        f"attribution sentence: {report['attribution_sentence']!r}. {len(report['tables'])} tables. Written by `run.py --phase schema-forward`; no value is read.",
        "",
    ]
    for i, t in enumerate(report["tables"]):
        lines += [
            f"## Table {i}: {t['rows']} rows, cells per row {t['cells_per_row']}",
            "",
            "Header: " + ", ".join(f"`{h}`" for h in t["header"]) + ".",
            "",
            "Row labels, in order: " + ", ".join(f"`{x}`" for x in t["row_labels"]) + ".",
            "",
            f"Settlement cell forms: {t['settlement_forms']}.",
            "",
        ]
    (ARCHIVE_CATALYST / "SCHEMA.md").write_text("\n".join(lines) + "\n")
    log_run("schema-forward", catalyst=sha(ARCHIVE_CATALYST / "schema-report.json"))
    print("forward schema supplement written")


#: Amendment 2: the contracts read from the pinned page, and the seasons built from them.
FORWARD_CONTRACTS = ("Nov-26", "Dec-26", "Q1-27", "Summer-27", "Winter-27")
FORWARD_SEASONS = {
    "winter 2026-27 (Nov-Mar)": ("Nov-26", "Dec-26", "Q1-27"),
    "Summer-27": ("Summer-27",),
    "Winter-27": ("Winter-27",),
}
#: The dated watches, one per season end, as 013's are opened in the v3 record.
FORWARD_WATCHES = (
    ("w-024-winter-2026-27", "winter 2026-27 (Nov-Mar)", "2027-03-31"),
    ("w-024-summer-27", "Summer-27", "2027-09-30"),
    ("w-024-winter-27", "Winter-27", "2028-03-31"),
)
F3_TOLERANCE = Decimal("0.15")
F4_GAS_TOLERANCE = Decimal("0.10")


def sealed_amendment_2(seal: str | None) -> str:
    digest = sha(AMENDMENT_2)
    if not seal or not digest.startswith(seal):
        sys.exit(f"forward needs --seal, the prefix of AMENDMENT-2.md's SHA-256 ({digest[:8]}…)")
    if not (HERE / "AMENDMENT-2.md.timestamps.json").exists():
        sys.exit("AMENDMENT-2.md is not frozen (no proof sidecar)")
    return digest


def phase_forward(seal: str | None) -> None:
    """Amendment 2: the spread implied by 024's ratio band and the pinned forward gas curve."""
    digest = sealed_amendment_2(seal)
    manifest = check_manifest()
    profile = catalyst_report.format_profile(CATALYST_FILE)
    expected = json.loads((ARCHIVE_CATALYST / "schema-report.json").read_text())
    diffs = differences(expected["tables"], profile["tables"]) + differences(
        expected["settlement_line"], profile["settlement_line"]
    )
    if diffs:
        sys.exit(f"C2 (amendment 2): the Catalyst page departs from the schema pass: {diffs}")
    R = json.loads(RESULTS_JSON.read_text())
    band = gs.ratio_band(R)
    nbp = catalyst_report.read_nbp(CATALYST_FILE)
    uk_ets = catalyst_report.read_uk_ets(CATALYST_FILE)
    gas = {
        c: gs.quantise(ofgem_wmi.to_gbp_per_mwh(nbp[c])) for c in ("Day-ahead", *FORWARD_CONTRACTS)
    }
    contracts = {
        c: {
            "pence_per_therm": nbp[c],
            "gas_gbp_per_mwh": gas[c],
            **{k: gs.quantise(v) for k, v in gs.implied_spread(gas[c], band).items()},
        }
        for c in FORWARD_CONTRACTS
    }
    seasons = {}
    for label, parts in FORWARD_SEASONS.items():
        g_ = gs.quantise(gs.season_mean([gas[c] for c in parts]))
        seasons[label] = {
            "contracts": list(parts),
            "gas_gbp_per_mwh": g_,
            **{k: gs.quantise(v) for k, v in gs.implied_spread(g_, band).items()},
        }
    monthly_ratios = {
        m: P["ratio_of_means"]
        for m, P in R["units"]["printed"]["periods"].items()
        if len(m) == 7 and m >= "2025-01" and P["ratio_of_means"] is not None
    }
    out = {
        "amendment_2_sha256": digest,
        "declaration_sha256": R["declaration_sha256"],
        "results_sha256": sha(RESULTS_JSON),
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": manifest["catalyst-uk-energy-market-report-2026-10-15"],
        "settlement_line": profile["settlement_line"],
        "kwh_per_therm": ofgem_wmi.KWH_PER_THERM,
        "band": {
            "low": band.low,
            "high": band.high,
            "central": band.central,
            "low_period": band.low_period,
            "high_period": band.high_period,
            "periods": {
                p: R["units"]["printed"]["periods"][p]["ratio_of_means"] for p in gs.BAND_PERIODS
            },
            "monthly_ratio_range_2025_on": {
                "min": min(monthly_ratios.values(), key=Decimal),
                "max": max(monthly_ratios.values(), key=Decimal),
            },
        },
        "day_ahead": {"pence_per_therm": nbp["Day-ahead"], "gas_gbp_per_mwh": gas["Day-ahead"]},
        "uk_ets_dec_26_gbp_per_t": uk_ets,
        "contracts": contracts,
        "seasons": seasons,
        "falsifiers": {
            "F3": {
                "tolerance": F3_TOLERANCE,
                "rule": "realised season ratio A outside the band by more than the tolerance",
            },
            "F4": {
                "gas_tolerance": F4_GAS_TOLERANCE,
                "rule": "realised season spread outside the implied band while realised gas is within the tolerance of the pinned forward",
            },
        },
        "watches": [
            {"watch": w, "season": s_, "due": d, "holder": "A115", "about": "024"}
            for w, s_, d in FORWARD_WATCHES
        ],
        "outcomes": [],
        "departures": [
            "The schema report amendment 2 cites by digest (35eafe66f552…) classed the commodities table's six settlement cells as 'other', because the reader's pound-per-tonne form at the time of the schema pass required '/t' where the page prints '/tonne'; the reader was corrected before the freeze and the supplement regenerated with it (digest "
            + sha(ARCHIVE_CATALYST / "schema-report.json")[:12]
            + "…) before this compute. The page's bytes are unchanged (C1); the first compute under the seal refused on C2 and was re-run after the regeneration. The UK ETS cell enters no figure."
        ],
    }
    write_json(FORWARD, out)
    log_run("forward", seal=seal, amendment_2_sha256=digest, forward_sha256=sha(FORWARD))
    print(
        f"forward under {digest[:8]}…: band {band.low} to {band.high} (central {band.central}); winter 2026-27 gas {seasons['winter 2026-27 (Nov-Mar)']['gas_gbp_per_mwh']} -> {seasons['winter 2026-27 (Nov-Mar)']['low']} to {seasons['winter 2026-27 (Nov-Mar)']['high']}"
    )


def forward_section() -> list[str]:
    if not FORWARD.exists():
        return []
    X = json.loads(FORWARD.read_text())
    b = X["band"]
    rows = [
        [
            c,
            fmt(v["pence_per_therm"]),
            fmt(v["gas_gbp_per_mwh"]),
            fmt(v["low"]),
            fmt(v["central"]),
            fmt(v["high"]),
        ]
        for c, v in X["contracts"].items()
    ]
    rows += [
        [
            f"**{s_}** ({' + '.join(v['contracts'])})",
            "—",
            fmt(v["gas_gbp_per_mwh"]),
            fmt(v["low"]),
            fmt(v["central"]),
            fmt(v["high"]),
        ]
        for s_, v in X["seasons"].items()
    ]
    lines = (
        [
            "## Forward record (amendment 2)",
            "",
            f'Computed {X["computed_at"][:10]} under amendment 2 `{X["amendment_2_sha256"][:8]}…`, from the ratio band of `results.json` (`{X["results_sha256"][:8]}…`, sealed under `{X["declaration_sha256"][:8]}…`) and the NBP curve as printed by Catalyst Commercial\'s "UK Energy Market Report - 15 October 2026" '
            f'(`{X["source"]["sha256"][:12]}…`, fetched {X["source"]["fetched_at"][:19]}Z; "{X["settlement_line"]}"). **This is a dated forecast appended to a forensic record, scored as a vector, never a verdict; it is not a Forward Mystery and claims no buyer, no absorption and no opportunity.**',
            "",
            "- **The band**: yearly ratio A (mean daily spread over mean SAP gas) for "
            + ", ".join(f"{p} {fmt(v, '0.001')}" for p, v in b["periods"].items())
            + f"; low edge {fmt(b['low'], '0.001')} ({b['low_period']}), high edge {fmt(b['high'], '0.001')} ({b['high_period']}), central case {fmt(b['central'], '0.001')} (2026 to date). "
            f"The band is four annual means of a monthly series whose monthly range since January 2025 is {fmt(b['monthly_ratio_range_2025_on']['min'], '0.01')} to {fmt(b['monthly_ratio_range_2025_on']['max'], '0.01')}: a month outside the band is not a falsification, a season is.",
            f"- **The curve**: Catalyst's table of NBP settlements for Wednesday 14 October 2026 in pence per therm, converted at {X['kwh_per_therm']} kWh per therm (p/therm × 10 ÷ {X['kwh_per_therm']} = GBP/MWh); day-ahead {fmt(X['day_ahead']['pence_per_therm'])} p/therm = {fmt(X['day_ahead']['gas_gbp_per_mwh'])} GBP/MWh for reference. The page is a broker-report aggregator's print, not the exchange's settlement file (ICE Endex NBP settlements are paid), and it is the only free dated print of the curve found; **its own footer calls its forward-season levels \"indicative editorial estimates\" that \"are not licensed market data\"**, so the curve here is Catalyst's indicative print, quoted with attribution and a link as its terms allow. A later edition is a new pin. The page's UK ETS Dec-26 line, {fmt(X['uk_ets_dec_26_gbp_per_t'])} GBP/t, is recorded and enters no figure below.",
            "- **Winter 2026-27** is November to March here: NBP seasons run October to March and April to September, and the page prints no Oct-26 (balance of month), so the winter is the mean of Nov-26, Dec-26 and Q1-27.",
            "",
        ]
        + md_table(
            [
                "contract or season",
                "NBP p/therm",
                "gas GBP/MWh",
                "implied spread, low",
                "central",
                "high",
            ],
            rows,
        )
        + [
            "",
            "The implied spread is the forward gas price times the band; it is **not a forecast of gas**.",
            "",
            '**Scoring, as a vector, appended as each season ends:** (a) the realised mean gas price (ONS SAP as 024 reads it, and Ofgem\'s monthly day-ahead price when it reaches the months) against the pinned forward; (b) the realised ratio A for the season, 024\'s measure re-run under its declaration for the new months, against the band; (c) the realised mean daily spread against the implied band. A miss is attributed in that order: gas moved (the curve was wrong, the ratio held); the ratio moved (the curve was right, the structure changed); both. The record never says "right" or "wrong" alone.',
            "",
            f"**Falsifiers, published with the claim.** **F3**: the realised ratio A for a full NBP season (winter 2026-27 as November to March, or Summer-27) lies outside the band by more than {fmt(X['falsifiers']['F3']['tolerance'])}: then the structure moved and the ratio is not a stable multiple. **F4**: the realised season spread lies outside the implied band although the season's realised gas lies within {pct(X['falsifiers']['F4']['gas_tolerance'])} of the pinned forward: then the miss is not gas, and the ratio method failed on its own terms.",
            "",
            "**Outcome schedule**, dated watches in the governed record (`check-record` refuses to let one lapse); each outcome is appended here, never edited in:",
            "",
        ]
        + md_table(
            ["watch", "season", "due", "holder"],
            [[w["watch"], w["season"], w["due"], w["holder"]] for w in X["watches"]],
        )
        + [""]
    )
    if X.get("departures"):
        lines += (
            ["**Departures from the amendment's expectation, recorded:**", ""]
            + [f"- {d}" for d in X["departures"]]
            + [""]
        )
    if X["outcomes"]:
        lines += ["Outcomes recorded:", ""] + [f"- {o}" for o in X["outcomes"]] + [""]
    return lines


def chart_4(
    R: dict[str, Any], plt: Any, tokens: dict[str, str], finish_footer: str
) -> dict[str, Any]:
    """The realised monthly spread, then the implied corridor with the forward gas beside it."""
    import matplotlib.dates as mdates

    X = json.loads(FORWARD.read_text())
    P = R["units"]["printed"]["periods"]
    months = [m for m in P if len(m) == 7 and m >= "2024-01"]
    xm = [mdates.date2num(date(int(m[:4]), int(m[5:]), 15)) for m in months]
    spread = [float(P[m]["spread_mean"]) for m in months]
    gas = [
        float(P[m]["gas_mean"]) if P[m]["gas_mean"] is not None else float("nan") for m in months
    ]
    # the corridor: each forward contract spans its delivery months
    spans = {
        "Nov-26": (date(2026, 11, 1), date(2026, 12, 1)),
        "Dec-26": (date(2026, 12, 1), date(2027, 1, 1)),
        "Q1-27": (date(2027, 1, 1), date(2027, 4, 1)),
        "Summer-27": (date(2027, 4, 1), date(2027, 10, 1)),
        "Winter-27": (date(2027, 10, 1), date(2028, 4, 1)),
    }
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.14)
    ax.plot(
        xm,
        spread,
        color=tokens["BLUE"],
        linewidth=2.4,
        label="realised monthly mean daily spread (024, printed day)",
    )
    ax.plot(
        xm,
        gas,
        color=tokens["ORANGE"],
        linewidth=1.8,
        label="realised monthly mean gas price (ONS SAP)",
    )
    first = True
    for c, (a, b_) in spans.items():
        v = X["contracts"][c]
        x0, x1 = mdates.date2num(a), mdates.date2num(b_)
        ax.fill_between(
            [x0, x1],
            [float(v["low"])] * 2,
            [float(v["high"])] * 2,
            color=tokens["BLUE_LIGHT"],
            alpha=0.35,
            linewidth=0,
            label="implied spread corridor: forward gas × ratio band" if first else None,
        )
        ax.plot(
            [x0, x1],
            [float(v["central"])] * 2,
            color=tokens["BLUE"],
            linewidth=2,
            linestyle="--",
            label="central case: forward gas × 2026-to-date ratio" if first else None,
        )
        ax.plot(
            [x0, x1],
            [float(v["gas_gbp_per_mwh"])] * 2,
            color=tokens["ORANGE"],
            linewidth=1.8,
            linestyle="--",
            label="forward gas as printed (Catalyst, settlement 14/10/2026)" if first else None,
        )
        ax.text(
            (x0 + x1) / 2,
            float(v["high"]) + (9 if c == "Dec-26" else 3),
            c,
            fontsize=10,
            color=tokens["INK_2"],
            ha="center",
            va="bottom",
        )
        first = False
    ax.axvline(mdates.date2num(date(2026, 10, 15)), color=tokens["INK_2"], linewidth=1)
    ax.text(
        mdates.date2num(date(2026, 10, 15)) - 10,
        5,
        "pinned 15/10/2026",
        fontsize=10,
        color=tokens["INK_2"],
        ha="right",
        va="bottom",
    )
    ax.set_xlim(mdates.date2num(date(2024, 1, 1)), mdates.date2num(date(2028, 4, 1)))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylim(0, max(max(spread), max(float(v["high"]) for v in X["contracts"].values())) * 1.12)
    ax.set_ylabel("Pounds per megawatt-hour", labelpad=10)
    ax.set_xlabel(
        "Calendar month, January 2024 to March 2028 (realised to the left of the pin date, implied to the right)",
        labelpad=10,
    )
    ax.yaxis.grid(True, color=tokens["GRID"], linewidth=0.8)
    ax.set_axisbelow(True)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=10.5)
    fig.text(
        0.03,
        0.955,
        "Realised monthly spread and the spread implied by the forward gas curve, Great Britain",
        fontsize=19,
        fontweight=600,
        color=tokens["INK"],
    )
    fig.text(
        0.03,
        0.915,
        "Realised: 024's monthly mean daily spread and mean SAP gas. Implied: Catalyst's NBP print of 14/10/2026 times 024's yearly ratio band (low, central, high).",
        fontsize=12.5,
        color=tokens["INK_2"],
    )
    fig.text(
        0.03,
        0.018,
        finish_footer
        + "\nforward curve: Catalyst Commercial report of 15/10/2026, settlement 14/10/2026.",
        fontsize=8.5,
        color=tokens["INK_2"],
        ha="left",
        va="bottom",
    )
    fig.savefig(FIGURES / "chart-4-implied-forward-spread.png", dpi=100)
    fig.savefig(FIGURES / "chart-4-implied-forward-spread.svg")
    plt.close(fig)
    printed = {
        f"chart 4 {c} {k}": v[k]
        for c, v in X["contracts"].items()
        for k in ("gas_gbp_per_mwh", "low", "central", "high")
    }
    printed["chart 4 band"] = (
        f"{b['low']} to {b['high']}, central {b['central']}" if (b := X["band"]) else ""
    )
    return printed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        required=True,
        choices=[
            "acquire",
            "schema",
            "schema-cross-check",
            "schema-forward",
            "format",
            "compute",
            "cross-check",
            "forward",
            "render",
            "figures",
        ],
    )
    parser.add_argument("--seal", default=None)
    args = parser.parse_args()
    if args.phase == "acquire":
        phase_acquire()
    elif args.phase == "schema":
        phase_schema()
    elif args.phase == "schema-cross-check":
        phase_schema_cross_check()
    elif args.phase == "schema-forward":
        phase_schema_forward()
    elif args.phase == "format":
        phase_format()
    elif args.phase == "compute":
        phase_compute(args.seal)
    elif args.phase == "cross-check":
        phase_cross_check(args.seal)
    elif args.phase == "forward":
        phase_forward(args.seal)
    elif args.phase == "render":
        phase_render()
    elif args.phase == "figures":
        phase_figures()


if __name__ == "__main__":
    main()
