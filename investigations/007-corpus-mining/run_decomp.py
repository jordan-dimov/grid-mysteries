"""007 T3 decomposition: is persistent BM skipping locational or commercial?

Runs DECLARATION-T3-DECOMPOSITION.md. Skipped volume is decomposed along
NESO's own stage chain (stage 0 raw -> stage 5 residual); the Exclusion
Reasons file only labels the stages. No model, no score, no GBP figure.
"""

import sys
from decimal import Decimal
from pathlib import Path

import polars as pl

from grid_mysteries.evidence import evidence_dir, write_json
from grid_mysteries.stats import spearman

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_skip import FILES, NESO, top_quartile_flag  # noqa: E402

EVIDENCE = evidence_dir(__file__)
KEY = ["date", "bm_unit", "bid_offer", "pair_id"]
FAMILIES = {"S": ["drop_2", "drop_3"], "U": ["drop_4"], "T": ["drop_1", "drop_5"]}


def dec(x: float | None) -> Decimal | None:
    return None if x is None else Decimal(str(round(x, 6)))


def stage_table(name: str) -> pl.DataFrame:
    df = pl.scan_csv(NESO / name, infer_schema_length=10000)
    rows = df.select(KEY + ["fuel", "stage", "skipped_volume_MWh", "in_merit_volume_MWh"]).collect()
    skipped = rows.pivot(
        on="stage", index=KEY + ["fuel"], values="skipped_volume_MWh", aggregate_function="sum"
    ).with_columns(pl.col([str(s) for s in range(6)]).fill_null(0.0))
    in_merit0 = (
        rows.filter(pl.col("stage") == 0)
        .group_by(KEY)
        .agg(pl.col("in_merit_volume_MWh").sum().alias("in_merit"))
    )
    per_pair = skipped.join(in_merit0, on=KEY, how="left").with_columns(
        pl.col("in_merit").fill_null(0.0)
    )
    per_pair = per_pair.with_columns(
        [
            (pl.col(str(s - 1)) - pl.col(str(s))).clip(lower_bound=0.0).alias(f"drop_{s}")
            for s in range(1, 6)
        ]
        + [(pl.col(str(s - 1)) - pl.col(str(s))).alias(f"drop_{s}u") for s in (2, 3)]
    ).rename({"0": "raw", "5": "residual"})
    unit = (
        per_pair.group_by(["bm_unit", "bid_offer", "fuel"])
        .agg(
            pl.col("in_merit").sum(),
            pl.col("raw").sum(),
            pl.col("residual").sum(),
            *[pl.col(f"drop_{s}").sum() for s in range(1, 6)],
            pl.col("drop_2u").sum(),
            pl.col("drop_3u").sum(),
        )
        .filter(pl.col("in_merit") > 0)
    )
    for fam, cols in FAMILIES.items():
        unit = unit.with_columns(sum(pl.col(c) for c in cols).alias(fam))
    return unit.with_columns(
        pl.col("residual").alias("R"),
        (pl.col("raw") / pl.col("in_merit")).alias("share_raw"),
        (pl.col("residual") / pl.col("in_merit")).alias("share_resid"),
        (pl.col("S") / pl.col("in_merit")).alias("share_S"),
    )


def flag(df: pl.DataFrame, share_col: str, out: str) -> pl.DataFrame:
    flagged = top_quartile_flag(
        df.select(["bm_unit", "bid_offer", "in_merit", share_col]).rename({share_col: "share"}),
        "share",
    )
    return flagged.select(["bm_unit", "bid_offer", "top_share"]).rename({"top_share": out})


def volume_shares(df: pl.DataFrame, suffix: str) -> dict:
    raw = float(df[f"raw{suffix}"].sum())
    out = {}
    for fam in ("S", "U", "T", "R"):
        vol = float(df[f"{fam}{suffix}"].sum())
        out[fam] = {"mwh": round(vol), "share_of_raw": dec(vol / raw) if raw else None}
    out["raw_mwh"] = round(raw)
    out["unit_median_share"] = {
        fam: dec(float((df[f"{fam}{suffix}"] / df[f"raw{suffix}"]).median()))
        for fam in ("S", "U", "T", "R")
    }
    return out


def majority_groups(exposed: pl.DataFrame) -> dict:
    out = {}
    for fam in ("S", "R", "T", "U"):
        grp = exposed.filter((pl.col(fam) / pl.col("raw")) >= 0.5)
        out[fam] = {
            "n": len(grp),
            "persist_rate": dec(float(grp["top_raw_b"].mean())) if len(grp) else None,
        }
    return out


