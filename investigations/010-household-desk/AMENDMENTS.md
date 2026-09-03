# 010 — amendments to the frozen declaration

Each entry is dated and states whether any data had been fetched.

## Amendment 1 — 2026-09-03, before any fetch: the inverter's time is shared within a slot

**What the declaration said.** The schedule is the exact optimum subject
to "charge power ≤ min(inverter, import limit), discharge power ≤
min(inverter, export limit)" and the storage constraints.

**What was wrong with it.** Those two bounds are independent, so the model
could import at full inverter power *and* export at full inverter power in
the same half-hour: 10 kWh in and 9 kWh out of a 20 kW inverter in thirty
minutes. No single inverter can do that. On a pair whose export price
exceeds its import price in some half-hours (a cheap overnight import with
Agile Outgoing, for example) the relaxation would have manufactured a
grid-to-grid pass-through at twice the physically possible rate and
flattered exactly the cross-tariff cases the investigation tests. Found by
a unit test on a one-slot day while building the model; no tariff data had
been requested.

**The amended constraint set**, per slot of `h` hours, in stored kWh:
grid import `c ≤ min(inverter, import limit) · h`; free energy `f ≤` the
slot's free allowance; release `d ≤ export limit · h / η` (the export
limit applies to delivered kWh); **`c + f + d ≤ inverter · h`** (the
inverter bounds battery-side power and its time is shared between
charging and discharging); stored balance in `[0, capacity]` at every
boundary and zero at both ends of the day. Within a slot the model is the
fluid limit — the inverter may alternate direction, so only the slot's
totals and the boundary balances are constrained, and a slot may release
energy it took in earlier in the same slot. Consequences the reader should
know: a 20 kW inverter at 90 % round trip delivers at most 18 kW; a
half-hour may legitimately spend part of its time charging and part
discharging, so a same-slot buy-and-sell is allowed at half rate rather
than forbidden.

**Solver.** The min-cost-flow formulation cannot express the shared time
budget (a grid-to-grid pass-through must spend the slot's time twice), so
the day is solved by exact dynamic programming over the stored balance
with piecewise-linear concave value functions, in exact rational
arithmetic, Decimal at the money boundary. Tests check that the recovered
schedule satisfies every constraint above and reproduces the optimum, and
that it matches a brute-force enumeration on a small instance.

Nothing else in the declaration changes: information set, day boundary,
cases, bars and falsifiers stand as frozen.
