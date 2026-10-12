# 023 — Did projects that changed hands slip more? Declaration

**Written 2026-10-12 on the sponsor's handover of that day (etrmbiz
`notes/2026-10-12-grid-mysteries-drift-paper-handover.md`, piece 2: "a new
investigation that crosses 019's ownership history with the slippage
results; its rule is declared first, and its findings are reported as an
association, never a cause").** Frozen by `scripts/freeze` after the
schema pass (`archives/023-holder-change-inputs/`) and before any date
movement is read for this question. Changes after the freeze are
amendments.

## The question

> Within the same window, did the connection dates of projects whose
> holder changed — a different registered company at the window's end
> than at its start — move differently from those of projects whose
> holder kept its printed name?

It speaks to a thesis put to the sponsor (sites concentrating into funds
and state money). The answer is an **association** in the register's own
data; it never says that a sale moved a date, or that a moved date
prompted a sale.

## Why 014's figures cannot simply be cut

014's identity is the normalised (project name, customer name, connection
site) triple. A project whose customer name changes between two copies is,
to 014, one project leaving and another arriving; it is never in 014's
matched comparison. The cross must therefore be rebuilt on the register's
`Project ID`, which survives a change of customer.

## Prior exposure, stated

- 019's figures (`877682f7…`, amendments 1 and 2, rule version
  `019-r2-v2`): 864 renames, 773 transfers, 95 not determinable among the
  name changes on current Project IDs; the rename lag median (122 days);
  the admissions and their counts. 014 version 4's headline and chain
  figures (2024-07-19 to 2025-07-22 determined +53,221.271 MW-years over
  88 groups, and its other published figures); 021's headline outcome
  (P-A and P-B hold, P-C fails by 0.4 points).
- **The schema pass of this investigation** (`archives/023-holder-change-inputs/`),
  which read no date movement: the columns, blanks and key duplicates of
  each end copy; that the register's Project IDs changed scheme on
  2022-08-24 (ids beginning `a03` until then, `a0l` from then; none spans
  the change), so a window must lie after it; the Project IDs at both ends
  of each window and how many are still printed on 2026-09-29; and the
  exposure counts below.
