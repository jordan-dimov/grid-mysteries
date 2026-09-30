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
- ``render``: ``FINDINGS.md`` as a pure function of the evidence, of the
  certificates 014 issued and of ``corrections.json``, and the web page
  ``site/overdue-queue/index.html`` from it. Needs no seal.

``--version 2`` runs the Gate cross-tab under ``DECLARATION-v2.md`` instead:
it takes version 1's committed selection as given (and refuses if it reads a
different one), splits the copy and the selection by the register's ``Gate``
column, and reads the four copies that carry that column to show what each
published for every overdue row in the confirmed tier.

``--version 3`` runs ``DECLARATION-v3.md``: the same method over copies the
daily capture holds, read from the mirror after each digest is checked
against its committed manifest. In order, each step committed before the
next: ``--phase method-check`` (C10, versions 1 and 2 reproduced on the
captured copy of 15 September); ``--phase compute --copy reference``;
``scripts/schema-report tec-capture`` for the next copy, then ``--phase n0``;
``--phase compute --copy next``; ``--phase compare`` (D1, D2).

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
CORRECTIONS = HERE / "corrections.json"
DECLARATION_V3 = HERE / "DECLARATION-v3.md"
PAGE = REPO_ROOT / "site" / "overdue-queue" / "index.html"
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


# --------------------------------------------------------------- version 3

V3 = EVIDENCE / "v3"
METHOD_CHECK = V3 / "method-check.json"
COMPARISON = V3 / "comparison.json"
MANIFESTS = REPO_ROOT / "data" / "manifests"
MIRROR = REPO_ROOT / "data" / "raw" / "archive"
CAPTURE_REPORT = REPO_ROOT / "archives" / "tec-register-capture" / "schema-report.json"
#: R1′: the reference copy, named by digest.
REFERENCE_T_PUBLIC = "2026-09-25"
REFERENCE_SHA256 = "da0b67b5ea34a85606f3a98269916f647c32a0f3b496f91a1136e80069175a6c"
#: The keys of version 1's census.json that C10 requires to reproduce.
C10_CENSUS_KEYS = (
    "status_counts_all_rows",
    "as_of",
    "rows_total",
    "undated",
    "dated",
    "dated_built",
    "dated_not_built_future",
    "selected_rows",
    "selected_mw",
    "selected_rows_without_capacity",
    "selected_rows_zero_capacity",
    "selected_rows_negative_capacity",
    "selected_mw_negative",
    "selected_rows_without_project_id",
    "distinct_project_ids",
    "selected_mw_largest_per_id",
    "by_status",
    "by_plant_type",
    "by_year",
    "swap_sensitivity",
    "scale",
    "checks",
    "falsifiers",
    "earliest",
    "repeated_project_ids",
)
#: The keys of version 2's gate.json that C10 requires to reproduce (G1 to G6).
C10_GATE_KEYS = (
    "rows_total",
    "g1_copy_by_gate",
    "g2_overdue_by_gate",
    "g3_overdue_by_gate_and_status",
    "g4_confirmed_tier_overdue",
    "g5_repetition",
    "g6_gated_copies",
    "g6_summary",
    "confirmed_tier_overdue_rows",
    "confirmed_tier_overdue_mw",
    "unknown_gate_values",
    "falsifiers",
)


def plain(obj: Any) -> Any:
    """`obj` as the evidence serialiser writes it, read back: what a committed
    file holds, so a recomputed value and a committed one compare exactly."""
    return json.loads(dumps(obj))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def committed(path: Path) -> bool:
    """Whether the file is tracked and unchanged against HEAD: the order of
    work says no step starts before the previous one is committed."""
    import subprocess

    rel = str(path.relative_to(REPO_ROOT))
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel], cwd=REPO_ROOT, capture_output=True
    )
    clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=REPO_ROOT)
    return tracked.returncode == 0 and clean.returncode == 0


def capture_entries() -> list[dict]:
    """Captured copies as the committed daily manifests record them."""
    return tr.capture_entries(sorted(MANIFESTS.glob("*.ndjson")))


def read_capture(entry: dict) -> list[dict[str, object]]:
    """A captured copy's rows, read from the mirror only after its bytes hash
    to the digest its manifest recorded."""
    path = MIRROR / entry["key"]
    if tr.sha256_file(path) != entry["sha256"]:
        raise SystemExit(f"refusing: {entry['key']} does not match its manifested digest")
    return tr.read_vintage(path, "csv")


