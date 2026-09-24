"""GB Connection Slippage: the public page and the record page of 014.

Both are pure functions of `evidence/series.json`: every number comes from
that file, nothing is computed here beyond formatting, and the same
evidence always renders the same bytes. The HTML is self-contained (inline
CSS, no script, no external asset), in the Balancing Bill's format.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from html import escape
from typing import Any

TITLE = "GB Connection Slippage"
SUBTITLE = "How far Britain's contracted grid-connection dates have moved, in megawatt-years"
REPO_URL = "https://github.com/jordan-dimov/grid-mysteries"
INVESTIGATION_PATH = "investigations/014-gb-connection-slippage"
CREDIBILITY = (
    "Built by Jordan Dimov, A115. Previously built trading and settlement systems "
    "at Shell, Centrica and Limejump."
)
CALL_TO_ACTION = (
    "Need the register's history for one project, as it stood on a given date? jdimov@a115.co.uk"
)
CALL_TO_ACTION_EMAIL = "jdimov@a115.co.uk"

INTRO = (
    "Every generator, battery or interconnector that wants to plug into Britain's "
    "high-voltage grid holds a contract with a target connection date, and the "
    "grid operator publishes the list twice a week, overwriting the last copy. "
    "This page keeps the copies. For projects on the list at both ends of a "
    "period, it adds up how far each target date moved, weighted by the "
    "project's capacity: a 100 MW project whose date moves one year later "
    "counts 100 megawatt-years. Projects that joined, left or changed size in "
    "the period are listed beside the total, never inside it."
)

BLANK = "—"
#: Dated page corrections, kept beside the declarations and attached to the
#: series by the runner; each keeps the old and the new value.
CORRECTIONS_FILE = "corrections.json"


# ---------------------------------------------------------------- formatting


def whole(value: str) -> Decimal:
    """Rounded to a whole unit, halves up, for the page only."""
    return Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def mw_years(value: str | None) -> str:
    if value is None:
        return BLANK
    return f"{whole(value):,}"


def mw(value: str | None) -> str:
    if value is None:
        return BLANK
    return f"{whole(value):,}"


def count(value: int | None) -> str:
    return BLANK if value is None else f"{value:,}"


def day_label(iso: str | None) -> str:
    if not iso:
        return BLANK
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def signed_mw_years(value: str | None) -> str:
    if value is None:
        return BLANK
    number = whole(value)
    return f"+{number:,}" if number > 0 else f"{number:,}"


# ---------------------------------------------------------------------- rows


PAIR_COLUMNS = (
    "From",
    "To",
    "Project-stages at both dates",
    "Dated at both ends",
    "Net movement, MW-years",
    "Moved later, MW-years",
    "Moved earlier, MW-years",
    "Dates later / earlier / unchanged",
    "Joined (MW)",
    "Left (MW)",
    "Capacity changed (net MW)",
    "F2 thin population",
)


#: With a split (declaration 3 onwards): the determined part, the number of
#: groups whose pairing is undetermined, and each named rule's net, in place
#: of the single net; the gross sides are version 2's rule's.
SPLIT_COLUMNS = (
    "From",
    "To",
    "Project-stages at both dates",
    "Dated at both ends",
    "Determined by stage labels, MW-years",
    "Groups not determined",
    "Net, version 2's rule, MW-years",
    "Net, content matching, MW-years",
    "Moved later, MW-years (version 2's rule)",
    "Moved earlier, MW-years (version 2's rule)",
    "Dates later / earlier / unchanged",
    "Joined (MW)",
    "Left (MW)",
    "Capacity changed (net MW)",
    "F2 thin population",
)
RULE_V2 = "014-v2"
RULE_CONTENT = "tec-identity-content-v1"


#: A copy-to-copy comparison (the reformed segment's table, declaration 3
#: onwards): F1 is the link's falsifier and is listed before its figures
#: (declaration 1); F2 is defined on trailing-year comparisons only.
LINK_COLUMNS = SPLIT_COLUMNS[:2] + ("F1 churn",) + SPLIT_COLUMNS[2:-1]
F1_TEXT = "F1: joined plus left over 20% of baseline"


def f1_cell(pair: dict[str, Any]) -> str:
    return F1_TEXT if pair["f1_churn"] else BLANK


def columns(split: bool) -> tuple[str, ...]:
    return SPLIT_COLUMNS if split else PAIR_COLUMNS


def link_cells(pair: dict[str, Any]) -> list[str]:
    """The cells of one copy-to-copy comparison with a split (LINK_COLUMNS)."""
    cells = pair_cells(pair)[:-1]
    return cells[:2] + [f1_cell(pair)] + cells[2:]


def pair_cells(pair: dict[str, Any]) -> list[str]:
    """The cells of one baseline-to-current comparison, as plain text."""
    split = pair.get("split")
    if split:
        return [
            day_label(pair["baseline"]),
            day_label(pair["current"]),
            count(pair["matched"]),
            count(pair["dated_both"]),
            signed_mw_years(split["determined"]),
            count(split["undetermined_groups"]),
            signed_mw_years(split["total"][RULE_V2]),
            signed_mw_years(split["total"][RULE_CONTENT]),
            mw_years(pair["mw_years_later"]),
            mw_years(pair["mw_years_earlier"]),
            f"{pair['later']:,} / {pair['earlier']:,} / {pair['unchanged']:,}",
            f"{pair['new_entries']:,} ({mw(pair['new_mw'])})",
            f"{pair['removed']:,} ({mw(pair['removed_mw'])})",
            f"{pair['capacity_changed']:,} ({signed_mw(pair['capacity_delta_mw'])})",
            "F2: matched under half of baseline" if pair.get("f2_thin") else BLANK,
        ]
    return [
        day_label(pair["baseline"]),
        day_label(pair["current"]),
        count(pair["matched"]),
        count(pair["dated_both"]),
        signed_mw_years(pair["mw_years_net"]),
        mw_years(pair["mw_years_later"]),
        mw_years(pair["mw_years_earlier"]),
        f"{pair['later']:,} / {pair['earlier']:,} / {pair['unchanged']:,}",
        f"{pair['new_entries']:,} ({mw(pair['new_mw'])})",
        f"{pair['removed']:,} ({mw(pair['removed_mw'])})",
        f"{pair['capacity_changed']:,} ({signed_mw(pair['capacity_delta_mw'])})",
        "F2: matched under half of baseline" if pair.get("f2_thin") else BLANK,
    ]


def signed_mw(value: str | None) -> str:
    if value is None:
        return BLANK
    number = whole(value)
    return f"+{number:,}" if number > 0 else f"{number:,}"


def render_pair_table(
    pairs: list[dict[str, Any]], first_label: str | None = None, *, links: bool = False
) -> str:
    """`links`: copy-to-copy comparisons, which carry F1 instead of F2 when split."""
    split = any(p.get("split") for p in pairs)
    as_links = links and split
    names = list(LINK_COLUMNS if as_links else columns(split))
    if first_label:
        names = [first_label] + names
    head = "".join(f'<th scope="col">{escape(c)}</th>' for c in names)
    body_rows = []
    for pair in pairs:
        cells = link_cells(pair) if as_links else pair_cells(pair)
        if first_label:
            label = str(pair.get("label", ""))
            cells = [label] + cells
        first = f'<th scope="row">{escape(cells[0])}</th>'
        rest = "".join(f"<td>{escape(c)}</td>" for c in cells[1:])
        cls = ' class="partial"' if pair.get("partial") else ""
        body_rows.append(f"<tr{cls}>{first}{rest}</tr>")
    body = "\n".join(body_rows)
    return f"<table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>"


def annual_pairs(segment: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for a in segment.get("annual", []):
        label = (
            f"{a['year']} (to {day_label(a['current'])}, partial)"
            if a["partial"]
            else str(a["year"])
        )
        out.append({**a, "label": label})
    return out


ROWS_WINDOW_DAYS = 400


def recent_rows(segment: dict[str, Any]) -> list[dict[str, Any]]:
    """The segment's rows from the last ROWS_WINDOW_DAYS before its last copy;
    the full history is the rows file the page links."""
    if not segment["rows"]:
        return []
    last = date.fromisoformat(segment["last"])
    return [
        r
        for r in segment["rows"]
        if (last - date.fromisoformat(r["t_public"])).days <= ROWS_WINDOW_DAYS
    ]


def vintage_pairs(segment: dict[str, Any]) -> list[dict[str, Any]]:
    """Newest first: each recent copy against its year-earlier baseline."""
    out = []
    for row in reversed(recent_rows(segment)):
        pair = row.get("vs_year_earlier")
        if pair is None:
            continue
        split = (row.get("split") or {}).get("vs_year_earlier")
        out.append({**pair, "label": day_label(row["t_public"]), "split": split})
    return out


def increment_rows(segment: dict[str, Any]) -> str:
    """Newest first: each vintage against the previous one, with the chain."""
    split = any(r.get("split") for r in segment["rows"])
    names = (
        (
            "Vintage",
            "Previous vintage",
            "F1 churn",
            "Since previous, determined by stage labels, MW-years",
            "Groups not determined",
            "Since previous, version 2's rule, MW-years",
            "Since previous, content matching, MW-years",
            "Chained, determined by stage labels, MW-years",
            "Chained, version 2's rule, MW-years",
            "Chained, content matching, MW-years",
            "Joined",
            "Left",
            "Day-month swap test",
        )
        if split
        else (
            "Vintage",
            "Previous vintage",
            "Net movement since previous, MW-years",
            "Chained total since segment start, MW-years",
            "Joined",
            "Left",
            "F1 churn",
            "Day-month swap test",
        )
    )
    head = "".join(f'<th scope="col">{escape(c)}</th>' for c in names)
    rows = []
    for row in reversed(recent_rows(segment)):
        pair = row.get("vs_previous")
        test = row["swap_test"]
        flag = (
            f"read swapped ({test['swap_explained']} of {test['disagreements']})"
            if test["flagged"]
            else ("clean" if pair else BLANK)
        )
        chained = (row.get("split") or {}).get("chained")
        chain_cells = (
            [
                signed_mw_years(chained["determined"]),
                signed_mw_years(chained["total"][RULE_V2]),
                signed_mw_years(chained["total"][RULE_CONTENT]),
            ]
            if split and chained
            else [signed_mw_years(row["cumulative_mw_years_net"])]
        )
        f1 = f1_cell(pair) if pair else BLANK
        if split:
            link = (row.get("split") or {}).get("vs_previous")
            cells = [
                day_label(row["t_public"]),
                day_label(pair["baseline"]) if pair else BLANK,
                f1,
                *(
                    [
                        signed_mw_years(link["determined"]),
                        count(link["undetermined_groups"]),
                        signed_mw_years(link["total"][RULE_V2]),
                        signed_mw_years(link["total"][RULE_CONTENT]),
                    ]
                    if pair and link
                    else [BLANK] * 4
                ),
                *chain_cells,
                count(pair["new_entries"]) if pair else BLANK,
                count(pair["removed"]) if pair else BLANK,
                flag,
            ]
        else:
            cells = [
                day_label(row["t_public"]),
                day_label(pair["baseline"]) if pair else BLANK,
                signed_mw_years(pair["mw_years_net"]) if pair else BLANK,
                *chain_cells,
                count(pair["new_entries"]) if pair else BLANK,
                count(pair["removed"]) if pair else BLANK,
                f1,
                flag,
            ]
        first = f'<th scope="row">{escape(cells[0])}</th>'
        rest = "".join(f"<td>{escape(c)}</td>" for c in cells[1:])
        rows.append(f"<tr>{first}{rest}</tr>")
    return (
        f"<table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table>"
    )


def unsigned(value: str | None) -> str:
    """Magnitude only, for prose that already names the direction."""
    if value is None:
        return BLANK
    return f"{abs(whole(value)):,}"


def headline_row(series: dict[str, Any]) -> dict[str, Any] | None:
    """The year-earlier comparison of the headline copy, from the rows."""
    h = series.get("headline")
    if not h:
        return None
    for segment in series["segments"]:
        for row in segment.get("rows", []):
            if row["t_public"] == h["t_public"] and row.get("vs_year_earlier"):
                return row["vs_year_earlier"]
    return None


def annual_sum(segment: dict[str, Any]) -> Decimal:
    """The year windows' net movements added up (formatting arithmetic only)."""
    return sum((Decimal(a["mw_years_net"]) for a in segment.get("annual", [])), Decimal(0))


