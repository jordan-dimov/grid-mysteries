# Investigation 004 — Britain's Most Expensive Half-Hour

## Status

**Pre-declared.** This document is committed before any June 2026 data
is fetched or inspected. The question is an event, not a methodology:

> **Take the settlement period with the highest published constraint
> cost in an untouched month. Reconstruct, from public data alone, what
> Britain actually did for those thirty minutes — and account for the
> money.**

No thesis. The investigation starts from "Britain spent £X managing
grid constraints in one half-hour; what happened?" and reports whatever
the reconstruction shows, including a boring answer.

**Sequencing**: Investigation 002 opens first, on 2026-08-21, on the
reserved 2026-08-11..17 window, under the v2 governed state machine.
004 does not begin acquisition before 002 has opened.

## Declared window and its exposure inventory

- **Corpus: GB settlement dates 2026-06-01 through 2026-06-30** — the
  most recent full calendar month not consumed by a prior investigation
  (May 2026 is consumed by 003; July 2026 by BESS Study 001;
  2026-08-04..10 by 001's lineage; 2026-08-11..17 is reserved for 002).
- **June is not pristine, and we declare its exposure exactly** rather
  than pretend otherwise:
  1. BESS Study 001 used 2026-06-25/28 MDO/MDB slices for schema
     reconnaissance (declared in that study).
  2. July fetch windows include 2026-06-30 UTC boundary slices (BST
     offset), and one MDO/MDB stream URL spans 2026-06-30T00:00Z
     onwards.
  3. The FY 2026-27 NESO constraint-cost and constraint-breakdown CSVs
     pinned for Investigation 003 **contain June rows**. Every 003
     computation filtered to May; no June row has been analysed, but
     the files are in our possession.
  4. The Ofgem RRT policy paper (June 2026 publication date) is pinned
     reference evidence; it contains no June 2026 market data.
- **The selection input dataset has zero prior exposure**: NESO's
  *Daily Balancing Costs 2026-2027* (settlement-period resolution, cost
  categories including `Constraints`) has never been fetched, read, or
  filtered by this project. Schema was learned on 2026-08-17 from a
  datastore probe returning **April/May 2026 rows only** (fields:
  `SETT_DATE`, `SETT_PERIOD`, `Energy Imbalance`, `Frequency Control`,
  `Positive Reserve`, `Constraints`, `Negative Reserve`, `Other`). No
  June row has been seen.
- No selection rule in this project has ever been trained on, amended
  by, or run against June 2026 data.

## Declared selection

**The selected case is the (settlement date, settlement period) in the
June window with the highest `Constraints` value in the pinned vintage
of NESO's Daily Balancing Costs 2026-2027.** Ties break by earlier
settlement date, then lower settlement period number. No discretion is
exercised after this point. Values are parsed as `Decimal`; the pinned
vintage is whatever NESO publishes at acquisition time, fetched
journalled and immutable before any June row is read. If the winning
period appears in NESO's "Missing Settlement Periods" companion
resource, that fact is reported alongside the selection, which stands
as published.

## Declared observability boundaries (stated before acquisition, so
they cannot become corrections)

1. **The category split is NESO's own attribution.** The per-period
   `Constraints` figure comes from NESO's internal assignment of
   balancing actions to cost categories; the mapping from individual
   acceptances to categories is not public. The reconstruction can show
   every acceptance and cashflow in the half-hour; it **cannot say
   which of them NESO counted inside the `Constraints` number**, and
   will not pretend to. Any decomposition we publish is of *published
   per-unit cashflows*, presented alongside — never equated with —
   NESO's category total. (Investigation 003's lesson, applied at
   declaration time.)
2. **No authoritative unit-to-constraint-boundary mapping exists
   publicly** (003, evidenced). Locational statements will use tiered,
   clearly-labelled context (GSP groups from the BM-unit reference,
   published network diagrams, CMIS tags where applicable), never
   asserted attribution.
3. **Intraday/wholesale positions, PN revision history, and
   control-room reasoning are not public** (003, probed and evidenced
   for PN history). Named where relevant; never inferred.
4. SO-flags are reported as published; an unflagged acceptance is not
   evidence the action was not constraint-related, and a flagged one is
   not evidence of cost category membership.

## Registered hypothesis (null-explainability form)

> The half-hour's publicly observable state — schedules, acceptances,
> flags, per-unit indicative cashflows, generation and interconnector
> context — can be reconstructed coherently from public data, and every
> major action in it is consistent with the visible system context,
> without requiring non-public information to explain *at the level of
> mechanism*. Where the published `Constraints` total cannot be
> decomposed from public data, that gap is itself a declared finding,
> not a failure of the hypothesis.

## Declared reconstruction outputs

For the selected half-hour, plus a declared context margin of the same
settlement day: every BOALF acceptance touching the period (direction,
levels, flags, acceptance times); per-unit published indicative BM
cashflows (EBOCF, BSC semantics, labelled as in 003); final PNs and
MELS/MILS for instructed units; fuel-mix and interconnector context;
wind-unit curtailment identification; day-ahead constraint-flow
forecast context (context only, per 003); storage behaviour in the
period; and the published cost-category row itself. Actual metered
generation (B1610/actual per-unit output) is a declared candidate
input for checking that instructed units physically responded, subject
to its availability for the period at acquisition time.

Three-column discipline throughout (observed / supported inference /
not publicly observable), as in 003. Realised facts only; no
counterfactual "should have cost" claims; "most expensive" means
highest published `Constraints` category value, nothing more.

## Framing rules, binding on all outputs

Mechanism, never accusation. No unit or party is characterised as
"gaming". The half-hour is reconstructed as a system event, not a
search for a villain. If the answer is mundane (one plant trip, one
boundary, entirely orthodox actions), the mundane answer is the
publication.

## Amendment protocol

Amendments follow 003's precedent: legitimate before acquisition with
honest chronology, recorded in this section, and the declaration
freezes when acquisition begins. An amended rule never runs against
data that taught the amendment.
