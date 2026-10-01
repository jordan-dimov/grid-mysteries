"""021 — FINDINGS.md as a pure function of the committed evidence.

Every number comes from `evidence/summary.json`, `evidence/comparisons.ndjson`
and `evidence/groups.ndjson`; nothing is computed here beyond formatting,
and the same evidence always renders the same bytes. The framing rules of
the sponsor (2026-09-30) are applied here: the date is the one in the
project's connection agreement, moved by agreed variation; every slippage
figure is accompanied by 006's cause split; no megawatt-year figure is
printed without its determined and undetermined split.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

TITLE = (
    "021 — Where the dates move: 014's slippage series by plant type and by host transmission owner"
)
RULE_V2 = "014-v2"
RULE_CONTENT = "tec-identity-content-v1"
BLANK = "—"
#: 006 (run 2026-08-26), T4: the cause split of the 213 slips of 24 months
#: or more, which accompanies every slippage figure on this page.
CAUSE_SPLIT = (
    "Cause, from 006: of the 213 slips of 24 months or more in 005's population, "
    "60 % were project-led, 26 % works-led and 14 % unattributable; nothing here "
    "revises that split or attributes any group's movement to a cause."
)
#: Groups below this share of dated capacity are folded in the year tables.
FOLD_BELOW = Decimal("5.0")
HOST_ORDER = ("NGET", "SPT", "SHET", "OFTO", "(blank)", "key changed")
ZERO = Decimal(0)

Rows = list[dict[str, Any]]


# ---------------------------------------------------------------- formatting


def whole(value: str | None) -> str:
    if value is None:
        return BLANK
    return f"{Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP):+,}"


def mw(value: str | None) -> str:
    if value is None:
        return BLANK
    return f"{Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}"


def pct(value: str | None) -> str:
    return BLANK if value is None else f"{Decimal(value):.1f} %"


def pts(value: str | None) -> str:
    return BLANK if value is None else f"{Decimal(value):+.1f}"


def day(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%-d %B %Y")


def window_label(c: dict[str, Any]) -> str:
    span = f"{day(c['baseline'])} to {day(c['current'])}"
    if c["window"] in ("headline", "copy-to-copy"):
        return span
    return f"{c['window']} ({span})"


def marks(c: dict[str, Any]) -> str:
    out = []
    if c.get("unfit"):
        out.append(
            "**unfit** (F-G4: the key-changed bucket holds more than a fifth of dated capacity)"
        )
    if c.get("not_read"):
        out.append("**shares not read** (R9: net within ±1,000 MW-years)")
    return "; ".join(out)


def dimension_label(dimension: str) -> str:
    return {"host_to": "host transmission owner", "plant_type": "plant type"}[dimension]


# ------------------------------------------------------------------ tables


def group_table(groups: Rows, label: str) -> list[str]:
    lines = [
        f"| {label} | Units at baseline / matched | "
        "Dated project-stages (later / earlier / unchanged) | "
        "Dated capacity, MW | Share of capacity | Net, MW-years (014 v2) | Determined | "
        "Undetermined (v2 / content) | Share of net | Share of determined | "
        "Concentration, points | Thin (R7) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for g in groups:
        und = g["undetermined"]
        thin = BLANK if g["thin"] is None else ("yes" if g["thin"] else "no")
        lines.append(
            f"| {g['group']} | {g['units_baseline']:,} / {g['matched']:,} | "
            f"{g['dated_both']:,} ({g['later']} / {g['earlier']} / "
            f"{g['unchanged']}) | {mw(g['capacity_baseline_mw'])} | "
            f"{pct(g['share_of_capacity_percent'])} | {whole(g['total'][RULE_V2])} | "
            f"{whole(g['determined'])} | {whole(und[RULE_V2])} / {whole(und[RULE_CONTENT])} | "
            f"{pct(g['share_of_net_percent'])} | {pct(g['share_of_determined_percent'])} | "
            f"{pts(g['concentration_points'])} | {thin} |"
        )
    return lines


def comparison_sentence(c: dict[str, Any]) -> str:
    f = c["figures_014_v4"]
    determined = Decimal(f["determined"])
    under_v2 = str(Decimal(f["total"][RULE_V2]) - determined)
    under_content = str(Decimal(f["total"][RULE_CONTENT]) - determined)
    changed = c["key_changed"]
    return (
        f"Net movement {whole(f['mw_years_net'])} MW-years under version 2's rule over "
        f"{f['dated_both']:,} project-stages dated at both ends and weighing "
        f"{mw(f['weighted_mw'])} MW; {whole(f['determined'])} of it is movement the "
        f"register's stage labels determine, and {f['undetermined_groups']} project groups "
        f"with an undetermined pairing add {whole(under_v2)} under version 2's rule or "
        f"{whole(under_content)} under content matching (014 version 4). Key changed "
        f"between the two copies: {changed['dated_both']} dated project-stages, "
        f"{mw(changed['capacity_baseline_mw'])} MW, {whole(changed['mw_years_net'])} "
        f"MW-years; unified by the spelling table: {c['unified_by_spelling_table']}. " + CAUSE_SPLIT
    )


def reading_cell(r: dict[str, Any]) -> str:
    return (
        f"{pct(r['share_of_capacity_percent'])} / {pct(r['share_of_net_percent'])} "
        f"({pts(r['concentration_points'])})"
    )


def storage_lines(c: dict[str, Any]) -> list[str]:
    s = c["storage"]
    out = [
        "| Reading | Groups | Dated project-stages | Dated capacity, MW | Share of capacity | "
        "Net, MW-years (v2) | Determined | Share of net | Concentration, points |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, label in (("alone", "Storage alone"), ("including", "Storage including compounds")):
        r = s[name]
        out.append(
            f"| {label} | {len(r['groups'])} | {r['dated_both']:,} | "
            f"{mw(r['capacity_baseline_mw'])} | {pct(r['share_of_capacity_percent'])} | "
            f"{whole(r['mw_years_net'])} | {whole(r['determined'])} | "
            f"{pct(r['share_of_net_percent'])} | {pts(r['concentration_points'])} |"
        )
    return out


def folded_cells(groups: Rows) -> str:
    named = [g for g in groups if not g["bucket"]]
    shown = [g for g in named if Decimal(g["share_of_capacity_percent"] or 0) >= FOLD_BELOW]
    rest = [g for g in named if g not in shown]
    cells = [
        f"{g['group']}: {pct(g['share_of_capacity_percent'])} of capacity, "
        f"{pct(g['share_of_net_percent'])} of net ({pts(g['concentration_points'])})"
        + (" thin" if g["thin"] else "")
        for g in shown
    ]
    if rest:
        cap = sum((Decimal(g["share_of_capacity_percent"] or 0) for g in rest), ZERO)
        net = sum((Decimal(g["share_of_net_percent"] or 0) for g in rest), ZERO)
        cells.append(f"{len(rest)} other groups: {cap:.1f} % of capacity, {net:.1f} % of net")
    return "; ".join(cells) or BLANK


def host_cell(groups: Rows, name: str) -> str:
    g = next((x for x in groups if x["group"] == name), None)
    if g is None:
        return BLANK
    return reading_cell(g) + (" thin" if g["thin"] else "")


def year_tables(groups_by_key: dict[str, Rows], which: Rows) -> list[str]:
    lines = [
        "### By host transmission owner",
        "",
        "Each cell: share of dated capacity / share of net movement (concentration in points).",
        "",
        "| Window | Net, MW-years (v2) | Determined | " + " | ".join(HOST_ORDER) + " | Marks |",
        "|---" * (4 + len(HOST_ORDER)) + "|",
    ]
    for c in (x for x in which if x["dimension"] == "host_to"):
        f = c["figures_014_v4"]
        cells = " | ".join(host_cell(groups_by_key[c["key"]], h) for h in HOST_ORDER)
        lines.append(
            f"| {window_label(c)} | {whole(f['mw_years_net'])} | {whole(f['determined'])} | "
            f"{cells} | {marks(c) or BLANK} |"
        )
    lines += [
        "",
        CAUSE_SPLIT,
        "",
        "### By plant type",
        "",
        f"Groups holding at least {FOLD_BELOW} % of the window's dated capacity are named; "
        "the rest are folded with their summed shares. Every group is in "
        "`evidence/groups.ndjson`.",
        "",
        "| Window | Net, MW-years (v2) | Determined | Key changed (share of capacity) | "
        "Groups | Marks |",
        "|---|---|---|---|---|---|",
    ]
    for c in (x for x in which if x["dimension"] == "plant_type"):
        f = c["figures_014_v4"]
        kc = next((g for g in groups_by_key[c["key"]] if g["group"] == "key changed"), None)
        changed = pct(kc["share_of_capacity_percent"]) if kc else "0.0 %"
        lines.append(
            f"| {window_label(c)} | {whole(f['mw_years_net'])} | {whole(f['determined'])} | "
            f"{changed} | {folded_cells(groups_by_key[c['key']])} | {marks(c) or BLANK} |"
        )
    lines += [
        "",
        CAUSE_SPLIT,
        "",
        "### The storage reading, two ways, per window",
        "",
        "| Window | Storage alone: share of capacity / share of net (points) | "
        "Including compounds: share of capacity / share of net (points) | Marks |",
        "|---|---|---|---|",
    ]
    for c in (x for x in which if x["dimension"] == "plant_type"):
        s = c["storage"]
        lines.append(
            f"| {window_label(c)} | {reading_cell(s['alone'])} | "
            f"{reading_cell(s['including'])} | {marks(c) or BLANK} |"
        )
    thin = [
        f"{window_label(c)}, by {dimension_label(c['dimension'])}: {', '.join(c['thin_groups'])}"
        for c in which
        if c["thin_groups"]
    ]
    lines += [
        "",
        "Thin groups under R7 (matched fewer than half of the group's baseline units; "
        "figures published, not suppressed): " + ("; ".join(thin) if thin else "none") + ".",
    ]
    return lines


def proposition_lines(props: dict[str, Any]) -> list[str]:
    pa, pb, pc = props["P-A"], props["P-B"], props["P-C"]

    def failing(p: dict[str, Any]) -> str:
        text = f" Failing: {', '.join(p['failing'])}." if p["failing"] else ""
        if p["failing_on_determined"] != p["failing"]:
            named = ", ".join(p["failing_on_determined"]) or "none"
            return text + f" On the determined reading the failing groups would be: {named}."
        return text + " The determined reading agrees."

    pa_groups = "; ".join(
        f"{g['group']} {pct(g['share_of_net_percent'])} of net "
        f"({pct(g['share_of_determined_percent'])} of the determined part) against "
        f"{pct(g['share_of_capacity_percent'])} of capacity" + (", thin" if g["thin"] else "")
        for g in pa["groups"]
    )
    pb_groups = "; ".join(
        f"{g['group']} {g['dated_both']} dated, {whole(g['mw_years_net'])} MW-years "
        f"({whole(g['determined'])} determined)" + (", thin" if g["thin"] else "")
        for g in pb["groups"]
    )
    inc, alone = pc["including_compounds"], pc["storage_alone"]
    return [
        "## Propositions, as declared and as decided",
        "",
        f"- **P-A** ({pa['statement']}): **{pa['verdict']}**. {pa_groups}.{failing(pa)}",
        f"- **P-B** ({pb['statement']}): **{pb['verdict']}**. {pb_groups}.{failing(pb)}",
        f"- **P-C** ({pc['statement']}): **{pc['verdict']}**. Including compounds "
        f"({len(inc['groups'])} groups): {pct(inc['share_of_net_percent'])} of net against "
        f"{pct(inc['share_of_capacity_percent'])} of capacity, {pts(pc['points'])} points; "
        f"share of the determined part {pct(pc['share_of_determined_percent'])}. "
        f"Storage alone: {pct(alone['share_of_net_percent'])} of net against "
        f"{pct(alone['share_of_capacity_percent'])} of capacity "
        f"({pts(alone['concentration_points'])} points); it does not decide P-C.",
    ]


# -------------------------------------------------------------- conclusion


def conclusion(
    summary: dict[str, Any], hh: dict[str, Any], hp: dict[str, Any], groups_by_key: dict[str, Rows]
) -> list[str]:
    """Composed from the propositions and the headline window's rows; no
    figure is typed here."""
    props = summary["propositions"]
    pa, pb, pc = props["P-A"], props["P-B"], props["P-C"]
    hosts = "; ".join(
        f"{g['group']} {pct(g['share_of_capacity_percent'])} of dated capacity and "
        f"{pct(g['share_of_net_percent'])} of net ({pts(g['concentration_points'])} points"
        + (", thin" if g["thin"] else "")
        + ")"
        for g in groups_by_key[hh["key"]]
        if not g["bucket"] and Decimal(g["share_of_capacity_percent"] or 0) > 0
    )
    plants = [g for g in groups_by_key[hp["key"]] if not g["bucket"]][:4]
    largest = "; ".join(
        f"{g['group']} {pct(g['share_of_capacity_percent'])} of capacity and "
        f"{pct(g['share_of_net_percent'])} of net ({pts(g['concentration_points'])} points"
        + (", thin" if g["thin"] else "")
        + ")"
        for g in plants
    )
    inc, alone = pc["including_compounds"], pc["storage_alone"]
    det_points = (
        Decimal(pc["share_of_determined_percent"]) - Decimal(inc["share_of_capacity_percent"])
        if pc["share_of_determined_percent"] is not None
        and inc["share_of_capacity_percent"] is not None
        else None
    )
    changed = next((g for g in groups_by_key[hp["key"]] if g["group"] == "key changed"), None)
    changed_share = changed["share_of_capacity_percent"] if changed else "0.0"
    return [
        "## Conclusion",
        "",
        f"Over the headline window, {window_label(hh)}, under this reading and with the 006 "
        "cause split standing unrevised:",
        "",
        f"- **By area**, net movement is spread close to dated capacity: {hosts}. "
        f"P-A **{pa['verdict']}**; P-B **{pb['verdict']}**.",
        f"- **By technology**, the largest groups are {largest}. Energy storage including "
        f"compounds ({len(inc['groups'])} register labels) holds "
        f"{pct(inc['share_of_capacity_percent'])} of dated capacity and "
        f"{pct(inc['share_of_net_percent'])} of net under version 2's rule "
        f"({pts(pc['points'])} points), and {pct(pc['share_of_determined_percent'])} of the "
        f"determined part ({pts(str(det_points) if det_points is not None else None)} points); "
        f"storage alone {pct(alone['share_of_capacity_percent'])} of capacity and "
        f"{pct(alone['share_of_net_percent'])} of net ({pts(alone['concentration_points'])} "
        f"points). P-C **{pc['verdict']}** on the rule it is judged on"
        + (
            "; it would hold on the determined reading, so the margin is one the identity "
            "rule decides, not the register."
            if pc["verdict"] == "fails"
            and det_points is not None
            and abs(det_points) <= Decimal(15)
            else "."
        ),
        f"- **What the by-technology reading rests on**: {pct(changed_share)} of the window's "
        "dated capacity printed a different plant type at the two ends and is in the "
        "key-changed bucket, never reassigned; the technology shares above are shares of the "
        "whole, that bucket included.",
        "",
        "A share of net above a share of capacity says the register's dates for that group "
        "carried less information over this window than the rest's; it does not say why, and "
        "006's split (three fifths project-led, a quarter works-led, the rest unattributable) "
        "is the only cause evidence this project holds.",
    ]


def key_changed_section(
    comparisons: Rows, groups_by_key: dict[str, Rows], stability: dict[str, Any] | None
) -> list[str]:
    """What the key-changed bucket holds, from the committed schema report:
    the copies inside each window at which the schema pass counted a change
    of the printed key between consecutive copies. Those counts are over
    every project-stage printed in both copies of each consecutive pair,
    not only the dated population, so they bound the bucket, they do not
    equal it."""
    lines = [
        "## What the key-changed bucket holds",
        "",
        "A project-stage whose plant type or host TO reads differently at the two ends of a "
        "window is in the key-changed bucket (R2). The schema pass "
        "(`archives/tec-register/schema-report.json`) counts, between every pair of "
        "consecutive copies, the project-stages whose printed key changed; for each window "
        "whose bucket holds at least 5 % of dated capacity, the copies inside it where that "
        "count was largest are listed. The counts are over every project-stage printed in "
        "both copies of a pair, not only the dated population, so they bound the bucket "
        "rather than equal it.",
        "",
    ]
    if stability is None:
        return [*lines, "The schema report was not given to the renderer; nothing listed."]
    rows = []
    for c in comparisons:
        kc = next((g for g in groups_by_key[c["key"]] if g["group"] == "key changed"), None)
        if kc is None or Decimal(kc["share_of_capacity_percent"] or 0) < FOLD_BELOW:
            continue
        field = f"{c['dimension']}_changed"
        inside = [
            x
            for x in stability["copies_with_a_change"]
            if c["baseline"] < x["t_public"] <= c["current"] and x.get(field, 0) > 0
        ]
        total = sum(x[field] for x in inside)
        top = sorted(inside, key=lambda x: -x[field])[:3]
        named = ", ".join(f"{x['t_public']} ({x[field]:,})" for x in top) or "none"
        rows.append(
            f"- {window_label(c)}, by {dimension_label(c['dimension'])}: bucket "
            f"{kc['dated_both']:,} dated project-stages, {pct(kc['share_of_capacity_percent'])} "
            f"of dated capacity, {whole(kc['total'][RULE_V2])} MW-years; the schema pass counts "
            f"{total:,} key changes between consecutive copies inside the window, most at {named}."
        )
    return [*lines, *(rows or ["No window's bucket reaches 5 % of dated capacity."])]


# -------------------------------------------------------------------- page


def expert_corner(summary: dict[str, Any], comparisons: Rows) -> list[str]:
    proofs = (summary.get("declaration_timestamps") or {}).get("proofs", [])
    witnessed = ", ".join(
        " ".join(str(p.get(k)) for k in ("kind", "tsa", "status") if p.get(k)) for p in proofs
    )
    copies = summary["copies"]
    rows = summary["rows"]
    return [
        "## Expert corner",
        "",
        f"- Declaration `DECLARATION.md` SHA-256 `{summary['declaration_sha256']}`; "
        f"proofs: {witnessed or 'none recorded'}.",
        f"- Schema pass `archives/tec-register/schema-report.json` SHA-256 "
        f"`{summary['schema_report_sha256']}`; 014 version 4 manifest SHA-256 "
        f"`{summary['v4_manifest_sha256']}` ({copies['usable']} usable copies, "
        f"{copies['first']} to {copies['last']}, C1 passed); content rule SHA-256 "
        f"`{summary['content_rule_sha256']}` (C5 passed).",
        f"- C2: every one of the {len(comparisons) // 2} comparisons recomputed to 014 version "
        "4's committed net, determined part, undetermined group count, dated count and "
        "weighted capacity exactly. C3 and C4 passed on every group (the determined part is "
        "rule-independent; counts and capacities sum exactly; nets within rounding).",
        f"- Rule version `{summary['rule_version']}`; rows appended: "
        f"{rows['comparisons_appended']} comparison lines and {rows['groups_appended']} group "
        f"lines; unfit comparisons (F-G4): {', '.join(summary['unfit']) or 'none'}; shares "
        f"not read (R9): {', '.join(summary['not_read']) or 'none'}.",
        "- Shares are over every bucket of a comparison, key changed and (blank) included, so "
        "they sum to 100 % up to rounding; a group's concentration is its share of net minus "
        "its share of dated capacity, both under version 2's rule. Counts and capacities are "
        "under version 2's rule; movement figures are given under both rules.",
    ]


def render_findings(
    summary: dict[str, Any],
    comparisons: Rows,
    groups: Rows,
    stability: dict[str, Any] | None = None,
) -> str:
    version = summary["rule_version"]
    comparisons = [c for c in comparisons if c["rule_version"] == version]
    groups_by_key: dict[str, Rows] = {}
    for g in groups:
        if g["rule_version"] == version:
            groups_by_key.setdefault(g["key"].rsplit("|", 1)[0], []).append(g)
    headline = {c["dimension"]: c for c in comparisons if c["window"] == "headline"}
    years = [c for c in comparisons if c["regime"] == "old" and c["window"] != "headline"]
    links = [c for c in comparisons if c["regime"] == "new"]
    hh, hp = headline["host_to"], headline["plant_type"]
    run = (
        f"*Declaration `DECLARATION.md`, SHA-256 `{summary['declaration_sha256']}`, frozen and "
        f"witnessed before any figure here was computed. Run {summary['run_date']} under seal "
        f"`{summary['seal']}`, rule version `{version}`. Every figure is from "
        "`evidence/comparisons.ndjson` and `evidence/groups.ndjson`, which carry three "
        "decimals; this page shows megawatt-years to the nearest whole unit and shares to "
        "0.1 %.*"
    )
    lines = [
        f"# {TITLE}",
        "",
        run,
        "",
        "## The mystery",
        "",
        "When Britain's contracted grid-connection dates move, in aggregate, is the movement "
        "concentrated in particular technologies or in particular transmission areas, or is "
        "it spread in proportion to the capacity each holds?",
        "",
        "## The reading, and what it is not",
        "",
        "The date read here is the one in each project's connection agreement as the TEC "
        "Register prints it, moved by agreed variation between two copies of the register; "
        "it is never a promise, and nothing here says why any of them moved. The reading "
        "offered is **how much information a register date carries by technology and by "
        "area**: a group whose share of net movement exceeds its share of dated capacity is "
        "a group whose dates, over that window and under this reading, carried less "
        "information than the rest. It is not a reading of who is to blame. " + CAUSE_SPLIT,
        "",
        "The population and arithmetic are 014 version 4's, unchanged (C1 and C2 pass, see "
        "the expert corner): for every project-stage present in both copies with a date in "
        "both, its capacity at the baseline times the years its date moved, later positive. "
        "A project-stage whose plant type or host TO reads differently at the two ends is in "
        "the **key changed** bucket and is never reassigned (R2); a blank key is the group "
        "(blank) (R3); compound plant types are kept whole (R1). Every group's net is split "
        "into the part the register's stage labels determine and the part that depends on "
        "the identity rule, as 014 version 4 splits the series.",
        "",
        f"## The headline window, {window_label(hh)}",
        "",
        comparison_sentence(hh),
        "",
        "### By host transmission owner",
        "",
        *group_table(groups_by_key[hh["key"]], "Host TO"),
        "",
        f"Marks: {marks(hh) or 'none'}.",
        "",
        "### By plant type",
        "",
        comparison_sentence(hp),
        "",
        *group_table(groups_by_key[hp["key"]], "Plant type"),
        "",
        f"Marks: {marks(hp) or 'none'}.",
        "",
        "### The storage reading, two ways",
        "",
        "The register prints compound plant types and this cut keeps them whole, so energy "
        "storage can be read as the label alone or as every group with the label among its "
        "components. Both are reported; neither is the right one.",
        "",
        *storage_lines(hp),
        "",
        CAUSE_SPLIT,
        "",
        *proposition_lines(summary["propositions"]),
        "",
        *conclusion(summary, hh, hp, groups_by_key),
        "",
        *key_changed_section(comparisons, groups_by_key, stability),
        "",
        "## The calendar-year windows of the old regime",
        "",
        "Each complete calendar year as 014 lists it (first copy on or after 1 January to the "
        "first copy on or after the next). The 2020 window spans the register's relabelling "
        "of 2020-06-05 and is where the key-changed bucket is expected to be largest.",
        "",
        *year_tables(groups_by_key, years),
        "",
        "## The reformed regime, copy to copy",
        "",
        "The copies from 2026-05-19 carry re-baselined dates and are compared copy to copy, "
        "never with the old regime.",
        "",
        *year_tables(groups_by_key, links),
        "",
        "## What this never claims",
        "",
        "Everything 014 never claims, and: that a technology or an area is worse at "
        "anything; that a compound label says which technology moved; that any project will "
        "connect, or when. A group's concentration reading is a property of the register's "
        "dates over one window under one reading, with the 006 cause split standing "
        "unrevised beside it.",
        "",
        *expert_corner(summary, comparisons),
        "",
        "## Reproducibility",
        "",
        "```",
        "uv run --group registers python "
        f"investigations/021-slippage-by-technology-and-area/run.py --seal {summary['seal']} "
        "--phase check",
        "uv run python investigations/021-slippage-by-technology-and-area/run.py --phase render",
        "scripts/check",
        "```",
        "",
    ]
    return "\n".join(lines)