def percent(value: str | None) -> str:
    return BLANK if value is None else f"{Decimal(value):.1f}%"


RULE_NAMES = {RULE_V2: "version 2's rule", RULE_CONTENT: "content matching"}


def thin_years(segment: dict[str, Any]) -> list[dict[str, Any]]:
    """Year windows whose determined part is under half of the year's figure
    under at least one of the two rules (compared in absolute value)."""
    out = []
    for window in segment.get("annual", []):
        split = window.get("split")
        if not split:
            continue
        determined = Decimal(split["determined"])
        rules = [
            rule
            for rule in (RULE_V2, RULE_CONTENT)
            if abs(determined) * 2 < abs(Decimal(split["total"][rule]))
        ]
        if rules:
            out.append({**window, "rules": rules})
    return out


def year_label(window: dict[str, Any]) -> str:
    return f"{window['year']} (partial)" if window["partial"] else str(window["year"])


def join_words(words: list[str]) -> str:
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def determined_share_sentence(series: dict[str, Any]) -> str | None:
    """Which years of the year-by-year table rest mostly on pairings the
    register does not determine, computed from the evidence."""
    old = next((s for s in series["segments"] if s["regime"] == "old"), None)
    if not old or not any(w.get("split") for w in old.get("annual", [])):
        return None
    years = thin_years(old)
    if not years:
        return (
            "In every year of the table the movement the register's stage labels determine "
            "is at least half of the year's figure under both rules."
        )
    details = []
    for w in years:
        split = w["split"]
        figures = " and ".join(
            f"{signed_mw_years(split['total'][rule])} under {RULE_NAMES[rule]}"
            for rule in w["rules"]
        )
        details.append(f"{year_label(w)}, {signed_mw_years(split['determined'])} of {figures}")
    return (
        f"In {join_words([year_label(w) for w in years])} the movement the register's stage "
        "labels determine is under half of the year's figure under at least one rule: "
        + "; ".join(details)
        + ". In those years more than half of that figure comes from project groups whose "
        "pairing the register does not determine."
    )


