"""018 — RESULTS.md as a pure function of the committed results.

The declaration fixes the order: the verdicts first (C4 before anything, as
F5 would be published first), then the context: the SERIES by month, the
largest parties per window, charged against paid, names under R6. Parties
are printed by BSC Party Id; a name is added only from the BM unit register
pinned at acquisition, labelled as that register's. Every H1 and H2 verdict
carries its provisional status in the same line when H3 holds. Nothing here
says why a figure moved: a difference is reported as a difference.
"""

from collections import defaultdict
from decimal import Decimal
from typing import Any

D = Decimal


def pounds(v: Any) -> str:
    x = D(v)
    return f"−£{-x:,.0f}" if x < 0 else f"£{x:,.0f}"


def mwh(v: Any) -> str:
    return f"{D(v):,.1f} MWh"


def share(v: Any) -> str:
    """A share as a percentage; one too small for a tenth is printed so that
    its sign and size are not hidden behind 0.0."""
    p = D(v) * 100
    return f"{p:.1f} %" if abs(p) >= D("0.05") or p == 0 else f"{p:.4f} %"


def ratio(v: Any) -> str:
    return f"{D(v):.2f}"


def party(pid: str, names: dict[str, str]) -> str:
    name = names.get(pid)
    return f"`{pid}` ({name})" if name else f"`{pid}`"


MEASURES = {
    "supplier_cash_total": "paid",
    "supplier_volume_total": "supplier compensation volume",
    "vtp_volume_total": "VTP volume",
    "charged_total": "charged",
}
WINDOW_WORDS = {
    "FEB": "FEB (February 2026 less 17/02)",
    "PRE": "PRE (10 to 23 August 2026)",
    "POST": "POST (24 August to 6 September 2026 less 28/08)",
    "SERIES": "SERIES (Wednesdays, 3 September 2025 to 19 August 2026)",
}


def _measure_value(measure: str, v: Any) -> str:
    return pounds(v) if measure in ("supplier_cash_total", "charged_total") else mwh(v)


