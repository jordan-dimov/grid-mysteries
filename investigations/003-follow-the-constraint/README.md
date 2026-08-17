# Investigation 003 — Follow the Constraint

## Status

**Pre-declared.** This document is committed before any data from the
declared window is fetched. The question is mechanism, not misconduct:

> **Can the publicly observable signature associated with repetitive
> re-trading be reconstructed across a full published constraint-cost
> episode — and how much of the proposed causal mechanism can public
> data actually prove?**

Ofgem has identified "repetitive re-trading" by storage behind
transmission constraints as a material system cost (~£90m/year). The
behaviour can be individually rational and collectively expensive at
once. This investigation does not ask whether anyone is "gaming" —
it selects one episode by a pre-declared rule and shows exactly how the
machine works, with the unobservable parts named as such.

## Declared window and corpus

- **Corpus: GB settlement dates 2026-05-01 through 2026-05-31** — chosen
  by chronology as the most recent calendar month with **zero prior
  project exposure** (July is consumed by BESS Study 001; 2026-08-04..10
  by Investigation 001's lineage; 2026-08-11..17 is reserved untouched
  for Investigation 002). Feasibility reconnaissance used only dataset
  schemas and non-May slices (a 2023 constraint-flows sample; June/August
  probes from earlier studies).
- To be pinned after this commit (journalled, immutable): NESO Day Ahead
  Constraint Flows and Limits (half-hourly, per constraint group), NESO
  constraint cost/volume breakdowns at the finest published granularity,
  NESO Skip Rates for May (fuel classification and context), Elexon
  BOALF, BOD, DISPTAV (both directions) and PN per settlement period,
  and the pinned BM-unit reference vintage.

## Declared definitions

- **Storage unit**: a unit classified `BATTERY` (or pumped storage where
  separately classified) in NESO's May Skip Rates fuel field — the
  operator's own classification, not ours. The classification source is
  pinned before use.
- **Published constraint-cost episode**: for a constraint group, a
  maximal run of consecutive settlement dates on which NESO's published
  outturn constraint cost/volume for that group is non-zero (money
  actually spent). The half-hourly Flow-vs-Limit dataset is **day-ahead
  forecast context** — NESO states it does not reflect subsequent
  changes — and is used as context only, never as evidence that the
  boundary was physically binding in a given half hour.
- **Repeat-curtailment cycle** (the RRT-*consistent* public signature):
  within one episode, a storage unit that (a) is bid down via an
  acceptance in settlement period t, (b) subsequently presents a final
  FPN scheduling export again in a later period of the same episode, and
  (c) is bid down again. Each additional (b)+(c) after the first
  bid-down is one cycle. **This proves repeated curtailment of
  re-presented schedules; it does not and cannot prove the intervening
  intraday re-trade** — a unit whose pre-existing schedule already
  exported in consecutive periods produces the identical public
  signature with no new trade. Final FPNs only; intra-period revision
  history is not public. Ofgem's causal mechanism is
  A (curtailment) → B (intraday re-sale) → C (curtailment again);
  public data observes A and C. Establishing what can and cannot be said
  about B is part of the investigation's output, not an assumption.
- **Episode repeat-curtailment score**: total repeat-curtailment cycles
  across storage units in the episode.

## Declared selection

**The selected case is the episode with the highest repeat-curtailment
score in the window.** Ties break by: greater total storage bid-down volume (MWh),
then earlier episode start, then constraint-group name. No discretion is
exercised after this point. If no episode has a positive score, that
is the result (`#hypothesis_not_evaluable` territory, honestly reported).

## Registered hypothesis (null-explainability form)

> The full sequence of publicly observable actions in the selected
> episode — storage bid-downs and re-presentations, wind curtailment,
> and replacement-energy acceptances — can be reconstructed and its
> realised cashflows accounted for from public data, with each apparently
> perverse step explained by the incentives and constraints visible at
> the time.

## The three-column discipline

Every reconstructed step is classified as exactly one of:

- **Observed** — directly in pinned public data;
- **Supported inference** — follows from observed data under a stated,
  falsifiable assumption, with the assumption named at the point of use;
- **Not publicly observable** — e.g. intraday/wholesale re-trades,
  private positions, control-room reasoning. Named, never inferred.

## Declared reconstruction outputs

For the selected episode: a period-by-period timeline (day-ahead
flow/limit context, storage FPNs and acceptances with acceptance timestamps,
curtailment actions, replacement offers); realised cashflow accounting
per actor class from DISPTAV volumes × BOD prices (**realised facts
only** — counterfactual "could a different sequence have cost less" is
explicitly out of scope for this investigation and reserved as a
declared follow-on, because substitutability would have to be proven
first); the observability boundary (intraday/wholesale re-trades,
private positions, control-room reasoning — all named, none inferred);
mechanism statuses per the Investigation 001 explanation protocol.

Multi-period reconstruction logic is built as tested modules in
`src/grid_mysteries/investigations/` (episodes, timelines, cycles) — the
first components of a reusable event-replay capability.

## Framing rules, binding on all outputs

Mechanism, never accusation. No unit or party is characterised as
"gaming"; individually-rational behaviour is described as such. Realised
cashflows are realised facts; nothing is a "waste" or "saving" without
proven substitutability. The observability boundary is stated wherever a
reader could otherwise assume completeness.

## Amendments before acquisition

1. **2026-08-17, before any May data was fetched.** The original
   declaration named the selector an "RRT score" and framed the episode
   "from first binding to final release". Both committed the exact error
   this project exists to expose: upgrading a mechanism-consistent
   signature into evidence of the mechanism. Renamed to
   **repeat-curtailment score** (RRT-*consistent*), with the A → ? → C
   observability structure made explicit (public data observes the
   curtailments, not the intervening intraday re-sale); episodes renamed
   **published constraint-cost episodes**; Flow-vs-Limit reclassified as
   day-ahead forecast context, never outturn binding evidence. The
   selection rule is otherwise identical. The registered hypothesis
   (`hyp-003-episode-reconstructable`) is unaffected: it claims
   reconstruction and accounting of *publicly observable* actions only.
