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
generation (B1610, settlement-period metered energy in MWh) is a
declared candidate input for **checking whether settlement-period
metered output is consistent with the instructed response** — it
cannot prove that a unit followed a particular acceptance at a
particular minute, and will not be presented as doing so; subject to
its availability for the period at acquisition time.

Two further observed-money layers are declared, so that any non-BM
component of the half-hour's cost is visible by design rather than
discovered as a residual:

- **Disaggregated BSAD** (NESO, 2026-27; settlement-period adjustment
  cost, volume, and `TradeFlag` where `T` = system and `F` = energy):
  all adjustments touching the selected period are reported. The
  `TradeFlag` is contextual evidence only — `T` means "system issue
  such as a constraint" and is **not** treated as membership of NESO's
  `Constraints` category, nor as attribution to any physical boundary.
- **Daily Balancing Volume** (NESO, 2026-27; settlement-period MWh by
  category, including `Constraint Offers (MWh)` and
  `Constraint Bids (MWh)`): gives the selected £ figure a published
  physical scale, presented alongside it — never as a unit-level
  decomposition of it.

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

## Amendments before acquisition

1. **2026-08-18, before any June data was fetched; no June row of any
   dataset named here has been seen.** Two changes. **(a)** The B1610
   wording overclaimed: B1610 is settlement-period metered energy
   (MWh), not instantaneous output, so it can show *consistency with*
   an instructed response, never *proof of* minute-level compliance;
   the declared output is reworded accordingly. **(b)** Two
   observed-money layers added — Disaggregated BSAD (adjustment cost,
   volume, system/energy `TradeFlag`) and Daily Balancing Volume
   (per-period category MWh, including constraint offers/bids) — so
   that any non-BM component of the winning half-hour's cost is
   declared visible up front rather than surfacing as an unexplained
   residual after selection. Both schemas were verified on 2026-08-18
   against **April 2026 rows only**. Neither dataset changes the
   selection rule, which is untouched. **The declaration is now
   frozen.**

---

# Results

Everything below this line was written after the selection ran. Nothing
above it has been altered.

## Selection result

Jordan sealed the protocol at 2026-08-22 22:57 (attested `gm_human`);
the fetcher verified that seal before its first request. Acquisition was
two-phase: three small NESO CSVs, then — only after the rule had run —
the deep record for one settlement day (336 per-period artefacts plus
EBOCF, B1610, FUELINST, SYSWARN).

The frozen rule ran offline over **1,436** June settlement periods, all
of which carry a published `Constraints` value:

> **Selected: 2026-06-24, settlement period 42 (20:30–21:00 BST).
> Published `Constraints` £1,176,150.**

Every other published category for that half-hour is zero or negative
(Other −£28,331, Energy Imbalance −£19,229, Negative Reserve −£18,006,
Frequency Control −£409, Positive Reserve £0). **NESO's published
balancing-cost attribution for the half-hour is overwhelmingly dominated
by the `Constraints` category** — which is a statement about NESO's
attribution, not about causation.

Four June periods are absent from the published series (21 June p22/p23,
23 June p8/p9); the winner is not among them, so the declared "Missing
Settlement Periods" caveat does not apply.

## It is not a spike

The rule picked the peak of a sustained evening episode. The **four most
expensive half-hours in the entire month are consecutive, all on 24
June**:

| period | BST | published `Constraints` |
|---|---|---:|
| p36 | 17:30–18:00 | £230,461 |
| p37 | 18:00–18:30 | £503,263 |
| p38 | 18:30–19:00 | £495,484 |
| **p39** | 19:00–19:30 | **£1,006,177** |
| **p40** | 19:30–20:00 | **£987,633** |
| **p41** | 20:00–20:30 | **£1,170,915** |
| **p42** | 20:30–21:00 | **£1,176,150** ← selected |
| p43 | 21:00–21:30 | £703,409 |
| p44 | 21:30–22:00 | £681,400 |
| p45 | 22:00–22:30 | £372,711 |

p39–p42 alone total **£4.34m**; the p36–p45 shoulder is **£7.33m**. The
selected half-hour is 12× the median June half-hour and 0.53% of the
month's £223.9m in thirty minutes.

## The money is not in the Balancing Mechanism

The four declared accounting layers, kept separate and never reconciled
to one another (`evidence/episode-diagnostic.json`), for p42:

