# BESS Study 001 — Benchmark fragility under GC0166 duration-aware data

## Status and corpus discipline

A **method-development study** on a new corpus: GB settlement dates
**2026-07-01 through 2026-07-31**. July 2026 is consumed by this study
and thereafter usable only for method work — never promotable to
prospective evidence. The untouched Investigation 002 window
(2026-08-11..17) is not approached. This document — panel rule, interval
and vintage semantics, all five rung definitions, missing-data
behaviours, and the labelling rules — is committed **before any July
data is fetched**. Feasibility reconnaissance to date deliberately used
only non-July slices (schema from 2026-06-25/28, membership from
2026-08-02) and is recorded as such.

## Research question

> When a benchmark tells a battery owner what the asset "could have
> earned" in the Balancing Mechanism, how much of that counterfactual
> survives as it is made physically, duration- and information-credible —
> and what was the benchmark actually entitled to know at decision time?

The output is **how the benchmark moves**, never "missed revenue": every
monetary figure in this study is arithmetic on public numbers, not a
saving, cost, or achievable value, and each rung's figure may only be
described by what that rung can defend.

## Registered hypothesis

> For the July 2026 GC0166 early-submitter panel, less than half of the
> price-only apparent opportunity survives to the public-as-of
> duration-aware rung.

No result is predetermined; a small collapse would itself be a finding
about the informativeness of the new datasets.

## The panel (mechanical, unit-blind)

Candidate units: every BM unit with any MDO or MDB record in July 2026.
A unit **enters the panel** iff, in **both** directions, at least **80%**
of July settlement periods are *reconstructable* (defined below) under
hindsight vintages. No unit is added or removed for narrative reasons;
the rule is committed before July coverage is examined. If the panel is
empty, that is the study's result.

## Interval and vintage semantics (MDO/MDB)

Records carry `timeFrom`/`timeTo`, `levelFrom`/`levelTo` (MW),
`publishTime` and `serialNumber`.

- **Vintage resolution**: for a given instant and vintage cutoff, the
  applicable record among those whose interval covers the instant and
  whose `publishTime` ≤ cutoff is the one with the greatest
  (`publishTime`, `serialNumber`), compared lexicographically, with a
  full content tie-break (interval bounds, levels) so the order is total
  and resolution can never depend on input order.
- **Hindsight** vintage: cutoff = +∞ (all published records).
- **Public-as-of** vintage: cutoff = settlement period start **minus 60
  minutes** (the GB gate-closure convention). This is called *publicly
  observable as of the decision time* — it proves public availability,
  never control-room knowledge.
- **Projection**: an applicable interval is clipped to the settlement
  period; its energy contribution is
  `max(|levelFrom|, |levelTo|) × clipped hours` — a deliberately
  *generous* upper bound, consistent with this project's convention that
  bounds must dominate the instantaneous truth so that any exclusion is
  airtight.
- **Deliverable-energy bound** for a (unit, period, direction, vintage):
  the sum of projected contributions over the period — MDO for offers
  (export capability), MDB for bids (import capability, absolute
  values).
- **Reconstructable**: a (unit, period, direction, vintage) is
  reconstructable iff the union of applicable intervals covers the full
  settlement period. Anything less is **unknown** — never interpolated,
  never partially credited.

## The five rungs

For each panel unit, July settlement period and direction, the *apparent
opportunity* is `best gap × substitutable volume`, where the best gap and
the worse-priced accepted volume come from the Investigation 001 screen
genre, unchanged: the unit's submitted BOD pair versus accepted DISPTAV
`Original` actions of other units in the same period and direction
(offers: accepted price above the unit's offer; bids: accepted price
below the unit's bid). Substitutable volume =
`min(unit's rung bound in MWh, worse-priced accepted MWh)`. What changes
per rung is only the **unit's bound**:

| Rung | Unit bound (MWh over the half hour) | What it can defend |
|---|---|---|
| R1 price-only | BOD level band × 0.5h | the price existed |
| R2 power-feasible | Method Study 001's conservative FPN/MEL/MIL headroom bound × 0.5h, floored at 0 | MW movement not provably impossible |
| R3h duration-aware, hindsight | min(R2, MDO/MDB deliverable-energy bound, hindsight vintage) | the published delivery envelope permits it |
| R3p duration-aware, public-as-of | min(R2, deliverable-energy bound, public-as-of vintage) | same, using only information publicly observable by the decision cutoff |
| R4 operational-context screen | R3p, with periods carrying NESO exclusion context on **either side** of the comparison reported separately | no obvious published exclusion on either side |

R4 is deliberately **not** volume-level operator comparability (001C
proved binary adoption of volumetric exclusions over-corrects); it
reports context presence from NESO's July Skip Rates exclusion data,
keyed on both the unit and its accepted counterparts, and splits the R3p
figure into context-present and context-free parts. Volume-level
reconstruction remains a separately declared frontier.

**Missing data is `unknown`, never a fallback.** A period that is not
reconstructable at R3h/R3p contributes nothing to those rungs' totals
and is counted and reported as unknown, carrying its R2 value only in
the unknown-bucket disclosure. Missing evidence must never make the
benchmark more permissive. A direction with no MDO (or MDB) coverage is
unknown in that direction only.

## Declared outputs

- **Benchmark Fragility table**: per rung, total apparent opportunity
  (GBP, Decimal, labelled as arithmetic), retention vs R1, and the
  unknown-bucket sizes; per unit and pooled; both directions.
- The **hindsight vs public-as-of gap**: periods where R3h > R3p — the
  counterfactual is physically feasible *only with information the
  benchmark acquired retrospectively*.
- The **Counterfactual Integrity Ladder** one-pager: each rung, what it
  defends, and what remains unknowable without owner data (state of
  charge, degradation and cycling constraints, existing commitments,
  outage/derating state, optimiser mandate, forecasts actually held,
  response latency, private commercial constraints).
- `evidence/` — pinned manifests (journalled, immutable), analysis JSON,
  panel table, charts.
- Morpholog: investigation `bess-001-benchmark-fragility`, the hypothesis
  above, and findings only for what the completed study supports.

## Declared inputs (all fetched after this commit)

| Data | Source | Grain |
|---|---|---|
| MDO, MDB | Elexon `datasets/{MDO,MDB}/stream` | per day, July |
| BOD, DISPTAV (both directions) | Elexon per-period endpoints (Investigation 001 layout) | 31 × 48 periods |
| PN, MELS, MILS | Elexon `datasets/{PN,MELS,MILS}/stream` filtered to panel units (`bmUnit` parameter, verified on a non-July slice), fetched **after** the panel step | per day, July |
| NESO Skip Rates July 2026 (In Merit All BM, Exclusion Reasons) | NESO Data Portal dumps | month |
| BM unit reference | already pinned vintage (`case-001/bmunits.json`) | — |

## Reproduction

```bash
uv run python investigations/bess-study-001-benchmark-fragility/bench.py fetch    # network; pins July
uv run python investigations/bess-study-001-benchmark-fragility/bench.py panel    # offline; applies the panel rule
uv run python investigations/bess-study-001-benchmark-fragility/bench.py analyse  # offline; deterministic
```
