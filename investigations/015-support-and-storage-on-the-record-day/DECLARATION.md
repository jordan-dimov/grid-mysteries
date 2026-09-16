# 015 — support and storage on the record day: declaration

**Frozen**: 2026-09-16 with `scripts/freeze`, witnessed by OpenTimestamps
and RFC 3161 tokens from freetsa.org and DigiCert and committed with the
proofs, before any join, split or storage table was computed. Opened on
the sponsor's instruction of 2026-09-16 (the record-day thread's two
questions). Results go in `RESULTS.md` in the six-part form; amendments,
dated, in `AMENDMENTS.md`. Unpublished until the sponsor's second seal.

## The mystery

> On 8 September 2026, Britain's most expensive constraint day, which
> support scheme stood behind the wind farms that were paid to stop, and
> what could the batteries on the system actually have done about it?

Two questions from the thread, answered with two tables and nothing else.
Investigation 012 established that £3,768,601 of the day's £33,610,463
paid out went to wind units on bids (11.2 %). This study splits that
money by the support scheme each unit holds (Bogi's question) and lays out
every energy-limited unit's registered capacity, side of the B6 boundary
and hours of energy against the constraint's duration (Nick's question).
It attributes nothing, values nothing counterfactual, and uses no
"missed revenue" language: each figure is what a public record can defend.

## Inputs already pinned (012 and 003; digests in their manifests)

- Elexon BM-unit register, 012's vintage:
  `data/raw/elexon/012/bmunits.json` (SHA-256 `2ec3f7f5…`, fetched
  2026-09-11). Fields used: `elexonBmUnit`, `nationalGridBmUnit`,
  `bmUnitName`, `bmUnitType`, `fuelType`, `generationCapacity`,
  `demandCapacity`, `gspGroupId`, `leadPartyName`.
- 8 September 2026: `data/raw/elexon/012/2026-09-08/ebocf_{bid,offer}.json`
  (EBOCF, 7,345 bid rows), `disptav_{bid,offer}_p01..p48.json` (DISPTAV,
  every `dataType`), `system-prices.json`, `mid.json` (99 files, 012's
  `deep-manifest.json`).
- NESO CMIS intertrip arming 2026-27:
  `data/raw/neso/cmis_arming_2026-27.csv` (003's reference manifest; 30
  rows; column `B6/EC5` names the boundary an armed BM unit sits behind).
