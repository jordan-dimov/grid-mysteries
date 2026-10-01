"""022 — FINDINGS.md as a pure function of the committed evidence.

Every sentence names the publisher and the publication date of what it
quotes. A forecast is "overstated by" or "understated by", never wrong.
The not-yet-scorable table is a result, not a gap. No optimiser is
named and no cause is attributed.
"""

import re
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
    period_mismatch = [c for c in rows if c["status"] == "period mismatch"]
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
    ]
    if period_mismatch:
        L += ["## The sentence the issue exists for", ""]
        for c in period_mismatch:
            publisher, published_on, url = c["vintage"]
            fund = publisher.split(" (")[0]
            m = re.search(r"(\d+) of 12 months overlap", c["note"])
            overlap = m.group(1) if m else "an unstated number of"
            if c["scope"].endswith("-excl-cm"):
                qualifier = "excluding the Capacity Market"
            elif c["scope"].endswith("-incl-cm"):
                qualifier = "including the Capacity Market"
            else:
                qualifier = "with no Capacity Market qualifier stated"
            outturn_q = (
                "under a revenue definition that does not state that qualifier"
                if c["realised_scope"] != c["scope"]
                else "under the same definition"
            )
            L.append(
                f"**{fund} assumed {pounds(c['forecast'])} per MW per year for calendar "
                f"{period_of(c)}, {qualifier} (published {published_on}), and earned "
                f"{pounds(c['realised'])} per MW per year in its own {c['realised_period']}, a "
                f"period that overlaps the assumed one by {overlap} of twelve months and is "
                f"reported {outturn_q}, so the two figures are printed side by side and not "
                "subtracted.** "
                f"Source: assumption as published by {fund} on {published_on} (`{url}`); outturn "
                f"as published by {fund} in its results for that year (figure "
                f"`{', '.join(c['realised_ids'])}` in `evidence/figures.ndjson`). "
                f"{c['note'][0].upper() + c['note'][1:]}."
            )
            L.append("")
        L += [
            "| publisher | assumption (published, period, scope) | figure | the fund's own "
            "outturn (period, scope) | figure | overlap | note |",
            "|---|---|---|---|---|---|---|",
        ]
        for c in period_mismatch:
            publisher, published_on, url = c["vintage"]
            overlap = c["note"].split(":")[1].split(";")[0].strip() if ":" in c["note"] else ""
            L.append(
                f"| {publisher} | {published_on}, calendar {period_of(c)}, {c['scope']} | "
                f"{pounds(c['forecast'])} | {c['realised_period']}, {c['realised_scope']} | "
                f"{pounds(c['realised'])} | {overlap} | both printed, nothing adjusted |"
            )
        L.append("")
    L += ["## The finding", ""]
    fund_cited = [
        r
        for r in reads
        if r["outcome"] == "figure"
        and r["figure"]["basis"] == "forecast"
        and "fund" in r["figure"]["publisher"].lower()
    ]
    docs = summary.get("fund_documents", {})
    if not scored:
        after = sorted(c["scorable_after"] for c in pending if c["scorable_after"])
        first = after[0] if after else "no date"
        publishers = sorted({c["vintage"][0] for c in rows})
        L.append(
            "**The listed funds were valued on revenue curves. Their own documents "
            f"({docs.get('nav', 0)} NAV announcements and {docs.get('prospectus', 0)} prospectus "
            f"and placing documents among {docs.get('total', 0)} pinned, back to "
            f"{docs.get('earliest', 'their earliest pages')}) cite those curves without a "
            "per-year level anyone can score, and the forecaster's public pages carry only "
            "in-year and horizon figures. Nobody who relied on these numbers can check them in "
            f"public before {first}.** "
            f"Of the {len(vintages)} forecast vintage(s) the reading rules found on the public "
            f"pages of {', '.join(publishers)}, none is scorable today (F1): each covers a period "
            "that has not ended, or the year of its own publication (in-year, never scored), or "
            "has no published outturn of its own scope. The per-asset cut is the paid product "
            "behind the public record. The not-yet-scorable table below is the result of issue "
            "1, with the date each vintage becomes scorable."
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
    L += ["", "## The fund-cited forecast figures (the only fund-side forecasts in existence)", ""]
    duplicates = {d["figure_id"]: d for d in summary.get("same_day_duplicates", [])}
    if fund_cited:
        L += [
            "| publisher | published | period | figure | scope | Capacity Market | cited source "
            "| as printed | page |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for r in sorted(fund_cited, key=lambda r: (r["published_on"], r["figure"]["period_start"])):
            f = r["figure"]
            if f["figure_id"] in duplicates:
                continue
            also = [d["url"] for d in duplicates.values() if d["same_as"] == f["figure_id"]]
            page_cell = f"`{r['page_url']}`" + (
                " (the same figure in " + ", ".join(f"`{u}`" for u in also) + ", one publication)"
                if also
                else ""
            )
            cm = (
                "excluded"
                if f["scope"].endswith("-excl-cm")
                else ("included" if f["scope"].endswith("-incl-cm") else "not stated")
            )
            L.append(
                f"| {f['publisher']} | {r['published_on']} | {f['period_start']}"
                + ("" if f["period_start"] == f["period_end"] else f" to {f['period_end']}")
                + f" | {pounds(f['value'])} | {f['scope']} | {cm} | "
                f"{f.get('cited_source') or 'source unnamed'} | {f['as_printed']} | "
                f"{page_cell} |"
            )
    else:
        L.append("None.")
    L += ["", "## Scope mismatches (both figures listed, nothing adjusted)", ""]
    if mismatch:
        L += [
            "",
            "A fund's assumption is for its own portfolio, under its own revenue definition "
            "(here, excluding the Capacity Market), over its own assets and durations. The fleet "
            "outturn is an index over every battery in Great Britain under the index's "
            "methodology. The two differ in population, in what counts as revenue and in "
            "duration mix, so forecast minus outturn would subtract one quantity from another "
            "and the difference would be a number without a meaning. Both figures are printed; "
            "the subtraction is not done.",
            "",
        ]
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
    L += ["", "## The realised side, as published", ""]
    annual = [r for r in reads if r["outcome"] == "figure" and r["figure"]["basis"] == "realised"]
    L += ["### Annual figures read (R-R5)", ""]
    if annual:
        L += [
            "| publisher | published | scope | period | figure | as printed | page |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in sorted(annual, key=lambda r: (r["figure"]["period_end"], r["published_on"])):
            f = r["figure"]
            label = f.get("period_label") or str(f["period_start"])
            L.append(
                f"| {f['publisher']} | {r['published_on']} | {f['scope']} | {label} | "
                f"{pounds(f['value'])} | {f['as_printed']} | `{r['page_url']}` |"
            )
        by_key: dict[tuple[str, int], list[dict[str, Any]]] = {}
        for r in annual:
            f = r["figure"]
            if f.get("period_end_date"):
                continue
            by_key.setdefault((f["scope"], f["period_start"]), []).append(r)
        multi = {k: v for k, v in by_key.items() if len(v) > 1}
        if multi:
            L += [
                "",
                "More than one figure read for one scope and year (R-S3 reads one and names "
                "the others):",
                "",
            ]
            for (scope, year), rs in sorted(multi.items()):
                read = max(rs, key=lambda r: (r["published_on"], r["figure"]["figure_id"]))
                others = "; ".join(
                    f"{pounds(x['figure']['value'])} ({x['figure']['as_printed']}, "
                    f"{x['published_on']})"
                    for x in rs
                    if x["figure"]["figure_id"] != read["figure"]["figure_id"]
                )
                L.append(
                    f"- {scope} {year}: read {pounds(read['figure']['value'])} "
                    f"({read['figure']['as_printed']}); also read {others}. Where the figures "
                    "differ by more than rounding, the sentences are in `evidence/figures.ndjson` "
                    "and the difference is not resolved here."
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
            "### Months printed differently on different pages (F4): both figures, both "
            "sources, both dates; the latest published read, nothing resolved",
            "",
        ]
        for x in months["restated"]:
            others = "; ".join(f"{pounds(o['value'])} on {o['published_on']}" for o in x["others"])
            L.append(
                f"- {x['scope']} {x['year']}-{x['month']:02d}: read {pounds(x['read'])} from "
                f"`{x['read_from']}`; others {others}"
            )
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
    asset_words = (
        "highest-earning",
        "top-performing",
        "top quartile",
        "jamesfield",
        "wishaw",
        "coventry",
        "capenhurst",
        "one system",
        "some batteries",
    )
    per_asset = [
        r
        for r in reads
        if r["outcome"] == "declined"
        and r["rule"] == "R-R3 a named asset or subset, not the population"
        and "modoenergy.com" in r["page_url"]
        and any(w in r["sentence"].lower() for w in asset_words)
    ]
    L += ["", "## Per-asset and subset figures on the public pages (listed, not read)", ""]
    if per_asset:
        L += [
            "These strings name an asset or the best-performing part of the fleet. The rules read "
            "none into any comparison; they are listed because they are public and an adviser may "
            "want them. The other strings declined by the same rule (swap basis risk, uplift "
            "ranges for individual batteries) stay in `evidence/figures.ndjson` under that rule.",
            "",
            "| published | as printed | sentence | page |",
            "|---|---|---|---|",
        ]
        for r in sorted(per_asset, key=lambda r: r["published_on"] or ""):
            L.append(
                f"| {r['published_on']} | {r['as_printed']} | "
                f"{r['sentence'][:200].replace('|', '/')} | `{r['page_url']}` |"
            )
    else:
        L.append("None.")
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
    for pub, pp in props.get("per_publisher", {}).items():
        L.append(
            f"- {pub}: P-A {pp['P-A']['verdict']}, P-B {pp['P-B']['verdict']}, "
            f"P-C {pp['P-C']['verdict']} ({pp['P-C']['pairs']} pair(s))."
        )
    L += [
        "",
        "## Method, in short",
        "",
        "Every page was pinned under a sealed plan. A schema pass listed every figure-looking "
        "string as printed. The reading rules were written against that pass and frozen before "
        "any figure was read. A forecast is a published headline for a stated future period. An "
        "outturn is a published realised figure for a past calendar year, or the mean of twelve "
        "published monthly figures where no annual figure is published. A year counts only if "
        "the forecast was published before it began. A forecast and an outturn of different "
        "populations are listed side by side and never adjusted. Every string is in the "
        "evidence with the rule that read or declined it. No row changes once committed.",
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
        f"and `evidence/months.json`, every row under rule version `{rv}`"
        + (
            " (amendments "
            + ", ".join(
                f"{n} SHA-256 `{d}`"
                for n, d in enumerate(summary.get("amendments_sha256") or [], start=2)
            )
            + f"; the rows under `{summary['supersedes_rule_version']}` and its predecessors "
            "remain in the evidence as computed)"
            if summary.get("amendments_sha256")
            else ""
        )
        + "; the pinned pages by "
        "digest in "
        "`evidence/pages-manifest.json` and `evidence/rns-manifest.json`; the schema reports under "
        f"`archives/modo-pages-022/` (SHA-256 `{summary['schema_modo_sha256']}`) and "
        f"`archives/rns-grid-022/` (SHA-256 `{summary['schema_rns_sha256']}`); `scripts/check`.",
        "",
    ]
    return "\n".join(L)
