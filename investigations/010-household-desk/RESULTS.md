# 010 — results: the £400 a month does not reproduce from published tariffs on any pairing the retailer permits; the export connection is the largest lever, the pairing the second, and Agile grid-to-grid is neither zero nor enough

**Run**: 2026-09-03, sealed by the sponsor on digest `6b91dd96` (commit
`9094783`) with Amendment 1 standing; acquisition 20:53–21:14 UTC, 453
artefacts journalled with SHA-256 (`evidence/manifest.json`). Amendment 2
(`AMENDMENTS.md`) was made after the run, before this document was
written, and changed one case only; the pre-amendment evaluation is
preserved as `evidence/results-PRE-AMENDMENT-2.json`. Every number here
comes from `evidence/results.json`, `evidence/results-permitted-pairs.json`
or the pinned rules pages named beside it. Runner `run.py`; model and
tests `src/grid_mysteries/investigations/household_desk.py`,
`tests/test_household_desk.py`; adapter `src/grid_mysteries/sources/octopus.py`,
`tests/test_octopus.py`. **Publication waits for the sponsor's second seal.**

Every backtest figure below is a **counterfactual under stated
assumptions** (an exact per-day optimum for a 200 kWh battery on published
prices), never what anyone earned, saved or lost.

## 1. The mystery

A Bloomberg feature (2026-09-03) says a Shropshire household with a
200 kWh battery earns about £400 a month in summer, and £300 in winter, by
buying electricity on Octopus's half-hourly prices and selling it back at
the evening peak, and that one June evening's export paid £60. Buying and
selling on the *same* half-hourly prices ought to net little once VAT,
the retailer's margin and network charges sit between the buy and sell
price. **How does the arithmetic work?**

## 2. The evidence

Published Octopus tariff prices, half-hour by half-hour, for regions C
(London), E (West Midlands, the Shropshire case) and J (South Eastern
England, the Kent case), 2026-06-01 → 08-31 and 2026-01-01 → 02-28; the
Elexon market-index and system prices beneath them; and Octopus's own
pages and terms for the tariff formula, the cap and which import and
export products may be combined.

**The wedge (region E, summer, 4,416 half-hours).** Agile import inclusive
of VAT minus Agile Outgoing export in the same half-hour: p10 4.65 p, median
10.77 p, p90 16.85 p per kWh. Mean import 20.0 / 21.7 / 26.5 p and mean
export 10.9 / 11.6 / 13.7 p in June / July / August, over an APX market
index of £96 / £106 / £130 per MWh (the N2EX index records in the pinned
stream carry zero price and volume throughout and are not used). The
100 p cap never bound: the highest import price in the window was 80.5 p,
once. In 80 / 83 / 45 half-hours per month the export price times the
round-trip efficiency exceeded the import price in the same half-hour —
the plunge-priced hours a battery lives on.

**2026-06-24, region E, the Agile day 23:00 → 23:00.** Agile import ranged
14.79 → 80.50 p; Agile Outgoing 8.57 → 37.24 p. Over 16:00–21:00 local the
ten export half-hours averaged **29.54 p/kWh** (22.52, 25.98, 35.47, 37.24,
34.76, 33.70, 35.10, 35.47 p from 16:00 to 19:30, then falling).

| exporting into 16:00–21:00 at | kWh delivered | gross receipts |
|---|---|---|
| 20 kW (a G99 connection) | 100 | **£29.54** |
| 11.04 kW (three-phase G98) | 55.2 | £16.31 |
| 3.68 kW (single-phase G98) | 18.4 | £5.44 |
| 40 kW, for reference | 200 | £59.08 |

The whole day's optimum on Agile ↔ Agile Outgoing at 20 kW: 120 kWh
imported for £18.95, 108 kWh exported for £34.14, **net £15.18**; at
3.68 kW, net £3.31. On Go ↔ Agile Outgoing (permitted) at 20 kW: net £21.44.

**Headline backtest — Agile ↔ Agile Outgoing, 200 kWh, 20 kW inverter,
20 kW export, 90 % round trip, no degradation, no solar** (monthly net =
window net ÷ complete months; every month complete, no day dropped):

