# ruff: noqa: E501
"""023 — Did projects that changed hands slip more? Gated runner.

    uv run --group registers python investigations/023-did-changing-hands-slip-more/run.py --phase schema

- ``schema`` (archive only, no network, before any declaration): for each
  candidate window the copies at its two ends as 014 v4 keeps them
  (partial-export rule, swap-test flag), their columns' blank counts, the
  duplicate (Project ID, Stage) keys, the Project IDs printed at both ends
  and how many of them 019's sealed holder history covers and classifies;
  the count of 019's classified name changes bracketed inside each window,
  by class. **No date movement is read**: the effective dates are counted
  as parsed or not, never differenced. Writes
  ``archives/023-holder-change-inputs/`` (SCHEMA.md, schema-report.json).
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import holder_change as hc
from grid_mysteries.investigations import queue_ownership as qo
from grid_mysteries.investigations.overdue_queue import project_id
from grid_mysteries.sources.tec_register import normalise_stage, parse_date
from grid_mysteries.tec import analysis
from grid_mysteries.tec import sources as tec_sources

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
RUN_LOG = EVIDENCE / "run-log.json"
ARCHIVE = REPO_ROOT / "archives" / "023-holder-change-inputs"
Q019 = REPO_ROOT / "investigations" / "019-who-holds-the-queue" / "evidence"
RUN_019 = "2026-09-30"
RAW_019 = REPO_ROOT / "data/raw/companies-house" / f"{RUN_019}-019"
#: 014 v4's headline trailing-year window, then its three calendar-year
#: windows of the Project ID era (Project ID is printed from 26/11/2021).
WINDOWS = (
    ("headline", date(2024, 7, 19), date(2025, 7, 22)),
    ("2022", date(2022, 1, 5), date(2023, 1, 6)),
    ("2023", date(2023, 1, 6), date(2024, 1, 5)),
    ("2024", date(2024, 1, 5), date(2025, 1, 3)),
)
COLUMNS = (
    "Project ID",
    "Stage",
    "Customer Name",
    "Project Status",
    "Plant Type",
    "MW Increase / Decrease",
    "MW Effective From",
)


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


def load_copies() -> list[cs.VintageInput]:
    """Every copy the repository holds, verified against its digest, with
    014's required columns (as 020's runner loads them)."""
    usable = []
    for copy in tec_sources.copies(REPO_ROOT):
        try:
            tec_sources.verify(copy)
            rows = tec_sources.read(copy)
        except Exception:  # noqa: BLE001 - unreadable copies take no part, as in 014
            continue
        if not rows or any(c not in rows[0] for c in analysis.REQUIRED_COLUMNS):
            continue
        usable.append(
            cs.VintageInput(
                copy.published_on, tuple(rows), copy.sha256, str(copy.path.relative_to(REPO_ROOT))
            )
        )
    return usable


def kept_copies() -> dict[date, analysis.Kept]:
    usable = load_copies()
    result = cs.series(usable, partial_export_rule=True)
    return {k.vintage.t_public: k for k in analysis.kept(usable, result)}


def load_019() -> tuple[dict[str, qo.Link], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """019's links under its latest rule version for its run, its
    admissions and the pinned profiles of every company they name: what
    019's compute reads, read the same way."""
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
    links = {n: qo.apply_admissions(lk, admitted) for n, lk in links.items()}
    numbers = {lk.company_number for lk in links.values() if lk.resolved and lk.company_number}
    for a in admitted.values():
        if a.get("company_number"):
            numbers.add(str(a["company_number"]))
        numbers |= {str(h["company_number"]) for h in a.get("holders") or []}
    profiles = {}
    for n in numbers:
        path = RAW_019 / "company" / str(n) / "profile.json"
        if path.exists():
            profiles[str(n)] = json.loads(path.read_text())
    return links, admitted, profiles


def names_by_id(k: analysis.Kept) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for r in k.vintage.rows:
        if pid := project_id(r):
            out.setdefault(pid, set()).add(qo.printed_name(r))
    return out


