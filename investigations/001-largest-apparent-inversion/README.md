# Mystery 001 — the week's largest apparent price-order inversion

## Status

**Pre-declared.** This document was committed *before* any data from the
declared window was fetched. The selection rule below may not change after
data is seen; if it turns out to be defective, the defect and its fix are
recorded here and the selection re-runs under the amended rule with the
amendment visible in git history.

## Why pre-declare?

Hand-picking an "interesting" settlement period would introduce selection
bias at the first research step. Instead, the case investigates itself into
existence: a deterministic rule, declared here in advance, is applied to a
time window chosen by chronology, and the top qualifying event becomes
Mystery 001 whether it turns out exciting, mundane, or already explained.

## Declared window

- Rule: the most recent complete Monday-to-Sunday week of GB settlement
  dates ending at least three full days before the declaration date, to
  allow settlement publication to stabilise.
- Declaration date: **2026-08-16**.
- Window therefore: settlement dates **2026-08-04 through 2026-08-10**
  inclusive, all published settlement periods (48 per day expected; no
  clock change occurs in this window).

## Declared data

For every settlement period in the window, from the Elexon Insights API:

| Dataset | Endpoint | Role |
|---|---|---|
| BOD | `/balancing/bid-offer/all?settlementDate={d}&settlementPeriod={p}` | submitted bid-offer pairs: prices (GBP/MWh) and MW level bands |
| DISPTAV | `/balancing/settlement/indicative/volumes/all/{bid\|offer}/{d}/{p}` | accepted volume per pair (MWh), `dataType == "Original"` rows |

Every response is pinned as an immutable local artefact; its SHA-256 digest,
URL, and fetch time are recorded in `evidence/manifest.json`. The analysis
reads only pinned artefacts. Later revisions by the publisher do not change
this investigation's inputs; they would be recorded as new evidence.

## Declared candidate definition

Within one settlement period and one direction:

- **Offers** are pairs with `pairId >= 1` priced at the BOD `offer` price;
  **bids** are pairs with `pairId <= -1` priced at the BOD `bid` price.
- A pair is **accepted** if its DISPTAV `Original` accepted volume is at
  least 0.01 MWh in absolute value (a de-minimis guard against settlement
  noise).
- A pair is **unaccepted** if its accepted volume is absent or exactly
  zero. Pairs strictly between zero and the de-minimis threshold qualify as
  neither side.
- A pair is **available** (in the narrow, declared-willingness sense) if
  its BOD level band reaches at least 1 MW in absolute value. Physical
  availability (MEL/PN headroom, dynamics) is deliberately *not* part of
  selection; it belongs to the explanation-testing stage.
- A **candidate** is an (accepted pair, unaccepted pair) combination from
  two different BM Units where the unaccepted pair was priced better for
  the system: cheaper for offers (NESO pays), higher-priced for bids (NESO
  is paid).
- Pairs whose price differs between BOD level slices of the same period are
  malformed and dropped; null-priced pairs are skipped.

## Declared measure and selection

- Measure: the **price gap in GBP/MWh** (accepted minus unaccepted for
  offers; unaccepted minus accepted for bids), computed in decimal
  arithmetic.
- Ranking: largest gap first; ties broken by settlement date, then
  settlement period, then direction, then accepted unit, accepted pair id,
  unaccepted unit, unaccepted pair id (all ascending/lexicographic).
- **The top-ranked candidate is Mystery 001.** No discretion is exercised
  after this point about *which* case to investigate.

The rule is implemented in `src/grid_mysteries/investigations/bod_inversion.py`
and exercised by `tests/test_bod_inversion.py` on synthetic fixtures.

## Declared hypothesis

No causal hypothesis is registered up front. The registered hypothesis is
the null:

> The apparent price-order inversion selected by this pre-declared
> procedure can be fully explained from publicly available information.

The investigation attempts to falsify that. Specific mechanisms (prior
dispatch state, dynamic parameters, constraints, SO-flagging, publication
timing, …) become child hypotheses only as evidence demands.

## Known limitations, declared up front

- "Unaccepted while cheaper" compares *whole pairs within one settlement
  period*; it does not model intra-period acceptance timing.
- Selection availability is declared willingness (a submitted BOD pair with
  a non-trivial level band), not proven physical deliverability.
- DISPTAV volumes are settlement outputs at the vintage fetched; the
  acceptance facts could in principle be revised in later settlement runs.
- Sentinel pricing (e.g. defensive ±£9,999 pairs) is *not* excluded by the
  rule. If the method selects a sentinel-driven case, that is the case.

## Reproduction

```bash
uv run python investigations/001-largest-apparent-inversion/select.py fetch   # network; pins raw artefacts
uv run python investigations/001-largest-apparent-inversion/select.py select  # offline; deterministic
```

`select` reads only pinned artefacts and writes `evidence/candidates-top50.json`
and `evidence/selected.json`.

## Selection result

*To be recorded by a later commit, after the data is fetched. The result
section may report the outcome but may not alter anything above it.*
