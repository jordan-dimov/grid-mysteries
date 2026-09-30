# ruff: noqa: E501
"""019 — Who holds the queue: gated, resumable runner under DECLARATION.md.

    uv run --group registers python investigations/019-who-holds-the-queue/run.py --phase names
    uv run --group registers python investigations/019-who-holds-the-queue/run.py --phase history
    uv run --group registers python investigations/019-who-holds-the-queue/run.py \\
        --phase acquire --seal 877682f7 [--run-date YYYY-MM-DD]
    scripts/schema-report companies-house            (== --phase schema)
    uv run --group registers python investigations/019-who-holds-the-queue/run.py --phase compute

Phases, each committed before the next:

- ``names`` (archive only): C1 on the copy, R1's distinct names →
  ``evidence/names.json``.
- ``history`` (archive only): every copy that prints a ``Project ID``, in
  publication order, each verified against its recorded digest; per id the
  printed customer name per copy, collapsed to changes →
  ``evidence/name-history.json`` (R4's input and the identity guard's
  first-seen dates).
- ``acquire`` (needs the seal): search every name once; classify by R2;
  advanced search and candidate profiles where no exact candidate; then for
  every rule-resolved company its profile, PSC list, PSC statements and
  charges. Every response is pinned and journalled under
  ``data/raw/companies-house/<run-date>-019/`` before the next request;
  ``links.ndjson`` is append-only (C4). Interrupted, it resumes from the
  journal (C5).
- ``schema``: field presence and spellings across the pinned responses →
  ``archives/companies-house-019/``.
- ``compute``: R3 to R6 and figures 1 to 4 over the pinned bytes and the
  admitted links; ``evidence/results.json`` and ``RESULTS.md``.
"""

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, write_json
from grid_mysteries.investigations import queue_ownership as qo
from grid_mysteries.investigations.overdue_queue import project_id
from grid_mysteries.sources import tec_register as tr
from grid_mysteries.sources.companies_house import (
    AuthenticatedFetcher,
    advanced_search_url,
    api_key,
    charges_url,
    profile_url,
    psc_statements_url,
    psc_url,
    search_url,
)
from grid_mysteries.sources.pinning import fetch_journalled, progress
from grid_mysteries.tec import sources as tec_sources

HERE = Path(__file__).parent
DECLARATION = HERE / "DECLARATION.md"
EVIDENCE = HERE / "evidence"
NAMES_JSON = EVIDENCE / "names.json"
HISTORY_JSON = EVIDENCE / "name-history.json"
LINKS_NDJSON = EVIDENCE / "links.ndjson"
PROPOSED_JSON = EVIDENCE / "links-proposed.json"
ADMITTED_JSON = EVIDENCE / "links-admitted.json"
COMPANIES_NDJSON = EVIDENCE / "companies.ndjson"
MANIFEST_JSON = EVIDENCE / "manifest.json"
RESULTS_JSON = EVIDENCE / "results.json"
RESULTS_MD = HERE / "RESULTS.md"
RUN_LOG = EVIDENCE / "run-log.json"
ARCHIVE = REPO_ROOT / "archives" / "companies-house-019"

COPY_SHA256 = "d1ccd9e210b4f6bc8f3b0e83d54032dc61f247dbbc1d9e469a342b7766ee5746"
COPY_KEY = "raw/neso/tec-register/2026-09-30/" + COPY_SHA256
COPY_MANIFEST = "data/manifests/2026-09-30.ndjson"
COPY_ROWS = 2199
SCHEMA_REPORT_SHA256 = "857dfc88949a95b3553d96fa25bd84fbed6f4ed433f1090f324140b644975ebd"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_seal(seal: str | None) -> str:
    digest = sha(DECLARATION)
    if digest != qo.DECLARATION_SHA256:
        sys.exit(
            f"DECLARATION.md hashes to {digest[:8]}, not the frozen {qo.DECLARATION_SHA256[:8]}"
        )
    if not seal or not digest.startswith(seal):
        sys.exit("refusing: --seal must be a prefix of the frozen declaration's SHA-256")
    return digest


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except OSError, json.JSONDecodeError:
        return {}


def slug(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60] or "blank"
    return f"{base}-{hashlib.sha256(name.encode()).hexdigest()[:8]}"


def the_copy() -> list[dict[str, object]]:
    path = REPO_ROOT / "data/raw/archive" / COPY_KEY
    if sha(path) != COPY_SHA256:
        sys.exit("C1: the copy's bytes do not hash to the declared digest")
    rows = tr.read_vintage(path, "csv")
    if len(rows) != COPY_ROWS:
        sys.exit(f"C1: {len(rows)} rows, not the schema report's {COPY_ROWS}")
    return rows


def log_run(phase: str, **facts: Any) -> None:
    log = load_json(RUN_LOG) or {"runs": []}
    log["runs"].append(
        {"phase": phase, "at": datetime.now(UTC).isoformat(timespec="seconds"), **facts}
    )
    write_json(RUN_LOG, log)


# ------------------------------------------------------------------ names