def split_headline_sentence(series: dict[str, Any]) -> str:
    """Declarations 3 and 4: the determined part, then each named rule; the
    wording is the frozen declaration's, the numbers are the evidence's."""
    h = series["headline"]
    split = h["split"]
    year = split["vs_year_earlier"]
    old = next((s for s in series["segments"] if s["regime"] == "old"), None)
    missing = (
        ", or that went missing from a copy between,"
        if series.get("split", {}).get("definition") == "path"
        else ""
    )
    between = ", at either end or in any copy between" if missing else ""
    sentence = (
        f"Between {day_label(h['baseline'])} and {day_label(h['t_public'])}, "
        f"{h['matched']:,} project-stages were on the register at both dates and "
        f"{h['dated_both']:,} of them carried a connection date on both copies. "
        f"{signed_mw_years(year['determined'])} MW-years is movement the register's own "
        f"stage labels determine. {year['undetermined_groups']:,} project groups that were "
        f"split, merged, renumbered or printed repeated stages{between}{missing} add "
        f"{signed_mw_years(year['undetermined'][RULE_V2])} under version 2's rule and "
        f"{signed_mw_years(year['undetermined'][RULE_CONTENT])} under content matching, so "
        f"the headline is {signed_mw_years(year['total'][RULE_V2])} or "
        f"{signed_mw_years(year['total'][RULE_CONTENT])} depending on the rule; other "
        "pairings are possible and are not bounded here."
    )
    if old:
        shares = split["undetermined_share_percent"]
        sentence += (
            f" Chained copy to copy across the old regime only ({old['vintages']:,} copies, "
            f"{day_label(old['first'])} to {day_label(old['last'])}; the reformed regime is a "
            f"separate series), the movement the stage labels determine is "
            f"{signed_mw_years(split['determined'])} megawatt-years; with the rest it is "
            f"{signed_mw_years(split['total'][RULE_V2])} under version 2's rule "
            f"({percent(shares[RULE_V2])} undetermined) or "
            f"{signed_mw_years(split['total'][RULE_CONTENT])} under content matching "
            f"({percent(shares[RULE_CONTENT])} undetermined). Under version 2's rule the chain "
            f"exceeds the sum of the year windows below "
            f"({signed_mw_years(str(annual_sum(old)))}) because it also counts "
            "project-stages present in two consecutive copies but not at both ends of a year."
        )
    return sentence


