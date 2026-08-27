# 008 · J1 — EAC ancillary-service substitution for the battery BM access discount

**Frozen**: 2026-08-27, before any EAC quantity or price has been placed
beside any unit's BM measure. First committed at `e8ee111` (sha256
`741b60f2…`); **amended the same day, before the seal and before any
fetch**, on the sponsor's condition that every scored measure be
normalised by registered battery MW and that Response and Reserve be
reported separately before any aggregate. Sealed by the commit that adds
this amended text.
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
- **Registered battery MW** $P$: Elexon `generationCapacity` from the
  pinned `reference/bmunits/all` snapshot. **Only units with $P > 0$ enter
  the scored population** (133 of the 155 currently matched units have
  it). Units without it are listed, and a secondary unscored reading uses
  the unit's maximum `executedQuantity` across the two months as $P$ —
  flagged as biased, because it bounds commitment at 1 by construction.
- **EAC commitment (MW·h per registered MW)**:
  $C = \sum \text{executedQuantity} \times h \,/\, P$, where $h$ is each
  delivery window's length in hours. This is the sponsor's
  "cleared EAC MW-hours ÷ registered battery MW". (Dividing further by the
  hours in the month gives a capacity fraction; reported alongside, same
  ranks.)
- **EAC gross value (£ per registered MW)**:
  $V = \sum \text{executedQuantity} \times \text{clearingPrice} \times h \,/\, P$.
  Labelled *gross availability payment*; never "revenue" net of anything.
- **Product split is reported first.** $C$ and $V$ are computed and
  tabulated separately for **Response** (DC, DM, DR) and **Reserve** (QR,
  SR, BR), with the correlations of the next section shown per family,
  *before* the pooled figures appear. The bars below are applied to the
  pooled measures; a family-level result that contradicts the pooled one
  is reported next to it and the verdict says so.

The size confound this guards against, stated so it cannot be forgotten:
without $P$ a large battery would show both more constrained in-merit
volume and more cleared EAC MW, manufacturing outcome (a).

## Bars

Scored on **September** only; August is in-sample and reported alongside.

1. **Direction**: Spearman rank correlation across the scored population
   (registered MW known) between $R'$ and $C$, and between $R'$ and $V$,
   both per registered MW.
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

The question, in the sponsor's words: **does poor BM access get compensated
elsewhere in the revenue stack?**

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
