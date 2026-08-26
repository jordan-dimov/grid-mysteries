"""Investigation 005 runner: load journaled TEC vintages, run the declared Q1-Q3.

Usage: uv run --with openpyxl --with xlrd python \
    investigations/005-connection-date-credibility/run.py

Reads data/raw/neso/tec-history/journal.ndjson, normalises each era's column
names to the module's canonical names, and writes evidence/tec-slippage-summary.json
plus a per-project metrics table under data/derived/. All analytical rules live in
grid_mysteries.investigations.tec_slippage; this file only does I/O and column mapping.
"""

import csv
import json
from collections import Counter
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, evidence_dir, write_json
from grid_mysteries.investigations.tec_slippage import (
    Vintage,
    all_metrics,
    build_timelines,
    match_report,
    population,
    q1_dispersion,
    q2_predictability,
    q3_materiality,
)

RAW = REPO_ROOT / "data/raw/neso/tec-history"
DERIVED = REPO_ROOT / "data/derived/tec-history"
EVIDENCE = evidence_dir(__file__)
REGIME_CUTOFF = date(2025, 12, 1)  # vintages from Dec 2025 are analysed separately (declaration)

ALIASES = {
    "project id": "Project ID",
    "plant id": "Project ID",
    "record id": "Project ID",
    "project name": "Project Name",
    "customer name": "Customer Name",
    "user": "Customer Name",
    "connection site": "Connection Site",
    "connection point": "Connection Site",
    "mw effective from": "MW Effective From",
    "mw effective date": "MW Effective From",
    "tec effective from date": "MW Effective From",
    "project status": "Project Status",
    "cumulative total capacity (mw)": "Cumulative Total Capacity (MW)",
    "mw total": "Cumulative Total Capacity (MW)",
    "mw connected": "MW Connected",
    "mw connected ": "MW Connected",
    "plant type": "Plant Type",
    "host to": "HOST TO",
    "stage": "Stage",
    "agreement type": "Agreement Type",
    "gate": "Gate",
}


def canon(header: object) -> str | None:
    key = " ".join(str(header or "").lower().replace("\n", " ").split())
    return ALIASES.get(key)


def cell(value: object) -> object:
    if isinstance(value, datetime):
        return value.date()
    return value


def rows_from_matrix(matrix: list[list[object]]) -> list[dict[str, object]]:
    header_index = next(
        (i for i, r in enumerate(matrix) if any(canon(c) == "Project Name" for c in r)), None
    )
    if header_index is None:
        return []
    headers = [canon(c) for c in matrix[header_index]]
    out = []
    for r in matrix[header_index + 1 :]:
        row = {h: cell(v) for h, v in zip(headers, r, strict=False) if h}
        if str(row.get("Project Name") or "").strip():
            out.append(row)
    return out


def read_vintage(path: Path, fmt: str) -> list[dict[str, object]]:
    if fmt == "csv" or path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
            matrix = [list(r) for r in csv.reader(f)]
        return rows_from_matrix(matrix)
    if path.suffix.lower() == ".xlsx":
        import openpyxl

        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        best: list[dict[str, object]] = []
        for ws in wb.worksheets:
            rows = rows_from_matrix([list(r) for r in ws.iter_rows(values_only=True)])
            if len(rows) > len(best):
                best = rows
        return best
    if path.suffix.lower() == ".xls":
        import xlrd

        book = xlrd.open_workbook(path)
        best = []
        for sh in book.sheets():
            matrix = []
            for i in range(sh.nrows):
                vals = []
                for j in range(sh.ncols):
                    c = sh.cell(i, j)
                    if c.ctype == xlrd.XL_CELL_DATE:
                        vals.append(datetime(*xlrd.xldate_as_tuple(c.value, book.datemode)).date())
                    else:
                        vals.append(c.value)
                matrix.append(vals)
            rows = rows_from_matrix(matrix)
            if len(rows) > len(best):
                best = rows
        return best
    return []


