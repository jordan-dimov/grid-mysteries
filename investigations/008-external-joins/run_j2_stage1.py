"""008 · J2 stage 1 — the cheap kill, run under DECLARATION-J2-SPV-FINANCING.md.

Requires COMPANIES_HOUSE_API_KEY. Every response is pinned and journalled
under data/raw/companies-house/<run-date>/ before any number is computed.
Pass --all-plant-types only if the declaration has been amended to widen
the cohort (the sealed text says storage; storage arms are below n >= 40).
"""

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.investigations.spv_financing import (
    ChargeFacts,
    arms,
    charge_facts,
    customer_of,
    portfolio_customers,
    resolve,
    stage1_verdict,
    summarise_arm,
)
from grid_mysteries.sources.companies_house import (
    AuthenticatedFetcher,
    api_key,
    charges_url,
    profile_url,
    search_url,
)
from grid_mysteries.sources.pinning import fetch_journalled, progress

METRICS = REPO_ROOT / "data/derived/tec-history/project-metrics.csv"
EVIDENCE = Path(__file__).parent / "evidence"


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-plant-types", action="store_true")
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()

    rows = list(csv.DictReader(METRICS.open()))
    built, scoping = arms(rows, storage_only=not args.all_plant_types)
    portfolio = portfolio_customers(rows)
    print(f"built arm {len(built)}, scoping arm {len(scoping)}", flush=True)

    raw = REPO_ROOT / "data/raw/companies-house" / args.run_date
    journal = raw / "journal.ndjson"
    manifest = raw / "manifest.json"
    fetch = AuthenticatedFetcher(api_key())

    customers = sorted({customer_of(r["key"]) for r in built + scoping})
    search_jobs = [
        ("companies-house-search", search_url(c), raw / "search" / f"{slug(c)}.json")
        for c in customers
    ]
    fetch_journalled(
        search_jobs,
        journal_path=journal,
        manifest_path=manifest,
        repo_root=REPO_ROOT,
        fetch=fetch,
        sleep_seconds=0,
        progress=progress,
    )

    resolutions = {}
    for c, (_, _, dest) in zip(customers, search_jobs, strict=True):
        hits = json.loads(dest.read_text()).get("items", [])
        resolutions[c] = resolve(c, hits)
    numbers = sorted({r.company_number for r in resolutions.values() if r.company_number})
    company_jobs = []
    for n in numbers:
        company_jobs.append(
            ("companies-house-profile", profile_url(n), raw / "company" / n / "profile.json")
        )
        company_jobs.append(
            ("companies-house-charges", charges_url(n), raw / "company" / n / "charges.json")
        )
    fetch_journalled(
        company_jobs,
        journal_path=journal,
        manifest_path=manifest,
        repo_root=REPO_ROOT,
        fetch=fetch,
        sleep_seconds=0,
        progress=progress,
    )

    def facts_for(projects):
        out: dict[str, ChargeFacts | None] = {}
        for p in projects:
            c = customer_of(p["key"])
            n = resolutions[c].company_number
            if n is None:
                out[c] = None
                continue
            profile = json.loads((raw / "company" / n / "profile.json").read_text())
            charges = json.loads((raw / "company" / n / "charges.json").read_text())
            out[c] = charge_facts(
                n,
                profile,
                charges,
                first_observed=date.fromisoformat(p["first_observed"]),
                last_observed=date.fromisoformat(p["last_observed"]),
            )
        return out

    def split(projects):
        return (
            [p for p in projects if customer_of(p["key"]) not in portfolio],
            [p for p in projects if customer_of(p["key"]) in portfolio],
        )

    built_spv, built_port = split(built)
    scop_spv, scop_port = split(scoping)
    summaries = {
        "built_spv": summarise_arm("built (non-portfolio)", built_spv, facts_for(built_spv)),
        "scoping_spv": summarise_arm("scoping (non-portfolio)", scop_spv, facts_for(scop_spv)),
        "built_portfolio": summarise_arm(
            "built (portfolio customers)", built_port, facts_for(built_port)
        ),
        "scoping_portfolio": summarise_arm(
            "scoping (portfolio customers)", scop_port, facts_for(scop_port)
        ),
    }
    verdict = stage1_verdict(summaries["built_spv"], summaries["scoping_spv"])

    EVIDENCE.mkdir(exist_ok=True)
    out = {
        "declaration": "DECLARATION-J2-SPV-FINANCING.md",
        "run_date": args.run_date,
        "cohort": "all plant types" if args.all_plant_types else "storage only (as sealed)",
        "raw_manifest": str(manifest.relative_to(REPO_ROOT)),
        "arms": {k: asdict(v) for k, v in summaries.items()},
        "verdict": asdict(verdict),
        "resolutions": {c: asdict(r) for c, r in resolutions.items()},
    }
    (EVIDENCE / "j2-stage1.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(out["arms"], indent=1, default=str))
    print(out["verdict"])


if __name__ == "__main__":
    sys.exit(main())