- NESO TEC Register, the copy of 2026-09-15
  (`data/raw/neso/tec-history/2026-09-15_neso-ckan.csv`, journalled by
  014's live pin): `Project Name`, `Customer Name`, `HOST TO`, `Plant Type`,
  `MW Increase / Decrease`, `Cumulative Total Capacity (MW)`.

## Inputs to acquire after this freeze, under this declaration's seal

- **LCCC data portal** (`dp.lowcarboncontracts.uk`, CKAN):
  *CfD to BM Unit Mapping* (datastore resource
  `c16f141d-2db9-4160-ade1-d0d19d224dc9`; fields `CFD_Id`, `BMU_Id`,
  `Effective_From`, `Effective_date_to`; 165 rows at reconnaissance) and
  *CfD Contract Portfolio Status* (resource
  `fdaf09d2-8cff-4799-a5b0-1c59444e492b`; fields `CFD_ID`,
  `Name_of_CFD_Unit`, `Allocation_Round`, `Technology_Type`,
  `Transmission_or_Distribution_connection`, `Status`,
  `Expected_Start_Date`, `Maximum_Contract_Capacity_MW`; 612 rows), each
  with its data-type-definitions CSV and `resource_show` metadata.
- **Ofgem Renewable Electricity Register**, public reports dashboard
  (`rer.ofgem.gov.uk/Reports/Dashboard`): the *Accredited Stations (RO)*
  download, served as `RO_Accredited_Stations_<date>_05-00.csv` from
  Ofgem's SharePoint (anonymous download confirmed by a header-only
  request at reconnaissance; the dashboard page is pinned with it so the
  link's provenance is on record). Its columns are **not known** at this
  freeze and are the subject of the schema pass below.
- **Elexon Insights** MDO and MDB day streams for 2026-09-08, all units
  (`/datasets/{MDO,MDB}/stream?from=2026-09-08T00:00Z&to=2026-09-09T00:00Z`),
  the same datasets and route as BESS Study 001.

Nothing else is fetched. Everything is pinned under `data/raw/lccc/015/`,
`data/raw/ofgem/015/` and `data/raw/elexon/015/`, journalled with SHA-256
before any value is read, manifests copied to `evidence/`.

## Schema pass, then reading, in that order

The three registers acquired above get a **schema report** each
(`scripts/schema-report csv <file>` → `archives/lccc-cfd-mapping/`,
`archives/lccc-cfd-portfolio/`, `archives/ofgem-ro-stations/`: columns,
row counts, blank rates, value forms), produced and committed **before any
join is computed**. The column names the reading rules below refer to by
role (station name, capacity, technology, accreditation identifier,
BM-unit identifier, effective dates) are bound to the reports' actual
headers in `evidence/reading.json`, which cites each report's digest. If a
role has no column (for example the RO report carries no BM-unit or MPAN
identifier), the rule that needs it is reported as not applicable, not
approximated by another column.

## Prior exposure (recorded, not hidden)

012's results are known in full. At reconnaissance for this file the
author counted, from 012's pinned bytes, 77 wind units with bid rows on 8
September and their GSP groups (70 blank, 5 `_P`, 2 `_N`), and 511
register units with both export and import capability; read the CfD
mapping's and portfolio's field names and row counts, the RO report's
file name, and the July 2026 MDO record shape from BESS Study 001's pins.
No join, no cashflow split, no storage table and no B6 assignment was
computed. The thread's own claims about which scheme the paid wind farms
hold were not read as evidence.

## Part 1 — wind bids on 8 September by support scheme

**Population.** Every BM unit whose register `fuelType` is `WIND` and that
has at least one EBOCF bid row on 2026-09-08 (012's `wind` class).

**The link table** (the plan's shape: one candidate link per unit and
register, with a confidence grade and its basis, superseded only on the
record):

- **CfD, grade A** — the unit's `elexonBmUnit` or `nationalGridBmUnit`
  equals a mapping row's `BMU_Id` with `Effective_From` on or before
  2026-09-08 and `Effective_date_to` blank or on or after it. Publisher
  supplied; no name matching. The CfD unit's technology, connection and
  capacity come from the portfolio by `CFD_ID`.
- **RO, grade A** — the RO report carries a BM-unit identifier column and
  it equals the unit's. Applies only if the schema pass finds such a
  column.
- **RO, grade B** — no identifier: the normalised station name equals, or
  is a token-superset of, the normalised BM-unit name (lower-case
  alphanumerics; the tokens *wind, farm, windfarm, wf, offshore, onshore,
  energy, power, station, limited, ltd, plc, phase, extension* removed
  before comparison) **and** the station's installed capacity is within
  15 % of the unit's `generationCapacity` (or of the summed capacity of
  every BM unit that matches the same station, when a station spans
  several units).
- **RO, grade C** — the name test passes and the capacity test fails, or
  the name matches only the lead party. Reported, never counted in the
  headline table.
- **Unmatched** — everything else, reported as such with its cashflow.
- A unit linked to both CfD (A) and RO (A or B) is reported as *both* and
  counted in neither scheme's headline row.

**Per scheme (CfD, RO grade A+B, both, unmatched):** number of units;
accepted bid volume (MWh, from the DISPTAV `dataType` that reconciles with
the day's system-prices totals within 0.1 % in both directions, 013's
volume gate; if none reconciles, volumes are blank and no price is
computed); bid cashflow (positive EBOCF bid rows, £, 012's `paid_out`
convention, with the signed sum beside it); average price (£ ÷ MWh over
unit-periods carrying both, as 012); share of the day's wind bid money.
Grade C is a second table, labelled sensitivity.

## Part 2 — the energy-limited units on 8 September

**Population.** Every BM unit with at least one MDO or MDB record for
2026-09-08 (BESS Study 001's candidate rule, unit-blind). The register
does not say "battery"; the table says "energy-limited unit" and reports
`fuelType` and `bmUnitType`, and pumped storage (`fuelType` `PS`) is shown
in its own rows, not removed.

**Columns, per unit:** `elexonBmUnit`, name, lead party, `bmUnitType`,
`fuelType`; registered export capacity (`generationCapacity`, MW) and
import capacity (`demandCapacity`, MW); **side of B6** with grade;
**hours of energy**; the day's accepted offer and bid MWh (volume gate as
above) and positive offer and bid £ (EBOCF); *no rows* where the unit
has none.

**Side of B6, graded, never guessed:**

- **Grade A** — the unit appears in the CMIS arming file with `B6` (armed
  against B6: north side).
- **Grade B** — the unit links to a TEC Register row (name test as Part 1,
  capacity within 15 % of the row's cumulative capacity) whose `HOST TO`
  is `SHET` or `SPT` (north) or `NGET` (south).
- **Grade C** — an embedded unit whose `gspGroupId` is `_P` or `_N`
  (north) or any other GSP group (south).
- **Unknown** — none of the above. Reported as unknown; no unit is placed
  by its name, its lead party or its postcode.

**Hours of energy** — the unit's maximum MDO level published for the day
(MWh) divided by its registered export capacity (MW), and the maximum MDB
level divided by its import capacity, each reported twice as BESS Study
001's rungs require: **R3h**, the maximum over every record published for
the day (hindsight), and **R3p**, the maximum over records whose
`publishTime` precedes the start of the day's first constrained period
(public-as-of). A unit with MDO but no MDB, or the reverse, is *unknown* in
the missing direction, never zero.

**The constraint's duration** — the number of settlement periods on
2026-09-08 with accepted wind-unit bid volume greater than zero under the
volume gate, in hours, and the longest contiguous run of such periods.
Each unit's hours of energy are shown beside it; the table draws no
conclusion from the comparison.

## Propositions, declared before the run

- **S1 (share).** RO-linked units (grades A and B) received more of 8
  September's wind bid cashflow than CfD-linked units. Decided by Part 1's
  headline table; fails if CfD-linked cashflow is the larger, or if
  unmatched cashflow exceeds both (then the record is *not determinable*,
  which is the finding).
- **S2 (price).** The volume-weighted average bid price of RO-linked units
  exceeds that of CfD-linked units. Decided only if both groups have
  volumes under the gate.
- **B1 (coverage).** No energy-limited unit north of B6 (grade A or B) has
  an R3p export energy bound covering the constraint's longest contiguous
  run at its registered export capacity. Fails on the first unit that
  does. Units of unknown side do not decide it.

## Falsifiers of the instrument

- **F0** The RO download needs a browser session after all: the sponsor
  saves the CSV from the dashboard and it is pinned by hand with its
  digest and the dashboard page; the journal says so.
- **F1** The RO report carries no capacity column: grade B is not
  applicable, every name match is grade C, and Part 1's RO row is empty
  with the sensitivity table standing in its place.
- **F2** No DISPTAV type reconciles on the day: volumes and prices blank,
  S2 and B1 undecided, deviations reported.
- **F3** The MDO/MDB streams return no records for the day: Part 2 is
  reported as *not determinable from the public record* with the empty
  response pinned.

## Outputs

- `evidence/links.json`: every candidate link (unit, register, target
  identifier, grade, basis) — the first instance of the governed link
  table for one population.
- `evidence/wind-by-scheme.json`, `evidence/storage.json`, `evidence/reading.json`,
  the manifests, and `RESULTS.md` in the six-part form with one table each.

## What this never claims

Why any unit bid what it bid; what any unit "should" have done; any
counterfactual dispatch, saving or lost revenue; any characterisation of a
party; any placement of a unit on a boundary not graded above; that a
support scheme causes a price. 012's caveats on indicative cashflows and
013's on the volume gate apply.
