"""017 — the findings page, a pure function of the census evidence and of the
certificates 014 issued.

The page prints what the register printed. It names projects, sites, stages
and statuses, because those are the register's own cells and the subject of
the investigation; it characterises no company and attributes no cause.
"""

import re
from datetime import date
from decimal import Decimal
from html import escape
from typing import Any

from grid_mysteries.investigations import overdue_queue as oq
from grid_mysteries.investigations.overdue_queue import share

#: Fields of a register row the page shows in its tables. The evidence keeps
#: every cell as published; the page shows the ones the census is about.
ROW_COLUMNS: tuple[tuple[str, str], ...] = (
    ("project_name", "Project"),
    ("connection_site", "Connection site"),
    ("stage", "Stage"),
    ("plant_type", "Plant type"),
    ("status", "Status"),
)


def mw(value: object) -> str:
    """A capacity as the page prints it: thousands separated, no trailing
    zeros, and an em dash where the register printed nothing."""
    if value is None or value == "":
        return "—"
    number = Decimal(str(value))
    whole = number.to_integral_value()
    return f"{whole:,}" if number == whole else f"{number.normalize():,}"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    return [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
        *["| " + " | ".join(r) + " |" for r in rows],
    ]


def _row_cells(row: dict[str, Any]) -> list[str]:
    return [str(row.get(key) or "—") for key, _label in ROW_COLUMNS]


def _headline(census: dict[str, Any]) -> str:
    return (
        f"In the copy of NESO's TEC Register published on {census['as_of']}, "
        f"**{census['selected_rows']} entries carrying "
        f"{mw(census['selected_mw'])} MW** have an effective date earlier than that "
        f"publication date and a project status other than “Built” "
        f"({census['distinct_project_ids']} distinct project ids, "
        f"{mw(census['selected_mw_largest_per_id'])} MW, on the second reading below)."
    )


def _undated_line(census: dict[str, Any]) -> str:
    """What the four class counts and the copy's status counts say together
    about the rows with no date. No new figure: arithmetic on numbers the
    declaration already required to be published."""
    built = census["status_counts_all_rows"].get("Built", 0)
    undated_built = built - census["dated_built"]
    if undated_built != census["undated"]:
        return (
            f"{census['undated']:,} rows carry no readable date, of which "
            f"{undated_built:,} are \u201cBuilt\u201d."
        )
    return (
        f"Those two numbers meet: the copy carries {built:,} rows at \u201cBuilt\u201d, "
        f"{census['dated_built']:,} of them dated, so {undated_built:,} \u201cBuilt\u201d rows "
        f"are undated \u2014 exactly the {census['undated']:,} undated rows in the copy. "
        "**Every row with no effective date is a row the register calls Built.** The register "
        "appears to clear the date once a project is built, which is why the residue this "
        "census measures \u2014 a date in the past with a status that is not Built \u2014 is "
        "the set of entries the register has neither moved on nor cleared."
    )


def _census_section(census: dict[str, Any]) -> list[str]:
    scale = census["scale"]
    lines = [
        "## The evidence",
        "",
        f"One copy of the register and nothing else: `{census['copy']['path']}`, "
        f"SHA-256 `{census['copy']['sha256']}`, {census['rows_total']:,} rows, fetched from "
        f"the NESO data portal on {census['copy']['t_public']} and journalled with its "
        "resource URL and publication basis.",
        "",
        "Every row of that copy falls in exactly one of four classes, which is check C3:",
        "",
        *_table(
            ["Class", "Rows"],
            [
                [
                    "Dated earlier than the copy's own date, status not “Built” (**the census**)",
                    f"**{census['selected_rows']:,}**",
                ],
                [
                    "Dated on or after the copy's own date, status not “Built”",
                    f"{census['dated_not_built_future']:,}",
                ],
                ["Dated, status “Built”", f"{census['dated_built']:,}"],
                ["No date the register's spellings can read", f"{census['undated']:,}"],
                ["All rows", f"{census['rows_total']:,}"],
            ],
        ),
        "",
        _undated_line(census),
        "",
        f"For scale, the same copy carries {mw(scale['mw_dated_on_or_after_as_of'])} MW dated "
        f"on or after {census['as_of']} across {scale['rows_dated_on_or_after_as_of']:,} rows, "
        f"of which {mw(scale['mw_scoping_dated_on_or_after_as_of'])} MW is at status "
        f"“Scoping”.",
        "",
        "### By status, as the register prints it",
        "",
        *_table(
            ["Status", "Rows", "MW"],
            [
                [g["status"] or "(blank)", f"{g['rows']:,}", mw(g["mw"])]
                for g in census["by_status"]
            ],
        ),
        "",
        "### By plant type, as the register prints it",
        "",
        "The register prints compound plant types; this census keeps them whole and does "
        "not split a combined entry across its technologies.",
        "",
        *_table(
            ["Plant type", "Rows", "MW"],
            [
                [g["plant_type"] or "(blank)", f"{g['rows']:,}", mw(g["mw"])]
                for g in census["by_plant_type"]
            ],
        ),
        "",
        "### By the year the date fell in",
        "",
        *_table(
            ["Year", "Rows", "MW"],
            [[str(g["year"]), f"{g['rows']:,}", mw(g["mw"])] for g in census["by_year"]],
        ),
        "",
        "### The earliest dates on the list",
        "",
        *_table(
            ["Effective from", *[label for _key, label in ROW_COLUMNS], "MW"],
            [[str(r["effective"]), *_row_cells(r), mw(r["mw"])] for r in census["earliest"]],
        ),
        "",
    ]
    return lines


def _limits_section(census: dict[str, Any]) -> list[str]:
    sens = census["swap_sensitivity"]
    repeated = census["repeated_project_ids"]
    lines = [
        "## What this does not say, and what could move it",
        "",
        "**It does not say that any capacity is late.** The register's status is NESO's "
        "own best-known classification, and NESO says so. A row whose date has passed and "
        "whose status is not “Built” may have connected without the status being "
        "refreshed — which is the same staleness this investigation is about. The claim "
        "is about what the document says, and only that.",
        "",
        f"**Zero-capacity rows.** {census['selected_rows_zero_capacity']} of the "
        f"{census['selected_rows']} carry a published capacity of 0 MW. They are counted in "
        "the row count and add nothing to the MW total, so the row count and the MW figure "
        "are not two views of the same thing. "
        + (
            "Every selected row carries a capacity the register's number formats can read; "
            "none had to be excluded."
            if not census["selected_rows_without_capacity"]
            else f"A further {census['selected_rows_without_capacity']} carry no readable "
            "capacity at all; they too are counted as rows and excluded from every total, "
            "because no capacity is not zero."
        ),
        "",
    ]
    if repeated:
        lines += [
            f"**Rows sharing a project id.** {len(repeated)} project "
            f"{'id appears' if len(repeated) == 1 else 'ids appear'} on more than one "
            "selected row. Counting rows gives "
            f"{mw(census['selected_mw'])} MW; counting each id once and keeping the largest "
            f"of its rows gives {mw(census['selected_mw_largest_per_id'])} MW over "
            f"{census['distinct_project_ids']} ids. Both readings were declared before the "
            "run and both are published; the rows are:",
            "",
            *_table(
                ["Project id", "Effective from", *[label for _k, label in ROW_COLUMNS], "MW"],
                [
                    [group["project_id"], str(r["effective"]), *_row_cells(r), mw(r["mw"])]
                    for group in repeated
                    for r in group["rows"]
                ],
            ),
            "",
        ]
    else:
        lines += [
            "**Rows sharing a project id.** None do on this copy, so the row reading and "
            "the id reading are the same number.",
            "",
        ]
    lines += [
        "**Day and month.** Every dated cell in this copy is written `DD/MM/YYYY`, and the "
        "archive's schema report records that no other spelling appears in it. Six copies "
        "elsewhere in the archive do exchange day and month, so the census publishes the "
        f"sensitivity: {sens['rows_with_a_swapped_reading']} of the selected rows "
        f"({mw(sens['mw_with_a_swapped_reading'])} MW) have a date that could be read the "
        f"other way round, and {sens['rows_swapped_reading_not_past']} of them "
        f"({mw(sens['mw_swapped_reading_not_past'])} MW) would then not be past the date at "
        "all. The day-month correction is a test between two consecutive copies and is not "
        "applied to one copy.",
        "",
    ]
    storage_only = next(
        (g["mw"] for g in census["by_plant_type"] if g["plant_type"] == "Energy Storage System"),
        0,
    )
    lines += [
        "**Against the ungoverned figures that prompted this.** The declaration records, "
        "before the freeze, what the author had already seen from an ad-hoc script outside "
        "this repository. The run agrees with it on the headline "
        f"({census['selected_rows']} rows, {mw(census['selected_mw'])} MW), on the yearly "
        "table, on the eight zero-capacity rows, on the earliest entry, and on the scale "
        "line. It differs in two places, and the run is what is published:",
        "",
        "- The scratch figures split the register's compound plant types across their "
        "technologies, which put 5,175 MW under Energy Storage. This census keeps compound "
        f"types whole, as declared, so Energy Storage System alone is "
        f"{mw(storage_only)} MW "
        "and the rest sits under the combined labels in the table above.",
        "- The two project ids that appear twice are the ones the scratch named, but not "
        "what it said they were. They are two genuine multi-stage entries — stage 1 "
        "and stage 2 of the same project, with different capacities and different dates "
        "— not a platform counted twice. Neither is a double count, which is why the "
        "two readings of the unit differ by 50 MW and not by more.",
        "",
    ]
    fired = census.get("falsifiers_fired") or []
    lines += [
        "**Falsifiers declared before the run.** "
        + ("None fired." if not fired else "Fired: " + "; ".join(fired) + ".")
        + " The three were: that day-month swapping could move more than a fifth of the "
        "selected MW into the future; that the copy carried a schema-report flag or a "
        "partial-export suspicion; and that the two readings of the unit differed by more "
        "than a tenth.",
        "",
    ]
    return lines


