# 005 — amendments and working notes

`DECLARATION.md` is frozen (commit `4101286`, digest `ee48de78…`). Everything
learned after it is written here, dated, so the difference between what was
declared and what was found stays visible.

## Amendment 1 — 2026-08-26: the unit is (identity, stage), an implementation contract under the declared identity

**Recorded after a first run, before any result was written up.** The
declaration defines identity as Project ID where present in both vintages,
else the normalised (name, customer, site) triple. It did not say what to
do when one identity has **several rows in one vintage**. From 2023 the
register does exactly that — a project can carry multiple *stage* rows
with different effective dates (134 duplicate triples in the 2023-06-16
vintage, 149 in 2024-06-14, 200 in 2025-07-22; none in 2021–22). Keying
on the triple alone pooled those stages into one timeline and
manufactured "revisions" from stage differences.

Fix: the timeline unit is (identity, register `Stage`); where `Stage` is
absent or not unique, rows sharing an identity are ordered by effective
date and MW. This is an implementation contract under the declared unit,
not a new rule; splits and merges are still not repaired.

Effect on the pre-declared results (before → after), preserved in
`evidence/tec-slippage-summary-PRE-AMENDMENT-1.json` and
`evidence/tec-slippage-summary.json`:

| | before | after |
|---|---|---|
| identities | 6,961 | 7,778 |
| population (span ≥ 2 y, first seen < 2025, slip observed) | 1,085 | 1,161 |
| Q1 IQR (months) | 23 | 17 |
| Q1 share slipped ≥ 24 m | 24.6 % | 21.4 % |
| Q1 share < 6 m | 60.3 % | 63.5 % |
| Q2 first-status ratio (Awaiting Consents vs Under Construction) | 3.44 | 3.40 |
| Q2 lead-time ratio (3–5 y vs > 5 y) | 2.76 | 2.87 |
| Q3 largest gap to pooled | +14.7 pp | +14.4 pp |
| projects with ≥ 10 revisions | 138 | 2 |

The verdicts on Q1, Q2 and Q3 are the same before and after; the fix
changes magnitudes, not conclusions, and removes an implausible tail.

## Finding, not amendment — 2026-08-26: Project ID is not a stable key (F-2 fires)

The `Project ID` column (present from 2021-11-26) is a Salesforce record
id whose format changed twice: `a030Y…` (2021–2022) → `a0l4L…` (2023) →
`a0l8e…` (2024–2025). Between the 2022-06-14 and 2023-06-16 vintages
**zero** IDs are shared; likewise 2023 → 2024. Within a regime IDs are
stable (2024-06 → 2025-07: 1,629 of 2,081 shared). Consequence: the
declared ID-keyed robustness check returns n = 0 for any span ≥ 2 years
by construction, because no ID regime lasts two years. The triple is the
only cross-era key, and its own churn (renames of customers and projects)
is why 5,498 of 7,778 identities "disappear" — F-3 applies and
disappearance is reported separately from slip throughout.

## Finding, not amendment — 2026-08-26: plant-type vocabulary is not harmonised across eras

Early vintages say "CCGT" and "Battery Storage"; later ones "CCGT
(Combined Cycle Gas Turbine)" and "Energy Storage System". The declared
rule (F-4) permits a one-to-one relabel. It was **not** applied, because
the need was noticed after the plant-type stratification had been read
and applying it then would be result-fitting. It is available for a
pre-declared phase 2.

## Observation — 2026-08-26: the declaration did not enumerate "Q1 and Q2 pass, Q3 fails"

Kill conditions (a)–(d) cover archive failure, Q1 failure, Q2 failure and
all-three-pass. The observed outcome — Q3 missed by 0.6 percentage points
— is none of them. The honest reading is that (d) is **not** triggered and
the snapshot is **not** started on the strength of a near-miss. Recorded
so that the threshold cannot be quietly relaxed; a phase-2 declaration
may set a different bar *before* its data is touched, and must say why.

## Amendment 2 — 2026-09-15: the register was under-read; re-run under 014's reading rules, and Q3 moves from a 0.6-point miss to a 0.03-point pass

