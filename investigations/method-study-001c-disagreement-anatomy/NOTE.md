# Where the disagreement goes: anatomy of the residue

*Method Study 001C research note. Entirely offline on pinned evidence
from Method Studies 001 and 001B; every figure in
`evidence/disagreement-analysis.json`.*

## The narrative the corpus supports

> **Price told me there were opportunities everywhere — the naive screen
> agreed with NESO's own skip methodology on 35% of unit-days. Physics
> took it to 65%. NESO's wind-offer rule took it to 67%. And the
> remaining disagreement is not mysterious: 99.7% of it is named by the
> operator's published operational data. Six unit-days in a week resist
> every public explanation available here.**

## The attribution (the study's core result)

Of the **2,226** cells the feasibility-aware screen flags but NESO's
stage-5 methodology does not mark as skipped:

| Primary attribution | cells | share |
|---|---:|---:|
| absent from NESO's in-merit universe (their availability construct never seated the unit) | 897 | 40.3% |
| behind constraint | 769 | 34.5% |
| long-notice / accessibility | 132 | 5.9% |
| ramping | 129 | 5.8% |
| wind offer | 122 | 5.5% |
| unwind | 106 | 4.8% |
| fully accepted in merit (nothing left to skip) | 39 | 1.8% |
| system-tagged | 25 | 1.1% |
| invalid parameters | 1 | 0.0% |
| **unmatched by any public explanation** | **6** | **0.27%** |

The registered hypothesis (`hyp-ms-001c-majority-attributable`) is
**confirmed**, far beyond its majority threshold. The two dominant terms
are exactly the two dimensions a price-only reconstruction lacks:
**availability as the operator defines it** (40.3%) and **location**
(34.5%).

The six unmatched cells are all bid-side battery/small units (`BHOLB-1`
×3, `THMRB-1` ×2, `CUMHW-1`), present in NESO's stage-5 stack, not
skipped, not excluded, not fully accepted. They are the genuine frontier
of what this public reconstruction cannot yet adjudicate; under the
explanation protocol they are *compatible but unproven* candidates for
intra-day timing and state-of-charge mechanisms, and nothing more.

## The waterfall — and why it bends

Recomputed on 001B's fixed 6,390-cell universe (see the recorded
correction in `METHOD-STUDY-001C.md`):

| layer | agreement | NESO skips caught | false alarms |
|---|---:|---:|---:|
| naive price screen | 34.9% | 1,997/2,017 | 4,137 |
| + physical deliverability | 64.7% | 1,988/2,017 | 2,226 |
| − wind-offer exclusions | **66.6% (peak)** | 1,988/2,017 | 2,104 |
| − behind-constraint (binary) | 64.8% | 1,018/2,017 | 1,252 |
| − system-tagged | 64.8% | 1,005/2,017 | 1,236 |
| − unwind | 57.9% | 477/2,017 | 1,148 |
| − ramping | 57.6% | 310/2,017 | 1,000 |
| − long-notice/accessibility | 58.3% | 292/2,017 | 942 |

The decline after the peak is a finding, not a failure: NESO's exclusions
are **volumetric and stage-scoped** — a unit can have some volume behind a
constraint and still be skipped for the rest — so adopting exclusion
*categories* as binary cell filters destroys genuine catches (the
constraint layer alone forfeits 970). Getting past 67% agreement
requires volume-level reconstruction, not more labels. That, plus
availability-as-the-operator-defines-it, is the concrete methodological
frontier for Investigation 002 and beyond.

## The layered story in one paragraph

A price-only screen is wrong about GB balancing opportunity in three
nested ways, and the corpus now quantifies each: it ranks physically
impossible alternatives first (001B: every one of its top 1,000); its
apparent magnitude is mostly phantom (001: 67.3% of pairwise inversions;
001B: 90.5% of the notional); and even its feasibility-filtered residue
is dominated by availability and location context the operator publishes
but price data cannot see (001C: 99.7% attributable, 6 cells/week
unmatched). Public data does not withhold the explanation — it withholds
the *resolution* at which the explanation operates.

## Reproduction

Commands in `METHOD-STUDY-001C.md`; inputs are the pinned artefacts of
Method Studies 001 and 001B (digests in their manifests). Corpus
discipline: retrospective method study on the consumed window;
Investigation 002's window remains untouched.
