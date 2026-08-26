# Investigation 005 — connection-date credibility: is GB connection-date slippage already measurable from the TEC register's history?

**Declared 2026-08-26, before any historical TEC register vintage was
opened. Frozen on commit; never edited. Results go in `RESULTS.md`;
amendments, if any, in `AMENDMENTS.md` with dates.**

## The commercial question this serves

> When a GB project says it has a connection in year X, how much should an
> investor believe X?

F001 established that lenders and acquirers already pay for assessment of
connection positions, and left open whether anyone measures *durability
over time*. This study asks whether the public record already contains
that measurement. It is a **two-day kill experiment**, not a product; it
explicitly does **not** build a "connection credibility score".

## What is known at declaration (used only to justify the study)

- NESO publishes the TEC Register (twice-weekly, single overwritten CKAN
  resource) with project name, customer, connection site, stage, MW,
  effective date, project status, agreement type, host TO, plant type,
  project ID/number and — from November 2025, populated on countersignature
  — Gate. NESO cautions that project status is its best-known
  classification, not authoritative project information.
- A NESO EIR response (document 363736, per an external lead) states NESO
  holds historical registers and points to its disclosure log; dated
  register pages reportedly remain accessible. Batch 01's C2 kill used two
  Wayback captures (2025-03-21, 2025-07-22) and found no capture between
  July 2025 and August 2026. **Whether an archive spanning years exists is
  the first thing to establish.**
- The register carries a regime break: connections reform re-baselined
  dates through Gate 2 offers from December 2025 onward.
- The CUSC Transmission Works Register publishes completion dates for
  enabling works and their amendments; joining it is **phase 2**, not this
  study.

## Pre-declared method

**Unit.** A project identity stable across vintages: `Project ID` where
present in both vintages; otherwise the normalised triple (project name,
customer name, connection site). Identities that split or merge are
recorded, not repaired.

**Events, per project across consecutive vintages:** revision of the
effective date (signed, in months); status transition; capacity change;
disappearance (present at t, absent from every later vintage);
appearance. Each vintage carries its publication date (t_public).

**Per-project metrics:** number of effective-date revisions; net slip
(last observed date − first observed date, months); maximum single
revision; disappeared (yes/no); first-observed status; plant type; host
TO; connection site; capacity band (<50, 50–200, 200–500, ≥500 MW);
initial lead time (first observed effective date − first vintage date,
years); observation span (years).

**Population for Q1–Q3:** projects with observation span ≥ 2 years and
first observed **before 2025-01-01**, so that reform re-baselining cannot
be counted as slippage. Vintages from December 2025 onward are analysed
separately and only descriptively.

## The three pre-declared questions and their thresholds

**Q1 — Is there substantial dispersion?** Substantial if, in the
population, the interquartile range of net slip is ≥ 12 months **and** at
least 20% of projects slipped ≥ 24 months while at least 20% slipped < 6
months (including advances). If dispersion fails, there is little
underwriting information and the study is killed.

**Q2 — Can observable characteristics predict any of it?** Predictive if
at least one pre-listed stratification — first-observed status; plant
type; host TO; initial lead-time band (<3, 3–5, >5 years); capacity band
— shows a rate of "slipped ≥ 24 months" that differs by a factor ≥ 2
between two strata each with n ≥ 30, **and** the direction of that
difference holds in two disjoint first-observation cohorts (first observed
2019–2021 versus 2022–2024). One-cohort effects are recorded but do not
pass.

**Q3 — Does it tell an investor something materially better than
"connection dates can slip"?** Yes if some passing stratum's slip-≥24-month
rate differs from the pooled base rate by ≥ 15 percentage points. That is
the difference between a base rate and an underwriting input.

**Kill conditions.** (a) The archive yields fewer than six vintages or
spans less than three years → killed as *not measurable from the public
record*, with the resolving observation named (NESO's internal register
history, EIR route). (b) Q1 fails → killed. (c) Q1 passes, Q2 fails →
*measurable but not predictable*: recorded as a descriptive fact, killed
for underwriting. (d) All three pass → the snapshot instrument starts
(twice weekly, TEC and embedded registers) and phase 2 (TWR join) is
declared separately.

## Declared falsifiers and confounders

- **F-1** Effective-date changes reflect NESO's administrative
  re-baselining (e.g. reform cohorts, TO programme replanning) rather than
  project-level risk — tested by the regime split and by checking whether
  slips cluster on single vintage dates across unrelated projects.
- **F-2** Project identity is unstable across vintages (renames, ID
  changes), making slip an artefact of matching — the match rate and
  split/merge counts are reported before any metric.
- **F-3** Disappearance is not attrition (de-duplication, transfer to the
  embedded register, data correction) — disappearance is reported
  separately from date slip and never pooled with it.
- **F-4** Status vocabulary changed across vintages — transitions are
  reported on the vocabulary observed, not a harmonised one, unless the
  mapping is one-to-one.
- The vendor-voice claim that grid DD demand "more than tripled" is a lead,
  not evidence, and is not used.

## Three clocks

Every vintage: t_public = its publication or capture date; t_discovered =
2026-08-26/27. No claim rests on a vintage whose publication date is not
established.

## What this study will not do

Build a score; join the Transmission Works Register; model Gate 2
survival from old-regime behaviour; claim anything about distribution-
connected projects; run longer than two working days before reporting.