| region | summer £/month | Jun / Jul / Aug | winter £/month | Jan / Feb | summer gross export | summer import cost | kWh exported/day | captured import / export p |
|---|---|---|---|---|---|---|---|---|
| **C** (replication) | **151.45** | 182 / 160 / 112 | 31.91 | 36 / 28 | £983 | £529 | 63.7 | 8.13 / 16.78 |
| **E** (Shropshire) | **135.04** | 160 / 145 / 101 | 24.63 | 28 / 22 | £795 | £389 | 52.4 | 7.27 / 16.49 |
| **J** (Kent) | **139.97** | 165 / 151 / 104 | 27.81 | 30 / 26 | £829 | £409 | 51.9 | 7.71 / 17.36 |

**Export limit, same pair, summer £/month:** 3.68 kW → C 43.69, E 38.64,
J 40.01; 11.04 kW → C 108.47, E 96.24, J 99.62; winter at 3.68 kW → £7–9.

**Every declared pair, summer, 20 kW, £/month (C / E / J), with the pairing
label read from the pinned documents after the numbers were computed:**

| import ↔ export | C | E | J | permitted? | decided by |
|---|---|---|---|---|---|
| Go ↔ **Flux Export** | 317.25 | 304.13 | 341.88 | **no** — Flux is a combined import-and-export tariff, "you therefore cannot be on any other tariffs" | smart-tariff terms §2.7.1 (`octopus-smart-tariff-terms.html`) |
| Agile ↔ Flux Export | 282.99 | 254.18 | 273.02 | **no** | same |
| **Go ↔ Agile Outgoing** | 227.21 | 217.47 | 240.44 | **yes** — Go "is only compatible with" SEG, Outgoing Octopus and Agile Outgoing | terms §2.1.2 (v1.6, 10 Apr 2025); Go FAQ "Outgoing Octopus is now compatible with Octopus Go" |
| **Flux ↔ Flux** | 192.32 | 190.60 | 208.32 | **yes** — the bundle itself | terms §2.7 |
| **Agile ↔ Agile Outgoing** | 151.45 | 135.04 | 139.97 | **yes** | Outgoing FAQ: Agile Outgoing sold alongside Agile; terms §2.2 |
| Go ↔ Outgoing Prime Fixed | 107.41 | 107.41 | 107.41 | **not determinable** — Prime (launched 2026-06-23) is absent from the terms pinned; §2.1.2 says "no other Octopus export tariffs" but predates it | terms §2.1.2; 69 of 92 days scored (product starts 23 June) |
| Agile ↔ Outgoing Octopus (12 p flat) | 102.86 | 99.57 | 96.62 | yes | Outgoing FAQ |
| Intelligent Flux Import ↔ Flux Export | 85.76 | 88.33 | 100.35 | **not a real pair** — Intelligent Flux is a bundle whose export product is not in the public products index; this row pairs its import with ordinary Flux export and is reported only for completeness | terms §2.3.2.3 |
| Agile ↔ Outgoing Prime Fixed | 99.82 | 95.87 | 92.81 | not determinable | as above; 69/92 days |
| Go ↔ Outgoing Octopus | 66.70 | 66.70 | 66.70 | yes | terms §2.1.2 |
| Flux Import ↔ Agile Outgoing | 43.98 | 50.94 | 54.55 | no | terms §2.7.1 |
| Intelligent Flux Import ↔ Agile Outgoing | 5.97 | 7.23 | 6.77 | no | terms §2.3.2.3 |
| Flux / Intelligent Flux Import ↔ Outgoing Octopus or Prime | 0.00 | 0.00 | 0.00 | no | terms |
| **Intelligent Octopus Go** ↔ anything | — | — | — | **not testable**: the declared code `INTELLI-VAR-22-10-14` closed on 2025-03-31 per its pinned product document, and the public products index (38 products) carries no successor; Intelligent Go pairs with SEG, Outgoing Octopus and Agile Outgoing per terms §2.3.1.2 (v2.6, 16 Feb 2026) | product document; products index |