def phase_names() -> None:
    rows = the_copy()
    all_names = qo.names(rows)
    out = {
        "declaration_sha256": qo.DECLARATION_SHA256,
        "copy_sha256": COPY_SHA256,
        "copy_manifest": COPY_MANIFEST,
        "schema_report_sha256": SCHEMA_REPORT_SHA256,
        "rows": len(rows),
        "distinct_names": len(all_names),
        "distinct_casefold": len({n.casefold() for n in all_names}),
        "case_pairs": qo.case_pairs(all_names),
        "no_suffix": sorted(n.name for n in all_names.values() if n.no_suffix),
        "rows_without_project_id": sum(1 for r in rows if not project_id(r)),
        "names": {
            n.name: {"rows": n.rows, "mw": n.mw, "project_ids": sorted(n.project_ids)}
            for n in sorted(all_names.values(), key=lambda x: x.name)
        },
    }
    write_json(NAMES_JSON, out)
    log_run("names", distinct_names=len(all_names))
    print(
        f"{len(rows)} rows, {len(all_names)} distinct names, {len(out['no_suffix'])} without a suffix"
    )


# ---------------------------------------------------------------- history


def phase_history() -> None:
    copies = tec_sources.copies(REPO_ROOT)
    per_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    read: list[dict[str, Any]] = []
    for copy in copies:
        try:
            tec_sources.verify(copy)
            rows = tec_sources.read(copy)
        except Exception as error:  # noqa: BLE001 - recorded, never hidden
            read.append(
                {"t_public": copy.published_on, "sha256": copy.sha256, "error": str(error)[:120]}
            )
            continue
        if not rows or "Project ID" not in rows[0]:
            continue
        seen: dict[str, str] = {}
        for row in rows:
            pid = project_id(row)
            if pid and pid not in seen:
                seen[pid] = qo.printed_name(row)
        for pid, name in seen.items():
            seq = per_id[pid]
            if not seq or seq[-1]["name"] != name:
                seq.append(
                    {"t_public": copy.published_on.isoformat(), "sha256": copy.sha256, "name": name}
                )
            else:
                seq[-1]["last_t_public"] = copy.published_on.isoformat()
        read.append(
            {
                "t_public": copy.published_on,
                "sha256": copy.sha256,
                "rows": len(rows),
                "ids": len(seen),
            }
        )
    first_seen: dict[str, str] = {}
    for seq in per_id.values():
        for entry in seq:
            name = entry["name"]
            if name not in first_seen or entry["t_public"] < first_seen[name]:
                first_seen[name] = entry["t_public"]
    out = {
        "declaration_sha256": qo.DECLARATION_SHA256,
        "copies_read": [r for r in read if "rows" in r],
        "copies_unreadable": [r for r in read if "error" in r],
        "copies_with_project_id": sum(1 for r in read if "rows" in r),
        "project_ids": len(per_id),
        "first_seen": dict(sorted(first_seen.items())),
        "history": dict(sorted(per_id.items())),
    }
    write_json(HISTORY_JSON, out)
    log_run("history", copies=len(out["copies_read"]), project_ids=len(per_id))
    print(
        f"{len(out['copies_read'])} copies with a Project ID column, {len(per_id)} ids, {len(first_seen)} names first-seen"
    )


# ---------------------------------------------------------------- acquire


class PatientFetcher:
    """The authenticated fetcher with a wait on 429 and 5xx (C5 counts them)."""

    def __init__(self, key: str) -> None:
        self.inner = AuthenticatedFetcher(key)
        self.failures = 0
        self.requests = 0

    def __call__(self, *, url: str, destination: Path, dataset: str):
        for attempt in range(6):
            try:
                self.requests += 1
                return self.inner(url=url, destination=destination, dataset=dataset)
            except httpx.HTTPStatusError as error:
                code = error.response.status_code
                self.failures += 1
                if code == 429 or code >= 500:
                    wait = 60 * (attempt + 1)
                    print(f"  {code} on {url[:80]}; waiting {wait}s", flush=True)
                    time.sleep(wait)
                    continue
                raise
            except httpx.TransportError as error:
                self.failures += 1
                print(f"  {type(error).__name__}; waiting 60s", flush=True)
                time.sleep(60)
        raise RuntimeError(f"gave up on {url}")


def append_links(links: list[qo.Link], run_date: str, search_digests: dict[str, str]) -> None:
    """C4: append only; a line that would change stops the run."""
    existing: dict[str, str] = {}
    if LINKS_NDJSON.exists():
        for line in LINKS_NDJSON.read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                existing[(record["name"], record["rule_version"], record["run_date"])] = line
    with LINKS_NDJSON.open("a") as f:
        for link in links:
            record = {
                "name": link.name,
                "class": link.klass,
                "company_number": link.company_number,
                "candidates": list(link.candidates),
                "note": link.note,
                "rule_version": link.rule_version,
                "run_date": run_date,
                "search_sha256": search_digests.get(link.name),
            }
            line = json.dumps(record, ensure_ascii=False)
            key = (link.name, link.rule_version, run_date)
            if key in existing:
                if existing[key] != line:
                    sys.exit(f"C4: links.ndjson line for {link.name!r} would change on recompute")
                continue
            f.write(line + "\n")


