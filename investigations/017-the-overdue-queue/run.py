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

``--version 2`` runs the Gate cross-tab under ``DECLARATION-v2.md`` instead:
it takes version 1's committed selection as given (and refuses if it reads a
different one), splits the copy and the selection by the register's ``Gate``
column, and reads the four copies that carry that column to show what each
published for every overdue row in the confirmed tier.

Nothing is fetched. The copy is the one already journalled on 2026-09-15.
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
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
DECLARATION_V2 = HERE / "DECLARATION-v2.md"
EVIDENCE = HERE / "evidence"
CENSUS_JSON = EVIDENCE / "census.json"
ROWS_NDJSON = EVIDENCE / "rows.ndjson"
RUN_LOG = EVIDENCE / "run-log.json"
GATE_JSON = EVIDENCE / "gate.json"
GATE_ROWS = EVIDENCE / "gate-rows.ndjson"
FINDINGS = HERE / "FINDINGS.md"
JOURNAL = REPO_ROOT / tr.JOURNAL_PATH
SCHEMA_REPORT = REPO_ROOT / "archives" / "tec-register" / "schema-report.json"
CERTIFICATES = REPO_ROOT / "investigations" / "014-gb-connection-slippage" / "certificates"

#: The copy this declaration names, by date and by digest (R1).
COPY_DATE = date(2026, 9, 15)
COPY_SHA256 = "d13406e495746f1b80e725321a5c7f95e21e0da16830bb6bd1f94ece172c9d5b"
#: NESO's own published definition of the two gates, pinned in this repository
#: and journalled by F001 on 2026-08-23; version 2 quotes it and reads the
#: register's `1` and `2` against it.
GATE_DEFINITION = {
    "path": "data/raw/neso/neso-g2wq-evidence-handbook-resources.html",
    "sha256": "cb5c712b7f43fa545725bae4cb942c2c4353b8c0a2095c5a65ce7694de6bb514",
    "url": (
        "https://www.neso.energy/industry-information/connections-reform/"
        "evidence-handbook-and-other-g2wq-submission-resources"
    ),
    "fetched_at": "2026-08-23T07:14:26.611756+00:00",
    "journal": (
        "investigations/forward/F001-connection-readiness/evidence/public-as-of-journal.ndjson"
    ),
}
MIN_SEAL_LENGTH = 8


def digest(declaration: Path = DECLARATION) -> str:
    return hashlib.sha256(declaration.read_bytes()).hexdigest()


def require_seal(seal: str | None, declaration: Path = DECLARATION) -> str:
    sealed = digest(declaration)
    if not seal or len(seal) < MIN_SEAL_LENGTH or not sealed.startswith(seal.lower()):
        raise SystemExit(
            f"refusing: --seal must be a prefix (>= {MIN_SEAL_LENGTH} hex) of "
            f"{declaration.name}'s SHA-256 {sealed[:16]}…"
        )
    return sealed


