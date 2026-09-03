# 010 — the household desk: declaration

**Frozen**: 2026-09-03, before any request to the Octopus Energy public
tariff API, Elexon, or any rules document for this question has been made
from this repository. Sealed by the commit that adds this file; its
SHA-256 is recorded in `RESULTS.md` when the run happens. Results go in
`RESULTS.md`; amendments, if any, in `AMENDMENTS.md`, dated. Acquisition
waits for the human seal (see *Acquisition gate*).

## Trigger and observations under test

Bloomberg, 2026-09-03, "Almost Anyone Can Make Money Selling Electricity
With AI and Batteries" (Rathi and Rudgard). The article's load-bearing
claims are the **observations**; each is a self-report relayed by a
journalist and is treated as such:

- **O1** Andrew Austin, Shropshire: 200 kWh home battery; charges from the
  grid by day on Octopus's half-hourly prices (published 16:00 daily);
  exported 16:00–21:00 on 2026-06-24 for £60; says the strategy makes about
  £400 a month in summer and £300 a month in winter *after his own
  consumption*.
- **O2** Aaron Wilkes, Kent: heat pump, battery and two EVs run by an AI
  agent; export payouts under about £10 a month; "Octopus caps his import
  at about £1/kWh"; his DNO quoted tens of thousands of pounds for the
  upgrade a bigger battery would need.
- Mark Purcell (Queensland, Amber) and Greg Robinson (Arizona, a US VPP)
  are **out of scope** for this run.

The article is not itself evidence about the electricity system; it is the
source of the claims. A copy is pinned under `data/raw/press/` at
acquisition if the sponsor supplies the URL or a saved copy; otherwise the
quotations above, transcribed by the sponsor on 2026-09-03, stand as the
record of what was claimed.

## The mystery

> How does a 200 kWh home battery make £400 a month on Octopus's
> half-hourly prices, when charging and discharging on those same prices
> nets roughly nothing?

## Prior exposure (recorded, not hidden)

On 2026-09-03, before this declaration, a scratch reconstruction was run
in **another repository** against the Octopus public tariff API: products
`AGILE-24-10-01` and `AGILE-OUTGOING-19-05-13`, tariff codes
`E-1R-<product>-C`, region **C only**, **June–August 2026**, a daily greedy
selection, 20 kW, 90 % round trip. It reported: grid-to-grid Agile cycling
at roughly zero over the summer; the reported earnings reconstructing only
on a cross-tariff pair (an Intelligent Octopus Go overnight import with
Agile Outgoing peak export, or Flux); and the 2026-06-24 £60 matching about
200 kWh of gross export at a ~30 p/kWh average export rate.

Consequences, fixed now:

1. Those three statements are **hypotheses with a known author** (H-gross,
   H-pair, H-agile-zero below), not findings. Nothing from that repository
   is copied here; every number is reproduced from artefacts pinned under
   this declaration or it does not appear.
2. **Region C, summer 2026, Agile ↔ Agile Outgoing is exposed.** Its result
   here is a *replication*, labelled as such in `RESULTS.md`. The
   **untouched tests** are: regions E and J; the winter window; every pair
   other than Agile ↔ Agile Outgoing; the export-limit and solar readings.
3. The day-selection rule declared below (an exact per-day optimum) differs
   from the scratch rule (greedy). The change was made for defensibility —
   an optimum upper-bounds every greedy, so a near-zero result cannot be
   blamed on a weak heuristic — and not because of anything the exposed
   window showed. It is stated here so that the reader can judge that.

## What this never claims

Nothing here says what tariff Mr Austin or Mr Wilkes is on, what their
inverters, connections or solar arrays are, or what they actually earned.
The investigation tests **arithmetic feasibility**: which combinations of
published tariff, connection limit and free energy make the reported
figures reproducible from public prices, and which do not. A backtest
figure is a **counterfactual under stated assumptions**, never a saving,
loss, or "what he made". Self-consumption is not modelled: the model is
the battery's grid-facing trades only, so "after his own consumption" is
read as "the export-minus-import figure attributed to the battery", the
most generous reading for the claim.

## Data (all fetched only after the seal, all pinned)

### Octopus Energy public tariff API (no key)

Base `https://api.octopus.energy/v1`. Pinned in this order:

1. `GET /products/` (every page) — the products index, so that a declared
   code found absent is recorded as *unavailable* rather than guessed
   around.
