# Investigation 003 — Follow the Constraint

## Status

**Pre-declared.** This document is committed before any data from the
declared window is fetched. The question is mechanism, not misconduct:

> **Can we reconstruct one entire constraint episode and account for
> every publicly observable pound of its storage, curtailment and
> replacement-energy economics — from first binding to final release?**

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
- **Congestion episode**: for a constraint group, a maximal run of
  consecutive settlement dates on which NESO's published constraint
  cost/volume for that group is non-zero (money actually spent — outturn
  binding, not forecast). Day-ahead flows/limits provide the intra-episode
  half-hourly timeline but do not define the episode.
- **Re-trade cycle** (the publicly observable unit of RRT): within one
  episode, a storage unit that (a) is bid down via an acceptance in
  settlement period t, (b) subsequently presents a final FPN scheduling
  export again in a later period of the same episode, and (c) is bid
  down again. Each additional (b)+(c) after the first bid-down is one
  cycle. Final FPNs only — intra-period revision history is not public,
  and this is recorded as a declared observability limit.
- **Episode RRT score**: total re-trade cycles across storage units in
  the episode.

## Declared selection

**The selected case is the episode with the highest RRT score in the
window.** Ties break by: greater total storage bid-down volume (MWh),
then earlier episode start, then constraint-group name. No discretion is
exercised after this point. If no episode has a positive RRT score, that
is the result (`#hypothesis_not_evaluable` territory, honestly reported).

## Registered hypothesis (null-explainability form)

> The full sequence of publicly observable actions in the selected
> episode — storage bid-downs and re-presentations, wind curtailment,
> and replacement-energy acceptances — can be reconstructed and its
> realised cashflows accounted for from public data, with each apparently
> perverse step explained by the incentives and constraints visible at
> the time.

## Declared reconstruction outputs

For the selected episode: a period-by-period timeline (constraint
flow/limit, storage FPNs and acceptances with acceptance timestamps,
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