def transition(a: pl.DataFrame, b: pl.DataFrame, label: str) -> dict:
    j = a.join(b, on=["bm_unit", "bid_offer"], suffix="_b")
    fa = flag(a, "share_raw", "top_raw_a")
    fb = flag(b, "share_raw", "top_raw_b")
    ra = flag(a, "share_resid", "top_resid_a")
    rb = flag(b, "share_resid", "top_resid_b")
    for f in (fa, fb, ra, rb):
        j = j.join(f, on=["bm_unit", "bid_offer"], how="left")
    j = j.filter(pl.col("top_raw_a").is_not_null() & pl.col("top_raw_b").is_not_null())

    exposed = j.filter(pl.col("top_raw_a"))
    persistent = exposed.filter(pl.col("top_raw_b"))
    groups = majority_groups(exposed)
    a1_gap = (
        groups["S"]["persist_rate"] - groups["R"]["persist_rate"]
        if groups["S"]["persist_rate"] is not None and groups["R"]["persist_rate"] is not None
        else None
    )
    exp_resid = j.filter(pl.col("top_resid_a"))
    b1_cond = dec(float(exp_resid["top_resid_b"].mean())) if len(exp_resid) else None
    b1_base = dec(float(j["top_resid_b"].mean()))
    fuel_mix = (
        persistent.group_by("fuel").agg(pl.len().alias("n")).sort("n", descending=True).to_dicts()
    )
    s_persist_fuel = (
        persistent.filter((pl.col("S") / pl.col("raw")) >= 0.5)
        .group_by("fuel")
        .agg(pl.len().alias("n"))
        .sort("n", descending=True)
        .to_dicts()
    )
    return {
        "label": label,
        "units_in_both": len(j),
        "raw_top_quartile": {
            "exposed_n": len(exposed),
            "persisted": len(persistent),
            "conditional": dec(float(exposed["top_raw_b"].mean())),
            "unconditional": dec(float(j["top_raw_b"].mean())),
        },
        "A1_majority_groups_month1": groups,
        "A1_gap_S_minus_R_pp": dec(float(a1_gap) * 100) if a1_gap is not None else None,
        "A2_B2_persistent_set": {
            "n": len(persistent),
            "month_1": volume_shares(persistent, ""),
            "month_2": volume_shares(persistent, "_b"),
            "fuel_mix_top5": fuel_mix[:5],
            "S_majority_persistent_fuel_top5": s_persist_fuel[:5],
        },
        "B1_residual_top_quartile": {
            "exposed_n": len(exp_resid),
            "persisted": int(exp_resid["top_resid_b"].sum()),
            "conditional": b1_cond,
            "unconditional": b1_base,
            "spearman_share_resid": spearman(
                list(
                    zip(
                        [Decimal(str(x)) for x in j["share_resid"].to_list()],
                        [Decimal(str(x)) for x in j["share_resid_b"].to_list()],
                        strict=True,
                    )
                )
            ),
        },
        "spearman_share_S": spearman(
            list(
                zip(
                    [Decimal(str(x)) for x in j["share_S"].to_list()],
                    [Decimal(str(x)) for x in j["share_S_b"].to_list()],
                    strict=True,
                )
            )
        ),
    }


def verdict(t: list[dict]) -> dict:
    a1 = all(
        r["A1_majority_groups_month1"]["S"]["n"] >= 30
        and r["A1_majority_groups_month1"]["R"]["n"] >= 30
        and r["A1_gap_S_minus_R_pp"] is not None
        and r["A1_gap_S_minus_R_pp"] >= 15
        for r in t
    )
    a2 = all(
        r["A2_B2_persistent_set"][m]["S"]["share_of_raw"] is not None
        and r["A2_B2_persistent_set"][m]["S"]["share_of_raw"] >= Decimal("0.5")
        for r in t
        for m in ("month_1", "month_2")
    )
    b1 = all(
        r["B1_residual_top_quartile"]["exposed_n"] >= 100
        and r["B1_residual_top_quartile"]["conditional"] is not None
        and r["B1_residual_top_quartile"]["conditional"] >= Decimal("0.5")
        for r in t
    )
    b2 = all(
        r["A2_B2_persistent_set"][m]["R"]["share_of_raw"] is not None
        and r["A2_B2_persistent_set"][m]["R"]["share_of_raw"] >= Decimal("0.25")
        for r in t
        for m in ("month_1", "month_2")
    )
    return {"A1": a1, "A2": a2, "A": a1 and a2, "B1": b1, "B2": b2, "B": b1 and b2}


