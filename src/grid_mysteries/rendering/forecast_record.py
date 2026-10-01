"""022 — FINDINGS.md as a pure function of the committed evidence.

Every sentence names the publisher and the publication date of what it
quotes. A forecast is "overstated by" or "understated by", never wrong.
The not-yet-scorable table is a result, not a gap. No optimiser is
named and no cause is attributed.
"""

from collections import Counter
from decimal import Decimal
from typing import Any


def pounds(value: str | Decimal | None) -> str:
    if value is None:
        return "-"
    return f"£{Decimal(value):,.0f}"


def pct(value: str | Decimal | None) -> str:
    return "-" if value is None else f"{Decimal(value):+.1f} %"


def period_of(row: dict[str, Any]) -> str:
    s, e = row["period_start"], row["period_end"]
    return str(s) if s == e else f"{s} to {e}"


def vintage_of(row: dict[str, Any]) -> str:
    publisher, published_on, url = row["vintage"]
    return f"{publisher}, {published_on}, `{url}`"


def render_findings(
    summary: dict[str, Any],
    readings: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    revisions: list[dict[str, Any]],
    months: dict[str, Any],
) -> str:
    rv = summary["rule_version"]
    rows = [c for c in comparisons if c["rule_version"] == rv]
    revs = [r for r in revisions if r["rule_version"] == rv]
    reads = [r for r in readings if r["rule_version"] == rv]
    scored = [c for c in rows if c["status"] == "scored"]
    mismatch = [c for c in rows if c["status"] == "scope mismatch"]
    pending = [c for c in rows if c["status"] in ("not yet scorable", "in-year, never scored")]
    vintages = {tuple(c["vintage"]) for c in rows}
    scorable = {tuple(c["vintage"]) for c in scored}
    props = summary["propositions"]
    L = [
        "# 022 — The Forecast Record, issue 1: findings",
        "",
        f"*Declaration `DECLARATION.md`, SHA-256 `{summary['declaration_sha256']}`, frozen and "
        f"witnessed before any figure; acquisition plan `ACQUISITION.md`, SHA-256 "
        f"`{summary['plan_sha256']}`; rule version `{rv}`; run {summary['run_date']}, computed "
        f"{summary['computed_at']}. Every figure below is as published by the publisher named, "
        "on the date named, and read from the pinned page whose digest the evidence carries. "
        "Nothing here attributes an error to a cause or names an optimiser.*",
        "",
        "## The mystery",
        "",
        "> Battery revenue forecasts move hundreds of millions of pounds of fund value, and nobody "
        "has ever published how accurate they were.",
        "",
        "## The result, in one paragraph",
        "",
    ]
    if not scored:
        L.append(
            f"Of the {len(vintages)} forecast vintage(s) the reading rules found on Modo Energy's "
            f"public pages, **none is scorable today** (F1): every published headline covers a "
            "period that has not ended, or the year of its own publication (in-year, never "
            "scored), or no realised figure of its scope has been published for it. The "
            "not-yet-scorable table below is the result of issue 1, with the date each vintage "
            "becomes scorable. P-A and P-B are undecided; "
            f"P-C is {props['P-C']['verdict']} over {props['P-C']['pairs']} revision pair(s)."
        )
    else:
        over = sum(
            1
            for v in scorable
            if props["P-A"]["per_vintage"].get(" ".join(map(str, v)), {}).get("reading")
            == "overstated"
        )
        L.append(
            f"{len(scorable)} of {len(vintages)} forecast vintages are scorable today; "
            f"{over} overstated the first realised year. P-A {props['P-A']['verdict']}, "
            f"P-B {props['P-B']['verdict']}, P-C {props['P-C']['verdict']}."
        )
    L += ["", "## Scored comparisons", ""]
    if scored:
        L += [
            "| vintage | scope | period | forecast | outturn (scope, ids) | signed error | % "
            "| note |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for c in scored:
            word = (
                "overstated by"
                if Decimal(c["signed_error"]) > 0
                else ("understated by" if Decimal(c["signed_error"]) < 0 else "exact")
            )
            L.append(
                f"| {vintage_of(c)} | {c['scope']} | {period_of(c)} | {pounds(c['forecast'])} | "
                f"{pounds(c['realised'])} ({c['realised_scope']}; "
                f"{', '.join(c['realised_ids'])}) | "
                f"{word} {pounds(abs(Decimal(c['signed_error'])))} | "
                f"{pct(c['signed_error_pct'])} | {c['note']} |"
            )
    else:
        L.append("None.")
    L += ["", "## Not yet scorable (a result, not a gap)", ""]
    if pending:
        L += [
            "| vintage | scope | period | forecast | status | scorable after | note |",
            "|---|---|---|---|---|---|---|",
        ]
        for c in pending:
            L.append(
                f"| {vintage_of(c)} | {c['scope']} | {period_of(c)} | {pounds(c['forecast'])} | "
                f"{c['status']} | {c['scorable_after'] or '-'} | {c['note']} |"
            )
    else:
        L.append("None.")
    L += ["", "## Scope mismatches (both figures listed, nothing adjusted)", ""]
    if mismatch:
        L += [
            "| vintage | forecast scope | period | forecast | realised figure (its scope) | note |",
            "|---|---|---|---|---|---|",
        ]
        for c in mismatch:
            L.append(
                f"| {vintage_of(c)} | {c['scope']} | {period_of(c)} | {pounds(c['forecast'])} | "
                f"{pounds(c['realised'])} ({c['realised_scope']}) | {c['note']} |"
            )
    else:
        L.append("None.")
    L += ["", "## Revisions between consecutive vintages (R-V)", ""]
    if revs:
        L += [
            "| publisher | scope | period | earlier (date, value) | later (date, value) | "
            "change | direction |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in revs:
            period = str(r["period_start"])
            if r["period_start"] != r["period_end"]:
                period += f" to {r['period_end']}"
            L.append(
                f"| {r['publisher']} | {r['scope']} | {period} | "
                f"{r['earlier']['published_on']}, {pounds(r['earlier']['value'])} | "
                f"{r['later']['published_on']}, {pounds(r['later']['value'])} | "
                f"{pounds(r['change'])} | {r['direction']} |"
            )
    else:
        L.append(
            "No two consecutive vintages print a forecast for the same scope and period, so no "
            "revision pair exists; P-C is undecided."
        )
    L += ["", "## The realised side, as published", ""]
    annual = [r for r in reads if r["outcome"] == "figure" and r["figure"]["basis"] == "realised"]
    L += ["### Annual figures read (R-R5)", ""]
    if annual:
        L += [
            "| publisher | published | scope | year | figure | as printed | page |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in sorted(annual, key=lambda r: (r["figure"]["period_start"], r["published_on"])):
            f = r["figure"]
            L.append(
                f"| {f['publisher']} | {r['published_on']} | {f['scope']} | {f['period_start']} | "
                f"{pounds(f['value'])} | {f['as_printed']} | `{r['page_url']}` |"
            )
    else:
        L.append("None.")
    L += ["", "### Monthly index figures read (R-R5), by scope and year (R-S4)", ""]
    L += ["| scope | year | months read | complete | mean of twelve |", "|---|---|---|---|---|"]
    for d in months["detail"]:
        L.append(
            f"| {d['scope']} | {d['year']} | {', '.join(str(m) for m in d['months_read'])} | "
            f"{'yes' if d['complete'] else 'no'} | {pounds(d['mean']) if d['mean'] else '-'} |"
        )
    if months["restated"]:
        L += [
            "",
            "Months printed differently on different pages beyond rounding (F4), the latest "
            "published read:",
            "",
        ]
        for x in months["restated"]:
            others = "; ".join(f"{pounds(o['value'])} on {o['published_on']}" for o in x["others"])
            L.append(
                f"- {x['scope']} {x['year']}-{x['month']:02d}: read {pounds(x['read'])} from "
                f"`{x['read_from']}`; others {others}"
            )
    L += ["", "## What the reading rules did with every figure-looking string", ""]
    tally = Counter(r["rule"] for r in reads)
    L += ["| rule | strings |", "|---|---|"]
    for rule, n in tally.most_common():
        L.append(f"| {rule} | {n:,} |")
    f2 = summary["falsifiers"]["F2"]
    L += [
        "",
        f"F1 (no scorable vintage): {'fires' if summary['falsifiers']['F1'] else 'silent'}. "
        f"F2 (the rules cannot read the corpus): {'fires' if f2['fires'] else 'silent'}, "
        f"{f2['unexplained']} of {f2['per_year_strings']} per-year strings on English pages "
        "declined for a period or population not stated "
        f"({f2['share_pct']} %, threshold {f2['threshold_pct']} %). "
        "F3 (a committed row would change): refused before writing, so silent by construction. "
        f"F4 (the realised side restates itself beyond rounding): {len(months['restated'])} "
        "month(s).",
        "",
        "## Propositions",
        "",
    ]
    for k in ("P-A", "P-B", "P-C"):
        L.append(f"- **{k}**: {props[k]['verdict']}.")
    L += [
        "",
        "## What this never claims",
        "",
        "That any forecast was wrong, careless or interested; that any error had a cause; that one "
        "publisher's forecasts are better or worse than another's; that an index level is a market "
        "fact rather than a published figure under its publisher's methodology; that a fund's "
        "reported revenue per megawatt is comparable to a fleet figure; or that any of this is a "
        "forecast of future revenue. Nothing here uses, reconstitutes or re-publishes any index as "
        "a benchmark; the figures quoted are those their publishers chose to publish on public "
        "pages.",
        "",
        "## The record",
        "",
        "`evidence/figures.ndjson`, `evidence/comparisons.ndjson`, `evidence/revisions.ndjson` "
        f"and `evidence/months.json`, every row under rule version `{rv}`; the pinned pages by "
        "digest in "
        "`evidence/pages-manifest.json` and `evidence/rns-manifest.json`; the schema reports under "
        f"`archives/modo-pages-022/` (SHA-256 `{summary['schema_modo_sha256']}`) and "
        f"`archives/rns-grid-022/` (SHA-256 `{summary['schema_rns_sha256']}`); `scripts/check`.",
        "",
    ]
    return "\n".join(L)
