"""017 — The queue that is past its own date: gated, idempotent runner.

    uv run --group registers python investigations/017-the-overdue-queue/run.py \\
        --seal <prefix of DECLARATION.md's SHA-256> --phase all

Phases:

- ``compute`` (needs the seal): read the one copy the declaration names,
  verify its bytes against the journal, run the census, check C1 to C5 and
  the falsifiers, and write the evidence. Selected rows are **append-only**
  (``evidence/rows.ndjson``); a line that would change on recompute stops
  the run.
- ``check`` (needs the seal): recompute and compare without writing.
- ``render``: ``FINDINGS.md`` as a pure function of the evidence and of the
  certificates 014 issued. Needs no seal.

Nothing is fetched. The copy is the one already journalled on 2026-09-15.
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import overdue_queue as oq
from grid_mysteries.rendering import overdue_queue as page
from grid_mysteries.sources import tec_register as tr

HERE = Path(__file__).parent
DECLARATION = HERE / "DECLARATION.md"
EVIDENCE = HERE / "evidence"
CENSUS_JSON = EVIDENCE / "census.json"
ROWS_NDJSON = EVIDENCE / "rows.ndjson"
RUN_LOG = EVIDENCE / "run-log.json"
FINDINGS = HERE / "FINDINGS.md"
JOURNAL = REPO_ROOT / tr.JOURNAL_PATH
SCHEMA_REPORT = REPO_ROOT / "archives" / "tec-register" / "schema-report.json"
CERTIFICATES = REPO_ROOT / "investigations" / "014-gb-connection-slippage" / "certificates"

#: The copy this declaration names, by date and by digest (R1).
COPY_DATE = date(2026, 9, 15)
COPY_SHA256 = "d13406e495746f1b80e725321a5c7f95e21e0da16830bb6bd1f94ece172c9d5b"
MIN_SEAL_LENGTH = 8


def digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def require_seal(seal: str | None) -> str:
    sealed = digest()
    if not seal or len(seal) < MIN_SEAL_LENGTH or not sealed.startswith(seal.lower()):
        raise SystemExit(
            f"refusing: --seal must be a prefix (>= {MIN_SEAL_LENGTH} hex) of "
            f"DECLARATION.md's SHA-256 {sealed[:16]}…"
        )
    return sealed


def timestamps() -> dict[str, Any] | None:
    sidecar = DECLARATION.with_name(DECLARATION.name + ".timestamps.json")
    if not sidecar.exists():
        return None
    stamps = json.loads(sidecar.read_text())
    return {
        "sha256": stamps["sha256"],
        "matches_declaration": stamps["sha256"] == digest(),
        "proofs": [
            {k: v for k, v in p.items() if k in ("kind", "tsa", "path", "tsa_time", "status")}
            for p in stamps["proofs"]
        ],
    }


def the_copy() -> tuple[dict, list[dict[str, object]]]:
    """The copy the declaration names, refusing anything else (R1)."""
    entries = tr.one_per_date(tr.read_journal(JOURNAL))
    latest = entries[-1]
    if latest["t_public"][:10] != COPY_DATE.isoformat() or latest["sha256"] != COPY_SHA256:
        raise SystemExit(
            f"refusing: the declaration names the copy of {COPY_DATE} "
            f"(SHA-256 {COPY_SHA256[:16]}…); the latest journalled copy is "
            f"{latest['t_public'][:10]} (SHA-256 {latest['sha256'][:16]}…). "
            "A census over a different copy needs its own declaration."
        )
    tr.verify_entry(latest, REPO_ROOT)
    rows = tr.read_vintage(REPO_ROOT / latest["path"], latest.get("format", ""))
    return latest, rows


def external_checks(
    result: dict[str, Any], rows: list[dict[str, object]]
) -> tuple[dict[str, bool], dict[str, int]]:
    """C1 and C4, the two checks that look outside the census itself, and the
    copy's status counts that C1 compares against the committed schema
    report. Those counts are the check's own evidence, not a breakdown: the
    same numbers are already published in `archives/tec-register/`."""
    report = json.loads(SCHEMA_REPORT.read_text())
    per_copy = {c["t_public"]: c for c in report["per_copy"]}
    copy = per_copy.get(COPY_DATE.isoformat(), {})
    counted: dict[str, int] = {}
    for row in rows:
        counted[oq.status(row)] = counted.get(oq.status(row), 0) + 1
    parsed, _skipped = tr.load_vintages(JOURNAL, REPO_ROOT)
    suspect = {s.t_public for s in cs.partial_exports([(t, len(r)) for t, r, _e in parsed])}
    by_date = {t: r for t, r, _e in parsed}
    return {
        "C1 the status counts equal the schema report's for this copy": (
            counted == copy.get("project_status") and sum(counted.values()) == result["rows_total"]
        ),
        "C4 the copy is in the series' reading with the same row count, and is not suspect": (
            len(by_date.get(COPY_DATE, [])) == result["rows_total"]
            and COPY_DATE not in suspect
            and not copy.get("flags")
        ),
    }, dict(sorted(counted.items(), key=lambda kv: (-kv[1], kv[0])))


def row_line(row: Any) -> str:
    """One selected row as one NDJSON line, through the evidence serialiser."""
    return json.dumps(json.loads(dumps(row)), separators=(",", ":"))


def compute(seal: str, run_date: str, *, write: bool) -> None:
    sealed = require_seal(seal)
    entry, rows = the_copy()
    result = oq.census(rows, COPY_DATE)
    checks, status_counts = external_checks(result, rows)
    result["checks"].update(checks)

    failed = [name for name, ok in result["checks"].items() if not ok]
    if failed:
        raise SystemExit("refusing: check(s) failed: " + "; ".join(failed))
    fired = [name for name, hit in result["falsifiers"].items() if hit]

    serialised = {r.index: row_line(r) for r in result["rows"]}
    committed: dict[int, str] = {}
    if ROWS_NDJSON.exists():
        for line in ROWS_NDJSON.read_text().splitlines():
            if line.strip():
                committed[json.loads(line)["index"]] = line
    changed = [k for k, line in serialised.items() if k in committed and committed[k] != line]
    new = [k for k in serialised if k not in committed]
    if not write:
        print(
            f"check: {len(serialised)} rows recomputed, {len(new)} not yet committed, "
            f"{len(changed)} committed row(s) would change"
        )
        raise SystemExit(1 if changed else 0)
    if changed:
        raise SystemExit(
            f"refusing: {len(changed)} committed row(s) would change on recompute. "
            "Rows are append-only (C5); record an amendment before rerunning."
        )

    computed_at = datetime.now(UTC).isoformat(timespec="seconds")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with ROWS_NDJSON.open("a") as out:
        for key in new:
            out.write(serialised[key] + "\n")
    summary = {
        "investigation": "017",
        "declaration": DECLARATION.name,
        "declaration_sha256": sealed,
        "declaration_timestamps": timestamps(),
        "schema_report_sha256": hashlib.sha256(SCHEMA_REPORT.read_bytes()).hexdigest(),
        "seal": seal,
        "run_date": run_date,
        "computed_at": computed_at,
        "copy": {
            "t_public": entry["t_public"][:10],
            "path": entry["path"],
            "sha256": entry["sha256"],
            "bytes": entry.get("bytes"),
            "source": entry.get("source"),
            "url": entry.get("url"),
            "t_public_basis": entry.get("t_public_basis"),
        },
        "status_counts_all_rows": status_counts,
        "rows_file": ROWS_NDJSON.name,
        "rows_appended": len(new),
        "falsifiers_fired": fired,
        **{
            k: v for k, v in result.items() if k not in ("rows", "earliest", "repeated_project_ids")
        },
        "earliest": result["earliest"],
        "repeated_project_ids": result["repeated_project_ids"],
    }
    write_json(CENSUS_JSON, summary)
    log = json.loads(RUN_LOG.read_text()) if RUN_LOG.exists() else []
    log.append(
        {
            "run_date": run_date,
            "computed_at": computed_at,
            "seal": seal,
            "declaration_sha256": sealed,
            "copy": entry["t_public"][:10],
            "selected_rows": result["selected_rows"],
            "rows_appended": len(new),
            "falsifiers_fired": fired,
        }
    )
    write_json(RUN_LOG, log)
    print(
        f"census of {entry['t_public'][:10]}: {result['selected_rows']} rows, "
        f"{result['selected_mw']} MW (rows); "
        f"{result['distinct_project_ids']} ids, {result['selected_mw_largest_per_id']} MW (ids)"
    )
    print(f"checks: all {len(result['checks'])} pass; falsifiers fired: {fired or 'none'}")


def certificates() -> list[dict[str, Any]]:
    """The Eggborough certificate bundles, read from 014's manifests."""
    out = []
    for manifest_path in sorted(CERTIFICATES.glob("eggborough*/MANIFEST.json")):
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
        record = json.loads((manifest_path.parent / "certificate.json").read_text())
        extracts = [
            json.loads(line)
            for line in (manifest_path.parent / "extracts.ndjson").read_text().splitlines()
            if line.strip()
        ]
        out.append(
            {
                "bundle": manifest["bundle"],
                "certificate_id": hashlib.sha256(manifest_bytes).hexdigest(),
                "project": manifest["project"],
                "stage": manifest.get("stage"),
                "dates": manifest["dates"],
                "record": record,
                "status_trace": oq.status_trace(
                    extracts, lambda r: oq.names_a_gas_turbine_plant(r["Plant type"])
                ),
            }
        )
    return out


def render() -> None:
    census = json.loads(CENSUS_JSON.read_text())
    rows = [json.loads(line) for line in ROWS_NDJSON.read_text().splitlines() if line.strip()]
    FINDINGS.write_text(page.render_findings(census, rows, certificates()))
    print(f"rendered {FINDINGS.relative_to(REPO_ROOT)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seal", help="prefix of the declaration's SHA-256")
    parser.add_argument("--phase", choices=("compute", "check", "render", "all"), default="render")
    parser.add_argument("--run-date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    if args.phase == "check":
        compute(args.seal, args.run_date, write=False)
        return
    if args.phase in ("compute", "all"):
        compute(args.seal, args.run_date, write=True)
    if args.phase in ("render", "all"):
        render()


if __name__ == "__main__":
    sys.exit(main())