def phase_acquire(seal: str | None, run_date: str) -> None:
    require_seal(seal)
    if not NAMES_JSON.exists() or not HISTORY_JSON.exists():
        sys.exit("run --phase names and --phase history first")
    all_names = load_json(NAMES_JSON)["names"]
    first_seen = {
        k: date.fromisoformat(v) for k, v in load_json(HISTORY_JSON)["first_seen"].items()
    }
    raw = REPO_ROOT / "data/raw/companies-house" / f"{run_date}-019"
    journal, manifest = raw / "journal.ndjson", raw / "manifest.json"
    fetcher = PatientFetcher(api_key())

    def pin(jobs):
        return fetch_journalled(
            jobs,
            journal_path=journal,
            manifest_path=manifest,
            repo_root=REPO_ROOT,
            fetch=fetcher,
            sleep_seconds=0,
            progress=progress,
        )

    ordered = sorted(all_names)
    print(f"{len(ordered)} names; searching", flush=True)
    pin([("ch-search", search_url(n), raw / "search" / f"{slug(n)}.json") for n in ordered])
    searches = {n: load_json(raw / "search" / f"{slug(n)}.json").get("items", []) for n in ordered}
    search_digests = {n: sha(raw / "search" / f"{slug(n)}.json") for n in ordered}

    need_adv = [n for n in ordered if len(qo.exact_candidates(n, searches[n])) == 0]
    print(f"{len(need_adv)} names with no exact candidate; advanced search", flush=True)
    pin(
        [
            ("ch-advanced-search", advanced_search_url(n), raw / "advanced" / f"{slug(n)}.json")
            for n in need_adv
        ]
    )
    advanced = {
        n: load_json(raw / "advanced" / f"{slug(n)}.json").get("items", []) for n in need_adv
    }
    adv_numbers = sorted({c.number for n in need_adv for c in qo.candidates(advanced[n])})
    print(f"{len(adv_numbers)} advanced-search hits; profiles", flush=True)
    pin([("ch-profile", profile_url(x), raw / "company" / x / "profile.json") for x in adv_numbers])
    profiles = {x: load_json(raw / "company" / x / "profile.json") for x in adv_numbers}

    links = [
        qo.resolve(
            n, searches[n], advanced.get(n) if n in advanced else None, profiles, first_seen.get(n)
        )
        for n in ordered
    ]
    resolved = sorted({lk.company_number for lk in links if lk.resolved and lk.company_number})
    print(
        f"{len(resolved)} companies resolved by rule; profile, PSC, statements, charges", flush=True
    )
    jobs = []
    for x in resolved:
        jobs += [
            ("ch-profile", profile_url(x), raw / "company" / x / "profile.json"),
            ("ch-psc", psc_url(x), raw / "company" / x / "psc.json"),
            (
                "ch-psc-statements",
                psc_statements_url(x),
                raw / "company" / x / "psc-statements.json",
            ),
            ("ch-charges", charges_url(x), raw / "company" / x / "charges.json"),
        ]
    pin(jobs)

    append_links(links, run_date, search_digests)

    def describe(number: str, name: str) -> dict[str, Any]:
        for hit in [*searches.get(name, []), *advanced.get(name, [])]:
            if str(hit.get("company_number")) == number:
                return {
                    "number": number,
                    "title": hit.get("title") or hit.get("company_name"),
                    "status": hit.get("company_status"),
                    "created": hit.get("date_of_creation"),
                    "ceased": hit.get("date_of_cessation"),
                    "address": hit.get("address_snippet"),
                }
        return {"number": number}

    proposed = [
        {
            "name": lk.name,
            "class": lk.klass,
            "candidates": [describe(c, lk.name) for c in lk.candidates],
            "note": lk.note,
            "rows": all_names[lk.name]["rows"],
            "mw": all_names[lk.name]["mw"],
            "project_ids": all_names[lk.name]["project_ids"],
        }
        for lk in links
        if not lk.resolved
    ]
    proposed.sort(key=lambda x: -Decimal(str(x["mw"])))
    write_json(
        PROPOSED_JSON,
        {
            "run_date": run_date,
            "rule_version": qo.RULE_VERSION,
            "count": len(proposed),
            "proposed": proposed,
        },
    )
    if not ADMITTED_JSON.exists():
        write_json(
            ADMITTED_JSON,
            {
                "note": "Written by a person, never by the runner. One entry per name: "
                '{"name": ..., "decision": "admitted"|"refused", "company_number": ..., '
                '"on": "YYYY-MM-DD", "by": "initials"}.',
                "admissions": [],
            },
        )
    write_json(
        MANIFEST_JSON,
        {
            "run_date": run_date,
            "journal": str(journal.relative_to(REPO_ROOT)),
            "journal_sha256": sha(journal),
            "requests": fetcher.requests,
            "failures": fetcher.failures,
            "classes": dict(Counter(lk.klass for lk in links)),
        },
    )
    log_run(
        "acquire",
        run_date=run_date,
        requests=fetcher.requests,
        failures=fetcher.failures,
        classes=dict(Counter(lk.klass for lk in links)),
    )
    failure_share = Decimal(fetcher.failures) / Decimal(max(fetcher.requests, 1))
    print(
        f"done: {dict(Counter(lk.klass for lk in links))}; {fetcher.requests} requests, "
        f"{fetcher.failures} retried ({failure_share:.3f})"
    )


