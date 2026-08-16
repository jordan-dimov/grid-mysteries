# Method Study 001C — Where does the remaining disagreement go?

## Status and corpus discipline

Retrospective method-development study, entirely offline on already-pinned
evidence: the 2026-08-04..2026-08-10 corpus, Method Study 001's
deliverability classification, and Method Study 001B's pinned NESO Skip
Rates resources. No new data is fetched; Investigation 002's window
remains untouched. This document — cell set, attribution mapping, layer
order and waterfall semantics — is committed **before** any aggregate
below is computed.

## Research question

Method Study 001B left 2,226 cells (date × direction × unit) that the
feasibility-aware screen flags but NESO's stage-5 methodology does not
mark as skipped. Are those cells attributable, systematically and not
just for a top-20 sample, to NESO's *published* exclusion categories —
and how does agreement change layer by layer as each piece of operational
context is added? What remains when the public exclusions run out?

## Registered hypothesis

> The majority (more than half) of the 2,226 post-filter disagreement
> cells are attributable to NESO-published exclusion categories or to
> full acceptance of the unit's in-merit volume, leaving a minority
> unmatched by any public operational explanation available here.

## Declared inputs

All pinned already: `../method-study-001-phantom-liquidity/evidence/alternatives.parquet`
(classification), `data/raw/neso/inmerit_allbm_2026-08.csv` and
`data/raw/neso/exclusions_2026-08.csv` (digests in
`../method-study-001b-naive-screen/evidence/neso-manifest.json`), and the
001B cell definitions, reused verbatim.

## Declared attribution mapping

Implemented and tested in
`src/grid_mysteries/investigations/exclusion_attribution.py`:

- The atomic reason vocabulary and its grouping into categories
  (`wind_offer`, `behind_constraint`, `system_tagged`, `unwind`,
  `ramping`, `long_notice_or_access`, `invalid_parameters`) was fixed
  from the **July 2026** resource, outside the corpus. Compound reason
  strings split into atomics; unrecognised fragments are preserved as
  `unrecognised`, never dropped.
- A disagreement cell's **exclusion rows** are NESO Exclusion Reasons
  rows matching its (date, direction, unit).
- **Primary attribution**: the category with the largest summed absolute
  excluded volume over the cell's rows; ties break by the declared layer
  order. Per-category volumes overlap by design for compound rows (the
  published data does not partition them); they rank, they do not
  partition energy. **Any-presence** counts are reported alongside.
- Cells with no exclusion rows are classified from the stage-5 in-merit
  file: **`fully_accepted_in_merit`** if the cell's stage-5 accepted
  volume is at least its in-merit volume (nothing left to skip);
  **`absent_from_neso_universe`** if the unit has no stage-5 row at all
  (NESO's availability construct never seated it); otherwise
  **`unmatched`** — the irreducible public-data disagreement.

## Declared waterfall

Layers add operational context to the screen cumulatively, in the fixed
order: physical deliverability (from 001B), then `wind_offer`,
`behind_constraint`, `system_tagged`, `unwind`, `ramping`,
`long_notice_or_access`, `invalid_parameters`, `unrecognised`. A layer
**unflags** any currently flagged cell having at least one exclusion row
of that category — applied to *all* flagged cells, never conditioned on
NESO's verdict (no peeking). After each layer the full agreement metrics
against NESO stage 5 are recomputed and reported: agreement rate, NESO
skips still caught, false alarms remaining. Losing genuine catches to a
layer is reported, not hidden.

## Outputs

- `evidence/disagreement-analysis.json` — attribution tables (primary and
  any-presence, by direction), the waterfall, and the unmatched residue
  with its top cells.
- `evidence/waterfall.svg` — the layer-by-layer agreement chart.
- `NOTE.md` — narrative; no neat ending is manufactured if the residue is
  large.
- Morpholog: investigation `ms-001c-disagreement-anatomy`, the hypothesis
  above, and a finding only for what the completed study supports.

## Reproduction

```bash
uv run python investigations/method-study-001c-disagreement-anatomy/disagreement.py analyse  # offline
uv run python investigations/method-study-001c-disagreement-anatomy/disagreement.py charts   # offline
```