def headline_sentence(series: dict[str, Any]) -> str:
    h = series.get("headline")
    if not h:
        return "No vintage yet has a baseline a year earlier, so there is no headline."
    if h.get("split"):
        return split_headline_sentence(series)
    pair = headline_row(series) or {}
    old = next((s for s in series["segments"] if s["regime"] == "old"), None)
    counts = (
        f" Among those, {pair['later']:,} moved later, {pair['earlier']:,} earlier and "
        f"{pair['unchanged']:,} did not move."
        if pair
        else ""
    )
    chain = ""
    if old:
        chain = (
            f" Chained copy to copy across the old regime only ({old['vintages']:,} copies, "
            f"{day_label(old['first'])} to {day_label(old['last'])}; the reformed regime is a "
            f"separate series), the movement is "
            f"{signed_mw_years(h['cumulative_mw_years_net'])} megawatt-years. That exceeds the "
            f"sum of the year windows below ({signed_mw_years(str(annual_sum(old)))}) because "
            "the chain also counts project-stages present in two consecutive copies but not at "
            "both ends of a year."
        )
    return (
        f"Between {day_label(h['baseline'])} and {day_label(h['t_public'])}, "
        f"{h['matched']:,} project-stages were on the register at both dates and "
        f"{h['dated_both']:,} of them carried a connection date on both copies.{counts} "
        f"Their dates moved by a net {signed_mw_years(h['mw_years_net'])} megawatt-years "
        f"({unsigned(h['mw_years_later'])} later, {unsigned(h['mw_years_earlier'])} "
        f"earlier).{chain}"
    )


def render_propositions(series: dict[str, Any]) -> str:
    props = series.get("propositions") or {}
    p1, p2 = props.get("P1"), props.get("P2")
    if not p1 or not p2:
        return "<p>Not yet computed.</p>"
    p1_text = (
        f"<strong>P1</strong>: {escape(p1['statement'])}: <strong>{escape(p1['verdict'])}</strong>"
    )
    if p1["windows"]:
        p1_text += (
            f" over {len(p1['windows'])} complete years ({p1['windows'][0]} to {p1['windows'][-1]})"
        )
    if p1["failing_years"]:
        p1_text += "; not positive in " + ", ".join(str(y) for y in p1["failing_years"])
    p2_text = (
        f"<strong>P2</strong>: {escape(p2['statement'])}: <strong>{escape(p2['verdict'])}</strong>"
        f" (falsifier date {escape(day_label(p2['falsifier_date']))}"
    )
    if p2.get("decided_on"):
        p2_text += (
            f"; decided on the copy of {escape(day_label(p2['decided_on']))}, "
            f"chained {escape(signed_mw_years(p2['chained_mw_years_net']))} MW-years"
        )
    p2_text += ")"
    f1 = series.get("f1_links") or []
    f2 = series.get("f2_rows") or []
    flags = (
        f"<strong>F1</strong> fired on {len(f1)} link(s) between consecutive copies; "
        f"<strong>F2</strong> fired on {len(f2)} year-on-year row(s). "
        "Both are marked in the tables."
    )
    return f"<ul><li>{p1_text}.</li><li>{p2_text}.</li><li>{flags}</li></ul>"


