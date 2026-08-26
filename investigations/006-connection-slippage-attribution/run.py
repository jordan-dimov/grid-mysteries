"""Investigation 006 runner: join 005's TEC timelines to the TWR and run T1-T4.

Usage: uv run --with openpyxl --with xlrd python \
    investigations/006-connection-slippage-attribution/run.py

I/O and column mapping only; the declared logic lives in
grid_mysteries.investigations.twr_attribution and tec_slippage. TEC loading
reuses 005's runner so the population is identical to 005's.
"""

import csv
import importlib.util
import json
from collections import Counter
from dataclasses import asdict
from datetime import date
from pathlib import Path

from grid_mysteries.evidence import evidence_dir, write_json
from grid_mysteries.investigations.tec_slippage import (
    all_metrics,
    build_timelines,
    population,
)
from grid_mysteries.investigations.twr_attribution import (
    TwrVintage,
    attribute_revisions,
    match_schemes,
    parse_twr_row,
    project_schemes,
    scheme_completion_by_vintage,
    t1_measurability,
    t2_discrimination,
    t3_reclassification,
    t4_descriptive,
    works_flag,
)

ROOT = Path(__file__).resolve().parents[2]
TWR = ROOT / "data/raw/neso/twr"
EVIDENCE = evidence_dir(__file__)

spec = importlib.util.spec_from_file_location(
    "run005", ROOT / "investigations/005-connection-date-credibility/run.py"
)
run005 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run005)


def load_twr() -> list[TwrVintage]:
    import openpyxl

    vintages = []
    for entry in (
        json.loads(line)
        for line in (TWR / "journal.ndjson").read_text().splitlines()
        if line.strip()
    ):
        if not entry.get("t_public"):
            continue
        wb = openpyxl.load_workbook(ROOT / entry["path"], read_only=True, data_only=True)
        best: list[dict] = []
        for ws in wb.worksheets:
            rows = [list(r) for r in ws.iter_rows(values_only=True)]
            header_index = next(
                (
                    i
                    for i, r in enumerate(rows)
                    if r
                    and any(
                        str(c or "").strip() in ("Project", "Project Name", "Generator Name")
                        for c in r
                    )
                ),
                None,
            )
            if header_index is None:
                continue
            headers = [str(c or "").strip() for c in rows[header_index]]
            carry: dict[str, object] = {}
            records = []
            for r in rows[header_index + 1 :]:
                d = dict(zip(headers, r, strict=False))
                # project-level cells are merged in the workbook: forward-fill them
                for k in (
                    "Project",
                    "Project Name",
                    "Generator Name",
                    "Customer",
                    "Company Name",
                    "Account Name",
                    "Connection Site",
                    "Site",
                    "Project Number",
                ):
                    if k in d and d[k] not in (None, ""):
                        carry[k] = d[k]
                    elif k in d:
                        d[k] = carry.get(k)
                if any(v not in (None, "") for v in r):
                    records.append(d)
            if len(records) > len(best):
                best = records
        vintages.append(
            TwrVintage(date.fromisoformat(entry["t_public"]), tuple(parse_twr_row(r) for r in best))
        )
    return sorted(vintages, key=lambda v: v.t_public)


def tec_project_numbers(vintages) -> dict[str, str]:
    """005 key -> TEC 'Project No' where a vintage carries it (2023-02 onward)."""
    from grid_mysteries.investigations.tec_slippage import stage_keys

    numbers: dict[str, str] = {}
    for v in vintages:
        keys = stage_keys(v.rows, use_project_id=False)
        for key, row in zip(keys, v.rows, strict=True):
            number = str(row.get("Project No") or row.get("Project Number") or "").strip()
            if number:
                numbers[key] = number
    return numbers


def main() -> None:
    tec_vintages, _ = run005.load_vintages()
    old = [v for v in tec_vintages if v.t_public < run005.REGIME_CUTOFF]
    last_old = max(v.t_public for v in old)
    timelines = build_timelines(old, use_project_id=False)
    metrics = all_metrics(timelines, last_old)
    pop = population(metrics)
    numbers = tec_project_numbers(old)

    twr = load_twr()
    scheme_tl = scheme_completion_by_vintage(twr)
    index = project_schemes(twr)
    schemes = {m.key: match_schemes(m.key, index, numbers.get(m.key)) for m in pop}
    flags = {m.key: works_flag(m, schemes[m.key], scheme_tl) for m in pop}
    matched = [m for m in pop if flags[m.key] is not None]

    t1 = t1_measurability(twr, pop, flags)
    t2 = t2_discrimination(matched, flags)
    t3 = t3_reclassification(matched, flags)
    attributions = {
        m.key: attribute_revisions(timelines[m.key], schemes[m.key], scheme_tl) for m in pop
    }
    t4 = t4_descriptive(attributions, {m.key: m.first_status for m in pop}, scheme_tl, twr)

    # F-4: T2 within host TO, descriptive
    by_to = {}
    for to in sorted({m.host_to for m in matched}):
        sub = [m for m in matched if m.host_to == to]
        r = t2_discrimination(sub, flags)
        by_to[to] = {
            "n_flagged": r.n_flagged,
            "n_unflagged": r.n_unflagged,
            "rate_flagged": r.rate_flagged,
            "rate_unflagged": r.rate_unflagged,
            "gap": r.gap,
        }
    match_by = Counter()
    for m in pop:
        if flags[m.key] is None:
            match_by["unmatched"] += 1
        elif numbers.get(m.key) and index.get(f"pn:{numbers[m.key].upper()}"):
            match_by["project_number"] += 1
        else:
            match_by["name_or_customer_site"] += 1
    summary = {
        "twr_vintages": [v.t_public for v in twr],
        "twr_rows_per_vintage": {v.t_public.isoformat(): len(v.rows) for v in twr},
        "schemes_with_timeline": len(scheme_tl),
        "population_005": len(pop),
        "matched": len(matched),
        "match_route": dict(match_by),
        "flag_distribution": dict(
            Counter(
                "slipped" if f else ("clean" if f is False else "unmatched") for f in flags.values()
            )
        ),
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "t4": t4,
        "f4_t2_within_host_to": by_to,
        "verdict": {
            "T1": t1.passes,
            "T2": t2.passes,
            "T3": t3.passes,
            "pass": t1.passes and (t2.passes or t3.passes),
        },
    }
    write_json(EVIDENCE / "twr-attribution-summary.json", summary)
    with (ROOT / "data/derived/tec-history/attribution.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "key",
                "first_status",
                "host_to",
                "net_slip_months",
                "works_flag",
                "n_schemes",
                "t_public",
                "months",
                "outcome",
                "schemes_moved",
            ]
        )
        for m in pop:
            for a in attributions[m.key]:
                w.writerow(
                    [
                        m.key,
                        m.first_status,
                        m.host_to,
                        m.net_slip_months,
                        flags[m.key],
                        len(schemes[m.key]),
                        a.t_public,
                        a.months,
                        a.outcome,
                        ";".join(a.schemes_moved),
                    ]
                )
    print(
        json.dumps(
            {
                k: (asdict(v) if hasattr(v, "__dataclass_fields__") else v)
                for k, v in summary.items()
                if k not in ("twr_vintages", "twr_rows_per_vintage")
            },
            indent=1,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