Winter, 20 kW: Go ↔ Flux Export 296–333 (not permitted); Go ↔ Agile
Outgoing 142–164; Flux ↔ Flux 148–167; Go ↔ Outgoing Octopus 147.51 (the
15 p flat rate applied until 2026-03-01); Agile ↔ Agile Outgoing 25–32.
Prime has no winter rates (n/a). The full table, and the 3.68 kW column
for every pair, are in `evidence/results.json` (`3-pairs`).

**Degradation, summer, 20 kW, £/month:** Agile ↔ Agile Outgoing at 2 p /
5 p per kWh delivered: C 117.63 / 80.32, E 106.22 / 73.65, J 111.21 /
78.36 (the optimum cycles less, not just earns less: 4,473 → 3,114 kWh
exported in C). Permitted best pair, Go ↔ Agile Outgoing:
at 2 p / 5 p: C 172.45 / 96.66, E 163.07 / 90.14, J 185.69 / 110.76
(from 227 / 217 / 240 at zero). Flux ↔ Flux: C 159.20 / 109.52,
E 157.48 / 107.80, J 175.20 / 125.52 (`evidence/results-permitted-pairs.json`).

**Free (solar) energy, summer, best permitted pair Go ↔ Agile Outgoing,
£/month** (free kWh/day at zero cost, 09:00–17:00 local, same losses;
Amendment 2 numbers):

| free kWh/day | 0 | 10 | 20 | 30 | **40** | 60 | 80 | 100 |
|---|---|---|---|---|---|---|---|---|
| 20 kW, C | 227 | 269 | 309 | 347 | **384** | 454 | 521 | 584 |
| 20 kW, E | 217 | 257 | 295 | 332 | **367** | 433 | 497 | 557 |
| 20 kW, J | 240 | 281 | 320 | 357 | **393** | 460 | 524 | 585 |
| 11.04 kW, C | 188 | 223 | 257 | 291 | **324** | 387 | 445 | 493 |
| 11.04 kW, E | 175 | 209 | 242 | 274 | **305** | 367 | 422 | 468 |
| 11.04 kW, J | 193 | 227 | 261 | 294 | **326** | 388 | 444 | 491 |
| 3.68 kW, C | 91 | 119 | 146 | 172 | **195** | 233 | 233 | 233 |
| 3.68 kW, E | 80 | 108 | 135 | 161 | **183** | 220 | 220 | 220 |
| 3.68 kW, J | 89 | 117 | 144 | 170 | **193** | 230 | 230 | 230 |

At single-phase G98 the free energy saturates from about 57 kWh/day: the
connection can carry no more, so the ceiling with unlimited solar is
£220–233. The Flux bundle behaves similarly (E: 191 → 355 at 20 kW and
39 → 169 at 3.68 kW with 40 kWh/day). Winter, Go ↔ Agile Outgoing, 20 kW:
142–164 with no free energy, 193–215 with 20 kWh/day; at 3.68 kW 35–41
and 85–91.


For the record, the same sweep on the non-permitted Go ↔ Flux Export pair
(what the runner selected by number before labelling): at 20 kW each
10 kWh/day adds about £24/month (E: 304 → 399 at 40 kWh/day, 541 at 100);
at 3.68 kW, 65.56 → 171.36 at 40 kWh/day, saturating at 216.97 from
60 kWh/day.

**Standing charges** (pinned, reported, in no backtest): Agile 39.54 /
61.56 / 55.79 p per day inclusive of VAT in C / E / J; Go 44.12 / 59.05 /
54.46; Flux 42.42 / 57.35 / 52.76; export tariffs 0.

## 3. Explanations tested