def render_corrections(corrections: list[dict[str, Any]] | None) -> str:
    if not corrections:
        return (
            "<p>None so far. When a figure on this page is corrected, the correction "
            "is listed here with its date and the old and new values; the old value "
            "is never silently overwritten.</p>"
        )
    items = "".join(
        f'<li><time datetime="{escape(c["date"])}">{escape(day_label(c["date"]))}</time>: '
        f"{escape(c['text'])}</li>"
        for c in corrections
    )
    return f"<ol>{items}</ol>"


def plain_reason(skipped: dict[str, Any]) -> str:
    """A reader's reason for a copy the archive holds but the reader cannot parse."""
    error = str(skipped.get("error", ""))
    path = str(skipped.get("path", ""))
    if path.endswith(".xls") and error.startswith("AssertionError"):
        return "2014 .xls layout the spreadsheet reader rejects"
    if "no header" in error:
        return "no header row found"
    return error


def render_gaps(series: dict[str, Any]) -> str:
    items = []
    rb = series.get("regime_break")
    if rb:
        items.append(
            f"<li><strong>Regime break.</strong> No copy is held between "
            f"{day_label(rb['last_old'])} and {day_label(rb['first_new'])} ({rb['days']} days): "
            f"the grid operator's connections-reform re-baselining. Copies from December 2025 "
            f"onward are a separate series below and are never chained to the earlier one.</li>"
        )
    for seg in series["segments"]:
        for hole in seg.get("holes", []):
            items.append(
                f"<li>No copy held between {day_label(hole['from'])} and "
                f"{day_label(hole['to'])} ({hole['days']} days)."
                + (
                    " That is the regime break above."
                    if rb and hole["from"] == rb["last_old"]
                    else ""
                )
                + "</li>"
            )
        for swapped in seg.get("swapped_vintages", []):
            items.append(
                f"<li>The copy of {day_label(swapped)} carried dates with day and month "
                f"exchanged; it is read with them exchanged back.</li>"
            )
    for s in series.get("suspect_copies", []):
        items.append(
            f"<li>The copy of {day_label(s['t_public'])} is a <strong>suspect copy</strong>: "
            f"{escape(s['note'])}; "
            + (
                "the next copy recovered, so it is left out of the series."
                if s.get("excluded")
                else "the shrink persisted, so it stays in the series and is marked here."
            )
            + "</li>"
        )
    skipped = series.get("vintages", {}).get("skipped", [])
    excluded = series.get("vintages", {}).get("excluded", [])
    if skipped:
        items.append(
            f"<li>{len(skipped)} held copies could not be parsed and are not in the series "
            f"({', '.join(day_label(s['t_public']) for s in skipped[:6])}"
            + (", …" if len(skipped) > 6 else "")
            + ").</li>"
        )
    if excluded:
        items.append(
            f"<li>{len(excluded)} held copies lack a column the series needs and are not in it "
            f"({', '.join(day_label(s['t_public']) for s in excluded)}).</li>"
        )
    return "<ul>" + "".join(items) + "</ul>" if items else "<p>None.</p>"


CSS = """\
:root{--ink:#1c1c1c;--muted:#5d5d5d;--rule:#d9d9d9;--bg:#fbfaf7;--seed:#eef0f4;--rec:#8a1c1c}
*{box-sizing:border-box}
body{margin:0;padding:1.25rem 1rem 3rem;background:var(--bg);color:var(--ink);
font:16px/1.5 Georgia,"Times New Roman",serif;max-width:72rem;margin-inline:auto}
h1{font-size:2rem;line-height:1.15;margin:0 0 .25rem}
h2{font-size:1.2rem;margin:2rem 0 .5rem}
.subtitle{color:var(--muted);font-size:1.1rem;margin:0 0 1.25rem}
p{max-width:44rem}
.headline{font-size:1.15rem;max-width:44rem;border-left:4px solid var(--rec);padding-left:1rem}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:1rem -1rem;padding:0 1rem}
table{border-collapse:collapse;width:100%;min-width:64rem;font-size:.9rem;
font-family:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
th,td{padding:.45rem .5rem;border-bottom:1px solid var(--rule);text-align:right;
vertical-align:top;white-space:nowrap}
thead th{text-align:right;font-weight:600;color:var(--muted);white-space:normal;
vertical-align:bottom;font-size:.8rem}
thead th:first-child,tbody th{text-align:left}
tbody th{font-weight:600}
tr.partial td,tr.partial th{color:var(--muted)}
details{margin:1rem 0}
summary{cursor:pointer;font-weight:600}
.notes{font-size:.9rem;color:var(--muted);max-width:44rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--rule);
font-size:.95rem;color:var(--muted)}
a{color:inherit}
@media (max-width:600px){body{padding:1rem .75rem 2rem}h1{font-size:1.6rem}
table{font-size:.8rem}th,td{padding:.35rem .4rem}}
"""


