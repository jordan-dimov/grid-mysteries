# Publication Pack 001 — the four-layer story

No new analysis. Every number here and in the two visuals
(`story.svg`, `anatomy-2226.svg`, rendered by `render.py` **from the
committed evidence files, never typed by hand**) already exists in the
governed record. Corpus: 2026-08-04..2026-08-10.

## Draft post copy (final arc, decided after Method Study 001D)

> I tried to find evidence that Britain's electricity system was
> ignoring cheaper power.
>
> My first pass found 3,856,031 apparent price-order inversions in one
> week.
>
> The largest looked absurd: NESO paid offshore wind £179.76/MWh to
> reduce output while a hydro unit appeared willing to pay the system
> £9,949/MWh to do the same thing. So I kept digging. The hydro unit
> wasn't generating.
>
> Then I tested the whole week. Every one of the raw screen's top 1,000
> "opportunities" was led by an alternative that physically couldn't
> deliver. The screen produced £607.8m of apparent counterfactual
> notional; one elementary physical-availability check cut it to £57.6m.
> Agreement with NESO's own skip methodology went from 35% to 65%.
>
> Then I chased the remaining disagreement through NESO's published
> operational data. Availability explained a large chunk. Constraints
> another. Wind rules, ramping, accessibility and unwind explained almost
> all the rest. Six unit-days survived.
>
> I investigated those too. They disappeared as well — the mistake was on
> the other side of my comparison: I was measuring against accepted
> actions NESO itself removes from its skip stack as constraint
> management.
>
> 3.86 million apparent anomalies. Zero unexplained cases in the week.
>
> Electricity-market data can be completely accurate and still tell you
> the wrong story if you reconstruct the system at the wrong level of
> resolution.
>
> So I've changed the model. The next investigation runs prospectively on
> a completely untouched week, rules frozen before I see the data, the
> selector now aware of physical availability, volume-level constraints
> and exclusions on both sides of the comparison.
>
> Now we find out what survives.

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
| Unmatched after 001C | 6 unit-days | MS-001C → `unmatched_cell_list` | `fnd-ms-001c-residue-attributed` |
| The £179.76 / £9,949 opening case | Mystery 001 | Investigation 001 `evidence/selected.json` + `case-report.json` | `fnd-001-explained` |
| The six, explained (accepted-side exclusions) | 6 / 6 | MS-001D `evidence/six-anatomy.json` (Behind constraint 760–43,752 rows per cell-date; SO-flagged counterparts) | `fnd-ms-001d-six-explained` |
| Unexplained residue for the week | 0 | 001C unmatched minus 001D explained (computed in `render.py`) | `fnd-ms-001d-six-explained` |

Evidence digests for the three analysis files are carried inside the
corresponding Finding claims in `morpholog/claims-export.json` and are
Merkle-anchored in `morpholog/audit-anchor.json`.

## The six unit-days that fell last (all explained by 001D)

| Date | Direction | NGC unit |
|---|---|---|
| 2026-08-05 | bid | BHOLB-1 |
| 2026-08-06 | bid | BHOLB-1 |
| 2026-08-06 | bid | THMRB-1 |
| 2026-08-09 | bid | BHOLB-1 |
| 2026-08-09 | bid | CUMHW-1 |
| 2026-08-10 | bid | THMRB-1 |

## Editorial decision and post two

The completed arc above is the chosen ending (governed finding
`fnd-ms-001d-six-explained`: all six fell to accepted-side "Behind
constraint"/"System-tagged" exclusions; the week's unmatched residue is
zero). The 001C cliffhanger is retired — we already know the answer, and
manufacturing suspense would undercut the project's credibility. The
tension belongs to Investigation 002.

**Post two, ready-made:** "My research system refused to let me publish
my own finding" — the organic Morpholog refusal (001C's finding was
lawfully rejected by `finding_has_at_least_one_source` until its
provenance manifests were attached), plus the governance architecture:
pre-registration sealed by kernel gates, replayable batches, signed
Merkle anchors, control tests proving the locks lock.

## Verification footer

Pre-registered hypotheses (each committed before its data was touched) ·
pinned evidence with SHA-256 manifests · governed Morpholog audit record,
replayable from `morpholog/batches/` and verifiable offline
(`morpholog audit verify-pack morpholog/evidence-pack.json
--anchor-file morpholog/audit-anchor.json`) · CI reruns the full gate and
the record replay on every push. Repository:
github.com/jordan-dimov/grid-mysteries.
