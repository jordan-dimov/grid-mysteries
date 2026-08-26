# 007 · T3 decomposition — is persistent BM skipping locational or commercial?

**Frozen**: 2026-08-26, before any unit-level exclusion or stage value was
computed. Sealed by the commit that adds this file. Follows T3 in
`DECLARATION.md` (digest 9ccfbe9e…); this is a new declaration, not an
extension of that one, and it generates no new latent questions.

## Frozen question (verbatim from the mandate)

> Among unit-directions that remain in the most-skipped quartile across
> months, what proportion of that persistence is associated with recurring
> system/constraint exclusion versus commercial/price-related exclusion?

## Metadata inspected before freezing (no unit-level values)

1. Reason vocabulary of the Exclusion Reasons files, with stage, for May,
   July and August 2026 (twenty distinct strings; twelve carry >1,000 MWh).
2. The arithmetic relation between the In Merit file and the Exclusion
   Reasons file. Findings that shape the method:
   - The In Merit file has one row per **stage 0–5** for each
     (date, unit, direction, pair). In-merit volume is essentially constant
     across stages; **skipped volume falls down the chain** (May: 1.758 M MWh
     at stage 0 → 0.190 M MWh at stage 5). Stage 0 is therefore the raw
     "in merit but not accepted" volume and stage 5 is the residual NESO's
     own methodology leaves unexplained.
   - `in_merit − accepted − skipped ≈ 0` at stage level for 98.7 % of
     unit-days (May).
   - Exclusion-row volumes (3.03 M MWh, May) are **not** a partition of the
     skipped volume: rows labelled "Accepted" come off the accepted side and
     some feasible-merit rows do not reduce skipped volume at all. The
     Exclusion Reasons file is therefore used only to **label** stages, never
     summed as if it were skipped volume.
   - Stage → reason mapping is stable across all three months:
     stage 1 = Wind offer; stage 2 = Behind constraint (≥ 94 % of the stage's
     excluded volume; remainder ramping / inaccessible very-long-notice);
     stage 3 = System-tagged; stage 4 = Unwind; stage 5 = long-notice /
     inaccessible / cannot-take-offline / pumped-storage-through-zero.
3. `run_skip.py` (T3) summed skipped and in-merit **across all six stages**,
   so T3's share was a stage mixture weighted towards raw skips. Recorded
   here as a limitation of T3's instrument; T3's measure is re-reported for
   continuity, but the primary measure below is stage-explicit.

## Objects

Per (bm_unit, bid_offer) per month, summing over days and pairs:

- `in_merit`  = Σ stage-0 in-merit volume (MWh); population requires > 0.
- `raw`       = Σ stage-0 skipped volume.
- `drop_s`    = Σ max(skipped[s−1] − skipped[s], 0) for s = 1..5, computed
  per (date, unit, direction, pair) before summing.
- `residual`  = Σ stage-5 skipped volume.

Reason families, fixed from the stage mapping above:

| Family | Stages | Reading |
|---|---|---|
| **S — system / locational** | 2 + 3 | behind constraint, system-tagged |
| **U — operational unwind** | 4 | operator unwinding earlier actions |
| **T — unit-technical declarations** | 1 + 5 | wind offer, notice/ramping/accessibility parameters the unit declares |
| **R — residual (unexplained by NESO's methodology)** | stage-5 skipped | where offer pricing and dispatcher behaviour live; NESO publishes no "price" exclusion reason because in-merit already means price-competitive |

"Commercial/price-related" in the frozen question is operationalised as
**R**, with **T** reported beside it as unit-controlled but technical. Shares
are of `raw`; where `raw` = 0 the unit contributes no share.

## Population and measures

Same as T3: unit-directions present in both months of a transition with
`in_merit` > 0 in both; transitions May→July and July→August (August =
the earlier vintage, `inmerit_allbm_2026-08.csv`, as in T3). Top quartile
by rank as in `run_skip.py::top_quartile_flag`.

- `share_raw`      = raw / in_merit           (primary persistence measure)
- `share_resid`    = residual / in_merit      (commercial-only measure)
- `share_S`        = (drop_2 + drop_3) / in_merit
- T3's original all-stage share, re-reported.

**Persistent set P** = top quartile of `share_raw` in both months.

## Pass conditions (all thresholds fixed now)

**A — locational persistence passes if both**
- A1: among month-1 top-quartile units, the persistence rate of units whose
  month-1 skipped volume is S-majority (S ≥ 50 % of raw) exceeds that of
  units that are R-majority by **≥ 15 pp**, with **n ≥ 30** in each group,
  in **both** transitions; and
- A2: within P, the volume-weighted S share of raw skipped volume is
  **≥ 50 %** in both months of both transitions.

**B — commercial persistence passes if both**
- B1: top-quartile persistence of `share_resid` (the measure with every
  system, unwind and technical exclusion removed) is **≥ 50 %** conditional
  (against 25 % unconditional) with **n ≥ 100** exposed, in both transitions;
  and
- B2: within P, the volume-weighted R share of raw skipped volume is
  **≥ 25 %** in both months of both transitions.

**C — neither**: if neither A nor B passes in full, the finding is banked as
"persistent skipping is a unit property whose composition is mixed or
dominated by technical/operational exclusions", and no decision changes.

A and B may both pass. A partial pass (one transition, or one sub-condition)
is reported as "not established" and does not change a decision.

## Decisions pre-attached to outcomes

- **A passes** → *If I were buying or siting a battery, or valuing one, I
  would diligence historical executable-BM exposure at the unit/location
  level rather than rely on system-average skip rates.* The nearest cheap
  existing-corpus test of economic meaning is then the £-value of the
  S-dominated skipped volume at the units' own offer prices — **described,
  not run**, in the results.
- **B passes** → *A BESS owner or optimiser can be benchmarked against its
  peers on residual skip share; persistent residual skipping is a
  behavioural signature, not a grid property.* Cheapest next test likewise
  described, not run.
- **C** → banked; no decision changes; the corpus-mining mandate's
  stop condition applies.

## Kill and limits declared in advance

- Three months, two transitions; a summer sample, not a year.
- Skip volume is not lost revenue: the price gap between a skipped and an
  accepted action is not measured here and no £ figure is produced.
- Stage families inherit any misattribution in NESO's own methodology;
  the stage-2 family contains ≤ 6 % non-constraint volume, reported as such.
- Units in the top quartile can have small in-merit volumes; the funnel
  reports volume-weighted and unit-count views separately.

## Inputs (sha256)

| File | Digest |
|---|---|
| `data/raw/neso/inmerit_allbm_2026-05.csv` | `809e3b69cf24db19c95904e8038d426067656947e00bde822a4f99e39710972b` |
| `data/raw/neso/inmerit_allbm_2026-07.csv` | `964968f407c6fe54cf2800d0e57597eb9775a8fd65631a7bf16b5f57ee0d9109` |
| `data/raw/neso/inmerit_allbm_2026-08.csv` | `983ead609c7e49031c2b6768351cd466c3ad88e76c988748b9eb2703a27eebda` |
| `data/raw/neso/exclusions_2026-05.csv` | `0fde1148e983980fe689f28e23d47feb1d14feb93f460216846fa21f900966a1` |
| `data/raw/neso/exclusions_2026-07.csv` | `66bbd53274517b4452c93af180b1c24e58917db5c03dd8dbb7157572e45a00d8` |
| `data/raw/neso/exclusions_2026-08.csv` | `cd0d54ff89ced5bbe33429ae14befb3e1f9b15e2d8f2de7cc1a918c98f6b77c2` |