| hypothesis | result |
|---|---|
| **H-gross** — the figures are gross export receipts | **Partly supported.** The £60 for 16:00–21:00 on 24 June matches gross receipts for about 203 kWh at the region-E Agile Outgoing average of 29.54 p (200 kWh → £59.08). It does *not* match 20 kW: five hours at 20 kW deliver 100 kWh for £29.54. Either the export ran at about 40 kW, or the figure is a rounder recollection, or it is not Agile Outgoing. The day's net on Agile ↔ Agile Outgoing at 20 kW is £15.18. |
| **H-pair** — a cross-tariff pair is needed | **Supported in direction, not in size.** The best permitted pair (Go night import at 8.63 p with Agile Outgoing) raises the summer ceiling to £217–240/month, 60 % above Agile ↔ Agile Outgoing, and the Flux bundle to £191–208. Only pairings the terms exclude (Go or Agile import with Flux export) reach £300. Intelligent Go could not be tested (product closed; no public successor). |
| **H-solar** — free energy closes the gap | **Supported as the only route to the claim, and it is a demanding one.** On the best permitted pair, £400 needs about 40 kWh/day of surplus solar *and* a 20 kW export (E: £367 at 40, £433 at 60 kWh/day); at three-phase G98 it needs 50–60 kWh/day; at single-phase G98 it is unreachable at any solar (£220–233 ceiling). 40 kWh/day of *surplus* is roughly the whole June output of a 10 kWp array on a good day, before any household use. Free energy is valued at zero here, so these are ceilings. |
| **H-export-limit** — the connection bounds earnings | **Supported, strongly.** From 20 kW to single-phase G98 (16 A/phase, 3.68 kW) the Agile ↔ Agile Outgoing ceiling falls from £135–151 to £39–44 (÷3.5) and the best permitted pair from £217–240 to £80–91. Three-phase G98 (11.04 kW) sits at £96–108 on Agile. |
| **H-region** | Small: C > J > E by 8–12 % on the headline; E (Shropshire) is the *lowest* of the three. |
| **H-rules** — pairing rules and the 100 p cap | Rules decide the outcome (table above). The 100 p cap did not bind in summer (max 80.5 p once); O2's "about £1/kWh" is the Agile cap, irrelevant to a battery that never buys at the top. |
| **H-wedge** — VAT and network charges kill grid-to-grid | **Refuted as stated.** The median same-half-hour wedge is 10.8 p, yet the optimum earns because it never trades the *same* half-hour: it buys at a captured 7–8 p (plunge and overnight hours) and sells at 16.5–17.4 p. The wedge shapes the margin; it does not zero it. |
| **H-degradation** | At 5 p/kWh delivered the headline halves (C 151 → 80) and the permitted best pair falls from £217–240 to £90–111. A degradation assumption is therefore first-order for any household's own arithmetic. |
| **H-agile-zero** — Agile grid-to-grid nets roughly nothing | **Refuted by its own replication.** The exposed region-C summer case gives £151/month, not zero; E and J (untouched) £135 and £140. Winter is £25–32. Why the scratch got zero is a methodological lesson, recorded below. |

**Why the replication refuted the hypothesis it was meant to replicate
(a methodological lesson).** The pre-declaration scratch model, as the
sponsor describes it, forced a full 200 kWh cycle every day — it bought
the cheapest hours and sold the dearest whether or not the day's spread
covered the round-trip loss and the wedge — so its loss-making days
cancelled its good ones and the summer summed to roughly zero. The exact
model cycles only when a trade pays: in region C it exports 63.7 kWh a
day on average, not 180, buying at a captured 8.13 p (the plunge and
overnight hours) and selling at 16.78 p, and on a day with no such spread
it does nothing. The difference between "£0" and "£151" is entirely the
decision *not* to trade. That is exactly the error a household's naive
automation makes when it is set to "charge overnight, discharge at peak"
every day regardless of price, and it is the first thing a public
calculator built on this model should show a household: the value is in
the days you skip. Recorded here as a lesson, not a correction to the
declaration, which named the exposed hypothesis as a hypothesis.

**Replication versus untouched tests.** The only exposed cell was region
C, summer, Agile ↔ Agile Outgoing. Its result here (£151.45/month at
20 kW) contradicts the scratch hypothesis it was meant to replicate, and
the two untouched regions agree with the replication, not the scratch.
Everything else in this document — E and J, winter, every other pair,
the export-limit and solar readings, the 24 June reconstruction — was
computed for the first time under this declaration.

## 4. The conclusion

The frozen target was: *the reported earnings are gross export receipts on
a retailer-granted cross-tariff spread; grid-to-grid arbitrage on Agile
nets roughly zero over summer 2026; the export connection, not the
software, bounds what a household can earn.* Scored clause by clause
against the pre-declared bars:

- **"The reported earnings are gross export receipts"** — bar: 24 June
  gross at 20 kW from 200 kWh within £45–75 *and* day net below £20.
  **Holds**, with the bar's own premise shown impossible. The £60 is
  gross export receipts for about 203 kWh at that evening's 29.54 p
  average (200 kWh × 29.54 p = £59.08). But 200 kWh cannot leave a 20 kW
  connection in five hours: 20 kW × 5 h = 100 kWh = £29.54 at most, so the
  bar's 20 kW figure lands at half the claim by arithmetic, not by price.
  Delivering 200 kWh between 16:00 and 21:00 needs 40 kW of export; the
  day's *net* on Agile ↔ Agile Outgoing at 20 kW is £15.18, on the best
  permitted pair £21.44. The figure is a gross receipt, and at 20 kW a
  physically impossible one.
- **"On a retailer-granted cross-tariff spread"** — bar: a permitted pair
  ≥ £300/month at 20 kW while no Agile ↔ Agile Outgoing case does. **Holds
  only in the narrowed form.** The best permitted pair, Go import with
  Agile Outgoing, reaches £217–240, 60 % above Agile alone, so the spread
  is real and retailer-granted; the claimed £300–400 needs either a
  pairing the terms exclude (Go or Agile import with Flux export,
  £254–342) or free energy (next clause).
- **"Grid-to-grid arbitrage on Agile nets roughly zero"** — bar: headline
  below £50 in every region (holds) or ≥ £200 anywhere (refuted).
  **Refuted by its own replication**: £151 in the exposed cell, £135 and
  £140 in the untouched regions, at 20 kW; between the two bars but
  nowhere near zero. Only at single-phase G98 (£39–44) does the phrase
  describe the data. The winter figure, £25–32, is a tenth of the £300
  claimed for winter.
- **"The export connection, not the software, bounds what a household
  can earn"** — bar: every permitted pair < £150 at 3.68 kW (holds:
  £80–91) while the same pair reaches £300 at 20 kW (fails: £240).
  **Holds** in the sense that matters: the connection is the largest
  single lever in the grid, ×2.6 on the best permitted pair and ×3.5 on
  Agile alone between single-phase G98 and 20 kW, and with unlimited
  solar the single-phase ceiling is still £220–233. The software cannot
  be the lever because the figures here are already the exact optimum
  over the household's own information set; no agent does better.

**Intelligent Octopus Go and the permitted-pair set.** The declared code
`INTELLI-VAR-22-10-14` closed on 2025-03-31 (its pinned product document's
`available_to`), returned no rates for either window, and the public
products index of 38 codes carries no successor; the current Intelligent
Go is not on the public price list. Its terms (§2.3.1, v2.6, 16 Feb 2026)
give a six-hour off-peak window, 23:30–05:30, against Go's five hours from
00:30, and pair it with SEG, Outgoing Octopus and Agile Outgoing — so it
is a permitted pairing that would plausibly sit **above** Go ↔ Agile
Outgoing, by an amount this run cannot measure. **The permitted-pair set
tested is therefore smaller than declared, and F1 is judged on the pairs
that could be tested**: Go ↔ Agile Outgoing, Flux ↔ Flux, Agile ↔ Agile
Outgoing, Agile or Go ↔ Outgoing Octopus. A reader who has Intelligent
Go's 2026 rates can rerun the JSON contract with them; if six hours at a
similar night price lift the 3.68 kW, 40 kWh/day figure from £183–195 past
£300, F1 fires at single-phase too. That gap is declared, not assumed
away.

**Falsifiers.** F2 (winter Agile ↔ Agile Outgoing ≥ £300) is not
triggered: £25–32. F1 (permitted pair + ≤ 40 kWh/day free energy ≥ £300 at
3.68 kW, on the testable pairs): **not triggered at single-phase G98** (Go ↔ Agile Outgoing with 40 kWh/day: C 195.37, E 183.33, J 193.19), **triggered in the three-phase reading** (11.04 kW with 40 kWh/day: C 323.62, E 305.46, J 325.94; at 30 kWh/day 291 / 274 / 294, below the bar). Recorded as a falsification of the conclusion's single-lever form: with a three-phase G98 export and a large surplus array, a permitted pairing does reach £300 without any G99 application. The conclusion is narrowed below to say so.