def sensitivity(a: pl.DataFrame, b: pl.DataFrame, label: str) -> dict:
    """POST-HOC, not part of the frozen test. Written after the first run showed
    (i) wind units enter the persistent set through the stage-1 "Wind offer"
    exclusion by definition and (ii) zero-clipped stage drops over-attribute.
    Reports the persistent set without wind, with unclipped drops."""
    j = a.join(b, on=["bm_unit", "bid_offer"], suffix="_b")
    j = j.join(flag(a, "share_raw", "ta"), on=["bm_unit", "bid_offer"]).join(
        flag(b, "share_raw", "tb"), on=["bm_unit", "bid_offer"]
    )
    persistent = j.filter(pl.col("ta") & pl.col("tb"))
    wind = persistent.filter(pl.col("fuel") == "WIND")
    non_wind = persistent.filter(pl.col("fuel") != "WIND")
    out: dict = {"label": label, "persistent_n": len(persistent), "wind_n": len(wind)}
    for suffix, month in (("", "month_1"), ("_b", "month_2")):
        raw = float(non_wind[f"raw{suffix}"].sum())
        unclipped_s = float((non_wind[f"drop_2u{suffix}"] + non_wind[f"drop_3u{suffix}"]).sum())
        out[month] = {
            "non_wind_n": len(non_wind),
            "non_wind_raw_mwh": round(raw),
            "non_wind_S_share_unclipped": dec(unclipped_s / raw) if raw else None,
            "non_wind_R_share": dec(float(non_wind[f"R{suffix}"].sum()) / raw) if raw else None,
            "non_wind_units_S_majority": int(
                ((non_wind[f"S{suffix}"] / non_wind[f"raw{suffix}"]) >= 0.5).sum()
            ),
            "non_wind_units_R_ge_25pct": int(
                ((non_wind[f"R{suffix}"] / non_wind[f"raw{suffix}"]) >= 0.25).sum()
            ),
            "wind_raw_mwh": round(float(wind[f"raw{suffix}"].sum())),
            "wind_stage1_share": dec(
                float(wind[f"drop_1{suffix}"].sum()) / float(wind[f"raw{suffix}"].sum())
            )
            if len(wind) and float(wind[f"raw{suffix}"].sum())
            else None,
        }
    exposed = j.filter(pl.col("ta") & (pl.col("fuel") != "WIND"))
    s_maj = exposed.filter((pl.col("S") / pl.col("raw")) >= 0.5)
    other = exposed.filter((pl.col("S") / pl.col("raw")) < 0.5)
    out["non_wind_exposed"] = {
        "n": len(exposed),
        "persist_rate": dec(float(exposed["tb"].mean())) if len(exposed) else None,
        "S_majority": {
            "n": len(s_maj),
            "persist_rate": dec(float(s_maj["tb"].mean())) if len(s_maj) else None,
        },
        "not_S_majority": {
            "n": len(other),
            "persist_rate": dec(float(other["tb"].mean())) if len(other) else None,
        },
    }
    return out


def main() -> None:
    may, jul, aug = (stage_table(FILES[k]) for k in ("may", "jul", "aug"))
    totals = {
        k: {
            "raw_mwh": round(float(d["raw"].sum())),
            "residual_mwh": round(float(d["residual"].sum())),
            **{f: round(float(d[f].sum())) for f in ("S", "U", "T")},
        }
        for k, d in (("may", may), ("jul", jul), ("aug", aug))
    }
    t = [transition(may, jul, "may->jul"), transition(jul, aug, "jul->aug")]
    out = {
        "declaration": "DECLARATION-T3-DECOMPOSITION.md",
        "system_totals": totals,
        "transitions": t,
        "verdict": verdict(t),
    }
    write_json(EVIDENCE / "t3-decomposition.json", out)
    write_json(
        EVIDENCE / "t3-decomposition-sensitivity.json",
        {
            "status": "post-hoc sensitivity, not part of the frozen test",
            "transitions": [sensitivity(may, jul, "may->jul"), sensitivity(jul, aug, "jul->aug")],
        },
    )
    for r in t:
        print(r["label"], "units", r["units_in_both"])
        print("  raw top-q persistence", r["raw_top_quartile"])
        print("  A1 groups", r["A1_majority_groups_month1"], "gap pp", r["A1_gap_S_minus_R_pp"])
        p = r["A2_B2_persistent_set"]
        for m in ("month_1", "month_2"):
            print(
                f"  P {m}: raw {p[m]['raw_mwh']} MWh;",
                {f: (p[m][f]["mwh"], str(p[m][f]["share_of_raw"])) for f in "SUTR"},
                "median",
                {f: str(v) for f, v in p[m]["unit_median_share"].items()},
            )
        print("  P fuel", p["fuel_mix_top5"])
        print("  S-majority persistent fuel", p["S_majority_persistent_fuel_top5"])
        print("  B1", r["B1_residual_top_quartile"], "| rho S", r["spearman_share_S"])
    print("system totals", totals)
    print("verdict", out["verdict"])


if __name__ == "__main__":
    main()
