"""021 — 014's slippage series by plant type and by host TO: gated,
append-only runner under the frozen declaration (SHA-256 76ad7dc3…).

    uv run --group registers python investigations/021-slippage-by-technology-and-area/run.py \\
        --seal 76ad7dc3 --phase check
    uv run --group registers python investigations/021-slippage-by-technology-and-area/run.py \\
        --seal 76ad7dc3 --phase compute [--run-date YYYY-MM-DD]
    uv run python investigations/021-slippage-by-technology-and-area/run.py --phase render

Phases:

- ``check`` (needs the seal): C1 to C5, the whole computation, and a
  comparison with the committed rows; writes nothing.
- ``compute`` (needs the seal): the same, then appends to
  ``evidence/comparisons.ndjson`` and ``evidence/groups.ndjson`` (a
  committed line must be byte-identical to its recomputation or the run
  refuses, F-G3; there is no --amend) and rewrites ``summary.json``.
- ``render``: ``FINDINGS.md`` as a pure function of the evidence.

Nothing is fetched: the population is 014 version 4's, checked digest by
digest (C1).
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import connection_slippage_v3 as v3
from grid_mysteries.investigations import slippage_by_group as sbg
from grid_mysteries.rendering import slippage_by_group as page
from grid_mysteries.sources import tec_register as tr
from grid_mysteries.tec import analysis
from grid_mysteries.tec import identity as content_rule

HERE = Path(__file__).parent
DECLARATION = HERE / "DECLARATION.md"
EVIDENCE = HERE / "evidence"
COMPARISONS = EVIDENCE / "comparisons.ndjson"
GROUPS = EVIDENCE / "groups.ndjson"
SUMMARY = EVIDENCE / "summary.json"
RUN_LOG = EVIDENCE / "run-log.json"
FINDINGS = HERE / "FINDINGS.md"
V4 = REPO_ROOT / "investigations" / "014-gb-connection-slippage"
V4_ROWS = V4 / "evidence" / "v4" / "rows.ndjson"
V4_SERIES = V4 / "evidence" / "v4" / "series.json"
V4_MANIFEST = V4 / "evidence" / "v4" / "vintage-manifest.json"
JOURNAL = REPO_ROOT / tr.JOURNAL_PATH
SCHEMA_REPORT = REPO_ROOT / "archives" / "tec-register" / "schema-report.json"
#: 014's reading rule 2: a copy lacking any of these is excluded there too.
REQUIRED_COLUMNS = (
    "Project Name",
    "Customer Name",
    "Connection Site",
    "MW Increase / Decrease",
    "MW Effective From",
)
MIN_SEAL_LENGTH = 8
DIMENSIONS = tuple(name for name, _ in sbg.GROUPING)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def declared(pattern: str, text: str) -> str:
    found = re.search(pattern, text)
    if not found:
        raise SystemExit(f"refusing: the declaration does not state {pattern!r}")
    return found[1]


def require_seal(seal: str | None) -> str:
    digest = sha(DECLARATION)
    if not seal or len(seal) < MIN_SEAL_LENGTH or not digest.startswith(seal.lower()):
        raise SystemExit(
            f"refusing: --seal must be a prefix (>= {MIN_SEAL_LENGTH} hex) of "
            f"DECLARATION.md's SHA-256 {digest[:16]}…"
        )
    return digest


def timestamps() -> dict[str, Any] | None:
    sidecar = DECLARATION.with_name(DECLARATION.name + ".timestamps.json")
    if not sidecar.exists():
        return None
    stamps = json.loads(sidecar.read_text())
    return {
        "sha256": stamps["sha256"],
        "matches_declaration": stamps["sha256"] == sha(DECLARATION),
        "proofs": [
            {k: v for k, v in p.items() if k in ("kind", "tsa", "path", "tsa_time", "status")}
            for p in stamps["proofs"]
        ],
    }


# ------------------------------------------------------------- the inputs


def usable_vintages(
    parsed: list[tuple[date, list[dict[str, object]], dict]],
) -> list[cs.VintageInput]:
    out = []
    for t, rows, entry in parsed:
        columns = {tr.canon(c) for c in (entry.get("columns") or [])}
        if any(c not in columns for c in REQUIRED_COLUMNS):
            continue
        out.append(
            cs.VintageInput(
                t_public=t, rows=tuple(rows), sha256=entry["sha256"], path=entry["path"]
            )
        )
    return out


def check_inputs(text: str) -> dict[str, str]:
    """C1 (digests) and C5, before anything is parsed."""
    schema = declared(r"schema-report\.json`, SHA-256\s+`([0-9a-f]{64})`", text)
    if sha(SCHEMA_REPORT) != schema:
        raise SystemExit(
            f"refusing (C1): the schema report hashes to {sha(SCHEMA_REPORT)[:16]}…, "
            f"not {schema[:16]}…"
        )
    manifest_prefix = declared(r"`vintage-manifest\.json` `([0-9a-f]{8})…`", text)
    if not sha(V4_MANIFEST).startswith(manifest_prefix):
        raise SystemExit("refusing (C1): 014 version 4's manifest is not the one declared")
    try:
        v3.check_rule_file(v3.CONTENT_RULE_FILE, v3.declared_rule_digest(text))
    except v3.ContentRuleChanged as exc:
        raise SystemExit(f"refusing (C5): {exc}") from None
    return {
        "schema_report_sha256": schema,
        "v4_manifest_sha256": sha(V4_MANIFEST),
        "content_rule_sha256": v3.declared_rule_digest(text),
    }


def v4_reference() -> dict[tuple[str, str, str], dict[str, Any]]:
    """014 version 4's committed figures per comparison, keyed by
    (regime, baseline, current), for C2."""
    out: dict[tuple[str, str, str], dict[str, Any]] = {}

    def entry(pair: dict[str, Any], split: dict[str, Any]) -> dict[str, Any]:
        return {
            "mw_years_net": pair["mw_years_net"],
            "mw_years_later": pair["mw_years_later"],
            "mw_years_earlier": pair["mw_years_earlier"],
            "dated_both": pair["dated_both"],
            "weighted_mw": pair["weighted_mw"],
            "determined": split["determined"],
            "undetermined_groups": split["undetermined_groups"],
            "total": split["total"],
        }

    for line in V4_ROWS.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["vs_previous"]:
            out[(row["regime"], row["vs_previous"]["baseline"], row["t_public"])] = entry(
                row["vs_previous"], row["split"]["vs_previous"]
            )
        if row["vs_year_earlier"]:
            out[(row["regime"], row["year_earlier_baseline"], row["t_public"])] = entry(
                row["vs_year_earlier"], row["split"]["vs_year_earlier"]
            )
    series = json.loads(V4_SERIES.read_text())
    for segment in series["segments"]:
        for window in segment["annual"]:
            out[(segment["regime"], window["baseline"], window["current"])] = entry(
                window, window["split"]
            )
    return out


# ----------------------------------------------------------------- compute


def comparisons_of(result: dict[str, Any]) -> list[dict[str, Any]]:
    """R4: the headline, the complete old-regime calendar years, the
    reformed regime copy to copy."""
    out = []
    old = next((s for s in result["segments"] if s["regime"] == "old"), None)
    if old:
        with_year = [r for r in old["rows"] if r["vs_year_earlier"] is not None]
        if with_year:
            last = with_year[-1]
            out.append(
                {
                    "regime": "old",
                    "window": "headline",
                    "baseline": last["year_earlier_baseline"],
                    "current": last["t_public"],
                }
            )
        for w in old["annual"]:
            if not w["partial"]:
                out.append(
                    {
                        "regime": "old",
                        "window": str(w["year"]),
                        "baseline": w["baseline"],
                        "current": w["current"],
                    }
                )
    new = next((s for s in result["segments"] if s["regime"] == "new"), None)
    if new:
        for r in new["rows"]:
            if r["vs_previous"] is not None:
                out.append(
                    {
                        "regime": "new",
                        "window": "copy-to-copy",
                        "baseline": r["vs_previous"]["baseline"],
                        "current": r["t_public"],
                    }
                )
    return out


def row_line(row: dict[str, Any]) -> str:
    return json.dumps(json.loads(dumps(row)), separators=(",", ":"))


def committed(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                out[json.loads(line)["key"]] = line
    return out


def compute(run_date: str, seal: str, *, write: bool) -> None:
    digest = require_seal(seal)
    rule_version = digest[:8]
    text = DECLARATION.read_text()
    digests = check_inputs(text)
    parsed, skipped = tr.load_vintages(JOURNAL, REPO_ROOT)
    usable = usable_vintages(parsed)
    manifest = json.loads(V4_MANIFEST.read_text())
    ours = [(v.t_public.isoformat(), v.sha256) for v in usable]
    theirs = [(m["t_public"], m["sha256"]) for m in manifest]
    if ours != theirs:
        raise SystemExit(
            f"refusing (C1, F-G1): {len(ours)} usable copies here against {len(theirs)} in "
            "014 version 4's manifest, or digests differ"
        )
    print(
        f"C1: {len(usable)} usable copies, every digest as 014 version 4's manifest; "
        f"schema report {digests['schema_report_sha256'][:16]}…; "
        f"C5: content rule {digests['content_rule_sha256'][:16]}…"
    )

    result = cs.series(usable, partial_export_rule=True)
    kept = analysis.kept(usable, result)
    v2_entries: dict[tuple[str, date], sbg.Entries] = {}
    v2_keys: dict[tuple[str, date], sbg.Keys] = {}
    c_entries: dict[tuple[str, date], sbg.Entries] = {}
    c_keys: dict[tuple[str, date], sbg.Keys] = {}
    carriers: dict[str, content_rule.ContentIdentity] = {}
    rows_of: dict[tuple[str, date], list[dict[str, object]]] = {}
    for k in kept:
        at = (k.regime, k.vintage.t_public)
        rows = list(k.vintage.rows)
        rows_of[at] = rows
        v2_entries[at] = cs.entries(rows, swapped=k.swapped)
        v2_keys[at] = sbg.keys_from_rows(rows)
        carrier = carriers.setdefault(k.regime, content_rule.ContentIdentity())
        c_entries[at] = carrier.step(rows, swapped=k.swapped)
        c_keys[at] = sbg.keys_from_units(carrier.units)
    position: dict[tuple[str, date], int] = {}
    determinacy: dict[str, v3.Determinacy] = {}
    for regime in dict.fromkeys(k.regime for k in kept):
        copies = [k for k in kept if k.regime == regime]
        position.update({(regime, k.vintage.t_public): n for n, k in enumerate(copies)})
        determinacy[regime] = v3.Determinacy([list(k.vintage.rows) for k in copies])

    reference = v4_reference()
    comparison_lines: dict[str, str] = {}
    group_lines: dict[str, str] = {}
    cuts: list[dict[str, Any]] = []
    for c in comparisons_of(result):
        regime, b, cur = c["regime"], c["baseline"], c["current"]
        ref = reference.get((regime, b.isoformat(), cur.isoformat()))
        if ref is None:
            raise SystemExit(
                f"refusing (C2, F-G1): 014 version 4 holds no figure for {regime} {b} -> {cur}"
            )
        undetermined = determinacy[regime].undetermined(
            position[(regime, b)], position[(regime, cur)]
        )
        try:
            split = v3.split(
                (v2_entries[(regime, b)], v2_entries[(regime, cur)]),
                (c_entries[(regime, b)], c_entries[(regime, cur)]),
                undetermined,
                baseline=b,
                current=cur,
            )
        except v3.RuleDisagreement as exc:
            raise SystemExit(f"refusing: {exc}") from None
        pair = cs.compare(
            v2_entries[(regime, b)], v2_entries[(regime, cur)], baseline_date=b, current_date=cur
        )
        recomputed = {
            "mw_years_net": str(pair.mw_years_net),
            "mw_years_later": str(pair.mw_years_later),
            "mw_years_earlier": str(pair.mw_years_earlier),
            "dated_both": pair.dated_both,
            "weighted_mw": str(pair.weighted_mw),
            "determined": str(split["determined"]),
            "undetermined_groups": split["undetermined_groups"],
            "total": {r: str(v) for r, v in split["total"].items()},
        }
        if recomputed != ref:
            raise SystemExit(
                f"refusing (C2, F-G1): {regime} {b} -> {cur} recomputes {recomputed}, "
                f"014 version 4 holds {ref}"
            )
        figures = {
            "mw_years_net": Decimal(ref["mw_years_net"]),
            "determined": Decimal(ref["determined"]),
            "weighted_mw": Decimal(ref["weighted_mw"]),
        }
        for dimension in DIMENSIONS:
            try:
                one = sbg.cut(
                    dimension=dimension,
                    v2=(v2_entries[(regime, b)], v2_entries[(regime, cur)]),
                    content=(c_entries[(regime, b)], c_entries[(regime, cur)]),
                    keys_v2=(v2_keys[(regime, b)], v2_keys[(regime, cur)]),
                    keys_content=(c_keys[(regime, b)], c_keys[(regime, cur)]),
                    undetermined=undetermined,
                    comparison=figures,
                )
            except sbg.RuleDisagreement as exc:
                raise SystemExit(f"refusing: {regime} {b} -> {cur} by {dimension}: {exc}") from None
            sums = one["sums"]
            if (
                sums["dated_both"] != pair.dated_both
                or sums["capacity_baseline_mw"] != pair.weighted_mw
                or not sums["within_rounding"]
            ):
                raise SystemExit(
                    f"refusing (C4): {regime} {b} -> {cur} by {dimension}: {sums} against "
                    f"dated {pair.dated_both}, weighted {pair.weighted_mw}"
                )
            key = f"{rule_version}|{regime}|{c['window']}|{b}|{cur}|{dimension}"
            head = {
                "key": key,
                "rule_version": rule_version,
                "regime": regime,
                "window": c["window"],
                "baseline": b,
                "current": cur,
                "dimension": dimension,
            }
            comparison_lines[key] = row_line(
                {
                    **head,
                    "figures_014_v4": ref,
                    **{k: v for k, v in one.items() if k not in ("groups", "dimension")},
                }
            )
            for g in one["groups"]:
                group_lines[f"{key}|{g['group']}"] = row_line(
                    {**head, "key": f"{key}|{g['group']}", **g}
                )
            cuts.append({**head, **{k: v for k, v in one.items() if k != "dimension"}})
    changed = sbg.require_unchanged(
        committed(COMPARISONS), comparison_lines
    ) + sbg.require_unchanged(committed(GROUPS), group_lines)
    new_c = [k for k in comparison_lines if k not in committed(COMPARISONS)]
    new_g = [k for k in group_lines if k not in committed(GROUPS)]
    if changed:
        raise SystemExit(
            f"refusing (F-G3): {len(changed)} committed row(s) would change under rule "
            f"version {rule_version} ({changed[:3]}…); a changed figure is a new declaration"
        )
    headline_host = next(
        x for x in cuts if x["window"] == "headline" and x["dimension"] == "host_to"
    )
    headline_plant = next(
        x for x in cuts if x["window"] == "headline" and x["dimension"] == "plant_type"
    )
    props = sbg.propositions(headline_host, headline_plant)
    print(
        f"comparisons: {len(cuts)} cut lines ({len(new_c)} new), {len(group_lines)} group "
        f"lines ({len(new_g)} new); unfit: {[x['key'] for x in cuts if x['unfit']]}; "
        f"not read: {[x['key'] for x in cuts if x['not_read']]}"
    )
    for name, p in props.items():
        print(f"{name}: {p['verdict']}")
    if not write:
        print("check: nothing written")
        return
    computed_at = datetime.now(UTC).isoformat(timespec="seconds")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with COMPARISONS.open("a") as out:
        for k in new_c:
            out.write(comparison_lines[k] + "\n")
    with GROUPS.open("a") as out:
        for k in new_g:
            out.write(group_lines[k] + "\n")
    summary = {
        "investigation": "021",
        "declaration": DECLARATION.name,
        "declaration_sha256": digest,
        "declaration_timestamps": timestamps(),
        "rule_version": rule_version,
        "seal": seal,
        "run_date": run_date,
        "computed_at": computed_at,
        **digests,
        "copies": {
            "usable": len(usable),
            "unparseable": len(skipped),
            "first": usable[0].t_public,
            "last": usable[-1].t_public,
        },
        "comparisons": [{k: v for k, v in x.items() if k not in ("groups", "sums")} for x in cuts],
        "propositions": props,
        "thin_groups": {x["key"]: x["thin_groups"] for x in cuts if x["thin_groups"]},
        "unfit": [x["key"] for x in cuts if x["unfit"]],
        "not_read": [x["key"] for x in cuts if x["not_read"]],
        "rows": {
            "comparisons_appended": len(new_c),
            "groups_appended": len(new_g),
            "comparisons_total": len(comparison_lines),
            "groups_total": len(group_lines),
        },
    }
    write_json(SUMMARY, summary)
    log = json.loads(RUN_LOG.read_text()) if RUN_LOG.exists() else []
    log.append(
        {
            "run_date": run_date,
            "computed_at": computed_at,
            "seal": seal,
            "declaration_sha256": digest,
            "rule_version": rule_version,
            "comparisons_appended": len(new_c),
            "groups_appended": len(new_g),
        }
    )
    write_json(RUN_LOG, log)
    print(f"written: {COMPARISONS.name}, {GROUPS.name}, {SUMMARY.name}, {RUN_LOG.name}")


# ------------------------------------------------------------------ render


def load_evidence() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    summary = json.loads(SUMMARY.read_text())
    comparisons = [
        json.loads(line) for line in COMPARISONS.read_text().splitlines() if line.strip()
    ]
    groups = [json.loads(line) for line in GROUPS.read_text().splitlines() if line.strip()]
    return summary, comparisons, groups


def render() -> None:
    FINDINGS.write_text(page.render_findings(*load_evidence()))
    print(f"rendered {FINDINGS.relative_to(REPO_ROOT)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seal", help="prefix of the declaration's SHA-256 (check, compute)")
    parser.add_argument("--phase", choices=("check", "compute", "render"), default="render")
    parser.add_argument("--run-date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    if args.phase == "check":
        compute(args.run_date, args.seal, write=False)
    elif args.phase == "compute":
        compute(args.run_date, args.seal, write=True)
    else:
        render()


if __name__ == "__main__":
    sys.exit(main())