- In the schema pass the author found that 019's figure 3 field
  `last_copy_with_earlier` holds the **first** copy of the earlier name's
  run (its `name_changes` reads the run's `t_public`). 019 is not changed by
  this declaration; this investigation rebuilds every bracket from 019's
  history runs and uses 019's rule on the end names (E1).
- **No stage's date movement has been computed on this cross, in any
  window, and no comparison between exposure groups has been seen.**

Exposure counts from the schema pass, Project IDs printed at both ends and
still printed on 2026-09-29 (E1's classes):

| window | ends | in scope | transfer | rename | same name | not determinable |
|---|---|---|---|---|---|---|
| headline | 2024-07-19 → 2025-07-22 | 1,630 | 142 | 181 | 1,294 | 13 |
| 2023 | 2023-01-06 → 2024-01-05 | 842 | 37 | 38 | 766 | 1 |
| 2024 | 2024-01-05 → 2025-01-03 | 1,368 | 83 | 86 | 1,195 | 4 |

## Windows, declared now

- **Primary: the headline window**, 014 version 4's trailing year, kept
  copies 2024-07-19 (`2ba43d88…`) and 2025-07-22 (`d8754702…`).
- **Replications: calendar 2023 and calendar 2024**, 014's annual windows
  of the `a0l` era (2023-01-06 → 2024-01-05, 2024-01-05 → 2025-01-03),
  each reported on its own. They overlap the headline window (2024) and
  each other at a shared end copy; they are not independent samples and
  are never pooled.
- 005's 2014 to 2025 run is **out**: before 2021-11-26 the register prints
  no Project ID, and before 2022-08-24 no id reaches the `a0l` era, so a
  change of customer cannot be followed there. 2022 is out for the same
  reason (no Project ID at both ends of 2022-01-05 → 2023-01-06).

Copies are read as 014 version 4 reads them: kept copies only (the
partial-export rule), dates by `parse_date` with the day-month swap where
014's swap test flagged the copy (none of the five end copies is flagged).

## Population, declared now

For each window, the **scope** is the Project IDs printed at both end
copies **and** in the 2026-09-29 copy (019's scope; 019's history and
links cover names on those ids). Ids at both ends that left the register
by 2026-09-29 are counted and their stages' movements reported as a
described group of their own, outside every contrast.

A **stage** is a row keyed (Project ID, `Stage` normalised by
`normalise_stage`) that is unique in each end copy and present in both,
with `MW Increase / Decrease` greater than zero and `Project Status` not
`Built` in the baseline copy, and an effective date that parses in both
copies. Rows failing each condition are counted by condition.

## Exposure, declared now

- **E1.** For each id in scope, the customer name printed at each end
  (`queue_ownership.printed_name`), and 019's R4 as amended
  (`queue_ownership.classify_change`) applied to that pair, with 019's
  copy-date rule resolving a name admitted with several holders at the end
  that prints it: **transfer** (both names resolve, different companies),
  **rename** (same company, or the previous-name routes), **same name**
  (identical printed name at both ends), **not determinable**, and
  **several names** (an id printing more than one customer name at an
  end). Links are 019's `019-r2-v2` lines of run 2026-09-30 with 019's
  admissions applied; profiles are 019's pinned ones. Nothing is fetched.
- A *transfer* is a different registered company. It includes moves
  between companies of one group (special-purpose vehicles); the label
  says nothing about ownership above the company.
- **Changes inside the window** (019's history runs between the end copies)
  are counted per id; an id with the same name at both ends after a change
  in between stays *same name* and is counted as such.

## The measure, declared now

Per stage: **days moved** = effective date at the current end minus at the
baseline; **months** = days ÷ 30.4375 (one decimal); **MW-years** =
baseline MW × days ÷ 365.25; **direction**: later, unchanged or earlier.
Per id: **net MW-years**, the sum over its stages. Distributions, never
averages alone.

## What is computed, declared now

For each window, for each exposure class: ids, stages, MW; the stages'
months (n, min, p25, median, p75, max, `energisation.quantiles`); the
shares later, unchanged and earlier with 95 % Wilson intervals; the ids'
net MW-years (quantiles and total).

**The contrast** is *transfer* against *same name*. Secondary contrasts,
reported beside and never as the headline: *rename* against *same name*;
*transfer or rename* against *same name*.

- **Crude**: the difference in the share of stages moved later, and the
  difference in median months (transfer minus same name).
- **Standardised**: strata are the baseline `Project Status` crossed with
  the plant family of 020 version 1 (`energisation_v1.family` on the
  baseline `Plant Type`). The standardised difference in the share moved
  later is Σ_s w_s (p_transfer,s − p_same,s) over strata holding stages of
  both groups, with w_s the transfer group's share of its stages in those
  strata; the share of transfer-group stages in strata with no same-name
  stage is reported beside. Every stratum's n and shares are tabled.
- **Intervals**: 95 % percentile bootstrap, resampling **ids** (with all
  their stages) with replacement within each group, 10,000 resamples,
  `random.Random(20261012)`, drawn in the order windows and contrasts are
  listed here, the same resamples serving the crude and standardised
  differences of one contrast.

## Checks each run must pass, or it stops

- **C1** Every end copy hashes to its journal digest, as in the schema
  report.
- **C2** 019's `name-history.json`, `names.json` and `results.json` hash to
  the digests in the schema report; its links and admissions are the ones
  019's compute last read (the run's digests are written into the results).
- **C3** Every id in scope is in exactly one exposure class; the classes
  sum to the scope.
- **C4** The per-stage lines (`evidence/stages.ndjson`, held) are a pure
  function of the inputs; a committed line that would change on recompute
  stops the run.

## Falsifiers, declared in advance

- **F1** Fewer than 30 *transfer* ids with at least one measured stage in
  the primary window: the contrast is **not determinable**; the counts are
  the outcome.
- **F2** The crude and standardised differences in the share moved later
  have opposite signs, or the standardised interval contains zero while
  the crude one does not: the raw difference is reported as **explained by
  the mix of status and technology**, and no direction is stated.
- **F3** If neither replication window's standardised difference has the
  primary window's sign, the association is reported as **not stable
  across windows**.
- **F4** If more than 10 % of the ids in scope print several names at an
  end, or more than 5 % of rows keyed at both ends fall in duplicate keys,
  the identity is unfit and the run stops.

## What this never claims

- That a change of holder caused a date to move, or the reverse. Sales
  cluster around consents and Gate 2; the strata are a partial answer to
  that confound, not a full one.
- Anything about the projects that left the register by 2026-09-29.
- Why any date moved. 006's cause split (60 % project-led, 26 % works-led,
  14 % unattributable) is a population figure and is not attributed to
  either group here.
- Anything about who ultimately owns a company.

## Order of work

1. This file is frozen. 2. Compute under its seal (archive and 019's held
evidence only; no network). 3. Findings to the sponsor before anything
public. The per-stage lines, the per-id exposure list and the results
renderings name companies and projects from 019's held evidence and are
held out of the public repository with 019's (ignored by git) until the
sponsor says; the schema report, this file, the code and its tests are
committed.

## Outputs

`evidence/stages.ndjson`, `evidence/exposure.ndjson`, `evidence/results.json`,
`RESULTS.md` (held); `evidence/rule-sources.json`, `evidence/run-log.json`
(committed).
