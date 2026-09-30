# ruff: noqa: E501
"""020 — Did it energise: gated runner under DECLARATION.md (fb8a3428…).

    uv run --group registers python investigations/020-did-it-energise/run.py --phase population --seal fb8a3428
    uv run --group registers python investigations/020-did-it-energise/run.py --phase schema --seal fb8a3428

- ``population`` (archive only): every copy of the register the repository
  holds (journal and daily capture, one per publication date, each verified
  against its recorded digest), 014's reading rules (required columns, the
  partial-export rule, the day-month swap test) through
  ``connection_slippage.series`` and ``tec.analysis.kept``, then 014's
  content identity stepped copy by copy; P1 (every unit's first ``Built``
  with the copy before it and the date it printed) and P2 (the Gate 2 rows
  of the 29/09/2026 copy) → ``evidence/population.ndjson`` (append-only),
  ``evidence/population-summary.json``, ``evidence/gate2.json``, and the
  register-only ``RESULTS-v0.md``.
- ``schema`` (network, under the seal): one sample of S1 (Elexon BM-unit
  reference), S2 (B1610, one settlement day, every unit), S3 (REMIT: the
  captured list and messages of 29/09/2026 from the mirror, plus one
  historical by-event listing) pinned under ``data/raw/elexon/020/`` and
  reported under ``archives/elexon-*-020/``; S4 (ENTSO-E) is recorded as
  not available (no token held). No figure is computed.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import energisation as en
from grid_mysteries.sources import elexon
from grid_mysteries.sources.pinning import fetch_journalled, progress
from grid_mysteries.tec import analysis
from grid_mysteries.tec import sources as tec_sources

HERE = Path(__file__).parent
DECLARATION = HERE / "DECLARATION.md"
EVIDENCE = HERE / "evidence"
POPULATION = EVIDENCE / "population.ndjson"
SUMMARY = EVIDENCE / "population-summary.json"
GATE2 = EVIDENCE / "gate2.json"
COPIES = EVIDENCE / "copies.json"
RUN_LOG = EVIDENCE / "run-log.json"
RESULTS_V0 = HERE / "RESULTS-v0.md"
COPY_SHA256 = "d1ccd9e210b4f6bc8f3b0e83d54032dc61f247dbbc1d9e469a342b7766ee5746"
SETTLEMENT_DAY = "2026-09-01"
REMIT_MIRROR_DAY = "2026-09-30"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_seal(seal: str | None) -> None:
    digest = sha(DECLARATION)
    if digest != en.DECLARATION_SHA256:
        sys.exit(
            f"DECLARATION.md hashes to {digest[:8]}, not the frozen {en.DECLARATION_SHA256[:8]}"
        )
    if not seal or not digest.startswith(seal):
        sys.exit("refusing: --seal must be a prefix of the frozen declaration's SHA-256")


def log_run(phase: str, **facts: Any) -> None:
    try:
        log = json.loads(RUN_LOG.read_text())
    except OSError, json.JSONDecodeError:
        log = {"runs": []}
    log["runs"].append(
        {"phase": phase, "at": datetime.now(UTC).isoformat(timespec="seconds"), **facts}
    )
    write_json(RUN_LOG, log)


# ------------------------------------------------------------- population


def load_copies() -> tuple[list[cs.VintageInput], list[dict[str, Any]], list[dict[str, Any]]]:
    usable, excluded, unreadable = [], [], []
    for copy in tec_sources.copies(REPO_ROOT):
        try:
            tec_sources.verify(copy)
            rows = tec_sources.read(copy)
        except Exception as error:  # noqa: BLE001 - recorded, never hidden
            unreadable.append(
                {"t_public": copy.published_on, "sha256": copy.sha256, "error": str(error)[:160]}
            )
            continue
        if not rows:
            unreadable.append(
                {
                    "t_public": copy.published_on,
                    "sha256": copy.sha256,
                    "error": "no header/rows parsed",
                }
            )
            continue
        columns = set(rows[0].keys())
        missing = [c for c in analysis.REQUIRED_COLUMNS if c not in columns]
        if missing:
            excluded.append(
                {"t_public": copy.published_on, "sha256": copy.sha256, "missing": missing}
            )
            continue
        usable.append(
            cs.VintageInput(
                copy.published_on, tuple(rows), copy.sha256, str(copy.path.relative_to(REPO_ROOT))
            )
        )
    return usable, excluded, unreadable


def phase_population(seal: str | None) -> None:
    require_seal(seal)
    usable, excluded, unreadable = load_copies()
    print(
        f"{len(usable)} usable copies, {len(excluded)} excluded (columns), {len(unreadable)} unreadable",
        flush=True,
    )
    result = cs.series(usable, partial_export_rule=True)
    kept = analysis.kept(usable, result)
    print(
        f"{len(kept)} kept copies after the partial-export rule; stepping the content identity",
        flush=True,
    )
    seen = en.sightings(
        [
            (k.regime, k.vintage.t_public, k.vintage.sha256, list(k.vintage.rows), k.swapped)
            for k in kept
        ]
    )
    found = en.transitions(seen)
    print(f"{len(found)} units with a first Built sighting", flush=True)

    # C2: append-only population lines; a line that would change stops the run.
    existing: dict[str, str] = {}
    if POPULATION.exists():
        for line in POPULATION.read_text().splitlines():
            if line.strip():
                existing[json.loads(line)["key"]] = line
    new_lines = []
    for t in found:
        record = {
            "key": f"{t.regime}|{t.unit}",
            **t.__dict__,
            "months_last_date_to_built_copy": t.months_from_last_date_to_built_copy,
        }
        line = dumps(record).replace("\n", "")
        if record["key"] in existing:
            if existing[record["key"]] != line:
                sys.exit(f"C2: population line for {record['key']} would change on recompute")
            continue
        new_lines.append(line)
    with POPULATION.open("a") as f:
        for line in new_lines:
            f.write(line + "\n")

    latest = next(v for v in usable if v.sha256 == COPY_SHA256)
    gate2 = en.gate_two_rows(list(latest.rows))
    write_json(
        GATE2,
        {
            "declaration_sha256": en.DECLARATION_SHA256,
            "copy_sha256": COPY_SHA256,
            "rows": len(gate2),
            "mw": sum((r["mw"] or Decimal(0)) for r in gate2),
            "items": gate2,
        },
    )
    write_json(
        COPIES,
        {
            "declaration_sha256": en.DECLARATION_SHA256,
            "usable": [
                {"t_public": v.t_public, "sha256": v.sha256, "rows": len(v.rows)} for v in usable
            ],
            "excluded_by_columns": excluded,
            "unreadable": unreadable,
            "kept": [
                {"regime": k.regime, "t_public": k.vintage.t_public, "swapped": k.swapped}
                for k in kept
            ],
            "suspect_copies": result["suspect_copies"],
            "segments": [
                {
                    "regime": s["regime"],
                    "first": s["first"],
                    "last": s["last"],
                    "vintages": s["vintages"],
                }
                for s in result["segments"]
            ],
        },
    )
    summary = en.summary(found)
    summary.update(
        {
            "declaration_sha256": en.DECLARATION_SHA256,
            "copies_usable": len(usable),
            "copies_kept": len(kept),
            "gate2_rows": len(gate2),
            "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "units_seen": sum(len(u) for u in seen.values()),
        }
    )
    write_json(SUMMARY, summary)
    RESULTS_V0.write_text(render_v0(summary, found))
    log_run(
        "population",
        usable=len(usable),
        kept=len(kept),
        transitions=len(found),
        new_lines=len(new_lines),
        gate2=len(gate2),
    )
    print(
        f"P1 {summary['by_class']}; measured {summary['measured']}; months median {summary['months_last_date_to_built_copy']['median']}; P2 {len(gate2)} rows"
    )


def render_v0(s: dict[str, Any], found: list[en.Transition]) -> str:
    q = s["months_last_date_to_built_copy"]
    L = [
        "# 020 — Did it energise: register-only first version (sponsor only)",
        "",
        f"Computed {s['computed_at']} under declaration `{en.DECLARATION_SHA256[:8]}…`. **This version reads the register alone.** "
        "No Elexon, REMIT or ENTSO-E source enters it; the realised delay of the declaration is not measured here. "
        "What is measured is the register's own account: for every unit that moves to `Built`, the date it printed in the copy "
        "before, and how many months later (or earlier) the first copy printing `Built` was published.",
        "",
        "## Population P1",
        "",
        f"{s['copies_usable']} usable copies, {s['copies_kept']} kept after 014's partial-export rule; {s['units_seen']} units under "
        f"`tec-identity-content-v1` across the regimes. Units with a first `Built` sighting: {s['transitions']} "
        f"({s['by_class']}). By regime and class: {s['by_regime_and_class']}.",
        "",
        f"Measured transitions (a `Built` sighting with a prior sighting that printed a date): {s['measured']}, {s['measured_mw']} MW. "
        f"Transitions whose prior sighting printed no date: {s['undated_before_built']}.",
        "",
        "## Months from the last printed date to the first copy printing `Built`",
        "",
        f"n={q['n']}: min {q['min']}, p25 {q['p25']}, median {q['median']}, p75 {q['p75']}, max {q['max']}. "
        f"`Built` printed before the date it had carried: {s['built_copy_before_the_date']}; within six months after: "
        f"{s['built_copy_within_six_months_after']}; later than six months: {s['built_copy_later_than_six_months']}.",
        "",
        "A negative value means the register called the project `Built` before the connection date it was carrying; a large positive "
        "value means the date it carried had passed long before the register said `Built`. The archive's cadence bounds every value: "
        "the first copy printing `Built` is the first copy *held*, not the first published, and the gap of July 2025 to May 2026 widens "
        "that bound for transitions seen in the May 2026 copy.",
        "",
        "| year of the `Built` copy | n | min | p25 | median | p75 | max |",
        "|---|---|---|---|---|---|---|",
    ]
    L += [
        f"| {y} | {v['n']} | {v['min']} | {v['p25']} | {v['median']} | {v['p75']} | {v['max']} |"
        for y, v in s["by_year_of_built_copy"].items()
    ]
    L += [
        "",
        "| plant type as printed | n | min | p25 | median | p75 | max |",
        "|---|---|---|---|---|---|---|",
    ]
    L += [
        f"| {p} | {v['n']} | {v['min']} | {v['p25']} | {v['median']} | {v['p75']} | {v['max']} |"
        for p, v in list(s["by_plant_type"].items())[:15]
    ]
    zero_mw = sum(
        1
        for t in found
        if t.klass == "transition"
        and t.last_date_before_built is not None
        and (t.mw or Decimal(0)) == 0
    )
    L += [
        "",
        "## Population P2",
        "",
        f"{s['gate2_rows']} rows print Gate `2` in the copy of 29/09/2026 (`evidence/gate2.json`).",
        "",
        "## What the schema pass found, for amendment 1",
        "",
    ]
    for name, key in (
        ("elexon-bmunits-020", "S1_bmunits"),
        ("elexon-b1610-020", "S2_b1610"),
        ("elexon-remit-020", "S3_remit"),
        ("entsoe-units-020", "S4_entsoe"),
    ):
        path = REPO_ROOT / "archives" / name / "schema-report.json"
        if not path.exists():
            L.append(f"- `{name}`: no report yet.")
            continue
        r = json.loads(path.read_text())[key]
        if key == "S1_bmunits":
            L.append(
                f"- **S1** `reference/bmunits/all`: {r['units']} units; date-like fields: {r['date_like_fields'] or 'none'}; "
                f"{r['with_eic']} with an EIC. No registration date is served, so F3's route applies: registration date leaves "
                "the question by amendment; S1 names units, lead parties, capacities and fuel types only."
            )
        elif key == "S2_b1610":
            L.append(
                f"- **S2** B1610 on {r['settlement_day']}: {r['records']:,} records over {r['distinct_bm_units']:,} distinct BM units, "
                f"quantity field `{r['quantity_field']}`; coverage is every unit with a metered volume that day, supplier units included, "
                "not only large generators; one day's file is about 100 MB, so S2 is read per admitted unit, never whole."
            )
        elif key == "S3_remit":
            pr = r["historical_probes"]
            L.append(
                f"- **S3** REMIT: {r['messages']} captured messages on {r['mirror_day']}; the by-event listing serves history "
                f"({', '.join(f'{k}: {v["items"]} items' for k, v in pr.items())}), giving ids, mrids and revision numbers only, "
                f"so each message's detail is a second request. Message fields present: "
                f"{', '.join(list(r['message_fields_present'])[:14])}; asset identifiers: "
                f"{', '.join(r['asset_identifier_fields']) or 'none found'}."
            )
        else:
            L.append(f"- **S4** ENTSO-E: {r['status']}.")
    L += [
        "",
        "*Post-hoc observation, not a declared figure, recorded for amendment 1:* "
        f"{zero_mw} of the {s['measured']} measured transitions carry a stage MW of 0 (a later stage of a built project, or a "
        "modification row), and the largest negative values above are such rows: the register prints `Built` against a project "
        "whose later stage still carries a future date. Amendment 1 should say whether the measure runs per unit or per project "
        "and how zero-MW stages are read.",
        "",
        "## What this version never claims",
        "",
        "That any unit produced anything: `Built` is a status the register prints when NESO is told a milestone was met. "
        "That the months above are delays: they are the distance between two things the register printed. "
        "The energisation truth waits for the sources the declaration names, after their schema pass and amendment 1.",
        "",
    ]
    return "\n".join(L)


# ----------------------------------------------------------------- schema


def field_report(bodies: list[dict[str, Any]], items_key: str = "data") -> dict[str, Any]:
    top: Counter = Counter()
    fields: Counter = Counter()
    n = 0
    for body in bodies:
        for k, v in body.items():
            if v not in (None, "", [], {}):
                top[k] += 1
        items = body.get(items_key) if isinstance(body, dict) else None
        if isinstance(items, list):
            for item in items:
                n += 1
                if isinstance(item, dict):
                    for k, v in item.items():
                        if v not in (None, "", [], {}):
                            fields[k] += 1
    return {
        "files": len(bodies),
        "items": n,
        "top_level_fields_present": dict(top.most_common()),
        "item_fields_present": dict(fields.most_common()),
    }


def phase_schema(seal: str | None, run_date: str) -> None:
    require_seal(seal)
    raw = REPO_ROOT / "data/raw/elexon/020" / run_date
    journal, manifest = raw / "journal.ndjson", raw / "manifest.json"
    jobs = [
        ("elexon-bmunits", elexon.bmunits_url(), raw / "bmunits.json"),
        (
            "elexon-b1610",
            elexon.b1610_stream_url(SETTLEMENT_DAY, ()),
            raw / f"b1610-{SETTLEMENT_DAY}.json",
        ),
        (
            "elexon-remit-by-event-2021",
            f"{elexon.BASE_URL}/remit/list/by-event?from=2021-01-01T00:00:00Z&to=2021-01-07T23:59:59Z",
            raw / "remit-by-event-2021-01.json",
        ),
        (
            "elexon-remit-by-event-2018",
            f"{elexon.BASE_URL}/remit/list/by-event?from=2018-01-01T00:00:00Z&to=2018-01-07T23:59:59Z",
            raw / "remit-by-event-2018-01.json",
        ),
    ]
    fetch_journalled(
        jobs,
        journal_path=journal,
        manifest_path=manifest,
        repo_root=REPO_ROOT,
        fetch=elexon.fetch_pinned,
        sleep_seconds=0.5,
        progress=progress,
    )

    def body(path: Path) -> Any:
        try:
            return json.loads(path.read_text())
        except OSError, json.JSONDecodeError:
            return {}

    reports: dict[str, Any] = {"run_date": run_date, "declaration_sha256": en.DECLARATION_SHA256}
    # S1
    bm = body(raw / "bmunits.json")
    units = bm if isinstance(bm, list) else bm.get("data") or []
    fields: Counter = Counter()
    for u in units:
        for k, v in u.items():
            if v not in (None, "", [], {}):
                fields[k] += 1
    date_like = sorted(
        k
        for k in fields
        if any(w in k.lower() for w in ("date", "from", "effective", "registered", "commission"))
    )
    reports["S1_bmunits"] = {
        "sha256": sha(raw / "bmunits.json"),
        "units": len(units),
        "fields_present": dict(fields.most_common()),
        "date_like_fields": date_like,
        "bm_unit_types": dict(Counter(str(u.get("bmUnitType")) for u in units).most_common()),
        "with_eic": sum(1 for u in units if u.get("eic")),
        "fuel_types": dict(Counter(str(u.get("fuelType")) for u in units).most_common(30)),
    }
    # S2
    b = body(raw / f"b1610-{SETTLEMENT_DAY}.json")
    recs = b if isinstance(b, list) else b.get("data") or []
    per_unit: Counter = Counter(str(r.get("bmUnit")) for r in recs)
    reports["S2_b1610"] = {
        "sha256": sha(raw / f"b1610-{SETTLEMENT_DAY}.json"),
        "settlement_day": SETTLEMENT_DAY,
        "records": len(recs),
        "distinct_bm_units": len(per_unit),
        "fields_present": dict(
            Counter(k for r in recs for k, v in r.items() if v not in (None, "")).most_common()
        ),
        "sample_units": sorted(per_unit)[:20],
        "quantity_field": next(
            (k for k in ("quantity", "generation", "value") if recs and k in recs[0]), None
        ),
    }
    # S3: the captured list and messages of the mirror day, and the two historical probes
    mirror_lines = [
        json.loads(x)
        for x in (REPO_ROOT / "data/manifests" / f"{REMIT_MIRROR_DAY}.ndjson")
        .read_text()
        .splitlines()
        if x.strip()
    ]
    remit = [x for x in mirror_lines if x.get("resource") == "remit"]
    lists = [x for x in remit if str(x.get("dataset", "")).startswith("ELEXON-REMIT-LIST")]
    messages = [x for x in remit if str(x.get("dataset", "")).startswith("ELEXON-REMIT-MESSAGE")]
    list_bodies = [body(REPO_ROOT / "data/raw/archive" / x["key"]) for x in lists]
    msg_bodies = [body(REPO_ROOT / "data/raw/archive" / x["key"]) for x in messages]
    msg_fields: Counter = Counter()
    asset_fields: Counter = Counter()
    for m in msg_bodies:
        inner = m.get("data") if isinstance(m, dict) and "data" in m else m
        items = inner if isinstance(inner, list) else [inner]
        for it in items:
            if not isinstance(it, dict):
                continue
            for k, v in it.items():
                if v not in (None, "", [], {}):
                    msg_fields[k] += 1
                if any(w in k.lower() for w in ("asset", "unit", "eic", "affected")):
                    asset_fields[k] += 1
    probes = {}
    for label in ("remit-by-event-2021-01", "remit-by-event-2018-01"):
        pb = body(raw / f"{label}.json")
        items = pb if isinstance(pb, list) else pb.get("data") or []
        dict_items = [i for i in items if isinstance(i, dict)]
        item_fields: Counter = Counter(
            k for i in dict_items for k, v in i.items() if v not in (None, "", [], {})
        )
        starts = sorted(
            str(i.get("eventStartTime") or i.get("eventStart"))
            for i in dict_items
            if i.get("eventStartTime") or i.get("eventStart")
        )
        probes[label] = {
            "sha256": sha(raw / f"{label}.json"),
            "items": len(items),
            "item_fields_present": dict(item_fields.most_common()),
            "earliest_event_start": starts[0] if starts else None,
            "latest_event_start": starts[-1] if starts else None,
            "asset_types": dict(Counter(str(i.get("assetType")) for i in dict_items).most_common()),
            "event_types": dict(Counter(str(i.get("eventType")) for i in dict_items).most_common()),
            "unavailability_types": dict(
                Counter(str(i.get("unavailabilityType")) for i in dict_items).most_common()
            ),
        }
    reports["S3_remit"] = {
        "mirror_day": REMIT_MIRROR_DAY,
        "lists": len(lists),
        "messages": len(messages),
        "list_report": field_report(list_bodies, "data"),
        "message_fields_present": dict(msg_fields.most_common()),
        "asset_identifier_fields": dict(asset_fields.most_common()),
        "historical_probes": probes,
    }
    reports["S4_entsoe"] = {
        "status": "not available: the repository holds no ENTSO-E Transparency token; no request made",
        "consequence": "S4 cannot enter amendment 1 until a token is held and a schema pass is run",
    }
    for name, key in (
        ("elexon-bmunits-020", "S1_bmunits"),
        ("elexon-b1610-020", "S2_b1610"),
        ("elexon-remit-020", "S3_remit"),
        ("entsoe-units-020", "S4_entsoe"),
    ):
        out = REPO_ROOT / "archives" / name
        write_json(
            out / "schema-report.json",
            {"run_date": run_date, "declaration_sha256": en.DECLARATION_SHA256, key: reports[key]},
        )
        (out / "SCHEMA.md").write_text(schema_md(name, key, reports[key], run_date))
    log_run(
        "schema",
        run_date=run_date,
        s1_units=reports["S1_bmunits"]["units"],
        s2_units=reports["S2_b1610"]["distinct_bm_units"],
        s3_messages=reports["S3_remit"]["messages"],
        probes={k: v["items"] for k, v in probes.items()},
    )
    print(
        f"S1 {reports['S1_bmunits']['units']} units, date-like fields {reports['S1_bmunits']['date_like_fields']}; "
        f"S2 {reports['S2_b1610']['records']} records over {reports['S2_b1610']['distinct_bm_units']} units on {SETTLEMENT_DAY}; "
        f"S3 {len(messages)} captured messages, probes {[(k, v['items']) for k, v in probes.items()]}; S4 not available"
    )


def schema_md(name: str, key: str, r: dict[str, Any], run_date: str) -> str:
    L = [
        f"# Schema report: {name}",
        "",
        f"Regenerated by `investigations/020-did-it-energise/run.py --phase schema` on {run_date} under declaration `{en.DECLARATION_SHA256[:8]}…`; "
        "`schema-report.json` beside this file has every field. No figure of the investigation is computed here.",
        "",
    ]
    if key == "S4_entsoe":
        L += [r["status"], "", r["consequence"], ""]
        return "\n".join(L)
    for k, v in r.items():
        if (
            isinstance(v, dict)
            and v
            and all(isinstance(x, int | str | type(None)) for x in v.values())
        ):
            L += (
                [f"## {k}", "", "| key | value |", "|---|---|"]
                + [f"| {a} | {b} |" for a, b in v.items()]
                + [""]
            )
        elif isinstance(v, dict):
            L += [f"## {k}", "", "```json", json.dumps(v, indent=1, default=str), "```", ""]
        else:
            L += [f"- **{k}**: {v}"]
    L.append("")
    return "\n".join(L)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--phase", required=True, choices=["population", "schema"])
    parser.add_argument("--seal", default=None)
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    EVIDENCE.mkdir(exist_ok=True)
    if args.phase == "population":
        phase_population(args.seal)
    else:
        phase_schema(args.seal, args.run_date)


if __name__ == "__main__":
    main()
