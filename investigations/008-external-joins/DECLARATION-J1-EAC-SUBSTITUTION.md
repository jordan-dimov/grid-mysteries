# 008 · J1 — EAC ancillary-service substitution for the battery BM access discount

**Frozen**: 2026-08-27, before any EAC quantity or price has been placed
beside any unit's BM measure. Sealed by the commit that adds this file.
Depends on `007/DECLARATION-T3-SEPTEMBER.md` (sha256 `6a1253d9…`) for the
definition of the per-unit access-discount measure $R'$ and shares its
trigger and seal.

## Hypothesis under test

> Batteries whose in-merit BM opportunity is persistently non-executable
> for locational reasons commit a larger share of their capacity to NESO's
> Response/Reserve services (EAC) — the BM access discount is partly hedged
> by ancillary-service substitution.

The null, which is equally publishable: EAC commitment is unrelated to the
access discount, or lower for constrained units.

## Inputs (fetched only after the human seal; digests recorded in results)

- NESO in-merit and exclusion-reason files for **August and September
  2026** (the same files the 007 September test uses).
- NESO EAC "Response-Reserve Results By Unit" rows with `deliveryStart` in
  August and September 2026 (CKAN resource `a63ab354-7e68-44c2-ad96-c6f920c30e85`
  or the corresponding monthly archive CSVs, whichever is complete at run
  time; both digests recorded if both are used).
- Elexon `reference/bmunits/all` (one pinned snapshot) for
  `generationCapacity`.

## Population

All battery units (`fuel == "BATTERY"`) with stage-0 in-merit volume > 0 in
**both** August and September, matched by exact id to an EAC `auctionUnit`
with `technologyType == "Batteries"` in at least one of the two months.
Units matched to EAC but with zero EAC executed quantity in a month are
retained with EAC = 0 for that month (non-participation is an outcome, not
missing data). **Minimum n ≥ 100** in September; below that the test is
"not determinable".

## Measures, per unit per month

- **Access discount** $R'$: exactly as defined in the 007 September
  declaration, pooled across directions (offers and bids reported
  separately as secondary).
- **EAC commitment (MW)**: $C = \sum \text{executedQuantity} \times h / (H \cdot P)$,
  where $h$ is the delivery-window length in hours, $H$ the hours in the
  month and $P$ the unit's capacity denominator: Elexon `generationCapacity`
  where > 0, else the unit's maximum `executedQuantity` observed in the EAC
  file across the two months (flagged; secondary reading excludes these
  units).
- **EAC gross value (£/MW)**: $V = \sum \text{executedQuantity} \times \text{clearingPrice} \times h / P$.
  Labelled *gross availability payment*; never "revenue" net of anything.
- Service split (Response: DC/DM/DR; Reserve: QR/SR/BR) reported as a
  secondary breakdown, not scored.

## Bars

Scored on **September** only; August is in-sample and reported alongside.

1. **Direction**: Spearman rank correlation across the population between
   $R'$ and $C$, and between $R'$ and $V$.
   - **(a) hedged** if ρ($R'$, $C$) ≥ +0.3 **and** ρ($R'$, $V$) ≥ +0.3;
   - **(b) unhedged / penalised** if ρ($R'$, $C$) ≤ −0.3 **or** both
     |ρ| < 0.2 with n ≥ 100;
   - **(c) volume without value** if ρ($R'$, $C$) ≥ +0.3 and ρ($R'$, $V$) < +0.2;
   - anything else: *indeterminate*, reported as such.
2. **Magnitude** (reported, not scored): median $V$ of the top-quartile-$R'$
   units versus the bottom quartile, as a ratio.

Secondary, not scored: the same correlations within the `AG-` and non-`AG-`
subsets; within units north and south of the SSE-SP/SCOTEX boundary as
classified by EAC postcode area (approximate, hand-mapped, declared in the
results before use).

## Outcomes, fixed now

- **(a)** → *If I were valuing a battery behind a constraint, I would treat
  its BM access discount as partly offset by ancillary-service revenue and
  would diligence the two streams together, not the BM stream alone.*
  007's September decision sentence is restated as net of substitution.
- **(b)** → *Location removes BM optionality without a compensating
  ancillary-service channel.* 007's decision sentence stands and is
  strengthened; the discount is unhedged.
- **(c)** → *The hedge exists in MW but not in £: constrained units lean on
  EAC at prices that make the substitution nearly worthless; the discount
  is unhedged in value and the exposure to EAC price is concentrated in
  constrained units.*
- **Not determinable** → recorded; may re-run on October under this same
  declaration, no amendment.

## What this does not say

No £ of loss is computed. An in-merit offer is not a margin; an EAC
clearing price is an availability payment, not a delivered-energy price.
Correlation across units in one month is not causation; a persistent
optimiser effect (some route-to-market providers favour EAC regardless of
location) is a confounder and the lead-party breakdown is reported so a
reader can see it. One month scored; a pass earns a second month, not a
publication.

## Gate

Acquisition after the human seal, once NESO publishes the full-month
September 2026 in-merit file (expected early October 2026). No EAC rows
are fetched before then. Digests of every input recorded before the script
runs.
