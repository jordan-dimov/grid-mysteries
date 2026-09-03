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

## Amendment 2 — 2026-09-03, after the sealed run, before any result was written up: slots are sliced to the settlement grid

**What the declaration said.** "Slots are the union of both series'
boundaries within the day."

**What was wrong with it.** A fixed schedule (Octopus Go: two rates a day;
Flux export: three) meets a half-hourly series only at its own few
boundaries, so a Go ↔ Flux day had seven slots, one of them ten and a half
hours long. Two consequences: the free-energy rule ("spread over daylight
slots by duration") put a whole day's solar into the single slot starting
inside 09:00–17:00, which at 20 kW was the 16:00–19:00 export slot whose
inverter budget was already spent — so the sweep in case 5 showed free
energy having **no effect at all** at 20 kW; and the inverter budget itself
was enforced over multi-hour spans, which is coarser than the model
intends. Found while reading `evidence/results.json` (case 5, every 20 kW
row identical across the sweep); traced on 2026-06-24, region C, Go ↔
Flux export, where the day had 7 slots and zero free energy was used.

**The amendment.** Slot boundaries are the union of both series'
boundaries **and the half-hour settlement grid** from the day's start
(`RESOLUTION = 30 min`; a later five-minute source passes its own). Rule
id becomes `010/per-day-optimum/v2`. This can only raise an optimum: every
schedule on the coarse grid is feasible on the fine one. Nothing about
information set, bars, cases or falsifiers changes.

**Record.** The pre-amendment evaluation is preserved byte for byte as
`evidence/results-PRE-AMENDMENT-2.json`; `evidence/results.json` is the
re-evaluation on the same pinned data (no fetch). `RESULTS.md` reports the
post-amendment numbers and names any case whose reading changes.
