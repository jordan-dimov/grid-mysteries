# 021 — Where the dates move: 014's slippage series by plant type and by host transmission owner

**Frozen**: 2026-10-01 with `scripts/freeze`, which witnesses this file by
OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert and
commits it with the proofs, before any grouped megawatt-year figure is
computed. Opened on the sponsor's instruction of 2026-10-01 (etrmbiz
handover note `notes/2026-10-01-grid-mysteries-prompt-014-by-technology-and-area.md`),
which overrides the next-milestone note's default that no new
investigation opens, and says so. The sponsor's seal for the runner is the
digest prefix of this file, given by that instruction; nothing goes
outside the repository until the sponsor has read `FINDINGS.md`.

## Why a new investigation and not an amendment of 014

014's rule reads: *an amended rule applies from the next copy forward and
never restates a row it learned from; a restated history is a new
declaration published beside the old one.* The cut asked for here computes
figures over windows that closed years ago (the calendar years 2014 to
2024 and the headline window 2024-07-19 to 2025-07-22). That is a restated
history, so it lives beside 014 as its own declaration, with its own
evidence, and changes nothing under `investigations/014-gb-connection-slippage/`.
014's version 4 (`DECLARATION-v4.md`, SHA-256
`7d07cbd159ac14d281f23b2399f41b44e8053922465f1b8277778fd4771b7954`,
released 2026-09-24 at commit `289db64`) stands as run; every rule below
that is not restated here is 014's, version 4 first, then what it inherits
from versions 3, 2 and 1.

## The mystery

> When Britain's contracted grid-connection dates move, in aggregate, is
> the movement concentrated in particular technologies or in particular
> transmission areas, or is it spread in proportion to the capacity each
> holds?

A public question put to the sponsor on 2026-10-01 by a capital-side
reader, answered the same day in words from 006 and 017 with this cut
promised. The reading this investigation offers is **how much information
a register date carries by technology and by area**, not who is to blame
for its moving: the date is the one in the project's connection agreement,
moved by agreed variation, and nothing here says why any of them moved
(014's "what this never claims" stands in full).

## Prior exposure (recorded, not hidden)

The author has seen, before writing this file:

1. **014 version 4's published figures in full** (`evidence/v4/`, SHA-256
   `rows.ndjson` `f47d6609…`, `series.json` `e895360a…`,
   `vintage-manifest.json` `4b53edab…`): the headline 2024-07-19 to
   2025-07-22 of +57,823.493 MW-years under version 2's rule (+53,221.271
   determined over 88 undetermined groups; +61,542.867 under content
   matching) over 1,147 matched and 889 dated project-stages weighing
   292,763.70 MW; every calendar-year window's figures (2014 to 2024
   complete, 2025 partial); the four reformed-regime copies (2026-05-19,
   2026-08-22, 2026-08-25, 2026-09-15) and their three increments
   (+18,879.661, −2.806 and +6,249.924 MW-years). **None of them is split by
   any column**: 014's rows carry no per-project field.
2. **006's results** (run 2026-08-26): the share of project-stages whose
   TEC date slipped 24 months or more, by host TO, in two cohorts (works
   slipped against works clean: NGET 18.3 % against 23.8 %, SHET 23.5 %
   against 31.6 %, SPT 24.4 % against 28.4 %), and the cause split of the
   213 slips of 24 months or more: **60 % project-led, 26 % works-led,
   14 % unattributable** (T4). Those are counts of project-stages under
   005's population and reading, not megawatt-years, and are not
   recomputed here; they accompany every slippage figure in `FINDINGS.md`.
3. **017's census** of the copy of 2026-09-15 by plant type as printed,
   compound types kept whole (98 overdue entries; Energy Storage System
   43 rows and 3,706.95 MW; Energy Storage System;PV Array 23 rows). A
   census of one copy, not a movement figure.