2. `GET /products/<code>/` for each declared product — the product
   document, which names the per-region tariff codes. The expected form is
   `E-1R-<product>-<region>`; the pinned document, not the expectation,
   decides. A mismatch is recorded in `AMENDMENTS.md` and the pinned code
   is used.
3. `GET /products/<code>/electricity-tariffs/<tariff>/standard-unit-rates/`
   and `.../standing-charges/`, `page_size=1500`, every page, for each
   (product, region, window) below. Fields read: `valid_from`, `valid_to`,
   `value_exc_vat`, `value_inc_vat`, `payment_method`. Any other schema
   stops the run.

**Products** (import): `AGILE-24-10-01` (Agile Octopus), `GO-VAR-22-10-14`
(Octopus Go), `INTELLI-VAR-22-10-14` (Intelligent Octopus Go — added to the
sponsor's list because H-pair names it and cannot be tested without it;
if the products index does not carry it the pair is *not testable* and is
recorded so), `FLUX-IMPORT-23-02-14`, `INTELLI-FLUX-IMPORT-23-07-14`.
**Products** (export): `AGILE-OUTGOING-19-05-13`, `OUTGOING-VAR-24-10-26`,
`OUTGOING-PRIME-FIX-12M-26-06-23`, `FLUX-EXPORT-23-02-14`. Intelligent
Flux export, if its product document names a separate export code, is
pinned from that document.