def _certificate_section(certificates: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## The exhibit: one project, traced across every copy",
        "",
        "A census of one copy cannot tell a reader whether a date that has passed is news "
        "or is eight years old, and it cannot see the entries whose date has not passed "
        "*yet* but has been rewritten repeatedly. For that the copies have to be read in "
        "sequence. The As-of Connection Record Certificate is 014's instrument for exactly "
        "that, and it is applied here to `Eggborough CCGT - OCGT - BESS`, 2,450 MW at "
        "Eggborough 400kV Substation, whose first stage is dated a fortnight after the "
        "copy this census reads.",
        "",
        "It takes more than one certificate, and that is the first finding: **the register has "
        "called this project three different things.** A reader who searches today's copy "
        "for its current name and then looks for that name in older copies finds nothing "
        "before 1 July 2025.",
        "",
        "Each bundle below is hash-addressed: its manifest's SHA-256 is the certificate "
        "id, the manifest lists every evidence file with its digest, and both the manifest "
        "and the certificate are witnessed by OpenTimestamps and by RFC 3161 tokens from "
        "two authorities. `python3 verify.py` inside a bundle recomputes every digest "
        "offline.",
        "",
    ]
    for cert in certificates:
        record = cert["record"]
        stage = f", stage {cert['stage']}" if cert.get("stage") else ""
        lines += [
            f"### `{record['project']}`{stage}, {cert['dates'][0]} to {cert['dates'][1]}",
            "",
            f"Bundle `{cert['bundle']}`, certificate id `{cert['certificate_id']}`. "
            f"{record['vintages_consulted']:,} copies consulted "
            f"({record['first_vintage']} to {record['last_vintage']}); "
            f"{record['vintages_absent']:,} with no matching row, "
            f"{record['vintages_ambiguous']:,} ambiguous, "
            f"{record.get('vintages_suspect', 0)} suspect.",
            "",
        ]
        trace = cert.get("status_trace") or {}
        if trace:
            lines += [
                "Every status the register published for this project's own row in the copies "
                "this bundle consulted \u2014 the row whose published plant type names a gas "
                "turbine plant or the hybrid label, which is what separates it from the coal "
                "station that shared its name until 2020 and from the storage project that "
                "took the name in 2024:",
                "",
                *_table(
                    ["Status as published", "Copies", "Rows", "First copy", "Last copy"],
                    [
                        [
                            name or "(blank)",
                            f"{len(seen['copies']):,}",
                            f"{seen['rows']:,}",
                            str(seen["first_copy"]),
                            str(seen["last_copy"]),
                        ]
                        for name, seen in trace.items()
                    ],
                ),
                "",
            ]
        if record["changes"]:
            lines += _table(
                ["#", "First shown in copy of", "Field", "Previously (last seen)", "Now"],
                [
                    [
                        str(i),
                        str(c["first_shown"]),
                        c["field"],
                        f"{c['previous'] or '—'} ({c['last_previous']})",
                        c["current"] or "—",
                    ]
                    for i, c in enumerate(record["changes"], start=1)
                ],
            )
        else:
            lines.append("No change between the two copies in force.")
        lines.append("")
    lines += _exhibit_reading(certificates)
    return lines


def _exhibit_reading(certificates: list[dict[str, Any]]) -> list[str]:
    """What the three bundles say when read in order. Every statement here is
    a line of a table above or a row of a bundle's `extracts.ndjson`."""
    copies = oq.distinct_copies([cert.get("status_trace") or {} for cert in certificates])
    statuses = sorted({name for cert in certificates for name in (cert.get("status_trace") or {})})
    return [
        "### Reading the bundles in order",
        "",
        "- The coal station's capacity leaves the register in the copy of **23 September "
        "2015**: the stage TEC goes from 0 to −1,940 MW and the cumulative total from "
        "1,940 MW to 0, effective 1 April 2016.",
        "- A **second** row named `Eggborough` appears in the copy of **8 November 2018**. "
        "The bundle's extract for that copy publishes it as 2,450 MW, effective "
        "**1 April 2022**, status **Awaiting Consents**, plant type CCGT — beside the "
        "coal row, by then “Built” at 1,870 MW.",
        "- The published target date then moves: 1 April 2022 until the copy of 2 April "
        "2020; **1 October 2024** in the copy of 9 April 2020; **1 October 2025** in the "
        "copy of 23 April 2021; **1 October 2026** in the copy of 16 September 2022. It "
        "has not moved since — four years on the same date.",
        "- Six of the changes listed above are the register printing one of those dates "
        "with day and month exchanged and then exchanging them back (1 October 2024 and "
        "10 January 2024; 1 October 2025 and 10 January 2025). The certificate records "
        "what was published; the day-month correction is a test between two consecutive "
        "copies, which a certificate does not apply.",
        "- In the copy of **5 January 2024** the name `Eggborough` stops being this "
        "project's. That one copy changes the customer, the capacity, the target date, "
        "the status, the plant type **and the project id** — the register has given "
        "the bare name to a different, smaller project, and this one continues under "
        "`Eggborough CCGT and BESS`.",
        "- In the copy of **24 December 2024** that entry becomes two rows: the split into "
        "stages. By the copy of **1 July 2025** the name is `Eggborough CCGT - OCGT - "
        "BESS`, stage 1 at **1,999 MW effective 1 October 2026** and stage 2 at 451 MW "
        "effective 1 October 2027.",
        f"- The bundles between them see this project in **{len(copies):,} copies** of the "
        f"register, from {copies[0]} to {copies[-1]}, and in every one of them the status "
        "reads "
        + (
            f"“{statuses[0]}” — it has never read anything else."
            if len(statuses) == 1
            else "one of: " + ", ".join(f"“{n}”" for n in statuses) + "."
        ),
        "",
        "### The two readings, and which one this investigation takes",
        "",
        "The Planning Inspectorate decided the development consent order for the Eggborough "
        "gas plant on **20 September 2018**, under the Planning Act 2008, for up to about "
        "2,500 MW. The register's first copy showing this entry as “Awaiting "
        "Consents” is seven weeks later, and every copy since says the same.",
        "",
        "So either **the status field means a consent other than that order** — there "
        "are others a project of this kind needs — or **the field has not been "
        "refreshed in eight years**. This investigation does not choose. It publishes the "
        "record and says that the register does not, on its face, distinguish the two. The "
        "question has been put to NESO under the Environmental Information Regulations "
        "(FOI/26/216, answer due 13 October 2026) and the answer will be published here "
        "when it arrives, whichever way it goes.",
        "",
        "*The consent order decision date above is stated from the public planning record "
        "and is **not pinned in this repository**; everything else in this section is a "
        "line of a witnessed certificate bundle. Pinning it is outstanding.*",
        "",
        "That is the general point the exhibit is for. A status in this register is not "
        "dated, and a reader of one copy cannot tell a value written last week from one "
        "written in 2018. The census above counts 98 entries whose date has passed; it "
        "cannot tell you, from that copy alone, which of them the register has simply "
        "stopped looking at. Only the sequence of copies can, and the sequence is not "
        "published — it has to be rebuilt.",
        "",
    ]


# ------------------------------------------------------------ version 3
# `DECLARATION-v3.md` (dd396986…) and its amendment 1 (35b74e13…): the same
# method over two later copies, and one declared comparison. Every figure is
# read from `evidence/v3/`; nothing is recomputed here.


def signed(value: object) -> str:
    """A difference as the page prints it: a sign, and no trailing zeros."""
    number = Decimal(str(value))
    if number == 0:
        return "0"
    return ("+" if number > 0 else "−") + mw(abs(number))


def _side_by_side(
    tables: list[list[dict[str, Any]]], label: str
) -> list[tuple[Any, list[dict[str, Any] | None]]]:
    """Grouped tables for several copies, one line per label: the labels of
    the last copy in its order, then any the last copy lacks."""
    order: list[Any] = [g[label] for g in tables[-1]]
    for table in tables[:-1]:
        order += [g[label] for g in table if g[label] not in order]
    by = [{g[label]: g for g in table} for table in tables]
    return [(key, [b.get(key) for b in by]) for key in order]


def _pair_cells(entries: list[dict[str, Any] | None]) -> list[str]:
    return [
        cell for e in entries for cell in ((f"{e['rows']:,}", mw(e["mw"])) if e else ("0", "0"))
    ]


def _same(values: list[Any]) -> bool:
    return all(v == values[0] for v in values)


def _v3_readings_table(rows: list[dict[str, Any]], copies: list[str]) -> list[str]:
    return _table(
        ["Project", "MW"] + [day(c) for c in copies],
        [
            [r["project_name"], mw(r["mw"])]
            + [
                (
                    f"{x['gate'] or 'blank'} / {x['effective_as_published']}"
                    if x["found"]
                    else "no matching row"
                )
                for x in r["readings"]
            ]
            for r in rows
        ],
    )


