"""009 step B — pinned Companies House acquisition and evaluation, under DECLARATION.md.

Order is fixed: search → advanced search / candidate profiles → resolution for
every arm → filing histories for every resolved company → only then states.
Requires COMPANIES_HOUSE_API_KEY. Every response is journalled under
data/raw/companies-house/<run-date>/.
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
from grid_mysteries.investigations.corporate_vitality import (
    PORTFOLIO_THRESHOLD,
    State,
    arm_shares,
    candidates,
    classify,
    resolve,
    test1_verdict,
    test2,
)
from grid_mysteries.investigations.tec_slippage import normalise
from grid_mysteries.sources.companies_house import (
    AuthenticatedFetcher,
    advanced_search_url,
    api_key,
    filing_history_url,
    normalise_company_name,
    profile_url,
    search_url,
)
from grid_mysteries.sources.pinning import fetch_journalled, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
AS_OF_T1 = date(2026, 8, 22)
AS_OF_T2 = date(2026, 8, 25)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "blank"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    args = parser.parse_args()
    fetch_date = date.fromisoformat(args.run_date)

    cohorts = json.loads((EVIDENCE / "cohorts.json").read_text())
    arms = cohorts["arms"]
    raw = REPO_ROOT / "data/raw/companies-house" / f"{args.run_date}-009"
    journal, manifest = raw / "journal.ndjson", raw / "manifest.json"
    fetch = AuthenticatedFetcher(api_key())

    def pin(jobs):
        fetch_journalled(
            jobs,
            journal_path=journal,
            manifest_path=manifest,
            repo_root=REPO_ROOT,
            fetch=fetch,
            sleep_seconds=0,
            progress=progress,
        )

    # customer → (original name, earliest first appearance across arms)
    customers: dict[str, tuple[str, date]] = {}
    for stages in arms.values():
        for s in stages:
            first = date.fromisoformat(s.get("first_observed") or s.get("first_seen"))
            cur = customers.get(s["customer_norm"])
            if cur is None or first < cur[1]:
                customers[s["customer_norm"]] = (s["customer"], first)
    print(f"{len(customers)} distinct customer names", flush=True)

    # Phase 1 — primary search
    pin(
        [
            ("ch-search", search_url(name), raw / "search" / f"{slug(norm)}.json")
            for norm, (name, _) in customers.items()
        ]
    )
    primary = {
        norm: load_json(raw / "search" / f"{slug(norm)}.json").get("items", [])
        for norm in customers
    }

    # Phase 2 — advanced search where no exact title; profiles for candidates
    need_adv = [
        norm
        for norm, hits in primary.items()
        if not any(
            normalise_company_name(h.get("title")) == normalise_company_name(customers[norm][0])
            for h in hits
        )
    ]
    pin(
        [
            (
                "ch-advanced-search",
                advanced_search_url(customers[norm][0]),
                raw / "advanced" / f"{slug(norm)}.json",
            )
            for norm in need_adv
        ]
    )
    advanced = {
        norm: load_json(raw / "advanced" / f"{slug(norm)}.json").get("items", [])
        for norm in need_adv
    }
    profile_numbers: set[str] = set()
    for norm in customers:
        target = normalise_company_name(customers[norm][0])
        for c in candidates(primary[norm]):
            if normalise_company_name(c.title) == target:
                profile_numbers.add(c.number)
        head = " ".join(target.split()[:2])
        for c in candidates(advanced.get(norm, [])):
            t = normalise_company_name(c.title)
            if t == target or t.startswith(head):
                profile_numbers.add(c.number)
    pin(
        [
            ("ch-profile", profile_url(n), raw / "company" / n / "profile.json")
            for n in sorted(profile_numbers)
        ]
    )
    profiles = {n: load_json(raw / "company" / n / "profile.json") for n in profile_numbers}

    # Phase 3 — resolution for every arm, before any state is read
    resolutions = {
        norm: resolve(
            customers[norm][0],
            primary[norm],
            advanced.get(norm, []),
            profiles,
            first_observed=first,
        )
        for norm, (_, first) in customers.items()
    }
    resolved_numbers = sorted({r.company_number for r in resolutions.values() if r.company_number})
    print(f"resolved {len(resolved_numbers)} of {len(customers)} names", flush=True)
    missing = [n for n in resolved_numbers if n not in profiles]
    pin([("ch-profile", profile_url(n), raw / "company" / n / "profile.json") for n in missing])
    for n in missing:
        profiles[n] = load_json(raw / "company" / n / "profile.json")

    # Phase 4 — filing histories for every resolved company (no selection on state)
    pin(
        [
            (
                "ch-filing-history",
                filing_history_url(n),
                raw / "company" / n / "filing-history.json",
            )
            for n in resolved_numbers
        ]
    )

    # Phase 5 — states
    states: dict[str, State | None] = {}
    for norm, r in resolutions.items():
        if r.company_number is None:
            states[norm] = None
            continue
        filings = load_json(raw / "company" / r.company_number / "filing-history.json").get(
            "items", []
        )
        states[norm] = classify(profiles[r.company_number], filings, fetch_date=fetch_date)

    register = list(
        csv.DictReader((REPO_ROOT / "data/raw/neso/tec_register_2026-08-22.csv").open())
    )
    counts: dict[str, int] = {}
    for x in register:
        counts[normalise(x["Customer Name"])] = counts.get(normalise(x["Customer Name"]), 0) + 1
    portfolio = {c for c, n in counts.items() if n >= PORTFOLIO_THRESHOLD}

    def split(stages):
        return [s for s in stages if s["customer_norm"] not in portfolio], [
            s for s in stages if s["customer_norm"] in portfolio
        ]

    sc_spv, sc_port = split(arms["scoping_3y"])
    bu_spv, bu_port = split(arms["built_uc"])
    shares = {
        "scoping_3y": arm_shares("Scoping >= 3y (non-portfolio)", sc_spv, states, as_of=AS_OF_T1),
        "built_uc": arm_shares("Built/UC (non-portfolio)", bu_spv, states, as_of=AS_OF_T1),
        "scoping_3y_portfolio": arm_shares(
            "Scoping >= 3y (portfolio)", sc_port, states, as_of=AS_OF_T1
        ),
        "built_uc_portfolio": arm_shares("Built/UC (portfolio)", bu_port, states, as_of=AS_OF_T1),
    }
    by_dim: dict[str, dict] = {}
    for dim in ("plant_type", "host_to"):
        groups: dict[str, list] = {}
        for s in sc_spv:
            groups.setdefault(s[dim], []).append(s)
        by_dim[dim] = {
            k: asdict(arm_shares(k, v, states, as_of=AS_OF_T1)) for k, v in groups.items()
        }
    t1 = test1_verdict(shares["scoping_3y"], shares["built_uc"])
    t2 = test2(arms["gone_scoping"], arms["control_present_scoping"], states, as_of=AS_OF_T2)
    t2_short = test2(
        arms["gone_scoping_short"], arms["control_present_scoping"], states, as_of=AS_OF_T2
    )

    tier_counts: dict[str, int] = {}
    for st in states.values():
        tier_counts[st.tier if st else "unresolved"] = (
            tier_counts.get(st.tier if st else "unresolved", 0) + 1
        )
    out = {
        "declaration": "DECLARATION.md",
        "run_date": args.run_date,
        "raw_manifest": str(manifest.relative_to(REPO_ROOT)),
        "customers": len(customers),
        "resolution_reasons": {
            r: sum(1 for x in resolutions.values() if x.reason == r)
            for r in sorted({x.reason for x in resolutions.values()})
        },
        "state_tiers_by_customer": tier_counts,
        "test1": {
            "arms": {k: asdict(v) for k, v in shares.items()},
            "verdict": asdict(t1),
            "by_dimension": by_dim,
        },
        "test2": {"scored": asdict(t2), "short_observation_unscored": asdict(t2_short)},
        "resolutions": {norm: asdict(r) for norm, r in resolutions.items()},
        "states": {norm: (asdict(st) if st else None) for norm, st in states.items()},
    }
    (EVIDENCE / "results.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    (EVIDENCE / "manifest.json").write_bytes(manifest.read_bytes())
    print(
        json.dumps(
            {
                "test1": out["test1"]["verdict"],
                "arms": {
                    k: {kk: str(vv) for kk, vv in asdict(v).items()} for k, v in shares.items()
                },
                "test2": out["test2"],
            },
            indent=1,
            default=str,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