def timestamps(declaration: Path = DECLARATION) -> dict[str, Any] | None:
    sidecar = declaration.with_name(declaration.name + ".timestamps.json")
    if not sidecar.exists():
        return None
    stamps = json.loads(sidecar.read_text())
    return {
        "sha256": stamps["sha256"],
        "matches_declaration": stamps["sha256"] == digest(declaration),
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


# --------------------------------------------------------------- version 2


def gated_copies() -> list[tuple[str, list[dict[str, object]]]]:
    """The copies that carry a Gate column, oldest first, named by the schema
    report rather than by this runner's own scan, and each verified against
    its journalled digest before it is read."""
    report = json.loads(SCHEMA_REPORT.read_text())
    wanted = [
        c["t_public"] for c in report["per_copy"] if any(value for value in (c.get("gate") or {}))
    ]
    by_date = {e["t_public"][:10]: e for e in tr.one_per_date(tr.read_journal(JOURNAL))}
    out = []
    for t_public in sorted(wanted):
        entry = by_date.get(t_public)
        if entry is None:
            continue
        tr.verify_entry(entry, REPO_ROOT)
        rows = tr.read_vintage(REPO_ROOT / entry["path"], entry.get("format", ""))
        if rows:
            out.append((t_public, rows))
    return out


def gate_checks(
    gate: dict[str, Any], rows: list[dict[str, object]], committed: dict[str, Any]
) -> dict[str, bool]:
    """C6, C8 and C9. C7 is checked against the committed rows in `compute_gate`."""
    report = json.loads(SCHEMA_REPORT.read_text())
    per_copy = {c["t_public"]: c for c in report["per_copy"]}
    vocabulary = per_copy.get(COPY_DATE.isoformat(), {}).get("gate") or {}
    counted: dict[str, int] = {}
    for row in rows:
        counted[oq.gate_of(row)] = counted.get(oq.gate_of(row), 0) + 1
    overdue_rows = sum(g["rows"] for g in gate["g2_overdue_by_gate"])
    overdue_mw = sum((Decimal(str(g["mw"])) for g in gate["g2_overdue_by_gate"]), Decimal(0))
    return {
        "C6 the Gate counts equal the schema report's for this copy": (
            counted == vocabulary and sum(counted.values()) == len(rows)
        ),
        "C8 the Gate split sums to version 1's committed census": (
            overdue_rows == committed["selected_rows"]
            and overdue_mw == Decimal(str(committed["selected_mw"]))
        ),
        "C9 every selected row's Gate cell is in the copy's vocabulary": all(
            g["gate"] in vocabulary for g in gate["g2_overdue_by_gate"]
        ),
    }


def compute_gate(seal: str, run_date: str, *, write: bool) -> None:
    sealed = require_seal(seal, DECLARATION_V2)
    entry, rows = the_copy()
    committed = json.loads(CENSUS_JSON.read_text())
    result = oq.census(rows, COPY_DATE)

    # C7: version 1's selection is taken as given, never re-chosen here.
    recomputed = {r.index: row_line(r) for r in result["rows"]}
    on_disk = {
        json.loads(line)["index"]: line
        for line in ROWS_NDJSON.read_text().splitlines()
        if line.strip()
    }
    if recomputed != on_disk:
        raise SystemExit(
            "refusing: this version reads a different selection from the one version 1 "
            "committed. Version 1 is not amended by version 2."
        )

    copies = gated_copies()
    gate = oq.gate_census(rows, result, copies)
    checks = gate_checks(gate, rows, committed)
    checks["C7 the selection is version 1's, unchanged"] = True
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("refusing: check(s) failed: " + "; ".join(failed))

    fired = [name for name, hit in gate["falsifiers"].items() if hit]
    if gate["falsifiers"][
        "F4 the Gate column carries a value the pinned definition does not cover"
    ]:
        raise SystemExit(
            "refusing: F4 fired. The Gate column carries "
            f"{gate['unknown_gate_values']}, which NESO's pinned definition does not cover. "
            "Name and read the value in an amended declaration before publishing."
        )
    suppress_g6 = gate["falsifiers"]["F6 fewer than three gated copies are readable"]

    serialised = {g.index: row_line(g) for g in gate["g4_confirmed_tier_overdue"]}
    already: dict[int, str] = {}
    if GATE_ROWS.exists():
        for line in GATE_ROWS.read_text().splitlines():
            if line.strip():
                already[json.loads(line)["index"]] = line
    changed = [k for k, line in serialised.items() if k in already and already[k] != line]
    new = [k for k in serialised if k not in already]
    if not write:
        print(
            f"check: {len(serialised)} confirmed-tier rows recomputed, {len(new)} not yet "
            f"committed, {len(changed)} committed row(s) would change"
        )
        raise SystemExit(1 if changed else 0)
    if changed:
        raise SystemExit(
            f"refusing: {len(changed)} committed Gate row(s) would change on recompute."
        )

    computed_at = datetime.now(UTC).isoformat(timespec="seconds")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with GATE_ROWS.open("a") as out:
        for key in new:
            out.write(serialised[key] + "\n")
    summary = {
        "investigation": "017",
        "declaration": DECLARATION_V2.name,
        "declaration_sha256": sealed,
        "declaration_timestamps": timestamps(DECLARATION_V2),
        "version_1_declaration_sha256": digest(DECLARATION),
        "schema_report_sha256": hashlib.sha256(SCHEMA_REPORT.read_bytes()).hexdigest(),
        "gate_definition": GATE_DEFINITION,
        "seal": seal,
        "run_date": run_date,
        "computed_at": computed_at,
        "copy": {
            "t_public": entry["t_public"][:10],
            "path": entry["path"],
            "sha256": entry["sha256"],
        },
        "rows_total": len(rows),
        "checks": checks,
        "falsifiers_fired": fired,
        "g6_suppressed": suppress_g6,
        **{k: v for k, v in gate.items() if k != "falsifiers"},
        "falsifiers": gate["falsifiers"],
    }
    write_json(GATE_JSON, summary)
    confirmed = next((g for g in gate["g1_copy_by_gate"] if g["gate"] == oq.CONFIRMED_TIER), None)
    print(
        f"gate cross-tab over {entry['t_public'][:10]}: confirmed tier carries "
        f"{confirmed['rows'] if confirmed else 0} rows / {confirmed['mw'] if confirmed else 0} MW; "
        f"{gate['confirmed_tier_overdue_rows']} of them "
        f"({gate['confirmed_tier_overdue_mw']} MW) are past their date"
    )
    print(f"gated copies: {', '.join(gate['g6_gated_copies'])}")
    print(f"checks: all {len(checks)} pass; falsifiers fired: {fired or 'none'}")


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
    gate = json.loads(GATE_JSON.read_text()) if GATE_JSON.exists() else None
    FINDINGS.write_text(page.render_findings(census, rows, certificates(), gate))
    print(f"rendered {FINDINGS.relative_to(REPO_ROOT)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seal", help="prefix of the declaration's SHA-256")
    parser.add_argument("--phase", choices=("compute", "check", "render", "all"), default="render")
    parser.add_argument(
        "--version",
        type=int,
        choices=(1, 2),
        default=1,
        help="1 is the census (DECLARATION.md); 2 is the Gate cross-tab (DECLARATION-v2.md)",
    )
    parser.add_argument("--run-date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    run_one = compute if args.version == 1 else compute_gate
    if args.phase == "check":
        run_one(args.seal, args.run_date, write=False)
        return
    if args.phase in ("compute", "all"):
        run_one(args.seal, args.run_date, write=True)
    if args.phase in ("render", "all"):
        render()


if __name__ == "__main__":
    sys.exit(main())
