# ruff: noqa: E501
"""025 — The exit clock. Gated runner.

    uv run --group registers python investigations/025-the-exit-clock/run.py --phase acquire
    uv run --group registers python investigations/025-the-exit-clock/run.py --phase schema
    uv run --group registers python investigations/025-the-exit-clock/run.py --phase format
    uv run --group registers python investigations/025-the-exit-clock/run.py --phase compute --seal <prefix>
    uv run --group registers python investigations/025-the-exit-clock/run.py --phase render

- ``acquire`` pins the rules documents the declaration cites (Ofgem's
  CMP470 minded-to consultation and Initial Impact Assessment, NESO's CUSC
  Section 15, Exhibits MM1 and MM2, the Wider Cancellation Charge statement
  series and the securities-freeze letter of 15/01/2026) once, under
  ``data/raw/<publisher>/025/``, journalled in ``evidence/sources-journal.ndjson``
  and ``evidence/sources-manifest.json``. Authorised by the sponsor's prompt
  of 22/10/2026 (etrmbiz notes/2026-10-22-grid-mysteries-prompt-025-the-exit-clock.md).
  The register archive itself is 005's and is not refetched.
- ``schema`` (archive only, no network, before the declaration): every TEC
  copy the repository holds, its columns, blank rates of the columns the
  rules read, Project ID continuity between consecutive copies (the
  re-keying copies), the gaps between copies, the vocabularies of Project
  Status, Agreement Type and Plant Type. **No exit is counted**: a chain's
  last sighting is never read. Writes ``archives/025-exit-clock-inputs/``.
- ``format`` after the freeze, before compute: every copy's format as the
  reader depends on it against the schema report.
- ``compute`` under the frozen DECLARATION.md: chains, exits, clocks,
  bands, hazards, strata, reconciliation → ``evidence/chains.ndjson``
  (append-only), ``evidence/results.json``.
- ``render``: FINDINGS.md and the chart from results.json.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import jsonable, write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import exit_clock as ec
from grid_mysteries.sources import tec_register as tr
from grid_mysteries.sources.http import fetch_artifact
from grid_mysteries.sources.pinning import pin, progress
from grid_mysteries.tec import analysis
from grid_mysteries.tec import sources as tec_sources

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
RUN_LOG = EVIDENCE / "run-log.json"
ACQUISITION_LOG = EVIDENCE / "acquisition-log.json"
SOURCES_JOURNAL = EVIDENCE / "sources-journal.ndjson"
SOURCES_MANIFEST = EVIDENCE / "sources-manifest.json"
DECLARATION = HERE / "DECLARATION.md"
ARCHIVE = REPO_ROOT / "archives" / "025-exit-clock-inputs"
FETCH_DATE = "2026-10-22"
AUTHORISATION = (
    "sponsor prompt 22/10/2026 (etrmbiz notes/2026-10-22-grid-mysteries-prompt-025-the-exit-clock.md: "
    '"Pin the two Ofgem documents as evidence with digests ... and NESO\'s CUSC Section 15 ... plus the Wider Cancellation Charge statement series")'
)

RAW_OFGEM = REPO_ROOT / "data" / "raw" / "ofgem" / "025"
RAW_NESO = REPO_ROOT / "data" / "raw" / "neso" / "025"
RAW_DESNZ = REPO_ROOT / "data" / "raw" / "desnz" / "025"

#: dataset -> (publisher, url, destination). NESO's `/document/<id>/download`
#: URLs carry no suffix; the suffix here is the served content type's.
WCC_STATEMENTS = {
    "2012-13": 46301,
    "2013-14": 46276,
    "2014-15": 46086,
    "2015-16": 83106,
    "2016-17": 45771,
    "2017-18": 45761,
    "2018-19": 106896,
    "2019-20": 136891,
    "2020-21": 162256,
    "2021-22": 186131,
    "2022-23": 232551,
    "2023-24": 275641,
    "2024-25": 301936,
}
SOURCES: dict[str, tuple[str, str, Path]] = {
    "ofgem-cmp470-minded-to-consultation": (
        "ofgem",
        "https://www.ofgem.gov.uk/sites/default/files/2026-09/CMP470-Minded-to-Consultation.pdf",
        RAW_OFGEM / "CMP470-Minded-to-Consultation.pdf",
    ),
    "ofgem-cmp470-initial-impact-assessment": (
        "ofgem",
        "https://www.ofgem.gov.uk/sites/default/files/2026-09/CMP470-Interim-Impact-Assessment.pdf",
        RAW_OFGEM / "CMP470-Interim-Impact-Assessment.pdf",
    ),
    "ofgem-cmp470-consultation-page": (
        "ofgem",
        "https://www.ofgem.gov.uk/consultation/connection-and-use-system-code-cusc-cmp470-introducing-oversubscribed-technologies-commitment-fee-otcf",
        RAW_OFGEM / f"cmp470-consultation-page-{FETCH_DATE}.html",
    ),
    "neso-cusc-section-15": (
        "neso",
        "https://www.neso.energy/document/91416/download",
        RAW_NESO / f"cusc-section-15-user-commitment-methodology-{FETCH_DATE}.pdf",
    ),
    "neso-cusc-exhibit-mm1-cancellation-charge-statement": (
        "neso",
        "https://www.neso.energy/document/91486/download",
        RAW_NESO / f"cusc-exhibit-mm1-cancellation-charge-statement-{FETCH_DATE}.pdf",
    ),
    "neso-cusc-exhibit-mm2-cancellation-charge-secured-amount": (
        "neso",
        "https://www.neso.energy/document/91491/download",
        RAW_NESO / f"cusc-exhibit-mm2-cancellation-charge-secured-amount-{FETCH_DATE}.pdf",
    ),
    "neso-securities-freeze-letter-2026-01-15": (
        "neso",
        "https://www.neso.energy/document/375916/download",
        RAW_NESO / "securities-freeze-letter-2026-01-15.pdf",
    ),
    "neso-cusc-code-documents-page": (
        "neso",
        "https://www.neso.energy/industry-information/codes/connection-and-use-system-code-cusc/cusc-code-documents",
        RAW_NESO / f"cusc-code-documents-page-{FETCH_DATE}.html",
    ),
    "neso-reports-and-registers-page-1": (
        "neso",
        "https://www.neso.energy/industry-information/connections/reports-and-registers",
        RAW_NESO / f"reports-and-registers-page-1-{FETCH_DATE}.html",
    ),
    # The joins' sources (prompt of 22/10/2026, "Joins, declared with the rest"):
    # DESNZ's REPD quarterly extract and NESO's Capacity Market Register.
    # Companies House is 019's held join; the DNO registers are the held
    # demand-sources archives.
    "desnz-repd-quarterly-extract-2026-q2": (
        "desnz",
        "https://assets.publishing.service.gov.uk/media/6a6cbdc00c36759b5ccaa305/REPD_Publication_Q2_2026.csv",
        RAW_DESNZ / "REPD_Publication_Q2_2026.csv",
    ),
    "desnz-repd-publication-page": (
        "desnz",
        "https://www.gov.uk/government/publications/renewable-energy-planning-database-quarterly-extract",
        RAW_DESNZ / f"repd-quarterly-extract-page-{FETCH_DATE}.html",
    ),
    "neso-capacity-market-register-package": (
        "neso",
        "https://api.neso.energy/api/3/action/package_show?id=capacity-market-register",
        RAW_NESO / f"capacity-market-register-package-show-{FETCH_DATE}.json",
    ),
    "neso-capacity-market-register-cmu": (
        "neso",
        "https://api.neso.energy/dataset/0b3ab475-5622-4465-8825-9d35d03bb28b/resource/25a5fa2e-873d-41c5-8aaf-fbc2b06d79e6/download/cmu_20261021.csv",
        RAW_NESO / "capacity-market-register-cmu_20261021.csv",
    ),
    "neso-capacity-market-register-components": (
        "neso",
        "https://api.neso.energy/dataset/0b3ab475-5622-4465-8825-9d35d03bb28b/resource/790f5fa0-f8eb-4d82-b98d-0d34d3e404e8/download/component_20261021.csv",
        RAW_NESO / "capacity-market-register-component_20261021.csv",
    ),
    "neso-capacity-market-register-cmu-history": (
        "neso",
        "https://api.neso.energy/dataset/0b3ab475-5622-4465-8825-9d35d03bb28b/resource/cd034839-73e7-4c37-b4e5-6ebea25627d8/download/cmu_changes_20261021.csv",
        RAW_NESO / "capacity-market-register-cmu_changes_20261021.csv",
    ),
    **{
        f"neso-wider-cancellation-charge-statement-{year}": (
            "neso",
            f"https://www.neso.energy/document/{doc}/download",
            RAW_NESO / f"wider-cancellation-charge-statement-{year}.pdf",
        )
        for year, doc in WCC_STATEMENTS.items()
    },
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


# --------------------------------------------------------------- acquire


def phase_acquire() -> None:
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
        label="025 sources",
        progress=progress,
        sleep_seconds=1.0,
    )
    try:
        log = json.loads(ACQUISITION_LOG.read_text())
    except OSError, json.JSONDecodeError:
        log = {"acquisitions": []}
    log["acquisitions"].append(
        {
            "at": datetime.now(UTC).isoformat(),
            "authorised_by": AUTHORISATION,
            "fetched": fetched,
            "verified_and_skipped": skipped,
            "files": {
                d: {
                    "path": str(p.relative_to(REPO_ROOT)),
                    "sha256": sha(p),
                    "bytes": p.stat().st_size,
                }
                for d, (_, _, p) in SOURCES.items()
            },
        }
    )
    write_json(ACQUISITION_LOG, log)
    log_run("acquire", fetched=fetched, skipped=skipped)


# ---------------------------------------------------------------- schema

SCHEMA_REPORT = ARCHIVE / "schema-report.json"
SCHEMA_MD = ARCHIVE / "SCHEMA.md"
#: Amendment 2's schema pass (continuation rule, series ended at SERIES_END),
#: written beside the declaration's report, which stays as it was.
ARCHIVE_A2 = ARCHIVE / "amendment-2"
SCHEMA_REPORT_A2 = ARCHIVE_A2 / "schema-report.json"
SCHEMA_MD_A2 = ARCHIVE_A2 / "SCHEMA.md"
GAP_DAYS = 30
#: A pair with more than this share of keys absent (but not a re-keying) is
#: listed in the schema report with its stitch outcome, counts only.
HIGH_CHURN = Decimal("0.05")


def load_copies(
    continuation: bool = False,
) -> tuple[list[tuple[tec_sources.Copy, cs.VintageInput]], list[dict[str, str]]]:
    """Every copy the repository holds (journal and daily capture), verified
    against its digest, with 014's required columns; unreadable copies are
    listed, not read. With `continuation` (Amendment 2, I11), rows printing no
    Project Name are read by `tec_register.continue_row`."""
    usable, skipped = [], []
    for copy in tec_sources.copies(REPO_ROOT):
        try:
            tec_sources.verify(copy)
            rows = tec_sources.read(copy, continuation=continuation)
        except Exception as exc:  # noqa: BLE001 - recorded, not hidden
            skipped.append({"t_public": copy.published_on.isoformat(), "error": repr(exc)[:160]})
            continue
        if not rows or any(c not in rows[0] for c in analysis.REQUIRED_COLUMNS):
            skipped.append(
                {
                    "t_public": copy.published_on.isoformat(),
                    "error": "no rows or required columns missing",
                }
            )
            continue
        usable.append(
            (
                copy,
                cs.VintageInput(
                    copy.published_on,
                    tuple(rows),
                    copy.sha256,
                    str(copy.path.relative_to(REPO_ROOT)),
                ),
            )
        )
    return usable, skipped


def kept_map(
    usable: list[cs.VintageInput],
) -> tuple[dict[date, analysis.Kept], list[dict[str, Any]]]:
    result = cs.series(usable, partial_export_rule=True)
    kept = {k.vintage.t_public: k for k in analysis.kept(usable, result)}
    suspects = result["suspect_copies"]
    return kept, suspects


def quantiles(values: list[Decimal]) -> dict[str, str]:
    if not values:
        return {}
    s = sorted(values)

    def q(p: float) -> str:
        return str(s[min(len(s) - 1, int(p * (len(s) - 1)))])

    return {"n": str(len(s)), "p50": q(0.5), "p90": q(0.9), "p99": q(0.99), "max": str(s[-1])}


def phase_schema(amended: bool = False) -> None:
    usable, skipped = load_copies(continuation=amended)
    if amended:
        usable = [(c, v) for c, v in usable if v.t_public <= SERIES_END]
    vintages = [v for _, v in usable]
    kept, suspects = kept_map(vintages)
    per_copy: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    continuities: list[ec.Continuity] = []
    rekeyings: list[dict[str, Any]] = []
    high_churn: list[dict[str, Any]] = []
    agreement_vocab: Counter[str] = Counter()
    status_vocab: Counter[str] = Counter()
    storage_spellings: Counter[str] = Counter()
    previous: tuple[date, dict[str, list[dict[str, object]]]] | None = None
    previous_date: date | None = None
    for copy, v in usable:
        rows = list(v.rows)
        k = kept.get(v.t_public)
        columns = sorted({c for c in rows[0] if c})
        blanks = {
            c: sum(1 for r in rows if not ec.text(r.get(c)))
            for c in ec.READ_COLUMNS
            if c in columns
        }
        keys = ec.keyed(rows, v.t_public)
        ids = [kk for kk in keys if kk.startswith("id:")]
        noid = [kk for kk in keys if kk.startswith("noid:")]
        multi = sum(1 for kk, rs in keys.items() if len(rs) > 1)
        for r in rows:
            agreement_vocab[ec.text(r.get("Agreement Type"))] += 1
            status_vocab[ec.text(r.get("Project Status"))] += 1
            pt = ec.text(r.get("Plant Type"))
            if ec._STORAGE.search(pt):
                storage_spellings[pt] += 1
        if previous_date is not None and (v.t_public - previous_date).days > GAP_DAYS:
            gaps.append(
                {
                    "from": previous_date.isoformat(),
                    "to": v.t_public.isoformat(),
                    "days": (v.t_public - previous_date).days,
                }
            )
        entry: dict[str, Any] = {
            "t_public": v.t_public.isoformat(),
            "sha256": v.sha256,
            "path": v.path,
            "source": copy.provenance.get("journal", copy.provenance.get("capture", {})).get(
                "source", "capture"
            ),
            "regime": "new" if v.t_public >= ec.REGIME_CUTOFF else "old",
            "kept": k is not None,
            "swapped": bool(k.swapped) if k else None,
            "rows": len(rows),
            **(
                {"continuation_rows": tr.unnamed_rows(copy.path, copy.file_format)}
                if amended
                else {}
            ),
            "chains": len(keys),
            "id_chains": len(ids),
            "noid_chains": len(noid),
            "multi_row_chains": multi,
            "columns": columns,
            "blank": blanks,
        }
        if k is not None:
            if previous is not None:
                c = ec.continuity(previous[0], v.t_public, set(previous[1]), set(keys))
                continuities.append(c)
                entry["absent_share_vs_previous_kept"] = (
                    None  # not recorded per copy: it is the series
                )
                if c.rekeying or c.absent_share > HIGH_CHURN:
                    vanished = {kk: rs for kk, rs in previous[1].items() if kk not in keys}
                    appeared = {kk: rs for kk, rs in keys.items() if kk not in previous[1]}
                    st = ec.stitch(vanished, appeared)
                    (rekeyings if c.rekeying else high_churn).append(
                        {
                            "earlier": c.earlier.isoformat(),
                            "later": c.later.isoformat(),
                            "keys_earlier": c.keys_earlier,
                            "keys_later": c.keys_later,
                            "absent_from_later": c.absent_from_later,
                            "new_in_later": c.new_in_later,
                            "absent_share": str(c.absent_share),
                            "id_prefixes_earlier": dict(
                                Counter(
                                    kk[3:6] for kk in previous[1] if kk.startswith("id:")
                                ).most_common(3)
                            ),
                            "id_prefixes_later": dict(
                                Counter(kk[3:6] for kk in keys if kk.startswith("id:")).most_common(
                                    3
                                )
                            ),
                            "stitch": st.counts(),
                        }
                    )
            previous = (v.t_public, keys)
        previous_date = v.t_public
        per_copy.append(entry)
    shares = [c.absent_share for c in continuities if not c.rekeying]
    new_shares = [
        (Decimal(c.new_in_later) / Decimal(c.keys_later)).quantize(Decimal("0.0001"))
        for c in continuities
        if not c.rekeying and c.keys_later
    ]
    pn_rows = [e for e in per_copy if "Project Number" in e["columns"]]
    report = {
        "investigation": "025-the-exit-clock",
        "written_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "purpose": "schema pass: formats, keys, continuity and vocabularies of every TEC copy held; no chain's last sighting is read and no exit is counted",
        **(
            {
                "reading": "Amendment 2: rows printing no Project Name read by tec_register.continue_row (I11); copies to the series end only",
                "series_end": SERIES_END.isoformat(),
                "continuation_rows": sum(e.get("continuation_rows", 0) for e in per_copy),
            }
            if amended
            else {}
        ),
        "copies_usable": len(usable),
        "copies_unreadable": skipped,
        "copies_kept": sum(1 for e in per_copy if e["kept"]),
        "first": per_copy[0]["t_public"],
        "last": per_copy[-1]["t_public"],
        "regime_cutoff": ec.REGIME_CUTOFF.isoformat(),
        "id_era_from": ec.ID_ERA_FROM.isoformat(),
        "suspect_copies": [{**s, "t_public": s["t_public"].isoformat()} for s in suspects],
        "gaps_over_30_days": gaps,
        "largest_gap_days": max((g["days"] for g in gaps), default=0),
        "continuity_pairs": len(continuities),
        "rekeying_threshold": str(ec.REKEY_SHARE),
        "rekeyings": rekeyings,
        "high_churn_threshold": str(HIGH_CHURN),
        "high_churn_pairs": high_churn,
        "absent_share_non_rekeying_pairs": quantiles(shares),
        "new_share_non_rekeying_pairs": quantiles(new_shares),
        "project_number_first_copy": pn_rows[0]["t_public"] if pn_rows else None,
        "agreement_type_vocabulary": dict(agreement_vocab.most_common()),
        "project_status_vocabulary": dict(status_vocab.most_common()),
        "storage_plant_type_spellings": dict(storage_spellings.most_common()),
        "per_copy": per_copy,
    }
    out_dir, out_json, out_md = (
        (ARCHIVE_A2, SCHEMA_REPORT_A2, SCHEMA_MD_A2)
        if amended
        else (ARCHIVE, SCHEMA_REPORT, SCHEMA_MD)
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_json, report)
    out_md.write_text(render_schema(report))
    log_run(
        "schema-a2" if amended else "schema",
        copies=len(usable),
        kept=report["copies_kept"],
        rekeyings=len(rekeyings),
        report_sha256=sha(out_json),
    )
    print(
        f"{len(usable)} copies, {report['copies_kept']} kept, {len(rekeyings)} re-keying pairs, largest gap {report['largest_gap_days']} days -> {out_dir.relative_to(REPO_ROOT)}"
    )


def render_schema(r: dict[str, Any]) -> str:
    L = [
        "# Schema report: 025 exit-clock inputs (every TEC Register copy held)",
        "",
        f"Written {r['written_at'][:10]} by `run.py --phase schema`; `schema-report.json` beside this file has every copy. "
        f"{r['copies_usable']} usable copies from {r['first']} to {r['last']} ({r['copies_kept']} kept under 014's partial-export rule), "
        f"{len(r['copies_unreadable'])} unreadable. **No exit is counted here**: the continuity figures below are aggregates over copy pairs, "
        "never a dated series, and no chain's last sighting is read.",
        "",
        "## Copies and gaps",
        "",
        f"- Project ID printed from {r['id_era_from']}; Project Number from {r['project_number_first_copy']}; regime break {r['regime_cutoff']}.",
        f"- Largest gap between consecutive usable copies: **{r['largest_gap_days']} days**. Gaps over 30 days:",
        "",
        "| from | to | days |",
        "|---|---|---|",
    ]
    L += [f"| {g['from']} | {g['to']} | {g['days']} |" for g in r["gaps_over_30_days"]]
    L += [
        "",
        f"- Suspect copies under the partial-export rule: {len(r['suspect_copies'])} "
        f"({sum(1 for s in r['suspect_copies'] if s['excluded'])} excluded).",
        "",
        "## Key continuity between consecutive kept copies",
        "",
        f"{r['continuity_pairs']} pairs. A pair in which more than {r['rekeying_threshold']} of the earlier copy's chain keys are absent from the later copy is a **re-keying**:",
        "",
        "| earlier | later | keys earlier | keys later | absent | new | absent share | id prefixes earlier | id prefixes later | stitch |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for k in r["rekeyings"]:
        L.append(
            f"| {k['earlier']} | {k['later']} | {k['keys_earlier']} | {k['keys_later']} | {k['absent_from_later']} | {k['new_in_later']} | {k['absent_share']} | {k['id_prefixes_earlier']} | {k['id_prefixes_later']} | {k['stitch']} |"
        )
    L += [
        "",
        f"Pairs that are not re-keyings but lose more than {r['high_churn_threshold']} of their keys, with the stitch's outcome on the vanished and appeared chains (counts only):",
        "",
        "| earlier | later | keys earlier | absent | new | absent share | stitch |",
        "|---|---|---|---|---|---|---|",
    ]
    for k in r["high_churn_pairs"]:
        L.append(
            f"| {k['earlier']} | {k['later']} | {k['keys_earlier']} | {k['absent_from_later']} | {k['new_in_later']} | {k['absent_share']} | {k['stitch']} |"
        )
    L += [
        "",
        f"Over the other pairs, the share of the earlier copy's keys absent from the later copy: {r['absent_share_non_rekeying_pairs']}; "
        f"the share of the later copy's keys new: {r['new_share_non_rekeying_pairs']}.",
        "",
        "## Vocabularies (cells, all usable copies)",
        "",
        "### Agreement Type",
        "",
        "| printed | cells |",
        "|---|---|",
    ]
    L += [f"| {k or '(blank)'} | {v} |" for k, v in r["agreement_type_vocabulary"].items()]
    L += ["", "### Project Status", "", "| printed | cells |", "|---|---|"]
    L += [f"| {k or '(blank)'} | {v} |" for k, v in r["project_status_vocabulary"].items()]
    L += [
        "",
        "### Plant Type spellings that print a storage technology",
        "",
        "| printed | cells |",
        "|---|---|",
    ]
    L += [f"| {k} | {v} |" for k, v in r["storage_plant_type_spellings"].items()]
    L += [
        "",
        "## Per copy (first and last five; every copy in schema-report.json)",
        "",
        "| t_public | regime | kept | rows | chains | id chains | no-id chains | multi-row chains | blank Project Status | blank Plant Type | blank Agreement Type | blank MW Effective From |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    shown = r["per_copy"][:5] + r["per_copy"][-5:]
    for e in shown:
        b = e["blank"]
        L.append(
            f"| {e['t_public']} | {e['regime']} | {e['kept']} | {e['rows']} | {e['chains']} | {e['id_chains']} | {e['noid_chains']} | {e['multi_row_chains']} | {b.get('Project Status', 'n/a')} | {b.get('Plant Type', 'n/a')} | {b.get('Agreement Type', 'n/a')} | {b.get('MW Effective From', 'n/a')} |"
        )
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- format

FORMAT_CHECK = EVIDENCE / "format-check.json"
DECLARATION_SHA256 = "bc05298419069041ae21b75d0fc556f5ecb48224eb947806325f704f4eb4cd78"
#: Amendment 1 of the reading (22/10/2026, night): I10, the admissible row.
AMENDMENT_1 = HERE / "AMENDMENT-1.md"
AMENDMENT_1_SHA256 = "4a76ec63daa74f697ba353ae636392ff4eb3e9e1af836aa9522a00ff3dbecce5"
#: The results computed under the declaration alone (945cfda), kept so the
#: amended compute can list every leaf that moved with its old and new value.
RESULTS_ALONE = EVIDENCE / "results-declaration-alone.json"
#: Amendment 2 of the reading (28/10/2026): I11, the continuation rule, and
#: I12, the 76 copies journalled on 28/10/2026. The results computed under the
#: declaration and Amendment 1 (305dbe8) are kept so every moved leaf is listed.
AMENDMENT_2 = HERE / "AMENDMENT-2.md"
AMENDMENT_2_SHA256 = "c0973a617cdbed240dd121ccf8e248128f014face16ffec3016f5bead3d0ce2e"
RESULTS_A1 = EVIDENCE / "results-amendment-1.json"
SCHEMA_A2_SHA256_PREFIX = "15711a92f8c5a67a"
SCHEMA_SHA256_PREFIX = "fa3cbb802f61d3b6"
SERIES_END = date(2026, 10, 20)
JOIN_ARCHIVES = {
    "desnz-repd-quarterly-extract-2026-q2": REPO_ROOT / "archives" / "025-repd-2026-q2",
    "neso-capacity-market-register-cmu": REPO_ROOT / "archives" / "025-cmr-cmu",
    "neso-capacity-market-register-components": REPO_ROOT / "archives" / "025-cmr-components",
    "neso-capacity-market-register-cmu-history": REPO_ROOT / "archives" / "025-cmr-cmu-history",
}


def check_manifest() -> dict[str, str]:
    """C2: every pinned file hashes to the manifest; returns dataset -> sha."""
    manifest = json.loads(SOURCES_MANIFEST.read_text())
    out = {}
    for entry in manifest:
        path = REPO_ROOT / entry["path"]
        digest = sha(path)
        if digest != entry["sha256"]:
            sys.exit(f"C2: {entry['path']} no longer hashes to the manifest")
        out[entry["dataset"]] = digest
    return out


def check_schema_report() -> str:
    """C2 against Amendment 2's schema report; the declaration's report
    (SCHEMA_SHA256_PREFIX) is checked to still be the one it cites."""
    if not sha(SCHEMA_REPORT).startswith(SCHEMA_SHA256_PREFIX):
        sys.exit(f"C2: the declaration's schema report no longer hashes to {SCHEMA_SHA256_PREFIX}")
    digest = sha(SCHEMA_REPORT_A2)
    if not digest.startswith(SCHEMA_A2_SHA256_PREFIX):
        sys.exit(
            f"C2: Amendment 2's schema report hashes to {digest[:16]}, the amendment cites {SCHEMA_A2_SHA256_PREFIX}"
        )
    return digest


def csv_header(path: Path) -> list[str]:
    import csv

    with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        return next(csv.reader(f), [])


def phase_format() -> None:
    """Every copy's format as the reader depends on it (columns, row count)
    against the schema report; every join file's header against its schema
    report; every pinned file's digest against the manifest."""
    check_manifest()
    report_sha = check_schema_report()
    report = json.loads(SCHEMA_REPORT_A2.read_text())
    expected = {e["t_public"]: e for e in report["per_copy"]}
    usable, skipped = load_copies(continuation=True)
    differences: list[dict[str, Any]] = []
    for _copy, v in usable:
        if v.t_public > SERIES_END:
            continue
        e = expected.get(v.t_public.isoformat())
        if e is None:
            differences.append(
                {"t_public": v.t_public.isoformat(), "departure": "copy not in the schema report"}
            )
            continue
        columns = sorted({c for c in v.rows[0] if c})
        if columns != e["columns"] or len(v.rows) != e["rows"] or v.sha256 != e["sha256"]:
            differences.append(
                {
                    "t_public": v.t_public.isoformat(),
                    "departure": "columns, rows or digest differ from the schema report",
                }
            )
    if len([v for _, v in usable if v.t_public <= SERIES_END]) != report["copies_usable"]:
        differences.append(
            {
                "departure": f"usable copies {len(usable)} against {report['copies_usable']} in the report"
            }
        )
    later = [v.t_public.isoformat() for _, v in usable if v.t_public > SERIES_END]
    files = {}
    for dataset, archive in JOIN_ARCHIVES.items():
        path = SOURCES[dataset][2]
        arch = json.loads((archive / "schema-report.json").read_text())
        header = csv_header(path)
        expected_cols = [c["name"] for c in arch["columns"]]
        files[dataset] = {
            "sha256": sha(path),
            "header_matches_schema_report": header == expected_cols,
            "columns": len(header),
        }
        if header != expected_cols or sha(path) != arch["sha256"]:
            differences.append(
                {"dataset": dataset, "departure": "header or digest differs from its schema report"}
            )
    out = {
        "checked_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "declaration_sha256": DECLARATION_SHA256,
        "schema_report_sha256": report_sha,
        "series_end": SERIES_END.isoformat(),
        "copies_checked": len([v for _, v in usable if v.t_public <= SERIES_END]),
        "copies_after_series_end_not_read": later,
        "unreadable": skipped,
        "join_files": files,
        "differences": differences,
    }
    write_json(FORMAT_CHECK, out)
    log_run("format", differences=len(differences), copies=out["copies_checked"])
    print(
        f"format check: {out['copies_checked']} copies, {len(files)} join files, {len(differences)} differences -> {FORMAT_CHECK.relative_to(REPO_ROOT)}"
    )
    if differences:
        for d in differences:
            print("  ", d)
        sys.exit(1)


