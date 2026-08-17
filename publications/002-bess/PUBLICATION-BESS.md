# Publication Pack — BESS Study 001

No new analysis. Every number below exists in committed evidence and the
governed record; the two visuals
(`../../investigations/bess-study-001-benchmark-fragility/evidence/fragility-ladder.svg`
and `.../revision-flows.svg`) are rendered by `render_fragility.py` from
the evidence file, never typed by hand. The Counterfactual Integrity
Ladder one-pager is `LADDER.md`.

## Draft post copy

> Britain has just started publishing a new piece of battery operating
> data.
>
> GC0166 went live this summer: batteries now publish Maximum Delivery
> Offer and Bid data — time-varying information about what a
> limited-duration asset can actually deliver, rather than a static
> power rating. July 2026 is the first full month for which the public
> data exists.
>
> I tested what it does to a naive battery revenue-opportunity benchmark,
> rebuilt level by level for the four early-submitter units, with every
> rule frozen before the data was fetched.
>
> Physics did what physics does: 95% of the price-only construct never
> survived basic deliverability checks.
>
> Then the new duration data removed **another 45% of what physics had
> allowed**. A battery can be "available" at 50 MW without having 50 MW
> available for the interval your benchmark just valued.
>
> The more interesting result: using the *final* published envelope gives
> a provably different answer from using only the envelope that was
> publicly observable when the decision had to be made — **in both
> directions**. The final data supported £4.7m of opportunity that
> wasn't publicly knowable at decision time, and withdrew £3.4m that the
> contemporaneous data had supported.
>
> That matters if hindsight is being used to judge whether an optimiser
> underperformed. A hindsight benchmark doesn't just know more — it
> reconstructs a *different feasible world* from the one the decision
> was made in.
>
> So the next time somebody says a battery captured 72% of its
> opportunity, the question is: **what information set defined the other
> 28%?**
>
> Public data can test whether a benchmark survives increasingly
> realistic public constraints. It still cannot tell you whether your
> battery could actually have captured the residual — that needs the
> asset's actual state of charge, commitments, outages, and the
> optimiser's information set and mandate.
>
> (All figures are arithmetic on public numbers — never savings or
> missed revenue. Method, evidence digests and the reproducible pipeline
> are public.)

## Every displayed number, bound to its source

| Number | Value | Source of truth | Governed finding |
|---|---|---|---|
| Price-only construct | £618,908,576 | `evidence/fragility-analysis.json` → `pooled.r1_price_only` | `fnd-bess-001-fragility` |
| Power-feasible | £29,215,605 (4.72%) | → `pooled.r2_power_feasible` | `fnd-bess-001-fragility` |
| Duration-aware, final vintage | £16,133,648 (2.61%) | → `pooled.r3h_duration_hindsight` | `fnd-bess-001-fragility` |
| Duration-aware, public-as-of | £14,870,059 (2.40%) | → `pooled.r3p_duration_public` | `fnd-bess-001-fragility` |
| GC0166's marginal effect | −44.8% of the physics-feasible figure | 1 − r3h/r2 (renderer-computed) | `fnd-bess-001-fragility` |
| Added in hindsight | £4,689,718 over 989 periods | → `future_only_gbp`, `hindsight_exceeds_public_periods` | `fnd-bess-001-fragility-corrected` |
| Revised away by final vintage | £3,426,133 over 1,991 periods | → `revised_away_gbp`, `public_exceeds_hindsight_periods` | `fnd-bess-001-fragility-corrected` |
| Context-free residual | £295,915 (0.05%; disclosure, not verdict) | → `pooled.r4_context_free` | `fnd-bess-001-fragility` |
| Panel | 4 of 6 units, 1488/1488 coverage; 2 excluded by the pre-committed 80% gate | `evidence/panel.json` | — |
| Hypothesis outcome | confirmed at 2.40% ≪ 50% | `hyp-bess-001-half-survives` | both findings |

Correction provenance: the first finding's £1.26m point-in-time figure
was a pooled net; the correcting finding decomposes it (both remain on
the record; see the study's Corrections section). Chronology: rules
committed 2026-08-16 before any July fetch; results and correction
2026-08-17; no public post has yet been made.

## Verification footer

Pre-registered rules and hypothesis (committed before the corpus was
fetched) · pinned evidence with SHA-256 manifests (4,623 artefacts for
this study) · governed Morpholog record, replayable from
`morpholog/batches/` and verifiable offline against a signed anchor ·
CI reruns the gate, the record replay and the control tests on every
push. Repository: github.com/jordan-dimov/grid-mysteries.
