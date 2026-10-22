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
from collections import Counter
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import exit_clock as ec
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
GAP_DAYS = 30
#: A pair with more than this share of keys absent (but not a re-keying) is
#: listed in the schema report with its stitch outcome, counts only.
HIGH_CHURN = Decimal("0.05")


def load_copies() -> list[tuple[tec_sources.Copy, cs.VintageInput]]:
    """Every copy the repository holds (journal and daily capture), verified
    against its digest, with 014's required columns; unreadable copies are
    listed, not read."""
    usable, skipped = [], []
    for copy in tec_sources.copies(REPO_ROOT):
        try:
            tec_sources.verify(copy)
            rows = tec_sources.read(copy)
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


def kept_map(usable: list[cs.VintageInput]) -> dict[date, analysis.Kept]:
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


def phase_schema() -> None:
    usable, skipped = load_copies()
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
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    write_json(SCHEMA_REPORT, report)
    SCHEMA_MD.write_text(render_schema(report))
    log_run(
        "schema",
        copies=len(usable),
        kept=report["copies_kept"],
        rekeyings=len(rekeyings),
        report_sha256=sha(SCHEMA_REPORT),
    )
    print(
        f"{len(usable)} copies, {report['copies_kept']} kept, {len(rekeyings)} re-keying pairs, largest gap {report['largest_gap_days']} days -> {ARCHIVE.relative_to(REPO_ROOT)}"
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase", required=True, choices=["acquire", "schema", "format", "compute", "render"]
    )
    parser.add_argument("--seal")
    args = parser.parse_args()
    if args.phase == "acquire":
        phase_acquire()
    elif args.phase == "schema":
        phase_schema()
    else:
        sys.exit(f"phase {args.phase} not written yet")


if __name__ == "__main__":
    main()
