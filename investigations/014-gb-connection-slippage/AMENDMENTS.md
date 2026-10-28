# 014 — amendments and dated findings

`DECLARATION.md` is frozen (SHA-256 `e4aba4c9…`, witnessed 2026-09-15 20:12
UTC). Everything learned after it is written here, dated. An amended rule
applies from the next copy forward and never restates a row it learned
from; a restated history is a new declaration published beside this one.

## Finding, not amendment — 2026-09-16: the three July 2020 copies were excluded for a reader gap, not a NESO omission

The declaration's prior-exposure section says four copies "lack an identity
column" (2020-07-09, 2020-07-16, 2020-07-23, 2021-06-22), and the first run
excluded the three July 2020 copies under reading rule 2. The archive schema
report (`archives/tec-register/SCHEMA.md`, introduced 2026-09-16) shows the
cause: those three copies carry the customer column under the bare header
**"Customer"**, which the reader's alias table did not map. The column was
present; the reader was not. (2021-06-22 is different: its header row never
parses.) The shared reader now maps "Customer" and "Electricity Connection:
Plant Type" (the 2020-07-23 spelling).

**Effect on the sealed series: none applied.** The committed
`evidence/series.json` was computed with the three copies excluded, exactly
as the declaration's rule read them at the time, and `run.py` refuses to
change a committed row without `--amend`. `run.py --phase check` (added
2026-09-16) measures the effect: with the three copies included, **420 of
the 697 committed rows would change**, because the chained total
(`cumulative_mw_years_net`) carries every increment forward from 2020-07-30
and the trailing-year rows whose baseline falls in the affected window
move too; the annual windows keep their endpoints, and the headline row's
year-on-year figure is unaffected. Whether to recompute under `--amend`
(a restated chain, recorded as such) or to leave the first publication as
run is the sponsor's decision, recorded here when made.

## Finding — 2026-09-16: two copies look like partial exports and are inside the series

The schema report flags **2015-05-08** (row count fell 46 % against the
previous copy) and **2023-11-28** (fell 52 %). Both are in the series as
ordinary copies; the declaration has no partial-export rule. F1 fired on
both links, which is the instrument doing its job after the fact. The
2023-11-28 copy is also the one in which Clash Gour was absent for one copy
in the certificate exemplar. A rule excluding copies whose row count falls
by more than a fifth against the previous copy, or reporting them as
suspect, belongs in the next declaration of this series and in the
certificate template, not in this one by amendment.

## Release seal — 2026-09-16 (version 2)

The sponsor's reconciliation review of the version 2 evidence found it
reconciled (headline arithmetic, the chained total's move from version 1,
every proposition, flag and gap traceable to a field) and asked for three
presentation changes, none touching evidence and none requiring a rerun:
a "dated at both ends" column so the movement counts close on the
population that can move; the headline sentence attributing movement to
those dated project-stages and scoping the chained total to the old regime,
with the year-window sum beside it; and a plain reason for the 32 copies
the reader cannot parse. Applied in the renderer, re-rendered, and sealed
for release by the sponsor's instruction of 2026-09-16. The page is served
at the unlisted Render hostname only and is not announced until the sponsor
says so.

## F4 fired — 2026-09-23 (version 3, first compute): the definition is wrong across more than one copy

The first version 3 compute (`run.py --version 3 --seal 435988c7 --phase
compute`, run date 2026-09-23) refused, as the declaration requires:
F4, *"On any comparison, the two rules give different movements for a group
whose pairing is determined: the definition is wrong."* Nothing was written
to `evidence/v3/`. The cause, recorded here before any rerun:

