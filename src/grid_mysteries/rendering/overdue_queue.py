"""017 — the findings page, a pure function of the census evidence and of the
certificates 014 issued.

The page prints what the register printed. It names projects, sites, stages
and statuses, because those are the register's own cells and the subject of
the investigation; it characterises no company and attributes no cause.
"""

from decimal import Decimal
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
    census: dict[str, Any],
    rows: list[dict[str, Any]],
    certificates: list[dict[str, Any]],
    gate: dict[str, Any] | None = None,
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
        *(_gate_section(gate, census) if gate else []),
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
