"""022 — the Forecast Record, issue 1: gated, journalled, idempotent runner.

    uv run python investigations/022-the-forecast-record/run.py --phase index   --seal <prefix>
    uv run python investigations/022-the-forecast-record/run.py --phase acquire --seal <prefix>
    uv run python investigations/022-the-forecast-record/run.py --phase schema
    scripts/schema-report modo-022                                  (== --phase schema)

``index`` and ``acquire`` need the sponsor's seal: a prefix (8 hex or
more) of the SHA-256 of ``ACQUISITION.md`` as frozen (proof sidecar
present and matching). ``index`` pins robots.txt and every sitemap it
names, lists every URL with its selection and reason (A1 to A3), pins the
two RNS listing pages and lists the result links they carry (A5), and
writes ``evidence/run-index.json``. ``acquire`` pins every selected page
and every listed RNS document, journalled with digests the moment each
lands; a failed fetch is recorded and skipped, never retried in the same
run. ``schema`` reads pinned bytes only and writes
``archives/modo-pages-022/`` and ``archives/rns-grid-022/``; it computes
no figure.

``compute`` and ``render`` refuse until a declaration exists that cites
the schema report by digest and is frozen; the reading rule is written
against that report, not before it.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import write_json
from grid_mysteries.sources import modo
from grid_mysteries.sources.pinning import load_journal, pin, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
PLAN = HERE / "ACQUISITION.md"
DECLARATION = HERE / "DECLARATION.md"
RUN_INDEX = EVIDENCE / "run-index.json"
ACQUISITION_LOG = EVIDENCE / "acquisition-log.json"
RAW = REPO_ROOT / "data" / "raw" / "modo" / "022"
RAW_RNS = REPO_ROOT / "data" / "raw" / "rns" / "022"
ARCHIVE_MODO = REPO_ROOT / "archives" / "modo-pages-022"
ARCHIVE_RNS = REPO_ROOT / "archives" / "rns-grid-022"
MIN_SEAL_LENGTH = 8
#: A4: the client names itself; nothing else is sent (no cookie, no key).
USER_AGENT = "grid-mysteries/022 (+https://research.a115.co.uk; public pages only)"
#: A5: the RNS listings and the anchor-text rule for the documents wanted.
INVESTEGATE = "https://www.investegate.co.uk/company"
RNS_LISTINGS: tuple[tuple[str, str], ...] = tuple(
    (
        f"rns/listing-investegate-{ticker.lower()}-page{n}",
        f"{INVESTEGATE}/{ticker}" + (f"?page={n}" if n > 1 else ""),
    )
    for ticker in ("GRID", "GSF", "HEIT")
    for n in (1, 2, 3)
) + (
    (
        "rns/listing-gresham-house",
        "https://greshamhouse.com/real-assets/energy-transition-investment/"
        "gresham-house-energy-storage-fund-plc/",
    ),
    (
        "rns/listing-gore-street",
        "https://www.gsenergystoragefund.com/investors/results-reports-and-presentations/",
    ),
)
RNS_LINK_PATTERN = r"(annual|final|full[- ]year|interim|half[- ]year(ly)?)\b.*\b(results|report)"
SLEEP_SECONDS = 0.5


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_plan_seal(seal: str | None) -> str:
    """The sponsor's seal: a prefix of the frozen plan's digest, with the
    proof sidecar present and naming the same bytes."""
    digest = sha(PLAN)
    if not seal or len(seal) < MIN_SEAL_LENGTH or not digest.startswith(seal.lower()):
        raise SystemExit(
            f"refusing: --seal must be a prefix (>= {MIN_SEAL_LENGTH} hex) of "
            f"ACQUISITION.md's SHA-256 {digest[:16]}…"
        )
    sidecar = PLAN.with_name(PLAN.name + ".timestamps.json")
    if not sidecar.exists():
        raise SystemExit("refusing: ACQUISITION.md is not frozen (no proof sidecar)")
    stamped = json.loads(sidecar.read_text()).get("sha256")
    if stamped != digest:
        raise SystemExit("refusing: ACQUISITION.md has changed since it was frozen")
    return digest


def journal(name: str) -> dict[str, Path]:
    return {
        "journal_path": EVIDENCE / f"{name}-journal.ndjson",
        "manifest_path": EVIDENCE / f"{name}-manifest.json",
    }


def fetch(*, url: str, destination: Path, dataset: str):
    """One public page, anonymous client, named user agent (A4)."""
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(
        timeout=60.0, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        destination.write_bytes(response.content)
    from grid_mysteries.hashing import sha256_file
    from grid_mysteries.models import SourceArtifact

    return SourceArtifact(
        source=modo.SOURCE if dataset.startswith("modo/") else "rns",
        dataset=dataset,
        path=destination,
        sha256=sha256_file(destination),
        fetched_at=datetime.now(UTC),
    )


def pin_each(jobs: list[tuple[str, str, Path]], name: str, label: str) -> list[dict[str, str]]:
    """Pin job by job so one refusal (403, 404, timeout) is recorded and
    the rest proceed; the journal is the same append-only file."""
    failures: list[dict[str, str]] = []
    for job in jobs:
        try:
            pin(
                [job],
                **journal(name),
                fetch=fetch,
                label=None,
                sleep_seconds=SLEEP_SECONDS,
                progress=progress,
            )
        except httpx.HTTPError as exc:
            failures.append(
                {"dataset": job[0], "url": job[1], "error": f"{type(exc).__name__}: {exc}"[:300]}
            )
            print(f"failed {job[1]}: {type(exc).__name__}", flush=True)
    pinned = len(jobs) - len(failures)
    print(f"{label}: {pinned} pinned or verified, {len(failures)} failed", flush=True)
    return failures


def log_acquisition(phase: str, digest: str, seal: str, **facts: Any) -> None:
    log = (
        json.loads(ACQUISITION_LOG.read_text())
        if ACQUISITION_LOG.exists()
        else {"acquisitions": []}
    )
    log["acquisitions"].append(
        {
            "phase": phase,
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "plan_sha256": digest,
            "seal": seal,
            **facts,
        }
    )
    write_json(ACQUISITION_LOG, log)


# ------------------------------------------------------------------ index


def index(seal: str | None, run_date: str) -> None:
    digest = require_plan_seal(seal)
    day = RAW / run_date
    failures = pin_each(
        [("modo/robots", modo.ROBOTS_URL, day / "robots.txt")], "discovery", "robots"
    )
    sitemap_urls = (
        modo.sitemaps_in_robots((day / "robots.txt").read_text(errors="replace"))
        if (day / "robots.txt").exists()
        else []
    )
    fallback = not sitemap_urls
    if fallback:
        sitemap_urls = [modo.FALLBACK_SITEMAP_URL]
    sitemaps: list[dict[str, Any]] = []
    entries: list[modo.SitemapEntry] = []
    queue = list(sitemap_urls)
    seen: set[str] = set()
    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        dest = day / "sitemaps" / modo.page_filename(url).replace(".html", ".xml")
        failures += pin_each([("modo/sitemap", url, dest)], "discovery", f"sitemap {url}")
        if not dest.exists():
            continue
        try:
            parsed = modo.parse_sitemap(dest.read_bytes())
        except Exception as exc:  # noqa: BLE001 - the shape of a foreign file is recorded, not guessed
            sitemaps.append(
                {
                    "url": url,
                    "path": str(dest.relative_to(REPO_ROOT)),
                    "kind": "unparseable",
                    "error": str(exc)[:200],
                }
            )
            continue
        sitemaps.append(
            {
                "url": url,
                "path": str(dest.relative_to(REPO_ROOT)),
                "sha256": sha(dest),
                "kind": parsed.kind,
                "entries": len(parsed.entries),
            }
        )
        if parsed.kind == "index":
            queue += [e.loc for e in parsed.entries]
        elif parsed.kind == "urlset":
            entries += list(parsed.entries)
    selection = modo.select(entries)
    disallowed = modo.disallowed_prefixes(
        (day / "robots.txt").read_text(errors="replace") if (day / "robots.txt").exists() else ""
    )
    selection = [
        modo.Selection(s.loc, s.lastmod, False, "not fetched: disallowed by robots.txt")
        if s.selected and modo.is_disallowed(s.loc, disallowed)
        else s
        for s in selection
    ]
    # A5: the RNS listings and the links they carry.
    listings = []
    rns_links: list[dict[str, str]] = []
    for dataset, url in RNS_LISTINGS:
        dest = day / "rns-listings" / (dataset.split("/", 1)[1] + ".html")
        failures += pin_each([(dataset, url, dest)], "discovery", dataset)
        if not dest.exists():
            listings.append({"dataset": dataset, "url": url, "pinned": False})
            continue
        found = modo.links(dest.read_text(errors="replace"), url, RNS_LINK_PATTERN)
        listings.append(
            {
                "dataset": dataset,
                "url": url,
                "pinned": True,
                "sha256": sha(dest),
                "links": len(found),
            }
        )
        rns_links += [{"listing": dataset, "href": href, "text": text} for href, text in found]
    reasons = Counter(s.reason for s in selection)
    write_json(
        RUN_INDEX,
        {
            "investigation": "022",
            "plan": PLAN.name,
            "plan_sha256": digest,
            "seal": seal,
            "run_date": run_date,
            "indexed_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "robots_sitemaps": sitemap_urls,
            "robots_disallowed_prefixes": disallowed,
            "fallback_sitemap_used": fallback,
            "sitemaps": sitemaps,
            "selection_tokens": list(modo.SELECTION_TOKENS),
            "urls_listed": len(selection),
            "urls_selected": sum(1 for s in selection if s.selected),
            "reasons": dict(reasons.most_common()),
            "urls": [asdict(s) for s in selection],
            "rns_listings": listings,
            "rns_link_pattern": RNS_LINK_PATTERN,
            "rns_links": rns_links,
            "failures": failures,
        },
    )
    selected = sum(1 for s in selection if s.selected)
    blocked = sum(1 for s in selection if s.reason.startswith("not fetched: disallowed"))
    log_acquisition(
        "index",
        digest,
        seal or "",
        urls_listed=len(selection),
        urls_selected=selected,
        urls_disallowed=blocked,
        rns_links=len(rns_links),
        failures=len(failures),
    )
    print(
        f"index: {len(selection)} URLs listed, {selected} selected, {blocked} disallowed "
        f"({dict(reasons)}); {len(rns_links)} RNS links; written {RUN_INDEX.relative_to(REPO_ROOT)}"
    )
    if blocked and not selected:
        print(
            "A6: every selected page is disallowed by robots.txt; issue 1 has no forecast side. "
            "Stopping after the index, as the plan says; the sponsor decides the next step."
        )


# ---------------------------------------------------------------- acquire


def acquire(seal: str | None) -> None:
    digest = require_plan_seal(seal)
    if not RUN_INDEX.exists():
        raise SystemExit("run --phase index first")
    idx = json.loads(RUN_INDEX.read_text())
    if idx["plan_sha256"] != digest:
        raise SystemExit("refusing: run-index.json was written under another plan")
    pages = [
        ("modo/page", u["loc"], RAW / "pages" / modo.page_filename(u["loc"]))
        for u in idx["urls"]
        if u["selected"]
    ]
    if not pages and any(u["reason"].startswith("not fetched: disallowed") for u in idx["urls"]):
        raise SystemExit(
            "refusing (A6): every selected page is disallowed by robots.txt; nothing is fetched "
            "under another agent or path, and the sponsor decides what comes next"
        )
    failures = pin_each(pages, "pages", "modo pages")
    docs = []
    names: set[str] = set()
    for n, link in enumerate(idx["rns_links"], start=1):
        name = f"{n:03d}-" + modo.page_filename(link["href"])
        if link["href"] in names:
            continue
        names.add(link["href"])
        docs.append(("rns/grid-document", link["href"], RAW_RNS / name))
    failures += pin_each(docs, "rns", "rns documents")
    log_acquisition(
        "acquire",
        digest,
        seal or "",
        pages=len(pages),
        rns_documents=len(docs),
        failures=len(failures),
        failed=failures,
    )
    print(
        f"acquire: {len(pages)} pages and {len(docs)} RNS documents in the jobs; "
        f"{len(failures)} failed"
    )


# ----------------------------------------------------------------- schema


def schema_pass(name: str, archive: Path, title: str, command: str) -> dict[str, Any]:
    """S1 to S5 over every journalled artefact of one journal: the report
    beside its summary, every figure-looking string as printed with its
    sentence, and the tallies. Computes no figure."""
    entries = load_journal(EVIDENCE / f"{name}-journal.ndjson")
    if not entries:
        raise SystemExit(f"refusing: nothing is journalled under {name}; run --phase acquire first")
    reports = []
    for relative, entry in sorted(entries.items()):
        path = REPO_ROOT / relative
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise SystemExit(f"refusing: {relative} no longer matches its journalled digest")
        reports.append(
            modo.page_report(url=entry["url"], path=relative, sha256=entry["sha256"], data=data)
        )
    shapes: Counter[str] = Counter()
    date_fields: Counter[str] = Counter()
    duration: Counter[str] = Counter()
    basis: Counter[str] = Counter()
    horizon: Counter[str] = Counter()
    paywall: Counter[str] = Counter()
    flags: Counter[str] = Counter()
    for r in reports:
        shapes.update(r.figure_shapes)
        date_fields.update(r.dates.keys())
        duration.update(r.duration)
        basis.update(r.basis)
        horizon.update(r.horizon)
        paywall.update({k: 1 for k in r.paywall})
        flags.update(r.flags)
    report = {
        "archive": name,
        "title": title,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "pages": len(reports),
        "figure_strings": sum(len(r.figures) for r in reports),
        "pages_with_a_figure_string": sum(1 for r in reports if r.figures),
        "figure_shapes": dict(shapes.most_common()),
        "date_fields_present_on_pages": dict(date_fields.most_common()),
        "duration_tokens": dict(duration.most_common()),
        "basis_tokens": dict(basis.most_common()),
        "horizon_tokens": dict(horizon.most_common()),
        "pages_with_paywall_token": dict(paywall.most_common()),
        "flags": dict(flags.most_common()),
        "per_page": [asdict(r) for r in reports],
    }
    archive.mkdir(parents=True, exist_ok=True)
    write_json(archive / "schema-report.json", report)
    lines = [
        f"# Schema report: {title}",
        "",
        f"Regenerated by `{command}`; `schema-report.json` beside this file has every page and "
        f"every figure-looking string with the sentence around it. {len(reports)} pages read from "
        "the journalled bytes after each digest was checked. Every number is the string it was "
        "printed as; no value is parsed and no figure is computed.",
        "",
        "## Figure-looking strings, by spelling (digits as 9)",
        "",
        "| spelling | occurrences |",
        "|---|---|",
    ]
    lines += [f"| `{k}` | {v:,} |" for k, v in shapes.most_common()] or ["| none | 0 |"]
    for heading, counter, unit in (
        ("Date fields the pages declare about themselves", date_fields, "pages"),
        ("Duration tokens", duration, "occurrences"),
        ("Basis tokens", basis, "occurrences"),
        ("Horizon tokens", horizon, "occurrences"),
        ("Paywall-looking tokens", paywall, "pages"),
        ("Flags", flags, "pages"),
    ):
        lines += ["", f"## {heading}", "", f"| token | {unit} |", "|---|---|"]
        lines += [f"| {k} | {v:,} |" for k, v in counter.most_common()] or ["| none | 0 |"]
    with_figures = [r for r in reports if r.figures]
    lines += [
        "",
        f"## Pages with at least one figure-looking string ({len(with_figures)} of {len(reports)})",
        "",
        f"Every page, including the {len(reports) - len(with_figures)} with none, is in "
        "`schema-report.json` with the same fields.",
        "",
        "| page | format | title | dates declared | figure strings | paywall tokens | flags |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in with_figures:
        dates = "; ".join(f"{k}={v[0]}" for k, v in sorted(r.dates.items())[:3])
        title_cell = (r.title or "").replace("|", "/")[:80]
        lines.append(
            f"| `{r.url}` | {r.format} | {title_cell} | {dates} | {len(r.figures)} | "
            f"{', '.join(r.paywall) or '-'} | {'; '.join(r.flags) or '-'} |"
        )
    (archive / "SCHEMA.md").write_text("\n".join(lines) + "\n")
    print(
        f"{len(reports)} pages, {report['figure_strings']} figure strings -> "
        f"{archive.relative_to(REPO_ROOT)}/"
    )
    return report


def schema() -> None:
    schema_pass(
        "pages",
        ARCHIVE_MODO,
        "Modo Energy public pages pinned by 022",
        "scripts/schema-report modo-022",
    )
    schema_pass(
        "rns",
        ARCHIVE_RNS,
        "Gresham House Energy Storage Fund RNS documents pinned by 022",
        "scripts/schema-report modo-022",
    )


def refuse_until_declared(phase: str) -> None:
    sidecar = DECLARATION.with_name(DECLARATION.name + ".timestamps.json")
    if not sidecar.exists():
        raise SystemExit(
            f"refusing ({phase}): the reading rule and the compute phase are written against the "
            "schema report and under a frozen DECLARATION.md; neither exists yet"
        )
    raise SystemExit(
        f"refusing ({phase}): not implemented until the declaration's reading rule is written"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--seal", help="prefix (>= 8 hex) of ACQUISITION.md's SHA-256 (index, acquire)"
    )
    parser.add_argument(
        "--phase", choices=("index", "acquire", "schema", "compute", "render"), required=True
    )
    parser.add_argument("--run-date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    if args.phase == "index":
        index(args.seal, args.run_date)
    elif args.phase == "acquire":
        acquire(args.seal)
    elif args.phase == "schema":
        schema()
    else:
        refuse_until_declared(args.phase)


if __name__ == "__main__":
    sys.exit(main())