def v3_section(v3: dict[str, Any]) -> list[str]:
    ref, nxt = v3["copies"]
    rc, nc = ref["census"], nxt["census"]
    rg, ng = ref["gate"], nxt["gate"]
    comp, n0, method = v3["comparison"], v3["n0"], v3["method_check"]
    d1, d2 = comp["d1"], comp["d2"]
    dates = [day(rc["as_of"]), day(nc["as_of"])]
    short = [
        f"{date.fromisoformat(c['as_of']).day} {date.fromisoformat(c['as_of']):%b}"
        for c in (rc, nc)
    ]
    tiers = [
        next(g for g in gate["g2_overdue_by_gate"] if g["gate"] == oq.CONFIRMED_TIER)
        for gate in (rg, ng)
    ]
    g6 = [rg["g6_summary"], ng["g6_summary"]]
    lines = [
        f"## Two later copies: {dates[0]} and {dates[1]}",
        "",
        "*This section is version 3 of the declaration (`DECLARATION-v3.md`, SHA-256 "
        f"`{v3['declaration_sha256']}`) and its amendment 1 "
        f"(`{v3['amendment']['file']}`, SHA-256 `{v3['amendment']['sha256']}`), each frozen "
        "and witnessed before any figure it governs was computed. Versions 1 and 2 above are "
        "unchanged by it.*",
        "",
    ]
    # The answer first.
    counts = [
        f"**{c['selected_rows']} entries carrying {mw(c['selected_mw'])} MW** on {d}"
        f" ({c['distinct_project_ids']} distinct project ids, "
        f"{mw(c['selected_mw_largest_per_id'])} MW)"
        for c, d in zip((rc, nc), dates, strict=True)
    ]
    lines += [
        "The same count, run on the copy NESO published on "
        f"{dates[0]} and on the first copy it published on or after 29 September, finds "
        f"{counts[0]} and {counts[1]} with an effective date earlier than that copy's own "
        "date and a status other than “Built”.",
        "",
    ]
    if _same([(t["rows"], Decimal(str(t["mw"])), t["rows_in_copy"]) for t in tiers]) and _same(
        [
            (
                g["rows_if_those_rows_are_read_as_not_past"],
                Decimal(str(g["mw_if_those_rows_are_read_as_not_past"])),
            )
            for g in g6
        ]
    ):
        t, o = tiers[1], g6[1]
        lines += [
            f"**In the confirmed tier, {t['rows']} of its {t['rows_in_copy']} entries are past "
            f"their confirmed date in both copies**, carrying {mw(t['mw'])} MW: "
            f"{pct(t['row_share_of_its_gate'])} of the tier's entries and "
            f"{pct(t['capacity_share_of_its_gate'])} of its capacity. Another copy of the "
            f"register prints {o['rows_a_gated_copy_publishes_as_not_past']} of those dates as "
            f"not yet past; on that reading it is {o['rows_if_those_rows_are_read_as_not_past']} "
            f"entries and {mw(o['mw_if_those_rows_are_read_as_not_past'])} MW, in both copies. "
            "Neither figure is quoted without the other.",
            "",
        ]
    else:
        for t, o, d in zip(tiers, g6, dates, strict=True):
            lines += [
                f"On {d}, **{t['rows']} of the confirmed tier's {t['rows_in_copy']} entries are "
                f"past their confirmed date**, carrying {mw(t['mw'])} MW "
                f"({pct(t['row_share_of_its_gate'])} of its entries, "
                f"{pct(t['capacity_share_of_its_gate'])} of its capacity); on the other reading, "
                f"{o['rows_if_those_rows_are_read_as_not_past']} entries and "
                f"{mw(o['mw_if_those_rows_are_read_as_not_past'])} MW.",
                "",
            ]
    classes = d2["classes"]
    left = {k: v for k, v in classes.items() if k.startswith("reference only")}
    joined = {k: v for k, v in classes.items() if k.startswith("next only")}
    only_arrivals = set(joined) <= {"next only: (b) the date arrived"}
    both = classes.get("in both", {"rows": 0})
    summary = (
        f"Between the two copies, {d1['days_between']} days apart, every one of the "
        f"{rc['selected_rows']} entries on the first list is still on the second"
        if not left
        else f"Between the two copies, {d1['days_between']} days apart, {both['rows']} entries "
        f"are on both lists and {sum(v['rows'] for v in left.values())} left"
    )
    arrivals = classes.get("next only: (b) the date arrived")
    if joined:
        summary += f", and {sum(v['rows'] for v in joined.values())} joined" + (
            ", because the date it already carried arrived; none left."
            if only_arrivals and not left and arrivals and arrivals["rows"] == 1
            else (", each because the date it already carried arrived." if only_arrivals else ".")
        )
    else:
        summary += "."
    lines += [summary, ""]

    # C10.
    v1, v2 = method["version_1"], method["version_2"]
    lines += [
        "### The method was checked first",
        "",
        "Before either count, the code for this version was run on the captured copy of "
        f"{day(method['copy']['t_public'])}, which has the same SHA-256 as the copy versions 1 "
        f"and 2 read. It reproduced version 1's {v1['rows_line_for_line']['committed']} selected "
        f"rows line for line and all {len(v1['totals_and_breakdowns'])} of its totals and "
        f"breakdowns, and version 2's {v2['gate_rows_line_for_line']['committed']} confirmed-tier "
        "rows with G1 to G6, to the penny (check C10, `evidence/v3/method-check.json`). "
        + (
            "It passed." if method["pass"] else "**It failed, so nothing below is published (F7).**"
        ),
        "",
    ]

    # The copies, R1′, R2′, N0 and amendment 1.
    spell = n0["schema_report_entry"]["date_spellings"]
    gaps = n0["selection"]["days_with_no_tec_record"]
    lines += [
        "### The copies",
        "",
        *_table(
            [
                "Copy",
                "Published (CKAN last_modified)",
                "NESO's filename",
                "Captured",
                "Rows",
                "SHA-256",
            ],
            [
                [
                    d,
                    c["copy"]["t_public_basis"]
                    .split(";")[0]
                    .removeprefix("CKAN resource last_modified "),
                    f"`{c['copy']['filename']}`",
                    c["copy"]["fetched_at"][:16].replace("T", " ") + " UTC",
                    f"{c['rows_total']:,}",
                    f"`{c['copy']['sha256'][:16]}…`",
                ]
                for c, d in zip((rc, nc), dates, strict=True)
            ],
        ),
        "",
        "Each copy's date is the day of its CKAN `last_modified`, as for every copy this "
        "archive has pinned. The first is named by its digest in the declaration; the second is "
        "the first copy the daily capture holds dated on or after 29 September. The capture runs "
        "once a day, so a copy NESO published and replaced within a day would never be seen; "
        + (
            "the capture's manifests hold a record of the register for every day from 29 "
            f"September to the day it fetched this one ({day(n0['selection']['captured_on'])}), "
            "so no day was missed."
            if not gaps
            else "the manifests hold no record of the register on "
            + ", ".join(day(g) for g in gaps)
            + "."
        ),
        "",
    ]
    fs = [c["filename_sensitivity"] for c in (rc, nc)]
    lines += [
        "NESO's filename names the day before each copy's date ("
        + " and ".join(day(f["filename_date"]) for f in fs if f["filename_date"])
        + "). Read against the filename's date instead, "
        + (
            "no entry moves on either copy."
            if all(f["rows"] == 0 for f in fs)
            else "; ".join(
                f"{f['rows']} entries ({mw(f['mw'])} MW) move on the copy of {day(f['as_of'])}"
                for f in fs
            )
            + "."
        ),
        "",
        "**The second copy spells its dates differently.** Every one of its "
        f"{spell['iso-dash']:,} dated cells is written `YYYY-MM-DD`, where the copy of "
        f"{dates[0]} and every earlier captured copy write `DD/MM/YYYY`. The declaration's "
        "schema check (N0) required the old spelling, so it stopped the run before anything "
        "about that copy was computed (`evidence/v3/n0.json`). Amendment 1 was then written from "
        "the schema report alone, approved and witnessed: the new spelling is read year, month, "
        "day, which is how the register's earlier ISO copies (22 and 25 August 2026, read by "
        "version 2) were read; and the day-month swap test the series uses for exactly this "
        "case was run first between the two copies. "
        f"It found {v3['swap_test']['disagreements']} dates that differ between them among "
        f"entries it could match, {v3['swap_test']['swap_explained']} of them explained by "
        "exchanging day and month, so it did not flag the copy (F11 did not fire). A change of "
        "spelling alone never moves an entry in the comparison below, which compares dates, not "
        "the way they are written. The copy also prints capacities with two decimals "
        "(`540.00`); they are the same numbers.",
        "",
    ]

    # D1.
    rows_d1 = [
        ("Entries past their date, not “Built”", "selected_rows", False),
        ("Their capacity, MW", "selected_mw", True),
        ("Distinct project ids among them", "distinct_project_ids", False),
        ("Capacity counting each id once, MW", "selected_mw_largest_per_id", True),
        ("Confirmed-tier entries past their date", "gate2_overdue_rows", False),
        ("Their capacity, MW", "gate2_overdue_mw", True),
        ("Entries dated on or after the copy's date", "rows_dated_on_or_after_as_of", False),
        ("Their capacity, MW", "mw_dated_on_or_after_as_of", True),
        ("Of those, capacity at “Scoping”, MW", "mw_scoping_dated_on_or_after_as_of", True),
    ]
    diff = d1["difference_next_minus_reference"]
    lines += [
        "### Side by side",
        "",
        "The calendar alone moves entries into the count as their dates arrive, so every "
        f"difference is read with both dates: {dates[0]} and {dates[1]}, "
        f"{d1['days_between']} days apart.",
        "",
        *_table(
            ["", short[0], short[1], "Difference"],
            [
                [
                    label,
                    mw(d1["reference"][key]) if is_mw else f"{d1['reference'][key]:,}",
                    mw(d1["next"][key]) if is_mw else f"{d1['next'][key]:,}",
                    signed(diff[key]),
                ]
                for label, key, is_mw in rows_d1
            ],
        ),
        "",
    ]

    # D2.
    def row_of(t: dict[str, Any]) -> dict[str, Any]:
        return t["next"] or t["reference"]

    lines += [
        "### Entry by entry",
        "",
        "Every entry on either list, matched by its project id and stage:",
        "",
        *_table(
            ["Class", "Entries", f"MW, {short[0]}", f"MW, {short[1]}"],
            [
                [k[0].upper() + k[1:], f"{v['rows']:,}", mw(v["mw_reference"]), mw(v["mw_next"])]
                for k, v in classes.items()
            ],
        ),
        "",
    ]
    listed = [t for k, v in classes.items() if k != "in both" for t in v["members"]]
    if listed:
        lines += [
            *_table(
                [
                    "Class",
                    "Project",
                    "Connection site",
                    "Stage",
                    "Status",
                    "MW",
                    "Date",
                    f"Date on {short[0]}",
                ],
                [
                    [
                        t["klass"][0].upper() + t["klass"][1:],
                        row_of(t)["project_name"],
                        row_of(t)["connection_site"],
                        row_of(t)["stage"] or "—",
                        row_of(t)["status"],
                        mw(row_of(t)["mw"]),
                        str(row_of(t)["effective"]),
                        t["other_effective"] or "—",
                    ]
                    for t in listed
                ],
            ),
            "",
        ]
    amb = d2["ambiguous"]["keys"]
    lines += [
        (
            "No project id and stage is on more than one row of either copy, so every entry is "
            "classed."
            if not amb
            else f"{len(amb)} project id and stage pairs are on more than one row "
            "and are in no class: " + ", ".join(f"`{k}`" for k in amb) + "."
        )
        + " The classes add up to each copy's own totals (check C11). An entry whose date "
        "arrived is not late for having arrived, and an entry that leaves has not been "
        "delivered for leaving; the register prints what changed, not why.",
        "",
    ]

    # Version 1's breakdowns, side by side.
    lines += ["### The breakdowns, side by side", ""]
    for title, key, label, fmt in (
        ("By status, as the register prints it", "by_status", "status", str),
        ("By plant type, as the register prints it", "by_plant_type", "plant_type", str),
        ("By the year the date fell in", "by_year", "year", str),
    ):
        lines += [
            f"#### {title}",
            "",
            *_table(
                [
                    title.split(",")[0].removeprefix("By ").capitalize(),
                    f"Entries, {short[0]}",
                    f"MW, {short[0]}",
                    f"Entries, {short[1]}",
                    f"MW, {short[1]}",
                ],
                [
                    [fmt(k) or "(blank)", *_pair_cells(entries)]
                    for k, entries in _side_by_side([rc[key], nc[key]], label)
                ],
            ),
            "",
        ]
    earliest = [
        [(r["project_name"], r["effective"], mw(r["mw"])) for r in c["earliest"]] for c in (rc, nc)
    ]
    lines += ["#### The earliest dates on the list", ""]
    shown: list[tuple[str | None, dict[str, Any]]]
    if earliest[0] == earliest[1]:
        lines += ["The same ten entries head both lists:", ""]
        shown = [(None, nc)]
    else:
        shown = [(when, copy_) for when, copy_ in zip(dates, (rc, nc), strict=True)]
    for when, copy_ in shown:
        if when:
            lines += [f"On {when}:", ""]
        lines += [
            *_table(
                ["Effective from", *[label for _key, label in ROW_COLUMNS], "MW"],
                [[str(r["effective"]), *_row_cells(r), mw(r["mw"])] for r in copy_["earliest"]],
            ),
            "",
        ]
    lines += [
        " ".join(
            f"On {d}, {c['selected_rows_zero_capacity']} of the {c['selected_rows']} carry 0 MW, "
            f"{len(c['repeated_project_ids'])} project ids appear on more than one entry, and "
            f"{c['swap_sensitivity']['rows_with_a_swapped_reading']} dates could be read with day "
            f"and month exchanged, {c['swap_sensitivity']['rows_swapped_reading_not_past']} of "
            f"them ({mw(c['swap_sensitivity']['mw_swapped_reading_not_past'])} MW) would then not "
            "be past."
            for c, d in zip((rc, nc), dates, strict=True)
        )
        + " In a copy that spells dates `YYYY-MM-DD` the other reading would be `YYYY-DD-MM`, "
        "which is not a spelling the register has used; the figure is given in the same form "
        "for both copies, as declared.",
        "",
    ]

    # Version 2's cross-tab, side by side.
    lines += [
        "### The confirmed tier in each copy",
        "",
        *_table(
            [
                "Gate cell",
                f"Entries, {short[0]}",
                f"MW, {short[0]}",
                f"Entries, {short[1]}",
                f"MW, {short[1]}",
            ],
            [
                [gate_label(entries[-1] or entries[0] or {"gate": k}), *_pair_cells(entries)]
                for k, entries in _side_by_side(
                    [rg["g1_copy_by_gate"], ng["g1_copy_by_gate"]], "gate"
                )
            ],
        ),
        "",
        "The entries past their date, by Gate cell, with each Gate's two shares of its own "
        "total (row share first, capacity share beside it):",
        "",
        *_table(
            ["Gate cell"]
            + [
                f"{h}, {s}" for s in short for h in ("Entries", "MW", "Row share", "Capacity share")
            ],
            [
                [gate_label(entries[-1] or entries[0] or {"gate": k})]
                + [
                    cell
                    for e in entries
                    for cell in (
                        (
                            f"{e['rows']:,}",
                            mw(e["mw"]),
                            pct(e["row_share_of_its_gate"]),
                            pct(e["capacity_share_of_its_gate"]),
                        )
                        if e
                        else ("0", "0", "—", "—")
                    )
                ]
                for k, entries in _side_by_side(
                    [rg["g2_overdue_by_gate"], ng["g2_overdue_by_gate"]], "gate"
                )
            ],
        ),
        "",
        *_table(
            [
                "Gate cell",
                "Status as printed",
                f"Entries, {short[0]}",
                f"MW, {short[0]}",
                f"Entries, {short[1]}",
                f"MW, {short[1]}",
            ],
            [
                [
                    gate_label({"gate": k[0], "tier": oq.tier_of(k[0])}),
                    k[1] or "(blank)",
                    *_pair_cells(entries),
                ]
                for k, entries in _side_by_side(
                    [
                        [
                            {**c, "key": (c["gate"], c["status"])}
                            for c in g["g3_overdue_by_gate_and_status"]
                        ]
                        for g in (rg, ng)
                    ],
                    "key",
                )
            ],
        ),
        "",
    ]
    names = [
        sorted(
            (r["project_name"], r["effective"], Decimal(str(r["mw"])))
            for r in g["g4_confirmed_tier_overdue"]
        )
        for g in (rg, ng)
    ]
    lines += [
        (
            "The same entries are in the confirmed tier and past their date in both copies:"
            if names[0] == names[1]
            else f"The confirmed-tier entries past their date on {dates[1]}:"
        ),
        "",
        *_gate_rows_table(ng["g4_confirmed_tier_overdue"]),
        "",
    ]
    reps = [g["g5_repetition"] for g in (rg, ng)]
    lines += [
        (
            "No two of them share a project id or a project name in either copy."
            if not any(r["sharing_a_project_id"] or r["sharing_a_project_name"] for r in reps)
            else "Some share a project id or name; both readings are in `gate.json` for each copy."
        ),
        "",
    ]

    # G6′.
    gated = ng["g6_gated_copies"]
    confirmed = ng["g4_confirmed_tier_overdue"]
    settled = [(r, oq.settles_entry_into_the_tier(r)) for r in confirmed]
    open_ = [(r, s) for r, s in settled if not s["settled"]]
    late = [
        r for r in confirmed if (r["first_copy_in_the_tier"] or "") > method["copy"]["t_public"]
    ]
    lines += [
        f"### What the {len(gated)} copies with a Gate column show",
        "",
        "Gate cell and date as each copy prints it, for every entry above, in each copy's own "
        "spelling of the date.",
        "",
        *_v3_readings_table(confirmed, gated),
        "",
        f"All {g6[1]['rows']} were already past their date in the first of these copies whose "
        "Gate cell reads `2`. "
        f"For {len(settled) - len(open_)} of them the date had already passed in the last copy "
        "held before that one, so in the copies held they entered the tier already behind "
        "their date. "
        + (
            f"For the other {len(open_)} ("
            + ", ".join(r["project_name"] for r, _s in open_)
            + f"; {mw(sum((Decimal(str(r['mw'])) for r, _s in open_), Decimal(0)))} MW) the date "
            "fell between the last copy held before and the first that reads `2`, a stretch of "
            + " and ".join(
                sorted({f"{s['days_between']} days" for _r, s in open_ if s["days_between"]})
            )
            + " with no copy held, so these copies do not settle when they entered the tier. "
            if open_
            else ""
        )
        + "A blank Gate cell in an earlier copy is not interpreted."
        + (
            " "
            + "; ".join(
                f"{r['project_name']} first reads `2` in the copy of "
                f"{day(r['first_copy_in_the_tier'])}, after version 2's count"
                for r in late
            )
            + "."
            if late
            else ""
        ),
        "",
    ]
    contested = [r for r in confirmed if r["dates_across_gated_copies_not_past"]]
    if contested:
        lines += [
            "The two readings of the tier's figure come from these entries, which some copy "
            "prints with a date that is not past:",
            "",
            *_table(
                [
                    "Project",
                    "MW",
                    f"Date on {short[1]}",
                    "Another copy",
                    "Which kind of difference",
                ],
                [
                    [
                        r["project_name"],
                        mw(r["mw"]),
                        str(r["effective"]),
                        ", ".join(str(d) for d in r["dates_across_gated_copies_not_past"]),
                        (
                            "the same digits with day and month exchanged"
                            if r["a_not_past_date_is_the_day_month_swap"]
                            else "the register moved the date"
                        ),
                    ]
                    for r in contested
                ],
            ),
            "",
        ]

    # Falsifiers, and what this version never claims.
    fired = sorted({f for c in (rc, nc) for f in c["falsifiers_fired"]})
    if d2_fired := [k for k, hit in comp["falsifiers"].items() if hit]:
        fired += d2_fired
    lines += [
        "### What this version never claims",
        "",
        "- That any difference between the two copies was caused by the announcement of 29 "
        "September, by any policy, by NESO's connections reform or by the queue fee. The copies "
        "are days apart, and the register records dates and statuses, not reasons.",
        "- That an entry whose date arrived is late, or that an entry leaving the list was "
        "delivered.",
        "- That either count measures the queue's health. Each measures what one copy of the "
        "register printed on its own date.",
        "",
        "**Falsifiers declared before the run.** "
        + ("None fired" if not fired else "Fired: " + "; ".join(fired))
        + ", on either copy or in the comparison (F1 to F11, including the filename reading, "
        "unmatched entries and the swap test).",
        "",
        "### Expert corner for version 3",
        "",
        f"- Declaration `investigations/017-the-overdue-queue/DECLARATION-v3.md`, SHA-256 "
        f"`{v3['declaration_sha256']}`; amendment "
        f"`investigations/017-the-overdue-queue/{v3['amendment']['file']}`, SHA-256 "
        f"`{v3['amendment']['sha256']}`; both witnessed by OpenTimestamps and RFC 3161 tokens "
        "from freetsa.org and DigiCert and committed with their proofs.",
        "- Copies read from the local mirror of the daily capture after each digest was checked "
        "against the committed manifest that recorded it: "
        + "; ".join(
            f"{d}, `{c['copy']['key']}` (manifest `{c['copy']['manifest']}`, SHA-256 "
            f"`{c['copy']['manifest_sha256']}`)"
            for c, d in zip((rc, nc), dates, strict=True)
        )
        + ".",
        "- Capture schema report (`archives/tec-register-capture/`) the censuses were checked "
        f"against: `{rc['capture_schema_report_sha256']}` for {dates[0]}, "
        f"`{nc['capture_schema_report_sha256']}` for {dates[1]} (regenerated with that copy in "
        "it, N0).",
        "- Evidence: `evidence/v3/method-check.json` (C10), "
        + ", ".join(f"`evidence/v3/{c['as_of']}/`" for c in (rc, nc))
        + " (`census.json`, `rows.ndjson`, `gate.json`, `gate-rows.ndjson`, append-only), "
        "`evidence/v3/n0.json`, `evidence/v3/a2-swap-test.json`, `evidence/v3/comparison.json`.",
        "- Checks that had to pass on each copy: "
        + "; ".join(sorted(nc["checks"]))
        + "; and in the comparison: "
        + "; ".join(sorted(comp["checks"]))
        + ".",
        "",
        "```",
        "uv run --group registers python investigations/017-the-overdue-queue/run.py \\",
        f"    --version 3 --seal {v3['declaration_sha256'][:12]} \\",
        f"    --amendment-seal {v3['amendment']['sha256'][:12]} --phase check --copy next",
        "```",
        "",
        "recomputes the second copy's census and fails if a committed row would change; "
        "`--copy reference` does the first, and `--phase method-check` reruns C10.",
        "",
    ]
    return lines


