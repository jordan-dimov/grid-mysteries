"""005, Amendment 2 (2026-09-15): the declared Q1-Q3 re-run under 014's reading rules.

    uv run --group registers python \
        investigations/005-connection-date-credibility/rerun-2026-09-15.py

Same declared method as `run.py` (identity triple, (identity, stage) unit,
regime cutoff, population, Q1-Q3 thresholds from `tec_slippage`), same
archive; only the *reading* changes, to the rules 014 declared:

- every era's column names mapped (the stage MW column, unmapped in 2026-08,
  plays no part in 005's metrics and is mapped for completeness);
- every date spelling parsed (`YYYY/MM/DD`, `DD-Mon-YY`, Excel serials were
  undated in the 2026-08 run);
- copies whose dates are day-month swapped are read exchanged back;
- stage numerals unified (`1.00` is `1`);
- copies lacking an identity column are excluded rather than read with a
  blank customer.

Writes `evidence/tec-slippage-summary-2026-09-15-014-READING-RULES.json` in
the shape of `tec-slippage-summary.json`; the 2026-08-26 files are untouched.
"""

import json
from collections import Counter
from datetime import date

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, evidence_dir, write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations.tec_slippage import (
    Vintage,
    all_metrics,
    build_timelines,
    match_report,
    population,
    q1_dispersion,
    q2_predictability,
    q3_materiality,
)
from grid_mysteries.sources import tec_register as tr

EVIDENCE = evidence_dir(__file__)
REGIME_CUTOFF = date(2025, 12, 1)
REQUIRED = (
    "Project Name",
    "Customer Name",
    "Connection Site",
    "MW Increase / Decrease",
    "MW Effective From",
)


def read_under_014_rules() -> tuple[list[Vintage], list[dict], list[dict], list[str]]:
    parsed, skipped = tr.load_vintages(REPO_ROOT / tr.JOURNAL_PATH, REPO_ROOT)
    vintages: list[Vintage] = []
    excluded: list[dict] = []
    swapped: list[str] = []
    previous: dict[str, cs.Entry] | None = None
    for t, rows, entry in parsed:
        columns = {tr.canon(c) for c in (entry.get("columns") or [])}
        missing = [c for c in REQUIRED if c not in columns]
        if missing:
            excluded.append({"t_public": t.isoformat(), "missing": missing})
            continue
        current = cs.entries(rows)
        flagged = previous is not None and cs.swap_test(previous, current).flagged
        if flagged:
            swapped.append(t.isoformat())
            current = cs.entries(rows, swapped=True)
        read_rows = []
        for row in rows:
            effective = tr.parse_date(row.get("MW Effective From"))
            if flagged:
                effective = tr.swap_day_month(effective) or effective
            read_rows.append(
                {
                    **row,
                    "MW Effective From": effective,
                    "Stage": tr.normalise_stage(row.get("Stage")),
                }
            )
        vintages.append(Vintage(t, tuple(read_rows)))
        previous = current if t < REGIME_CUTOFF else None
    return vintages, skipped, excluded, swapped


