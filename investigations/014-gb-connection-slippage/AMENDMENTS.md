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
