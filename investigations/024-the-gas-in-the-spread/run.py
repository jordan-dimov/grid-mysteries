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
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import write_json
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
#: dataset -> (publisher, url, destination). The three data files and, for
#: vintage and licence, the publishers' own metadata pages.
SOURCES = {
    "neso-n2ex-day-ahead": ("neso", POWER_URL, POWER_FILE),
    "ons-sap-gas-daily": ("ons", GAS_URL, GAS_FILE),
    "govuk-ukets-ccm-monthly-average-prices": ("govuk", CARBON_URL, CARBON_FILE),
    "neso-n2ex-day-ahead-resource-metadata": ("neso", POWER_META_URL, POWER_META_FILE),
    "ons-sap-gas-dataset-page": ("ons", GAS_PAGE_URL, GAS_PAGE_FILE),
    "govuk-ukets-markets-guidance": ("govuk", CARBON_GUIDE_URL, CARBON_GUIDE_FILE),
}


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        required=True,
        choices=["acquire", "schema", "format", "compute", "render", "figures"],
    )
    parser.add_argument("--seal", default=None)
    args = parser.parse_args()
    if args.phase == "acquire":
        phase_acquire()
    elif args.phase == "schema":
        phase_schema()
    else:
        sys.exit(f"phase {args.phase} is not written yet")


if __name__ == "__main__":
    main()
