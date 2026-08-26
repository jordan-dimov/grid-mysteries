"""007 T1 (slip persistence) and T2 (attrition by attribute) on the TEC archive.

Reuses 005's loader and timelines; computes only the conditional rates the
declaration froze. No model, no score.
"""

import importlib.util
import json
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from grid_mysteries.evidence import evidence_dir, write_json
from grid_mysteries.investigations.tec_slippage import (
    all_metrics,
    build_timelines,
    months_between,
    population,
)

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "run005", ROOT / "investigations/005-connection-date-credibility/run.py"
)
run005 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run005)
EVIDENCE = evidence_dir(__file__)
SLIP = 6


def revisions(timeline):
    out = []
    for a, b in zip(timeline, timeline[1:], strict=False):
        if a.effective and b.effective and b.effective != a.effective:
            out.append((b.t_public, months_between(a.effective, b.effective)))
    return out


def rate(hits, n):
    return Decimal(hits) / Decimal(n) if n else None


def t1(timelines, pop):
    exposed = Counter()
    control = Counter()
    by_cohort = {"2014-2018": [Counter(), Counter()], "2019-2024": [Counter(), Counter()]}
    for m in pop:
        tl = timelines[m.key]
        first, last = tl[0].t_public, tl[-1].t_public
        cohort = "2014-2018" if first.year <= 2018 else "2019-2024"
        revs = revisions(tl)
        slips = [(t, mo) for t, mo in revs if mo >= SLIP]
        if slips:
            t0, _ = slips[0]
            if (last - t0).days >= 730:
                again = any(
                    t0 < t <= t0 + timedelta(days=730) and mo >= SLIP for t, mo in slips[1:]
                )
                exposed["n"] += 1
                exposed["hit"] += again
                by_cohort[cohort][0]["n"] += 1
                by_cohort[cohort][0]["hit"] += again
        no_early = not any(t <= first + timedelta(days=365) for t, _ in slips)
        if no_early and (last - first).days >= 1095:
            later = any(
                first + timedelta(days=365) < t <= first + timedelta(days=1095) for t, mo in slips
            )
            control["n"] += 1
            control["hit"] += later
            by_cohort[cohort][1]["n"] += 1
            by_cohort[cohort][1]["hit"] += later
    re, rc = rate(exposed["hit"], exposed["n"]), rate(control["hit"], control["n"])
    ratio = re / rc if re is not None and rc else None
    gap = re - rc if re is not None and rc is not None else None
    cohorts = {}
    holds = True
    for name, (e, c) in by_cohort.items():
        ce, cc = rate(e["hit"], e["n"]), rate(c["hit"], c["n"])
        cohorts[name] = {
            "exposed_n": e["n"],
            "exposed_rate": ce,
            "control_n": c["n"],
            "control_rate": cc,
        }
        holds = holds and ce is not None and cc is not None and ce > cc
    passes = (
        exposed["n"] >= 100
        and control["n"] >= 100
        and ratio is not None
        and ratio >= Decimal("1.5")
        and gap is not None
        and gap >= Decimal("0.15")
        and holds
    )
    return {
        "exposed_n": exposed["n"],
        "exposed_rate": re,
        "control_n": control["n"],
        "control_rate": rc,
        "ratio": ratio,
        "gap": gap,
        "cohorts": cohorts,
        "direction_holds_both_cohorts": holds,
        "passes": passes,
    }


EXPOSURES = {
    "first_status": lambda m: m.first_status or "unknown",
    "plant_type": lambda m: m.plant_type or "unknown",
    "capacity_band": lambda m: m.capacity_band,
    "initial_lead_time_band": lambda m: m.initial_lead_time_band,
}


def attrition_table(metrics, final, min_age_days=365, censor_days=180):
    eligible = [m for m in metrics if (final - m.first_observed).days >= min_age_days]
    table = {}
    for name, key in EXPOSURES.items():
        counts, hits = Counter(), Counter()
        for m in eligible:
            s = key(m)
            counts[s] += 1
            hits[s] += (final - m.last_observed).days >= censor_days
        table[name] = {s: {"n": counts[s], "rate": rate(hits[s], counts[s])} for s in counts}
    return len(eligible), table


def passing_pairs(table, min_n):
    pairs = []
    for name, strata in table.items():
        big = {s: v for s, v in strata.items() if v["n"] >= min_n and v["rate"] is not None}
        for a, va in big.items():
            for b, vb in big.items():
                if (
                    vb["rate"]
                    and va["rate"] / vb["rate"] >= 2
                    and va["rate"] - vb["rate"] >= Decimal("0.15")
                ):
                    pairs.append(
                        {
                            "exposure": name,
                            "high": a,
                            "high_rate": va["rate"],
                            "high_n": va["n"],
                            "low": b,
                            "low_rate": vb["rate"],
                            "low_n": vb["n"],
                            "ratio": va["rate"] / vb["rate"],
                        }
                    )
    return pairs


def t2(metrics, final, old_vintages):
    n_elig, table = attrition_table(metrics, final)
    pairs = passing_pairs(table, 50)
    # robustness: Project-ID-keyed window 2024-06-14 .. 2025-07-22
    window = [v for v in old_vintages if date(2024, 6, 14) <= v.t_public <= final]
    id_metrics = all_metrics(build_timelines(window, use_project_id=True), final)
    id_metrics = [m for m in id_metrics if m.key.startswith("id:")]
    n_id, id_table = attrition_table(id_metrics, final, min_age_days=365)
    confirmed = []
    for p in pairs:
        strata = id_table.get(p["exposure"], {})
        a, b = strata.get(p["high"]), strata.get(p["low"])
        ok = (
            a
            and b
            and a["n"] >= 30
            and b["n"] >= 30
            and a["rate"] is not None
            and b["rate"] is not None
            and a["rate"] > b["rate"]
        )
        confirmed.append({**p, "id_window_high": a, "id_window_low": b, "confirmed": bool(ok)})
    return {
        "eligible_name_keyed": n_elig,
        "table_name_keyed": table,
        "eligible_id_keyed_window": n_id,
        "table_id_keyed_window": id_table,
        "candidate_pairs": confirmed,
        "passes": any(c["confirmed"] for c in confirmed),
    }


def main():
    vintages, _ = run005.load_vintages()
    old = [v for v in vintages if v.t_public < run005.REGIME_CUTOFF]
    final = max(v.t_public for v in old)
    timelines = build_timelines(old, use_project_id=False)
    metrics = all_metrics(timelines, final)
    pop = population(metrics)
    out = {
        "final_vintage": final,
        "population_t1": len(pop),
        "t1": t1(timelines, pop),
        "t2": t2(metrics, final, old),
    }
    write_json(EVIDENCE / "t1-t2-summary.json", out)
    print(
        json.dumps(
            {
                "t1": out["t1"],
                "t2_passes": out["t2"]["passes"],
                "t2_pairs": out["t2"]["candidate_pairs"],
            },
            indent=1,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