def render_findings(
    census: dict[str, Any],
    rows: list[dict[str, Any]],
    certificates: list[dict[str, Any]],
    gate: dict[str, Any] | None = None,
    corrections: list[dict[str, Any]] | None = None,
    v3: dict[str, Any] | None = None,
) -> str:
    """The findings page. `rows` is the append-only evidence of selected rows;
    it is not re-derived here, only counted, so the page can never disagree
    with the file it cites. `corrections` are inserted where they govern
    (`apply_corrections`), so a re-render keeps every one."""
    lines = [
        "# 017 — The queue that is past its own date",
        "",
        f"*Census over the copy of {census['as_of']}. Declaration `DECLARATION.md`, "
        f"SHA-256 `{census['declaration_sha256']}`, frozen and witnessed before any figure "
        f"here was computed. Run {census['run_date']}.*",
        "",
        "## The mystery",
        "",
        _headline(census),
        "",
        "That sentence is deliberately narrow. It is not the claim that "
        f"{mw(census['selected_mw'])} MW of generation and storage is late — the "
        "register cannot support that, and this investigation does not make it. It is the "
        "claim that this many entries *say the date has passed and do not say Built*. What "
        "such an entry means is the second question, and the register does not answer it.",
        "",
        *_census_section(census),
        *(_gate_section(gate, census) if gate else []),
        *(v3_section(v3) if v3 else []),
        *_certificate_section(certificates),
        *_limits_section(census),
        "## Expert corner",
        "",
        f"- Declaration: `investigations/017-the-overdue-queue/DECLARATION.md`, SHA-256 "
        f"`{census['declaration_sha256']}`, witnessed by OpenTimestamps and by RFC 3161 "
        "tokens from freetsa.org and DigiCert at the moment of the freeze, and committed "
        "with its proofs by `scripts/freeze`.",
        *(
            [
                "- Version 2 of the declaration, the Gate cross-tab: "
                "`investigations/017-the-overdue-queue/DECLARATION-v2.md`, SHA-256 "
                f"`{gate['declaration_sha256']}`, witnessed the same way and frozen after "
                "version 1 had run. Its evidence is `evidence/gate.json` and "
                "`evidence/gate-rows.ndjson`; NESO's definition of the tiers is pinned at "
                f"`{gate['gate_definition']['path']}`, SHA-256 "
                f"`{gate['gate_definition']['sha256']}`.",
                "- Checks version 2 had to pass: " + "; ".join(sorted(gate["checks"])) + ".",
            ]
            if gate
            else []
        ),
        "- Archive schema report version 1's reading rules were written against: SHA-256 "
        f"`{census['schema_report_sha256']}` (`archives/tec-register/`)."
        + (
            f" Version 2 was written against `{gate['schema_report_sha256']}`, which adds "
            "the Gate vocabulary to the same pass and changes no status count, so version "
            "1's check C1 passes against both."
            if gate
            else ""
        ),
        f"- The one copy: `{census['copy']['path']}`, SHA-256 `{census['copy']['sha256']}`, "
        f"{census['copy'].get('bytes', 0):,} bytes, source `{census['copy'].get('source')}`, "
        f"publication basis: {census['copy'].get('t_public_basis')}",
        "- Measure: `MW Increase / Decrease` as published, read as `Decimal`. The "
        "cumulative column is never added to it and never substituted for it.",
        f"- Boundary: an effective date **strictly earlier** than {census['as_of']}, the "
        "copy's own publication date — not the date the census was run.",
        f"- Selected rows, one line each as published: `evidence/rows.ndjson` "
        f"({len(rows)} lines, append-only). Summary: `evidence/census.json`.",
        "- Checks that had to pass: " + "; ".join(sorted(census["checks"])) + ".",
        "",
        "## Reproducibility",
        "",
        "```",
        "uv run --group registers python investigations/017-the-overdue-queue/run.py \\",
        f"    --seal {census['declaration_sha256'][:12]} --phase check",
        "```",
        "",
        "recomputes the census from the same copy and fails if a committed row would "
        "change. `scripts/check-rules` maps every rule in the declaration to the test that "
        "holds it; `scripts/verify-proofs` checks the declaration's timestamps against the "
        "roots committed under `trust/tsa/`.",
        "",
    ]
    return apply_corrections("\n".join(lines), corrections)


