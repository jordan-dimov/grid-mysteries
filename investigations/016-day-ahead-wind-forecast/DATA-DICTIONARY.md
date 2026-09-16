# 016 — data dictionary

Every table in `data/` describes **settlement day 2026-09-08**. Each was written
by `run.py --phase export` from bytes pinned under `data/raw/elexon/016/` and
from 012's and 015's committed evidence; `evidence/pack.json` carries the
SHA-256 of every input and every output.

## Conventions, stated once

**Time zone.** Every timestamp in every file is **UTC** and carries a trailing
`Z`. Elexon publishes some datetimes without the `Z`; those are UTC too, and
the export normalises them. Nothing here is in local time.

**Settlement periods.** A settlement day is 48 half-hour periods numbered 1–48,
and period 1 starts at **local** midnight. 8 September 2026 was in British
Summer Time, so **period 1 starts 2026-09-07T23:00Z** and period 48 starts
2026-09-08T22:30Z. Period *p* starts at `2026-09-07T23:00Z + (p−1)×30 min`.
Reading the day as `2026-09-08T00:00Z`–`23:59Z` silently drops periods 1–2 and
picks up the next day's — the mistake 012 had to correct for MID.

**Numbers.** Written as published, as text, without rounding or unit
conversion. Read them as decimals, not binary floats, if you intend to
reconcile against a settlement total.

**Empty cells mean absent, not zero.** A blank is "the publisher did not carry
a value here". Where the publisher carried a zero, the cell reads `0`.

**MW versus MWh.** Forecasts and notifications are **MW** (an instantaneous
level). B1610 is **MWh** (an energy volume over a half hour). A 100 MW level
held for a whole period is 50 MWh. The pack never converts between them.

---

## `forecast_issues.csv` — WINDFOR as published (384 rows)

NESO's wind generation forecast, **every issue** published on 7 and 8 September
2026, kept where the target hour falls in the 8 September settlement day.
16 issues (eight per day: 03:30, 05:30, 08:30, 10:30, 12:30, 16:30, 19:30 and
23:30 UTC) × 24 target hours.

| Column | Meaning |
|---|---|
| `publish_time_utc` | When NESO published this issue. This is the column that makes the forecast's *evolution* readable: an issue published at 2026-09-07T03:30Z was knowable ~21 hours before period 1. |
| `target_start_utc` | The hour the forecast value applies to, by its start instant. |
| `settlement_date` | `2026-09-08` throughout. |
| `settlement_period` | The period that **starts** at `target_start_utc`. Always odd (1, 3, 5 … 47), because WINDFOR is hourly. This is Elexon's own mapping, not ours: the pinned `windfor_evolution_2026-09-08T1200Z.json` shows the publisher labelling 12:00Z as period 27. |
| `covers_periods` | The two periods the hour spans, e.g. `27-28`. The pack does **not** interpolate WINDFOR onto half-hours; if you need a half-hourly series, say how you made it. |
| `forecast_mw` | Forecast wind generation, MW. |
| `dataset` | `WINDFOR`. |

**Scope caveat, and it is the important one.** WINDFOR covers "wind farms which
are visible to the ESO and have operational metering". That is not the same
population as FUELINST's wind, and neither is the same as the sum of the wind
BM units in `b1610_actuals.csv`. Three series, three scopes. Comparing them
without saying which population each covers will produce an error that is an
artefact of scope, not of meteorology.

## `b1440_day_ahead.csv` — day-ahead wind and solar forecast (144 rows)

The day-ahead forecast (dataset DGWS, formerly B1440), `processType = day ahead`:
48 periods × three series (`Wind Offshore`, `Wind Onshore`, `Solar`).

| Column | Meaning |
|---|---|
| `publish_time_utc` | When this row was published. |
| `process_type` | `Day ahead` throughout. |
| `business_type` | `Wind generation` or `Solar generation`. |
| `psr_type` | `Wind Offshore`, `Wind Onshore` or `Solar`. |
| `settlement_date`, `settlement_period`, `target_start_utc` | The period forecast, as published. |
| `quantity_mw` | Forecast generation, MW. |