def evidence_dir_of(declaration_name: str) -> str:
    """`evidence` for the first declaration, `evidence/vN` for `DECLARATION-vN.md`."""
    if declaration_name == "DECLARATION.md":
        return "evidence"
    return "evidence/" + declaration_name.removeprefix("DECLARATION-").removesuffix(".md")


SPLIT_NOTE = (
    "Where a project prints several rows, the register does not always say which row of "
    "one copy is which row of another: when its stages were split, merged or renumbered, "
    "printed the same stage twice, or went missing from a copy in between. Movement in "
    "every other project is determined by the register's own stage labels, and every "
    "identity rule that pairs a stage with the stage of the same label gives the same "
    "figure. For the rest this page gives the figure under two named rules: version 2's "
    "rule (rows numbered by date) and content matching (rows followed by their capacity "
    "and date). The two are not bounds; other pairings are possible."
)


def render_page(series: dict[str, Any], repo_url: str = REPO_URL) -> str:
    declaration_name = series.get("declaration", "DECLARATION.md")
    declaration = f"{repo_url}/blob/main/{INVESTIGATION_PATH}/{declaration_name}"
    evidence_dir = evidence_dir_of(declaration_name)
    evidence = f"{repo_url}/tree/main/{INVESTIGATION_PATH}/{evidence_dir}"
    rows_note = (
        f" The two tables of individual copies show the last {ROWS_WINDOW_DAYS} days; "
        f"every copy since 2014 is one line of <code>{evidence_dir}/"
        f"{escape(series.get('rows_file', 'series.json'))}</code>, appended and never rewritten."
        if series.get("rows_file")
        else ""
    )
    digest = series.get("declaration_sha256", "")
    corrections_note = (
        f" and of <code>{escape(CORRECTIONS_FILE)}</code>" if series.get("corrections") else ""
    )
    old = next((s for s in series["segments"] if s["regime"] == "old"), None)
    new = next((s for s in series["segments"] if s["regime"] == "new"), None)
    prompt, email = CALL_TO_ACTION.removesuffix(CALL_TO_ACTION_EMAIL), CALL_TO_ACTION_EMAIL
    contact = f'{escape(prompt)}<a href="mailto:{email}">{email}</a>'
    coverage = (
        f" The series is built from {old['vintages']:,} copies of the register, "
        f"{day_label(old['first'])} to {day_label(old['last'])}"
        if old
        else ""
    )
    if new:
        coverage += (
            f", plus {new['vintages']} copies since {day_label(new['first'])} "
            "under the reformed regime"
        )
    coverage += "." if coverage else ""
    split_note = (
        f'<p class="notes">{escape(SPLIT_NOTE)}</p>\n'
        if (series.get("headline") or {}).get("split")
        else ""
    )
    old_annual = render_pair_table(annual_pairs(old), "Year") if old else "<p>No copies.</p>"
    share = determined_share_sentence(series)
    share_note = f"<p>{escape(share)}</p>\n" if share else ""
    old_vintages = render_pair_table(vintage_pairs(old), "Copy of") if old else ""
    old_increments = increment_rows(old) if old else ""
    new_block = ""
    if new:
        new_pairs = []
        for row in reversed(new["rows"]):
            pair = row.get("vs_previous")
            if pair is not None:
                split = (row.get("split") or {}).get("vs_previous")
                new_pairs.append({**pair, "label": day_label(row["t_public"]), "split": split})
        new_table = (
            render_pair_table(new_pairs, "Copy of", links=True)
            if new_pairs
            else "<p>One copy only; nothing to compare yet.</p>"
        )
        new_block = f"""
<h2>Since the reform: a separate series</h2>
<p class="notes">From December 2025 the register carries dates re-baselined under the
grid operator's connections reform (Gate 2 offers). Movement across that change is
the reform, not slippage, so these copies form their own series, compared copy to
copy from {escape(day_label(new["first"]))}, and are never added to the figures above.</p>
<div class="scroll">
{new_table}
</div>
"""
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(TITLE)}</title>
<meta name="description" content="{escape(SUBTITLE)}">
<style>
{CSS}</style>
</head>
<body>
<header>
<h1>{escape(TITLE)}</h1>
<p class="subtitle">{escape(SUBTITLE)}</p>
</header>
<main>
<p>{escape(INTRO)}{escape(coverage)}</p>