# --------------------------------------------------------------- compute

#: The chain lines of the computes under the declaration and Amendment 1,
#: kept untouched; Amendment 2's compute writes its own append-only file.
CHAINS_A1 = EVIDENCE / "chains.ndjson"
CHAINS = EVIDENCE / "amendment-2" / "chains.ndjson"
#: Exits rendered from this compute's chains, beside them: the compute under
#: Amendment 1 rewrote one shared file and its exits were lost on 28/10/2026.
EXITS = EVIDENCE / "amendment-2" / "exits.ndjson"
RESULTS_JSON = EVIDENCE / "results.json"
CLOCKS = ("A", "B", "C")
STATE_FIELDS = (
    "key",
    "rows",
    "status",
    "plant_type",
    "agreement",
    "host_to",
    "stage_mw",
    "cumulative_mw",
    "connection",
    "gate",
    "name",
    "customer",
    "site",
    "project_number",
)


def sealed_declaration(seal: str | None) -> str:
    digest = sha(DECLARATION)
    if digest != DECLARATION_SHA256:
        sys.exit(
            f"DECLARATION.md hashes to {digest[:8]}…, the runner expects {DECLARATION_SHA256[:8]}…"
        )
    if not seal or not digest.startswith(seal):
        sys.exit(f"compute needs --seal, the prefix of DECLARATION.md's SHA-256 ({digest[:8]}…)")
    if not (HERE / "DECLARATION.md.timestamps.json").exists():
        sys.exit("DECLARATION.md is not frozen (no proof sidecar)")
    a1 = sha(AMENDMENT_1)
    if a1 != AMENDMENT_1_SHA256:
        sys.exit(
            f"AMENDMENT-1.md hashes to {a1[:8]}…, the runner expects {AMENDMENT_1_SHA256[:8]}…"
        )
    if not (HERE / "AMENDMENT-1.md.timestamps.json").exists():
        sys.exit("AMENDMENT-1.md is not frozen (no proof sidecar)")
    a2 = sha(AMENDMENT_2)
    if a2 != AMENDMENT_2_SHA256:
        sys.exit(
            f"AMENDMENT-2.md hashes to {a2[:8]}…, the runner expects {AMENDMENT_2_SHA256[:8]}…"
        )
    if not (HERE / "AMENDMENT-2.md.timestamps.json").exists():
        sys.exit("AMENDMENT-2.md is not frozen (no proof sidecar)")
    return digest