def load_vintages() -> tuple[list[Vintage], list[dict]]:
    journal = [
        json.loads(line)
        for line in (RAW / "journal.ndjson").read_text().splitlines()
        if line.strip()
    ]
    by_date: dict[str, dict] = {}
    for entry in journal:
        if entry.get("duplicate_of"):
            continue
        d = entry["t_public"][:10]
        # one vintage per date: prefer the richer (more rows) file on conflict
        if d not in by_date or (entry.get("row_count") or 0) > (by_date[d].get("row_count") or 0):
            by_date[d] = entry
    vintages, skipped = [], []
    for d, entry in sorted(by_date.items()):
        path = REPO_ROOT / entry["path"]
        try:
            rows = read_vintage(path, entry.get("format", ""))
        except Exception as exc:  # noqa: BLE001 - recorded, not hidden
            skipped.append({"t_public": d, "path": entry["path"], "error": repr(exc)[:200]})
            continue
        if not rows:
            skipped.append({"t_public": d, "path": entry["path"], "error": "no header/rows parsed"})
            continue
        vintages.append(Vintage(date.fromisoformat(d), tuple(rows)))
    return vintages, skipped


def main() -> None:
    vintages, skipped = load_vintages()
    old = [v for v in vintages if v.t_public < REGIME_CUTOFF]
    new = [v for v in vintages if v.t_public >= REGIME_CUTOFF]
    last_old = max(v.t_public for v in old)

    timelines = build_timelines(old, use_project_id=False)
    metrics = all_metrics(timelines, last_old)
    pop = population(metrics)
    q1, q2 = q1_dispersion(pop), q2_predictability(pop)
    q3 = q3_materiality(pop, q2)

    # robustness: Project-ID-keyed window from 2021-11-26
    id_window = [v for v in old if v.t_public >= date(2021, 11, 26)]
    id_metrics = all_metrics(build_timelines(id_window, use_project_id=True), last_old)
    id_pop = [
        m for m in id_metrics if m.observation_span_years >= 2 and m.net_slip_months is not None
    ]
    id_q1 = q1_dispersion(id_pop)

    status_vocab = Counter(o.status for t in timelines.values() for o in t)
    disappeared = sum(1 for m in metrics if m.disappeared)
    summary = {
        "vintages_loaded": len(vintages),
        "vintages_old_regime": len(old),
        "vintages_new_regime": [v.t_public for v in new],
        "vintage_span": [old[0].t_public, last_old],
        "vintages_per_year": dict(sorted(Counter(v.t_public.year for v in vintages).items())),
        "skipped_vintages": skipped,
        "match_report": match_report(timelines),
        "identities_total": len(metrics),
        "identities_with_2_plus_years_and_slip": len(pop),
        "disappeared_identities_old_regime": disappeared,
        "status_vocabulary_top": status_vocab.most_common(25),
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "id_keyed_window_from_2021_11_26": {"n": len(id_pop), "q1": id_q1},
        "revisions_distribution": dict(sorted(Counter(min(m.revisions, 10) for m in pop).items())),
        "net_slip_quantiles_months": {
            q: sorted(m.net_slip_months for m in pop)[int((len(pop) - 1) * f)] if pop else None
            for q, f in (("p10", 0.1), ("p25", 0.25), ("p50", 0.5), ("p75", 0.75), ("p90", 0.9))
        },
    }
    # Committed before the trailing-newline convention; its pinned bytes stay.
    write_json(EVIDENCE / "tec-slippage-summary.json", summary, trailing_newline=False)
    DERIVED.mkdir(parents=True, exist_ok=True)
    with (DERIVED / "project-metrics.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [k for k in asdict(metrics[0]) if k != "status_transitions"] + ["status_transitions"]
        )
        for m in metrics:
            d = asdict(m)
            w.writerow(
                [d[k] for k in d if k != "status_transitions"]
                + [";".join("->".join(t) for t in m.status_transitions)]
            )
    print(
        dumps(
            {
                k: summary[k]
                for k in (
                    "vintages_loaded",
                    "identities_total",
                    "identities_with_2_plus_years_and_slip",
                    "q1",
                    "q3",
                )
            }
        )
    )
    for r in q2:
        print(
            r.name,
            "ratio",
            r.best_ratio,
            r.high,
            "vs",
            r.low,
            "both cohorts",
            r.holds_in_both_cohorts,
            "passes",
            r.passes,
        )


if __name__ == "__main__":
    main()