def apply_corrections(markdown: str, corrections: list[dict[str, Any]] | None) -> str:
    """Insert each correction as its own paragraph directly after the line it
    governs, which is the one line starting with its `after` text. The text it
    corrects is kept as written. An anchor that matches no line, or more than
    one, stops the render: a correction is never dropped or misplaced."""
    lines = markdown.split("\n")
    for correction in corrections or []:
        hits = [i for i, line in enumerate(lines) if line.startswith(correction["after"])]
        if len(hits) != 1:
            raise ValueError(
                f"correction of {correction['date']}: anchor {correction['after']!r} "
                f"matches {len(hits)} lines, not one"
            )
        lines[hits[0] + 1 : hits[0] + 1] = ["", correction["markdown"]]
    return "\n".join(lines)


# ------------------------------------------------------- the outbound document
# Numbers that leave the repository are governed before they go. `post_facts`
# is the machine-readable form, one entry per slot, each carrying the exact
# sentence it licenses and the artefacts that hold it up; `render_post` is the
# draft that quotes them.


def _cert(certificates: list[dict[str, Any]], bundle_prefix: str) -> dict[str, Any]:
    return next(c for c in certificates if c["bundle"].startswith(bundle_prefix))


def _gate_slots(census: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """The two slots version 2 adds, each with the sentence it licenses and
    the caveat that must travel with it."""
    tier = next(g for g in gate["g1_copy_by_gate"] if g["gate"] == "2")
    overdue = next(g for g in gate["g2_overdue_by_gate"] if g["gate"] == "2")
    g6 = gate["g6_summary"]
    common = {
        "as_of": census["as_of"],
        "source": "NESO TEC Register",
        "source_sha256": census["copy"]["sha256"],
        "declaration_sha256": gate["declaration_sha256"],
        "gate_definition_sha256": gate["gate_definition"]["sha256"],
        "reading": (
            "the register prints 1 and 2 in the Gate column, not the words; reading 2 as "
            "Gate 2 is an interpretation against NESO's pinned definition, and a blank "
            "Gate is never interpreted"
        ),
    }
    return {
        "gb-tec-gate2-capacity-2026-09": {
            **common,
            "value": tier["mw"],
            "unit": "MW",
            "rows": tier["rows"],
            "claim": (
                f"In the copy of NESO's TEC Register published on {census['as_of']}, "
                f"{tier['rows']} entries carrying {mw(tier['mw'])} MW read `2` in the Gate "
                "column \u2014 the tier NESO defines as holding a confirmed connection "
                "date, point and queue position."
            ),
        },
        "gb-tec-gate2-overdue-2026-09": {
            **common,
            "value": overdue["mw"],
            "unit": "MW",
            "rows": overdue["rows"],
            "row_share_of_the_tier": overdue["row_share_of_its_gate"],
            "capacity_share_of_the_tier": overdue["capacity_share_of_its_gate"],
            "claim": (
                f"{overdue['rows']} of those {tier['rows']} entries, "
                f"{mw(overdue['mw'])} MW, carry a confirmed date earlier than that "
                f"publication date: {pct(overdue['row_share_of_its_gate'])} of the tier's "
                f"rows and {pct(overdue['capacity_share_of_its_gate'])} of its capacity, "
                "which are two separate shares that happen to be close."
            ),
            "must_travel_with_the_claim": [
                (
                    f"In all {g6['rows']} cases the date had already passed in the first "
                    "held copy whose Gate cell reads 2; none was given a confirmed date in "
                    "these copies and then missed it."
                ),
                (
                    f"{g6['rows_a_gated_copy_publishes_as_not_past']} of the rows, "
                    f"{mw(g6['mw_a_gated_copy_publishes_as_not_past'])} MW, are published "
                    "with a date that is not past in another held copy. On that reading the "
                    f"figure is {mw(g6['mw_if_those_rows_are_read_as_not_past'])} MW over "
                    f"{g6['rows_if_those_rows_are_read_as_not_past']} rows."
                ),
                "Nothing here is a statement about delivery, readiness or NESO's assessment.",
            ],
        },
        **_scoping_slot(census, gate),
    }


def _scoping_slot(census: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """The rows that sit in the confirmed tier at status "Scoping" (G3), and
    the rows themselves (G4).

    Both are inside version 2's declared breakdowns, so this promotes a figure
    that already exists under the seal rather than computing a new one. Every
    qualifier below is per-row evidence from G4 and G6, not an inference from
    the wider claim.
    """
    overdue = next(g for g in gate["g2_overdue_by_gate"] if g["gate"] == "2")
    rows = [r for r in gate["g4_confirmed_tier_overdue"] if r["status"] == SCOPING_STATUS]
    if not rows:
        return {}
    total = sum((Decimal(str(r["mw"])) for r in rows if r["mw"] is not None), Decimal(0))
    contested = [r for r in rows if r["dates_across_gated_copies_not_past"]]
    contested_mw = sum(
        (Decimal(str(r["mw"])) for r in contested if r["mw"] is not None), Decimal(0)
    )
    all_already_past = all(r["already_past_when_first_in_the_tier"] for r in rows)
    scoping_all = census["status_counts_all_rows"].get(SCOPING_STATUS, 0)
    travels = []
    if all_already_past:
        travels.append(
            f"For each of these {len(rows)} rows individually, not only for the wider "
            f"{overdue['rows']}, the date had already passed in the first held copy whose "
            "Gate cell reads 2. None was given a confirmed date in these copies and then "
            "missed it."
        )
    else:
        travels.append(
            "The 'already past on entering the tier' finding holds for the wider set but "
            f"not for every one of these {len(rows)} rows; "
            f"{sum(1 for r in rows if r['already_past_when_first_in_the_tier'])} of them "
            "carry it."
        )
    if contested:
        travels.append(
            f"{len(contested)} of the {len(rows)} rows, {mw(contested_mw)} MW \u2014 "
            f"{pct(share(contested_mw, total))} of this figure, a much larger share than of "
            "the tier total \u2014 are rows another held copy publishes with a date that "
            f"is not past. On that reading this figure is {mw(total - contested_mw)} MW over "
            f"{len(rows) - len(contested)} rows. The two must be quoted together."
        )
    travels += [
        (
            f"\u201c{SCOPING_STATUS}\u201d is the register's own status word, which this "
            f"copy also prints on {scoping_all:,} of its {census['rows_total']:,} rows, "
            f"{census['scale']['rows_scoping_dated_on_or_after_as_of']:,} of them dated in "
            "the future. No conclusion is drawn here from the pairing of that status with "
            "the confirmed tier; the two columns are reported side by side."
        ),
        "Nothing here is a statement about delivery, readiness or NESO's assessment.",
    ]
    return {
        "gb-tec-gate2-overdue-scoping-2026-09": {
            "as_of": census["as_of"],
            "source": "NESO TEC Register",
            "source_sha256": census["copy"]["sha256"],
            "declaration_sha256": gate["declaration_sha256"],
            "declared_breakdowns": ["G3", "G4", "G6"],
            "value": total,
            "unit": "MW",
            "rows": len(rows),
            "row_share_of_the_overdue_tier": share(len(rows), overdue["rows"]),
            "capacity_share_of_the_overdue_tier": share(total, Decimal(str(overdue["mw"]))),
            "claim": (
                f"{len(rows)} of the {overdue['rows']} entries in the confirmed tier that "
                f"are past their confirmed date \u2014 {mw(total)} MW of "
                f"{mw(overdue['mw'])} MW \u2014 carry a project status of "
                f"\u201c{SCOPING_STATUS}\u201d in the same copy."
            ),
            "the_rows": [
                {
                    "project": r["project_name"],
                    "mw": r["mw"],
                    "effective_from_as_printed": r["effective_as_published"],
                    "status": r["status"],
                }
                for r in rows
            ],
            "must_travel_with_the_claim": travels,
        }
    }


def post_facts(
    census: dict[str, Any],
    certificates: list[dict[str, Any]],
    gate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Every figure the draft below uses, as a register of slots."""
    scale = census["scale"]
    long_record = _cert(certificates, "eggborough-2014-01-31")
    current = _cert(certificates, "eggborough-ccgt-ocgt-bess-2025-07-01")
    now = current["record"]["as_of"][1]["state"]
    trace_copies = oq.distinct_copies([c.get("status_trace") or {} for c in certificates])
    trace_statuses = sorted({n for c in certificates for n in (c.get("status_trace") or {})})
    common = {
        "as_of": census["as_of"],
        "source": "NESO TEC Register",
        "source_sha256": census["copy"]["sha256"],
        "source_path": census["copy"]["path"],
        "declaration_sha256": census["declaration_sha256"],
        "schema_report_sha256": census["schema_report_sha256"],
    }
    slots = {
        "gb-tec-overdue-entries-2026-09": {
            **common,
            "value": census["selected_rows"],
            "unit": "register rows",
            "claim": (
                f"In the copy of NESO's TEC Register published on {census['as_of']}, "
                f"{census['selected_rows']} entries have an effective date earlier than that "
                "publication date and a project status other than “Built”."
            ),
            "evidence": "investigations/017-the-overdue-queue/evidence/rows.ndjson",
        },
        "gb-tec-overdue-capacity-2026-09": {
            **common,
            "value": census["selected_mw"],
            "unit": "MW (MW Increase / Decrease, summed over rows)",
            "claim": (
                f"Those {census['selected_rows']} entries carry "
                f"{mw(census['selected_mw'])} MW of stage TEC as published."
            ),
            "second_reading": {
                "value": census["selected_mw_largest_per_id"],
                "distinct_project_ids": census["distinct_project_ids"],
                "rule": "each project id counted once, keeping the largest of its rows",
            },
            "evidence": "investigations/017-the-overdue-queue/evidence/census.json",
        },
        "gb-tec-queue-future-capacity-2026-09": {
            **common,
            "value": scale["mw_dated_on_or_after_as_of"],
            "unit": "MW",
            "claim": (
                f"The same copy carries {mw(scale['mw_dated_on_or_after_as_of'])} MW dated on "
                f"or after {census['as_of']}, across "
                f"{scale['rows_dated_on_or_after_as_of']:,} rows."
            ),
        },
        "gb-tec-queue-scoping-capacity-2026-09": {
            **common,
            "value": scale["mw_scoping_dated_on_or_after_as_of"],
            "unit": "MW",
            "claim": (
                f"Of that, {mw(scale['mw_scoping_dated_on_or_after_as_of'])} MW is at status "
                "“Scoping”."
            ),
        },
        "gb-tec-undated-rows-are-built-2026-09": {
            **common,
            "value": census["undated"],
            "unit": "rows",
            "claim": (
                f"Every one of the copy's {census['undated']} rows with no readable effective "
                f"date is a row the register calls “Built”: the copy carries "
                f"{census['status_counts_all_rows'].get('Built', 0)} “Built” rows, "
                f"{census['dated_built']} of them dated."
            ),
        },
        "eggborough-tec-record-2018-2026": {
            **common,
            "value": len(trace_copies),
            "unit": "copies of the register the project appears in",
            "copies": trace_copies,
            "claim": (
                f"In every one of the {len(trace_copies):,} copies of the register in which "
                "the project now named \u201cEggborough CCGT - OCGT - BESS\u201d appears, "
                f"from {trace_copies[0]} to {trace_copies[-1]}, its published status reads "
                + (
                    f"\u201c{trace_statuses[0]}\u201d."
                    if len(trace_statuses) == 1
                    else "one of: " + ", ".join(f"\u201c{n}\u201d" for n in trace_statuses) + "."
                )
            ),
            "certificate_ids": {c["bundle"]: c["certificate_id"] for c in certificates},
            "names_the_register_has_used": [c["record"]["project"] for c in certificates],
            "long_record_copies_consulted": long_record["record"]["vintages_consulted"],
        },
        "eggborough-stage-1-tec-2026-09": {
            **common,
            "value": now.get("MW increase / decrease (stage TEC)"),
            "unit": "MW",
            "claim": (
                "As published on "
                f"{census['as_of']}, stage 1 of “Eggborough CCGT - OCGT - BESS” at "
                f"Eggborough 400kV Substation reads "
                f"{now.get('MW increase / decrease (stage TEC)')} MW, effective from "
                f"{now.get('MW effective from (target date)')}, status "
                f"“{now.get('Project status')}”."
            ),
            "certificate_id": current["certificate_id"],
        },
    }
    if gate:
        slots.update(_gate_slots(census, gate))
    return {
        "register": "BEDROCK candidate slots",
        "governed_by": [
            "investigations/017-the-overdue-queue/DECLARATION.md",
            "investigations/017-the-overdue-queue/DECLARATION-v2.md",
        ],
        "not_pinned_here": [
            "The Planning Inspectorate's decision on the Eggborough development consent "
            "order, 20 September 2018. Stated from the public planning record; no artefact "
            "for it is held in this repository. Any outbound use must carry that caveat."
        ],
        "slots": slots,
    }


def render_post(
    census: dict[str, Any],
    certificates: list[dict[str, Any]],
    gate: dict[str, Any] | None = None,
) -> str:
    """The draft post. Plain words, the stake first, the method at the end;
    every figure comes from a slot in `post_facts`."""
    facts = post_facts(census, certificates, gate)["slots"]
    tier = next(g for g in (gate or {}).get("g1_copy_by_gate", []) if g["gate"] == "2")
    overdue = next(g for g in gate["g2_overdue_by_gate"] if g["gate"] == "2") if gate else None
    assert gate is not None and overdue is not None
    g6 = gate["g6_summary"]
    scoping = next(
        c
        for c in gate["g3_overdue_by_gate_and_status"]
        if c["gate"] == "2" and c["status"] == "Scoping"
    )
    oldest = min(gate["g4_confirmed_tier_overdue"], key=lambda r: str(r["effective"]))
    contested = [
        r for r in gate["g4_confirmed_tier_overdue"] if r["dates_across_gated_copies_not_past"]
    ]
    respelled = [r for r in contested if r["a_not_past_date_is_the_day_month_swap"]]
    moved = [r for r in contested if not r["a_not_past_date_is_the_day_month_swap"]]
    long_record = _cert(certificates, "eggborough-2014-01-31")
    scoping_slot = facts["gb-tec-gate2-overdue-scoping-2026-09"]
    scoping_contested = [
        r
        for r in gate["g4_confirmed_tier_overdue"]
        if r["status"] == SCOPING_STATUS and r["dates_across_gated_copies_not_past"]
    ]
    scoping_contested_rows = len(scoping_contested)
    scoping_contested_mw = sum(
        (Decimal(str(r["mw"])) for r in scoping_contested if r["mw"] is not None), Decimal(0)
    )
    scoping_slot = facts["gb-tec-gate2-overdue-scoping-2026-09"]
    scoping_contested = [
        r
        for r in gate["g4_confirmed_tier_overdue"]
        if r["status"] == SCOPING_STATUS and r["dates_across_gated_copies_not_past"]
    ]
    scoping_contested_rows = len(scoping_contested)
    scoping_contested_mw = sum(
        (Decimal(str(r["mw"])) for r in scoping_contested if r["mw"] is not None), Decimal(0)
    )
    return "\n".join(
        [
            "<!-- DRAFT, held for the sponsor's second seal. Not posted. Rendered from",
            "investigations/017-the-overdue-queue/evidence by render_post.py. -->",
            "",
            "# Britain's connection queue has a tier that means \u201cconfirmed\u201d. "
            f"{pct(overdue['capacity_share_of_its_gate'])} of it is already past the date "
            "it confirmed.",
            "",
            "Last year the rules for connecting to the grid changed. Projects used to join "
            "a queue in the order they applied. Now NESO sorts them into two tiers, and the "
            "whole point of the reform is what the tiers mean. Here is NESO's own wording:",
            "",
            "> Gate 2 applies to projects that meet the new requirements for readiness [\u2026] "
            "These projects can secure a **confirmed** connection date, connection point, "
            "and queue position. Gate 1 applies to projects that do not meet the Gate 2 "
            "criteria [and] will not be assigned a confirmed connection date.",
            "",
            "So Gate 2 is the promise. It is the tier a developer raises money against, a "
            "supply chain plans around, and a system operator counts on when it says how "
            "much capacity is coming and when.",
            "",
            f"In the register NESO published on {census['as_of']}, the confirmed tier holds "
            f"{tier['rows']} projects and {mw(tier['mw'])} MW.",
            "",
            f"**{overdue['rows']} of them, {mw(overdue['mw'])} MW, are already past the date "
            "they confirmed.** That is "
            f"{pct(overdue['row_share_of_its_gate'])} of the tier's projects and "
            f"{pct(overdue['capacity_share_of_its_gate'])} of its capacity \u2014 two "
            "different measures that happen to land in the same place.",
            "",
            "## The part I did not expect",
            "",
            "A date can pass for ordinary reasons. A project is confirmed for a Tuesday in "
            "March, something slips, and the date goes by. That is a normal thing for a "
            "register to record.",
            "",
            "That is not what happened here.",
            "",
            "I hold four copies of the register that carry the Gate column: "
            + ", ".join(gate["g6_gated_copies"])
            + f". In **every one of the {g6['rows']} cases**, the date had already passed "
            "in the first copy where that project shows up in the confirmed tier. Not one "
            "of them was confirmed for a future date and then missed it. Every one was put "
            "into the confirmed tier carrying a date that had already gone \u2014 "
            f"{oldest['project_name']} by more than two years.",
            "",
            "The tier is doing what it was designed to do for the projects in it. It is "
            "just that for these, the date it confirms is a date in the past.",
            "",
            "## And one more thing in the same table",
            "",
            f"{scoping['rows']} of the {overdue['rows']} \u2014 {mw(scoping['mw'])} MW "
            "\u2014 sit in the confirmed tier at a project status of "
            "\u201cScoping\u201d. That is the status this copy of the register also gives "
            f"to {census['status_counts_all_rows'].get('Scoping', 0):,} other entries, "
            f"{census['scale']['rows_scoping_dated_on_or_after_as_of']:,} of which are "
            "dated years into the future. I am not going to tell you what to make of a "
            "project being ready enough to confirm and still at Scoping. I am telling you "
            "the two columns say that, side by side, in NESO's own file.",
            "",
            "Here they are. Names as the register prints them, dates as the register prints them:",
            "",
            *_table(
                ["Project", "MW", "Connection date the register gives it", "Status"],
                [
                    [
                        r["project"],
                        mw(r["mw"]),
                        f"`{r['effective_from_as_printed']}`",
                        r["status"],
                    ]
                    for r in scoping_slot["the_rows"]
                ],
            ),
            "",
            "Every one of those nine, individually and not just as part of the wider "
            f"{overdue['rows']}, was already past its date in the first copy I hold where "
            "its Gate cell reads 2.",
            "",
            "Two of the nine are the ones I am least sure about \u2014 see the next "
            f"section \u2014 and they are {mw(scoping_contested_mw)} of the "
            f"{mw(scoping['mw'])} MW, which is "
            f"{pct(share(scoping_contested_mw, Decimal(str(scoping['mw']))))} of this "
            "particular figure. Without them it is "
            f"{mw(Decimal(str(scoping['mw'])) - scoping_contested_mw)} MW over "
            f"{scoping['rows'] - scoping_contested_rows} projects.",
            "",
            "## Here is where I might be wrong, before anyone tells me",
            "",
            f"{len(contested)} of the {overdue['rows']} entries are ones another copy of "
            "the register publishes with a date that is not past at all, and together they "
            f"are {mw(g6['mw_a_gated_copy_publishes_as_not_past'])} MW of the "
            f"{mw(overdue['mw'])}.",
            "",
            *[
                f"- **{r['project_name']}, {mw(r['mw'])} MW.** This copy prints its date as "
                f"`{r['effective_as_published']}`. An earlier copy prints the same digits "
                "with the day and the month the other way round, as "
                + ", ".join(f"`{d}`" for d in r["dates_across_gated_copies_not_past"])
                + ", which has not happened yet. I cannot tell you from one file which "
                "reading is right."
                for r in respelled
            ],
            *[
                f"- **{r['project_name']}, {mw(r['mw'])} MW.** An earlier copy gave it "
                + ", ".join(f"`{d}`" for d in r["dates_across_gated_copies_not_past"])
                + f"; this one gives `{r['effective']}`. The register moved the date "
                "earlier, and the earlier date is the one still ahead of us."
                for r in moved
            ],
            "",
            f"Take them out and the number is "
            f"{mw(g6['mw_if_those_rows_are_read_as_not_past'])} MW over "
            f"{g6['rows_if_those_rows_are_read_as_not_past']} projects instead of "
            f"{mw(overdue['mw'])} MW over {overdue['rows']}.",
            "",
            "I am publishing the larger number because that is what the rule I wrote down "
            "in advance produces from the file as it is spelled, and I am publishing this "
            "paragraph in the same breath because that is the honest size of the "
            "uncertainty. If you quote one, quote the other.",
            "",
            "There is no double counting to net off. The two 540 MW offshore platform rows "
            "on the list are separate entries with different project numbers, not one "
            "project counted twice. I checked, because I assumed the opposite.",
            "",
            "## Why any of this is hard to see",
            "",
            "NESO publishes this register weekly and replaces it each time. There is no "
            "history. If you want to know whether a date has just moved or has been wrong "
            "for eight years, you have to have kept the old copies \u2014 so I have: "
            f"{long_record['record']['vintages_consulted']:,} readable copies back to "
            "January 2014.",
            "",
            "What that archive shows is that the register is harder to read than it looks. "
            "One project in it has been called three different things; in the copy of 5 "
            "January 2024 its old name was handed to a completely different, smaller "
            "project, id and all, so anyone tracking it by name has been following the "
            "wrong row ever since. Today that project reads "
            f"{mw(facts['eggborough-stage-1-tec-2026-09']['value'])} MW, due in a fortnight, at "
            "a status it has carried in every one of "
            f"{facts['eggborough-tec-record-2018-2026']['value']} copies since November "
            "2018.",
            "",
            "## The boring part that makes the rest worth reading",
            "",
            "Both counting rules were written down, timestamped and published **before** "
            "the numbers were computed \u2014 including a written record of the rough "
            "figures I already had in my head, and of the two places where the careful run "
            "disagreed with them. The file is pinned by its digest. NESO's definition of "
            "the tiers is pinned too. Anyone can take the same file, apply the same rule, "
            "and get a different answer if I have this wrong.",
            "",
            "That is the whole method: say what you will count before you count it, then "
            "publish the thing that would prove you wrong next to the thing you found.",
            "",
            "*What this does not say: that any of these projects is late, has failed, or "
            "will fail. A register records a tier and a date. It does not record whether "
            "anything got built, and I have not inferred that it does.*",
            "",
        ]
    )


# --------------------------------------------------- version 2: the Gate column


#: The register's own word, quoted rather than characterised.
SCOPING_STATUS: str = "Scoping"


def pct(value: object) -> str:
    """A declared share as a percentage. R11 keeps the row share and the
    capacity share apart, so this never merges two of them."""
    if value is None or value == "":
        return "—"
    return f"{Decimal(str(value)) * 100:.1f}%"


def gate_label(entry: dict[str, Any]) -> str:
    """A Gate class as the page names it: the register's own cell, and the
    tier only where NESO's pinned definition supplies one."""
    printed = entry.get("gate") or ""
    if not printed:
        return "(blank)"
    tier = entry.get("tier")
    return f"`{printed}` ({tier})" if tier else f"`{printed}`"


def _gate_rows_table(rows: list[dict[str, Any]]) -> list[str]:
    return _table(
        ["Due", "Project", "Connection site", "Stage", "Plant type", "Status", "MW"],
        [
            [
                str(r["effective"]),
                str(r["project_name"]),
                str(r["connection_site"]),
                str(r["stage"] or "—"),
                str(r["plant_type"]),
                str(r["status"]),
                mw(r["mw"]),
            ]
            for r in rows
        ],
    )


def _gate_section(gate: dict[str, Any], census: dict[str, Any]) -> list[str]:
    confirmed_row = next((g for g in gate["g1_copy_by_gate"] if g["gate"] == "2"), None)
    overdue2 = next((g for g in gate["g2_overdue_by_gate"] if g["gate"] == "2"), None)
    g6 = gate["g6_summary"]
    already_past_mw = g6["mw_whose_date_had_already_passed_when_first_in_the_tier"]
    scoping = next(
        (
            c
            for c in gate["g3_overdue_by_gate_and_status"]
            if c["gate"] == "2" and c["status"] == "Scoping"
        ),
        None,
    )
    scoping_all = census["status_counts_all_rows"].get("Scoping", 0)
    lines = [
        "## What the count is *of*: the confirmed tier",
        "",
        "*This section is version 2 of the declaration (`DECLARATION-v2.md`, SHA-256 "
        f"`{gate['declaration_sha256']}`), frozen after the census above had run and before "
        "any figure in this section was computed. Version 1's census is unchanged by it.*",
        "",
        "Under NESO's connections reform the queue is sorted into tiers. NESO's own "
        "published definition, pinned in this repository "
        f"(`{gate['gate_definition']['path']}`, SHA-256 "
        f"`{gate['gate_definition']['sha256'][:16]}…`, fetched "
        f"{gate['gate_definition']['fetched_at'][:10]}), says it in these words:",
        "",
        "> Gate 2 applies to projects that meet the new requirements for readiness and "
        "Strategic Alignment. These projects can secure a **confirmed** connection date, "
        "connection point, and queue position. Gate 1 applies to projects that do not meet "
        "the Gate 2 criteria. […] Gate 1 projects will not be assigned a confirmed "
        "connection date but may progress through future windows if readiness is "
        "demonstrated.",
        "",
        "So a date in the Gate 2 tier is a *confirmed* date in NESO's own sense. Every "
        f"copy of the register this archive holds from {gate['g6_gated_copies'][0]} carries "
        "a `Gate` column; the archive holds none at all between 22 July 2025 and that date, "
        "so the column's earlier history is not reconstructable here. Two cautions, both "
        "declared before this was computed: the register does **not** print the words "
        "“Gate 1” and “Gate 2” — it prints `1` and `2`, and "
        "reading those as the two tiers is the one interpretation made here; and NESO's "
        "definition says nothing about a **blank** cell, so a blank is reported as a blank "
        "and is never called “not assessed” or folded into either tier.",
        "",
        "### The copy, split by Gate (G1)",
        "",
        *_table(
            ["Gate cell", "Rows", "MW"],
            [[gate_label(g), f"{g['rows']:,}", mw(g["mw"])] for g in gate["g1_copy_by_gate"]],
        ),
        "",
        "### The overdue entries, split by Gate (G2)",
        "",
        *_table(
            [
                "Gate cell",
                "Rows",
                "MW",
                "Row share of the overdue",
                "Capacity share of the overdue",
                "Row share of its own Gate",
                "Capacity share of its own Gate",
            ],
            [
                [
                    gate_label(g),
                    f"{g['rows']:,}",
                    mw(g["mw"]),
                    pct(g["row_share_of_overdue"]),
                    pct(g["capacity_share_of_overdue"]),
                    pct(g["row_share_of_its_gate"]),
                    pct(g["capacity_share_of_its_gate"]),
                ]
                for g in gate["g2_overdue_by_gate"]
            ],
        ),
        "",
    ]
    if confirmed_row and overdue2:
        lines += [
            f"**{overdue2['rows']} of the {confirmed_row['rows']} entries in the confirmed "
            f"tier are already past their confirmed date**, carrying "
            f"{mw(overdue2['mw'])} MW of the tier's {mw(confirmed_row['mw'])} MW. That is "
            f"{pct(overdue2['row_share_of_its_gate'])} of the tier's rows and "
            f"{pct(overdue2['capacity_share_of_its_gate'])} of its capacity. The two shares "
            "are close here, which is a coincidence of this copy and not a general fact; "
            "they are computed and printed separately for that reason, and neither stands "
            "for the other.",
            "",
        ]
    lines += [
        "### Which statuses sit inside the tier (G3)",
        "",
        *_table(
            ["Gate cell", "Status as printed", "Rows", "MW"],
            [
                [gate_label(c), c["status"] or "(blank)", f"{c['rows']:,}", mw(c["mw"])]
                for c in gate["g3_overdue_by_gate_and_status"]
            ],
        ),
        "",
    ]
    if scoping:
        lines += [
            f"{scoping['rows']} of the {overdue2['rows'] if overdue2 else 0} overdue "
            f"confirmed-tier entries — {mw(scoping['mw'])} MW — read "
            "“Scoping”. That is the status the register prints for "
            f"{scoping_all:,} of this copy's {census['rows_total']:,} rows, "
            f"{census['scale']['rows_scoping_dated_on_or_after_as_of']:,} of which are dated "
            "in the future. The page draws no conclusion from that pairing; it is what the "
            "two columns say side by side.",
            "",
        ]
    lines += [
        "### Every overdue entry in the confirmed tier (G4)",
        "",
        *_gate_rows_table(gate["g4_confirmed_tier_overdue"]),
        "",
        "### What the gated copies show (G6), and the question they answer",
        "",
        "A single copy cannot say whether a confirmed date was set and then passed, or "
        "whether the entry was moved into the confirmed tier with the date already gone. "
        "Only the copies can, and the archive holds "
        f"{len(gate['g6_gated_copies'])} that carry a `Gate` column: "
        + ", ".join(gate["g6_gated_copies"])
        + ".",
        "",
        *_table(
            ["Project", "MW", "Due, as this copy prints it"]
            + [f"Gate / date in the copy of {d}" for d in gate["g6_gated_copies"]],
            [
                [r["project_name"], mw(r["mw"]), str(r["effective"])]
                + [
                    (
                        f"{(x['gate'] or 'blank')} / {x['effective_as_published']}"
                        if x["found"]
                        else "no matching row"
                    )
                    for x in r["readings"]
                ]
                for r in gate["g4_confirmed_tier_overdue"]
            ],
        ),
        "",
        f"**In every one of the {g6['rows']} cases, the date had already passed in the first "
        "of these copies whose Gate cell reads `2`.** Not one of them was given a confirmed "
        "date in these copies and then watched it go by: each was published into the "
        "confirmed tier carrying a date that was already behind it, some by weeks and some "
        f"by more than two years. That covers {mw(already_past_mw)} "
        "MW. It is a statement about what the register published and when, not about any "
        "project's readiness and not about delivery.",
        "",
    ]
    if g6["rows_a_gated_copy_publishes_as_not_past"]:
        swap_rows = [
            r for r in gate["g4_confirmed_tier_overdue"] if r["dates_across_gated_copies_not_past"]
        ]
        lines += [
            "**And the figure has to carry this against itself.** "
            f"{g6['rows_a_gated_copy_publishes_as_not_past']} of the "
            f"{g6['rows']} rows, {mw(g6['mw_a_gated_copy_publishes_as_not_past'])} MW, are "
            "rows some copy above publishes with a date that is **not** past at all:",
            "",
            *_table(
                ["Project", "MW", "This copy", "Another copy", "Which kind of difference"],
                [
                    [
                        r["project_name"],
                        mw(r["mw"]),
                        str(r["effective"]),
                        ", ".join(str(d) for d in r["dates_across_gated_copies_not_past"]),
                        (
                            "the same digits with day and month exchanged"
                            if r["a_not_past_date_is_the_day_month_swap"]
                            else "the register moved the date"
                        ),
                    ]
                    for r in swap_rows
                ],
            ),
            "",
            "The census rule reads each copy as it is spelled and does not apply the "
            "day-month correction to a single copy, so those rows are inside the count "
            "above, as declared. On the other reading the confirmed tier's overdue capacity "
            f"is {mw(g6['mw_if_those_rows_are_read_as_not_past'])} MW over "
            f"{g6['rows_if_those_rows_are_read_as_not_past']} rows. Both numbers are "
            "published here; anyone quoting the larger one should quote this paragraph "
            "with it.",
            "",
        ]
    repetition = gate["g5_repetition"]
    if not repetition["sharing_a_project_id"] and not repetition["sharing_a_project_name"]:
        lines += [
            "**Repetition (G5).** None. No two of the overdue confirmed-tier rows share a "
            "project id, and no two share a project name: the two 540 MW offshore platform "
            "rows are printed as separate entries, `Platform 1` and `Platform 2`, with "
            "different project ids and different project numbers. There is no double count "
            "to net off and no second reading to publish.",
            "",
        ]
    else:
        lines += [
            "**Repetition (G5).** Rows sharing a project id: "
            + (", ".join(f"`{g['key']}`" for g in repetition["sharing_a_project_id"]) or "none")
            + ". Rows sharing a project name: "
            + (", ".join(f"{g['key']}" for g in repetition["sharing_a_project_name"]) or "none")
            + f". Together they carry {mw(repetition['mw_in_repeated_rows'])} MW.",
            "",
        ]
    lines += [
        "**What this section does not say.** That any of these projects has failed to "
        "deliver, or will. The register records a tier and a date; it does not record "
        "delivery, and nothing is inferred about it here. Nor is anything said about "
        "whether NESO's assessment was right — that is not a question this evidence "
        "can reach.",
        "",
    ]
    return lines


# ------------------------------------------------------------------ the web page
# `site/overdue-queue/index.html` is FINDINGS.md in the style of 014's page,
# with a lead that leads on the row share. Every number in the lead is read
# from the evidence; the one sentence about the exhibit is checked against
# FINDINGS.md before it is printed.

PAGE_TITLE = "The queue that is past its own date"
PAGE_SUBTITLE = (
    "Entries in Britain's grid-connection register whose own connection date has passed, "
    "counted under a method sealed before the count"
)
PAGE_INVESTIGATION = "investigations/017-the-overdue-queue"
#: The exhibit sentence of the lead, and the phrases of FINDINGS.md it rests
#: on; if FINDINGS.md stops carrying any of them the page is not rendered.
EXHIBIT_LEAD = (
    "A single copy cannot tell a date written last week from one written years ago. "
    "One project shows why the copies have to be kept: the register has called the "
    "2,450 MW project at Eggborough by three different names, has given its old name to "
    "a different project (in January 2024), and in every one of the 511 copies that show it, "
    "from November 2018 to September 2026, has printed its status as “Awaiting Consents”."
)
EXHIBIT_SUPPORT = (
    "the register has called this project three different things",
    "the register has given the bare name to a different, smaller project",
    "**511 copies** of the register, from 2018-11-08 to 2026-09-15",
    "the status reads “Awaiting Consents”",
    "2,450 MW at Eggborough 400kV Substation",
)
PAGE_CSS = """\
table{min-width:40rem}
th,td,thead th{text-align:left;white-space:normal}
h3{font-size:1.05rem;margin:1.5rem 0 .4rem}
blockquote{margin:1rem 0;padding:.25rem 0 .25rem 1rem;border-left:3px solid var(--rule);
max-width:44rem}
blockquote p{margin:.4rem 0}
pre{overflow-x:auto;background:var(--seed);padding:.75rem;font-size:.85rem}
li{max-width:44rem;margin:.3rem 0}
code{font-size:.9em;overflow-wrap:anywhere}
.forward{max-width:44rem}
"""

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<![*\w])\*(?![\s*])(.+?)(?<![\s*])\*(?![*\w])")


def inline_html(text: str) -> str:
    """The inline markdown FINDINGS.md uses: code spans, bold, italic.
    Everything else is escaped as text. Code spans are set aside first, so
    emphasis may run across one and nothing inside one is emphasised."""
    spans: list[str] = []

    def hold(m: re.Match[str]) -> str:
        spans.append(f"<code>{escape(m.group(1))}</code>")
        return f"\x00{len(spans) - 1}\x00"

    out = escape(re.sub(r"`([^`]*)`", hold, text), quote=False)
    out = _ITALIC.sub(r"<em>\1</em>", _BOLD.sub(r"<strong>\1</strong>", out))
    return re.sub("\x00(\\d+)\x00", lambda m: spans[int(m.group(1))], out)


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def markdown_html(markdown: str) -> str:
    """The block markdown FINDINGS.md uses, and no more: headings, paragraphs,
    pipe tables, block quotes, bullet lists and fenced code."""
    lines = markdown.split("\n")
    html: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            end = next(j for j in range(i + 1, len(lines)) if lines[j].startswith("```"))
            html.append("<pre><code>" + escape("\n".join(lines[i + 1 : end])) + "</code></pre>")
            i = end + 1
        elif m := re.match(r"(#{1,4}) (.*)", line):
            level = len(m.group(1))
            html.append(f"<h{level}>{inline_html(m.group(2))}</h{level}>")
            i += 1
        elif line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            head, body = _cells(block[0]), [_cells(r) for r in block[2:]]
            html.append(
                '<div class="scroll"><table><thead><tr>'
                + "".join(f"<th>{inline_html(c)}</th>" for c in head)
                + "</tr></thead><tbody>"
                + "".join(
                    "<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in r) + "</tr>"
                    for r in body
                )
                + "</tbody></table></div>"
            )
        elif line.startswith(">"):
            block = []
            while i < len(lines) and lines[i].startswith(">"):
                block.append(lines[i].removeprefix(">").strip())
                i += 1
            html.append(f"<blockquote><p>{inline_html(' '.join(block))}</p></blockquote>")
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:])
                i += 1
            html.append("<ul>" + "".join(f"<li>{inline_html(t)}</li>" for t in items) + "</ul>")
        else:
            block = []
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"(#{1,4} |\||>|- |```)", lines[i])
            ):
                block.append(lines[i])
                i += 1
            html.append(f"<p>{inline_html(' '.join(block))}</p>")
    return "\n".join(html)