def flatten(value: Any, path: str = "") -> dict[str, Any]:
    """Every leaf of a JSON value by its path, lists by index."""
    out: dict[str, Any] = {}
    if isinstance(value, dict):
        for k, v in value.items():
            out.update(flatten(v, f"{path}/{k}" if path else str(k)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            out.update(flatten(v, f"{path}[{i}]"))
    else:
        out[path] = value
    return out


def moved_leaves(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    """Amendments 1 and 2: the leaves whose value differs between two results
    files, with the old and new value, excluding the clock and the amendment blocks."""
    skip = ("computed_at", "amendments", "amendment_1", "amendment_2")
    b = {k: v for k, v in flatten(before).items() if not k.startswith(skip)}
    a = {k: v for k, v in flatten(after).items() if not k.startswith(skip)}
    moved = []
    for k in sorted(set(b) | set(a)):
        if b.get(k, "(absent)") != a.get(k, "(absent)"):
            moved.append({"leaf": k, "before": b.get(k, "(absent)"), "after": a.get(k, "(absent)")})
    return moved


class Chain:
    """One chain: its runs of unchanged state over consecutive kept copies,
    its key changes, interruptions and flags. Built by `build_chains`."""

    def __init__(self, chain_id: str, first_index: int) -> None:
        self.id = chain_id
        self.first_index = first_index
        self.runs: list[dict[str, Any]] = []
        self.key_changes: list[dict[str, str]] = []
        self.interruptions = 0
        self.stage_reductions = 0
        self.not_determinable = False
        self.nd_at: date | None = None
        self.last_index = -1
        self.sightings = 0

    def add(self, s: ec.Sighting, index: int) -> None:
        state = {f: getattr(s, f) for f in STATE_FIELDS}
        if self.runs and self.last_index == index - 1 and self.runs[-1]["state"] == state:
            self.runs[-1]["last_t"] = s.t_public
            self.runs[-1]["last_sha"] = s.sha256
            self.runs[-1]["copies"] += 1
        else:
            if self.runs and self.last_index != index - 1:
                self.interruptions += 1
            if self.runs and state["rows"] < self.runs[-1]["state"]["rows"]:
                self.stage_reductions += 1
            self.runs.append(
                {
                    "first_t": s.t_public,
                    "last_t": s.t_public,
                    "first_sha": s.sha256,
                    "last_sha": s.sha256,
                    "copies": 1,
                    "state": state,
                }
            )
        self.last_index = index
        self.sightings += 1
        self.not_determinable = False
        self.nd_at = None

    @property
    def first(self) -> dict[str, Any]:
        return self.runs[0]

    @property
    def last(self) -> dict[str, Any]:
        return self.runs[-1]

    def present_at(self, t: date) -> dict[str, Any] | None:
        for r in self.runs:
            if r["first_t"] <= t <= r["last_t"]:
                return r
        return None

    def state_in_month(self, month: date) -> dict[str, Any]:
        """The run active in a calendar month: the latest run that began on or
        before the month's last day (K2, clock C)."""
        end = date(month.year + (month.month // 12), month.month % 12 + 1, 1)
        chosen = self.runs[0]
        for r in self.runs:
            if r["first_t"] < end:
                chosen = r
            else:
                break
        return chosen["state"]

    def families(self) -> list[str]:
        return [ec.plant_family(r["state"]["plant_type"]) for r in self.runs]

    def reclassified(self) -> bool:
        fams = [f for f in self.families() if f != "blank"]
        return len(set(fams)) > 1

    def as_line(self) -> dict[str, Any]:
        return {
            "chain": self.id,
            "first_t": self.first["first_t"],
            "last_t": self.last["last_t"],
            "sightings": self.sightings,
            "runs": self.runs,
            "key_changes": self.key_changes,
            "interruptions": self.interruptions,
            "stage_reductions": self.stage_reductions,
            "not_determinable": self.not_determinable,
            "nd_at": self.nd_at,
        }


def build_chains(
    sequence: list[analysis.Kept],
) -> tuple[dict[str, Chain], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """I1 to I9 over the kept copies in publication order, I10 before keying."""
    chains: dict[str, Chain] = {}
    admission: dict[str, Any] = {"refused_rows": [], "sparse_rows": []}
    chain_by_key: dict[str, str] = {}
    seen_key_chain: dict[str, str] = {}
    prev_keys: dict[str, list[dict[str, object]]] = {}
    prev_t: date | None = None
    pair_log: list[dict[str, Any]] = []
    reused_keys: list[dict[str, Any]] = []
    for index, k in enumerate(sequence):
        t = k.vintage.t_public
        rows, refused = ec.admit(list(k.vintage.rows))
        if refused:
            admission["refused_rows"].append(
                {"t_public": t.isoformat(), "sha256": k.vintage.sha256, "refused": refused}
            )
        for r in rows:
            if len(ec.fields_printed(r)) == 1:
                admission["sparse_rows"].append(
                    {
                        "t_public": t.isoformat(),
                        "fields": ["Project Name", *ec.fields_printed(r)],
                        "key": ec.row_key(r, t),
                    }
                )
        keys = ec.keyed(rows, t)
        mapping: dict[str, str] = {}
        claimed: set[str] = set()
        vanished = {kk: rs for kk, rs in prev_keys.items() if kk not in keys}
        appeared = {kk: rs for kk, rs in keys.items() if kk not in prev_keys}
        # I3: continuing keys claim their chains first.
        for kk in keys:
            if kk in prev_keys:
                mapping[kk] = chain_by_key[kk]
                claimed.add(chain_by_key[kk])
        # I9: a key seen before returns to its chain, unless that chain is
        # already printed in this copy under another key (then the row is a
        # different project reusing a key, and is new).
        returned = 0
        for kk in list(appeared):
            cid = seen_key_chain.get(kk)
            if cid is not None and cid not in claimed:
                mapping[kk] = cid
                claimed.add(cid)
                returned += 1
                del appeared[kk]
            elif cid is not None:
                under = next(k2 for k2, c2 in mapping.items() if c2 == cid)
                reused_keys.append(
                    {
                        "t_public": t.isoformat(),
                        "key": kk,
                        "chain": cid,
                        "chain_printed_under": under,
                        "era": "id" if ec.is_id_era(t) else "pre-id",
                    }
                )
        st = ec.stitch(vanished, appeared)
        c = ec.continuity(prev_t or t, t, set(prev_keys), set(keys)) if prev_t else None
        rekeying = bool(c and c.rekeying)
        tier_counts = Counter(st.tier_of.values())
        fresh = list(st.unmatched_new) + list(st.ambiguous_new)
        for new_key, old_key in st.matched.items():
            cid = chain_by_key[old_key]
            if cid in claimed:
                fresh.append(new_key)
                reused_keys.append(
                    {
                        "t_public": t.isoformat(),
                        "key": new_key,
                        "chain": cid,
                        "chain_printed_under": next(k2 for k2, c2 in mapping.items() if c2 == cid),
                        "era": "id" if ec.is_id_era(t) else "pre-id",
                        "via": f"stitch tier {st.tier_of[new_key]} to {old_key}",
                    }
                )
                continue
            mapping[new_key] = cid
            claimed.add(cid)
            chains[cid].key_changes.append(
                {
                    "t_public": t.isoformat(),
                    "from": old_key,
                    "to": new_key,
                    "tier": st.tier_of[new_key],
                }
            )
        for new_key in fresh:
            cid = f"{new_key}@{t.isoformat()}"
            chains[cid] = Chain(cid, index)
            mapping[new_key] = cid
        nd = 0
        if rekeying:
            for old_key in list(st.unmatched_old) + list(st.ambiguous_old):
                ch = chains[chain_by_key[old_key]]
                ch.not_determinable = True
                ch.nd_at = t
                nd += 1
        added: set[str] = set()
        for kk in keys:
            cid = mapping.get(kk)
            if cid is None:
                raise RuntimeError(f"{t}: key {kk} has no chain")
            if cid in added:
                raise RuntimeError(f"{t}: chain {cid} would be added twice in one copy (I2)")
            added.add(cid)
            chains[cid].add(
                ec.sighting(t, k.vintage.sha256, kk, keys[kk], swapped=k.swapped), index
            )
            seen_key_chain[kk] = cid
        if c is not None:
            pair_log.append(
                {
                    "earlier": c.earlier.isoformat(),
                    "later": t.isoformat(),
                    "rekeying": rekeying,
                    "vanished": len(vanished),
                    "appeared": len(appeared) + returned,
                    "returned_own_key": returned,
                    "stitched": len(st.matched),
                    "tiers": dict(tier_counts),
                    "new_chains": len(fresh),
                    "ambiguous_new": len(st.ambiguous_new),
                    "ambiguous_old": len(st.ambiguous_old),
                    "unmatched_old": len(st.unmatched_old),
                    "not_determinable": nd,
                }
            )
        chain_by_key = mapping
        prev_keys = keys
        prev_t = t
    for r in admission["sparse_rows"]:
        r["chain"] = seen_key_chain.get(r.pop("key"))
    return chains, pair_log, reused_keys, admission


def strata_of(state: dict[str, Any], first_t: date) -> dict[str, str]:
    fam = ec.plant_family(state["plant_type"])
    return {
        "family": fam,
        "storage": "storage" if fam in ("storage-only", "storage-mixed") else "other",
        "status": ec.status_family(state["status"]),
        "agreement": ec.agreement_family(state["agreement"]),
        "host_to": ec.text(state["host_to"]) or "(blank)",
        "cohort": "2014 opening" if first_t == date(2014, 1, 31) else str(first_t.year),
    }


def nested() -> Any:
    return defaultdict(nested)


def phase_compute(seal: str | None) -> None:
    declaration = sealed_declaration(seal)
    manifest_shas = check_manifest()
    report_sha = check_schema_report()
    usable, skipped = load_copies(continuation=True)
    vintages = [v for _, v in usable if v.t_public <= SERIES_END]
    kept, suspects = kept_map(vintages)
    sequence = sorted(kept.values(), key=lambda k: k.vintage.t_public)
    copy_dates = [k.vintage.t_public for k in sequence]
    if copy_dates[-1] != SERIES_END:
        sys.exit(
            f"C1: the last kept copy is {copy_dates[-1]}, the declaration ends the series at {SERIES_END}"
        )
    chains, pair_log, reused_keys, admission = build_chains(sequence)
    exit_cutoff = SERIES_END - timedelta(days=ec.N_DAYS)

    # ---- classes (E1 to E3, I5), C3
    classes: Counter[str] = Counter()
    per_chain: dict[str, dict[str, Any]] = {}
    for cid, ch in chains.items():
        last = ch.last
        cls = ec.classify(
            last["last_t"],
            last["state"]["status"],
            series_end=SERIES_END,
            not_determinable=ch.not_determinable,
        )
        classes[cls] += 1
        per_chain[cid] = {"class": cls}
    if sum(classes.values()) != len(chains):
        sys.exit("C3: classes do not sum to the chains")

    # ---- not determinable by era (I8)
    era_counts: dict[str, Counter[str]] = {"pre-id": Counter(), "id": Counter()}
    for cid, ch in chains.items():
        era = "id" if ch.last["last_t"] >= ec.ID_ERA_FROM else "pre-id"
        era_counts[era]["chains"] += 1
        if per_chain[cid]["class"] == ec.NOT_DETERMINABLE:
            era_counts[era]["not_determinable"] += 1
    nd_share_id = Decimal(era_counts["id"]["not_determinable"]) / Decimal(
        era_counts["id"]["chains"] or 1
    )

    # ---- exits, bands, exposure, strata (E4, K2 to K5, S1 to S5, R1)
    exits: list[dict[str, Any]] = []
    expo: Any = nested()  # expo[dim][value][regime][clock][band] = months
    exits_by: Any = nested()  # exits_by[dim][value][regime][clock][band] = count
    monthly: Any = nested()
    total_exposure_months = 0
    reclassified: Counter[str] = Counter()
    for cid, ch in chains.items():
        cls = per_chain[cid]["class"]
        last_state = ch.last["state"]
        first_state = ch.first["state"]
        strata = strata_of(last_state, ch.first["first_t"])
        strata_pairs = [("all", "all"), *strata.items()]
        if strata["family"] == "storage-only":
            strata_pairs.append(("storage_only", "storage-only"))
        trig_a = ec.trigger_date(last_state["connection"]) if last_state["connection"] else None
        trig_b = ec.trigger_date(first_state["connection"]) if first_state["connection"] else None
        if ch.reclassified():
            reclassified["chains"] += 1
            if (
                strata["storage"] == "storage"
                or "storage" in {ec.plant_family(r["state"]["plant_type"]) for r in ch.runs}
                or any(f.startswith("storage") for f in ch.families())
            ):
                reclassified["touching storage"] += 1
        if cls == ec.NOT_DETERMINABLE:
            continue
        months = ec.months_in(ch.first["first_t"], ch.last["last_t"])
        total_exposure_months += len(months)
        for m in months:
            regime = ec.regime_of(m)
            conn_c = ch.state_in_month(m)["connection"]
            trig_c = ec.trigger_date(conn_c) if conn_c else None
            bands = {"A": ec.band(m, trig_a), "B": ec.band(m, trig_b), "C": ec.band(m, trig_c)}
            for dim, value in strata_pairs:
                for clock, b in bands.items():
                    cell = expo[dim][value][regime][clock]
                    cell[b] = cell.get(b, 0) + 1
        if cls != ec.EXIT:
            continue
        xc = ec.exit_copy(ch.last["last_t"], copy_dates)
        regime = ec.regime_of(xc)
        bands = {"A": ec.band(xc, trig_a), "B": ec.band(xc, trig_b), "C": ec.band(xc, trig_a)}
        months_to_trigger_a = ec.months_between(xc, trig_a) if trig_a else None
        for dim, value in strata_pairs:
            for clock, b in bands.items():
                cell = exits_by[dim][value][regime][clock]
                cell[b] = cell.get(b, 0) + 1
        month_key = xc.strftime("%Y-%m")
        mw = last_state["stage_mw"] or Decimal(0)
        mrow = monthly[month_key]
        for key, cond in (
            ("all", True),
            ("storage", strata["storage"] == "storage"),
            ("storage_only", strata["family"] == "storage-only"),
        ):
            if cond:
                mrow[key] = mrow.get(key, 0) + 1
                mrow[f"mw_{key}"] = mrow.get(f"mw_{key}", Decimal(0)) + mw
        exits.append(
            {
                "chain": cid,
                "regime": regime,
                "first_t": ch.first["first_t"].isoformat(),
                "last_t": ch.last["last_t"].isoformat(),
                "last_sha256": ch.last["last_sha"],
                "exit_copy": xc.isoformat(),
                "exit_month": month_key,
                "gap_days": (xc - ch.last["last_t"]).days,
                "connection_at_last": last_state["connection"].isoformat()
                if last_state["connection"]
                else None,
                "connection_at_first": first_state["connection"].isoformat()
                if first_state["connection"]
                else None,
                "trigger_a": trig_a.isoformat() if trig_a else None,
                "trigger_b": trig_b.isoformat() if trig_b else None,
                "months_to_trigger_a": months_to_trigger_a,
                "band_a": bands["A"],
                "band_b": bands["B"],
                **strata,
                "status_printed": last_state["status"],
                "plant_type_printed": last_state["plant_type"],
                "gate": last_state["gate"],
                "stage_mw": str(mw),
                "rows": last_state["rows"],
                "sightings": ch.sightings,
                "key_changes": len(ch.key_changes),
                "interruptions": ch.interruptions,
                "reclassified": ch.reclassified(),
                "join_key": {
                    "first": {
                        f: first_state[f]
                        for f in ("name", "customer", "site", "key", "project_number", "stage_mw")
                    },
                    "last": {
                        f: last_state[f]
                        for f in ("name", "customer", "site", "key", "project_number", "stage_mw")
                    },
                },
            }
        )
    # C4
    for dim in exits_by:
        for value in exits_by[dim]:
            for regime in exits_by[dim][value]:
                sums = {
                    clock: sum(exits_by[dim][value][regime][clock].values()) for clock in CLOCKS
                }
                if len(set(sums.values())) != 1:
                    sys.exit(f"C4: bands do not sum alike across clocks for {dim}={value} {regime}")
    exit_count = sum(1 for e in exits)
    if (
        sum(v for v in exits_by["all"]["all"]["old"]["A"].values())
        + sum(v for v in exits_by["all"]["all"]["new"]["A"].values())
        != exit_count
    ):
        sys.exit("C4: bands do not sum to exits")

    # ---- hazards (K5, K6)
    def hazard_table(dim: str, value: str, regime: str, clock: str) -> list[dict[str, Any]]:
        out = []
        for b in (*ec.BANDS, ec.UNDATED):
            k = exits_by[dim][value][regime][clock].get(b, 0) if value in exits_by[dim] else 0
            e = expo[dim][value][regime][clock].get(b, 0) if value in expo[dim] else 0
            iv = ec.byar_interval(k, Decimal(e))
            out.append(
                {
                    "band": b,
                    "exits": k,
                    "chain_months": e,
                    "hazard_per_chain_month": str(iv[0]) if iv else None,
                    "lower": str(iv[1]) if iv else None,
                    "upper": str(iv[2]) if iv else None,
                    "per_100_chain_years": str((iv[0] * 1200).quantize(Decimal("0.01")))
                    if iv
                    else None,
                    "per_100_chain_years_lower": str((iv[1] * 1200).quantize(Decimal("0.01")))
                    if iv
                    else None,
                    "per_100_chain_years_upper": str((iv[2] * 1200).quantize(Decimal("0.01")))
                    if iv
                    else None,
                }
            )
        return out

    def flatness(dim: str, value: str, regime: str, clock: str) -> bool | None:
        ivs = []
        for b in ec.BANDS:
            k = exits_by[dim][value][regime][clock].get(b, 0)
            e = expo[dim][value][regime][clock].get(b, 0)
            ivs.append(ec.byar_interval(k, Decimal(e)))
        return ec.flat(ivs)

    hazards: dict[str, Any] = {}
    for regime in ("old", "new"):
        hazards[regime] = {}
        for clock in CLOCKS:
            hazards[regime][clock] = {
                "all": hazard_table("all", "all", regime, clock),
                "storage": hazard_table("storage", "storage", regime, clock),
                "storage-only": hazard_table("storage_only", "storage-only", regime, clock),
                "other": hazard_table("storage", "other", regime, clock),
            }
    storage_strata: dict[str, Any] = {}
    # Strata tables over storage chains: a second accumulation restricted to storage.
    s_expo: Any = nested()
    s_exits: Any = nested()
    for cid, ch in chains.items():
        cls = per_chain[cid]["class"]
        if cls == ec.NOT_DETERMINABLE:
            continue
        last_state = ch.last["state"]
        strata = strata_of(last_state, ch.first["first_t"])
        if strata["storage"] != "storage":
            continue
        trig_a = ec.trigger_date(last_state["connection"]) if last_state["connection"] else None
        for m in ec.months_in(ch.first["first_t"], ch.last["last_t"]):
            if ec.regime_of(m) != "old":
                continue
            b = ec.band(m, trig_a)
            for dim in ("status", "agreement", "host_to", "cohort"):
                cell = s_expo[dim][strata[dim]]
                cell[b] = cell.get(b, 0) + 1
        if cls == ec.EXIT:
            xc = ec.exit_copy(ch.last["last_t"], copy_dates)
            if ec.regime_of(xc) == "old":
                b = ec.band(xc, trig_a)
                for dim in ("status", "agreement", "host_to", "cohort"):
                    cell = s_exits[dim][strata[dim]]
                    cell[b] = cell.get(b, 0) + 1
    for dim in ("status", "agreement", "host_to", "cohort"):
        storage_strata[dim] = {}
        for value in sorted(set(s_expo[dim]) | set(s_exits[dim])):
            rows_out = []
            for b in (*ec.BANDS, ec.UNDATED):
                k = s_exits[dim][value].get(b, 0)
                e = s_expo[dim][value].get(b, 0)
                iv = ec.byar_interval(k, Decimal(e))
                rows_out.append(
                    {
                        "band": b,
                        "exits": k,
                        "chain_months": e,
                        "per_100_chain_years": str((iv[0] * 1200).quantize(Decimal("0.01")))
                        if iv
                        else None,
                        "lower": str((iv[1] * 1200).quantize(Decimal("0.01"))) if iv else None,
                        "upper": str((iv[2] * 1200).quantize(Decimal("0.01"))) if iv else None,
                    }
                )
            storage_strata[dim][value] = {
                "exits": sum(r["exits"] for r in rows_out),
                "chain_months": sum(r["chain_months"] for r in rows_out),
                "bands": rows_out,
            }

    storage_old_exits = sum(exits_by["storage"]["storage"]["old"]["A"].values())
    storage_only_old_exits = sum(exits_by["storage_only"]["storage-only"]["old"]["A"].values())

    # ---- reconciliation (O1, O2)
    def snapshot_on_or_after(d: date) -> date:
        return next(c for c in copy_dates if c >= d)

    snapshots = [
        snapshot_on_or_after(date(2023, 1, 1)),
        snapshot_on_or_after(date(2024, 1, 1)),
        snapshot_on_or_after(date(2025, 1, 1)),
        max(c for c in copy_dates if c < ec.REGIME_CUTOFF),
    ]
    o1 = []
    for s, s_next in zip(snapshots, snapshots[1:], strict=False):
        by_status: dict[str, Counter[str]] = defaultdict(Counter)
        for cid, ch in chains.items():
            r = ch.present_at(s)
            if r is None:
                continue
            fam = ec.plant_family(r["state"]["plant_type"])
            if fam not in ("storage-only", "storage-mixed"):
                continue
            st = ec.status_family(r["state"]["status"])
            by_status[st]["present"] += 1
            by_status["all"]["present"] += 1
            left = per_chain[cid]["class"] == ec.EXIT and ch.last["last_t"] < s_next
            if left:
                by_status[st]["left"] += 1
                by_status["all"]["left"] += 1
            r2 = ch.present_at(s_next)
            if r2 is not None and ec.plant_family(r2["state"]["plant_type"]) not in (
                "storage-only",
                "storage-mixed",
            ):
                by_status[st]["reclassified_away"] += 1
                by_status["all"]["reclassified_away"] += 1
            elif r2 is not None and ec.plant_family(r2["state"]["plant_type"]) != fam:
                by_status[st]["family_changed_within_storage"] += 1
                by_status["all"]["family_changed_within_storage"] += 1
        o1.append(
            {
                "snapshot": s.isoformat(),
                "next": s_next.isoformat(),
                "days": (s_next - s).days,
                "by_status": {
                    st: {
                        **dict(c),
                        "left_share": str(
                            (Decimal(c["left"]) / Decimal(c["present"])).quantize(Decimal("0.0001"))
                        )
                        if c["present"]
                        else None,
                    }
                    for st, c in sorted(by_status.items())
                },
            }
        )
    window_exits = [
        e for e in exits if "2023-01" <= e["exit_month"] <= "2025-11" and e["storage"] == "storage"
    ]
    o2 = {
        "window": "exit copies 2023-01-01 to 2025-11-30 (old regime)",
        "storage_exits": len(window_exits),
        "storage_only_exits": sum(1 for e in window_exits if e["family"] == "storage-only"),
        "by_status": dict(Counter(e["status"] for e in window_exits)),
        "by_exit_year": dict(Counter(e["exit_month"][:4] for e in window_exits)),
        "ofgem": {
            "exited_or_reclassified_2023_2025": 72,
            "per_year": "6.7%",
            "scoping_or_awaiting": "7.4%",
            "consents_approved": "3%",
            "under_construction": "0%",
        },
    }

    # ---- row counts through the break (R3)
    rows_through_break = [
        {"t_public": k.vintage.t_public.isoformat(), "rows": len(k.vintage.rows)}
        for k in sequence
        if date(2025, 10, 1) <= k.vintage.t_public <= date(2026, 3, 1)
    ]

    # ---- C5: chains.ndjson append-only; exits.ndjson rewritten from chains
    existing: dict[str, str] = {}
    if CHAINS.exists():
        for raw in CHAINS.read_text().splitlines():
            if raw.strip():
                existing[json.loads(raw)["chain"]] = raw
    held_alone = sorted(cid for cid in existing if cid not in chains)
    new_lines = []
    for cid in sorted(chains):
        line = json.dumps(chains[cid].as_line(), default=jsonable, sort_keys=True)
        if cid in existing:
            if existing[cid] != line:
                sys.exit(f"C5: chains.ndjson line {cid} would change on recompute")
        else:
            new_lines.append(line)
    CHAINS.parent.mkdir(parents=True, exist_ok=True)
    with CHAINS.open("a") as f:
        for line in new_lines:
            f.write(line + "\n")
    (EVIDENCE / "reused-keys.json").write_text(json.dumps(reused_keys, indent=1) + "\n")
    EXITS.write_text(
        "".join(
            json.dumps(e, default=jsonable, sort_keys=True) + "\n"
            for e in sorted(exits, key=lambda e: (e["exit_copy"], e["chain"]))
        )
    )

    results: dict[str, Any] = {
        "investigation": "025-the-exit-clock",
        "declaration_sha256": declaration,
        "schema_report_sha256": report_sha,
        "sources_manifest_sha256": sha(SOURCES_MANIFEST),
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "series": {
            "first_copy": copy_dates[0].isoformat(),
            "last_copy": SERIES_END.isoformat(),
            "kept_copies": len(sequence),
            "usable_copies": len(vintages),
            "unreadable": len(skipped),
            "suspect_copies": [{**s, "t_public": s["t_public"].isoformat()} for s in suspects],
            "n_days": ec.N_DAYS,
            "exit_cutoff": exit_cutoff.isoformat(),
        },
        "chains": {
            "total": len(chains),
            "classes": dict(classes),
            "by_era": {k: dict(v) for k, v in era_counts.items()},
            "not_determinable_share_id_era": str(nd_share_id.quantize(Decimal("0.0001"))),
            "kill_a_fired": nd_share_id > Decimal("0.10"),
            "reclassified": dict(reclassified),
            "stage_reductions": sum(ch.stage_reductions for ch in chains.values()),
            "interrupted_chains": sum(1 for ch in chains.values() if ch.interruptions),
            "key_changes": sum(len(ch.key_changes) for ch in chains.values()),
            "key_change_tiers": dict(
                Counter(kc["tier"] for ch in chains.values() for kc in ch.key_changes)
            ),
        },
        "reused_keys": {
            "count": len(reused_keys),
            "by_copy": dict(Counter(r["t_public"] for r in reused_keys)),
            "by_era": dict(Counter(r["era"] for r in reused_keys)),
            "via_stitch": sum(1 for r in reused_keys if "via" in r),
        },
        "pairs": {
            "count": len(pair_log),
            "rekeying": [p for p in pair_log if p["rekeying"]],
            "returned_own_key_total": sum(p["returned_own_key"] for p in pair_log),
            "stitched_total": sum(p["stitched"] for p in pair_log),
            "not_determinable_total": sum(p["not_determinable"] for p in pair_log),
        },
        "exits": {
            "total": exit_count,
            "old_regime": sum(1 for e in exits if e["regime"] == "old"),
            "new_regime": sum(1 for e in exits if e["regime"] == "new"),
            "storage_old_regime": storage_old_exits,
            "storage_only_old_regime": storage_only_old_exits,
            "kill_b_fired": storage_old_exits < 200,
            "by_class": {
                "family": dict(Counter(e["family"] for e in exits)),
                "status": dict(Counter(e["status"] for e in exits)),
                "agreement": dict(Counter(e["agreement"] for e in exits)),
                "host_to": dict(Counter(e["host_to"] for e in exits)),
                "cohort": dict(Counter(e["cohort"] for e in exits)),
                "regime": dict(Counter(e["regime"] for e in exits)),
            },
            "gap_days": {
                "median": sorted(e["gap_days"] for e in exits)[len(exits) // 2] if exits else None,
                "max": max((e["gap_days"] for e in exits), default=None),
            },
            "new_regime_by_gate": dict(
                Counter((e["gate"] or "(blank)") for e in exits if e["regime"] == "new")
            ),
            "new_regime_by_status": dict(
                Counter(e["status"] for e in exits if e["regime"] == "new")
            ),
        },
        "exposure": {"total_chain_months": total_exposure_months},
        "monthly": {
            m: {k: (str(v) if isinstance(v, Decimal) else v) for k, v in monthly[m].items()}
            for m in sorted(monthly)
        },
        "hazards": hazards,
        "flat": {
            "storage_old_A": flatness("storage", "storage", "old", "A"),
            "storage_old_B": flatness("storage", "storage", "old", "B"),
            "storage_old_C": flatness("storage", "storage", "old", "C"),
            "storage_only_old_A": flatness("storage_only", "storage-only", "old", "A"),
            "all_old_A": flatness("all", "all", "old", "A"),
            "other_old_A": flatness("storage", "other", "old", "A"),
        },
        "storage_strata_old_A": storage_strata,
        "months_to_trigger_histogram_storage_old": dict(
            sorted(
                Counter(
                    e["months_to_trigger_a"]
                    for e in exits
                    if e["regime"] == "old"
                    and e["storage"] == "storage"
                    and e["months_to_trigger_a"] is not None
                ).items()
            )
        ),
        "months_to_trigger_histogram_all_old": dict(
            sorted(
                Counter(
                    e["months_to_trigger_a"]
                    for e in exits
                    if e["regime"] == "old" and e["months_to_trigger_a"] is not None
                ).items()
            )
        ),
        "reconciliation": {"o1_snapshots": o1, "o2_window": o2},
        "rows_through_break": rows_through_break,
        "pinned": manifest_shas,
        "amendments": [
            {"n": 1, "file": "AMENDMENT-1.md", "sha256": AMENDMENT_1_SHA256},
            {"n": 2, "file": "AMENDMENT-2.md", "sha256": AMENDMENT_2_SHA256},
        ],
    }
    results["amendment_1"] = {
        "refused_rows": admission["refused_rows"],
        "rows_refused": sum(r["refused"] for r in admission["refused_rows"]),
        "sparse_rows_admitted": [
            {
                "t_public": r["t_public"],
                "fields": r["fields"],
                "chain_class": per_chain.get(r.get("chain") or "", {}).get("class", "(no chain)"),
            }
            for r in admission["sparse_rows"]
        ],
    }
    a1_copy_dates = {
        e["t_public"]
        for e in json.loads(SCHEMA_REPORT.read_text())["per_copy"]
        if e["t_public"] <= SERIES_END.isoformat()
    }
    results["amendment_2"] = {
        "continuation_rows_read": sum(
            tr.unnamed_rows(c.path, c.file_format)
            for c, v in usable
            if v.t_public <= SERIES_END and v.t_public in kept
        ),
        "copies_added": sorted(
            v.t_public.isoformat()
            for _, v in usable
            if v.t_public <= SERIES_END and v.t_public.isoformat() not in a1_copy_dates
        ),
        "chain_lines_held_from_amendment_1": sum(
            1 for line in CHAINS_A1.read_text().splitlines() if line.strip()
        ),
        "chains_not_rebuilt_from_held_file": len(held_alone),
        "moved": moved_leaves(json.loads(RESULTS_A1.read_text()), results),
    }
    write_json(RESULTS_JSON, results)
    log_run(
        "compute",
        declaration=declaration[:16],
        chains=len(chains),
        exits=exit_count,
        storage_old=storage_old_exits,
        nd_share_id=str(nd_share_id.quantize(Decimal("0.0001"))),
        new_chain_lines=len(new_lines),
    )
    print(
        f"{len(chains)} chains; classes {dict(classes)}; exits {exit_count} (old {results['exits']['old_regime']}, storage old {storage_old_exits}); ND share id era {nd_share_id:.4f}; kill a {results['chains']['kill_a_fired']}, kill b {results['exits']['kill_b_fired']}, flat storage old A {results['flat']['storage_old_A']}"
    )


# ----------------------------------------------------------------- joins

JOINS = EVIDENCE / "joins.ndjson"
JOINS_RESULTS = EVIDENCE / "joins-results.json"
Q019 = REPO_ROOT / "investigations" / "019-who-holds-the-queue" / "evidence"
RUN_019 = "2026-09-30"
CH_RUN_DATE = "2026-10-22"
CH_RAW = REPO_ROOT / "data" / "raw" / "companies-house" / f"{CH_RUN_DATE}-025"
CH_JOURNAL = EVIDENCE / "ch-journal.ndjson"
CH_MANIFEST = EVIDENCE / "ch-manifest.json"
REPD_DATE_COLUMNS = {
    "refused": ("Planning Permission Refused", "Appeal Refused", "Secretary of State - Refusal"),
    "withdrawn": ("Planning Application Withdrawn", "Appeal Withdrawn"),
    "expired": ("Planning Permission Expired",),
    "granted": ("Planning Permission Granted", "Appeal Granted", "Secretary of State - Granted"),
    "submitted": ("Planning Application Submitted",),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    import csv

    with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        return [
            {(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)
        ]


def uk_date(value: str) -> date | None:
    from grid_mysteries.sources.tec_register import parse_date

    return parse_date(value)


def company_forms(*names: str) -> set[str]:
    from grid_mysteries.sources.companies_house import normalise_company_name

    out = set()
    for n in names:
        for part in str(n or "").split("/"):
            c = normalise_company_name(part.strip())
            if c:
                out.add(c)
    return out


def unique(candidates: list[str]) -> tuple[str | None, str]:
    if len(candidates) == 1:
        return candidates[0], "matched"
    if candidates:
        return None, "ambiguous"
    return None, "unmatched"


def repd_class(row: dict[str, str], m: date) -> str:
    def dates(kind: str) -> list[date]:
        return [d for c in REPD_DATE_COLUMNS[kind] for d in [uk_date(row.get(c, ""))] if d]

    adverse = [d for k in ("refused", "withdrawn", "expired") for d in dates(k) if d < m]
    grants = [d for d in dates("granted") if d < m]
    if adverse:
        last_adverse = max(adverse)
        if not any(g > last_adverse for g in grants):
            return "refused, withdrawn or expired before exit"
    if grants:
        return "consented at exit"
    if row.get("Development Status (short)") == "Abandoned":
        return "abandoned (undated)"
    if any(d < m for d in dates("submitted")):
        return "application pending at exit"
    return "no planning event before exit"


def join_repd(exits: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows = [
        r
        for r in read_csv(SOURCES["desnz-repd-quarterly-extract-2026-q2"][2])
        if r.get("Technology Type") == "Battery"
    ]
    from grid_mysteries.sources.tec_register import parse_decimal

    prepared = []
    for r in rows:
        prepared.append(
            {
                "row": r,
                "ref": r["Ref ID"],
                "tokens": ec.place_tokens(r.get("Site Name", "")),
                "operators": company_forms(r.get("Operator (or Applicant)", "")),
                "capacity": parse_decimal(r.get("Installed Capacity (MWelec)", "")),
            }
        )
    by_operator: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pr in prepared:
        for o in pr["operators"]:
            by_operator[o].append(pr)
    out = {}
    for e in exits:
        jk = e["join_key"]
        tokens = ec.place_tokens(jk["last"]["name"]) | ec.place_tokens(jk["first"]["name"])
        customers = company_forms(jk["last"]["customer"], jk["first"]["customer"])
        mw = parse_decimal(jk["last"]["stage_mw"])
        m = date.fromisoformat(e["exit_copy"]).replace(day=1)
        tier = None
        cands_a = [
            pr["ref"] for o in customers for pr in by_operator.get(o, []) if pr["tokens"] & tokens
        ]
        ref, state = unique(sorted(set(cands_a)))
        if ref:
            tier = "a: operator and place token"
        if ref is None and state != "ambiguous":
            cands_b = [
                pr["ref"]
                for pr in prepared
                if pr["tokens"] & tokens and ec.within_one_mw(pr["capacity"], mw)
            ]
            ref, state = unique(sorted(set(cands_b)))
            if ref:
                tier = "b: place token and capacity"
        if ref is None and state != "ambiguous":
            cands_c = sorted(
                {
                    pr["ref"]
                    for o in customers
                    for pr in by_operator.get(o, [])
                    if len(by_operator[o]) == 1
                }
            )
            ref, state = unique(cands_c)
            if ref:
                tier = "c: operator's only battery row"
        row = next((pr["row"] for pr in prepared if pr["ref"] == ref), None) if ref else None
        out[e["chain"]] = {
            "state": state,
            "tier": tier,
            "repd_ref": ref,
            "class": repd_class(row, m) if row else "no planning record",
            "development_status": row.get("Development Status (short)") if row else None,
        }
    return out


def join_cmr(exits: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    from grid_mysteries.sources.tec_register import parse_decimal

    cmu_rows = [
        r
        for r in read_csv(SOURCES["neso-capacity-market-register-cmu"][2])
        if r.get("Primary Fuel Type") == "Storage - Battery"
    ]
    comp_rows = read_csv(SOURCES["neso-capacity-market-register-components"][2])
    locations: dict[str, set[str]] = defaultdict(set)
    for r in comp_rows:
        locations[r.get("CMU ID", "")] |= ec.place_tokens(r.get("Location and Post Code", ""))
    cmus: dict[str, dict[str, Any]] = {}
    for r in cmu_rows:
        cid = r.get("CMU ID", "")
        c = cmus.setdefault(
            cid, {"companies": set(), "tokens": set(), "capacities": [], "rows": []}
        )
        c["companies"] |= company_forms(r.get("Name of Applicant", ""), r.get("Parent Company", ""))
        c["tokens"] |= ec.place_tokens(r.get("CM Unit Name", "")) | locations.get(cid, set())
        cap = parse_decimal(r.get("Connection or DSR Capacity", ""))
        if cap is not None:
            c["capacities"].append(cap)
        c["rows"].append(r)
    by_company: dict[str, list[str]] = defaultdict(list)
    for cid, c in cmus.items():
        for co in c["companies"]:
            by_company[co].append(cid)
    out = {}
    for e in exits:
        jk = e["join_key"]
        tokens = (
            ec.place_tokens(jk["last"]["name"])
            | ec.place_tokens(jk["first"]["name"])
            | ec.place_tokens(jk["last"]["site"])
        )
        customers = company_forms(jk["last"]["customer"], jk["first"]["customer"])
        mw = parse_decimal(jk["last"]["stage_mw"])
        m = date.fromisoformat(e["exit_copy"]).replace(day=1)
        tier = None
        cands = sorted(
            {
                cid
                for co in customers
                for cid in by_company.get(co, [])
                if cmus[cid]["tokens"] & tokens
            }
        )
        match, state = unique(cands)
        if match:
            tier = "a: company and place token"
        if match is None and state != "ambiguous":
            cands = sorted(
                {
                    c
                    for co in customers
                    for c in by_company.get(co, [])
                    if any(ec.within_one_mw(x, mw) for x in cmus[c]["capacities"])
                }
            )
            match, state = unique(cands)
            if match:
                tier = "b: company and capacity"
        if match is None and state != "ambiguous":
            cands = sorted(
                {
                    c
                    for c, v in cmus.items()
                    if v["tokens"] & tokens
                    and any(ec.within_one_mw(x, mw) for x in v["capacities"])
                }
            )
            match, state = unique(cands)
            if match:
                tier = "c: place token and capacity"
        cls = "no record"
        term_months = None
        if match:
            rows = cmus[match]["rows"]
            awarded = [r for r in rows if r.get("Capacity Agreement Awarded") == "Yes"]
            issued_before = [
                r
                for r in awarded
                if (uk_date(r.get("Date of Issue of Capacity Agreement", "")) or date.max) < m
            ]
            terminated = [
                (uk_date(r.get("Date of Termination of Capacity Agreement", "")), r)
                for r in rows
                if r.get("Capacity Agreement has been Terminated") == "Yes"
            ]
            term_dates = [d for d, _ in terminated if d]
            held_live = [r for r in issued_before if not any(d < m for d in term_dates)]
            if term_dates and min(term_dates) < m:
                cls = "terminated before exit"
                term_months = ec.months_between(min(term_dates), m)
            elif held_live:
                cls = "agreement held at exit"
                if term_dates:
                    cls = "agreement held at exit, terminated after"
                    term_months = -ec.months_between(m, min(term_dates))
            elif term_dates:
                cls = "terminated after exit"
                term_months = -ec.months_between(m, min(term_dates))
            elif awarded:
                cls = "agreement awarded after exit"
            else:
                cls = "never held"
        out[e["chain"]] = {
            "state": state,
            "tier": tier,
            "cmu_id": match,
            "class": cls,
            "termination_minus_exit_months": term_months,
        }
    return out


def load_019_links() -> dict[str, Any]:
    from grid_mysteries.investigations import queue_ownership as qo

    links: dict[str, qo.Link] = {}
    for line in (Q019 / "links.ndjson").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r["run_date"] == RUN_019 and r["rule_version"] == qo.RULE_VERSION_V2:
            links[r["name"]] = qo.Link(
                r["name"],
                r["class"],
                r["company_number"],
                tuple(r["candidates"]),
                r["note"],
                r["rule_version"],
            )
    admitted = {
        a["name"]: a
        for a in json.loads((Q019 / "links-admitted.json").read_text()).get("admissions", [])
    }
    return {n: qo.apply_admissions(lk, admitted) for n, lk in links.items()}


def join_companies_house(exits: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    from grid_mysteries.sources import companies_house as chs

    links = load_019_links()
    numbers: dict[str, str] = {}
    for e in exits:
        name = ec.text(e["join_key"]["last"]["customer"])
        lk = links.get(name)
        if lk is not None and lk.resolved and lk.company_number:
            numbers[e["chain"]] = lk.company_number
    wanted = sorted(set(numbers.values()))
    jobs = []
    for n in wanted:
        jobs.append(
            ("companies-house-profile", chs.profile_url(n), CH_RAW / "company" / n / "profile.json")
        )
        jobs.append(
            ("companies-house-charges", chs.charges_url(n), CH_RAW / "company" / n / "charges.json")
        )
    if jobs:
        fetcher = chs.AuthenticatedFetcher(chs.api_key())
        pin(
            jobs,
            journal_path=CH_JOURNAL,
            manifest_path=CH_MANIFEST,
            fetch=fetcher,
            label="025 Companies House refresh",
            progress=progress,
            sleep_seconds=0,
        )
    out: dict[str, dict[str, Any]] = {}
    for e in exits:
        number = numbers.get(e["chain"])
        m = date.fromisoformat(e["exit_copy"]).replace(day=1)
        if number is None:
            out[e["chain"]] = {"state": "not linked", "company_number": None, "class": "not linked"}
            continue
        profile = json.loads((CH_RAW / "company" / number / "profile.json").read_text())
        charges = json.loads((CH_RAW / "company" / number / "charges.json").read_text())
        status = profile.get("company_status")
        cess = profile.get("date_of_cessation")
        cess_d = date.fromisoformat(cess) if cess else None
        live = []
        for it in charges.get("items") or []:
            created = it.get("created_on")
            satisfied = it.get("satisfied_on")
            if (
                created
                and date.fromisoformat(created) < m
                and not (satisfied and date.fromisoformat(satisfied) < m)
            ):
                live.append(it)
        classes = []
        if cess_d and 0 <= ec.months_between(m, cess_d) < 12:
            classes.append("dissolved within twelve months after exit")
        elif cess_d and cess_d < m and ec.months_between(cess_d, m) < 12:
            classes.append("dissolved within twelve months before exit")
        elif cess_d:
            classes.append("dissolved, more than twelve months from exit")
        if live:
            classes.append("live charge at exit")
        out[e["chain"]] = {
            "state": "linked",
            "company_number": number,
            "company_status": status,
            "date_of_cessation": cess,
            "live_charges_at_exit": len(live),
            "class": "; ".join(classes) if classes else "neither",
        }
    return out


def phase_joins() -> None:
    results = json.loads(RESULTS_JSON.read_text())
    exits = [json.loads(line) for line in EXITS.read_text().splitlines() if line.strip()]
    storage = [e for e in exits if e["storage"] == "storage"]
    id_era = [e for e in storage if date.fromisoformat(e["last_t"]) >= ec.ID_ERA_FROM]
    j1 = join_repd(storage)
    j2 = join_cmr(storage)
    j3 = join_companies_house(exits)

    def share(j: dict[str, dict[str, Any]], subset: list[dict[str, Any]]) -> str | None:
        if not subset:
            return None
        return str(
            (
                Decimal(sum(1 for e in subset if j[e["chain"]]["state"] in ("matched", "linked")))
                / Decimal(len(subset))
            ).quantize(Decimal("0.001"))
        )

    lines = []
    for e in exits:
        lines.append(
            {
                "chain": e["chain"],
                "exit_copy": e["exit_copy"],
                "storage": e["storage"],
                "regime": e["regime"],
                "band_a": e["band_a"],
                "repd": j1.get(e["chain"]),
                "cmr": j2.get(e["chain"]),
                "companies_house": j3.get(e["chain"]),
            }
        )
    JOINS.write_text(
        "".join(json.dumps(line, default=jsonable, sort_keys=True) + "\n" for line in lines)
    )

    def by_class_and_band(j: dict[str, dict[str, Any]]) -> dict[str, Any]:
        table: Any = nested()
        for e in storage:
            if e["regime"] != "old":
                continue
            cls = j[e["chain"]]["class"]
            table[cls][e["band_a"]] = table[cls].get(e["band_a"], 0) + 1
        return {cls: dict(v) for cls, v in table.items()}

    j2_timing = Counter(
        j2[e["chain"]]["termination_minus_exit_months"]
        for e in storage
        if j2[e["chain"]]["termination_minus_exit_months"] is not None
    )
    live_share_base = [e for e in exits if j3[e["chain"]]["state"] == "linked"]
    summary = {
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "declaration_sha256": results["declaration_sha256"],
        "run_on": {
            "exits": len(exits),
            "storage_exits": len(storage),
            "storage_exits_id_era": len(id_era),
        },
        "repd": {
            "matched_share_storage": share(j1, storage),
            "matched_share_storage_id_era": share(j1, id_era),
            "threshold_70_met_id_era": (share(j1, id_era) or "0") >= "0.700",
            "states": dict(Counter(v["state"] for v in j1.values())),
            "tiers": dict(Counter(v["tier"] for v in j1.values() if v["tier"])),
            "classes": dict(Counter(v["class"] for v in j1.values())),
            "classes_id_era": dict(Counter(j1[e["chain"]]["class"] for e in id_era)),
            "class_by_band_old_regime": by_class_and_band(j1),
        },
        "cmr": {
            "matched_share_storage": share(j2, storage),
            "matched_share_storage_id_era": share(j2, id_era),
            "threshold_70_met_id_era": (share(j2, id_era) or "0") >= "0.700",
            "states": dict(Counter(v["state"] for v in j2.values())),
            "tiers": dict(Counter(v["tier"] for v in j2.values() if v["tier"])),
            "classes": dict(Counter(v["class"] for v in j2.values())),
            "classes_id_era": dict(Counter(j2[e["chain"]]["class"] for e in id_era)),
            "class_by_band_old_regime": by_class_and_band(j2),
            "termination_minus_exit_months": dict(sorted(j2_timing.items())),
        },
        "companies_house": {
            "linked_share_all_exits": share(j3, exits),
            "linked_share_storage": share(j3, storage),
            "linked_share_storage_id_era": share(j3, id_era),
            "companies_fetched": len(
                {v["company_number"] for v in j3.values() if v.get("company_number")}
            ),
            "classes": dict(Counter(v["class"] for v in j3.values())),
            "classes_storage": dict(Counter(j3[e["chain"]]["class"] for e in storage)),
            "live_charge_share_of_linked": str(
                (
                    Decimal(
                        sum(
                            1 for e in live_share_base if j3[e["chain"]].get("live_charges_at_exit")
                        )
                    )
                    / Decimal(len(live_share_base))
                ).quantize(Decimal("0.001"))
            )
            if live_share_base
            else None,
            "status_now": dict(
                Counter(v.get("company_status") for v in j3.values() if v["state"] == "linked")
            ),
        },
    }
    write_json(JOINS_RESULTS, summary)
    log_run(
        "joins",
        storage_exits=len(storage),
        repd_share_id_era=summary["repd"]["matched_share_storage_id_era"],
        cmr_share_id_era=summary["cmr"]["matched_share_storage_id_era"],
        ch_linked=summary["companies_house"]["linked_share_all_exits"],
    )
    print(
        json.dumps({k: v for k, v in summary.items() if k in ("run_on",)}),
        "repd",
        summary["repd"]["matched_share_storage_id_era"],
        summary["repd"]["classes_id_era"],
        "cmr",
        summary["cmr"]["matched_share_storage_id_era"],
        summary["cmr"]["classes_id_era"],
        "ch",
        summary["companies_house"]["linked_share_all_exits"],
        summary["companies_house"]["classes"],
    )


# ---------------------------------------------------------------- render

FINDINGS = HERE / "FINDINGS.md"
APPENDIX = HERE / "FINDINGS-APPENDIX.md"
FIGURES = HERE / "figures"
BAND_ORDER = (*ec.BANDS, ec.UNDATED)


def pct(x: str | None) -> str:
    return f"{Decimal(x) * 100:.1f} %" if x is not None else "n/a"


def hazard_md(rows: list[dict[str, Any]], title: str) -> list[str]:
    out = [
        f"**{title}**",
        "",
        "| band (clock A, trigger from the connection date at last sighting) | exits | chain-months at risk | exits per 100 chain-years | 95 % interval |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        iv = (
            f"{r['per_100_chain_years_lower']} to {r['per_100_chain_years_upper']}"
            if r["per_100_chain_years"] is not None
            else "n/a"
        )
        out.append(
            f"| {r['band']} | {r['exits']} | {r['chain_months']:,} | {r['per_100_chain_years'] or 'n/a'} | {iv} |"
        )
    return out + [""]


def phase_render() -> None:
    R = json.loads(RESULTS_JSON.read_text())
    J = json.loads(JOINS_RESULTS.read_text()) if JOINS_RESULTS.exists() else None
    runs = json.loads(RUN_LOG.read_text())["runs"]
    discarded = [r for r in runs if r["phase"] == "compute-discarded"]
    reused = json.loads((EVIDENCE / "reused-keys.json").read_text())
    exits = [json.loads(line) for line in EXITS.read_text().splitlines() if line.strip()]
    chains_lines = [json.loads(line) for line in CHAINS.read_text().splitlines() if line.strip()]
    rk = {p["later"] for p in R["pairs"]["rekeying"]}
    id_era_stitches = Counter(
        kc["tier"]
        for ch in chains_lines
        for kc in ch["key_changes"]
        if kc["t_public"] >= ec.ID_ERA_FROM.isoformat() and kc["t_public"] not in rk
    )
    hz = R["hazards"]["old"]
    sA = {r["band"]: r for r in hz["A"]["storage"]}
    sB = {r["band"]: r for r in hz["B"]["storage"]}
    sC = {r["band"]: r for r in hz["C"]["storage"]}
    allA = {r["band"]: r for r in hz["A"]["all"]}
    E = R["exits"]
    C = R["chains"]
    claims = ec.findings_claims(R)
    if failed := [c for c, holds in claims.items() if not holds]:
        sys.exit(
            "render: FINDINGS states as fixed text what these results no longer support; "
            "rewrite those sentences before rendering: " + "; ".join(failed)
        )
    nd_id = C["by_era"]["id"].get("not_determinable", 0)
    far_ratio = Decimal(sA[ec.BANDS[4]]["per_100_chain_years"]) / Decimal(
        sA[ec.BANDS[0]]["per_100_chain_years"]
    )
    o1 = R["reconciliation"]["o1_snapshots"]
    o2 = R["reconciliation"]["o2_window"]
    storage_exits = [e for e in exits if e["storage"] == "storage"]
    storage_old = [e for e in storage_exits if e["regime"] == "old"]
    by_year_storage = Counter(e["exit_month"][:4] for e in storage_old)
    by_year_all = Counter(e["exit_month"][:4] for e in exits if e["regime"] == "old")
    top3 = ", ".join(
        f"{m} ({v.get('storage', 0)})"
        for m, v in sorted(R["monthly"].items(), key=lambda kv: -kv[1].get("storage", 0))[:3]
    )
    rekey_text = ", ".join(f"{p['earlier']} to {p['later']}" for p in R["pairs"]["rekeying"])
    L: list[str] = []
    L += [
        "# 025, the exit clock: when projects leave the TEC Register, measured against the User Commitment trigger date",
        "",
        f"*Computed {R['computed_at'][:10]} under the frozen declaration `{R['declaration_sha256'][:8]}…` (`DECLARATION.md`, proofs beside it) and its Amendments 1 and 2 of the reading (`AMENDMENT-1.md` `{R['amendments'][0]['sha256'][:8]}…`, frozen 22/10/2026; `AMENDMENT-2.md` `{R['amendments'][1]['sha256'][:8]}…`, frozen 28/10/2026) from every TEC Register copy the repository holds to {R['series']['last_copy']} ({R['series']['kept_copies']} kept copies) and the documents pinned 22/10/2026 (`evidence/sources-manifest.json`). **Held for the sponsor; nothing here is public, and nothing goes to Ofgem or the introducer until sealed.** Every figure is reproducible by `run.py --phase compute --seal {R['declaration_sha256'][:8]}`; the per-chain appendix is `FINDINGS-APPENDIX.md` (held, names projects).*",
        "",
        "## The mystery",
        "",
        "Ofgem's CMP470 consultation (17/09/2026) would charge battery projects to stay in the connection queue, on the reading that a project faces little incentive to reassess its viability until its User Commitment trigger date, the 1 April three financial years before its connection date, after which the Wider Cancellation Charge applies. The question put to the register's history: **when do projects actually leave, relative to that date, and does the rate of leaving change as the date approaches and passes?**",
        "",
        "## The answer, narrowly",
        "",
        f"1. **Exits are few.** Of {C['total']:,} project chains the register has printed since January 2014, {E['total']} left it (status not Built, absent for at least {R['series']['n_days']} days before {R['series']['last_copy']}); {E['storage_old_regime']} of those were storage projects leaving before the connections-reform break of December 2025 ({E['storage_only_old_regime']} storage-only). "
        + (
            "**Kill condition (b) fired**: fewer than 200 storage exits in the old regime, so the series is reported as thin and no storage hazard below is called a pattern."
            if E["kill_b_fired"]
            else "Kill condition (b) did not fire: the old regime holds at least 200 storage exits."
        ),
        f"2. **No bunching before the trigger date, on any clock.** For storage, the exit rate in the twelve months before the trigger ({sA[ec.BANDS[2]]['per_100_chain_years']} exits per 100 chain-years, interval {sA[ec.BANDS[2]]['per_100_chain_years_lower']} to {sA[ec.BANDS[2]]['per_100_chain_years_upper']}) is indistinguishable from the rate more than two years before it ({sA[ec.BANDS[0]]['per_100_chain_years']}, {sA[ec.BANDS[0]]['per_100_chain_years_lower']} to {sA[ec.BANDS[0]]['per_100_chain_years_upper']}). The same holds under clock B (trigger from the connection date first printed: {sB[ec.BANDS[2]]['per_100_chain_years']} against {sB[ec.BANDS[0]]['per_100_chain_years']}) and clock C (the date as printed in each copy: {sC[ec.BANDS[2]]['per_100_chain_years']} against {sC[ec.BANDS[0]]['per_100_chain_years']}).",
        f'3. **The rate rises after the trigger, under clock A only.** More than twelve months after the trigger implied by the last-printed connection date, storage left at {sA[ec.BANDS[4]]["per_100_chain_years"]} per 100 chain-years ({sA[ec.BANDS[4]]["per_100_chain_years_lower"]} to {sA[ec.BANDS[4]]["per_100_chain_years_upper"]}), {far_ratio:.0f} times the far-before rate; the bands are not flat within their uncertainty (K6: {R["flat"]["storage_old_A"]}). Under clocks B and C the bands **are** flat ({R["flat"]["storage_old_B"]}, {R["flat"]["storage_old_C"]}). Interpretation, offered not asserted: clock A reads the trigger from the date a project last printed, so a project that leaves with a stale, passed or imminent connection date sits far "after" its trigger by construction; the rise says projects leave late in their own printed programme (017\'s overdue residue), not that they leave because the bill arrived.',
        f"4. **All technologies together show the same shape, with more exits.** {E['old_regime']} old-regime exits: {allA[ec.BANDS[0]]['per_100_chain_years']} per 100 chain-years far before the trigger, {allA[ec.BANDS[2]]['per_100_chain_years']} in the year before, {allA[ec.BANDS[3]]['per_100_chain_years']} in the year after, {allA[ec.BANDS[4]]['per_100_chain_years']} beyond. Here the rate does step up from the far-before band to the two years before the trigger ({allA[ec.BANDS[1]]['per_100_chain_years']}), which storage alone does not show; the controls are mostly wind and gas chains from 2014 to 2021.",
        f"5. **Against Ofgem's 72.** Ofgem counted 72 storage projects that \"exited the connection queue or changed their technology classification\" between 2023 and 2025 (6.7 % a year). This series counts {o2['storage_exits']} storage exits with exit copies from January 2023 to November 2025 ({o2['by_exit_year'].get('2023', 0)}, {o2['by_exit_year'].get('2024', 0)}, {o2['by_exit_year'].get('2025', 0)} by year), and on Ofgem's own annual-snapshot footing {sum(s['by_status']['all'].get('reclassified_away', 0) for s in o1)} storage chains reclassified away from storage between snapshots. The counts meet within a factor of two (F1 silent); the **rates** do not: {pct(o1[0]['by_status']['all']['left_share'])}, {pct(o1[1]['by_status']['all']['left_share'])} and {pct(o1[2]['by_status']['all']['left_share'])} of storage chains present at each January snapshot had left by the next, against 6.7 %; Scoping {pct(o1[1]['by_status'].get('Scoping', {}).get('left_share'))} and {pct(o1[2]['by_status'].get('Scoping', {}).get('left_share'))} against Ofgem's 7.4 % for Scoping or Awaiting Consents; Consents Approved {pct(o1[2]['by_status'].get('Consents Approved', {}).get('left_share'))} against 3 %; Under Construction {pct(o1[2]['by_status'].get('Under Construction/Commissioning', {}).get('left_share'))} against 0 %. The direction agrees (earlier stages leave more; nothing leaves from construction); the level does not, and the candidates are in the reconciliation section.",
        "",
        "What this does **not** say: why any project left; what any project had posted or accrued; that a trigger date caused anything. The register records absence.",
        "",
        "## Provisional to sealed",
        "",
    ]
    if discarded:
        d = discarded[-1]
        L.append(
            f"The first compute of 22/10/2026 was discarded before any line was committed: it produced 13 chains holding two keys in one copy, a runner defect against rule I2: a key returned to the register while its chain was already continuing under a stitched key, and the runner let the chain carry both (discarded `chains.ndjson` SHA-256 `{d['discarded_chains_sha256'][:16]}…`, the note in `evidence/run-log.json`). The rerun under the same sealed declaration moved the headline by: chains 2,631 to {C['total']:,}; exits 493 to {E['total']}; storage exits in the old regime 95 to {E['storage_old_regime']}. The 13 are reported below as a stitching finding."
        )
    A1 = R.get("amendment_1") or {}
    A2 = R.get("amendment_2") or {}
    moved = A2.get("moved") or []
    by_leaf = {m["leaf"]: m for m in moved}
    fig1 = by_leaf.get("exits/storage_old_regime")
    bands8 = [
        m
        for m in moved
        if any(m["leaf"] == f"hazards/old/A/all[{i}]/per_100_chain_years" for i in range(5))
    ]
    L += ["", "## Amendment 1 of the reading", ""]
    L.append(
        f"Amendment 1 (`AMENDMENT-1.md` `{R['amendments'][0]['sha256'][:8]}…`) admits a row to chain-building only if it prints a Project Name and at least one other field of the register (I10). On this series it refused {A1.get('rows_refused', 0)} rows, in {len(A1.get('refused_rows') or [])} copy(ies): "
        + ", ".join(f"{r['t_public']} ({r['refused']})" for r in A1.get("refused_rows") or [])
        + f". {len(A1.get('sparse_rows_admitted') or [])} row(s) printing a name and exactly one other field were admitted as the rule reads: "
        + "; ".join(
            f"{r['t_public']}, {' and '.join(r['fields'])}, chain class {r['chain_class']}"
            for r in A1.get("sparse_rows_admitted") or []
        )
        + ". What moved under Amendment 1 alone is listed in `results-amendment-1.json` (`amendment_1.moved`)."
    )
    L += ["", "## Amendment 2 of the reading", ""]
    L.append(
        (
            f"**Figure 1's storage exit count moved: {fig1['before']} to {fig1['after']}.** "
            if fig1
            else "**Figure 1's storage exit count did not move.** "
        )
        + (
            f"**{len(bands8)} of figure 8's rates moved** (all technologies, clock A, old regime, five trigger bands; listed below). "
            if bands8
            else "**None of figure 8's five trigger-band rates moved.** "
        )
        + f"Amendment 2 (`AMENDMENT-2.md` `{R['amendments'][1]['sha256'][:8]}…`) reads the rows that print no Project Name as continuations of the named row above (I11, chosen by rebuilding NESO's complete exports of 38 month-ends) and admits the {len(A2.get('copies_added') or [])} copies journalled on 28/10/2026 (I12). It read {A2.get('continuation_rows_read', 0):,} continuation rows in the kept copies. The {A2.get('chain_lines_held_from_amendment_1', 0):,} chain lines of the earlier computes stay in `evidence/chains.ndjson`; this compute's are in `evidence/amendment-2/chains.ndjson` (C5, append-only from its first write). "
        + f"Re-keyings: {len(R['pairs']['rekeying'])}, "
        + "; ".join(
            f"{p['earlier']} to {p['later']} ({p['stitched']} stitched, {p['not_determinable']} not determinable)"
            for p in R["pairs"]["rekeying"]
        )
        + f". Every leaf of `results.json` that differs from `results-amendment-1.json` (`6fc3d59e…`, the compute of 305dbe8) is listed below with its old and new value: {len(moved)} leaves, storage leaves first."
    )
    if moved:
        L += ["", "| leaf | before | after |", "|---|---|---|"]
        for m_ in sorted(
            moved, key=lambda m: (0 if "storage" in m["leaf"].lower() else 1, m["leaf"])
        ):
            L.append(f"| `{m_['leaf']}` | {m_['before']} | {m_['after']} |")
    L += [
        "",
        "## The evidence",
        "",
        f"- **Copies**: {R['series']['usable_copies']} usable, {R['series']['kept_copies']} kept (014's partial-export rule excluded {len(R['series']['suspect_copies'])}: {', '.join(s['t_public'] for s in R['series']['suspect_copies'])}), {R['series']['first_copy']} to {R['series']['last_copy']}; every copy verified against its journalled or manifested digest (C1); the series end fixed at {R['series']['last_copy']} and copies published after it unread.",
        f"- **Chains**: {C['total']:,}. Classes (C3): {C['classes'].get('present at series end', 0):,} present at the series end, {C['classes'].get('exit', 0)} left, {C['classes'].get('completed', 0)} completed (last printed as Built), {C['classes'].get('open', 0)} open (last seen after {R['series']['exit_cutoff']}), {C['classes'].get('not determinable', 0)} not determinable ("
        + (
            "all before the Project ID era"
            if nd_id == 0
            else f"{C['by_era']['pre-id'].get('not_determinable', 0)} before the Project ID era, {nd_id} in it"
        )
        + "). "
        + (
            f"**Kill (a) fired: the ID-era not-determinable share is {pct(C['not_determinable_share_id_era'])}, over the declared 10 %, and by the declaration the investigation stops and says so.**"
            if C["kill_a_fired"]
            else f"**Kill (a) did not fire**: the ID-era not-determinable share is {pct(C['not_determinable_share_id_era'])}."
        ),
        f"- **Stitching**: {C['key_changes']:,} key changes carried a chain across a change of key, by tier: {', '.join(f'{k} {v:,}' for k, v in sorted(C['key_change_tiers'].items(), key=lambda kv: -kv[1]))}. {R['pairs']['returned_own_key_total']} keys returned to their chain after an interruption (I9); {C['interrupted_chains']} chains were interrupted at least once; {C['stage_reductions']:,} stage reductions (rows lost while the chain stayed); {C['reclassified']['chains']} chains changed plant family at some point (I7), none of them counted as an exit for that reason.",
        f"- **Exposure**: {R['exposure']['total_chain_months']:,} chain-months at risk over the series.",
        "",
        "### Monthly exit series (old regime, exit copies January 2014 to November 2025)",
        "",
        "| year | all exits | storage exits |",
        "|---|---|---|",
    ]
    for y in sorted(set(by_year_all) | set(by_year_storage)):
        L.append(f"| {y} | {by_year_all.get(y, 0)} | {by_year_storage.get(y, 0)} |")
    L += [
        "",
        f"The monthly series itself (counts and MW, all and storage) is the `monthly` block of `evidence/results.json`, drawn in `figures/monthly-exits.png` (held). 2014's {by_year_all.get('2014', 0)} exits fall in a year of sparse, differently formatted copies (gaps up to 95 days, single-copy column eras) and should be read as the register settling, not as a wave. Storage exits in the old regime cluster in {top3}.",
        "",
        "### Hazard by band (storage, old regime)",
        "",
    ]
    L += hazard_md(
        hz["A"]["storage"], "Clock A: trigger from the connection date printed at last sighting"
    )
    L += hazard_md(
        hz["B"]["storage"], "Clock B: trigger from the connection date printed at first sighting"
    )
    L += hazard_md(
        hz["C"]["storage"],
        "Clock C: exposure placed by the date printed in each copy; exits by clock A",
    )
    L += hazard_md(
        hz["A"]["storage-only"],
        "Clock A, storage-only (plant type prints storage and nothing else)",
    )
    L += hazard_md(hz["A"]["all"], "Clock A, every chain")
    L += hazard_md(
        hz["A"]["other"], "Clock A, chains that print no storage technology (the control)"
    )
    L += [
        f"Flatness (K6, the five bands' intervals share a value): storage A {R['flat']['storage_old_A']}, B {R['flat']['storage_old_B']}, C {R['flat']['storage_old_C']}; storage-only A {R['flat']['storage_only_old_A']}; all A {R['flat']['all_old_A']}; other A {R['flat']['other_old_A']}.",
        "",
        "### The clock, exit by exit",
        "",
        f"Months from exit copy to trigger (clock A; negative means the exit came before the trigger), storage, old regime: {sum(v for k, v in R['months_to_trigger_histogram_storage_old'].items() if int(k) < -24)} exits more than 24 months before, {sum(v for k, v in R['months_to_trigger_histogram_storage_old'].items() if -24 <= int(k) < -12)} at 12 to 24 before, {sum(v for k, v in R['months_to_trigger_histogram_storage_old'].items() if -12 <= int(k) < 0)} in the year before, {sum(v for k, v in R['months_to_trigger_histogram_storage_old'].items() if 0 <= int(k) < 12)} in the year after, {sum(v for k, v in R['months_to_trigger_histogram_storage_old'].items() if int(k) >= 12)} more than a year after; {sum(1 for e in storage_old if e['months_to_trigger_a'] is None)} with no connection date. Drawn with the bands shaded in `figures/exit-clock.png` (held).",
        "",
        "### Strata (storage, old regime, clock A)",
        "",
        "| stratum at last sighting | exits | chain-months | exits per 100 chain-years |",
        "|---|---|---|---|",
    ]
    for dim, label in (
        ("status", "Project Status"),
        ("agreement", "Agreement Type"),
        ("host_to", "Host TO"),
        ("cohort", "First-observation cohort"),
    ):
        for value, t in R["storage_strata_old_A"][dim].items():
            rate = (
                (Decimal(t["exits"]) * 1200 / Decimal(t["chain_months"])).quantize(Decimal("0.01"))
                if t["chain_months"]
                else None
            )
            L.append(
                f"| {label}: {value} | {t['exits']} | {t['chain_months']:,} | {rate if rate is not None else 'n/a'} |"
            )
    L += [
        "",
        f"The stage split Ofgem can set beside its 7.4 / 3 / 0: storage chains at Scoping or Awaiting Consents left at {((Decimal(R['storage_strata_old_A']['status'].get('Scoping', {}).get('exits', 0) + R['storage_strata_old_A']['status'].get('Awaiting Consents', {}).get('exits', 0)) * 1200) / Decimal(R['storage_strata_old_A']['status'].get('Scoping', {}).get('chain_months', 0) + R['storage_strata_old_A']['status'].get('Awaiting Consents', {}).get('chain_months', 1))).quantize(Decimal('0.01'))} per 100 chain-years over the whole old regime, Consents Approved at {((Decimal(R['storage_strata_old_A']['status'].get('Consents Approved', {}).get('exits', 0)) * 1200) / Decimal(R['storage_strata_old_A']['status'].get('Consents Approved', {}).get('chain_months', 1))).quantize(Decimal('0.01'))}, Under Construction at {((Decimal(R['storage_strata_old_A']['status'].get('Under Construction/Commissioning', {}).get('exits', 0)) * 1200) / Decimal(R['storage_strata_old_A']['status'].get('Under Construction/Commissioning', {}).get('chain_months', 1))).quantize(Decimal('0.01'))} (a rate per 100 chain-years is comparable to a percentage per year).",
        "",
        "### Regimes",
        "",
        f"- Reformed regime (exit copies from 2025-12-01): {E['new_regime']} exits. Too few for a hazard table; the candidate in CANDIDATES.md waits for the series to lengthen.",
        "",
        "| reformed regime, exits by | value | exits |",
        "|---|---|---|",
        *[
            f"| Project Status at last sighting | {k} | {v} |"
            for k, v in sorted(E["new_regime_by_status"].items())
        ],
        *[
            f"| Gate at last sighting | {k} | {v} |"
            for k, v in sorted(E["new_regime_by_gate"].items())
        ],
        "",
        f"- The register's row count through the Gate 2 reset: {R['rows_through_break'][0]['rows']:,} on {R['rows_through_break'][0]['t_public']}, {next(r['rows'] for r in R['rows_through_break'] if r['t_public'] >= '2025-11-25'):,} on {next(r['t_public'] for r in R['rows_through_break'] if r['t_public'] >= '2025-11-25')}, {R['rows_through_break'][-1]['rows']:,} on {R['rows_through_break'][-1]['t_public']}. **The queue reset is not visible as a mass departure from the TEC Register.**",
        "",
        "## Explanations tested",
        "",
        "### Reconciliation to Ofgem (O1, O2)",
        "",
        "Annual snapshots as Ofgem had them (the first kept copy on or after 1 January, and the last old-regime copy), storage chains present, the share that had left by the next snapshot, and the share reclassified away from storage:",
        "",
        "| snapshot | next | status | present | left | left share | reclassified away |",
        "|---|---|---|---|---|---|---|",
    ]
    for s_ in o1:
        for st, c in s_["by_status"].items():
            L.append(
                f"| {s_['snapshot']} | {s_['next']} | {st} | {c.get('present', 0)} | {c.get('left', 0)} | {pct(c.get('left_share'))} | {c.get('reclassified_away', 0)} |"
            )
    L += [
        "",
        f"Window count (O2): {o2['storage_exits']} storage exits with exit copies 2023-01 to 2025-11 ({o2['storage_only_exits']} storage-only). Ofgem: 72 exited or reclassified, 6.7 % a year. By status at last sighting:",
        "",
        "| O2 window, status at last sighting | storage exits |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in sorted(o2["by_status"].items(), key=lambda kv: -kv[1])],
        "",
        f"Candidates for the gap in rates, none asserted: (i) **denominator**: Ofgem's queue is NESO's full connections queue, which includes distribution-connected projects below the TEC Register's threshold and projects not yet on the register; a smaller, earlier-stage population would both raise the rate and hold more of the exits; (ii) **classification**: Ofgem's figure lumps exits with reclassification, and the register's reclassifications under one key are counted here as reclassifications ({sum(s['by_status']['all'].get('reclassified_away', 0) for s in o1)} away from storage across the snapshots) and never as exits; (iii) **snapshot dates**: Ofgem's are not published; (iv) **re-keying**: a snapshot pair that spans a re-keying copy sees every project leave unless it is stitched, and the August 2022 re-issue lies just before Ofgem's first window.",
        "",
        "### The stitching caveat (the question Ofgem will ask)",
        "",
        f"Identity is the whole method. {C['key_change_tiers'].get('all five', 0):,} of the {C['key_changes']:,} key changes were at the {len(R['pairs']['rekeying'])} re-keying copies and matched on every feature; the next two tiers ({C['key_change_tiers'].get('name, customer, stage', 0)} on name, customer and stage; {C['key_change_tiers'].get('name, site, stage', 0)} on name, site and stage) are mostly re-spelt sites and customers at the June 2020 format change and at the re-issues. In the Project ID era, outside the re-keying copies, only **{sum(id_era_stitches.values())}** stitches were made ({', '.join(f'{k} {v}' for k, v in id_era_stitches.most_common())}); that is the most by which stitching can have hidden an ID-era exit. "
        + (
            f"The stitch's one caught failure: **{len(reused)} keys returned to the register while their chain was already printed under another key** (at {', '.join(f'{k} ({v})' for k, v in sorted(R['reused_keys']['by_copy'].items()))}), all in the ID era and none at a re-keying boundary. Each was a project sharing its **name** with a different project (different customer, mostly a different site and MW): the name-based tiers had merged two projects, the returning id separated them, and the runner now keeps the id's chain and treats the row as new. These are the copies 017's certificates show as \"presence ambiguous (2 rows)\". "
            if reused
            else "No key returned to the register while its chain was printed under another key. "
        )
        + f"Nothing says how many unreturned merges remain; the bound above ({sum(id_era_stitches.values())} ID-era stitches outside re-keyings) is the honest ceiling.",
        "",
        "### The joins (addendum J1 to J3), run on the storage exits",
        "",
    ]
    if J:
        L += [
            f"- **J1 REPD** (battery rows, July 2026 extract): matched {J['repd']['states'].get('matched', 0)} of {J['run_on']['storage_exits']} storage exits ({pct(J['repd']['matched_share_storage'])}; ID era {pct(J['repd']['matched_share_storage_id_era'])}), {J['repd']['states'].get('ambiguous', 0)} ambiguous (tiers tabled below). **Below the 70 % threshold: the matched subset is reported and the join stops.** Classes among the matched: {', '.join(f'{k} {v}' for k, v in J['repd']['classes'].items() if k != 'no planning record')}. One sentence per class: no matched storage exit was consented at exit; {J['repd']['classes'].get('refused, withdrawn or expired before exit', 0)} left after a refusal, withdrawal or expiry; {J['repd']['classes'].get('abandoned (undated)', 0)} are abandoned in the planning record; {J['repd']['classes'].get('application pending at exit', 0)} left with an application pending; {J['repd']['classes'].get('no planning event before exit', 0)} left with a planning record that holds no event before the exit. Coordinates were not used (the register prints none).",
            f"- **J2 Capacity Market Register** (storage CMUs, 21/10/2026): matched {J['cmr']['states'].get('matched', 0)} ({pct(J['cmr']['matched_share_storage'])}; ID era {pct(J['cmr']['matched_share_storage_id_era'])}), {J['cmr']['states'].get('ambiguous', 0)} ambiguous (one customer with several CMUs at one site; tiers tabled below). **Below 70 %: matched subset only.** Classes: {', '.join(f'{k} {v}' for k, v in J['cmr']['classes'].items() if k != 'no record')}. No matched exit had a terminated capacity agreement, so the termination-against-exit timing table is empty{'' if not J['cmr']['termination_minus_exit_months'] else ': ' + ', '.join(f'{k} {v}' for k, v in J['cmr']['termination_minus_exit_months'].items())}.",
            f"- **J3 Companies House** (019's links, profiles and charges refreshed {CH_RUN_DATE}, {J['companies_house']['companies_fetched']} companies): {pct(J['companies_house']['linked_share_all_exits'])} of all exits linked ({pct(J['companies_house']['linked_share_storage'])} of storage exits, {pct(J['companies_house']['linked_share_storage_id_era'])} in the ID era; 019 resolved names on current ids, so pre-2021 customers are mostly unlinked). Of the linked, {pct(J['companies_house']['live_charge_share_of_linked'])} had a live charge at exit (company status now and the classes tabled below). One sentence: the companies behind linked exits are almost all still active, and more than a third carried a live charge when their project left the register, which is the case Ofgem should worry about and the one this register cannot explain.",
            "",
            "| join | breakdown | value | count |",
            "|---|---|---|---|",
            *[
                f"| J1 REPD | match tier | {k} | {v} |"
                for k, v in sorted(J["repd"]["tiers"].items())
            ],
            *[
                f"| J2 Capacity Market | match tier | {k} | {v} |"
                for k, v in sorted(J["cmr"]["tiers"].items())
            ],
            *[
                f"| J3 Companies House | company status now | {k} | {v} |"
                for k, v in sorted(J["companies_house"]["status_now"].items())
            ],
            *[
                f"| J3 Companies House | class at exit | {k} | {v} |"
                for k, v in sorted(J["companies_house"]["classes"].items(), key=lambda kv: -kv[1])
            ],
            "",
            "Why the joins are thin: the register prints a substation and a developer's project name; REPD prints a planning site and the applicant; the Capacity Market prints a unit name and the applicant. A place token shared by both is rare when the register's name is a substation and REPD's is a road. The declared next step, if the sponsor wants the joins to carry weight, is an amendment that sends the unmatched residue to a model as **proposer** (016's admission rule), with the proposals pinned and admitted by a declared rule; the declared tiers stay the record.",
        ]
    L += [
        "",
        "## Conclusion",
        "",
        f"From the register's own history, storage projects did not leave in a bunch before their User Commitment trigger date in 2014 to 2025; under every clock the year before the trigger looks like the years before that. What rises is the exit rate **after** the trigger implied by a project's last-printed connection date, and that rise disappears when the clock is set by the date first printed or by the date as it stood each month: it is the signature of projects leaving late in their own programme. With {E['storage_old_regime']} storage exits the intervals are wide and the series is thin by its own kill rule; this is a described measurement, not a verdict on CMP470. The premise that \"projects leave when the bill arrives\" is neither confirmed nor refuted by bunching; it is simply not what the register shows happening before the date.",
        "",
        "## Expert corner",
        "",
        f"- **Re-keying dates**: {rekey_text} (more than half of keys absent); Project ID printed from 2021-11-26 (`a03…` ids), re-issued 2022-08-24 (`a0l…`); Project Number from 2024-06-18. 2024-01-05 is **not** a re-keying (0 of 1,452 ids absent), contrary to the prompt's expectation; the id change the 017 Eggborough certificate shows there is one project's.",
        "- **The trigger rule**: CUSC Section 15 v1.14 Part Two 2.2(a), read on `MW Effective From` as the Charging Date; branch (b) (the Construction Agreement date when closer) and any contractual variation are not applied. Ofgem's own footnote uses the same rule of thumb. A project whose connection date was re-set had a different trigger before the re-set; clocks B and C carry that.",
        "- **CMP223 embedded percentages** (2024-25 statement, section 5): secured amount after the trigger 42 % of the cancellation charge before key consents and 10 % after for directly connected; 45 % and 26 % for embedded; 100 % before the trigger. Zonal tariffs 2024-25 by zone code A1 to T6 (GBP 0 to 15,677.41 per MW). No 2025-26 or 2026-27 statement exists; the 15/01/2026 letter froze securities to 30/09/2026.",
        f"- **Regime break**: copies from 2025-12-01; row count {R['rows_through_break'][0]['rows']:,} to {R['rows_through_break'][-1]['rows']:,} across it.",
        f"- **Gap between last sighting and exit copy**: median {E['gap_days']['median']} days, maximum {E['gap_days']['max']}; the register's resolution, not the project's timing.",
        "- **Not computed**: the zone mapping (no public site-to-zone list; phase 2 stopped); the DNO register join (J4, candidate); the EIR validation (`EIR-REQUEST-NESO-TERMINATIONS.md`, drafted for the sponsor, not sent).",
        "- **Watch**: `w-025-monthly-exit-series`, due 30/11/2026 and monthly, extends the series from the daily capture under this declaration.",
        "",
        "## Reproducibility",
        "",
        f"`DECLARATION.md` `{R['declaration_sha256']}`; `AMENDMENT-1.md` `{R['amendments'][0]['sha256']}` (blank-pattern addendum `archives/025-exit-clock-inputs/blank-patterns.json`); `evidence/results-declaration-alone.json` (the compute under the declaration alone); schema report `{R['schema_report_sha256'][:16]}…`; sources manifest `{R['sources_manifest_sha256'][:16]}…`; `evidence/results.json`, `evidence/joins-results.json`, `evidence/format-check.json`, `evidence/run-log.json` (committed); `evidence/chains.ndjson` (append-only, C5), `evidence/exits.ndjson`, `evidence/joins.ndjson`, `evidence/reused-keys.json`, `FINDINGS-APPENDIX.md` (held). Rules: `src/grid_mysteries/investigations/exit_clock.py`, tests `tests/test_exit_clock.py`, map `evidence/rule-sources.json`.",
    ]
    FINDINGS.write_text("\n".join(L) + "\n")

    # ---- appendix (held): every exit chain with its runs and join key
    chains_by_id = {c["chain"]: c for c in chains_lines}
    A = [
        "# 025, appendix: every chain that left the register (held; names projects and companies)",
        "",
        f"*{len(exits)} exits under `DECLARATION.md` `{R['declaration_sha256'][:8]}…` with Amendment 1 (`{R['amendments'][0]['sha256'][:8]}…`). For each: the join key Ofgem can apply to its own securities table (project name, customer, connection site, Project ID and Number, MW, at first and last sighting), then every run of unchanged state (first and last copy, copies in the run, the copies' digests) so that any row can be checked against NESO's own archive. Copies' dates and digests are in `archives/025-exit-clock-inputs/schema-report.json`.*",
        "",
    ]
    for e in sorted(exits, key=lambda e: (e["exit_copy"], e["chain"])):
        ch = chains_by_id[e["chain"]]
        jk = e["join_key"]
        A += [
            f"## {jk['last']['name']}, exit copy {e['exit_copy']} ({e['regime']} regime)",
            "",
            f"- Join key, last sighting {e['last_t']}: name `{jk['last']['name']}`, customer `{jk['last']['customer']}`, site `{jk['last']['site']}`, key `{jk['last']['key']}`, Project Number `{jk['last']['project_number'] or '-'}`, MW {jk['last']['stage_mw']}. First sighting {e['first_t']}: name `{jk['first']['name']}`, customer `{jk['first']['customer']}`, site `{jk['first']['site']}`, key `{jk['first']['key']}`, MW {jk['first']['stage_mw']}.",
            f"- Status at last sighting {e['status_printed']}; plant type `{e['plant_type_printed']}`; agreement {e['agreement']}; host TO {e['host_to']}; gate `{e['gate'] or '-'}`. Connection date at last sighting {e['connection_at_last'] or '-'} (trigger A {e['trigger_a'] or '-'}, band {e['band_a']}); at first sighting {e['connection_at_first'] or '-'} (trigger B {e['trigger_b'] or '-'}, band {e['band_b']}). Sightings {e['sightings']}, key changes {e['key_changes']}, interruptions {e['interruptions']}, reclassified {e['reclassified']}.",
            "",
            "| first copy | last copy | copies | key | status | plant type | customer | site | MW | connection | first digest | last digest |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for r in ch["runs"]:
            st = r["state"]
            A.append(
                f"| {r['first_t']} | {r['last_t']} | {r['copies']} | `{st['key']}` | {st['status']} | {st['plant_type']} | {st['customer']} | {st['site']} | {st['stage_mw'] or '-'} | {st['connection'] or '-'} | `{r['first_sha'][:12]}` | `{r['last_sha'][:12]}` |"
            )
        A.append("")
    APPENDIX.write_text("\n".join(A) + "\n")
    log_run("render", findings_sha256=sha(FINDINGS), appendix_sha256=sha(APPENDIX))
    print(f"rendered {FINDINGS.relative_to(REPO_ROOT)} and the appendix ({len(exits)} exits)")


def phase_figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    R = json.loads(RESULTS_JSON.read_text())
    FIGURES.mkdir(exist_ok=True)
    monthly = R["monthly"]
    months = sorted(m for m in monthly if m < "2025-12")
    all_counts = [monthly[m].get("all", 0) for m in months]
    storage_counts = [monthly[m].get("storage", 0) for m in months]
    xs = [date(int(m[:4]), int(m[5:]), 1) for m in months]
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(xs, all_counts, width=25, color="#bbbbbb", label="all exits")
    ax.bar(xs, storage_counts, width=25, color="#1f4e79", label="storage exits")
    ax.set_title(
        "Projects leaving the TEC Register by month of exit copy, January 2014 to November 2025 (old regime)"
    )
    ax.set_ylabel("exits")
    ax.legend(frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / "monthly-exits.png", dpi=150)
    plt.close(fig)

    hist = {int(k): v for k, v in R["months_to_trigger_histogram_storage_old"].items()}
    hist_all = {int(k): v for k, v in R["months_to_trigger_histogram_all_old"].items()}
    lo, hi = -60, 132
    ks = list(range(lo, hi + 1))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    shades = [
        (-(10**6), -24, "#eef3f8"),
        (-24, -12, "#dbe6f1"),
        (-12, 0, "#c3d5e8"),
        (0, 12, "#f6dcd4"),
        (12, 10**6, "#f0bfb0"),
    ]
    for ax, h, title in ((ax1, hist_all, "all chains"), (ax2, hist, "storage chains")):
        for a, b, colour in shades:
            ax.axvspan(max(a, lo - 0.5), min(b, hi + 0.5), color=colour, lw=0)
        ax.bar(ks, [h.get(k, 0) for k in ks], width=1, color="#1f4e79")
        ax.axvline(0, color="black", lw=1)
        ax.set_ylabel(f"exits ({title})")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    ax1.set_title(
        "Exits by months from exit copy to the User Commitment trigger date (clock A), old regime; bands shaded: >24 and 12 to 24 and 0 to 12 months before, 0 to 12 and >12 after; exits beyond the axis are counted in the outer bands"
    )
    ax2.set_xlabel(
        "months from exit copy to trigger date (negative: the exit came before the trigger)"
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "exit-clock.png", dpi=150)
    plt.close(fig)

    hz = R["hazards"]["old"]["A"]
    fig, ax = plt.subplots(figsize=(11, 4))
    bands = list(ec.BANDS)
    x = range(len(bands))
    for offset, key, colour, label in (
        (-0.2, "all", "#999999", "all chains"),
        (0.2, "storage", "#1f4e79", "storage chains"),
    ):
        rows = {r["band"]: r for r in hz[key]}
        vals = [float(rows[b]["per_100_chain_years"] or 0) for b in bands]
        lows = [
            float(rows[b]["per_100_chain_years"] or 0)
            - float(rows[b]["per_100_chain_years_lower"] or 0)
            for b in bands
        ]
        highs = [
            float(rows[b]["per_100_chain_years_upper"] or 0)
            - float(rows[b]["per_100_chain_years"] or 0)
            for b in bands
        ]
        ax.bar(
            [i + offset for i in x],
            vals,
            width=0.4,
            color=colour,
            label=label,
            yerr=[lows, highs],
            capsize=3,
        )
    ax.set_xticks(list(x))
    ax.set_xticklabels(bands, rotation=0, fontsize=8)
    ax.set_ylabel("exits per 100 chain-years")
    ax.set_title(
        "Exit hazard by band around the trigger date (clock A, old regime), with 95 % Byar intervals"
    )
    ax.legend(frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / "hazard-by-band.png", dpi=150)
    plt.close(fig)
    (FIGURES / "captions.md").write_text(
        "# 025 figures (drawn from evidence/results.json by run.py --phase figures; PNGs held out of git)\n\n"
        "- `monthly-exits.png`: projects leaving the TEC Register by month of exit copy, January 2014 to November 2025, all chains (grey) and storage chains (blue).\n"
        "- `exit-clock.png`: exits by months from exit copy to the trigger date implied by the last-printed connection date (clock A), all chains and storage chains, with the five bands shaded.\n"
        "- `hazard-by-band.png`: exits per 100 chain-years in each band with Byar 95 % intervals, all chains and storage chains, old regime, clock A.\n"
    )
    log_run("figures", files=["monthly-exits.png", "exit-clock.png", "hazard-by-band.png"])
    print(f"figures -> {FIGURES.relative_to(REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        required=True,
        choices=[
            "acquire",
            "schema",
            "schema-a2",
            "format",
            "compute",
            "joins",
            "render",
            "figures",
        ],
    )
    parser.add_argument("--seal")
    args = parser.parse_args()
    if args.phase == "acquire":
        phase_acquire()
    elif args.phase == "schema":
        phase_schema()
    elif args.phase == "schema-a2":
        phase_schema(amended=True)
    elif args.phase == "format":
        phase_format()
    elif args.phase == "compute":
        phase_compute(args.seal)
    elif args.phase == "joins":
        phase_joins()
    elif args.phase == "render":
        phase_render()
    elif args.phase == "figures":
        phase_figures()
    else:
        sys.exit(f"phase {args.phase} not written yet")


if __name__ == "__main__":
    main()
