"""007 T3 (skip persistence by unit) on NESO's in-merit stack files.

Monthly skip share per (bm_unit, direction) = sum(skipped) / sum(in_merit);
conditional top-quartile persistence May -> July, July -> August (earlier
August vintage). No model, no score.
"""

import json
from decimal import Decimal
from pathlib import Path

import polars as pl

from grid_mysteries.evidence import evidence_dir, write_json
from grid_mysteries.stats import spearman

ROOT = Path(__file__).resolve().parents[2]
NESO = ROOT / "data/raw/neso"
EVIDENCE = evidence_dir(__file__)
FILES = {
    "may": "inmerit_allbm_2026-05.csv",
    "jul": "inmerit_allbm_2026-07.csv",
    "aug": "inmerit_allbm_2026-08.csv",
}


def shares(name: str) -> pl.DataFrame:
    df = pl.scan_csv(NESO / name, infer_schema_length=10000)
    return (
        df.group_by(["bm_unit", "bid_offer", "fuel"])
        .agg(
            pl.col("in_merit_volume_MWh").sum().alias("in_merit"),
            pl.col("skipped_volume_MWh").sum().alias("skipped"),
        )
        .filter(pl.col("in_merit") > 0)
        .with_columns((pl.col("skipped") / pl.col("in_merit")).alias("share"))
        .collect()
    )


def stage_vocabulary(name: str) -> dict:
    df = pl.scan_csv(NESO / name, infer_schema_length=10000)
    stages = df.group_by("stage").agg(pl.len().alias("rows")).collect()
    return {r["stage"]: r["rows"] for r in stages.to_dicts()}


def top_quartile_flag(df: pl.DataFrame, col: str) -> pl.DataFrame:
    ordered = df.sort([col, "in_merit"], descending=[True, True])
    k = max(1, len(ordered) // 4)
    return ordered.with_row_index("rank").with_columns((pl.col("rank") < k).alias(f"top_{col}"))


def transition(a: pl.DataFrame, b: pl.DataFrame, label: str) -> dict:
    joined = a.join(b, on=["bm_unit", "bid_offer"], suffix="_b")
    joined = joined.with_columns(
        pl.col("share").alias("share_a"), pl.col("share_b").alias("share_b")
    )
    fa = top_quartile_flag(
        joined.select(["bm_unit", "bid_offer", "fuel", "in_merit", "share_a"]).rename(
            {"share_a": "share"}
        ),
        "share",
    )
    fb = top_quartile_flag(
        joined.select(["bm_unit", "bid_offer", "in_merit_b", "share_b"]).rename(
            {"share_b": "share", "in_merit_b": "in_merit"}
        ),
        "share",
    )
    flags = (
        fa.select(["bm_unit", "bid_offer", "fuel", "top_share"])
        .rename({"top_share": "top_a"})
        .join(
            fb.select(["bm_unit", "bid_offer", "top_share"]).rename({"top_share": "top_b"}),
            on=["bm_unit", "bid_offer"],
        )
    )
    exposed = flags.filter(pl.col("top_a"))
    n_exposed = len(exposed)
    hits = int(exposed["top_b"].sum())
    cond = Decimal(hits) / Decimal(n_exposed) if n_exposed else None
    base = Decimal(int(flags["top_b"].sum())) / Decimal(len(flags)) if len(flags) else None
    by_fuel = {}
    for fuel, sub in exposed.group_by("fuel"):
        f = fuel[0] if isinstance(fuel, tuple) else fuel
        by_fuel[str(f)] = {
            "n": len(sub),
            "persist_rate": Decimal(int(sub["top_b"].sum())) / Decimal(len(sub)),
        }
    persistent = exposed.filter(pl.col("top_b"))
    largest = persistent.group_by("fuel").agg(pl.len().alias("n")).sort("n", descending=True)
    rho = (
        spearman(
            list(
                zip(
                    [Decimal(str(x)) for x in joined["share_a"].to_list()],
                    [Decimal(str(x)) for x in joined["share_b"].to_list()],
                    strict=True,
                )
            )
        )
        if len(joined) >= 3
        else None
    )
    return {
        "label": label,
        "units_in_both": len(joined),
        "exposed_n": n_exposed,
        "persisted": hits,
        "conditional": cond,
        "unconditional_top_b": base,
        "spearman": rho,
        "by_fuel": by_fuel,
        "largest_fuel_among_persistent": largest.to_dicts()[:3],
    }


def main():
    vocab = {k: stage_vocabulary(v) for k, v in FILES.items()}
    may, jul, aug = (shares(FILES[k]) for k in ("may", "jul", "aug"))
    mj = transition(may, jul, "May -> Jul")
    ja = transition(jul, aug, "Jul -> Aug (earlier Aug vintage)")
    passes = (
        mj["exposed_n"] >= 100
        and mj["conditional"] is not None
        and mj["conditional"] >= Decimal("0.5")
        and ja["conditional"] is not None
        and ja["conditional"] >= Decimal("0.5")
    )
    out = {
        "stage_vocabulary": vocab,
        "units_per_month": {"may": len(may), "jul": len(jul), "aug": len(aug)},
        "may_to_jul": mj,
        "jul_to_aug": ja,
        "passes": passes,
    }
    write_json(EVIDENCE / "t3-summary.json", out)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
