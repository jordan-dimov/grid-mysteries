# 017 — The queue that is past its own date: declaration, version 2

**The Gate cross-tab.** Written 2026-09-17, after the schema pass that
covers the `Gate` column and before any Gate figure was computed in this
repository. Frozen by `scripts/freeze`, which witnesses these bytes with
OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert and
commits the file with its proofs.

## What this version is, and is not

Version 1 (`DECLARATION.md`, SHA-256 `400b42f7…`, witnessed and run
2026-09-17) **stands entirely as run**. Its census is not recomputed, not
re-chosen and not amended: the same 98 rows, the same 12,034.86 MW, the
same four classes, the same breakdowns, the same appended
`evidence/rows.ndjson`. This version adds **one new dimension over the same
copy** — the register's `Gate` column — and nothing else. Version 1's rule
R7 fixed its breakdowns at four and forbade adding a fifth after its run;
that is why this is a second declaration rather than an edit, and why the
Gate figures are computed only after this file is witnessed.

Everything version 1 declares is inherited verbatim and is not repeated:
the copy and its digest, the as-of date, the reading rules R1 to R6, the
measure, what the census never claims, and checks C1 to C5. Where this file
is silent, version 1 speaks.

## Why the Gate column is worth a declaration of its own

Version 1 answers *how many entries are past their date*. A reader may
fairly ask why that matters, and the register itself now supplies the
stake. Under NESO's connections reform, projects are sorted into tiers, and
NESO's own published definition — pinned in this repository at
`data/raw/neso/neso-g2wq-evidence-handbook-resources.html`, SHA-256
`cb5c712b7f43fa545725bae4cb942c2c4353b8c0a2095c5a65ce7694de6bb514`,
fetched 2026-08-23 from
`https://www.neso.energy/industry-information/connections-reform/evidence-handbook-and-other-g2wq-submission-resources`
and journalled at
`investigations/forward/F001-connection-readiness/evidence/public-as-of-journal.ndjson`
— says, in NESO's words:

> Gate 2 applies to projects that meet the new requirements for readiness
> and Strategic Alignment. These projects can secure a confirmed connection
> date, connection point, and queue position. Gate 1 applies to projects
> that do not meet the Gate 2 criteria. […] Gate 1 projects will not be
> assigned a confirmed connection date but may progress through future
> windows if readiness is demonstrated.

So a date in the Gate 2 tier is a **confirmed** date in NESO's own sense,
and a Gate 1 date is not. The question this version asks is therefore
narrow and has a stake in it: **how much of the confirmed tier is already
past its confirmed date, as the register publishes it?**

## Prior exposure (recorded, not hidden)

The author has seen ungoverned figures for exactly this cross-tab,
produced on 2026-09-17 by an ad-hoc script outside this repository, over
the same copy: whole copy by Gate — Gate 1 272,882.7 MW over 756 rows,
Gate 2 13,524.4 MW over 95 rows, blank 311,980.8 MW over 1,349 rows; the
98 overdue rows by Gate — blank 74 rows / 9,166.6 MW, Gate 2 17 rows /
2,497.9 MW, Gate 1 7 rows / 370.3 MW; and as the largest overdue Gate 2
rows, Inch Cape Offshore Wind Farm Platform twice at 540 MW (due
2026-02-21, Consents Approved), Eccles BESS 500 MW (due 2026-04-12,
Scoping) and Zenobe Eccles Battery Storage 400 MW (due 2026-04-30,
Scoping). **None of those are results.** The run may contradict them; if
it does, the run is published and the difference is reported, as version 1
did.

## The schema pass this is written against

`archives/tec-register/schema-report.json`, SHA-256
`be060a7c671887010b3ad93c2d57f2c3caff0b01ed9dbe1dbbc6f91aac39b211`,
committed at `3f374ba`. It is cited for three facts. **First**, the
register does **not** print the words "Gate 1" and "Gate 2" in that
column: across the whole archive it prints only `1`, `2` and blank, and in
the copy of 2026-09-15 it prints `1` on 756 rows, `2` on 95 rows and blank
on 1,349. **Second**, only four copies in the archive carry a non-blank
Gate at all — 2026-05-19, 2026-08-22, 2026-08-25 and 2026-09-15 — with the
count of `2` reading 4, 83, 85 and 95 and the blanks falling from 1,650 to
1,349. **Third**, version 1's status vocabulary is unchanged by the
extension, so version 1's check C1 passes against this report as it did
against the one it was written for (`ce3c61d7…`, recoverable at `419fde5`).

## Reading rules added by this version

**R8 — the Gate cell.** The `Gate` column as printed, with runs of
whitespace collapsed. Nothing is inferred from it beyond the mapping in R9,
and blanks are blanks.

