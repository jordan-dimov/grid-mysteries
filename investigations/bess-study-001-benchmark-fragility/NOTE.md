# Benchmark fragility, measured: what GC0166 data does to a battery counterfactual

*BESS Study 001 research note. Corpus: July 2026, consumed by this study;
the Investigation 002 window (2026-08-11..17) untouched. Every figure is
reproducible from the pinned evidence (`evidence/fragility-analysis.json`,
digest bound into `fnd-bess-001-fragility`); every rule was committed
before July was fetched. All monetary figures are **arithmetic on public
numbers** — never savings, missed revenue, or achievable value.*

## The panel (mechanical, unit-blind)

Six units published MDO/MDB data in July. The pre-declared gate (≥80% of
July's 1,488 settlement periods reconstructable in both directions,
hindsight vintages) admitted four — `2__HANGE004`, `E_BARNB-1`,
`E_BHOLB-1`, `T_PINFB-1`, each at 1488/1488 — and excluded `E_BURWB-2`
(49%) and `E_THMRB-1` (34%), both mid-month joiners. The rule was
committed before coverage was examined, and it excluded one of the two
units this project found narratively interesting in earlier work. That
is what a mechanical panel is for.

## The Benchmark Fragility table (pooled, July, both directions)

| Rung | Apparent opportunity | Retention | What this level can defend |
|---|---:|---:|---|
| R1 price-only | £618,908,576 | 100% | the price existed |
| R2 power-feasible | £29,215,605 | 4.72% | MW movement not provably impossible (FPN/MEL/MIL) |
| R3h duration-aware, hindsight | £16,133,648 | 2.61% | the published delivery envelope permits it |
| R3p duration-aware, public-as-of | £14,870,059 | 2.40% | same, using only information publicly observable 60 minutes before the period |
| R4 no exclusion context on either side | £295,915 | 0.05% | no published NESO exclusion context on either side of the comparison |

Three results stand out:

1. **Physics is still the biggest correction** — 95.3% of the price-only
   construct never survives FPN/MEL/MIL. This replicates the phantom-
   liquidity finding on a battery-specific panel.
2. **The new GC0166 data is materially informative**: duration envelopes
   remove a further **44.8% of what physics alone permitted**
   (£29.2m → £16.1m). A battery can be "available" at its power rating
   without having that energy available for the interval a benchmark
   values — and July 2026 is the first month where public data
   quantifies that for GB.
3. **£1,263,589 of the duration-aware figure existed only in hindsight**
   (7.8% of R3h, across 989 unit-direction-periods): the MDO/MDB
   information that makes those opportunities look feasible was published
   *after* the decision cutoff. A benchmark using final envelopes is
   quietly using information the decision-maker did not have. This is
   the *publicly observable as of decision time* result — it proves
   public availability, never control-room knowledge.

The R4 row is a **disclosure, not a verdict**: 98% of the surviving
public-as-of figure coincides with NESO exclusion context (constraint,
wind, tagging…) on at least one side of the comparison, at daily grain.
001C proved such context is volumetric, so this study deliberately does
not adopt it as a filter — it reports how little of the counterfactual
is free of it.

The registered hypothesis (`hyp-bess-001-half-survives`: less than half
survives to R3p) is **confirmed** at 2.40%. Unknown buckets under the
binding never-fallback rule: 2 periods in the entire study.

## What remains unknowable without owner data

Actual state of charge; degradation and cycling constraints; existing
market commitments (FFR/DC/wholesale positions consuming the same MWh);
outage and derating state; optimiser mandate and risk limits; forecasts
actually held at decision time; response latency; private commercial
constraints. **Public data can test whether a claimed opportunity
survives public reality. Asset data is required to establish whether the
opportunity was actually achievable.** Every rung above is an upper
bound on the layer beneath it.

## Reproduction

Commands in `METHOD-STUDY-BESS-001.md`. Evidence: `july-manifest.json`
(4,528 artefacts), `neso-july-manifest.json`, `physical-july-manifest.json`
(93), `panel.json`, `fragility-analysis.json` — manifests registered and
the finding published in the governed record (`bess-001-benchmark-fragility`).
