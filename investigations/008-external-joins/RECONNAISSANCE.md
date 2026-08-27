# 008 — external-data reconnaissance (2026-08-27)

**Mandate**: identify up to five public datasets not in the corpus that add an
independent economic or physical dimension to an existing Grid Mysteries
finding; inspect **schema and join feasibility only**; rank by information
gain; freeze at most two joins; return before running them. No batch of
forward candidates was generated.

**What was and was not touched.** Schemas were read from CKAN metadata and
file headers. Identity columns (unit ids, names, postcodes, technology,
status counts) were pulled into the session scratchpad to measure match
rates. **No outcome field of any proposed join was computed or joined**: no
EAC quantity or price was placed beside a unit's skip share; no Companies
House record was requested at all; no REPD or CfD milestone date was
compared with a TEC date. Scratchpad copies are un-pinned and will be
discarded; every input to a frozen join is re-fetched and digest-pinned
under `data/raw/` only after the human seal. One incidental observation is
disclosed for the record: the national 24-month constraint-cost forecast
values were visible when its header was read (24 rows, £146–531 m/month);
they are not an outcome of any join proposed here.

Corpus-side facts used below (identity only): NESO's in-merit files name
units in National Grid BMU form (`KILSB-1`, `AG-ASTK08`); the three-month
union holds **171 battery units** (63 `AG-` aggregator/additional units);
the current TEC register holds 1,498 storage rows (91 Built, 10 under
construction, 1,161 Scoping); 1,365 of 1,373 distinct TEC customer names
carry a company suffix, and 767 of 956 storage customers hold exactly one
project.

## The five datasets, as they actually are

| # | dataset | grain / size | keys it carries | history | note that matters |
|---|---|---|---|---|---|
| E1 | **NESO EAC "Response-Reserve Results By Unit"** (CKAN resource `a63ab354…`) | one row per (unit, service, product, half-hour delivery window); 1,123,536 rows live (FY 26-27); monthly archive CSVs back to launch | `auctionUnit` (= NG BMU id), `registeredAuctionParticipant`, `serviceType`, `auctionProduct`, `executedQuantity`, `clearingPrice`, `deliveryStart/End`, `technologyType`, `postCode`, `unitResultID` | kept (not overwritten) | **same unit naming as the in-merit stack** — an exact key, no resolution table |
| E2 | **DESNZ REPD** Q2 2026 (published 2026-08-03) | 14,657 rows; 2,678 Battery (178 Operational, 122 Under Construction, 1,328 Awaiting Construction) | `Ref ID`, `Operator`, `Site Name`, `Post Code`, X/Y, `Planning Authority`, dated milestones (Application Submitted / Withdrawn / Refused / Granted / Expired / Under Construction / Operational), `Storage Type`, `CfD Allocation Round` | quarterly extracts; milestone *dates* carried in each extract | no TEC id; join is by name/operator/postcode |
| E3 | **NESO constraint costs** | outturn: daily £ by boundary, 6 groups in 26-27 (ESTEX, SCOTEX, SEIMP, SSE-SP, SSHARN, SWALEX), FY files 21-22 → 26-27; DA flows/limits: 31 groups, half-hourly from 2023 (already held) | `Constraint Group`, date | kept | **the "24-month forecast by boundary" does not exist**: the published forecast is one national £m series, 24 rows × 2 columns (`Month`, `Constraint Cost (£m)`), overwritten monthly |
| E4 | **CfD**: gov.uk AR7/AR7a results (PDF/xlsx: project, region, applicant, technology, MW, strike price, delivery year, pot) and **LCCC Contract Portfolio Status** (610 contracts) | LCCC: `CFD_ID`, `Name_of_CFD_Unit`, `Allocation_Round`, `Technology_Type`, `Transmission_or_Distribution_connection` (190 T / 420 D), `Status` (396 Pre-MDD, 75 Live post-FIC, 75 Pre-Start, 51 Terminated, 13 Live pre-FIC), `Expected_Start_Date`, `Maximum_Contract_Capacity_MW` | LCCC updated monthly, overwritten | no TEC id, no postcode; ~150 of the 190 transmission units plausibly resolvable to TEC by name |
| E5 | **Companies House Public Data API** | per company: profile, filing history, charges, officers, PSC, insolvency, registered office | company number; search by name | filings dated by delivery | free API key; rate limit (600 req / 5 min) is from documentation memory, not verified on the page fetched; charge fields (`created_on`, `delivered_on`, `status`, `persons_entitled`, `classification`) likewise |

Bridge dataset, also new to the corpus: **Elexon `reference/bmunits/all`**
(3,058 BMUs): `nationalGridBmUnit` ↔ `elexonBmUnit`, `leadPartyName`,
`bmUnitType`, `generationCapacity`, `gspGroupId/Name`. 171/171 in-merit
battery units resolve; GSP group is null for 47 (mostly `AG-`/V units);
`generationCapacity` > 0 for 133 of the 155 EAC-matched battery units.