**The narrowed conclusion the evidence supports:**

> On Octopus's published prices for summer 2026, a 200 kWh home battery
> trading grid-to-grid on a permitted tariff pairing has a ceiling of
> about £220–240 a month with a 20 kW export (Go import with Agile
> Outgoing), £135–150 on Agile alone, and £40–90 on the 3.68 kW
> single-phase export an ordinary DNO grants without a G99 application —
> all before degradation, which at 5 p/kWh roughly halves them. £400 a
> month is not reachable from the grid alone on any pairing the retailer's
> terms permit. It becomes reachable only with free energy on a scale of
> about 40 kWh a day of surplus solar and a 20 kW export, or 50–60 kWh a
> day at three-phase G98; at single-phase G98 no amount of solar gets past
> about £230. The lever ranking is therefore: export connection first,
> surplus solar second, tariff pairing third, software last — the exact
> optimum here is the most any software could do. The 24 June £60 matches
> gross export receipts for about 200 kWh at that evening's export price,
> which a 20 kW connection cannot deliver in five hours. In winter the
> Agile-only ceiling is a tenth of the £300 claimed, and the best
> permitted pair a half.

What remains unknown: which tariffs the households are on, their
inverter and connection ratings, their solar, and whether "after his own
consumption" means what we assumed. None of that is public.

## 5. Expert corner

- **Products / tariff codes.** All nine declared products resolved to
  `E-1R-<product>-<region>` in their pinned product documents
  (`evidence/tariff-codes.json`, no differences). `INTELLI-VAR-22-10-14`:
  document pinned, `available_to` 2025-03-31, zero rate rows in both
  windows, absent from the index of 38 products. `OUTGOING-PRIME-FIX-12M-26-06-23`:
  `available_from` 2026-06-23; 23 summer days dropped, winter none.
  `OUTGOING-VAR-24-10-26`: 15 p to 2026-03-01, 12 p after. Not declared and
  not used: `GO-FIX-12M-26-08-19`, the SEG products.
- **Regions.** C London, E West Midlands, J South Eastern England
  (Octopus region letters; the last component of every tariff code).
- **Windows.** Summer local 2026-06-01 → 08-31 (92 decision days, 0
  dropped on every pair with rates); winter 2026-01-01 → 02-28 (59 days).
  Requests `period_from=2026-05-31T21:00Z&period_to=2026-09-01T00:00Z`
  and `2025-12-31T22:00Z` → `2026-03-01T00:00Z`, `page_size=1500`, pages
  followed by the API's own `next` link.
- **VAT.** Import `value_inc_vat` (5 %, HMRC Notice 701/19 reduced rate
  for qualifying use, pinned); export `value_exc_vat`, equal to
  `value_inc_vat` on every export row (checked in the adapter).
- **Agile formula and cap** (pinned `octopus-agile-pricing-explained.html`):
  price = min(D × W + P, 95) exclusive of VAT, D = 2.00 (London), 2.10
  (West Midlands), 2.20 (South East); P = 12 p in all three, 16:00–19:00
  only; 95 p exclusive = 100 p inclusive cap. Agile Outgoing (pinned
  `octopus-outgoing-faqs.html`): M × APX + B + C, C only 16:00–19:00.
- **Pairing rules**: `octopus-smart-tariff-terms.html` §2.1.2 (Go), §2.3.1.2
  (Intelligent Go), §2.3.2.3 (Intelligent Flux), §2.7.1 (Flux); `octopus-go-faqs.html`;
  `octopus-outgoing-faqs.html`; the help article
  `octopus-export-import-combinations.html` describes a table that is
  rendered client-side and carries no list in the pinned HTML.