4. **The schema pass cited below**, including its count of project-stages
   whose printed plant type or host TO changes between consecutive copies.
   That count is a fact about the columns and is the reason for reading
   rule R1; it is not a movement figure.

**No grouped megawatt-year figure, for any window, any plant type or any
host TO, has been computed in this repository or outside it before this
file was frozen.** The propositions below were written from the exposure
above and judged before the first compute.

## The schema pass this is written against

`archives/tec-register/schema-report.json`, SHA-256
`9ed878f499db8a8c2e248b7c11ea37e75ee1142af140fa3f5b01f36d638f8b37`
(`SCHEMA.md` beside it `683e0f10…`), committed at `a399a35` and regenerated
by `scripts/schema-report tec-register`. It is cited for these facts, each
checked by the runner before any figure (C1):

- `Plant Type` and `HOST TO` are mapped in **every one of the 23 eras**
  from 2014-01-31, under the headers `Plant Type`, `Electricity Connection:
  Plant Type` (2020-07-23), `HOST TO` and `Host TO`
  (`tests/test_tec_register.py::test_every_era_header_row_maps_the_grouping_columns`).
- **Blank cells**: 500 `Plant Type` cells and 294 `HOST TO` cells over
  593,853 rows of 700 copies, 380 and 280 of them in the era 2021-11-26 to
  2024-06-14; none in the four reformed-regime copies. A blank is read as
  a group of its own, printed "(blank)" (R3).
- **Every spelling of `HOST TO`**: `NGET` (every copy), `SHET` (from
  2014-05-26), `SPT` (from 2014-05-09), `OFTO` (from 2020-06-05),
  `OFFSHORE` (2015-03-31 to 2020-05-28), `SHE` (2014-01-31 to 2014-12-05),
  `SPTL` (2014-01-31 to 2014-07-04) and blank (75 copies, 2020-12-15 to
  2025-07-22). No interconnector label is printed in this column
  (`Interconnector` is a plant type, 25 cells).
- **The plant-type vocabulary changed on 2020-06-05**: `CCGT`, `OCGT`,
  `CHP`, `PV Array` and `Oil & AGT`/`Oil + AGT` (used to 2020-05-28) became
  `CCGT (Combined Cycle Gas Turbine)`, `OCGT (Open Cycle Gas Turbine)`,
  `CHP (Combined Heat and Power)`, `PV Array (Photo Voltaic/solar)` and
  `Oil & AGT (Advanced Gas Turbine)` (from 2020-06-05); `Battery Storage`
  (2016-10-28 to 2020-05-28) was followed by `Energy Storage System` (from
  2020-06-05; 12 project-stages carried the one label into the other on
  that copy, the rest had left the register); `HYBRID` (to 2020-05-28)
  became `Hybrid` (2020-06-05 to 2023-08-11), after which its
  project-stages printed compound labels (24 of them `Energy Storage
  System; PV Array…`); `Onshore Wind` is printed in four 2014 copies
  beside `Wind Onshore`; `Energy storage system` once. **The separator of compound
  types changed from `; ` to `;` on 2024-05-31**, with 41 copies between
  2023-05-05 and 2024-05-30 printing both: 488 and 481 project-stages
  "changed" plant type on 2024-05-24 and 2024-05-31 by that spelling alone.
- **Key stability under 014's unit key**: over 582,817 project-stages
  printed in a copy and the copy before it, 2,710 change their printed
  plant type (365 distinct transitions, the separator and the 2020-06-05
  re-spellings first among them) and 270 their printed host TO (21
  transitions: `SHE`→`SHET` 111, `SPTL`→`SPT` 64, `OFFSHORE`→`OFTO` 12,
  blank→a TO 30, 42 moves between `NGET`, `SPT`, `SHET` and the offshore
  label, 5 to blank, and 6 among the 2014 spellings).
  So a key can change for the same project-stage, rarely, and the cut must
  say where it did (R2).

## Inputs and population: 014 version 4's, unchanged