## Join feasibility measured (identity only)

| join | key | measured match | resolution cost |
|---|---|---|---|
| J1 EAC × in-merit | exact `auctionUnit` = `bm_unit` | **154 / 171 battery units (90 %)**; 57 / 63 `AG-` units; 144 matched units carry a postcode, none carries two; 283 / 584 of all in-merit units match | none |
| J2 Companies House × TEC | legal name search → company number | not measured live (no key in session); 1,365 / 1,373 customer names have a company suffix; expected ≥ 85 % on exact legal names, lower across TEC's three naming eras (F-2) | moderate: one name-resolution table, hand-checked for the top multi-project customers (Pivoted Power LLP 33, Lightsource 35) |
| J3 REPD × TEC history | fuzzy (name, operator, capacity, region) | crude token matcher on 1,498 storage rows: **348 unique, 351 ambiguous, ~800 none**; EAC postcode → REPD battery postcode: 93 / 194 exact, 181 outward-code (20 unique) | high: a curated resolution table of ~1,500 storage names plus wind/solar; compounds TEC's own identity churn |
| J4 constraint boundary × unit | none published | NESO's `exclusion_reason` says only "Behind constraint" — **no boundary is named**; GSP group (124 units) or postcode (144) must be hand-mapped to boundary zones from the network diagram | high and approximate |
| J5 CfD × TEC | fuzzy name | crude matcher on 190 transmission CfD units: 47 unique, 128 ambiguous (matcher weakness on short offshore names), 15 none; realistic ceiling ~150 after hand resolution; but the TEC archive hole (2025-07-22 → 2026-05-19) covers the AR6/AR7 contract-signature period | moderate; the sample that falls in the well-sampled window is ~60 projects (AR4/AR5) |

## The joins, ranked by information gain

Information gain = probability the answer changes an existing GM
interpretation × economic importance of that interpretation, divided by the
cost of the cheapest falsifier. Ease was not a criterion; it entered only
through the denominator.

### 1. J1 — EAC unit-level results × BM access discount (007)  — **FROZEN**

- **Existing GM dataset**: NESO in-merit + exclusion stacks (May/Jul/Aug 2026), 007's per-unit
  constraint-excluded share of in-merit value $R' = S/(S+A)$ (`DECLARATION-T3-SEPTEMBER.md`).
- **External**: E1, plus the Elexon BMU reference for capacity.
- **Key / match**: exact unit id; 154 / 171 battery units.
- **Question**: *does a battery whose in-merit BM opportunity is persistently
  non-executable for locational reasons hold a larger share of its capacity
  in Response/Reserve — i.e. is the BM access discount hedged by
  ancillary-service substitution — or does it hold the same or less?*
- **Why not obvious**: EAC procurement is national and location-blind, so a
  constrained unit faces no *access* penalty there; but Response prices have
  compressed towards £1–3/MW/h, so substitution can be real in MW and empty
  in £. Whether optimisers actually shift constrained units' capacity toward
  EAC, and whether that shift carries value, is not knowable from either
  dataset alone.
- **Decision owner**: BESS buyer / lender pricing a site; the route-to-market
  optimiser choosing the revenue stack; 007's own decision sentence
  ("diligence the executable share of BM opportunity"), which is
  incomplete if the discount is hedged.
- **Two opposing outcomes, both interesting**:
  (a) constrained units commit materially more capacity and earn more per
  MW in EAC → *the BM access discount is partly hedged*; 007's diligence
  advice must be restated as net of substitution, and "constraint destroys
  battery value" is wrong as stated;
  (b) no relationship, or constrained units are *less* present in EAC →
  *location removes BM optionality without a compensating channel*; the
  discount is unhedged and 007's decision sentence stands, strengthened.
  A third reading, (c) constrained units are more EAC-heavy but at no
  higher £/MW, is the "volume without value" case and is also decision-
  relevant (it says the hedge exists only while EAC is not saturated).
- **Cheapest falsifier**: one SQL aggregation of E1 per unit-month
  (Σ executedQuantity × hours, Σ executedQuantity × clearingPrice × hours),
  one Spearman against $R'$ across ≥ 100 matched battery units. |ρ| < 0.2
  on both MW and £ measures kills both (a) and (b) in favour of "no
  relationship".
- **Identity / data-quality risk**: 22 matched units lack a capacity
  denominator (use EAC's own maximum executed MW as the fallback,
  reported separately); `AG-` units may bundle assets (the EAC
  `technologyType` field is taken as the disambiguator); EAC half-hour
  delivery windows must be converted to MW·h consistently across products;
  a unit re-registered between months drops out.