**Recorded after investigation 014 (GB Connection Slippage) built a tested
reader for the same archive.** Three defects in this study's runner
(`run.py`, unchanged) were found there: the stage-capacity column
(`MW Increase / Decrease`) was never mapped; effective dates spelled
`YYYY/MM/DD`, `DD-Mon-YY` or as Excel serial numbers were left unparsed and
so read as undated (7,626 slash-form cells, 1,496 serials and a smaller
number of `DD-Mon-YY` cells across the archive); and no test existed for
copies whose date cells carry day and month exchanged (three copies:
2021-01-29, 2021-02-19, 2022-03-11). Two further reading rules 014 declared
also apply: stage numerals are unified (`1.00` is `1`) and copies lacking
an identity column are excluded rather than read with a blank customer
(2020-07-09, 2020-07-16, 2020-07-23). The stage-capacity column plays no
part in 005's metrics; the date and stage rules do.

**What was re-run.** `rerun-2026-09-15.py`: the declared method exactly as
`run.py` runs it (identity triple, (identity, stage) unit of Amendment 1,
regime cutoff, population, Q1–Q3 thresholds in `tec_slippage`), over the
same journalled archive, reading it under 014's rules. Output:
`evidence/tec-slippage-summary-2026-09-15-014-READING-RULES.json`. The
2026-08-26 evidence files are untouched.

| | 2026-08-26 run | under 014's reading rules |
|---|---|---|
| old-regime copies read | 696 | 693 |
| identities | 7,778 | 7,248 |
| population (span ≥ 2 y, first seen < 2025, slip observed) | 1,161 | 1,163 |
| net slip p75 / p90 (months) | 17 / 41 | 22 / 43 |
| Q1 IQR (months) | 17 | 22 |
| Q1 share slipped ≥ 24 m | 21.4 % | 23.4 % |
| Q1 share < 6 m | 63.5 % | 60.2 % |
| Q2 first-status ratio (Awaiting Consents vs Under Construction) | 3.40 | 3.65 |
| Q2 lead-time ratio (3–5 y vs > 5 y) | 2.87 | 2.78 |
| Q3 pooled rate | 21.4 % | 23.4 % |
| Q3 largest gap to pooled (Awaiting Consents) | +14.4 pp | **+15.03 pp** |
| Q3 gap, 3–5-year lead time | +14.4 pp | +14.1 pp |
| projects with ≥ 10 revisions | 2 | 0 |
| **Verdicts Q1 / Q2 / Q3** | pass / pass / **fail** (by 0.6 pp) | pass / pass / **pass** (by 0.03 pp) |

**What this means, narrowly.** Q1 and Q2 hold under both readings, with
the same passing strata in the same direction. Q3 was decided by a
threshold the declaration fixed at 15 percentage points; the 2026-08-26 run
missed it by 0.6 and this run clears it by 0.03. A verdict that flips on
a reading correction and sits three hundredths of a point from its bar is
not evidence that the bar was well placed; it is evidence that the answer
to "is a 14–15-point gap an underwriting input" was always a commercial
judgement the threshold could only pretend to settle (the 2026-08-26
observation above said as much).

**Consequence under the declaration.** Kill condition (d), "all three
pass", is now met on the corrected reading, and (d) says the snapshot
instrument starts and phase 2 is declared separately. **Nothing is started
by this amendment.** The study was closed by sponsor decision on
2026-08-26; whether the corrected verdict reopens it is that decision's to
revisit, and the twice-weekly snapshot (d) asked for is in any case now
being kept by investigation 014's runner and the capture job that follows
it. The published figures in `RESULTS.md` and Publication Pack 004 stand as
the 2026-08-26 reading, with this amendment beside them; they are not
rewritten.

## Correction to Amendment 2 — 2026-09-16

Amendment 2 says three copies (2020-07-09, 2020-07-16, 2020-07-23) were
excluded because they lack an identity column. The archive schema report
(`archives/tec-register/SCHEMA.md`) shows they carry the customer column
under the header "Customer", which neither this study's runner nor 014's
reader mapped at the time. The exclusion in the 2026-09-15 re-run stands as
run and its figures are not changed; the stated cause was wrong and is
corrected here. The reader now maps the header.