<p class="headline">{escape(headline_sentence(series))}</p>
{split_note}
<h2>Year by year</h2>
<p class="notes">Each row compares the first copy of the register in one year with the
first copy of the next. <em>Project-stages at both dates</em> is the population the
movement is summed over; a project that was renamed, changed customer or changed
its connection site in between counts as having left and joined, never as moved.
<em>Dated at both ends</em> is how many of those carried a connection date on both
copies; only they can move, so the later, earlier and unchanged counts add up to it.
<em>Joined</em> and <em>left</em> show the count and the capacity in megawatts. A
positive movement is later; megawatt-years are rounded to whole numbers here and
kept to three decimals in the evidence file. The last column marks a comparison whose
population at both dates is under half of the earlier copy's rows (the declaration's
F2): the figure stands, and the reader is told it rests on a thin population. The
2020 and 2022 windows straddle the register's own format changes (a new column set
from June 2020; connection-site names respelled from December 2022), which the
earlier investigation found break the identity of many rows; F2 there reflects the
register, not the projects.</p>
<div class="scroll">
{old_annual}
</div>
{share_note}
<details>
<summary>Every copy against the copy a year earlier</summary>
<p class="notes">The same calculation for every copy held, each against the latest copy at
least 365 days before it. Newest first.</p>
<div class="scroll">
{old_vintages}
</div>
</details>

<details>
<summary>Every copy against the previous copy, and the chained total</summary>
<p class="notes">The movement between consecutive copies, and the running sum of those
movements since the first copy. The chain counts a project while it is present in two
consecutive copies, so it survives renames better than the year-on-year figure but
mixes populations across time. The last column reports the test for a copy whose
dates were published with day and month exchanged.</p>
<div class="scroll">
{old_increments}
</div>
</details>
{new_block}
<h2>Propositions, declared before the run</h2>
{render_propositions(series)}

<h2>Gaps, breaks and copies not used</h2>
{render_gaps(series)}

<h2>How the numbers are made</h2>
<p>The rules were written down and sealed before the series was computed, and the
sealed text is never edited afterwards. The list is the grid operator's TEC
Register (Transmission Entry Capacity), assembled from its own disclosures under
the Environmental Information Regulations, Wayback Machine captures and the live
data portal. A <em>project-stage</em> is one row of the register: the project's
name, customer and connection site together with its stage. Its <em>capacity</em>
is the stage's MW increase as published, and its <em>date</em> is the register's
effective-from date for that capacity. Movement is the difference between the two
dates in days divided by 365.25, times the capacity in the earlier copy, so a
change of capacity never enters the movement; it is reported beside it. Rows
without a parseable date on both sides, or without a capacity, are counted and
contribute nothing. Nothing here says why a date moved, whether a project will
connect, or what any party is entitled to; the grid operator's own caveat that
project status is its best-known classification applies throughout.</p>
<p class="notes">Declaration (SHA-256 <code>{escape(digest[:16])}…</code>):
<a href="{escape(declaration)}">{escape(INVESTIGATION_PATH)}/{escape(declaration_name)}</a>,
witnessed by OpenTimestamps and two RFC 3161 authorities before the series was computed.
Evidence, every copy's digest and every row:
<a href="{escape(evidence)}">{escape(evidence_dir)}/</a>.
Code and tests: <a href="{escape(repo_url)}">{escape(repo_url.removeprefix("https://"))}</a>.
Figures computed {escape(series.get("computed_at", "")[:10])} and read from
<code>{escape(evidence_dir)}/series.json</code>; the page is a pure function of the
evidence{corrections_note}.{rows_note}</p>

<h2>Corrections</h2>
{render_corrections(series.get("corrections"))}
</main>
<footer>
<p>{escape(CREDIBILITY)}</p>
<p>{contact}</p>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------- markdown


def md_pair_row(label: str, pair: dict[str, Any]) -> str:
    cells = pair_cells(pair)
    return "| " + " | ".join([label] + cells) + " |"


def markdown_propositions(series: dict[str, Any], *, sep: str = " —") -> list[str]:
    props = series.get("propositions") or {}
    p1, p2 = props.get("P1"), props.get("P2")
    if not p1 or not p2:
        return ["- Not yet computed."]
    lines = [
        f"- **P1**{sep} {p1['statement']}: **{p1['verdict']}** "
        f"({len(p1['windows'])} complete years"
        + (
            f"; not positive in {', '.join(str(y) for y in p1['failing_years'])}"
            if p1["failing_years"]
            else ""
        )
        + ").",
        f"- **P2**{sep} {p2['statement']}: **{p2['verdict']}** "
        f"(falsifier date {p2['falsifier_date']}"
        + (
            f"; decided on {p2['decided_on']}, chained {p2['chained_mw_years_net']} MW-years"
            if p2.get("decided_on")
            else ""
        )
        + ").",
        f"- **F1** fired on {len(series.get('f1_links') or [])} consecutive-copy link(s); "
        f"**F2** on {len(series.get('f2_rows') or [])} year-on-year row(s).",
    ]
    return lines