- **Window rule**: August in-merit data taught the $R'$ cohort. The frozen
  test therefore runs on **September** alongside the 007 September test, on
  the same seal; May–August are reported as in-sample description.

### 2. J2 — Companies House SPV events × TEC date history (005/006)  — **FROZEN**

- **Existing GM dataset**: `data/derived/tec-history/project-metrics.csv`
  (7,778 project-stage rows; per-project revisions, net slip, disappearance,
  status transitions) and 006's attribution (works-led 26 %, project-led
  60 %, unattributable 14 %).
- **External**: E5 — company profile, charges, filing history, PSC.
- **Key / match**: TEC `Customer Name` → company number by exact legal-name
  search; expected ≥ 85 % on current-era names.
- **Question**: *does a publicly visible financing event at the project SPV
  — a registered lender charge — precede a fall in the project's TEC-date
  volatility, and do the 60 % of slips that 006 attributed to the project
  side cluster before such an event or in its absence?*
- **Why not obvious**: everyone assumes financial close leads to build. What
  is not known is whether close is *visible at SPV level* (charges may sit
  at the holdco), whether TEC dates keep moving *after* it (which would
  make post-close slips transmission-side and give 006's negative finding an
  independent check), and whether the charge date leads or lags the last
  TEC revision.
- **Decision owner**: lender / secondary buyer of pre-construction projects;
  NESO connections reform (whether a public financing signal could stand in
  for the "readiness" evidence Gate 2 now demands).
- **Two opposing outcomes, both interesting**:
  (a) TEC revision rate falls sharply after a registered charge → the
  Companies House charge date is a public early-warning/readiness signal,
  and 006's "project-led" bucket is largely a *pre-financing* bucket;
  (b) no change in TEC volatility after the charge, or charges are rarely
  found at the SPV → financing does not harden connection dates
  (transmission-side causes dominate post-close), or project finance is
  invisible at SPV level in GB — either is a real fact about where delivery
  risk sits.
- **Cheapest falsifier**: for the Built storage projects in 005's population
  versus storage projects Scoping for ≥ 3 years, the incidence of an
  outstanding charge at the SPV. ~200 API calls. If Built ≈ Scoping, the
  charge carries no information and the event study is not worth running.
- **Identity / data-quality risk**: customer-name changes across TEC eras
  and project transfers between customers (the F-2 lesson); holdco versus
  SPV financing; aggregators holding many projects in one company; charge
  `created_on` versus `delivered_on`; Companies House name punctuation.

### 3. J3 — REPD planning milestones × TEC history — *not frozen*

- Question: *which clock moves first when a project is in trouble —
  planning or grid?* Both answers are valuable (grid-leads → TEC archive is
  a distress signal; planning-leads → TEC dates are administrative and
  005's credibility finding sharpens), and REPD's dated milestone columns
  mean one extract carries the whole planning clock.
- Not frozen because its cheapest falsifier costs a curated resolution
  table of ~1,500 storage names against a register whose own identities
  churn, and because since the 2025-26 connections reform planning consent
  is a formal gate criterion, so the forward-looking value of "which clock
  leads" is being settled by rule; the historical question remains
  interesting and is the natural third join once J2 has built the
  customer-name resolution table it can reuse.

### 4. J4 — thermal-constraint outturn × unit-level access — *not frozen; premise corrected*

- The forward-looking version ("could the discount have been seen before
  acquisition?") needs a boundary-level forecast; **none is published** —
  the 24-month forecast is a single national series. The outturn cost by
  boundary exists (six groups, daily, since FY 21-22), and the DA
  flows/limits file (31 groups) is a better predictor, but NESO's exclusion
  reasons do not name the boundary, so unit → boundary must be
  hand-mapped from postcode/GSP group. Rather than a standalone join, the
  postcode/GSP-group location becomes a **dimension inside J1** (north/
  south of B6 as the coarsest, robust cut), which is where it earns its
  keep.

### 5. J5 — CfD award × TEC date volatility — *not frozen*

- Question is good and both outcomes matter (award hardens dates → CfD
  delivery year is a credibility signal; it doesn't → CfD de-risks price,
  not delivery; and 51 Terminated contracts give a distress subsample).
  Ranked last because the usable sample is ~60 transmission projects
  (AR4/AR5) — AR6/AR7 signatures fall inside the TEC archive hole — and
  because offshore wind slips are the population 006 found most
  works-led, so the event study is confounded by TO works from the start.
  Revisit if the EIR request fills the 2025-26 archive hole.

## Frozen for analysis

`DECLARATION-J1-EAC-SUBSTITUTION.md` and `DECLARATION-J2-SPV-FINANCING.md`.
Neither has been run. Acquisition of E1 outcome rows and any Companies House
record waits on the human seal; J1 additionally waits on NESO's September
2026 in-merit file, per `007/DECLARATION-T3-SEPTEMBER.md`.
