# 007 — corpus mining, three frozen tests

**Declared 2026-08-26, before any of the three results was computed.
Frozen on commit; never edited. Results in `RESULTS.md`.** Mandate: use
only data already in the repository; no fetch, FOI, scrape or search; no
model, no score; simple conditional rates; no rescue after outcome.

## T1 — slip persistence (Q1)

- **Population.** 005's old-regime TEC timelines (699 vintages, 2014-01-31 →
  2025-07-22), project-stages keyed as in 005 Amendment 1, observed ≥ 2
  years, first observed before 2025-01-01.
- **Unit.** Project-stage.
- **Exposure.** A *first slip*: the first consecutive-vintage revision of
  `MW Effective From` by ≥ +6 months, occurring at vintage t with ≥ 24
  months of observation remaining after t.
- **Outcome.** A further ≥ +6-month revision within the 24 months after t.
- **Comparison.** Control rate = among project-stages with no ≥ 6-month slip
  in their first 12 months of observation and ≥ 36 months of observation,
  the share with a ≥ +6-month revision in months 12–36.
- **Materiality.** Exposed rate ÷ control rate ≥ 1.5 **and** gap ≥ 15 pp,
  n ≥ 100 in each group; direction holds in both first-observation cohorts
  (2014–2018 and 2019–2024).
- **Kill.** Ratio < 1.5 or gap < 15 pp or either cohort reverses → "a slip
  is a slip, not a signal".

## T2 — position attrition by attribute (Q2)

- **Population.** Same timelines; project-stages first observed ≥ 12 months
  before the final old-regime vintage (2025-07-22).
- **Unit.** Project-stage.
- **Outcome.** *Disappeared*: last observed ≥ 180 days before the final
  vintage (so not right-censored) and absent from every later vintage.
- **Exposures (pre-listed).** First-observed status; plant type (vocabulary
  as observed, not harmonised); capacity band; initial lead-time band.
- **Materiality.** Some pair of strata within one exposure with attrition
  ratio ≥ 2 and gap ≥ 15 pp, n ≥ 50 each.
- **Robustness (mandatory).** Re-run keyed on `Project ID` within the
  ID-stable window 2024-06-14 → 2025-07-22 (renames cannot split
  identities there); the passing pair's direction must hold, with n ≥ 30
  each. A pair that passes only on the name-triple key is a rename
  artefact and fails.
- **Kill.** No pair passes both.

## T3 — skip persistence by unit (Q3)

- **Population.** BM units × direction with positive in-merit volume in
  both May 2026 and July 2026 in NESO's in-merit stack files (retained
  copies; the earlier August vintage `inmerit_allbm_2026-08.csv` for
  robustness).
- **Unit.** (bm_unit, direction).
- **Metric.** Monthly skip share = Σ skipped volume ÷ Σ in-merit volume.
- **Exposure.** Top quartile of May skip share (ties broken by volume
  descending).
- **Outcome.** Top quartile of July skip share.
- **Materiality.** P(top quartile in July | top quartile in May) ≥ 50%, i.e.
  ≥ 2× the unconditional 25%, with n ≥ 100 units in the exposed group; the
  July → August transition shows the same inequality.
- **Descriptive (always reported).** The same conditional by fuel; Spearman
  rank correlation of skip share May → July; the share of persistent
  top-quartile units accounted for by the largest fuel.
- **Interpretation limit, fixed now.** A skip is not an inefficiency (001,
  001B–D established the deliverability and system-flag reasons). T3
  measures whether skip share is a *persistent unit-level property*, which
  is what an owner or acquirer can price; it says nothing about why.
- **Kill.** Conditional < 50% or n < 100, or the Jul → Aug check reverses.

## Decision sentences to be completed, or not

- T1: "If I were a lender, a first observed slip on a position I am
  financing would make me ______."
- T2: "If I were acquiring development-stage positions, I would discount
  class ______ for attrition by ______."
- T3: "If I were buying or siting a BESS, a unit's/location's skip share
  is ______ (persistent / not), so I would ______."

If a sentence cannot be completed honestly from the result, the finding
is banked as "interesting but economically irrelevant".