def phase_acquire_amended(seal: str | None, amendment_seal: str | None, run_date: str) -> None:
    """Amendment 1: the earlier names (A1) and the snippet route (A2), rule version v2."""
    require_seal(seal)
    amendment_digest = require_amendment(amendment_seal)
    names_doc = load_json(NAMES_JSON)["names"]
    history_doc = load_json(HISTORY_JSON)
    first_seen = {k: date.fromisoformat(v) for k, v in history_doc["first_seen"].items()}
    earlier = qo.earlier_names(names_doc, history_doc["history"])
    ordered = sorted(names_doc) + earlier
    raw = REPO_ROOT / "data/raw/companies-house" / f"{run_date}-019"
    journal, manifest = raw / "journal.ndjson", raw / "manifest.json"
    fetcher = PatientFetcher(api_key())

    def pin(jobs):
        return fetch_journalled(
            jobs,
            journal_path=journal,
            manifest_path=manifest,
            repo_root=REPO_ROOT,
            fetch=fetcher,
            sleep_seconds=0,
            progress=progress,
        )

    print(f"{len(names_doc)} copy names + {len(earlier)} earlier names (A1); searching", flush=True)
    pin([("ch-search", search_url(n), raw / "search" / f"{slug(n)}.json") for n in ordered])
    searches = {n: load_json(raw / "search" / f"{slug(n)}.json").get("items", []) for n in ordered}
    search_digests = {n: sha(raw / "search" / f"{slug(n)}.json") for n in ordered}
    no_exact = [n for n in ordered if not qo.exact_candidates(n, searches[n])]
    snippet_numbers = sorted(
        {c.number for n in no_exact for c in qo.snippet_candidates(n, searches[n])}
    )
    print(
        f"{len(no_exact)} names with no exact candidate; {len(snippet_numbers)} snippet candidates (A2); profiles",
        flush=True,
    )
    pin(
        [
            ("ch-profile", profile_url(x), raw / "company" / x / "profile.json")
            for x in snippet_numbers
        ]
    )
    profiles = {x: load_json(raw / "company" / x / "profile.json") for x in snippet_numbers}
    still = [
        n
        for n in no_exact
        if len(
            [
                c
                for c in qo.snippet_candidates(n, searches[n])
                if c.number in profiles and qo.previous_name_matches(n, profiles[c.number])
            ]
        )
        == 0
    ]
    print(f"{len(still)} names on to the advanced search", flush=True)
    pin(
        [
            ("ch-advanced-search", advanced_search_url(n), raw / "advanced" / f"{slug(n)}.json")
            for n in still
        ]
    )
    advanced = {n: load_json(raw / "advanced" / f"{slug(n)}.json").get("items", []) for n in still}
    adv_numbers = sorted(
        {c.number for n in still for c in qo.candidates(advanced[n])} - set(profiles)
    )
    pin([("ch-profile", profile_url(x), raw / "company" / x / "profile.json") for x in adv_numbers])
    for x in adv_numbers:
        profiles[x] = load_json(raw / "company" / x / "profile.json")
    links = [
        qo.resolve_v2(
            n, searches[n], advanced.get(n) if n in advanced else None, profiles, first_seen.get(n)
        )
        for n in ordered
    ]
    resolved = sorted({lk.company_number for lk in links if lk.resolved and lk.company_number})
    print(
        f"{len(resolved)} companies resolved under v2; profile, PSC, statements, charges",
        flush=True,
    )
    jobs = []
    for x in resolved:
        jobs += [
            ("ch-profile", profile_url(x), raw / "company" / x / "profile.json"),
            ("ch-psc", psc_url(x), raw / "company" / x / "psc.json"),
            (
                "ch-psc-statements",
                psc_statements_url(x),
                raw / "company" / x / "psc-statements.json",
            ),
            ("ch-charges", charges_url(x), raw / "company" / x / "charges.json"),
        ]
    pin(jobs)
    append_links(links, run_date, search_digests)

    def describe(number: str, name: str) -> dict[str, Any]:
        for hit in [*searches.get(name, []), *advanced.get(name, [])]:
            if str(hit.get("company_number")) == number:
                return {
                    "number": number,
                    "title": hit.get("title") or hit.get("company_name"),
                    "status": hit.get("company_status"),
                    "created": hit.get("date_of_creation"),
                    "ceased": hit.get("date_of_cessation"),
                    "address": hit.get("address_snippet"),
                    "snippet": hit.get("snippet"),
                }
        return {"number": number}

    proposed = [
        {
            "name": lk.name,
            "class": lk.klass,
            "earlier_name": lk.name not in names_doc,
            "candidates": [describe(c, lk.name) for c in lk.candidates],
            "note": lk.note,
            "rows": names_doc.get(lk.name, {}).get("rows", 0),
            "mw": names_doc.get(lk.name, {}).get("mw", "0"),
            "project_ids": names_doc.get(lk.name, {}).get("project_ids", []),
        }
        for lk in links
        if not lk.resolved
    ]
    proposed.sort(key=lambda x: (x["earlier_name"], -Decimal(str(x["mw"]))))
    write_json(
        PROPOSED_JSON,
        {
            "run_date": run_date,
            "rule_version": qo.RULE_VERSION_V2,
            "amendment_1_sha256": amendment_digest,
            "count": len(proposed),
            "count_copy_names": sum(1 for x in proposed if not x["earlier_name"]),
            "proposed": proposed,
        },
    )
    previous = load_json(MANIFEST_JSON)
    classes = dict(Counter(lk.klass for lk in links))
    classes_copy = dict(Counter(lk.klass for lk in links if lk.name in names_doc))
    write_json(
        MANIFEST_JSON,
        {
            **previous,
            "amendment_1": {
                "sha256": amendment_digest,
                "rule_version": qo.RULE_VERSION_V2,
                "journal_sha256": sha(journal),
                "requests": fetcher.requests,
                "failures": fetcher.failures,
                "earlier_names": len(earlier),
                "classes_all": classes,
                "classes_copy_names": classes_copy,
            },
        },
    )
    log_run(
        "acquire-amendment-1",
        run_date=run_date,
        requests=fetcher.requests,
        failures=fetcher.failures,
        earlier_names=len(earlier),
        classes_copy_names=classes_copy,
        classes_all=classes,
    )
    print(
        f"done under v2: copy names {classes_copy}; all names {classes}; {fetcher.requests} requests, {fetcher.failures} retried"
    )


