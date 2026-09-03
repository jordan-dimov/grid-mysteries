# 010 — the household desk: results

**Status: NOT RUN.** Declaration `6b91dd96…` (commit `9094783`), frozen
2026-09-03 before any request for this question; Amendment 1
(`AMENDMENTS.md`, 2026-09-03, pre-fetch) tightens the model's physical
constraint set. Acquisition waits for the human seal: `run.py --seal
6b91dd96 --run-date <date> [--press-url <Bloomberg URL>]`. Every figure
below marked *[awaiting run]* is filled from `evidence/results.json` and
nothing else; the frozen target conclusion is then defended or narrowed,
never rewritten. Publication waits for a second human seal.

## 1. The mystery

A Bloomberg feature (2026-09-03) says a Shropshire household with a
200 kWh battery earns about £400 a month in summer by buying electricity
on Octopus's half-hourly prices and selling it back at the evening peak.
Buying and selling on the *same* half-hourly prices ought to net roughly
nothing once VAT, the retailer's margin and network charges sit between
the buy and sell price. **How does the arithmetic work?**

## 2. The evidence

*[awaiting run]* — the smallest reconstruction that supports the question:

- Published Octopus tariff prices, half-hour by half-hour, for regions C,
  E and J, June–August 2026 and January–February 2026: Agile import and
  Agile Outgoing export side by side, and the fixed overnight and Flux
  schedules the declaration names.
- The half-hours 16:00–21:00 on 2026-06-24 in region E: export price,
  import price, and what 200 kWh exported at 20 kW versus 3.68 kW would
  have been paid.
- The wholesale layer beneath: Elexon market index and system prices in
  the same half-hours.

## 3. Explanations tested

*[awaiting run]* — one row per hypothesis in the declaration (H-gross,
H-pair, H-solar, H-export-limit, H-region, H-rules, H-wedge,
H-degradation, H-agile-zero): what was checked, what was ruled out, what
remains unknown. Region C summer Agile ↔ Agile Outgoing is a
**replication** of a pre-declaration scratch result and is labelled so.

## 4. The conclusion

**Frozen target** (from the declaration, scored clause by clause):

> The reported earnings are gross export receipts on a retailer-granted
> cross-tariff spread; grid-to-grid arbitrage on Agile nets roughly zero
> over summer 2026; the export connection, not the software, bounds what
> a household can earn.

*[awaiting run]* — each clause: holds / refuted / indeterminate against
the pre-declared bars; falsifiers F1 and F2 checked and reported with
their numbers whichever way they fall. Every backtest figure is a
counterfactual under stated assumptions, never a saving or a loss.

## 5. Expert corner

Fixed now (the rest *[awaiting run]*):

- **Products / tariff codes.** Import: `AGILE-24-10-01`, `GO-VAR-22-10-14`,
  `INTELLI-VAR-22-10-14`, `FLUX-IMPORT-23-02-14`,
  `INTELLI-FLUX-IMPORT-23-07-14`. Export: `AGILE-OUTGOING-19-05-13`,
  `OUTGOING-VAR-24-10-26`, `OUTGOING-PRIME-FIX-12M-26-06-23`,
  `FLUX-EXPORT-23-02-14`. Tariff codes expected `E-1R-<product>-<region>`;
  the codes actually pinned are in `evidence/tariff-codes.json`, and any
  difference in `evidence/acquisition-log.json`.
- **Regions.** C London (headline, our patch), E West Midlands
  (Shropshire), J South Eastern England (Kent).
- **Windows.** Summer: local 2026-06-01 → 2026-08-31 inclusive
  (`period_from=2026-05-31T21:00Z`, `period_to=2026-09-01T00:00Z`).
  Winter: 2026-01-01 → 2026-02-28 (`2025-12-31T22:00Z` → `2026-03-01T00:00Z`).
  2026-06-24 as the Agile day 23:00 23/06 → 23:00 24/06 local.
- **VAT.** Import read from `value_inc_vat` (domestic 5 %); export from
  `value_exc_vat`, with `value_inc_vat == value_exc_vat` asserted on every
  export row. Standing charges pinned, reported, not in any backtest.
- **Model.** `household_desk.py`, rule `010/per-day-optimum/v1`. Decision
  day 23:00 → 23:00 local, decided at 16:00 local the day it starts; Agile
  rates stamped `published_at` = that 16:00, fixed schedules known
  indefinitely; a day with any unknown or missing price is dropped and
  counted; a month with fewer than 25 scored days is *incomplete*.
  Battery 200 kWh; inverter 20 kW battery-side, time-shared within a slot
  (Amendment 1); export limit on delivered kWh at 20 / 11.04 / 3.68 kW;
  round trip 0.90 with losses on discharge; degradation 0 / 2 / 5 p per
  kWh delivered; free energy 0–100 kWh/day spread over 09:00–17:00 local.
  Exact per-day optimum by dynamic programming over the stored balance
  (piecewise-linear concave value functions, exact rationals; Decimal for
  money). It upper-bounds any daily heuristic.
- **Fetch timestamps, digests.** `evidence/manifest.json` (copied from the
  journals under `data/raw/octopus/<run-date>-010/`, `data/raw/elexon/010/`,
  `data/raw/rules/010/`, `data/raw/press/`).
- **Rules documents.** Listed in `run.py::RULES_DOCUMENTS`; what was
  actually retrieved, and what was not, in `evidence/acquisition-log.json`.
  Permitted / not-permitted pair labels are read from the pinned pages
  *after* the backtests were computed.
- **Elexon.** MID (both providers) and settlement system prices per day;
  shown beneath Agile, never substituted into the formula; MID is not the
  N2EX day-ahead auction Agile is indexed to.

## 6. Reproducibility

Code: `src/grid_mysteries/sources/octopus.py` (adapter),
`src/grid_mysteries/investigations/household_desk.py` (model and the JSON
contract `backtest_json`), `tests/test_octopus.py`,
`tests/test_household_desk.py` (no live API in tests). Runner:
`investigations/010-household-desk/run.py`. Evidence: `evidence/results.json`,
`evidence/manifest.json`, `evidence/tariff-codes.json`,
`evidence/acquisition-log.json` *[awaiting run]*. Raw pulls under
`data/raw/` are local and immutable, journalled with SHA-256 before any
price is read.

The JSON contract a public page may call:

```json
{
  "battery_kwh": "200", "inverter_kw": "20", "export_limit_kw": "3.68",
  "import_limit_kw": null, "round_trip_efficiency": "0.90",
  "degradation_p_per_kwh": "2", "free_energy_kwh_per_day": "0",
  "import_tariff": {"product": "AGILE-24-10-01", "region": "E"},
  "export_tariff": {"product": "AGILE-OUTGOING-19-05-13", "region": "E"},
  "window": {"from": "2026-06-01", "to": "2026-06-30"}
}
```

returning monthly and window totals (imported, exported and free kWh;
gross export receipts, import cost, degradation cost and net in pounds;
average captured prices; scored and dropped days; the echoed assumptions
and the rule id).
