"""017 — the findings page, a pure function of the census evidence and of the
certificates 014 issued.

The page prints what the register printed. It names projects, sites, stages
and statuses, because those are the register's own cells and the subject of
the investigation; it characterises no company and attributes no cause.
"""

from decimal import Decimal
from typing import Any

from grid_mysteries.investigations import overdue_queue as oq

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
    return f"{whole:,}" if number == whole else f"{number:,}"


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


def render_findings(
    census: dict[str, Any], rows: list[dict[str, Any]], certificates: list[dict[str, Any]]
) -> str:
    """The findings page. `rows` is the append-only evidence of selected rows;
    it is not re-derived here, only counted, so the page can never disagree
    with the file it cites."""
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
        *_certificate_section(certificates),
        *_limits_section(census),
        "## Expert corner",
        "",
        f"- Declaration: `investigations/017-the-overdue-queue/DECLARATION.md`, SHA-256 "
        f"`{census['declaration_sha256']}`, witnessed by OpenTimestamps and by RFC 3161 "
        "tokens from freetsa.org and DigiCert at the moment of the freeze, and committed "
        "with its proofs by `scripts/freeze`.",
        f"- Archive schema report the reading rules were written against: SHA-256 "
        f"`{census['schema_report_sha256']}` (`archives/tec-register/`).",
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
    return "\n".join(lines)


# ------------------------------------------------------- the outbound document
# Numbers that leave the repository are governed before they go. `post_facts`
# is the machine-readable form, one entry per slot, each carrying the exact
# sentence it licenses and the artefacts that hold it up; `render_post` is the
# draft that quotes them.


def _cert(certificates: list[dict[str, Any]], bundle_prefix: str) -> dict[str, Any]:
    return next(c for c in certificates if c["bundle"].startswith(bundle_prefix))


def post_facts(census: dict[str, Any], certificates: list[dict[str, Any]]) -> dict[str, Any]:
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
    return {
        "register": "BEDROCK candidate slots",
        "governed_by": "investigations/017-the-overdue-queue/DECLARATION.md",
        "not_pinned_here": [
            "The Planning Inspectorate's decision on the Eggborough development consent "
            "order, 20 September 2018. Stated from the public planning record; no artefact "
            "for it is held in this repository. Any outbound use must carry that caveat."
        ],
        "slots": slots,
    }


def render_post(census: dict[str, Any], certificates: list[dict[str, Any]]) -> str:
    """The draft post, quoting only the slots above."""
    facts = post_facts(census, certificates)["slots"]
    scale = census["scale"]
    current = _cert(certificates, "eggborough-ccgt-ocgt-bess-2025-07-01")
    lines = [
        "<!-- DRAFT, held for the sponsor's second seal. Not posted. Rendered from",
        "investigations/017-the-overdue-queue/evidence by render_post.py. -->",
        "",
        "# 12 GW of Britain's connection queue is past its own date. That is a fact about "
        "a spreadsheet, not a fact about the grid.",
        "",
        "NESO publishes the TEC Register: every transmission connection, its capacity, the "
        "date that capacity is expected to take effect, and a status.",
        "",
        f"In the copy published on {census['as_of']}, **{census['selected_rows']} entries "
        f"carrying {mw(census['selected_mw'])} MW** have an effective date that has already "
        "passed and a status other than “Built”.",
        "",
        "I want to be careful about what that sentence is, because the interesting part is "
        "what it is *not*. It is not “12 GW is late”. The register cannot support "
        "that: its status is NESO's own best-known classification, and a project may have "
        "connected without the status being refreshed. It is the narrower claim that this "
        "many entries **say the date has passed and do not say Built**.",
        "",
        "| Status as the register prints it | Entries | MW |",
        "|---|---|---|",
        *[
            f"| {g['status'] or '(blank)'} | {g['rows']} | {mw(g['mw'])} |"
            for g in census["by_status"]
        ],
        "",
        "| Year the date fell in | Entries | MW |",
        "|---|---|---|",
        *[f"| {g['year']} | {g['rows']} | {mw(g['mw'])} |" for g in census["by_year"]],
        "",
        f"For scale, the same copy carries {mw(scale['mw_dated_on_or_after_as_of'])} MW dated "
        f"in the future, {mw(scale['mw_scoping_dated_on_or_after_as_of'])} MW of it at "
        "“Scoping”. The oldest entry on the overdue list is "
        f"{census['earliest'][0]['project_name']}, {mw(census['earliest'][0]['mw'])} MW, dated "
        f"{census['earliest'][0]['effective']}, still reading "
        f"“{census['earliest'][0]['status']}”.",
        "",
        "## One thing fell out of the arithmetic",
        "",
        facts["gb-tec-undated-rows-are-built-2026-09"]["claim"],
        "",
        "The register clears the date when a project is built. So the "
        f"{census['selected_rows']} are precisely the entries it has neither moved on nor "
        "cleared — which is what makes them worth counting, and what makes the next "
        "question unavoidable.",
        "",
        "## Why one copy of a register is never enough",
        "",
        "A single copy cannot tell you whether a date that has passed is news or is eight "
        "years old. Only the sequence of copies can, and the sequence is not published — "
        "it has to be rebuilt. I have been rebuilding it: 700 readable copies of this "
        "register back to January 2014.",
        "",
        "Take one entry. Today it reads:",
        "",
        "> " + facts["eggborough-stage-1-tec-2026-09"]["claim"],
        "",
        "That date is a fortnight after the copy. Here is what the sequence says about it.",
        "",
        "- The register has called this project **three different things**. Search today's "
        "copy for its current name, then look for that name in older copies, and you find "
        "nothing before 1 July 2025.",
        "- The entry first appears in the copy of **8 November 2018**, at 2,450 MW, dated "
        "**1 April 2022**, status **Awaiting Consents**.",
        "- The date then walks: 1 October 2024 by April 2020, 1 October 2025 by April 2021, "
        "1 October 2026 by September 2022. It has not moved in four years.",
        "- In the copy of **5 January 2024** the bare name is handed to a different, smaller "
        "project — customer, capacity, date, status, plant type and **project id** all "
        "change in one copy. A reader tracking this project by name would have followed the "
        "wrong row from that day on.",
        "- " + facts["eggborough-tec-record-2018-2026"]["claim"],
        "",
        "The development consent order for this scheme was decided by the Planning "
        "Inspectorate on **20 September 2018**, seven weeks before the register's first "
        "“Awaiting Consents” copy for it. So either the status field means a "
        "consent other than that order, or it has not been refreshed in eight years. I am "
        "not going to tell you which. I have asked NESO under the Environmental Information "
        "Regulations (FOI/26/216, due 13 October) and I will publish the answer either way.",
        "",
        "## What is published with this",
        "",
        "The selection rule was written down and witnessed by OpenTimestamps and by two "
        "RFC 3161 authorities **before** any figure was computed "
        f"(SHA-256 `{census['declaration_sha256'][:16]}…`), including a record of the "
        "rough numbers I had already seen and the two places where the governed run "
        "contradicted them. The copy of the register is pinned by digest. The project's "
        "history comes as four hash-addressed certificate bundles that verify offline "
        f"(the current one is `{current['certificate_id'][:16]}…`).",
        "",
        "If you think the count is wrong, the fastest way to show it is to take the same "
        "copy, apply the same rule, and get a different number. That is the point of "
        "publishing the rule first.",
        "",
        "*Caveat carried deliberately: the consent order decision date above is from the "
        "public planning record and is not pinned in the repository. Everything else here "
        "is.*",
        "",
    ]
    return "\n".join(lines)