def day(iso: str) -> str:
    """`2026-09-15` as `15 September 2026`."""
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def page_lead(census: dict[str, Any], gate: dict[str, Any]) -> list[str]:
    """The lead, as HTML paragraphs: the confirmed tier's row share first and
    its capacity share beside it (R11), the other reading of the tier in the
    next sentence, the whole census by rows with its id reading (R6), and
    what none of it says."""
    tier = next(e for e in gate["g2_overdue_by_gate"] if e["gate"] == oq.CONFIRMED_TIER)
    other = gate["g6_summary"]
    return [
        '<p class="headline">'
        f"Of the {tier['rows_in_copy']} entries in the confirmed tier of NESO's connection "
        "register, the tier NESO says carries a confirmed connection date, "
        f"<strong>{tier['rows']} were already past that date</strong> in the copy published "
        f"on {day(census['as_of'])}: {pct(tier['row_share_of_its_gate'])} of the tier's "
        f"entries, and {pct(tier['capacity_share_of_its_gate'])} of its capacity.</p>",
        "<p>Another copy of the register prints "
        f"{other['rows_a_gated_copy_publishes_as_not_past']} of those {tier['rows']} "
        "dates as not yet past, so on that reading it is "
        f"{other['rows_if_those_rows_are_read_as_not_past']} entries. Both readings are set "
        "out below, and neither is quoted here without the other. Across the whole register, "
        f"{census['selected_rows']} entries ({census['distinct_project_ids']} distinct project "
        "ids) say their date has passed and do not say “Built”.</p>",
        "<p>None of this says that any project is late. The register records a date and a "
        "status, not delivery, and NESO describes the status as its best-known "
        "classification. What is counted is what the document says.</p>",
        f"<p>{escape(EXHIBIT_LEAD)}</p>",
    ]


