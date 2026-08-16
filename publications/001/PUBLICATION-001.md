# Publication Pack 001 — the four-layer story

No new analysis. Every number here and in the two visuals
(`story.svg`, `anatomy-2226.svg`, rendered by `render.py` **from the
committed evidence files, never typed by hand**) already exists in the
governed record. Corpus: 2026-08-04..2026-08-10.

## Draft post copy

> I built a model to find missed opportunities in Britain's Balancing
> Mechanism. Every one of its top 1,000 opportunities was physically
> impossible.
>
> That wasn't the interesting part.
>
> Once I added the first layer of physics, agreement with NESO's own
> skip methodology jumped from 35% to 65%.
>
> Then I followed the remaining disagreement through the operator's own
> published data. 99.7% had an operational explanation. Availability.
> Constraints. Wind rules. Ramping. Unwind. Accessibility.
>
> After starting with 3.86 million apparent price inversions, I was left
> with six unit-days in an entire week that public data still couldn't
> explain.
>
> That is the part I want to investigate.
>
> *Public data does not withhold the explanation — it withholds the
> resolution at which the explanation operates.*

## Every displayed number, bound to its source

| Number | Value | Source of truth | Governed finding |
|---|---|---|---|
| Raw pairwise inversions | 3,856,031 | MS-001 `evidence/analysis.json` → `funnel.f1_raw_pairwise_inversions` | `fnd-ms-001-majority-phantom` |
| Top-1,000 with impossible #1 | 1,000 / 1,000 | MS-001B `evidence/screen-analysis.json` → `top_n_distortion_by_gap.1000.naive_top1_alternative_non_deliverable` | `fnd-ms-001b-phantom-led-ranking` |
| Raw vs feasibility-aware top-100 overlap | 0 | MS-001B → `top_n_distortion_by_gap.100.overlap_with_post_filter_top_n` | `fnd-ms-001b-phantom-led-ranking` |
| Naive notional (arithmetic on public numbers, not value) | £607.8m → £57.6m (90.5% vanished) | MS-001B → `naive_counterfactual_notional_gbp` | `fnd-ms-001b-phantom-led-ranking` |
| Agreement with NESO stage 5 | 34.9% → 64.7% | MS-001C `evidence/disagreement-analysis.json` → `waterfall[0..1].agreement_rate` (fixed 6,390-cell universe) | `fnd-ms-001c-residue-attributed` |
| NESO skips still caught | 1,988 / 2,017 | MS-001C → `waterfall[1]` | `fnd-ms-001c-residue-attributed` |
| Residual disagreement cells | 2,226 | MS-001C → `disagreement_cells` | `fnd-ms-001c-residue-attributed` |
| Publicly attributed | 2,220 / 2,226 = 99.7% | MS-001C → `primary_attribution` (availability universe 897 = 40.3%, behind constraint 769 = 34.5%, other published rules 554, unmatched 6) | `fnd-ms-001c-residue-attributed` |
| Unmatched frontier | 6 unit-days | MS-001C → `unmatched_cell_list` | `fnd-ms-001c-residue-attributed` |

Evidence digests for the three analysis files are carried inside the
corresponding Finding claims in `morpholog/claims-export.json` and are
Merkle-anchored in `morpholog/audit-anchor.json`.

## The six frontier unit-days

| Date | Direction | NGC unit |
|---|---|---|
| 2026-08-05 | bid | BHOLB-1 |
| 2026-08-06 | bid | BHOLB-1 |
| 2026-08-06 | bid | THMRB-1 |
| 2026-08-09 | bid | BHOLB-1 |
| 2026-08-09 | bid | CUMHW-1 |
| 2026-08-10 | bid | THMRB-1 |

## Update after Method Study 001D (before any publication)

The six frontier unit-days were subsequently investigated (governed
finding `fnd-ms-001d-six-explained`): **all six are explained** by the
same locational mechanism, keyed on the accepted side of the comparison —
NESO excludes constraint-driven accepted actions from its skip-comparison
stack, so the comparison our screen made is one the operator's
methodology declines to make. The week's unmatched residue is now
**zero**. The post may therefore end either on "six unit-days I want to
investigate" (accurate as of 001C, with 001D as the follow-up post) or on
the stronger completed arc ("and when I chased the last six, they fell to
the same mechanism"). Both endings are supported by the governed record;
choose editorially, not evidentially.

## Verification footer

Pre-registered hypotheses (each committed before its data was touched) ·
pinned evidence with SHA-256 manifests · governed Morpholog audit record,
replayable from `morpholog/batches/` and verifiable offline
(`morpholog audit verify-pack morpholog/evidence-pack.json
--anchor-file morpholog/audit-anchor.json`) · CI reruns the full gate and
the record replay on every push. Repository:
github.com/jordan-dimov/grid-mysteries.
