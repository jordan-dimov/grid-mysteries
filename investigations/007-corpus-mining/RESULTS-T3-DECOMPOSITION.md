# 007 · T3 decomposition — results

**Declaration**: `DECLARATION-T3-DECOMPOSITION.md`, sha256
`ac7b079b33bd2da276a1a0f3bb86c757d7fa0726904e58c1de03ae67d1580a0b`,
sealed at commit `f1b2f85` before any unit-level value was computed.
**Run**: 2026-08-26, `run_decomp.py`; evidence in
`evidence/t3-decomposition.json` (frozen test) and
`evidence/t3-decomposition-sensitivity.json` (post-hoc, labelled as such).

## Verdict under the frozen rule: **C — neither A nor B passes**

| Condition | Threshold | May→Jul | Jul→Aug | Result |
|---|---|---|---|---|
| A1 S-majority vs R-majority persistence gap | ≥ 15 pp, n ≥ 30 each | −5.5 pp (S n=124, R **n=10**) | +29.8 pp (S n=157, R **n=16**) | fail (R group too small) |
| A2 volume-weighted S share of persistent set | ≥ 50 % both months | 34.9 % / 28.5 % | 34.2 % / 31.2 % | fail |
| B1 residual-share top-quartile persistence | ≥ 50 %, n ≥ 100 | 49.1 % (80/163; base 25.2 %) | 51.0 % (105/206; base 25.0 %) | fail by 0.9 pp |
| B2 R share of persistent set's skipped volume | ≥ 25 % | 0.95 % / 0.59 % | 0.55 % / 0.51 % | fail decisively |

No decision changes under the frozen rule. The corpus-mining stop condition
applies and no further latent questions are generated.

T3 itself replicates on the stage-explicit measure: top-quartile persistence
of the stage-0 (raw) skip share is 66.7 % (106/159) against 23.1 %
unconditional, and 57.4 % (109/190) against 21.7 %.

## What the decomposition actually shows

The answer to the frozen question is sharper than the verdict suggests, and
it cuts against the thesis that motivated the test.

**1. Persistent skipped volume is almost entirely volume NESO's own
methodology already explains.** System-wide, the residual skipped volume
left after all five exclusion stages is 10.8 % / 12.3 % / 10.9 % of raw
skipped volume (May / July / August). Within the persistently most-skipped
set it is **0.5–1 %** by volume. The "commercial/price-related" component
the question asked about is not there to be found in this population.

**2. The persistent set is two different populations.**

- **Wind unit-directions** (19 of 106; 27 of 109 persistent units) carry
  **68–70 % of the set's skipped volume**, and 99.6–100 % of that volume is
  removed at stage 1 as "Wind offer". Their persistence is *definitional*:
  a wind offer in merit is never accepted under NESO's methodology, so the
  unit's raw skip share is ~100 % every month. This is a flaw in T3's
  instrument, recorded as a correction to T3 below, not a property of the
  grid.
- **Non-wind unit-directions** (70 / 71 units) have skipped volume that is
  essentially all stage-2/3 — behind constraint or system-tagged. With the
  pre-declared zero-clipping the S family reads 106–116 % of raw; unclipped
  (the post-hoc sensitivity) it is ~100 % net of a small stage-5
  re-addition. **65–68 of the ~70 units are S-majority in every month**;
  the unit-median S share is 0.93–1.05. The residual is 1.7–2.6 % of their
  volume, and only 7–10 units in any month have residual ≥ 25 %.
  By fuel, the S-dominated persistent units are batteries (23 / 27), gas
  reciprocating and CCGT/OCGT units, and non-pumped hydro (11 / 11); by
  direction, offers dominate volume (226 k of 231 k MWh) while bids are
  roughly half the unit count.

**3. Why A failed anyway.** A1 needed a comparison group of persistent
"commercial" units that, it turns out, barely exists (9–16 R-majority units
across the whole exposed set), and A2's volume weighting was swamped by the
wind artefact. In the post-hoc non-wind view, S-majority exposed units
persist at 63.1 % / 58.1 % against 55.6 % (n=9) / 30.0 % (n=10) for the
rest — directionally A, statistically nothing. Under the project rule an
amended test may not run against the window that taught the amendment,
so this is reported as a lesson, not a pass.

**4. What B's near-miss means.** Residual skip share is a moderately
persistent unit property (Spearman 0.57 / 0.60; top-quartile persistence
49–51 %). It is small in volume — about 11 % of raw skipped volume
system-wide — and concentrated outside the persistently most-skipped set.
If there is a behavioural signature, it lives among ordinary units, not
among the units T3 flagged.

## Correction appended to T3 (preserved, not rewritten)

T3's headline "skip share is a persistent unit property" stands, but part
of it is trivial. Because `run_skip.py` summed across NESO's six stages and
used raw skipped volume, wind units whose offers are excluded by rule enter
the top quartile every month by construction. Roughly a fifth of T3's
persistent set by count and two-thirds by volume is this artefact. The
non-trivial residue of T3 is: **non-wind units that are persistently
skipped are persistently skipped because they sit behind a constraint or
are system-tagged**, and that locational condition is itself
month-to-month stable (Spearman of the S share 0.40 / 0.62).

## Decision it would change, and the next test — described, not run

Under the frozen rule no component survived, so formally there is nothing
to attach a decision to. Reported here because the mandate asked for it
conditionally and the descriptive evidence points one way:

- **The decision, if the locational reading held on a fresh window**: if I
  were buying, siting or valuing a battery, I would diligence the
  historical *executable* share of its in-merit BM volume at the unit
  level, because for the persistently skipped non-wind units nearly all
  in-merit volume is non-dispatchable for locational reasons, and that
  condition persists month to month. Behind-constraint volume is by
  definition not an executable opportunity, so the economic content is a
  *negative* one — a discount on expected BM access, not a hidden upside.
- **Cheapest existing-corpus test of economic meaning** (not run): for
  battery unit-directions in the three in-merit files, compute per
  unit-month the constraint-excluded (stage 2 + 3) in-merit MWh and the
  accepted MWh, value each at the unit's own `average_price_per_MWh` from
  the in-merit file, and report the ratio of locationally non-executable
  in-merit value to accepted BM value, with its month-to-month unit-level
  persistence. Pass condition to freeze: ratio ≥ 0.5 for the persistent
  S-dominated battery set with Spearman ≥ 0.5 across both transitions.
  This is a gross bound on revenue-at-stake, never a loss: an offer price
  is not a margin, and skipped volume may have earned elsewhere. Same
  three files, one script, about an hour. To respect the window rule it
  should run on the September in-merit file once published, or be
  declared openly as a same-window sensitivity.

## Limits

Three summer months, two transitions. Stage families inherit NESO's own
attribution. The zero-clipped stage drops over-attribute by 6–16 % for the
S family; the unclipped figures are post-hoc. No £ figure is produced.
