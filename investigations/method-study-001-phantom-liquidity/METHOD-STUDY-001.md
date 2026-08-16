# Method Study 001 — Phantom liquidity in GB Balancing Mechanism data

## Status and corpus discipline

This is a **retrospective method-development study** on the
already-consumed corpus of Investigation 001: settlement dates
**2026-08-04 through 2026-08-10**. It is explicitly *not* Investigation
002 and produces **no out-of-sample evidence**; per the project doctrine,
an amended selection rule never re-runs on the window that taught it, and
no data after 2026-08-10 is touched here. What this study *can* legitimately
do with in-sample data is measure the behaviour of the naive method itself.

This document — metrics, classification rules, fallbacks and output
policy — is committed **before** the additional physical-state data is
fetched and before any aggregate below is computed.

## Research question

> When analysts treat submitted Balancing Mechanism bids and offers as
> available flexibility, how badly can they misread what the grid actually
> could have dispatched?

## Registered hypothesis

> In the 2026-08-04..2026-08-10 corpus, the majority (more than half) of
> raw pairwise price-order inversions involve an unaccepted alternative
> that is clearly non-deliverable under the conservative public
> physical-state bound declared below.

The study may falsify this. A small collapse would itself be a
publishable, more surprising result.

## Inputs

- The 1,008 pinned window artefacts of Investigation 001 (BOD, DISPTAV;
  digests in `../001-largest-apparent-inversion/evidence/manifest.json`).
- **New**: per-period `PN`, `MELS` and `MILS` records for every settlement
  period in the window, from
  `/balancing/physical/all?dataset={PN|MELS|MILS}&settlementDate={d}&settlementPeriod={p}`,
  pinned under the repo's immutable journalled machinery
  (`evidence/physical-manifest.json`).
- The BM Unit reference vintage already pinned for Investigation 001
  (`data/raw/elexon/case-001/bmunits.json`, SHA-256
  `1a60fcbbad99f2b7…`), for registered generation/demand capacities.

## Declared funnel metrics

Candidate generation uses Investigation 001's rule **unchanged**
(`bod_inversion.py`: de-minimis 0.01 MWh, availability band ≥ 1 MW,
same-unit exclusion, pair-level, per period and direction).

- **F1 — raw pairwise inversions**: total (accepted, unaccepted) pairs
  with a positive price gap. Expected to reproduce 3,856,031.
- **F2 — episodes**: distinct (settlement date, period, direction)
  containing at least one inversion. Ceiling 672.
- **F3 — unique alternatives**: distinct (date, period, direction,
  unaccepted BMU, pair id) participating in at least one inversion.
- **F4 — concentration**: share of F1 attributable to each
  (unaccepted BMU, submitted price, direction) group; reported as the full
  cumulative (Pareto) curve plus the top-20 table. No threshold.
- **F5 — persistence**: for each (BMU, pair id, price) submission, the
  fraction of the 336 settlement periods in which it appears in BOD;
  reported as a distribution and as the F1-weighted mean. Continuous; no
  threshold.
- **F6 — clearly non-deliverable alternatives**: F3 members whose
  deliverable-volume upper bound (below) is ≤ 0.
- **F7 — residual**: F3 minus F6, with the raw-inversion (F1) and episode
  (F2) counts they carry. The residual is reported with its price-gap
  percentiles.

## Declared conservative deliverability bound

Implemented and tested in
`src/grid_mysteries/investigations/phantom_liquidity.py`:

- For a **bid** alternative: `max FPN endpoint − floor`, where the floor is
  the minimum MILS endpoint; if MILS is absent, `min(0, registered demand
  capacity)`; if both absent, unbounded.
- For an **offer** alternative: `ceiling − min FPN endpoint`, where the
  ceiling is the maximum MELS endpoint; if MELS is absent, the registered
  generation capacity; if both absent, unbounded.
- Endpoint extremes are taken across *all* level slices of the settlement
  period, pairing the most generous values, so the bound dominates the
  instantaneous headroom at every moment of the half hour.
- Classification: **non_deliverable** iff the bound ≤ 0 (zero is the only
  threshold, and it is not arbitrary: it is the definition of "no room to
  move"). Everything else, including any case with missing public state,
  is **not_ruled_out**.

`not_ruled_out` is *not* a claim of executability: intra-period acceptance
timing, ramp rates and other dynamic parameters, prior instructions,
stable-limit behaviour and constraint location are all untested here. The
endpoint of this study is only: *these apparent alternatives survive / do
not survive the public feasibility checks applied here.*

## Outputs

- `evidence/analysis.json` — every count and definition above.
- `evidence/alternatives.parquet` — one row per F3 alternative with its
  price, band, physical extremes, bound, classification, persistence and
  carried inversion count (exact decimal values as strings alongside
  float convenience columns). If the file exceeds 10 MB it moves to
  `data/derived/` with its digest recorded in `analysis.json`.
- `evidence/funnel.svg`, `evidence/concentration.svg` — the two charts.
- `NOTE.md` — the research note. A candidate headline is only included if
  the numbers support it; no dramatic conclusion is manufactured.
- A Morpholog finding for claims directly supported by the completed
  study, attached to the pinned manifests.

## Reproduction

```bash
uv run python investigations/method-study-001-phantom-liquidity/study.py fetch    # network; pins PN/MELS/MILS
uv run python investigations/method-study-001-phantom-liquidity/study.py analyse  # offline; deterministic
uv run python investigations/method-study-001-phantom-liquidity/study.py charts   # offline; renders SVGs
```