**"Day ahead" means ahead of the clock day, not the settlement day.** Periods
3–48 were published **2026-09-07T16:45:11Z**, as expected. Periods 1–2 — which
belong to the 8 September settlement day but fall on the 7 September clock day —
were published a day earlier, at **2026-09-06T16:45:03Z**. Those two periods
therefore sit at a ~31-hour lead time while the rest sit at ~7 to ~30 hours. If
you score lead time, score those two separately or exclude them and say so.

## `wind_units.csv` — the wind BM units (284 rows)

Every row of the BM unit register with `fuelType = WIND`, from 012's BMUNITS
vintage of 2026-09-11 (the same vintage 015 read). **Not** filtered to Scotland.

| Column | Meaning |
|---|---|
| `bm_unit` | Elexon BM unit id, e.g. `T_SGRWO-1`. Blank on 51 rows (see below). |
| `national_grid_bm_unit` | NGESO's id for the same unit, e.g. `SGRWO-1`. |
| `eic` | Energy Identification Code, where registered. |
| `bm_unit_name`, `lead_party` | As registered. |
| `bm_unit_type` | `T` transmission, `E` embedded, `S` supplier, `C`, `2__` aggregations. |
| `generation_capacity_mw` | Registered generation capacity, MW. |
| `gsp_group_id` | Grid supply point group, where the register carries one. Null for most transmission-connected units. |
| `north_of_b6` | `True` only where `side_of_b6` is `north`. **`False` also means "unknown"** — read `side_of_b6`, not this column, if the distinction matters. |
| `side_of_b6` | `north`, `south` or `unknown`. |
| `side_grade` | `A` CMIS intertrip arming lists the unit against B6; `B` TEC register host TO by name and capacity; `C` GSP group; `-` no graded evidence. |
| `side_basis` | The sentence justifying the grade. |
| `queryable` | `True` where the unit has an Elexon id, so `pn_final.csv` and `b1610_actuals.csv` could be asked for it. |
| `bid_paid_gbp_015` | 015's figure for what this unit was paid out on bids that day, carried across verbatim. Blank where 015 recorded no bid cashflow. |

**Where the B6 classification comes from and how far to trust it.** It is 015's
declared ladder (`side_of_b6` in `src/grid_mysteries/investigations/support_and_storage.py`),
applied unchanged to wind. 015 declared and tested that ladder for 28
energy-limited units; running it over 233 wind units is a wider use of the same
rule, and it shows: **99 north, 12 south, 173 unknown**. Of the unknowns, 51 are
the id-less rows below; the other 122 are transmission-connected units with no
GSP group in the register and no name-and-capacity match in the TEC vintage.
The ladder never guesses from a name. Grades: A 11, B 75, C 25.

**51 rows carry no Elexon BM unit id.** They are skeleton register entries —
an NGESO id and `fuelType: WIND`, every other field null. No per-unit dataset in
this pack can carry them, and querying Elexon by the NGESO id returns nothing
(tried, empty). They are kept so the wind population is not silently 233.

**⚠ `T_WLNYO-4` appears twice**, once per EIC registration (`48W00000WLNYO-4-`
and `48W00001WLNYO-4R`); otherwise the two rows are identical. The register
really does carry it twice, so neither row is dropped. **De-duplicate on
`bm_unit` before joining or summing**, or Walney 4's 330 MW and its
`bid_paid_gbp_015` both count twice. This is why the file has 284 rows, 233
with an id and 232 distinct ids, and why 015's 77 wind units with bid cashflow
appear on 78 rows here.

## `pn_final.csv` — final physical notifications (12,416 rows, 227 units)

PN for the wind BM units, all 48 periods.

| Column | Meaning |
|---|---|
| `bm_unit`, `national_grid_bm_unit` | The unit. |
| `settlement_date`, `settlement_period` | The period the segment belongs to. |
| `time_from_utc`, `time_to_utc` | The segment's start and end. |
| `level_from_mw`, `level_to_mw` | MW at the start and end of the segment. |