- **G98 threshold.** ENA's document pages returned 403 to a scripted fetch
  (recorded); UK Power Networks pages were not attempted at the sponsor's
  instruction. The pinned ENA engineering-database index
  (`ena-eng-docs.html`) lists EREC G98 Issue 2 as "Requirements for the
  connection of Fully Type Tested Micro-generators (up to and including
  16 A per phase)"; 16 A × 230 V = 3.68 kW single-phase, 11.04 kW
  three-phase, by nominal voltage. The Distribution Code pages
  (`distribution-code.html`, `dcode-engineering-documents.html`) refer to
  the same ENA database.
- **Model.** Rule `010/per-day-optimum/v2`. Decision day 23:00 → 23:00
  local, decided 16:00 local on the day it starts (the terms say Agile
  prices are "usually published between 16:00-22:00 (normally, but not
  always, nearer 16:00)", so the stamp is slightly generous to the
  household); fixed schedules known indefinitely. Slots: union of both
  series' boundaries and the half-hour grid (Amendment 2). Battery
  200 kWh; inverter 20 kW battery-side, time-shared within a slot
  (Amendment 1); export limit on delivered kWh; round trip 0.90 with
  losses on discharge (so a 20 kW inverter delivers at most 18 kW);
  degradation per kWh delivered; free energy spread over 09:00–17:00
  slots by duration and passed through the same inverter budget and
  losses; stored balance in [0, 200] at every boundary and zero at both
  ends of the day. Exact per-day optimum by dynamic programming over the
  stored balance (piecewise-linear concave value functions, exact
  rationals; Decimal for money). It **upper-bounds** any daily heuristic,
  including the households' software; where a figure reproduces a claim,
  the household's own agent would do worse, not better. Runtime: about
  2 s per 92-day case; the declared grid is about 320 cases.
- **Elexon.** MID stream and settlement system prices for 151 days;
  APX MID monthly means and system prices reported; N2EX MID records in
  the pinned stream are zero price and zero volume and are not used. No
  backtest figure depends on Elexon.
- **Fetch timestamps and digests.** `evidence/manifest.json`: 453
  artefacts, 2026-09-03 20:53:53 → 21:14:39 UTC, plus the rules pages
  pinned in two later rules-phase runs the same evening (journals under
  `data/raw/rules/010/`). Acquisition notes, absences and refusals:
  `evidence/acquisition-log.json`.
- **Press artefact.** The sponsor supplied a Bloomberg subscriber gift
  link on 2026-09-03 (article id `TKRSG5KIP3I900`; access token expiring
  2026-09-10 12:52:01 UTC). Bloomberg refused the scripted fetch with 403;
  the attempt, the article identity and the expiry are recorded in
  `evidence/acquisition-log.json` (token redacted). Not retried with a
  browser agent. A saved copy can be pinned with
  `run.py --seal 6b91dd96 --run-date 2026-09-03 --phase press --press-file <saved.html|.pdf>`,
  which journals it as `sponsor-saved-copy` with its digest. Until then
  the sponsor's transcription of the claims in `DECLARATION.md` is the
  record of what was claimed, as the declaration provides.

## 6. Reproducibility

`uv run python investigations/010-household-desk/run.py --seal 6b91dd96
--run-date 2026-09-03 --phase evaluate` re-derives `evidence/results.json`
from the pinned data (about ten minutes; the journal refuses to refetch
anything already pinned). The permitted-pair sweeps were produced by a
scratch script calling the same `backtest_json`; its inputs and outputs
are in `evidence/results-permitted-pairs.json` and the request objects
inside it reproduce each case through the JSON contract:

```json
{
  "battery_kwh": "200", "inverter_kw": "20", "export_limit_kw": "3.68",
  "import_limit_kw": null, "round_trip_efficiency": "0.90",
  "degradation_p_per_kwh": "0", "free_energy_kwh_per_day": "0",
  "import_tariff": {"product": "GO-VAR-22-10-14", "region": "E"},
  "export_tariff": {"product": "AGILE-OUTGOING-19-05-13", "region": "E"},
  "window": {"from": "2026-06-01", "to": "2026-08-31"}
}
```

Tests (no live API): 152 in the suite, of which 23 cover the day rule,
slot construction, the optimum (hand cases, brute force, feasibility and
value consistency under Hypothesis), the JSON contract; 5 cover the
adapter's URL builders, VAT handling, publication stamps and page
merging. `scripts/check` passes in full.