# ----------------------------------------------------------------- schema


def phase_schema(run_date: str) -> None:
    raw = REPO_ROOT / "data/raw/companies-house" / f"{run_date}-019"
    if not raw.exists():
        sys.exit(f"no pinned responses under {raw}")
    kinds = {
        "search": sorted((raw / "search").glob("*.json")) if (raw / "search").exists() else [],
        "advanced": sorted((raw / "advanced").glob("*.json"))
        if (raw / "advanced").exists()
        else [],
        "profile": sorted(raw.glob("company/*/profile.json")),
        "psc": sorted(raw.glob("company/*/psc.json")),
        "psc-statements": sorted(raw.glob("company/*/psc-statements.json")),
        "charges": sorted(raw.glob("company/*/charges.json")),
    }
    report: dict[str, Any] = {"run_date": run_date, "endpoints": {}}
    date_form = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for kind, files in kinds.items():
        top: Counter = Counter()
        item_fields: Counter = Counter()
        spellings: dict[str, Counter] = defaultdict(Counter)
        dates_ok = dates_bad = 0
        n_items = 0
        not_found = 0
        for f in files:
            body = load_json(f)
            if not body or body.get("errors"):
                not_found += 1
                continue
            for k, v in body.items():
                if v not in (None, "", [], {}):
                    top[k] += 1
            for item in body.get("items") or []:
                n_items += 1
                for k, v in item.items():
                    if v not in (None, "", [], {}):
                        item_fields[k] += 1
                    if k in (
                        "notified_on",
                        "ceased_on",
                        "created_on",
                        "satisfied_on",
                        "delivered_on",
                        "date_of_creation",
                        "date_of_cessation",
                    ):
                        if date_form.match(str(v)):
                            dates_ok += 1
                        else:
                            dates_bad += 1
                for key in ("company_status", "kind", "status"):
                    if key in item:
                        spellings[f"items.{key}"][str(item[key])] += 1
            for key in ("company_status", "type"):
                if key in body:
                    spellings[key][str(body[key])] += 1
                for p in body.get("previous_company_names") or []:
                    item_fields["previous_company_names[].name"] += bool(p.get("name"))
                    item_fields["previous_company_names[].effective_from"] += bool(
                        p.get("effective_from")
                    )
                    item_fields["previous_company_names[].ceased_on"] += bool(p.get("ceased_on"))
            if body.get("date_of_creation"):
                if date_form.match(str(body["date_of_creation"])):
                    dates_ok += 1
                else:
                    dates_bad += 1
        report["endpoints"][kind] = {
            "files": len(files),
            "not_found_or_empty": not_found,
            "items": n_items,
            "top_level_fields_present": dict(top.most_common()),
            "item_fields_present": dict(item_fields.most_common()),
            "spellings": {k: dict(v.most_common()) for k, v in spellings.items()},
            "dates_iso": dates_ok,
            "dates_other": dates_bad,
        }
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    write_json(ARCHIVE / "schema-report.json", report)
    lines = [
        "# Schema report: Companies House responses pinned for 019",
        "",
        f"Regenerated by `scripts/schema-report companies-house {run_date}` from `data/raw/companies-house/{run_date}-019/` "
        "(local, journalled; digests in the investigation's manifest). Field presence counts non-empty values; "
        "no figure of the investigation is computed here.",
        "",
    ]
    for kind, e in report["endpoints"].items():
        lines += [
            f"## `{kind}`: {e['files']} files, {e['not_found_or_empty']} not found or empty, {e['items']} items; "
            f"dates ISO {e['dates_iso']}, other {e['dates_other']}",
            "",
        ]
        lines += ["| field | files or items with a value |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in e["top_level_fields_present"].items()]
        lines += [f"| items[].{k} | {v} |" for k, v in e["item_fields_present"].items()]
        for key, counts in e["spellings"].items():
            lines += [
                "",
                f"`{key}` spellings: " + ", ".join(f"`{k}` {v}" for k, v in counts.items()),
            ]
        lines.append("")
    (ARCHIVE / "SCHEMA.md").write_text("\n".join(lines) + "\n")
    log_run(
        "schema", run_date=run_date, files={k: e["files"] for k, e in report["endpoints"].items()}
    )
    print(
        f"schema report -> {ARCHIVE.relative_to(REPO_ROOT)}/ ({', '.join(f'{k} {e["files"]}' for k, e in report['endpoints'].items())})"
    )


# ---------------------------------------------------------------- compute


AMENDMENT_1 = HERE / "DECLARATION-amendment-1.md"


def require_amendment(amendment_seal: str | None) -> str:
    digest = sha(AMENDMENT_1)
    if not amendment_seal or not digest.startswith(amendment_seal):
        sys.exit("refusing: --amendment-seal must be a prefix of the frozen amendment's SHA-256")
    if not (AMENDMENT_1.with_suffix(".md.timestamps.json")).exists():
        sys.exit("refusing: the amendment has no proof sidecar; freeze it first")
    return digest


def versions_present(run_date: str) -> set[str]:
    out = set()
    if LINKS_NDJSON.exists():
        for line in LINKS_NDJSON.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r["run_date"] == run_date:
                    out.add(r["rule_version"])
    return out


def load_links(run_date: str, version: str = qo.RULE_VERSION) -> dict[str, qo.Link]:
    out: dict[str, qo.Link] = {}
    for line in LINKS_NDJSON.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r["run_date"] != run_date or r["rule_version"] != version:
            continue
        out[r["name"]] = qo.Link(
            r["name"], r["class"], r["company_number"], tuple(r["candidates"]), r["note"], version
        )
    return out


def phase_compute(run_date: str) -> None:
    require_seal(qo.DECLARATION_SHA256[:8])
    if not (ARCHIVE / "schema-report.json").exists():
        sys.exit("run the schema phase first")
    raw = REPO_ROOT / "data/raw/companies-house" / f"{run_date}-019"
    names_doc = load_json(NAMES_JSON)
    all_names: dict[str, qo.Name] = {}
    for n, facts in names_doc["names"].items():
        all_names[n] = qo.Name(n, facts["rows"], Decimal(facts["mw"]), set(facts["project_ids"]))
    admitted = {a["name"]: a for a in load_json(ADMITTED_JSON).get("admissions", [])}
    version = (
        qo.RULE_VERSION_V2 if qo.RULE_VERSION_V2 in versions_present(run_date) else qo.RULE_VERSION
    )
    links = {
        n: qo.apply_admissions(lk, admitted) for n, lk in load_links(run_date, version).items()
    }
    links_v1 = (
        {
            n: qo.apply_admissions(lk, admitted)
            for n, lk in load_links(run_date, qo.RULE_VERSION).items()
        }
        if version != qo.RULE_VERSION
        else None
    )
    missing = [n for n in all_names if n not in links]
    if missing:
        sys.exit(f"C6: {len(missing)} names have no link line (e.g. {missing[0]!r})")
    numbers = sorted(
        {lk.company_number for lk in links.values() if lk.resolved and lk.company_number}
    )
    profiles = {x: load_json(raw / "company" / x / "profile.json") for x in numbers}
    companies = []
    for x in numbers:
        p = profiles[x]
        psc = qo.psc_summary(
            load_json(raw / "company" / x / "psc.json"),
            load_json(raw / "company" / x / "psc-statements.json"),
        )
        ch = qo.charge_facts(load_json(raw / "company" / x / "charges.json"))
        companies.append(
            {
                "company_number": x,
                "company_name": p.get("company_name"),
                "company_status": p.get("company_status"),
                "date_of_creation": p.get("date_of_creation"),
                "under_a_year_old": qo.under_a_year_old(p),
                "age_years": qo.age_years(p),
                "previous_names": p.get("previous_company_names") or [],
                **psc,
                **ch,
            }
        )
    # C7: no PSC name anywhere in committed evidence (only counts are kept).
    with COMPANIES_NDJSON.open("w") as f:
        for c in companies:
            f.write(dumps(c).replace("\n", "") + "\n")
    by_number = {c["company_number"]: c for c in companies}

    rows = the_copy()
    figure1 = qo.resolution_figure(all_names, links)

    def company_of(row):
        lk = links.get(qo.printed_name(row))
        return (
            by_number.get(lk.company_number) if lk and lk.resolved and lk.company_number else None
        )

    # Figure 2: age
    age_rows = age_mw = 0
    young_rows = young_mw = Decimal(0)
    age_hist: dict[str, dict[str, Any]] = defaultdict(lambda: {"rows": 0, "mw": Decimal(0)})
    for row in rows:
        c = company_of(row)
        if c is None or c["age_years"] is None:
            continue
        mw = (
            Decimal(str(all_names[qo.printed_name(row)].mw))
            if False
            else (tr.parse_decimal(row.get("MW Increase / Decrease")) or Decimal(0))
        )
        age_rows += 1
        age_mw += mw
        if c["under_a_year_old"]:
            young_rows += 1
            young_mw += mw
        bucket = f"{int(Decimal(c['age_years']))}y"
        status = str(row.get("Project Status") or "")
        age_hist[f"{status}|{bucket}"]["rows"] += 1
        age_hist[f"{status}|{bucket}"]["mw"] += mw
    figure2 = {
        "resolved_rows": age_rows,
        "resolved_mw": age_mw,
        "under_a_year_rows": young_rows,
        "under_a_year_mw": young_mw,
        "share_rows": qo.share(young_rows, age_rows),
        "share_mw": qo.share(young_mw, age_mw),
        "by_status_and_age_years": dict(sorted(age_hist.items())),
    }

    # Figure 3: name changes
    history = load_json(HISTORY_JSON)["history"]
    current_ids = {pid for n in all_names.values() for pid in n.project_ids}
    changes = [c for c in qo.name_changes(history) if c.project_id in current_ids]
    classed = [qo.classify_change(c, links, profiles) for c in changes]
    counts = Counter(c["class"] for c in classed)
    both_resolved = sum(1 for c in classed if c["class"] in ("rename", "transfer"))
    lags = sorted(c["register_lag_days"] for c in classed if c["register_lag_days"] is not None)
    mw_by_id = defaultdict(lambda: Decimal(0))
    for row in rows:
        if pid := project_id(row):
            mw_by_id[pid] += tr.parse_decimal(row.get("MW Increase / Decrease")) or Decimal(0)
    transfers = sorted(
        (c for c in classed if c["class"] == "transfer"), key=lambda c: -mw_by_id[c["project_id"]]
    )
    figure3 = {
        "events": len(classed),
        "by_class": dict(counts),
        "share_both_resolved": qo.share(both_resolved, len(classed)),
        "F3_fires": (qo.share(both_resolved, len(classed)) or Decimal(0)) < qo.EVENT_THRESHOLD
        if classed
        else None,
        "rename_lag_days": {
            "n": len(lags),
            "min": lags[0] if lags else None,
            "median": lags[len(lags) // 2] if lags else None,
            "max": lags[-1] if lags else None,
            "values": lags,
        },
        "largest_transfers": [{**c, "mw": mw_by_id[c["project_id"]]} for c in transfers[:10]],
        "all": classed,
    }

    # Figure 4: charges
    charged: dict[str, dict[str, Any]] = defaultdict(lambda: {"rows": 0, "mw": Decimal(0)})
    chargee_counter: Counter = Counter()
    for row in rows:
        c = company_of(row)
        mw = tr.parse_decimal(row.get("MW Increase / Decrease")) or Decimal(0)
        klass = "unresolved" if c is None else ("charged" if c["charged"] else "uncharged")
        for dim in (
            "all",
            f"status:{row.get('Project Status')}",
            f"gate:{row.get('Gate') or '(blank)'}",
        ):
            charged[f"{dim}|{klass}"]["rows"] += 1
            charged[f"{dim}|{klass}"]["mw"] += mw
    for c in companies:
        for name in c["chargees"]:
            chargee_counter[name] += 1
    figure4 = {
        "by_class": dict(sorted(charged.items())),
        "distinct_chargees": len(chargee_counter),
        "most_frequent_chargees": chargee_counter.most_common(10),
    }

    # C6: classes sum to the copy.
    total = sum(v["rows"] for k, v in charged.items() if k.startswith("all|"))
    if total != len(rows):
        sys.exit(f"C6: charge classes sum to {total}, not {len(rows)} rows")
    results = {
        "rule_version": version,
        "amendment_1_sha256": sha(AMENDMENT_1) if version == qo.RULE_VERSION_V2 else None,
        "figure1_resolution_v1": qo.resolution_figure(all_names, links_v1) if links_v1 else None,
        "earlier_names_searched": sum(1 for n in links if n not in all_names),
        "declaration_sha256": qo.DECLARATION_SHA256,
        "copy_sha256": COPY_SHA256,
        "run_date": run_date,
        "schema_report_sha256": sha(ARCHIVE / "schema-report.json"),
        "manifest": load_json(MANIFEST_JSON),
        "admissions": len(admitted),
        "figure1_resolution": figure1,
        "figure2_age": figure2,
        "figure3_name_changes": figure3,
        "figure4_charges": figure4,
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    write_json(RESULTS_JSON, results)
    RESULTS_MD.write_text(render(results))
    log_run(
        "compute",
        run_date=run_date,
        admissions=len(admitted),
        F1=figure1["F1_fires"],
        F2=figure1["F2_fires"],
    )
    print(
        f"figure 1: {figure1['resolved_names']}/{figure1['names']} names resolved "
        f"({figure1['resolved_share_of_names']}), MW share {figure1['resolved_share_of_mw']}; "
        f"F1 {'FIRES' if figure1['F1_fires'] else 'silent'}, F2 {'FIRES' if figure1['F2_fires'] else 'silent'}"
    )


def render(r: dict[str, Any]) -> str:
    f1, f2, f3, f4 = (
        r["figure1_resolution"],
        r["figure2_age"],
        r["figure3_name_changes"],
        r["figure4_charges"],
    )
    L = [
        "# 019 — Who holds the queue: results (sponsor only, not for publication)",
        "",
        f"Computed {r['computed_at']} under declaration `{r['declaration_sha256'][:8]}…` over the copy "
        f"`{r['copy_sha256'][:8]}…` (29/09/2026), Companies House responses pinned on {r['run_date']} "
        f"({r['manifest'].get('requests')} requests), schema report `{r['schema_report_sha256'][:8]}…`, "
        f"{r['admissions']} human admission(s) applied. Every figure is a function of the pinned bytes, "
        "`evidence/links.ndjson` and `evidence/links-admitted.json`.",
        "",
        f"Rule version `{r['rule_version']}`"
        + (
            f" (amendment 1 `{r['amendment_1_sha256'][:8]}…`; {r['earlier_names_searched']} earlier names searched for figure 3; "
            f"under v1 the copy's names resolved {r['figure1_resolution_v1']['resolved_names']} of {r['figure1_resolution_v1']['names']})."
            if r.get("figure1_resolution_v1")
            else "."
        ),
        "",
        "## 1. Resolution",
        "",
        f"{f1['names']} distinct printed names, {f1['rows']} rows, {f1['mw']} MW. Resolved (by rule or admission): "
        f"{f1['resolved_names']} names ({f1['resolved_share_of_names']}), {f1['resolved_mw']} MW ({f1['resolved_share_of_mw']}). "
        f"**F1 (resolution under 70 %) {'fires' if f1['F1_fires'] else 'does not fire'}; "
        f"F2 (identity guard over 10 % of rule-resolved) {'fires' if f1['F2_fires'] else 'does not fire'}** "
        f"(guard share {f1['identity_guard_share_of_rule_resolved']}).",
        "",
        "| class | names | rows | MW |",
        "|---|---|---|---|",
    ]
    L += [f"| {k} | {v['names']} | {v['rows']} | {v['mw']} |" for k, v in f1["by_class"].items()]
    if f1["F1_fires"]:
        L += [
            "",
            "F1 fired: figures 2 to 4 below are computed for the record but the join is declared unfit; "
            "figure 1 is the outcome.",
        ]
    L += [
        "",
        "## 2. Companies under a year old on 29/09/2026",
        "",
        f"Of {f2['resolved_rows']} resolved rows ({f2['resolved_mw']} MW): {f2['under_a_year_rows']} rows "
        f"({f2['share_rows']}) and {f2['under_a_year_mw']} MW ({f2['share_mw']}) sit under a company incorporated on or after "
        f"{qo.UNDER_A_YEAR_FROM}.",
        "",
        "| status \\| age | rows | MW |",
        "|---|---|---|",
    ]
    buckets = ("under 1y", "1 to 2y", "2 to 3y", "3 to 5y", "5 to 10y", "10y and over")
    edges = (1, 2, 3, 5, 10)

    def bucket(years: int) -> str:
        return next((buckets[i] for i, e in enumerate(edges) if years < e), buckets[-1])

    grouped: dict[str, dict[str, Any]] = {}
    for k, v in f2["by_status_and_age_years"].items():
        status_, age = k.rsplit("|", 1)
        cell = grouped.setdefault(
            f"{status_} | {bucket(int(age[:-1]))}", {"rows": 0, "mw": Decimal(0)}
        )
        cell["rows"] += v["rows"]
        cell["mw"] += Decimal(str(v["mw"]))
    ordered = sorted(
        grouped.items(),
        key=lambda kv: (kv[0].split(" | ")[0], buckets.index(kv[0].split(" | ")[1])),
    )
    L += [f"| {k} | {v['rows']} | {v['mw']} |" for k, v in ordered]
    L += ["", "(Exact ages per status are in `evidence/results.json`.)"]
    L += [
        "",
        "## 3. The register's own customer-name changes",
        "",
        f"{f3['events']} name-change events on project ids present in the copy, across the copies that print a Project ID. "
        f"By class: {f3['by_class']}. Both names resolved for {f3['share_both_resolved']} of events; "
        f"F3 {'fires' if f3['F3_fires'] else 'does not fire'}.",
        "",
        f"Register lag behind a Companies House rename (days from `ceased_on` of the old name to the first copy printing the new): "
        f"n={f3['rename_lag_days']['n']}, min {f3['rename_lag_days']['min']}, median {f3['rename_lag_days']['median']}, "
        f"max {f3['rename_lag_days']['max']}.",
        "",
        "Ten largest transfers by MW:",
        "",
        "| project id | MW | earlier name | later name | earlier co. | later co. | first copy with later |",
        "|---|---|---|---|---|---|---|",
    ]
    L += [
        f"| {c['project_id']} | {c['mw']} | {c['earlier']} | {c['later']} | {c['earlier_company']} | {c['later_company']} | {c['first_copy_with_later']} |"
        for c in f3["largest_transfers"]
    ]
    L += ["", "## 4. Charges", "", "| dimension \\| class | rows | MW |", "|---|---|---|"]
    L += [f"| {k} | {v['rows']} | {v['mw']} |" for k, v in f4["by_class"].items()]
    L += [
        "",
        f"{f4['distinct_chargees']} distinct chargee names; most frequent: "
        + ", ".join(f"{n} ({c})" for n, c in f4["most_frequent_chargees"])
        + ".",
        "",
        "## What this never claims",
        "",
        "See the declaration. Nothing here is published; PSC names are not in any evidence file.",
        "",
    ]
    return "\n".join(L)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--phase",
        required=True,
        choices=["names", "history", "acquire", "acquire-amendment-1", "schema", "compute"],
    )
    parser.add_argument("--seal", default=None)
    parser.add_argument("--amendment-seal", default=None)
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    EVIDENCE.mkdir(exist_ok=True)
    if args.phase == "names":
        phase_names()
    elif args.phase == "history":
        phase_history()
    elif args.phase == "acquire":
        phase_acquire(args.seal, args.run_date)
    elif args.phase == "acquire-amendment-1":
        phase_acquire_amended(args.seal, args.amendment_seal, args.run_date)
    elif args.phase == "schema":
        phase_schema(args.run_date)
    else:
        phase_compute(args.run_date)


if __name__ == "__main__":
    main()
