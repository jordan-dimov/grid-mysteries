# Method Study 001D — The six

## Status and corpus discipline

Retrospective explanation-testing of the six unmatched unit-day cells
identified by Method Study 001C, on the consumed 2026-08-04..2026-08-10
corpus. The cases were selected by 001C's committed procedure, not by
hand. The only new data permitted is period-level BOALF for the relevant
consumed dates (journalled, immutable). Investigation 002's window
remains untouched. This document is committed before any per-cell result
is computed.

## The cases (fixed by 001C's evidence, verbatim)

`../method-study-001c-disagreement-anatomy/evidence/disagreement-analysis.json`
→ `unmatched_cell_list`: BHOLB-1 (2026-08-05, -06, -09), THMRB-1
(-06, -10), CUMHW-1 (-09); all bid-direction.

## Registered hypothesis

> Each of the six unmatched unit-day cells can be fully explained from
> public period-level information.

## Declared mechanisms to test, per cell

1. **Accepted-side exclusion**: 001C attributed disagreement only through
   exclusion rows keyed by the *alternative* unit. NESO's Exclusion
   Reasons file also carries rows with
   `excluded_from_accepted_or_feasible_merit_stack = "Accepted"`, keyed
   by the accepted unit: a pricier accepted action excluded from NESO's
   comparison stack cannot generate a NESO skip. Test: for the accepted
   units our screen compared the cell's unit against (recomputed from
   pinned window data for the cell's date, bid direction), collect their
   accepted-side exclusion rows and BOALF acceptance flags for the
   periods concerned.
2. **Granularity**: our intensity sums period-level gaps; NESO aggregates
   daily. Test: the cell's period-by-period profile — in which periods it
   qualified, with what gap and deliverable-headroom bound — against its
   NESO stage-0..5 daily volumes.
3. **De-minimis deliverability**: the surviving headroom bound may be
   physically trivial. Report the bound (from Method Study 001's
   classification table) per qualifying period.
4. **Battery state of charge / intra-day energy limits**: expected to be
   **not observable publicly** unless the PN profile itself settles it;
   the PN extremes per period are reported.

Statuses per the Investigation 001 explanation protocol; plausibility
never rises above *compatible but unproven*; each per-cell conclusion is
one of explained / partly explained / publicly unexplained.

## Outputs

- `evidence/six-anatomy.json` — per-cell period profiles, accepted-side
  exclusion evidence, NESO stage profile, protocol status per mechanism.
- `evidence/boalf-manifest.json` — newly pinned BOALF artefacts.
- `NOTE.md` — per-cell verdicts and the overall hypothesis resolution.
- Morpholog: investigation `ms-001d-the-six`, the hypothesis above, and a
  finding only for what the completed study supports.

## Reproduction

```bash
uv run python investigations/method-study-001d-the-six/sixcases.py fetch    # BOALF for relevant consumed periods
uv run python investigations/method-study-001d-the-six/sixcases.py analyse  # offline
```

## Corrections

1. **Determinism fix (recorded 2026-08-16, after the governed finding
   was published but before any public post; results unaffected).** `analyse` iterated a Python set of counterpart units,
   so tie ordering inside its counters depended on per-process hash
   randomisation: re-runs produced content-identical output with
   reordered equal-count entries, breaking byte-for-byte reproduction.
   The script now iterates in sorted order. The pinned
   `evidence/six-anatomy.json` remains the published vintage (its digest
   is bound into `fnd-ms-001d-six-explained`); every count and every
   conclusion is unchanged.