**Regions**: **C** (London — the project's own patch, headline case),
**E** (West Midlands — Shropshire, O1), **J** (South East — Kent, O2).

**Windows** (requested in UTC, wide enough to cover the local days):
- Summer: local 2026-06-01 00:00 → 2026-09-01 00:00
  (`period_from=2026-05-31T21:00Z`, `period_to=2026-09-01T00:00Z`).
- 2026-06-24 in full: the Agile day 2026-06-23 23:00 → 2026-06-24 23:00
  local *and* the calendar day, both inside the summer window.
- Winter: local 2026-01-01 00:00 → 2026-03-01 00:00
  (`period_from=2025-12-31T22:00Z`, `period_to=2026-03-01T00:00Z`).

**VAT**: import prices are read **inclusive of VAT** (`value_inc_vat`,
domestic 5 %); export payments carry no VAT for a domestic customer and
are read from `value_exc_vat`, with `value_inc_vat == value_exc_vat`
asserted on every export row. Standing charges are pinned and reported;
they are not marginal to the battery and enter no backtest figure.

### Elexon Insights (adapter already in `sources/elexon.py`)

For every local day in both windows: the Market Index Data stream
(`/datasets/MID/stream`, both index providers) and settlement system
prices (`/balancing/settlement/system-prices/<date>`). Purpose: to show
the wholesale layer beneath Agile in the same half-hours. Limit declared
now: Agile's published input is the N2EX day-ahead hourly auction, which
Elexon does not carry; MID is the nearest Elexon wholesale reference and
is shown alongside, never substituted into the formula. No backtest
figure depends on Elexon data.

### Primary-source rules documents (pinned as HTML/PDF, not guessed)

- Octopus: the Agile Octopus tariff page and Octopus's own Agile pricing
  explanation (the formula and the **100 p/kWh import cap**, O2's
  "about £1/kWh"); the Outgoing Octopus, Octopus Go, Intelligent Octopus
  Go and Octopus Flux pages and terms, for **which import and export
  products may be paired** (H-pair depends on this and it is not assumed).
- ENA Engineering Recommendations **G98** and **G99** (via the Distribution
  Code / ENA library): the per-phase export threshold under G98 (expected
  16 A/phase ≈ 3.68 kW single-phase, 11.04 kW three-phase) above which a
  G99 application is needed. The pinned document decides the figure.
- HMRC VAT Notice 701/19 (fuel and power) for the 5 % domestic rate.

URLs are recorded in the manifest at fetch. If a page has moved, the
site's current equivalent is pinned and the substitution noted in
`AMENDMENTS.md`; content is never taken from memory.

## Explanations to test, each with what settles it

| id | explanation | settled by |
|---|---|---|
| **H-gross** | The reported figures are gross export receipts, not net of import cost | The 2026-06-24 reconstruction: gross export 16:00–21:00 versus net after the day's charging cost, at the published prices |
| **H-pair** | The arithmetic needs a cross-tariff pair: a cheap fixed overnight import (Go / Intelligent Go / Flux) with Agile Outgoing or Flux export | Backtest of every declared pair; the pairing-rules documents say which pairs the retailer permits |
| **H-solar** | Part of the exported energy is free (solar) | The free-energy sweep: how many kWh/day at zero cost are needed to reach £400 net on the best permitted pair |
| **H-export-limit** | The export connection, not the software, bounds earnings | The same pairs at 3.68 kW (G98 single-phase), 11.04 kW (G98 three-phase) and 20 kW (a G99 connection) |
| **H-region** | Regional prices change the answer | C, E and J side by side |
| **H-rules** | Pairing rules and the 100 p import cap shape what is achievable | The pinned Octopus documents; the cap's incidence in the pinned import series |
| **H-wedge** | VAT and network charges are the import–export wedge that kills grid-to-grid cycling | Import inc-VAT versus export in the same half-hours, and MID beneath both |
| **H-degradation** | Throughput cost erases the residual | The degradation sensitivity |
| **H-agile-zero** | Grid-to-grid Agile ↔ Agile Outgoing nets roughly nothing | The headline backtest in all three regions and both windows |

## The model (fixed now; code in `src/grid_mysteries/investigations/household_desk.py`)

A pure tariff-pair backtest. Inputs: battery capacity (kWh), inverter (kW),
export limit (kW), optional import limit (kW), round-trip efficiency,
degradation cost (p per kWh delivered to the grid), free energy per day
(kWh, at zero energy cost, available 09:00–17:00 local, same loss
applied), import series, export series, window. All money in `Decimal`
pence; results reported in pounds to the penny.

**Tariff interface.** A tariff is a sorted list of rates, each an interval
`[valid_from, valid_to)` with a pence-per-kWh price and a `published_at`
timestamp: the moment the household could know it. Intervals of any
length are accepted, so a five-minute wholesale pass-through (Amber) or an
EPEX-indexed continental tariff can be added as a source later without
touching the model. Those sources are **not built** in this run.

**Information set and day rule.** The decision day is the Agile day:
23:00 local to 23:00 local. Its prices are published at about 16:00 local
on the day it starts, so a household on Agile genuinely knows the whole
day's import and export prices when it decides; using them is not
foresight and is not a cheat. The source stamps every Agile rate
`published_at` = 16:00 local on the calendar day of the 23:00 that starts
its Agile day; fixed time-of-use tariffs are known indefinitely. A rate
with `published_at` later than the decision time is not usable.

**Schedule.** For each decision day the schedule is the **exact optimum**
of the day's trades: choose charge and discharge energy per slot to
maximise export revenue minus import cost minus degradation, subject to
charge power ≤ min(inverter, import limit), discharge power ≤
min(inverter, export limit), stored energy between 0 and capacity at
every slot boundary, energy exported in a slot present in storage at the
slot's start (so no same-slot round trip and no selling before buying),
and stored energy **zero at both ends of the day**. Solved as a min-cost
flow on the day's slot boundaries (successive shortest paths), which is
exact for this linear problem. Losses are applied on discharge: one
stored kWh delivers η kWh. Because it is an optimum over the household's
true information set, it **upper-bounds** any daily heuristic, including
the household's software; a result near zero therefore cannot be
attributed to a weak strategy. Where a result *does* reproduce the claim,
the optimum overstates what an agent achieves, and that is said.

**Missing data.** Slots are the union of both series' boundaries within
the day. A decision day with any slot lacking an import or export price
is dropped and counted; the count is reported. A month with fewer than 25
scored days is reported as *incomplete* and is not compared against a bar.

**JSON contract.** `backtest_json(request, import_rates, export_rates)`
takes `{battery_kwh, inverter_kw, export_limit_kw, import_limit_kw?,
round_trip_efficiency, degradation_p_per_kwh, free_energy_kwh_per_day?,
import_tariff:{product, region}, export_tariff:{product, region},
window:{from, to}}` and returns monthly and window totals of imported
kWh, exported kWh, free kWh used, gross export receipts, import cost,
degradation cost and net, the average captured prices, scored and dropped
day counts, and the echoed assumptions. It is the one function a public
page elsewhere may call with a household's own parameters.

## Declared cases (the whole grid is run; nothing is added after)

Common: 200 kWh, 20 kW inverter, η = 0.90, degradation 0 unless stated.

1. **Headline** — Agile ↔ Agile Outgoing; export limit 20 kW; regions C
   (replication), E, J; summer and winter.
2. **Export limit** — case 1 at 3.68 kW and 11.04 kW.
3. **Pairs** — each declared export product with each declared import
   product, regions C, E, J, summer and winter, export limits 20 kW and
   3.68 kW. Permitted versus not-permitted pairs are labelled from the
   pinned rules documents *after* the backtest is computed; the backtest
   itself is run for every pair.
4. **Degradation** — cases 1 and the best permitted pair at 2 p and 5 p per
   kWh delivered (an assumption range, roughly £300/kWh of cells over
   6,000 cycles; not a measured figure).
5. **Solar** — the best permitted pair, summer, at export limits 3.68 kW
   and 20 kW, with free energy 0, 10, 20, 30, 40, 60, 80, 100 kWh/day.
6. **2026-06-24** — for every pair and region E: gross export receipts
   16:00–21:00 local from 200 kWh at 20 kW and from 3.68 kW; the day's
   optimum net; the average export price over those ten half-hours.
7. **Wedge** — for region E, summer: the distribution of (import inc VAT −
   export) in the same half-hour on Agile ↔ Agile Outgoing; the share of
   import half-hours at the 100 p cap; MID and system price beneath.

## Target conclusion, written now to be defended or narrowed

> The reported earnings are gross export receipts on a retailer-granted
> cross-tariff spread; grid-to-grid arbitrage on Agile nets roughly zero
> over summer 2026; the export connection, not the software, bounds what
> a household can earn.

Each clause is scored separately.

**Bars** (monthly net = the model's window net divided by scored months):

- *"Nets roughly zero"* holds if the headline case's monthly net is below
  **£50** in every region for the summer window (an eighth of the claim);
  it is **refuted** if any region reaches **£200**; between, indeterminate.
- *"Gross, not net"* holds if the 2026-06-24 gross export at 20 kW from
  200 kWh lies within **£45–£75** of the reported £60 while the day's net
  on Agile ↔ Agile Outgoing is below **£20**.
- *"Cross-tariff spread"* holds if at least one **permitted** pair reaches
  **£300/month** at 20 kW in summer while no Agile ↔ Agile Outgoing case
  does.
- *"Connection bounds it"* holds if every permitted pair at 3.68 kW falls
  below **£150/month** while the same pair at 20 kW reaches £300.

## Falsifiers (published with the claim)

The conclusion is **wrong** if either holds:

- **F1** a permitted pair plus a *realistic* solar contribution — declared
  as **≤ 40 kWh/day** of free energy, about what a large domestic array
  (~10 kWp) yields on a good June day, and all of it assumed surplus —
  reproduces **≥ £300/month** net at an export limit an ordinary DNO
  grants without reinforcement (**3.68 kW single-phase G98**, or 11.04 kW
  three-phase G98, reported separately); or
- **F2** the winter window shows Agile ↔ Agile Outgoing grid-to-grid
  cycling alone at **≥ £300/month** in any of the three regions.

Either outcome is recorded as a falsification, with the numbers, and the
conclusion is narrowed to what survives.

## Acquisition gate

Human seal, then, in this order: products index; product documents;
unit rates and standing charges for every declared (product, region,
window); Elexon MID and system prices for every day; rules documents.
Everything is pinned under `data/raw/octopus/<run-date>-010/`,
`data/raw/elexon/010/` and `data/raw/press/`, journalled with SHA-256
before any price is read into the model; the manifest is copied to
`evidence/`. The runner (`run.py`) refuses to fetch unless invoked with
`--seal <prefix of this file's SHA-256>`, so the seal is on the record in
the command that acquired the data. Rules documents are read **after** the
backtests are computed, so the permitted/not-permitted labelling cannot
steer the numbers.

## Out of scope for this run

The Forward Mystery on the load-control licence (its own declaration);
Amber and continental sources; any page or product work; Purcell and
Robinson. Portability is served only by the tariff interface above.

## Limits declared in advance

Self-reported earnings are the observations; the test is of feasibility,
not of the individuals' accounts. The optimum is an upper bound on any
realisable daily schedule. Prices are the published tariff prices; any
private or legacy rate a customer holds is invisible here. Household load
and the value of self-consumption are not modelled. Degradation is an
assumption range. Elexon MID is not the Agile input. One summer and one
winter window of one year.