| layer | |
|---|---|
| **1** NESO published `Constraints` | **+£1,176,150** |
| **2** Balancing Mechanism | 1,085 MWh of accepted **bids** across **113 units**; ~**zero** accepted offers; net published indicative cashflow **−£155,861** |
| **3** non-BM adjustments (Disaggregated BSAD) | **+£1,277,241** over 1,173 MWh = **£1,089/MWh**; **all** flagged `F` (Energy), system-flagged `T` exactly zero |
| **4** NESO published volumes | **0** constraint offers, −589 MWh constraint bids |

Inside the Balancing Mechanism the system operator was, on published
indicative cashflows, **receiving** money — units paying to be turned
down. The cost sat in replacement energy bought **outside** the
mechanism. Layer 3 tracks layer 1 period by period across the episode
and exceeds it by ~£101k at p42. **Whether NESO computes its
`Constraints` figure from those rows is not public and is not asserted
here** — the declaration said layer 1 could not be decomposed, and it
cannot.

Across the whole day, non-BM adjustments total **£9,194,144** over
10,278 MWh, and NESO attributes **£8,228,649** of the day to
`Constraints`.

## Diffuse, not concentrated

**113 units** carry the accepted energy at p42; the top five are 35% of
it, falling to 18–20% at p43/p44. This is the visible peak of a
whole-system rearrangement, not a handful of extraordinary decisions.
The bid-down fuel mix rotates through the episode — CCGT-led at p36,
pumped storage and unclassified aggregator units through the peak, wind
climbing to 226 MWh by p43. The largest single units at p42 are
Dinorwig and Foyers (pumped storage), then aggregators, then Scottish
offshore wind.

## What the system was doing (pinned primary context)

From `FUELINST`, comparing the episode (p36–p45) with midday (p24–p26):

- **CCGT rose from 9,775 MW to 15,799 MW (+6,024 MW), 51% of episode
  generation.**
- Pumped storage swung from −1,026 MW (pumping) to +907 MW (generating),
  a 1,933 MW turnaround.
- Interconnectors totalled 2,938 MW, 9% of generation — and several
  moved *against* import: Viking −2,248 MW versus midday, Nemo
  −1,043 MW, BritNed −479 MW, while Ireland swung +536 MW.

## The Electricity Margin Notice — primary evidence

`SYSWARN` carries NESO Control Centre's own notices
(`data/raw/elexon/2026-06-24/syswarn.json`, pinned post-selection):

- **2026-06-23 21:04** — ELECTRICITY MARGIN NOTICE **for 19:00–22:00 on
  24/06/2026**. "There is a reduced system margin. **System margin
  shortfall 1900 MW**… **1300 MW of generation is excluded from the
  available system margin due to system constraints.**"
- **2026-06-24 07:10** — reissued, shortfall revised to **1450 MW**,
  with **1250 MW excluded due to system constraints**.
- **2026-06-24 13:20** — cancellation.

**The EMN window 19:00–22:00 BST is settlement periods 39–44. The
mechanically selected p42 sits inside it, and so do all four of the
month's most expensive half-hours.** The rule found the peak of the
warned period without any knowledge of the warning.

And the notice resolves what would otherwise look like a contradiction —
a *margin* event whose cost NESO books under *`Constraints`*. NESO's own
text says both at once: the margin was short **because** 1,250–1,300 MW
of generation was excluded **by system constraints**. That is most of
the 1,450–1,900 MW shortfall.

## Secondary reporting, held separately and treated as provisional

Contemporary press coverage (not pinned, not evidence here) describes a
record June heatwave, ~£1,400/MWh paid for interconnector imports, ~1.7
GW secured, CCGT unplanned outages ~40% above normal, and a UK June
temperature record on 24 June. Two of its figures are independently
confirmed by our pinned primary data — the **1,900 MW** shortfall (exact
match to the first EMN) and **~£9.1m of trades** (£9,194,144 measured,
a 1% match). Others we cannot check and do not assert.

**Ofgem has commissioned a NESO post-event review of the June heat event
under Licence Condition C7.5, plus an independent investigation into
allegations about control-room record-keeping.** The public account of
this week is therefore *provisional*, and nothing in this investigation
depends on it: every claim above rests on pinned published data.