def v3_page_paragraph(v3: dict[str, Any], base: str) -> str:
    """The page's line on version 3, in place of the promise that it would be
    run: the two later copies' confirmed-tier figure with its other reading,
    and what changed between them, all read from the evidence."""
    ref, nxt = (c["census"] for c in v3["copies"])
    tiers = [
        next(g for g in c["gate"]["g2_overdue_by_gate"] if g["gate"] == oq.CONFIRMED_TIER)
        for c in v3["copies"]
    ]
    others = [
        c["gate"]["g6_summary"]["rows_if_those_rows_are_read_as_not_past"] for c in v3["copies"]
    ]
    d2 = v3["comparison"]["d2"]["classes"]
    left = sum(v["rows"] for k, v in d2.items() if k.startswith("reference only"))
    arrived = d2.get("next only: (b) the date arrived", {"rows": 0})["rows"]
    joined = sum(v["rows"] for k, v in d2.items() if k.startswith("next only"))
    t = tiers[1]
    if _same([(x["rows"], x["rows_in_copy"]) for x in tiers]) and _same(others):
        tier = (
            f"In both, {t['rows']} of the confirmed tier's {t['rows_in_copy']} entries are past "
            f"their date ({pct(t['row_share_of_its_gate'])} of its entries, "
            f"{pct(t['capacity_share_of_its_gate'])} of its capacity; {others[1]} on the other "
            "reading)"
        )
    else:
        tier = "; ".join(
            f"on {day(c['as_of'])}, {x['rows']} of the confirmed tier's {x['rows_in_copy']} "
            f"entries are past their date ({o} on the other reading)"
            for c, x, o in zip((ref, nxt), tiers, others, strict=True)
        ).capitalize()
    change = (
        f"across the register the list went from {ref['selected_rows']} to "
        f"{nxt['selected_rows']} entries"
        + (
            ", only because " + ("one date" if arrived == 1 else f"{arrived} dates") + " arrived"
            if joined == arrived and not left and arrived
            else f" ({joined} joined, {left} left)"
        )
    )
    name, sha = "DECLARATION-v3.md", v3["declaration_sha256"]
    return (
        '<p class="forward"><strong>Two later copies, counted the same way.</strong> The method '
        f'was sealed in <a href="{escape(base)}/{escape(name)}">{escape(name)}</a> '
        f"(SHA-256 <code>{escape(sha[:16])}…</code>) and its amendment before the copies NESO "
        f"published on {escape(day(ref['as_of']))} and {escape(day(nxt['as_of']))} were counted. "
        f"{escape(tier)}, and {escape(change)}. The section “Two later copies” below has both "
        "counts and the comparison.</p>"
    )


