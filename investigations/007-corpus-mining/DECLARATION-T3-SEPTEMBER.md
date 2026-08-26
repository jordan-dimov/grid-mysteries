# 007 · September out-of-sample test — the battery BM access discount

**Frozen**: 2026-08-26, before NESO's September 2026 in-merit file exists.
Sealed by the commit that adds this file. Follows `DECLARATION-T3-DECOMPOSITION.md`
(sha256 `ac7b079b…`, verdict C) and its post-hoc sensitivity, which taught the
narrower hypothesis tested here. That sensitivity ran on August data;
under the window rule this test runs on **September**, and no
same-window sensitivity is run in the meantime.

## Hypothesis

> For non-wind units, especially batteries, a large share of apparent
> in-merit BM opportunity is persistently non-executable because of
> location/system constraints — and that access discount persists by
> unit/location.

## Population (fixed now, evaluated on the August file)

Battery unit-directions (`fuel == "BATTERY"`, each `bid_offer` direction
separately) that in the August in-merit file have:

- stage-0 in-merit volume > 0 and raw skipped volume > 0; and
- are **system-dominated**: family S (stage-2 + stage-3 skipped-volume
  drops, zero-clipped, exactly as defined in `DECLARATION-T3-DECOMPOSITION.md`
  and computed by `run_decomp.py::stage_table`) ≥ 50 % of raw skipped
  volume.

August = the most complete August vintage available at run time (expected
to be the full-month file; digest recorded in the results). The cohort is
defined **only** from August; September is never used to select it.

**Minimum cohort**: **n ≥ 20** battery unit-directions present in both
months with September in-merit volume > 0. Below that the test is
"not determinable", not a fail.

## Primary quantity, per unit-direction per month

$$
R = \frac{\text{constraint-excluded in-merit gross value}}{\text{accepted BM gross value}}
$$

- Constraint-excluded in-merit gross value = Σ over (date, pair) of
  (stage-2 + stage-3 skipped-volume drop) × |stage-0 `average_price_per_MWh`|.
- Accepted BM gross value = Σ over (date, pair) of stage-0
  `accepted_volume_MWh` × |stage-0 `average_price_per_MWh`|.
- Prices are the unit's own observed average offer/bid prices from the
  in-merit file, in absolute value so that bids and offers are both gross
  magnitudes. Offers and bids are reported separately as well as pooled;
  the bars apply to the pooled cohort.
- For ranking and for zero handling the bounded transform
  $R' = S / (S + A)$ is used: it is a monotone function of $R$ (so Spearman
  is identical where $R$ is finite) and a unit-month with zero accepted
  value and positive excluded value takes $R' = 1$ (equivalently $R = \infty$,
  which counts as ≥ 0.5). Unit-months with both values zero are dropped.

Labelled everywhere as **gross value-at-stake**. Never "loss", "foregone
revenue" or "saving": an offer price is not a margin, and a unit skipped
in the BM may have earned elsewhere.

## Bars (both must pass)

1. **Economic magnitude**: median $R \ge 0.5$ (equivalently median
   $R' \ge 1/3$) across the cohort **in September**. August median reported
   alongside but is in-sample and does not count.
2. **Persistence**: Spearman rank correlation of $R'$ between August and
   September across the cohort **≥ 0.5**.

Secondary readings, reported and not scored: the same two figures with
unclipped stage drops; offers-only and bids-only; the count of cohort
units with $R' = 1$.

## Outcomes, fixed now

- **Pass** → *If I were buying, siting or valuing a battery, I would
  diligence its historical executable share of in-merit BM opportunity at
  unit level rather than assuming system-average BM access.* The finding
  is then: **a battery can be economically "in merit" but structurally
  unable to access that opportunity, and that access discount persists by
  unit/location.**
- **Fail** → banked as: *persistent raw skipping was mostly a mixture of
  methodology and system exclusions, not a durable economic asset
  attribute.* No decision changes.
- **Not determinable** (cohort < 20) → recorded as such; the test may be
  re-run on October under this same declaration with no amendment.

## Gate and trigger

Acquisition is the irreversible boundary for forensic work: the September
in-merit and exclusion-reasons files are fetched only after the human
seal, once NESO publishes the full-month September 2026 file (expected
early October 2026). Digests of every input are recorded in the results
before the script runs. No August archaeology in the meantime.

## Limits declared in advance

One out-of-sample month; a pass earns a second month, not a publication.
Stage families inherit NESO's attribution; zero-clipping over-attributes
S by 6–16 % (unclipped reading reported). Unit-direction identity is the
BM unit id; a unit re-registered between months drops out of the join.