**PN is a series of point MW values, not a per-period level.** A period may
carry one segment or several — up to three here — and the level ramps linearly
between the two points. To get MWh for a period, integrate the segments
trapezoidally across it; the pack deliberately does not, so that whatever you
do is yours and visible.

**PN is the generator's own expectation, not a forecast of the weather.** It is
what the lead party told NESO it intended the unit to do. It already embeds the
party's commercial intent, its own wind forecast, and any position it had taken.
Treating it as a meteorological forecast will conflate all three.

**No publish or receipt time.** The dataset does not carry one, so this file
cannot by itself prove when a PN was submitted or that it is the version
standing at gate closure (one hour before the period). It is the PN Elexon
serves for the period, which is the final one.

**Five units were asked for and served nothing**: `2__NNATP001`, `2__PSMAR001`,
`C__PSMAR001`, `E_BRNLW-1`, `E_KHLLW-1`. They submitted no PN for the day.

## `b1610_actuals.csv` — metered half-hourly generation (11,136 rows, 232 units)

| Column | Meaning |
|---|---|
| `bm_unit`, `national_grid_bm_unit` | The unit. |
| `settlement_date`, `settlement_period`, `half_hour_end_utc` | The period, by number and by the instant it ends. |
| `settlement_run_type` | `II` (Interim Information) on every row. |
| `psr_type` | `Generation` on every row. |
| `quantity_mwh` | Metered volume for the half hour, MWh. |

**B1610 covers metered BM units only.** Embedded and sub-threshold wind never
appears, so this is not GB wind output — it is the output of the units that are
settled individually. Every one of the 232 queryable units was served, all 48
periods.

**Run type matters.** These are Interim Information figures, first published
five days after the day and **revised by later settlement runs**. Re-fetching
this table later may return different numbers for the same period; that is the
publisher revising, not an error. If a figure carries weight, quote the run type.

**1,849 rows are negative.** Wind BM units can meter net import (station load
when not generating). Negative is a real value, not a sign error.

## `fuelinst_wind_5min.csv` — wind outturn, five-minutely (288 rows)

Re-exported from 012's pinned FUELINST file — **not refetched** — filtered to
`fuelType = WIND` and `settlementDate = 2026-09-08`. 48 periods × 6 readings.

| Column | Meaning |
|---|---|
| `publish_time_utc` | When the reading was published (each row is published at the end of its five minutes). |
| `start_time_utc` | The instant the five-minute reading starts. |
| `settlement_date`, `settlement_period` | The period it falls in. |
| `fuel_type` | `WIND`. |
| `generation_mw` | Instantaneous metered generation, MW. |

FUELINST is transmission-metered outturn by fuel type: a third population,
different again from WINDFOR's and from the BM units in `b1610_actuals.csv`.

## `cost_context.csv` — what the day cost (14 rows)

Figures already recorded by 012 and 015, each named with the evidence file it
comes from, so nothing has to be taken on trust or recomputed.

| Column | Meaning |
|---|---|
| `figure` | The quantity. |
| `value` | As recorded. Blank where the record does not hold the figure. |
| `unit` | GBP, MWh, MW, GBP/MWh, settlement periods, BM units, or fraction. |
| `source_investigation` | `012`, `015`, `derived` (a ratio of two rows here), or `not in the record`. |
| `evidence_file` | The committed file the value is read from. |
| `note` | What the figure is and how not to misuse it. |

**Two volume conventions exist for this day and they differ a lot.** 012's own
`accepted_mwh` used DISPTAV `Original`; 015 established that `Original`
under-reads bids and that `Tagged` is the type reconciling with the day's
settlement totals. `cost_context.csv` quotes the `Tagged` figure. Do not mix
them in one calculation.

**There is no north-of-B6 share of the wind bill in the record**, and the file
says so in a row rather than leaving a gap. 015 graded sides of B6 for the 28
energy-limited units only. `wind_units.csv` applies the same ladder to wind, so
the material for such a split is here — but 173 of 284 rows are `unknown`, and
015 already found that 45 % of the wind bid money sits on units it could not
link to any support register. Any split you compute should carry those two
numbers beside it.