def end_facts(k: analysis.Kept) -> dict[str, Any]:
    rows = list(k.vintage.rows)
    blank = {c: sum(1 for r in rows if not str(r.get(c) or "").strip()) for c in COLUMNS}
    keys = Counter((project_id(r), normalise_stage(r.get("Stage"))) for r in rows if project_id(r))
    return {
        "t_public": k.vintage.t_public.isoformat(),
        "sha256": k.vintage.sha256,
        "regime": k.regime,
        "swap_flagged": k.swapped,
        "rows": len(rows),
        "columns_missing": [c for c in COLUMNS if c not in rows[0]],
        "blank": blank,
        "effective_unparsed_nonblank": sum(
            1
            for r in rows
            if str(r.get("MW Effective From") or "").strip()
            and parse_date(r.get("MW Effective From")) is None
        ),
        "project_ids": len({project_id(r) for r in rows if project_id(r)}),
        "duplicate_id_stage_keys": sum(1 for n in keys.values() if n > 1),
        "rows_in_duplicate_keys": sum(n for n in keys.values() if n > 1),
        "statuses": dict(Counter(str(r.get("Project Status") or "") for r in rows)),
    }


def phase_schema() -> None:
    kept = kept_copies()
    links, admitted, profiles = load_019()
    history_doc = json.loads((Q019 / "name-history.json").read_text())
    history = history_doc["history"]
    names = json.loads((Q019 / "names.json").read_text())
    current = {pid for v in names["names"].values() for pid in v["project_ids"]}
    results_path = Q019 / "results.json"
    results = json.loads(results_path.read_text())
    events = results["figure3_name_changes"]["all"]
    windows = []
    for label, b, c in WINDOWS:
        if b not in kept or c not in kept:
            windows.append(
                {
                    "window": label,
                    "baseline": b.isoformat(),
                    "current": c.isoformat(),
                    "kept": False,
                }
            )
            continue
        ids_b = {project_id(r) for r in kept[b].vintage.rows if project_id(r)}
        ids_c = {project_id(r) for r in kept[c].vintage.rows if project_id(r)}
        both = ids_b & ids_c
        classes = {
            (e["project_id"], e["earlier"], e["later"], e["first_copy_with_later"]): e["class"]
            for e in events
        }
        inside = [
            (pid, change)
            for pid in sorted(both)
            for change in hc.boundaries(history.get(pid, []), b, c)
        ]
        nb, nc = names_by_id(kept[b]), names_by_id(kept[c])
        ends = {
            pid: hc.ends_class(pid, nb[pid], nc[pid], b, c, links, admitted, profiles)["class"]
            for pid in both
        }
        changed_inside = {pid for pid, _ in inside}
        by_class = Counter(classes.get((pid, *ch), "not-in-019-scope") for pid, ch in inside)
        windows.append(
            {
                "window": label,
                "baseline": end_facts(kept[b]),
                "current": end_facts(kept[c]),
                "ids_at_both_ends": len(both),
                "ids_in_019_history": len(both & set(history)),
                "ids_current_on_2026_09_29": len(both & current),
                "name_changes_inside_window": len(inside),
                "name_changes_inside_by_019_class": dict(by_class),
                "ids_with_a_change_inside": len({pid for pid, _ in inside}),
                "ends_class": dict(Counter(ends.values())),
                "ends_class_current_ids": dict(
                    Counter(v for pid, v in ends.items() if pid in current)
                ),
                "same_name_at_ends_but_changed_inside": sum(
                    1 for pid, v in ends.items() if v == hc.SAME_NAME and pid in changed_inside
                ),
                "ids_with_a_transfer_inside": len(
                    {pid for pid, ch in inside if classes.get((pid, *ch)) == "transfer"}
                ),
            }
        )
    report = {
        "archive": "023-holder-change-inputs",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "inputs": {
            "019_name_history_sha256": sha(Q019 / "name-history.json"),
            "019_names_sha256": sha(Q019 / "names.json"),
            "019_results_sha256": sha(results_path),
            "019_rule_version": results["rule_version"],
            "019_declaration_sha256": results["declaration_sha256"],
            "019_amendment_2_sha256": results["amendment_2_sha256"],
            "019_history_project_ids": len(history),
            "019_history_first_copy": history_doc.get("copies_with_project_id"),
            "019_links_rule_version": qo.RULE_VERSION_V2,
            "019_links_loaded": len(links),
            "019_admissions": len(admitted),
            "019_profiles_pinned": len(profiles),
            "019_current_project_ids": len(current),
            "019_events_classified": len(events),
            "019_events_scope": "current project ids (printed in the 29/09/2026 copy) only",
            "019_field_note": "019's `last_copy_with_earlier` is the first copy of the earlier name's run (name_changes reads the run's t_public); brackets here are rebuilt from the history's runs",
            "project_id_scheme_change": "ids beginning a03 printed 2021-11-26 to 2022-08-24, a0l from 2022-08-24: no id spans the change",
        },
        "kept_copies": len(kept),
        "first_kept_with_project_id": min(
            (t for t, k in kept.items() if any(project_id(r) for r in k.vintage.rows)), default=None
        ),
        "windows": windows,
    }
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    write_json(ARCHIVE / "schema-report.json", report)
    L = [
        "# Schema report: 023-holder-change-inputs",
        "",
        f"Regenerated by `investigations/023-did-changing-hands-slip-more/run.py --phase schema` on {report['generated_at'][:10]}; "
        "`schema-report.json` beside this file has every field. No date movement is read and no figure of the investigation is computed here.",
        "",
        "## Inputs",
        "",
        "| key | value |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in report["inputs"].items()],
        f"| kept copies (014 v4's reading) | {report['kept_copies']} |",
        f"| first kept copy printing a Project ID | {report['first_kept_with_project_id']} |",
        "",
        "## Windows",
    ]
    for w in windows:
        L += ["", f"### {w['window']}", ""]
        if w.get("kept") is False:
            L.append(f"An end copy is not kept ({w['baseline']} or {w['current']}).")
            continue
        for end in ("baseline", "current"):
            f = w[end]
            L.append(
                f"- **{end}** {f['t_public']} (`{f['sha256'][:12]}…`, {f['regime']}, swap flagged {f['swap_flagged']}): "
                f"{f['rows']} rows, {f['project_ids']} Project IDs, columns missing {f['columns_missing'] or 'none'}; "
                f"blank {f['blank']}; effective dates printed but unparsed {f['effective_unparsed_nonblank']}; "
                f"duplicate (Project ID, Stage) keys {f['duplicate_id_stage_keys']} covering {f['rows_in_duplicate_keys']} rows"
            )
        L.append(
            f"- Project IDs at both ends {w['ids_at_both_ends']}; in 019's history {w['ids_in_019_history']}; "
            f"still printed on 29/09/2026 (019's classified scope) {w['ids_current_on_2026_09_29']}"
        )
        L.append(
            f"- name changes inside the window (019's history runs, classed by 019's figure 3): {w['name_changes_inside_window']} "
            f"({w['name_changes_inside_by_019_class']}) on {w['ids_with_a_change_inside']} Project IDs, "
            f"{w['ids_with_a_transfer_inside']} of them with a transfer"
        )
        L.append(
            f"- 019's R4 on the names printed at the two ends: {w['ends_class']}; among ids still printed on 29/09/2026: {w['ends_class_current_ids']}; "
            f"same name at both ends after a change inside: {w['same_name_at_ends_but_changed_inside']}"
        )
    (ARCHIVE / "SCHEMA.md").write_text("\n".join(L) + "\n")
    EVIDENCE.mkdir(exist_ok=True)
    log_run("schema", windows=len(windows))
    print("\n".join(L[-30:]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--phase", required=True, choices=["schema"])
    args = parser.parse_args()
    if args.phase == "schema":
        phase_schema()
    else:
        sys.exit(f"unknown phase {args.phase}")


if __name__ == "__main__":
    main()
