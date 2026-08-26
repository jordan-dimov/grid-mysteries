# 006 — results: the enabling works' history does not improve identification of unreliable connection dates; if anything, it points the other way

**Run**: 2026-08-26, one working day. Declaration `be3cce73…` (commit
`0d8a470`), Amendment 1 (`de15224`) declared the completion-date proxy
before any join was computed. Evidence: `evidence/twr-attribution-summary.json`;
per-revision attributions in `data/derived/tec-history/attribution.csv`; TWR
vintages and journal under `data/raw/neso/twr/` (FOI-25-133, document
371516, SHA-256 `d5f2d8f9…`). Logic and tests:
`src/grid_mysteries/investigations/twr_attribution.py`,
`tests/test_twr_attribution.py`; runner `run.py`.

## The material (T1 — kill condition (a): not met)

NESO's FOI-25-133 disclosure (7 Nov 2025) contains **31 Transmission
Works Register reports, 2017-05-04 → 2025-10-03**, roughly quarterly
(median gap 94 days), growing from 758 project→scheme rows to 7,376. Each
row pairs a project with one enabling scheme (e.g. `SHET-RI-025c`) and
carries the **project's** connection date — not the scheme's completion
date (Amendment 1). 3,359 distinct schemes have a proxy completion
timeline (earliest dependent connection date per vintage).

**Join:** 863 of 005's 1,161 population project-stages matched to ≥ 1
scheme (**74.3 %**), all by the normalised (customer, site) or (name, site)
rule — no TEC project number resolved through the TWR's `PRO-` numbers
in this window. Threshold ≥ 50 %: **passes**. Of the 863, 351 had a matched
scheme whose proxy completion date had already slipped ≥ 6 months within
12 months of the project's first TEC observation ("works slipped"); 512
had not ("works clean").

## Three-column reading

**Observed.**

| | works slipped (n 351) | works clean (n 512) | gap |
|---|---|---|---|
| TEC slip ≥ 24 months | **21.7 %** | **26.6 %** | **−4.9 pp** |
| cohort 2019–2021 | lower | higher | same sign |
| cohort 2022–2024 | lower | higher | same sign |

- **T2 — discrimination: FAIL.** Bar ≥ +20 pp; observed −4.9 pp, and the
  *negative* direction holds in both cohorts and within each host TO
  (NGET 18.3 % vs 23.8 %; SHET 23.5 % vs 31.6 %; SPT 24.4 % vs 28.4 %).
- **T3 — reclassification: FAIL.** Pooled matched rate 24.6 %; bands at
  ±10 pp. Status-only bands: Awaiting Consents *high*, Scoping and Consents
  Approved *mid*. Adding the works flag moves **47 of 863 projects (5.4 %)**
  — all of them Awaiting Consents projects whose works had slipped, which
  drop from *high* to *mid*. Bar ≥ 20 %.
- **T4 — attribution of ≥ 24-month TEC slips (213 events):** works-led 56
  (26 %), project-led 128 (60 %), unattributable 29 (14 %). By first
  status: Scoping 29 / 57 / 9; Awaiting Consents 20 / 39 / 4; Consents
  Approved 7 / 26 / 8. F-1: the 2,610 works moves spread across TWR
  vintages — the busiest single vintage carries 15.6 % — so this is not
  one administrative re-baselining event. F-3: median TWR gap 94 days, so
  the ±180/90-day attribution window is resolvable.

**Supported inference.**

- The dependency graph beneath the date, read at this cadence and through
  this proxy, does **not** add underwriting information beyond the TEC
  register itself. Where it changes a classification at all, it changes it
  toward *lower* risk.
- About a quarter of large TEC slips are accompanied by a same-direction
  move in an enabling scheme's proxy date inside the window; three fifths
  are not. On this evidence most large slips are not visibly network-led.
- The negative sign is a real regularity, not noise: it survives both
  cohorts and every TO with n ≥ 30. It is recorded and **deliberately not
  explained** here. Two mechanisms are compatible with it and with the
  declared falsifiers, and neither is tested: F-5 reverse ordering (a
  works slip and the project's re-dating land together, so a project
  flagged at month 12 has already absorbed its slip); and the 005 lead-time
  effect (projects behind large shared reinforcements sit further out and
  their dates move less).

**Not publicly determinable.** Per-scheme completion dates (the TWR as
disclosed does not carry them; CUSC says the register should); whether the
proxy's moves are works slippage or the earliest dependent withdrawing;
anything about post-December-2025 vintages.

## Verdict under the declaration

T1 passes; T2 and T3 fail → **kill condition (b)**:

> **Interesting empirical evidence about GB connection slippage, suitable
> for publication and credibility-building, not a proprietary underwriting
> instrument.**

005's findings stand as the publishable result: a fifth of contracted
positions slip by two years or more; *Awaiting Consents* triples the odds
relative to *under construction*; three-to-five-year lead times slip three
times as often as longer ones. 006 adds that the enabling works' public
history, read through the only proxy the disclosed register permits, does
not sharpen any of that — and that "your works have already slipped" is
not, on this evidence, bad news for a project's date.

No snapshot instrument is started. No score is built. The plant-type
harmonisation remains out of scope.

## What would change this

- **Per-scheme completion dates.** If NESO's internal TWR carries them (as
  CUSC describes), an EIR request for the scheme-level date history would
  replace the proxy. Recorded as watch material alongside `w-005-tec-hole`.
- **A pre-declared test of F-5** — does a works move *precede* the project
  re-dating, or land with it? The attribution table
  (`data/derived/tec-history/attribution.csv`) already holds the ordering;
  the reading rule must be frozen before it is examined.

## Sources

NESO FOI-25-133 (document 371516, 7 Nov 2025): "TWR Report" workbooks 4 May
2017 → 3 Oct 2025; TEC vintages per 005. CUSC Section 6 (Transmission Works
Register obligations) as the description of what the register is meant to
publish.