def render_page(
    findings: str,
    census: dict[str, Any],
    gate: dict[str, Any],
    *,
    next_declaration: tuple[str, str] | None = None,
    v3: dict[str, Any] | None = None,
    repo_url: str = "https://github.com/jordan-dimov/grid-mysteries",
    credibility: str = "",
    contact_email: str = "",
) -> str:
    """The web page: the lead, then FINDINGS.md as rendered (its title
    replaced by the page's), then where the record lives. `next_declaration`
    is (file name, SHA-256) of a declaration frozen for a later copy."""
    missing = [p for p in EXHIBIT_SUPPORT if p not in findings]
    if missing:
        raise ValueError(f"FINDINGS.md no longer supports the page's exhibit sentence: {missing}")
    body = findings.split("\n", 1)[1] if findings.startswith("# ") else findings
    base = f"{repo_url}/blob/main/{PAGE_INVESTIGATION}"
    forward = ""
    if v3:
        forward = v3_page_paragraph(v3, base)
    elif next_declaration:
        name, sha = next_declaration
        forward = (
            '<p class="forward"><strong>The next copy is already declared.</strong> '
            f'<a href="{escape(base)}/{escape(name)}">{escape(name)}</a> '
            f"(SHA-256 <code>{escape(sha[:16])}…</code>) was sealed before any figure in it "
            "was computed. It applies this method to the copy NESO published on 25 September "
            "2026 and to the first copy published on or after 29 September 2026, and it "
            "declares how the two will be compared. Both results will be reported in the "
            "findings, whichever way they come out.</p>"
        )
    contact = (
        f'<p>Questions or challenges: <a href="mailto:{escape(contact_email)}">'
        f"{escape(contact_email)}</a></p>"
        if contact_email
        else ""
    )
    from grid_mysteries.rendering.connection_slippage import CSS

    lead = "\n".join(page_lead(census, gate))
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(PAGE_TITLE)}</title>
<meta name="description" content="{escape(PAGE_SUBTITLE)}">
<style>
{CSS}{PAGE_CSS}</style>
</head>
<body>
<header>
<h1>{escape(PAGE_TITLE)}</h1>
<p class="subtitle">{escape(PAGE_SUBTITLE)}</p>
</header>
<main>
{lead}
{forward}
{markdown_html(body)}
<p class="notes">This page is <a href="{escape(base)}/FINDINGS.md">FINDINGS.md</a>
with a lead added, both pure functions of the committed evidence
(<a href="{escape(repo_url)}/tree/main/{PAGE_INVESTIGATION}/evidence">evidence/</a>)
and of the corrections in <code>corrections.json</code>.</p>
</main>
<footer>
<p>{escape(credibility)}</p>
{contact}
</footer>
</body>
</html>
"""
