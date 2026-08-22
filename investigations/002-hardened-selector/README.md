# Mystery 002 — what survives a hardened selector on an untouched week

## Status

**Pre-declared.** This document is committed *before* any settlement data
from the declared window is fetched or inspected. The selection rule below
may not change after data is seen; if it proves defective, the defect and
its fix are recorded in **Corrections** and the amended rule runs against a
*different, untouched* window — never against the window that taught the
amendment.

Declaration date: **2026-08-22**.

## What 002 tests

Investigation 001 and Method Studies 001/001B/001C/001D consumed
2026-08-04..10 and taught one concrete lesson: a selection rule whose
availability test is BOD bands alone surfaces **undeliverable standing
submissions** first (001's case: an alternative with FPN 0 and MEL 0 that
could not import a single MW), and a comparison universe that ignores the
*accepted* side treats **system-driven curtailment** as if it were a
missed cheap action (001D's six residual cases).

Publication Pack 001 committed publicly to the consequence:

> the next investigation runs prospectively on a completely untouched
> week, rules frozen before I see the data, the selector now aware of
> physical availability, volume-level constraints and exclusions on both
> sides of the comparison.

002 is that run. The question is deliberately open:

> **Applied to a week it has never seen, does the hardened selector still
> surface a case that public data cannot explain — or does the residue go
> to zero again?**

Both answers are publishable. A zero residue is a second independent
validation of the method; a surviving unexplained case is Mystery 002.

## Declared window

- **Settlement dates 2026-08-11 through 2026-08-17 inclusive** (Tuesday to
  Monday, contiguous with 001's 2026-08-04..10), all published settlement
  periods; no clock change occurs in this window.
- This window was **reserved in advance**, before 001's own window was
  analysed, and has been protected in every subsequent session. Its
  identity is therefore fixed by prior commitment, not derived by a
  chronology rule applied today — which removes any suspicion that the
  window was chosen after the fact.
- The window ended five days before this declaration, satisfying 001's
  "at least three full days for settlement publication to stabilise".

## Corpus exposure, declared honestly

The window has **never been contacted for Elexon market data**: no BOD,
DISPTAV, BOALF, PN, MELS or MILS artefact for 2026-08-11..17 exists in
`data/raw/`, and none has ever been fetched.

Two NESO **monthly** files in our possession do contain reserved-window
rows, and this is declared rather than discovered later:

| File | Fetched | Rows dated 2026-08-11..15 |
|---|---|---|
| `data/raw/neso/exclusions_2026-08.csv` | 2026-08-16 | 74,897 |
| `data/raw/neso/inmerit_allbm_2026-08.csv` | 2026-08-16 | 638,986 |

Both were pinned for Method Study 001B (NESO publishes monthly files with
a lag; on 16 August they ran to 08-15). **No row inside the reserved
window has ever entered an analysis, result, chart or finding**: every
study filters to its own window (`if date not in window`, where `window`
is 2026-08-04..10), and the reserved-window rows were dropped before any
computation. Possession is not inspection — but the previously repeated
claim "2026-08-11..17 remains untouched" was imprecise, and this table is
the correction.

The methodological consequence is contained by design: **NESO exclusion
data is not a selection input for 002** (see below). It is used only as a
post-selection cross-check, so no pre-held row can influence which case
002 selects.

## Declared data

For every settlement period in the window, pinned immutably (SHA-256,
URL, fetch time journalled to `evidence/`) from the Elexon Insights API:

| Dataset | Role in 002 |
|---|---|
| BOD | submitted bid-offer pairs: prices (GBP/MWh) and MW level bands |
| DISPTAV (bid + offer) | accepted volume per pair (MWh), `dataType == "Original"` rows |
| BOALF | acceptance records, including the `soFlag` used by the accepted-side screen |
| PN | final physical notification levels (deliverability floor/ceiling reference) |
| MELS / MILS | maximum export / import levels (headroom bounds) |
| BM-unit reference | registered generation and demand capacity (headroom fallbacks) |

Analysis reads only pinned artefacts. Later publisher revisions do not
change 002's inputs; they would be recorded as new evidence.

NESO Skip Rates (in-merit and exclusion data) for the window will be
fetched and pinned **after selection is complete**, purely as a
cross-check output. It is explicitly not a selection input.

## Declared candidate definition

Unchanged from 001 unless stated. Within one settlement period and one
direction:

- **Offers** are pairs with `pairId >= 1` at the BOD offer price; **bids**
  are pairs with `pairId <= -1` at the BOD bid price.
- A pair is **accepted** if its DISPTAV `Original` accepted volume is at
  least **0.01 MWh** in absolute value; **unaccepted** if absent or exactly
  zero. Volumes strictly between qualify as neither.
- A pair is **submitted-available** if its BOD level band reaches at least
  **1 MW** in absolute value.
- A **candidate** is an (accepted pair, unaccepted pair) combination from
  two different BM Units where the unaccepted pair was priced better for
  the system (cheaper for offers, higher-priced for bids).
- Pairs whose price differs between BOD level slices of the same period are
  malformed and dropped; null-priced pairs are skipped.

**Amendment A — physical deliverability enters selection** (taught by 001,
which selected an alternative with zero deliverable volume). An unaccepted
alternative qualifies only if it is **not provably non-deliverable**:
using `grid_mysteries.investigations.phantom_liquidity`, compute the
period's headroom upper bound in the candidate's direction
(`max FPN − MILS floor` for bids; `MELS ceiling − min FPN` for offers,
with registered capacities as declared fallbacks). An alternative
classified `non_deliverable` (bound ≤ 0, which proves no instant of
positive headroom) is **excluded from selection**. Anything else is
`not_ruled_out` and remains a candidate — this is a one-sided,
conservative test, never a claim of executability. Missing public state
yields `not_ruled_out`, so absent data can never manufacture an exclusion.

**Amendment B — the accepted side is screened too** (taught by 001D, where
all six surviving residual cases were accepted actions NESO removes from
its own skip stack as constraint management). A candidate is excluded when
its **accepted** action is flagged `soFlag = true` in BOALF — Elexon's own
published marker that the action was system-driven rather than
energy-balancing. Comparing a system-driven curtailment against an
energy-priced alternative is the category error 001D identified.

**Deliberately not adopted** (taught by 001C): NESO's published exclusion
reasons are **volumetric**, and adopting them as binary selection filters
*degraded* agreement with NESO's own methodology. They are therefore not
used to filter candidates on either side — only reported as a
post-selection cross-check. This also keeps the pre-held NESO rows out of
the selection path entirely.

## Declared measure and selection

- Measure: the **price gap in GBP/MWh** (accepted minus unaccepted for
  offers; unaccepted minus accepted for bids), in decimal arithmetic —
  the same measure as 001, so the two runs are directly comparable.
- Ranking: largest gap first; ties broken by settlement date, then
  settlement period, then direction, then accepted unit, accepted pair id,
  unaccepted unit, unaccepted pair id (all ascending/lexicographic).
- **The top-ranked surviving candidate is Mystery 002.** No discretion is
  exercised after this point about which case to investigate.
- If **no candidate survives** both screens, that is the result and is
  reported as such (`#hypothesis_not_evaluable` territory under v2) — an
  empty week is a finding, not a failure to be worked around.

Monetary aggregates, if reported, are labelled **naive counterfactual
notional** (arithmetic on public numbers), never a saving, loss or waste.

## Declared reported outputs (not selection)

Recorded whatever the selection turns out to be, so the week's shape is
public even if the headline case is mundane:

1. The **funnel**: raw candidates → after Amendment A → after Amendment B,
   with counts and the share of naive notional removed at each stage.
2. **Comparison with 001's week**: whether the hardened rule changes the
   character of what it surfaces on a week it never saw.
3. **NESO cross-check**: agreement between the surviving set and NESO's
   published in-merit/exclusion data for the window, computed after
   selection, reported without precision/recall language.

## Registered hypothesis (null-explainability form)

No causal hypothesis is registered up front. The registered hypothesis is
the null:

> The apparent price-order inversion selected by this hardened, pre-declared
> procedure can be fully explained from publicly available information.

002 attempts to falsify it. Specific mechanisms become child hypotheses
only as evidence demands, under the same explanation-status protocol as
001 (`investigations/001-largest-apparent-inversion/EXPLANATION-PROTOCOL.md`).

## Known limitations, declared up front

- The comparison remains **whole pairs within one settlement period**; it
  does not model intra-period acceptance timing.
- Amendment A rules out only what public state *proves* undeliverable.
  Dynamics, prior instructions, notice times and constraint location remain
  untested at selection and belong to explanation.
- Amendment B uses `soFlag` as published. An unflagged action is not
  evidence the action was not constraint-related, and a flagged one is not
  proof of a physical constraint; the flag is used as a declared,
  falsifiable screen, not as ground truth.
- DISPTAV volumes are settlement outputs at the pinned vintage and could be
  revised in later runs.
- Sentinel pricing (defensive ±£9,999-style pairs) is still **not**
  excluded by price. Amendment A removes those that cannot deliver; one
  that *can* deliver and is genuinely unaccepted remains a legitimate case.

## Governance (v2)

002 is the first investigation to run under the v2 governed research state
machine (`morpholog/research-v2-draft.morph`), following
`morpholog/V2-LAUNCH-RUNBOOK.md`:

1. Jordan performs the human-only bootstrap (H1–H3a) from his own shell;
   the machine never holds the human credential.
2. The machine opens `inq-002`, records v1 lineage, assigns the reserved
   corpus, declares this protocol's digest and its Decimal parameters.
3. **Jordan seals the protocol.** The seal is the only emitter of
   `DataAcquisitionAuthorised` — the machine may not fetch a single
   artefact of this window before it exists.
4. The machine consumes that intent through the outbox lease, fetches,
   registers evidence idempotently, and consumes the corpus.
5. Analysis reads declared parameters from the governed record
   (`grid_mysteries.governance.declared_parameter`), never from constants
   in code or prose.
6. Publication requires Jordan's approval of the exact rendered digest.

The launch posture is **cooperative-machine**, stated precisely in the
runbook's three-layer threat model: governed-path actor enforcement is
proven; raw-database and acquisition capability security are not provided.
002 does not claim the machine was technically incapable of bypassing the
process — it claims the process is explicit, testable and replayable.

## Framing rules, binding on all outputs

Mechanism, never accusation. No unit or party is characterised as gaming.
Realised cashflows are realised facts; nothing is a saving or waste without
proven substitutability. Observation, interpretation and conclusion stay
separated. The observability boundary is stated wherever a reader could
otherwise assume completeness.

## Amendment protocol

Amendments are legitimate **before acquisition** with honest chronology,
recorded here, and the declaration freezes when acquisition begins. An
amended rule never runs against data that taught the amendment.

## Corrections

Corrections stay here permanently; the declaration above is never silently
rewritten.

## Reproduction

Recorded after selection; nothing above this line is altered afterwards.