**R9 — the tier, and the one interpretation made here.** The register
prints `1` and `2`; NESO's pinned definition names "Gate 1" and "Gate 2".
This declaration reads a cell of `1` as Gate 1 and a cell of `2` as Gate 2,
and **states in the published page that the register does not spell this
out and that the mapping is an interpretation**. Any other non-blank value
is reported under its printed spelling and is not mapped to a tier.

**R10 — the blank is not interpreted.** NESO's pinned definition defines
the two gates and says nothing about a blank cell. A blank Gate is
therefore reported as **blank**, is never called "not assessed", "not yet
gated", "ungated" or anything else, and is never merged into either tier.
The page may report that the blank count falls across the four copies while
the gated counts rise, because that is a count; it may not say what the
blanks mean.

**R11 — shares are two numbers, never one.** Wherever a share is given it
is given twice and labelled: the **row share** (rows in the class over rows
in the denominator) and the **capacity share** (MW over MW). The two are
never averaged, substituted or described with one figure, and where they
happen to be close the page says so rather than letting one stand for both.

## The breakdowns this version adds, declared before they are computed

Exactly six, and no others may be added after the run.

- **G1 — the whole copy by Gate**: rows and MW per printed Gate value,
  under version 1's measure R5.
- **G2 — the selected (overdue) rows by Gate**: rows and MW per printed
  Gate value, with each Gate's row share and capacity share of the overdue
  total, and of that Gate's own total in G1.
- **G3 — the selected rows by Gate and by status as printed**, a
  cross-tab, so a reader can see which statuses sit in the confirmed tier.
- **G4 — every selected Gate 2 row, listed in full as published**: project
  name, connection site, stage, plant type, status, capacity, effective
  date as printed, project id and project number.
- **G5 — repetition inside the selected Gate 2 rows**, both ways: rows
  sharing a project id (version 1's 15-character form) and, separately,
  rows sharing a normalised project name. Both are listed, with the Gate 2
  overdue MW recomputed under each, because a reader who sees one name
  twice will ask, and a shared name is not a shared entry.
- **G6 — what the four gated copies show about each selected Gate 2 row**:
  for each, its Gate cell and its effective date as published in each of
  the four copies that carry a Gate column. This is the only evidence
  available on whether a confirmed date was carried into the tier already
  in the past, or was set and then passed, and its limits are stated with
  it in R12.

## R12 — what the Gate cross-tab can and cannot distinguish

A row in Gate 2 whose date has passed is consistent with at least two
stories: the project was assessed into the confirmed tier while carrying a
date that had already gone or was about to, or it was given a confirmed
date that then passed. **One copy cannot tell them apart.** G6 narrows the
question with the only copies that carry the column, and the page reports
exactly what those four copies show — a date unchanged across them, or
moved, and a Gate cell unchanged, or newly set. Where the four copies do
not settle it, the page says the evidence does not settle it. Nothing here
is a statement about physical delivery, about any project's readiness, or
about whether NESO's assessment was right; version 1's "what the census
never claims" governs this version unchanged.

## Checks this version must pass, or it fails

- **C6** The Gate counts over all rows sum to the copy's 2,200 and equal
  the schema report's `gate` for this copy.
- **C7** The selected rows this version reads are exactly the rows version
  1 committed: the same count, the same row indices, and the same MW total
  to the last penny. A difference stops the run; version 1 is not amended
  by this one.
- **C8** G2's rows and MW sum across Gate values to version 1's committed
  98 rows and 12,034.86 MW.
- **C9** Every selected row's Gate cell appears in the schema report's
  vocabulary for this copy.

## Falsifiers, declared in advance

- **F4** If the copy's Gate column carries any value other than `1`, `2`
  and blank, the cross-tab is not published until that value is named and
  read, and it is never silently folded into a tier.
- **F5** If rows sharing a project id, or rows sharing a project name,
  account for more than a tenth of the overdue Gate 2 MW, the Gate 2 figure
  is published as both readings in the same sentence, never as one number.
- **F6** If fewer than three of the four gated copies are readable, G6 is
  not published and R12's question is reported as unaddressed.

## Outputs

- `evidence/gate.json` — the summary: G1 to G6, the shares, the checks and
  the falsifier verdicts, with this declaration's digest and the digests of
  the copy, the schema report and NESO's pinned definition.
- `evidence/gate-rows.ndjson` — one line per selected Gate 2 row as
  published, with its reading in each of the four gated copies,
  append-only.
- `FINDINGS.md` gains the Gate section; version 1's sections are unchanged.
- `evidence/post-facts.json` gains the slots
  `gb-tec-gate2-capacity-2026-09` and `gb-tec-gate2-overdue-2026-09`.
- `evidence/rule-sources.json` names the test behind every rule above.

## What this version still never claims

Everything version 1 refused, and one more: **that a project in Gate 2 with
a date in the past has failed to deliver, or will not deliver.** The
register records a tier and a date. It does not record delivery, and this
investigation does not infer it.
