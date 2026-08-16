# The naive opportunity screen, measured — and checked against NESO

*Method Study 001B research note. Corpus 2026-08-04..2026-08-10; every
figure reproducible from `evidence/` (see `METHOD-STUDY-001B.md` for the
pre-declared metrics). The antagonist here is not any analyst: it is the
seductive but wrong answer you get when price data is easier to obtain
than operational truth.*

## Candidate headline

> **I built the naive "missed opportunity" screen that public GB
> balancing data invites you to build. All 100 of its top opportunities
> had a physically impossible #1 pick, and none of the raw top 100 kept a
> top-100 place once a single feasibility question was asked. Checked
> against NESO's own skip-rate methodology, that one question nearly
> doubled the screen's agreement with the operator — and the biggest
> remaining disagreements turn out to be exclusions NESO's methodology
> already documents.**

## What was measured

25,326 accepted balancing actions that week (13,965 offers, 11,361 bids)
had at least one apparently better-priced alternative in raw bid-offer
data. For each, the naive screen picks the single best-priced
alternative; the physical-state screen removes alternatives Method Study
001 proved could not deliver (zero headroom from FPN/MEL/MIL at every
instant of the period) and picks the best survivor.

- **64.5%** of naive #1 picks (16,336 of 25,326) were provably
  non-deliverable — the registered hypothesis
  (`hyp-ms-001b-naive-top1-phantom`, majority) is **confirmed**.
- Only 5.1% of apparent opportunities vanish entirely; the screen's
  failure mode is not fabricating opportunities but **ranking phantoms
  first**: the raw top 10, top 100 and top 1,000 (by gap, and again by
  notional) had a non-deliverable #1 pick **every single time**, and the
  overlap between raw and feasibility-aware top-100 rankings is **zero**.
- Median apparent-gap reduction per action: £75/MWh (p75 £262; the p90 of
  £9,886 is the ±£9,949 sentinel-submission effect from Method Study 001).
- The **naive counterfactual notional** — accepted MWh × apparent gap,
  which is *arithmetic on public numbers, never a saving, cost, missed
  revenue or achievable value* — summed to **£607.8 m for one week**. A
  single deliverability question removed **90.5%** of it. The £57.6 m
  that remains is *unadjudicated*, not achievable: timing, dynamics and
  location are all still untested.

## The external check: NESO's own skip methodology

NESO's official Skip Rates dataset (pinned, all seven window dates
covered) gives per-unit daily skipped volumes through six methodology
stages. On the 6,390 comparable (date, direction, unit) cells:

| | naive screen | + physical-state filter |
|---|---|---|
| agreement with NESO stage 5 | 34.9% | **64.7%** |
| NESO skips caught | 1,997 / 2,017 | 1,988 / 2,017 |
| cells flagged that NESO does not skip | 4,137 | 2,226 |

The naive screen flags 96% of all unit-days — it cries "skip" at almost
everything. One physical-feasibility test removes 46% of those false
alarms while giving up only 9 of NESO's 2,017 skips. Rank correlation
with NESO's skipped *volumes* stays weak either way (Spearman 0.34 →
0.39): even a feasibility-filtered price screen does not track magnitudes,
which is itself a finding. Definitions differ (daily aggregation,
availability-based stacks), so these are agreement counts, not
precision/recall.

**The top 20 disagreements close the loop.** Every one is a persistent
wind-unit offer — the same Tullo/Burn of Whilk/Lochluichart/Moy/Andershaw
submissions that dominated Method Study 001's residual — and NESO's
Exclusion Reasons file says exactly why the operator does not count them:
**"Wind offer"** (stage 1; 4,186 exclusion rows across the 20) and
**"Behind constraint"** (561 rows). The dimensions our public
reconstruction lacks are not mysterious; they are named in the operator's
own methodology, and location is the largest.

## Residual anatomy (top 20 surviving cases)

The accepted side is 19/20 CCGT and only 1/20 SO-flagged — ordinary
energy actions. The surviving alternatives are 6 North Scotland wind
units and 14 aggregated supplier/flexibility units (Statkraft, EDF,
Flexitricity aggregates) — precisely the categories where public
availability and location data are weakest. Under the explanation
protocol these cases are *compatible but unproven* for constraint and
wind-exclusion mechanisms; none is evidence of dispatch error.

## Why this matters

If a backtest, curtailment-cost estimate, or optimiser benchmark treats
public bid-offer ladders as dispatchable flexibility, this corpus says
its opportunity ranking is not slightly wrong — its entire head is
phantom-led, and ~90% of its apparent £-magnitude dissolves under the
*first* physics question, before location or dynamics are even asked. The
hard problem in public energy data is not acquiring it; it is knowing
what the data is entitled to tell you — and the gap between those two
things is measurable.

## Reproduction

Commands in `METHOD-STUDY-001B.md`. Evidence: `screen-analysis.json`,
`screen.parquet` (25,326 actions), `neso-comparison.json`,
`neso-manifest.json` (pinned NESO CSVs), `anatomy.json`,
`case-boalf-manifest.json`, `screen-funnel.svg`, `rank-distortion.svg`.
Corpus discipline: retrospective method study on the consumed window;
Investigation 002's window remains untouched.