def render_results(r: dict[str, Any], names: dict[str, str], record: dict[str, str]) -> str:
    h, c4, ctx = r["hypotheses"], r["C4"], r["context"]
    provisional = h["H3"]["verdict"] == "holds"
    tag = " (provisional until POST reaches R1, because H3 holds)" if provisional else ""
    L: list[str] = []
    a = L.append

    a("# 018 — The compensation pot after P511: results")
    a("")
    a(
        f"Computed {r['computed_at'][:16].replace('T', ' ')} UTC under `DECLARATION.md` "
        f"(`{r['declaration_sha256'][:8]}…`) and `AMENDMENT-1.md` "
        f"(`{r['amendment_1_sha256'][:8]}…`, the byte-order mark), rule version "
        f"`{r['declaration_sha256'][:8]}.{r['amendment_1_sha256'][:8]}`. Rendered from "
        "`evidence/results.json` by `run.py --phase render`; every figure below is that "
        "file's. Not published."
    )
    a("")
    a("> Ofgem changed the rules on 24 August 2026 (P511) after £18.9m of mutualised")
    a("> supplier compensation had been paid in six months, most of it arising from one")
    a("> arrangement. Did the pot shrink afterwards, or did it just change hands?")
    a("")

    # -- verdicts ------------------------------------------------------------
    a("## The verdicts")
    a("")
    paid_dev, vtp_dev = D(c4["paid_vs_elexon"]) * 100, D(c4["vtp_vs_elexon"]) * 100
    a(
        f"**C4 {'passes' if c4['passes'] else 'FAILS (F5)'}.** Read on each day's SF run, the "
        f"28 days of February 2026 total {pounds(c4['paid'])} paid and "
        f"{mwh(c4['vtp_volume'])} of VTP volume, {paid_dev:+.1f} % and {vtp_dev:+.1f} % from "
        "Elexon's £5,576,308 and 63,827.48 MWh (P510 Initial Written Assessment slides), "
        "inside the declared ±15 %."
        + ("" if c4["passes"] else " No H verdict is published until the difference is explained.")
    )
    a("")
    if provisional:
        a(
            "**H3 holds, so every H1 and H2 verdict is provisional** until POST has reached "
            "its R1 run: POST is read on SF, FEB on R3."
        )
        a("")
    f, p = h["H1-FEB"], h["H1-PRE"]
    a(
        f"**H1, both baselines in one sentence.** POST's mean daily supplier compensation "
        f"volume was {ratio(f['ratio'])} times FEB's ({mwh(f['post_mean'])} against "
        f"{mwh(f['baseline_mean'])} a day), and POST's mean daily paid was "
        f"{ratio(p['ratio'])} times PRE's ({pounds(p['post_mean'])} against "
        f"{pounds(p['baseline_mean'])} a day); each is killed below 0.50, so H1-FEB "
        f"{f['verdict']} and H1-PRE {p['verdict']}{tag}."
    )
    a("")
    for key, side, measure, bar in (
        ("H2-VTP", "VTP party", "pooled VTP volume", "10 %"),
        ("H2-SUP", "recipient", "pooled paid", "25 %"),
    ):
        x = h[key]
        if x["verdict"] == "not decided":
            a(f"**{key}** not decided.")
        else:
            a(
                f"**{key} {x['verdict']}{tag}.** FEB's largest {side}, "
                f"{party(x['party'], names)}, carried {share(x['baseline_share'])} of FEB's "
                f"{measure} and {share(x['post_share'])} of POST's (holds above 50 % in FEB "
                f"and below {bar} in POST)."
            )
        a("")
    moved = sum(
        1
        for d in h["H3"]["days"].values()
        if d["sf_to_latest"] is not None and D(d["sf_to_latest"]) > D("0.05")
    )
    a(
        f"**H3 {h['H3']['verdict']}.** Daily paid moved from its SF run to its latest run by "
        f"more than 5 % on {moved} of the four RESTATE days (holds on two or more):"
    )
    a("")
    a("| day | SF paid | latest run | latest paid | SF to latest |")
    a("|---|---|---|---|---|")
    for day, d in h["H3"]["days"].items():
        rows = d["paid"]
        sf = next((x for x in rows if x["run"] == "SF"), None)
        last = rows[-1] if rows else None
        a(
            f"| {day} | {pounds(sf['value']) if sf else '-'} | {last['run'] if last else '-'} | "
            f"{pounds(last['value']) if last else '-'} | "
            f"{share(d['sf_to_latest']) if d['sf_to_latest'] is not None else '-'} |"
        )
    a("")
    a("| falsifier | fired |")
    a("|---|---|")
    for k, v in r["falsifiers"].items():
        a(f"| {k} | {'not decided' if v is None else ('**yes**' if v else 'no')} |")
    a("")

    # -- checks --------------------------------------------------------------
    a("## Checks")
    a("")
    mx = r["missing_or_excluded"]
    a(
        "**C5.** Every FEB, PRE and POST day had a run at or after SF; runs read: "
        + "; ".join(f"{w} {', '.join(v)}" for w, v in r["runs_read"].items())
        + ". Days with no qualifying run listed: "
        + (", ".join(f"{w} {len(v)}" for w, v in mx["missing"].items() if v) or "none")
        + "."
    )
    a("")
    bad = mx["files"]
    a(
        f"**C1 to C3, C6, C7.** {len(bad)} file(s) failed a decisive check and are excluded "
        "(the day counts as missing in a window; a RESTATE day is read on its other runs):"
    )
    a("")
    if bad:
        windows_of = defaultdict(list)
        for w, files in mx["excluded"].items():
            for fn in files:
                windows_of[fn].append(w)
        a("| file | read in | failed | off-prefix cells (position:prefix) |")
        a("|---|---|---|---|")
        for fn, e in bad.items():
            off = ", ".join(f"`{k}` {n}" for k, n in e["off_prefix"].items()) or "-"
            where = ", ".join(windows_of.get(fn, [])) or "RESTATE"
            a(f"| `{fn}` | {where} | {'; '.join(x.split()[0] for x in e['failed'])} | {off} |")
        a("")
    a(
        f"**Amendment 1.** {len(r['leading_byte_order_mark'])} files began with a UTF-8 "
        "byte-order mark and were read with it removed: "
        + ", ".join(f"`{x}`" for x in r["leading_byte_order_mark"])
        + "."
    )
    a("")
    beside = c4["latest_run_beside"]
    a(
        f"Beside C4, the same 28 days on their latest run ({', '.join(beside['runs'])}): "
        f"{pounds(beside['paid'])} paid ({D(beside['paid_vs_elexon']) * 100:+.1f} %) and "
        f"{mwh(beside['vtp_volume'])} ({D(beside['vtp_vs_elexon']) * 100:+.1f} %), no band."
    )
    a("")

    # -- context -------------------------------------------------------------
    a("## Context (no threshold applies)")
    a("")
    a("**Every measure against both baselines** (POST mean daily ÷ baseline mean daily):")
    a("")
    a("| measure | against FEB | against PRE |")
    a("|---|---|---|")
    for m, word in MEASURES.items():
        rf, rp = f.get("reported", {}).get(m), p.get("reported", {}).get(m)
        a(f"| {word} | {ratio(rf) if rf else '-'} | {ratio(rp) if rp else '-'} |")
    a("\nDeciding: H1-FEB on supplier compensation volume, H1-PRE on paid.\n")
    pre = ctx["h2_against_pre"]
    if pre:
        a(
            "**H2's computation against PRE**: "
            + "; ".join(
                f"{party(v['party'], names)} {share(v['baseline_share'])} of PRE's "
                f"{'VTP volume' if k == 'VTP' else 'paid'}, {share(v['post_share'])} of POST's"
                for k, v in pre.items()
            )
            + "."
        )
        a("")
    al = ctx["pre_almaperj_vtp_volume"]
    a(
        f"**`ALMAPERJ` in PRE** (PRE follows Ofgem's decision of 10 August): "
        f"{share(al['share_of_pre'])} of PRE's VTP volume; by day "
        + ", ".join(f"{d[8:10]}/{d[5:7]} {D(v):,.0f}" for d, v in al["by_day"].items())
        + " MWh."
    )
    a("")
    a(
        "**Charged against paid**, each window's days read "
        "(two published figures and their difference):"
    )
    a("")
    a("| window | days | paid | charged | charged − paid |")
    a("|---|---|---|---|---|")
    for w in ("FEB", "PRE", "POST", "SERIES"):
        t = ctx["window_totals"].get(w)
        if t:
            diff = D(t["charged"]) - D(t["supplier_cash"])
            a(
                f"| {w} | {t['days']} | {pounds(t['supplier_cash'])} | {pounds(t['charged'])} | "
                f"{pounds(diff)} ({D(diff) / D(t['supplier_cash']) * 100:+.1f} %) |"
            )
    a("")
    a("**Largest parties per window**, by share of the window's pooled total:")
    a("")
    for w in ("FEB", "PRE", "POST", "SERIES"):
        lg = ctx["largest"].get(w)
        if not lg:
            continue
        a(f"*{WINDOW_WORDS[w]}*")
        a("")
        a("| | VTP volume | paid | charged |")
        a("|---|---|---|---|")
        cols = [lg["vtp_volume"], lg["paid"], lg["charged"]]
        for i in range(max(len(c) for c in cols)):
            cells = []
            for c in cols:
                cells.append(f"{party(c[i][0], names)} {share(c[i][2])}" if i < len(c) else "")
            a(f"| {i + 1} | " + " | ".join(cells) + " |")
        a("")
    a("**SERIES by month** (mean per Wednesday read; excluded Wednesdays are not in the mean):")
    a("")
    months: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ctx["series"]:
        months[str(row["settlement_date"])[:7]].append(row)
    a("| month | Wednesdays read | paid | charged | VTP volume | supplier compensation volume |")
    a("|---|---|---|---|---|---|")
    for mth, rows in sorted(months.items()):
        n = len(rows)

        def mean(k: str, rows: list[dict[str, Any]] = rows, n: int = n) -> D:
            return sum((D(x[k]) for x in rows), D(0)) / n

        a(
            f"| {mth} | {n} | {pounds(mean('paid'))} | {pounds(mean('charged'))} | "
            f"{mwh(mean('vtp_volume'))} | {mwh(mean('supplier_volume'))} |"
        )
    a("")

    # -- names ---------------------------------------------------------------
    a("## Names (R6)")
    a("")
    leaders = [h[k]["party"] for k in ("H2-SUP", "H2-VTP") if h[k].get("party")]
    carried = [x for x in leaders if x in names]
    missing = [x for x in leaders if x not in names]
    a(
        f"Names are the BM unit register's (Elexon Insights `reference/bmunits/all`, pinned "
        f"at acquisition, {record.get('register', 'see Record')}), mapping a lead party id to "
        "its name. Ids printed without a name are not carried by that register. Elexon's P510 "
        'slides name "SEFE Energy Limited" as the largest recipient and "Almape Holdings '
        'Limited" as the largest VTP for September 2025 to February 2026. '
        + (
            f"The register carries {' and '.join(party(x, names) for x in carried)}. "
            if carried
            else ""
        )
        + (
            f"The register does not carry {' or '.join(f'`{x}`' for x in missing)}, so "
            "which id either of Elexon's names belongs to is not asserted here."
            if missing
            else "Elexon's names are quoted as Elexon's and matched to no id."
        )
    )
    a("")

    # -- never ---------------------------------------------------------------
    a("## What this does not claim")
    a("")
    a(
        "That `ALMAPERJ` and `GMTR` (or Almape Holdings and SEFE Energy) were one "
        "configuration; that anyone broke a rule; that P511 caused any change (the windows "
        "compare levels and shares before and after a date, while the market grew, "
        "half-hourly settlement migration went on and the SCRP moves by quarter); savings, "
        'losses or "should have"; that thirteen days of POST are typical of what follows; '
        "that charged minus paid is an error, a leak or anyone's money."
    )
    a("")
    a("## Record")
    a("")
    for k, v in record.items():
        a(f"- {k}: `{v}`")
    a("")
    return "\n".join(L)