def capture_copy_report(sha256: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """The capture schema report and this copy's entry in it, by digest."""
    report = json.loads(CAPTURE_REPORT.read_text())
    copy = next((c for c in report["per_copy"] if c["sha256"] == sha256), None)
    if copy is None:
        raise SystemExit(
            f"refusing: the capture schema report does not cover the copy {sha256[:16]}…; "
            "rerun scripts/schema-report tec-capture and commit it first (N0)"
        )
    return report, copy


def gated_copies_v3(as_of: date) -> list[dict[str, Any]]:
    """G6′: the four gated copies version 2 read, then every captured copy
    dated later than 15 September and no later than the copy under census,
    one reading per distinct digest, oldest first (`oq.gated_copies_for`).
    Each is verified against its journal or its manifest before it is read."""
    report = json.loads(SCHEMA_REPORT.read_text())
    wanted = {
        c["t_public"] for c in report["per_copy"] if any(value for value in (c.get("gate") or {}))
    }
    journalled = [
        {"t_public": e["t_public"][:10], "sha256": e["sha256"], "source": "journal", "entry": e}
        for e in tr.one_per_date(tr.read_journal(JOURNAL))
        if e["t_public"][:10] in wanted
    ]
    captured = [
        {"t_public": e["t_public"], "sha256": e["sha256"], "source": "capture", "entry": e}
        for e in capture_entries()
    ]
    out = []
    for copy in oq.gated_copies_for(journalled, captured, COPY_DATE, as_of):
        entry = copy.pop("entry")
        if copy["source"] == "journal":
            tr.verify_entry(entry, REPO_ROOT)
            rows = tr.read_vintage(REPO_ROOT / entry["path"], entry.get("format", ""))
        else:
            rows = read_capture(entry)
        if rows:
            out.append({**copy, "rows": rows})
    return out


def census_of(entry: dict) -> dict[str, Any]:
    """This version's method over one captured copy: version 1's census, R2′,
    version 2's cross-tab with G6′. Pure of any check that looks outside it,
    so C10 and the two censuses run exactly the same code."""
    rows = read_capture(entry)
    as_of = date.fromisoformat(entry["t_public"])
    result = oq.census(rows, as_of)
    gated = gated_copies_v3(as_of)
    gate = oq.gate_census(rows, result, [(g["t_public"], g["rows"]) for g in gated])
    return {
        "rows": rows,
        "result": result,
        "gate": gate,
        "gated": [{k: g[k] for k in ("t_public", "sha256", "source")} for g in gated],
        "filename": oq.filename_sensitivity(result, oq.filename_date(entry["filename"])),
    }


def method_check(*, write: bool) -> bool:
    """C10: this runner, applied to the captured copy of 15 September, must
    reproduce version 1's committed selection line for line with its totals
    and breakdowns, and version 2's G1 to G6, to the last penny."""
    entry = next((e for e in capture_entries() if e["sha256"] == COPY_SHA256), None)
    if entry is None:
        raise SystemExit("refusing: no captured copy carries version 1's digest")
    run = census_of(entry)
    result, gate = run["result"], run["gate"]

    v1_lines = [line for line in ROWS_NDJSON.read_text().splitlines() if line.strip()]
    new_lines = [row_line(r) for r in result["rows"]]
    v1 = json.loads(CENSUS_JSON.read_text())
    status_counts: dict[str, int] = {}
    for row in run["rows"]:
        status_counts[oq.status(row)] = status_counts.get(oq.status(row), 0) + 1
    recomputed = plain(
        {
            **{k: v for k, v in result.items() if k != "rows"},
            "status_counts_all_rows": dict(
                sorted(status_counts.items(), key=lambda kv: (-kv[1], kv[0]))
            ),
        }
    )
    # Version 1's C1 and C4 checked artefacts outside the census; its committed
    # `checks` carry them beside C2 and C3, and only C2 and C3 are recomputed.
    census_keys = {
        k: (
            {c: recomputed["checks"].get(c) for c in v1["checks"] if c in recomputed["checks"]}
            == {c: v1["checks"][c] for c in v1["checks"] if c in recomputed["checks"]}
            if k == "checks"
            else recomputed.get(k) == v1.get(k)
        )
        for k in C10_CENSUS_KEYS
    }
    v2 = json.loads(GATE_JSON.read_text())
    gate_plain = plain({**gate, "rows_total": len(run["rows"])})
    gate_keys = {k: gate_plain.get(k) == v2.get(k) for k in C10_GATE_KEYS}
    v2_lines = [line for line in GATE_ROWS.read_text().splitlines() if line.strip()]
    new_gate_lines = [row_line(g) for g in gate["g4_confirmed_tier_overdue"]]

    def lines(old: list[str], new: list[str]) -> dict[str, Any]:
        return {
            "committed": len(old),
            "recomputed": len(new),
            "identical": sum(1 for a, b in zip(old, new, strict=False) if a == b),
            "differing_line_numbers": [
                i + 1 for i, (a, b) in enumerate(zip(old, new, strict=False)) if a != b
            ],
            "pass": old == new,
        }

    rows_cmp = lines(v1_lines, new_lines)
    gate_cmp = lines(v2_lines, new_gate_lines)
    passed = (
        rows_cmp["pass"]
        and gate_cmp["pass"]
        and all(census_keys.values())
        and all(gate_keys.values())
    )
    record = {
        "investigation": "017",
        "check": "C10",
        "declaration": DECLARATION_V3.name,
        "declaration_sha256": digest(DECLARATION_V3),
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "copy": {
            "t_public": entry["t_public"],
            "sha256": entry["sha256"],
            "key": entry["key"],
            "manifest": entry["manifest"],
            "manifest_sha256": file_sha256(MANIFESTS / entry["manifest"]),
            "filename": entry["filename"],
            "same_digest_as_versions_1_and_2": entry["sha256"] == COPY_SHA256,
        },
        "version_1": {
            "declaration_sha256": v1["declaration_sha256"],
            "rows_ndjson_sha256": file_sha256(ROWS_NDJSON),
            "census_json_sha256": file_sha256(CENSUS_JSON),
            "rows_line_for_line": rows_cmp,
            "totals_and_breakdowns": census_keys,
        },
        "version_2": {
            "declaration_sha256": v2["declaration_sha256"],
            "gate_rows_ndjson_sha256": file_sha256(GATE_ROWS),
            "gate_json_sha256": file_sha256(GATE_JSON),
            "gate_rows_line_for_line": gate_cmp,
            "g1_to_g6": gate_keys,
            "gated_copies_read": run["gated"],
        },
        "filename_sensitivity": plain(run["filename"]),
        "pass": passed,
    }
    print(
        f"C10 over the captured copy of {entry['t_public']} ({entry['sha256'][:16]}…): "
        f"v1 rows {rows_cmp['identical']}/{rows_cmp['committed']} identical, "
        f"v1 keys {sum(census_keys.values())}/{len(census_keys)}, "
        f"v2 rows {gate_cmp['identical']}/{gate_cmp['committed']}, "
        f"v2 keys {sum(gate_keys.values())}/{len(gate_keys)}: " + ("PASS" if passed else "FAIL")
    )
    if write:
        write_json(METHOD_CHECK, record)
        print(f"wrote {METHOD_CHECK.relative_to(REPO_ROOT)}")
    return passed


def copy_checks(
    run: dict[str, Any], entry: dict, report: dict[str, Any], copy: dict[str, Any]
) -> dict[str, bool]:
    """C1′ to C4′ and C6′, C8′, C9′ for one copy, against the capture
    schema report. C2′ and C3′ come from the census itself."""
    rows, result, gate = run["rows"], run["result"], run["gate"]
    counted: dict[str, int] = {}
    gates: dict[str, int] = {}
    for row in rows:
        counted[oq.status(row)] = counted.get(oq.status(row), 0) + 1
        gates[oq.gate_of(row)] = gates.get(oq.gate_of(row), 0) + 1
    ordered = sorted(report["per_copy"], key=lambda c: c["t_public"])
    counts = [(date.fromisoformat(c["t_public"]), c["rows"]) for c in ordered]
    suspect = {s.t_public for s in cs.partial_exports(counts)}
    overdue_rows = sum(g["rows"] for g in gate["g2_overdue_by_gate"])
    overdue_mw = sum((Decimal(str(g["mw"])) for g in gate["g2_overdue_by_gate"]), Decimal(0))
    vocabulary = copy.get("gate") or {}
    return {
        "C1′ the status counts equal the capture schema report's for this copy": (
            counted == copy["project_status"]
            and sum(counted.values()) == result["rows_total"] == copy["rows"]
        ),
        "C2′ dated plus undated is every row": result["checks"][
            "C2 dated plus undated is every row"
        ],
        "C3′ the four classes partition every row": result["checks"][
            "C3 the four classes partition every row"
        ],
        "C4′ the copy carries no flag and the partial-export rule does not make it suspect": (
            not copy["flags"] and date.fromisoformat(entry["t_public"]) not in suspect
        ),
        "C6′ the Gate counts equal the capture schema report's for this copy": (
            gates == vocabulary and sum(gates.values()) == len(rows)
        ),
        "C8′ the Gate split sums to this version's census of the copy": (
            overdue_rows == result["selected_rows"] and overdue_mw == result["selected_mw"]
        ),
        "C9′ every selected row's Gate cell is in the copy's vocabulary": all(
            g["gate"] in vocabulary for g in gate["g2_overdue_by_gate"]
        ),
    }


def append_only(path: Path, lines: dict[int, str], *, write: bool) -> tuple[list[int], list[int]]:
    """C5′: the new and the changed lines against a committed file, keyed by
    row index; a changed line stops the run before anything is written."""
    already: dict[int, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                already[json.loads(line)["index"]] = line
    changed = [k for k, line in lines.items() if k in already and already[k] != line]
    new = [k for k in lines if k not in already]
    if write and changed:
        raise SystemExit(
            f"refusing: {len(changed)} committed line(s) of {path.name} would change on "
            "recompute (C5′). Rows are append-only; record an amendment before rerunning."
        )
    if write and new:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as out:
            for key in new:
                out.write(lines[key] + "\n")
    return new, changed


def which_copy(name: str) -> tuple[dict, dict[str, Any]]:
    """R1′: the reference copy by digest, or the next copy by rule, with what
    the manifests say about the days before it was captured."""
    entries = capture_entries()
    if name == "reference":
        entry = next((e for e in entries if e["sha256"] == REFERENCE_SHA256), None)
        if entry is None or entry["t_public"] != REFERENCE_T_PUBLIC:
            raise SystemExit(
                f"refusing: the reference copy {REFERENCE_SHA256[:16]}… dated "
                f"{REFERENCE_T_PUBLIC} is not in the committed manifests"
            )
        return entry, {"rule": "named by digest in DECLARATION-v3.md"}
    entry = oq.next_copy(entries)
    if entry is None:
        raise SystemExit(
            f"no captured copy is dated on or after {oq.NEXT_COPY_FROM}; if none is by "
            f"{oq.NEXT_COPY_DEADLINE}, that is the outcome (R1′)"
        )
    captured_on = date.fromisoformat(entry["fetched_at"][:10])
    days: set[date] = set()
    for manifest in sorted(MANIFESTS.glob("*.ndjson")):
        for line in manifest.read_text().splitlines():
            if line.strip() and json.loads(line).get("dataset", "").startswith(tr.CAPTURE_DATASET):
                days.add(date.fromisoformat(json.loads(line)["day"]))
    gaps = oq.capture_gaps(days, oq.NEXT_COPY_FROM, captured_on)
    return entry, {
        "rule": (f"the earliest captured copy with last_modified on or after {oq.NEXT_COPY_FROM}"),
        "captured_on": captured_on,
        "days_checked": [oq.NEXT_COPY_FROM, captured_on],
        "days_with_no_tec_record": gaps,
    }


def n0_verdict(seal: str) -> bool:
    """N0 for the next copy, from the committed capture schema report alone:
    the verdict is written whichever way it comes out, and no census figure
    of the next copy is computed here (F8)."""
    sealed = require_seal(seal, DECLARATION_V3)
    if not committed(CAPTURE_REPORT):
        raise SystemExit("refusing: commit the schema pass before recording N0")
    entry, selection = which_copy("next")
    report, copy = capture_copy_report(entry["sha256"])
    columns = next(e["columns"] for e in report["eras"] if e["last"] >= REFERENCE_T_PUBLIC)
    verdict = oq.n0(copy, columns)
    passed = all(verdict.values())
    write_json(
        V3 / "n0.json",
        {
            "investigation": "017",
            "version": 3,
            "rule": "N0",
            "declaration": DECLARATION_V3.name,
            "declaration_sha256": sealed,
            "capture_schema_report_sha256": file_sha256(CAPTURE_REPORT),
            "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "selection": selection,
            "copy": {
                k: entry[k]
                for k in ("t_public", "t_public_basis", "filename", "sha256", "bytes", "key")
            },
            "schema_report_entry": {
                k: copy[k]
                for k in ("rows", "columns", "date_spellings", "project_status", "gate", "flags")
            },
            "verdict": verdict,
            "pass": passed,
            "consequence": (
                "the next census may be computed under this version"
                if passed
                else "F8: no census of this copy is computed under this version and the "
                "comparison is not run; a reading for what changed must be declared and "
                "witnessed as an amendment, written from the schema report alone, before "
                "any figure is computed"
            ),
        },
    )
    print(
        f"N0 for {entry['t_public']} ({entry['sha256'][:16]}…): "
        + ("PASS" if passed else "FAIL: " + "; ".join(k for k, ok in verdict.items() if not ok))
    )
    return passed


def compute_v3(seal: str, run_date: str, which: str, *, write: bool) -> None:
    sealed = require_seal(seal, DECLARATION_V3)
    if not METHOD_CHECK.exists() or not json.loads(METHOD_CHECK.read_text())["pass"]:
        raise SystemExit("refusing: C10 has not passed; run --phase method-check first (F7)")
    if write and not committed(METHOD_CHECK):
        raise SystemExit("refusing: commit evidence/v3/method-check.json before any census")
    entry, selection = which_copy(which)
    if which == "next":
        ref_census = V3 / REFERENCE_T_PUBLIC / "census.json"
        if write and not (ref_census.exists() and committed(ref_census)):
            raise SystemExit("refusing: commit the reference census before the next one")
        if write and not committed(CAPTURE_REPORT):
            raise SystemExit("refusing: commit the N0 schema pass before the next census")
    report, copy = capture_copy_report(entry["sha256"])
    n0 = None
    if which == "next":
        columns = next(e["columns"] for e in report["eras"] if e["last"] >= REFERENCE_T_PUBLIC)
        n0 = oq.n0(copy, columns)
        if not all(n0.values()):
            raise SystemExit(
                "refusing: N0 fails for the next copy (F8): "
                + "; ".join(k for k, ok in n0.items() if not ok)
            )

    run = census_of(entry)
    result, gate = run["result"], run["gate"]
    checks = copy_checks(run, entry, report, copy)
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("refusing: check(s) failed: " + "; ".join(failed))
    if gate["falsifiers"][
        "F4 the Gate column carries a value the pinned definition does not cover"
    ]:
        raise SystemExit(f"refusing: F4 fired on {gate['unknown_gate_values']}")

    out = V3 / entry["t_public"]
    rows_file, gate_rows_file = out / "rows.ndjson", out / "gate-rows.ndjson"
    row_lines = {r.index: row_line(r) for r in result["rows"]}
    gate_lines = {g.index: row_line(g) for g in gate["g4_confirmed_tier_overdue"]}
    new, changed = append_only(rows_file, row_lines, write=write)
    new_g, changed_g = append_only(gate_rows_file, gate_lines, write=write)
    if not write:
        print(
            f"check {entry['t_public']}: {len(row_lines)} rows ({len(new)} new, {len(changed)} "
            f"would change); {len(gate_lines)} Gate 2 rows ({len(new_g)} new, {len(changed_g)} "
            "would change)"
        )
        raise SystemExit(1 if changed or changed_g else 0)
    # C7 replaced: the cross-tab reads exactly the rows this census selected,
    # as committed for this copy.
    on_disk = [json.loads(x)["index"] for x in rows_file.read_text().splitlines() if x.strip()]
    checks["C5′ selected rows written append-only, no committed line changed"] = True
    checks["C7′ the cross-tab reads exactly the rows this census of the copy selected"] = (
        on_disk == [r.index for r in result["rows"]]
    )
    if not checks["C7′ the cross-tab reads exactly the rows this census of the copy selected"]:
        raise SystemExit("refusing: the committed rows are not this census's selection (C7′)")

    falsifiers = {
        **result["falsifiers"],
        "F2 the copy carries a flag or is a suspected partial export": False,
        **gate["falsifiers"],
        "F10 the filename reading moves more than a tenth of the selected MW": run["filename"][
            "F10 the filename reading moves more than a tenth of the selected MW"
        ],
    }
    fired = [name for name, hit in falsifiers.items() if hit]
    computed_at = datetime.now(UTC).isoformat(timespec="seconds")
    status_counts = dict(sorted(copy["project_status"].items(), key=lambda kv: (-kv[1], kv[0])))
    provenance = {
        "investigation": "017",
        "version": 3,
        "declaration": DECLARATION_V3.name,
        "declaration_sha256": sealed,
        "declaration_timestamps": timestamps(DECLARATION_V3),
        "capture_schema_report_sha256": file_sha256(CAPTURE_REPORT),
        "seal": seal,
        "run_date": run_date,
        "computed_at": computed_at,
        "which": which,
        "selection": selection,
        "copy": {
            "t_public": entry["t_public"],
            "t_public_basis": entry["t_public_basis"],
            "filename": entry["filename"],
            "sha256": entry["sha256"],
            "bytes": entry["bytes"],
            "key": entry["key"],
            "fetched_at": entry["fetched_at"],
            "manifest": entry["manifest"],
            "manifest_sha256": file_sha256(MANIFESTS / entry["manifest"]),
        },
    }
    census_summary = {
        **provenance,
        "n0": n0,
        "status_counts_all_rows": status_counts,
        "rows_file": rows_file.name,
        "rows_appended": len(new),
        **{k: v for k, v in result.items() if k not in ("rows", "checks", "falsifiers")},
        "filename_sensitivity": run["filename"],
        "checks": checks,
        "falsifiers": falsifiers,
        "falsifiers_fired": fired,
    }
    gate_summary = {
        **provenance,
        "gate_definition": GATE_DEFINITION,
        "rows_total": len(run["rows"]),
        "g6_gated_copies_read": run["gated"],
        "gate_rows_file": gate_rows_file.name,
        "gate_rows_appended": len(new_g),
        **{k: v for k, v in gate.items() if k != "falsifiers"},
        "falsifiers": gate["falsifiers"],
    }
    write_json(out / "census.json", census_summary)
    write_json(out / "gate.json", gate_summary)
    log_path = V3 / "run-log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else []
    log.append(
        {
            "run_date": run_date,
            "computed_at": computed_at,
            "seal": seal,
            "which": which,
            "copy": entry["t_public"],
            "sha256": entry["sha256"],
            "selected_rows": result["selected_rows"],
            "rows_appended": len(new),
            "gate_rows_appended": len(new_g),
            "falsifiers_fired": fired,
        }
    )
    write_json(log_path, log)
    print(
        f"{which} census of {entry['t_public']} ({entry['sha256'][:16]}…): "
        f"{result['selected_rows']} rows, {result['selected_mw']} MW; "
        f"{result['distinct_project_ids']} ids, {result['selected_mw_largest_per_id']} MW; "
        f"Gate 2 overdue {gate['confirmed_tier_overdue_rows']} rows / "
        f"{gate['confirmed_tier_overdue_mw']} MW"
    )
    print(f"checks: all {len(checks)} pass; falsifiers fired: {fired or 'none'}")


def compare_v3(seal: str, run_date: str, *, write: bool) -> None:
    """D1 and D2, only once both censuses are committed."""
    sealed = require_seal(seal, DECLARATION_V3)
    ref_entry, _ = which_copy("reference")
    next_entry, _ = which_copy("next")
    for t in (ref_entry["t_public"], next_entry["t_public"]):
        for name in ("census.json", "rows.ndjson", "gate.json"):
            if not committed(V3 / t / name):
                raise SystemExit(f"refusing: commit evidence/v3/{t}/{name} before comparing")
    ref, nxt = census_of(ref_entry), census_of(next_entry)
    for run, entry in ((ref, ref_entry), (nxt, next_entry)):
        on_disk = [
            line
            for line in (V3 / entry["t_public"] / "rows.ndjson").read_text().splitlines()
            if line.strip()
        ]
        if on_disk != [row_line(r) for r in run["result"]["rows"]]:
            raise SystemExit(f"refusing: {entry['t_public']}'s committed rows do not recompute")
    d1 = oq.side_by_side((ref["result"], ref["gate"]), (nxt["result"], nxt["gate"]))
    d2 = oq.transitions(ref["rows"], ref["result"], nxt["rows"], nxt["result"])
    if not all(d2["checks"].values()):
        raise SystemExit("refusing: C11 fails; D2's classes do not sum to the censuses")
    f9 = d2["falsifiers"][
        "F9 more than a tenth of either copy's selected rows are ambiguous or have no id"
    ]
    record = {
        "investigation": "017",
        "version": 3,
        "declaration": DECLARATION_V3.name,
        "declaration_sha256": sealed,
        "seal": seal,
        "run_date": run_date,
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "reference": {
            "t_public": ref_entry["t_public"],
            "sha256": ref_entry["sha256"],
            "census_json_sha256": file_sha256(V3 / ref_entry["t_public"] / "census.json"),
        },
        "next": {
            "t_public": next_entry["t_public"],
            "sha256": next_entry["sha256"],
            "census_json_sha256": file_sha256(V3 / next_entry["t_public"] / "census.json"),
        },
        "d1": d1,
        "d2_published": not f9,
        "d2": d2,
        "checks": d2["checks"],
        "falsifiers": d2["falsifiers"],
    }
    if not write:
        print(dumps(plain(record)["d1"]))
        return
    write_json(COMPARISON, record)
    print(f"wrote {COMPARISON.relative_to(REPO_ROOT)}")
    for klass, entry in d2["classes"].items():
        print(f"  {klass}: {entry['rows']} rows, {entry['mw_reference']} / {entry['mw_next']} MW")
    verdict = "FIRED" if f9 else "not fired"
    print(f"  ambiguous keys: {len(d2['ambiguous']['keys'])}; C11 pass; F9 {verdict}")


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
    corrections = json.loads(CORRECTIONS.read_text()) if CORRECTIONS.exists() else None
    findings = page.render_findings(census, rows, certificates(), gate, corrections)
    FINDINGS.write_text(findings)
    print(f"rendered {FINDINGS.relative_to(REPO_ROOT)}")
    if gate is None:
        return
    from grid_mysteries.rendering import connection_slippage as site

    PAGE.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(
        page.render_page(
            findings,
            census,
            gate,
            next_declaration=(
                (DECLARATION_V3.name, digest(DECLARATION_V3)) if DECLARATION_V3.exists() else None
            ),
            repo_url=site.REPO_URL,
            credibility=site.CREDIBILITY,
            contact_email=site.CALL_TO_ACTION_EMAIL,
        )
    )
    print(f"rendered {PAGE.relative_to(REPO_ROOT)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seal", help="prefix of the declaration's SHA-256")
    parser.add_argument(
        "--phase",
        choices=("compute", "check", "render", "all", "method-check", "n0", "compare"),
        default="render",
    )
    parser.add_argument(
        "--version",
        type=int,
        choices=(1, 2, 3),
        default=1,
        help=(
            "1 is the census (DECLARATION.md); 2 is the Gate cross-tab (DECLARATION-v2.md); "
            "3 is the two later copies and their comparison (DECLARATION-v3.md)"
        ),
    )
    parser.add_argument(
        "--copy", choices=("reference", "next"), help="version 3: which copy to census"
    )
    parser.add_argument("--run-date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    if args.version == 3:
        if args.phase == "method-check":
            require_seal(args.seal, DECLARATION_V3)
            raise SystemExit(0 if method_check(write=True) else 1)
        if args.phase == "n0":
            n0_verdict(args.seal)
            return
        if args.phase == "compare":
            compare_v3(args.seal, args.run_date, write=True)
            return
        if args.phase in ("compute", "check"):
            if not args.copy:
                raise SystemExit("--copy reference|next is required")
            compute_v3(args.seal, args.run_date, args.copy, write=args.phase == "compute")
            return
    run_one = compute if args.version == 1 else compute_gate
    if args.phase in ("method-check", "n0", "compare"):
        raise SystemExit(f"--phase {args.phase} belongs to --version 3")
    if args.phase == "check":
        run_one(args.seal, args.run_date, write=False)
        return
    if args.phase in ("compute", "all"):
        run_one(args.seal, args.run_date, write=True)
    if args.phase in ("render", "all"):
        render()


if __name__ == "__main__":
    sys.exit(main())