def render_markdown(series: dict[str, Any]) -> str:
    """SERIES.md: the record page kept beside the declaration."""
    old = next((s for s in series["segments"] if s["regime"] == "old"), None)
    new = next((s for s in series["segments"] if s["regime"] == "new"), None)
    counts = series.get("vintages", {})
    split = bool((series.get("headline") or {}).get("split"))
    names = columns(split)
    # Version 2's released record page keeps its wording; a split page names
    # its own evidence directory.
    evidence = evidence_dir_of(series.get("declaration", "DECLARATION.md")) if split else "evidence"
    head = "| " + " | ".join(["Year", *names]) + " |\n|" + "---|" * (len(names) + 1)
    annual = "\n".join(md_pair_row(p["label"], p) for p in annual_pairs(old)) if old else ""
    # Version 2's rows file is named as its record page named it; a split
    # page names the append-only rows file its declaration defines.
    rows_source = (
        f"{evidence}/{series.get('rows_file', 'series.json')}"
        if split
        else (f"{evidence}/series.json")
    )
    lines = [
        f"# {TITLE}{':' if split else ' —'} series (investigation 014)",
        "",
        f"*{SUBTITLE}. The page at `site/connection-slippage/index.html` and this file are pure "
        f"functions of `{evidence}/series.json`"
        + (f" and `{rows_source}`" if split else "")
        + ".*",
        "",
        f"**Declaration** `{series.get('declaration', 'DECLARATION.md')}`, SHA-256 "
        f"`{series.get('declaration_sha256', '')}`, witnessed before the run. "
        f"Computed {series.get('computed_at', '')[:19]}Z (run date {series.get('run_date', '')}). "
        f"Copies of the register: {counts.get('journal_rows', 0)} journal rows, "
        f"{counts.get('distinct_dates', 0)} distinct publication dates, "
        f"{counts.get('parsed', 0)} parsed, "
        f"{counts.get('usable', 0)} usable ({len(counts.get('skipped', []))} unparseable, "
        f"{len(counts.get('excluded', []))} lacking a required column).",
        "",
        "## Headline",
        "",
        headline_sentence(series),
        "",
        *([SPLIT_NOTE, ""] if (series.get("headline") or {}).get("split") else []),
        "## Propositions",
        "",
        *markdown_propositions(series, sep=":" if split else " —"),
        "",
        "## Year by year (old regime)",
        "",
        head,
        annual,
        "",
    ]
    share = determined_share_sentence(series)
    if share:
        lines += [share, ""]
    if new:
        lines += [
            "## Since the reform (separate series, copy to copy)",
            "",
            head.replace("Year", "Copy of", 1)
            if not split
            else "| "
            + " | ".join(["Copy of", *LINK_COLUMNS])
            + " |\n|"
            + "---|" * (len(LINK_COLUMNS) + 1),
        ]
        for row in reversed(new["rows"]):
            if row.get("vs_previous"):
                row_split = (row.get("split") or {}).get("vs_previous")
                pair = {**row["vs_previous"], "split": row_split}
                label = day_label(row["t_public"])
                lines.append(
                    "| " + " | ".join([label, *link_cells(pair)]) + " |"
                    if split and row_split
                    else md_pair_row(label, pair)
                )
        lines.append("")
    rb = series.get("regime_break")
    lines += ["## Gaps, breaks and copies not used", ""]
    if rb:
        lines.append(
            f"- Regime break: no copy between {rb['last_old']} and {rb['first_new']} "
            f"({rb['days']} days); "
            "nothing is chained across it."
        )
    for s in series.get("suspect_copies", []):
        lines.append(
            f"- {s['t_public']}: suspect copy, {s['note']}; "
            + ("excluded (the next copy recovered)." if s.get("excluded") else "kept and marked.")
        )
    for seg in series["segments"]:
        for hole in seg.get("holes", []):
            lines.append(
                f"- {seg['regime']} regime: no copy between {hole['from']} and {hole['to']} "
                f"({hole['days']} days)."
            )
        for sw in seg.get("swapped_vintages", []):
            lines.append(f"- {sw}: day-month swapped dates, read exchanged back.")
    for s in counts.get("skipped", []):
        lines.append(f"- {s['t_public']}: not parsed ({plain_reason(s)}).")
    for s in counts.get("excluded", []):
        lines.append(f"- {s['t_public']}: excluded, lacks {', '.join(s['missing'])}.")
    if split and series.get("corrections"):
        lines += ["", "## Corrections", ""]
        lines += [f"- {c['date']}: {c['text']}" for c in series["corrections"]]
    lines += [
        "",
        f"Every copy's row, both comparisons and the swap test are in `{rows_source}`; "
        f"the copies themselves are listed with digests in `{evidence}/vintage-manifest.json`.",
        "",
    ]
    return "\n".join(lines)