**The definition judges determinacy only at the two copies compared; the
content rule, as declared ("units are carried from copy to copy within a
segment"), follows rows through every copy in between.** A group can print
the same single stage label at both ends and be restructured in between.
Barry Power Station (Centrica Barry Ltd, Aberthaw 132 kV) printed one row,
-136 MW for 2016-04-01, on 2015-04-13; by 2016-03-07 a second row, +235 MW
for 2018-04-01, under the same blank stage; by 2016-04-12 only the +235 MW
row. At the two ends the group is determined, so version 2's rule pairs the
-136 MW reduction with the +235 MW row (271.8 MW-years); content matching
follows the rows and pairs nothing (0). Measured over every comparison
(674 trailing-year, 696 increments, 13 windows): **27 comparisons fail** (26
trailing-year, 1 window), in four groups (Barry Power Station, Bramford
Tertiary, Corby, Thorpe Marsh), 23,152.735 MW-years of disagreement in
absolute terms. No increment fails: consecutive copies have nothing in
between. The headline comparison (2024-07-19 to 2025-07-22) does not fail.

**An implementation defect, fixed, not a rule change.** The first diagnosis
also showed one increment failing (Windy Standard III, 2024-10-22): both
rules gave 131.754 MW-years, but the check compared per-group Decimal sums
accumulated in different orders, which differ beyond the 28th significant
digit. The check now sums each group's values in sorted order.

**The figures already seen, before any decision.** Two ways to restate the
definition remove every failure; either is a new declaration, since this
one is frozen and never restated by amendment:

- *(a) Path-aware undetermined set, content rule carried as declared*: a
  group is also undetermined when its labels change or repeat in any kept
  copy from the baseline to the current one. Headline: determined
  +53,221.271 over 88 groups; +4,602.222 under version 2's rule, +8,321.596
  under content matching (totals +57,823.493 and +61,542.867 unchanged).
- *(b) Definition as frozen, content rule applied between the two copies
  compared* (the same code and digest, run on the two copies alone, as
  version 2's rule compares them): headline determined +57,400.291 over 54
  groups; +423.202 under version 2's rule, +2,531.432 under content
  matching (content total +59,931.723 instead of +61,542.867).

Under both, the chain is unchanged (its increments are consecutive):
determined +392,125.567, +532,780.315 under version 2's rule and
+534,180.588 under content matching. The headline's determined part,
quantised as version 2 quantises a net (each gross side to 0.001), is
+57,400.291; the +57,400.290 in version 3's prior-exposure section was the
total quantised once. The choice between (a), (b) or something else is the
sponsor's; version 3 stays frozen and unrun.

## Page checked against version 4 before release, 2026-09-24 (presentation only; no rule, row or figure changed)

The preview rendered on 2026-09-23 was read against `DECLARATION-v4.md` and
what it inherits from versions 3, 2 and 1, line by line, before the
release seal. The headline sentence, the chained total with its two
undetermined shares, the year windows, the trailing-year table and P1/P2
match. Five things did not, all in the renderer; the sealed declarations
and the evidence under `evidence/v4/` are untouched:

1. **Increments without their split.** Version 4 declares the determined
   part, the group count and each rule's figure for every increment of the
   chain; the table showed version 2's net alone. It now shows all four for
   each increment, beside the chained columns.
2. **F2 on copy-to-copy rows.** The reformed segment's table is copy to
   copy, but carried an "F2 thin population" column; F2 is defined on
   trailing-year comparisons only, and F1, which is defined on consecutive
   copies, was not shown there. It now carries F1 and not F2. Neither
   fired on the reformed segment, so no flag changes.
3. **F1 after its figures.** Version 1: an F1 link "is listed as such on the
   page before its figures". The F1 column now precedes the figures in both
   copy-to-copy tables.
4. **The coverage count.** The introduction said "700 copies … 31 Jan 2014 to
   22 Jul 2025, plus 4 copies since 19 May 2026": 700 is every usable copy,
   so the 4 reformed copies were counted twice and the 2 copies excluded by
   the partial-export rule as used. The old-regime series uses 694. The
   same sentence was on version 2's page served since 2026-09-16, so it is
   listed in `corrections.json`, which the page's Corrections section now
   reads (version 2's record page is not affected).
5. **Wording.** "Page generated" gave the compute date, which is not the
   date the page is rendered at release; it now says "Figures computed".
   The record page names `evidence/v4/rows.ndjson` as where the rows are
   (it said `series.json`, which since version 2 holds only the summary).
   Dash punctuation in the propositions is replaced.

Considered and left: the tables give each comparison's determined part and
each rule's total, not the undetermined part as a column. The declaration
defines the undetermined part as that difference, the headline states it
in words, and the evidence carries it to 0.001 for every comparison;
adding two more columns to fifteen was judged to cost more reading than it
returns. Tests: `tests/test_connection_slippage_page.py`, five added.

## Finding, not amendment — 2026-10-01: the series cut by plant type and host TO lives in 021

A public question of 2026-10-01 asked whether the slippage is concentrated
in particular technologies or regions. Cutting the series by `Plant Type`
and `HOST TO` computes figures over windows that closed years ago, which
this file's rule forbids as an amendment (an amended rule applies from the
next copy forward), so it is a separate declaration beside this one:
`investigations/021-slippage-by-technology-and-area/DECLARATION.md`
(SHA-256 `76ad7dc3…`, frozen 2026-10-01), with the same population checked
digest by digest against `evidence/v4/vintage-manifest.json` and every
comparison checked against this series' committed figures before any group
figure was written. Nothing under this directory changed. The schema pass
behind it (`archives/tec-register/`, report `9ed878f4…`) added the two
columns' vocabularies, blank rates and key stability to the archive report;
version 4's `series.json` cites the earlier report (`be060a7c…`) it was
computed against, which is unchanged in git.

## Finding, not amendment — 2026-10-15: the 301-day hole is closed in the archive, and version 4 cannot be recomputed over it under its own rules

NESO answered 005's EIR request (FOI/26/216, letter of 13 October 2026) with
83 TEC Register copies dated 2025-07-25 to 2026-05-15, journalled on
2026-10-15 under the source label `neso-foi-email`
(`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-216.md`).
No gap longer than 7 days remains between 2025-07-22 and 2026-05-19. The
archive schema report was regenerated over 783 usable copies: the `Gate`
column's era begins 2025-11-21 (53 copies to 2026-09-15), the previous era
runs 2024-06-18 to 2025-11-18 (97 copies).

**What the declaration expected.** Version 1 says the answered request's
copies "enter the archive as new journal rows and the series is recomputed
under this declaration; they fall inside the regime break below, so they
cannot change any row of the old-regime series." The regime break is a
date (copies dated 2025-12-01 or later), not the hole: 36 of the copies
(2025-07-25 to 2025-11-28) belong to the old regime and 47 (2025-12-05 to
2026-05-15) to the reformed one.

**What `run.py --seal 7d07cbd1 --phase check` found on 2026-10-15**, over
835 journal rows, 815 distinct dates, 783 usable copies:

    refusing: the version 2 side of 4 row(s) differs from evidence/v2
    (2026-05-19, 2026-08-22, 2026-08-25, 2026-09-15)

The four reformed-regime rows restate, because the segment's first copy is
now 2025-12-05 and 2026-05-19 gains an increment and a chain position.
Version 4's rows carry version 2's row byte for byte
(`require_v2_side_unchanged`), and version 2 is closed, so **`--amend` does
not reach this refusal**: the series with the hole filled is a restated
history, and under this file's own rule "a restated history is a new
declaration published beside this one". No evidence was written. By the
declaration's own reasoning the old-regime rows to 2025-07-22 do not change
(each copy's comparisons look backward); the 36 old-regime copies would
append rows and extend the partial 2025 window to 2025-11-28; P2's "first
copy of the reformed regime" would move from 2026-05-19 to 2025-12-05 and
its 365-day falsifier date with it. None of that is computed here.

**Effect on the published series: none.** `evidence/v4/`, `SERIES.md` and
the site page stand as run on 2026-09-23. The "Gaps" section's statement
that no copy is held between 2025-07-22 and 2026-05-19 describes the
archive the series was computed from, not the archive now; a version 5
beside this one, with the sponsor's seal, is what recomputes. Whether to
open it is the sponsor's decision, recorded here when made.

## Finding, not amendment — 2026-10-28: the 2025 and 2026 gaps are closed, and the reader drops later stage rows from 2020-06 to 2024-05

The archive gained 51 publication dates from NESO's EIR response FOI/26/245
(2025-01-03 to 2025-07-18, 2026-08-14 to 2026-09-15) and 25 from NESO's
published response FOI-26-226 (2023-06-30, 2026-05-22 to 2026-08-11), plus
further copies of held dates that no reader chooses
(`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-245.md`).
The gaps this page names of 2025-04-01 to 2025-07-01 (91 days) and
2026-05-19 to 2026-08-22 (95 days) are closed in the archive.

**What `run.py --seal 7d07cbd1 --phase check` found on 2026-10-28**, over
1,064 journal rows, 891 distinct dates, 859 usable copies:

    refusing: the version 2 side of 10 row(s) differs from evidence/v2
    (2023-07-04, 2024-07-02, 2025-03-21, 2025-04-01, 2025-07-01)

Old-regime rows now restate as well as reformed ones, because new copies
fall inside old-regime comparison windows. This was not traced row by row.
As on 2026-10-15, `--amend` does not reach the refusal, and a version 5
beside this one is what recomputes. No evidence was written. A dated correction stating the
archive fact was added to `corrections.json` and `SERIES.md` and
`site/connection-slippage/index.html` were re-rendered. Neither is
deployed; no figure on the page changes.

**A reader defect, found by the regenerated schema pass.** From 2020-06-18
to 2024-05-30 the published register prints a project's name on its first
stage row only. `read_vintage` keeps only rows that print a name, so in 346
copies 40,107 rows were never read, 27 to 183 a copy. Most are later stages of
the named project above them; some carry their own Project ID. From
2024-05-31 every row prints its name. Version 4's series, released on 2026-09-24, reads
first-stage rows only across those four years. Its figures are what the
declared reader computes, and **whether they are what the register
printed is now an open question**, not checked here. A proposed correction for the
page, for the sponsor to word and release: *"From June 2020 to May 2024 the
register printed a project's name on its first stage row only, and this
series read only rows that print a name; later stages of multi-stage
projects in those copies are not in it. A version 5 would read them."*
It is not added to `corrections.json`; publishing a correction to a released
page is the sponsor's seal.

**Released the same day on the sponsor's instruction** (28/10/2026, before any
recompute), in the sponsor's wording, as a preamble correction in
`corrections.json`. The headline was checked before it was claimed. Version 2's rule keys
each copy on its own (`cs.entries`), the determined figure compares the two end
copies only (`analysis.undetermined`), and the kept-copy flags read the copy
immediately before. The window's copies run from 2024-07-16 to 2025-07-22 (54 in the
window), all after 2024-05-30, the last copy that drops rows. **+57,823 (version
2's rule) and +53,221 (determined) are unaffected.** Content matching carries row
identity from the regime's first copy, so its +61,543, the cumulative series
and the year-by-year rows for 2020 to 2024 may change; the correction says so.