The journalled archive `data/raw/neso/tec-history/` read by 014's reader
with 014's reading rules 1 to 5 and version 2's aliases; **exactly the 700
copies of 014 version 4's `evidence/v4/vintage-manifest.json`** (SHA-256
`4b53edab…`), checked digest by digest before anything is computed (C1).
No copy is fetched by this investigation. Version 2's partial-export rule
(2015-05-08 and 2023-11-28 excluded), the day-month swap test, the regime
break (the old regime to 2025-07-22; the reformed regime from 2026-05-19,
compared copy to copy and never chained to the old), 014's unit
(identity, stage) and its identity rule, version 4's definition of a
determined pairing, the content rule `tec-identity-content-v1`
(`src/grid_mysteries/tec/identity.py`, SHA-256
`a0ee2ac0dcc6919e37061f89a5b0fc1c663cf566cb1a7df3a55f75c761aa0fb8`, F5)
and the movement arithmetic (|MW at the baseline| × years moved, later
positive, gross sides each quantised to 0.001 MW-years) are all 014's and
are not restated. The population of every comparison is 014's: the units
present in both copies **with a parseable date in both** ("dated at both
ends"); a unit whose baseline capacity is blank or zero is counted and
contributes nothing, as in 014.

## The comparisons (R4): these and no others

1. **The headline window**: 014's trailing-year comparison at the last
   old-regime copy, 2024-07-19 to 2025-07-22.
2. **Each complete calendar-year window of the old regime**, as 014
   version 4 lists them: 2014 (2014-01-31 to 2015-01-09) through 2024
   (2024-01-05 to 2025-01-03), eleven windows. The partial 2025 window is
   not cut.
3. **The reformed regime, copy to copy**: 2026-05-19 to 2026-08-22,
   2026-08-22 to 2026-08-25, 2026-08-25 to 2026-09-15, each separately.

Fifteen comparisons, each cut two ways (by plant type, by host TO). No
other comparison, window, trailing year or grouping may be added after a
run; a further cut is a new declaration.

## Reading rules

- **R1, the grouping key as printed, with a spelling table.** A unit's
  plant type and host TO are its row's `Plant Type` and `HOST TO` cells
  as printed, with runs of whitespace collapsed to one space and no
  whitespace around `;`. A compound plant type is **kept whole**, as 017
  did: `Energy Storage System;PV Array (Photo Voltaic/solar)` is one group
  and is never split across its technologies. Within each `;`-separated
  component, and only these, a spelling the schema pass shows the register
  replaced by its own expansion or its own later spelling is read as that
  spelling: `CCGT`→`CCGT (Combined Cycle Gas Turbine)`, `OCGT`→`OCGT (Open
  Cycle Gas Turbine)`, `CHP`→`CHP (Combined Heat and Power)`, `PV
  Array`→`PV Array (Photo Voltaic/solar)`, `Oil & AGT` and `Oil +
  AGT`→`Oil & AGT (Advanced Gas Turbine)`, `HYBRID`→`Hybrid`, `Onshore
  Wind`→`Wind Onshore`, `Energy storage system`→`Energy Storage System`;
  for host TO, `SHE`→`SHET`, `SPTL`→`SPT`, `OFFSHORE`→`OFTO`. **Nothing
  else is unified**: `Battery Storage` is not `Energy Storage System`,
  `Hybrid` is not any compound, `Pump Storage` and `LAES (Liquid Air
  Energy Storage)` are not energy storage for R8. Case is otherwise kept.
- **R2, the key is read at both ends, and a change is a bucket, never a
  reassignment.** For each unit dated at both ends, the key is read in the
  baseline copy and in the current copy under R1. A unit whose two
  readings agree belongs to that group. A unit whose two readings differ
  belongs to the **"key changed"** bucket of that comparison and
  dimension, is never assigned to either reading, and the bucket is
  reported with its size (units, capacity, movement) beside the groups.
  Beside it, the number of units whose keys differ *as printed* but agree
  under R1's table is reported as **"unified by the spelling table"**, so
  that the table's effect is visible.
- **R3, blank is a group.** A blank key is the group "(blank)".
- **R5, what every group reports**, for each comparison and dimension:
  the net, later and earlier movement in MW-years under version 2's rule
  and under content matching; the **determined** part (movement over
  units of project groups whose pairing version 4's definition
  determines, identical under both rules, C3) and the **undetermined**
  part under each rule, so that no group figure is printed without 014's
  split; the units dated at both ends and, of those, the counts moved
  later, earlier and unchanged; the group's units in the baseline copy
  and its matched units (under version 2's rule); the capacity at both
  ends, |MW| in the baseline copy summed over the dated units (the weight
  014 uses) and |MW| in the current copy summed over the same units; its
  **share of net movement** (its net under version 2's rule over the
  comparison's), its **share of the determined part**, its **share of
  dated capacity** (its baseline capacity over the comparison's
  `weighted_mw`), and the **concentration reading**, share of net minus
  share of capacity, in percentage points. Shares are over every bucket
  of the comparison, "key changed" and "(blank)" included, so they sum
  to the whole.
- **R6, rounding.** A group's gross sides are each quantised to 0.001
  MW-years and its net is their sum, as 014 quantises a comparison; the
  determined part the same way, and the undetermined part under a rule is
  that rule's group net minus the determined part. The sum of the groups'
  printed nets can differ from the comparison's own printed net by
  rounding; that residual is reported per comparison and dimension, and
  is at most 0.001 MW-years per bucket (C4). Counts and capacities sum
  exactly. Shares are quantised to 0.1 percentage points.
- **R7, the thin-population rule, inherited from F2.** F2 reads: matched
  units fewer than half of the baseline's units. Applied to each group on
  its own population: a group whose matched units are fewer than half of
  its units in the baseline copy is marked **thin**, its figures are
  published, not suppressed, and `FINDINGS.md` names every thin group.
  The number of dated project-stages is printed beside every group; P-B
  names its own threshold.
- **R8, the two storage readings.** Because compound types are kept
  whole, "energy storage" has two readings, both reported for every
  comparison: **storage alone**, the group whose key is exactly `Energy
  Storage System` (and, in windows before 2020-06-05, the group `Battery
  Storage`, reported as its own group and named); and **storage
  including compounds**, every group whose key has `Energy Storage
  System` (or `Battery Storage`) among its `;`-separated components. Each
  reading's share of net movement and share of dated capacity is
  reported; "key changed" units are in neither.
- **R9, shares of a small net are not read.** Where a comparison's net
  under version 2's rule is within ±1,000 MW-years, its group shares are
  computed and published but marked "not read", and no proposition is
  judged on them. The reformed-regime link 2026-08-22 to 2026-08-25
  (−2.806 MW-years) is expected to fall here.

## Checks the runner makes before and after computing

- **C1** The usable copies are exactly 014 version 4's manifest, digest
  by digest; the schema report on disk hashes to the digest above.
- **C2** For every comparison, the net under version 2's rule, the net
  under content matching, the determined part and the undetermined group
  count equal 014 version 4's committed figures for that comparison
  **exactly**, as strings; the comparison's `dated_both` and
  `weighted_mw` likewise. The cut is of the published series or it is
  not run.
- **C3** For every group, the determined part is identical under the two
  rules (version 4's F4, per group).
- **C4** Over every comparison and dimension, counts and capacities sum
  to the comparison's; printed nets sum to the comparison's within 0.001
  per bucket.
- **C5** The content rule's file hashes to the digest above (014's F5).

A failed check refuses the run and is recorded in `AMENDMENTS.md` before
any rerun; nothing is written.

## Propositions, judged before the first compute

Each is judged on the headline window, under version 2's rule (the
published headline figure), with the same reading on the determined part
reported beside it; where the two readings disagree the disagreement is
reported, not resolved.

- **P-A (no single area dominates beyond its size).** No single host TO
  carries more than **two thirds** of the headline window's net movement
  while holding **less than half** of its dated capacity. *Falsified* if
  any host TO group (not the "key changed" or "(blank)" bucket) has a
  share of net above 66.7 % and a share of dated capacity below 50.0 %.
- **P-B (every sizeable area moves later).** In the headline window the
  net movement is positive in every host TO group with at least
  **thirty** dated project-stages. *Falsified* by any such group whose
  net under version 2's rule is zero or negative.
- **P-C (storage moves in proportion to its size).** Energy storage,
  including compounds (R8's second reading), carries a share of net
  movement within **fifteen percentage points** of its share of dated
  capacity in the headline window. *Falsified* if the two shares differ
  by more than 15.0 points in either direction. The storage-alone reading
  is reported beside it and does not decide P-C.

Each proposition is decided by its instance on the first compute: holds,
fails (the group named), or **undecided** if the headline window falls
under R9 or every group it names is thin under R7.

## Falsifiers of the instrument

- **F-G1** C1 or C2 fails: this is not a cut of 014's series; the run
  refuses.
- **F-G2** C3 fails: the determined part depends on the rule in some
  group; the definition inherited from 014 does not carry to groups; the
  run refuses.
- **F-G3** A committed row of `evidence/groups.ndjson` or
  `evidence/comparisons.ndjson` would change on recompute under the same
  rule version: the run refuses. There is no `--amend`; a changed figure
  is a new declaration beside this one, and a row is recorded once per
  rule version (the kill test of 2026-09-25, `bill/KILL-TEST.md`).
- **F-G4** In any comparison and dimension the "key changed" bucket holds
  more than **a fifth** of the comparison's dated capacity: the grouping
  key is not stable enough over that window to read, and the cut for that
  comparison and dimension is published marked **unfit**. The 2020 window
  (2020-01-02 to 2021-01-07), which spans the 2020-06-05 re-labelling, is
  where this is expected if anywhere.

## Outputs

- `evidence/comparisons.ndjson`: one line per comparison and dimension,
  append-only, carrying `rule_version` (this file's SHA-256 prefix), the
  comparison's 014 figures as checked by C2, the "key changed" and
  "unified by the spelling table" counts, the rounding residual, R9's
  mark and F-G4's mark.
- `evidence/groups.ndjson`: one line per comparison, dimension and group
  (buckets included), append-only, carrying `rule_version` and everything
  R5 lists.
- `evidence/summary.json` (rewritten each run): this declaration's digest
  and timestamps, the schema report's digest, the seal, the run date, the
  propositions with their instances, the storage readings per comparison,
  the thin groups and the unfit comparisons.
- `evidence/run-log.json`; `evidence/rule-sources.json` naming the test
  behind every rule and check above (`scripts/check-rules`).
- `FINDINGS.md`, a pure function of the evidence (`run.py --phase
  render`), every figure from the committed rows, the 006 cause split in
  the same breath as every slippage figure, and no megawatt-year figure
  without its determined and undetermined split.

## The record

This investigation's record is git plus external witnesses, as for every
forensic investigation from 012 onward: this file with its proofs, the
committed evidence with `rule_version` on every row, and `scripts/check`.
No row is proposed to a Morpholog database by this declaration; a figure
the sponsor adopts outside the repository is cited by its row's
`rule_version` and the commit that holds it.

## What this never claims

Everything 014 never claims, and in addition: that a technology or an
area is "worse" at anything. A group's share of net movement above its
share of capacity says that the register's dates for that group carried
less information over that window, under this reading, than the dates of
the rest; 006 found three fifths of large slips project-led, a quarter
works-led and the remainder unattributable, and nothing here revises that
split or attributes any group's movement to a cause. A compound type is a
register label, not a statement about which technology moved. Nothing
here is a forecast of any project's energisation.