def main() -> None:
    vintages, skipped, excluded, swapped = read_under_014_rules()
    old = [v for v in vintages if v.t_public < REGIME_CUTOFF]
    new = [v for v in vintages if v.t_public >= REGIME_CUTOFF]
    last_old = max(v.t_public for v in old)
    timelines = build_timelines(old, use_project_id=False)
    metrics = all_metrics(timelines, last_old)
    pop = population(metrics)
    q1, q2 = q1_dispersion(pop), q2_predictability(pop)
    q3 = q3_materiality(pop, q2)
    summary = {
        "amendment": "2 (2026-09-15): 014's reading rules; 005's declared method unchanged",
        "vintages_loaded": len(vintages),
        "vintages_old_regime": len(old),
        "vintages_new_regime": [v.t_public for v in new],
        "vintage_span": [old[0].t_public, last_old],
        "skipped_vintages": skipped,
        "excluded_vintages": excluded,
        "swapped_vintages": swapped,
        "match_report": match_report(timelines),
        "identities_total": len(metrics),
        "identities_with_2_plus_years_and_slip": len(pop),
        "disappeared_identities_old_regime": sum(1 for m in metrics if m.disappeared),
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "revisions_distribution": dict(sorted(Counter(min(m.revisions, 10) for m in pop).items())),
        "net_slip_quantiles_months": {
            q: sorted(m.net_slip_months for m in pop)[int((len(pop) - 1) * f)] if pop else None
            for q, f in (("p10", 0.1), ("p25", 0.25), ("p50", 0.5), ("p75", 0.75), ("p90", 0.9))
        },
    }
    write_json(EVIDENCE / "tec-slippage-summary-2026-09-15-014-READING-RULES.json", summary)
    before = json.loads((EVIDENCE / "tec-slippage-summary.json").read_text())
    after = json.loads(dumps(summary))

    def stratum(q2_list, name):
        r = next(x for x in q2_list if x["name"] == name)
        return r["best_ratio"], r["high"], r["low"], r["passes"]

    rows = [
        (
            "vintages loaded (old regime)",
            before["vintages_old_regime"],
            after["vintages_old_regime"],
        ),
        ("identities", before["identities_total"], after["identities_total"]),
        (
            "population",
            before["identities_with_2_plus_years_and_slip"],
            after["identities_with_2_plus_years_and_slip"],
        ),
        ("Q1 IQR (months)", before["q1"]["iqr_months"], after["q1"]["iqr_months"]),
        (
            "Q1 share slipped >= 24 m",
            before["q1"]["share_slipped_ge_24"],
            after["q1"]["share_slipped_ge_24"],
        ),
        ("Q1 share < 6 m", before["q1"]["share_lt_6"], after["q1"]["share_lt_6"]),
        ("Q1 passes", before["q1"]["passes"], after["q1"]["passes"]),
        (
            "Q2 first_status",
            stratum(before["q2"], "first_status"),
            stratum(after["q2"], "first_status"),
        ),
        (
            "Q2 initial_lead_time_band",
            stratum(before["q2"], "initial_lead_time_band"),
            stratum(after["q2"], "initial_lead_time_band"),
        ),
        ("Q2 plant_type", stratum(before["q2"], "plant_type"), stratum(after["q2"], "plant_type")),
        ("Q3 pooled rate", before["q3"]["pooled_rate"], after["q3"]["pooled_rate"]),
        (
            "Q3 materially different",
            before["q3"]["materially_different"],
            after["q3"]["materially_different"],
        ),
        ("Q3 passes", before["q3"]["passes"], after["q3"]["passes"]),
        (
            "net slip quantiles",
            before["net_slip_quantiles_months"],
            after["net_slip_quantiles_months"],
        ),
        (
            "revisions >= 10",
            before["revisions_distribution"].get("10"),
            after["revisions_distribution"].get("10"),
        ),
    ]
    for label, b, a in rows:
        print(f"{label:32s} before {b!s:60.60s} after {a!s}")
    for r in after["q2"]:
        print(
            "Q2",
            r["name"],
            "ratio",
            r["best_ratio"],
            r["high"],
            "vs",
            r["low"],
            "holds",
            r["holds_in_both_cohorts"],
            "passes",
            r["passes"],
        )
    print("q3 gaps:", [(name, s, rate) for name, s, rate in after["q3"]["materially_different"]])
    pooled = after["q3"]["pooled_rate"]
    for r in after["q2"]:
        if r["passes"]:
            for s in r["rates"]:
                if s["n"] >= 30:
                    from decimal import Decimal

                    print(
                        "  gap",
                        r["name"],
                        s["stratum"],
                        s["n"],
                        s["rate_ge_24"],
                        f"{(Decimal(s['rate_ge_24']) - Decimal(pooled)) * 100:+.1f} pp",
                    )


if __name__ == "__main__":
    main()
