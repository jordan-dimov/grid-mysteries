# 025 — The exit clock. Declaration

**Written 2026-10-22 on the sponsor's instruction of that day (etrmbiz
`notes/2026-10-22-grid-mysteries-prompt-025-the-exit-clock.md` and its
addendum `notes/2026-10-22-grid-mysteries-prompt-025-addendum-joins.md`),
which opens this investigation and sets aside the milestone of 27/08/2026
("no new investigation by default") because the payer in prospect is a
regulator buying method.** Frozen by `scripts/freeze` after the schema pass
(`archives/025-exit-clock-inputs/`) and before any chain's last sighting is
read. Changes after the freeze are amendments.

## The mystery

> Ofgem is about to charge battery projects to stay in the connection queue
> on the belief that projects leave only when the bill arrives, and nobody
> has measured when they actually leave.

The question this declaration answers: **for every project that has left
NESO's TEC Register since 2014, when did it leave relative to its User
Commitment trigger date, and does the rate of leaving change as that date
approaches and passes?**

"Left the register" is the only verb used for the event. The register
records absence, not cause: it never says withdrew, terminated, cancelled
or abandoned, and nor does this investigation.

## External assertions to reconcile against, never targets

From Ofgem's CMP470 Initial Impact Assessment (17/09/2026, pinned below,
`7b80637c…`), paragraph 4.7: "Between 2023 and 2025, 72 energy storage
projects exited the connection queue or changed their technology
classification – a 6.7% reduction per year. During this period,
earlier-stage projects were more likely to exit the queue. 7.4% of projects
at the 'scoping' or 'awaiting consents' stages dropped out each year,
compared to 3% of projects with approved consents. No projects at the
construction stage exited the queue." Paragraph 2.5: the Workgroup "noted
there was insufficient data from network operators to directly quantify the
benefits and costs". Paragraph 6.5: "we do not have data or analysis to
support this assumption". Paragraph 2.8: NESO provided Ofgem with "a list of
all battery energy storage systems (BESS) projects with Gate 2 status,
including information on their current and maximum securities and
liabilities, connection capacity, and connection date", "similar data on the
connection queues in 2023, 2024, and 2025 for all technologies, excluding
data on their current and maximum securities and liabilities", and
"aggregate data on the number of BESS project terminations and the total
Cancellation Charges issued".

From the minded-to consultation (pinned, `77a9e724…`), page 5: "around 58%
of BESS projects capacity has not passed the 'trigger date' (three years
before energisation) ... while only around 16% has both passed the trigger
date and secured planning consent"; footnote 1: "The trigger date is
generally 1 April three financial years ahead of project energisation. See:
CUSC Section 15 - User Commitment Methodology v1.13 (21 January 2026)".

These figures are recorded so that the reconciliation below can be set
beside them. Nothing here is tuned to meet them.

## Prior exposure, stated

- **The sponsor's unsealed probe** (feasibility note of 22/10/2026, from
  005's identity table, project-stage identities, no stitching, no transfer
  split): energy storage identities vanishing per year 150 (2020), 89, 277,
  305, 545 (2024), 283 (to July 2025); of storage disappearances with a
  connection date, 881 last seen more than a year before the implied
  trigger, 182 within the year before, 172 within the year after, 455 more
  than a year after. The note itself says these are identities, not
  projects, and not a finding. They are the only exit-shaped figures the
  author has seen, and they are recorded here so that the result can be
  judged against them rather than steered by them.
- **The schema pass of this investigation** (`archives/025-exit-clock-inputs/
  schema-report.json`, SHA-256 `fa3cbb802f61d3b6…`; `SCHEMA.md` beside it),
  which read every copy's columns, blank rates, chain keys and the
  continuity of keys between consecutive kept copies, as aggregates: 793
  usable copies 2014-01-31 to 2026-10-20, 791 kept under 014's
  partial-export rule (2015-05-08 and 2023-11-28 excluded); the largest gap
  between consecutive copies is **95 days** (2014-07-04 to 2014-10-07 and
  2026-05-19 to 2026-08-22); three copy pairs lose more than half their
  keys (2020-06-05, the Stage column's arrival with re-spelt sites;
  2021-11-26, Project ID's arrival; 2022-08-24, the `a03` to `a0l` id
  re-issue) and sixteen pairs lose more than 5 %; over the other pairs the
  median share of keys absent from the next copy is 0.06 % and the 99th
  percentile 6.4 %. The stitch tiers below were chosen by their outcome at
  those pairs, counts only (every tier's count is in the report). The copy
  of 2024-01-05 is **not** a re-keying (0 of 1,452 ids absent); the
  Eggborough certificate of 017 shows one project's id changing there with
  its customer, capacity and technology, which the stitch below treats as
  one chain.
- **The author's looks at rows**, made to write the stitch and not
  recorded as figures: six vanished and six appeared rows at each of
  2020-06-05 and 2022-08-24 (sites re-spelt, customer case changed, sites
  blank in the re-issue copy); twelve storage rows of the copy of
  2026-09-15, twelve battery rows of the REPD extract, twelve storage CMU
  rows and six storage component rows, to see the forms of names, operators
  and locations the join keys compare.
- **Ofgem's figures above**, read in the documents pinned here.
- No chain's last sighting has been read; no exit, band, hazard or join has
  been computed.

## Sources

### The register

The archive of NESO's TEC Register as the repository holds it: the
journalled copies (`data/raw/neso/tec-history/journal.ndjson`, 005's
archive extended by FOI/26/216 and live pins) and the daily capture's copies
(`data/manifests/*.ndjson`, mirrored under `data/raw/archive/`), read
together by `grid_mysteries.tec.sources.copies` (one copy per publication
date, 014's reading rule). **The series ends at the copy of 2026-10-20**,
the last copy in the schema report; copies published after it are not read
under this declaration, so that the result does not move with the capture.
Every copy's bytes are checked against its recorded digest before it is
read (C1).

### Rules documents and the joins' files, pinned 22/10/2026

All fetched by `run.py --phase acquire` on the sponsor's instruction,
journalled and verified against `evidence/sources-manifest.json` (SHA-256
`55f47fb98d19e50b…`); a pinned file is never refetched or overwritten.

| dataset | path | SHA-256 | bytes |
|---|---|---|---|
| Ofgem, CMP470 minded-to consultation (17/09/2026) | `data/raw/ofgem/025/CMP470-Minded-to-Consultation.pdf` | `77a9e72470b7…` | 4,404,300 |
| Ofgem, CMP470 Initial Impact Assessment (cover says Initial; file named Interim) | `data/raw/ofgem/025/CMP470-Interim-Impact-Assessment.pdf` | `7b80637c5c58…` | 594,420 |
| Ofgem, consultation page | `data/raw/ofgem/025/cmp470-consultation-page-2026-10-22.html` | `0b1a985c3fea…` | 202,942 |
| NESO, CUSC Section 15 User Commitment Methodology, **v1.14, 09/09/2026** | `data/raw/neso/025/cusc-section-15-user-commitment-methodology-2026-10-22.pdf` | `6bf040ba18e1…` | 575,434 |
| NESO, CUSC Exhibit MM1 Cancellation Charge Statement v5 | `data/raw/neso/025/cusc-exhibit-mm1-cancellation-charge-statement-2026-10-22.pdf` | `663761272f87…` | 193,497 |
| NESO, CUSC Exhibit MM2 Cancellation Charge Secured Amount v4 | `data/raw/neso/025/cusc-exhibit-mm2-cancellation-charge-secured-amount-2026-10-22.pdf` | `a86bb3e2c25f…` | 183,053 |
| NESO, securities freeze letter, 15/01/2026 | `data/raw/neso/025/securities-freeze-letter-2026-01-15.pdf` | `b4980e764b90…` | 177,222 |
| NESO, CUSC code documents page | `data/raw/neso/025/cusc-code-documents-page-2026-10-22.html` | `78a59dacc4e7…` | 1,262,859 |
| NESO, connections reports and registers page | `data/raw/neso/025/reports-and-registers-page-1-2026-10-22.html` | `8ff1452824b0…` | 1,311,351 |
| NESO, Wider Cancellation Charge Statements 2012-13 to 2024-25 (thirteen) | `data/raw/neso/025/wider-cancellation-charge-statement-<year>.pdf` | in the manifest | |
| DESNZ, Renewable Energy Planning Database, July 2026 (Q2) extract | `data/raw/desnz/025/REPD_Publication_Q2_2026.csv` | `84c1b5f958a9…` | 5,087,389 |
| DESNZ, REPD publication page | `data/raw/desnz/025/repd-quarterly-extract-page-2026-10-22.html` | `bad8461436f8…` | 106,028 |
| NESO, Capacity Market Register, CMU file of 21/10/2026 | `data/raw/neso/025/capacity-market-register-cmu_20261021.csv` | `ff7879b0f161…` | 8,765,493 |
| NESO, Capacity Market Register, components file of 21/10/2026 | `data/raw/neso/025/capacity-market-register-component_20261021.csv` | `c04cdef6ba32…` | 8,326,681 |
| NESO, Capacity Market Register, CMU history of 21/10/2026 | `data/raw/neso/025/capacity-market-register-cmu_changes_20261021.csv` | `de3aea8a4e84…` | 10,979,985 |
| NESO, Capacity Market Register package metadata | `data/raw/neso/025/capacity-market-register-package-show-2026-10-22.json` | `6db67d4039df…` | 14,743 |

**Departures from the prompt, recorded.** The prompt names Section 15
v1.13 (21/01/2026); the version NESO serves on 22/10/2026 is v1.14
(09/09/2026, CMP476, described by NESO as a correction). The trigger-date
clause quoted below is read from v1.14; Ofgem's footnote reads the same
rule from v1.13. The prompt asks for the Wider Cancellation Charge
statement series; NESO's listing ends at 2024-25 (published 31/01/2024),
and the letter of 15/01/2026 says NESO froze the biannual securities
process for 1 April to 30 September 2026 and that "the Wider Cancellation
Charge will not be triggered during this period or be increased if it has
already been triggered". No 2025-26 or 2026-27 statement was found; the gap
is recorded, not filled.

### Schema reports cited

- `archives/025-exit-clock-inputs/schema-report.json` `fa3cbb802f61d3b6…`
  (the register: copies, keys, continuity, vocabularies).
- `archives/tec-register/schema-report.json` `8404e69a2abbec6a…` (the
  archive's standing report: eras, date spellings, status vocabulary).
- `archives/025-repd-2026-q2/schema-report.json` `bc5bacb7c69eb600…`
  (14,657 rows, 53 columns; 2,678 rows with Technology Type `Battery`).
- `archives/025-cmr-cmu/schema-report.json` `a9ce834d28542b6e…` (18,203
  rows, 78 columns; 3,110 with Primary Fuel Type `Storage - Battery`).
- `archives/025-cmr-components/schema-report.json` `1f7d22c8b1958797…`
  (29,840 rows, 18 columns).
- `archives/025-cmr-cmu-history/schema-report.json` `9b155e2cc78e3346…`
  (72,433 rows, 10 columns; not read by any rule below, pinned for the
  record).

## Reading the register, declared now

- **Copies.** The kept copies are 014 version 4's: one copy per
  publication date; the partial-export rule excludes a copy whose row count
  falls by more than a fifth against the previous kept copy when the next
  copy recovers by more than a fifth (two copies excluded, above); the
  swap test of `connection_slippage` decides per copy whether day and month
  are read exchanged.
- **Columns**, by their canonical names (`tec_register.ALIASES`): Project
  ID, Project Number, Project Name, Customer Name, Connection Site, Stage,
  Project Status, Plant Type, Agreement Type, HOST TO, MW Increase /
  Decrease, Cumulative Total Capacity (MW), MW Effective From, Gate. Dates
  by `parse_date` (every spelling in the archive report). Text by
  `normalise` (lower-case alphanumerics, single spaces; 005's rule).
- **Status words**, as printed, grouped by `status_family`: Scoping,
  Awaiting Consents, Consents Approved (with the four `Consented` cells),
  Under Construction/Commissioning, Built; `Terminated` (431 cells,
  2015 to 2021), `Active` (110 cells) and blank are kept as printed and
  reported as their own families.
- **Plant family** (`plant_family`): **storage-only** when every technology
  the cell prints is `Energy Storage System` or `Battery Storage`;
  **storage-mixed** when storage is printed with others; **other**; blank.
  **"Storage"** below means storage-only or storage-mixed; storage-only is
  reported beside it throughout.
- **Agreement family** (`agreement_family`): `Direct Connection`,
  `Directly Connected` and `BCA` are **directly connected**; `Embedded` and
  `BEGA` are **embedded**; blank and `Null` are blank.

## Identity, declared now

- **I1. The unit is the chain.** A project is a chain of register rows
  across copies. A chain may hold several rows in one copy (stages); the
  chain is what leaves or stays. Stage rows that vanish while the chain
  stays are reductions, not exits, and are counted beside.
- **I2. The key within a copy.** In the Project ID era (copies dated
  2021-11-26 or later) the key is the Project ID on its 15-character form
  (017's rule); a row printing no id (one row, in one copy) is keyed by its
  triple and marked. Before the ID era the key is 005's normalised triple
  (project name, customer name, connection site).
- **I3. Continuity.** A chain continues from one kept copy to the next
  kept copy when its key is printed in both.
- **I4. The stitch.** At every pair of consecutive kept copies, the chains
  whose key is printed in the earlier copy and not the later (*vanished*)
  are matched to the chains printed in the later and not the earlier
  (*appeared*), tier by tier, strictest first, on a signature over each
  chain's rows (the sorted tuple of per-row features, so a two-stage project
  matches a two-stage project): **(0)** Project Number, where printed on
  both sides; **(1)** name, customer, site, stage and cumulative MW;
  **(2)** name, site, stage; **(3)** name, customer, stage; **(4)** name,
  customer, site; **(5)** name, stage, cumulative MW; **(6)** customer,
  site, stage, cumulative MW; **(7)** name alone. Within a tier a signature
  shared by exactly one vanished and one appeared chain is a match and
  both leave the pool; a signature shared by several on either side is left
  to the next tier. A matched appeared chain continues the vanished chain.
  An appeared chain matched on no tier is a new chain. A vanished chain
  matched on no tier is, at that pair, a candidate departure (E1 decides),
  **except** at a re-keying pair, where it is **not determinable**.
- **I5. Re-keying pairs** are the pairs in which more than half of the
  earlier copy's keys are absent from the later copy: 2020-05-28 to
  2020-06-05, 2021-11-23 to 2021-11-26 and 2022-08-19 to 2022-08-24
  (schema report). A departure cannot be evidenced by a copy that re-keys
  everything, so a vanished chain unmatched there is not determinable and
  is carried neither as an exit nor as a survivor; it is counted and its
  share reported.
- **I6. A change of customer name or holder does not end a chain** when
  tiers 0, 2, 3, 5 or 7 match it (they do not read the customer); the
  change is recorded on the chain. In the ID era the id itself carries the
  chain through any name change. 019's rename-or-transfer classes are
  reported on the chains whose names 019 resolved; nothing new is resolved
  here.
- **I7. Reclassification.** A chain whose plant family differs between two
  of its sightings is a **reclassification**, counted and reported, never
  an exit.
- **I8. Not determinable, by era.** The share of chains whose continuation
  is not determinable (I5, and chains ambiguous at every tier) is reported
  per era: before 2021-11-26 and from it. **Kill (a):** if the ID-era
  share exceeds 10 %, the investigation stops and says so.
- **I9. Gaps.** A chain absent from one or more kept copies and printed
  again later under its own key is one chain; its absence is recorded as
  an interruption, not an exit. The stitch matches consecutive copies only;
  a chain that returns under a different key after an absence is a new
  chain (reported as such, with the count of returning signatures as a
  check).

## Exit, declared now

- **E1.** A chain **left the register** when its last sighting is in a
  kept copy at least **N = 95 days** before the series end (2026-10-20),
  that is on or before **2026-07-17**, and no kept copy after the last
  sighting prints its key or a stitched continuation, and its Project
  Status at last sighting is not `Built`. N is the archive's largest gap
  between consecutive copies (schema report).
- **E2.** A chain whose last sighting is after 2026-07-17 is **open**: not
  an exit, not a survivor; counted.
- **E3.** A chain whose status at last sighting is `Built` **completed**;
  its leaving is not an exit (the register clears built projects; 017).
- **E4. The exit month** is the calendar month of the **exit copy**, the
  first kept copy after the last sighting. The **last sighting** is also
  reported; the gap between the two is the register's resolution at that
  date.
- **E5.** Nothing is said about why any chain left.

## The clock, declared now

- **K1. The rule as published.** CUSC Section 15 v1.14, Part Two,
  paragraph 2.2: "The Trigger Date will be (a) the 1 April which is three
  Financial Years prior to the start of the Financial Year in which the
  Charging Date occurs or (b) where the Charging Date is less than three
  Financial Years from the date of the Construction Agreement, the date of
  the Construction Agreement". Paragraph 2.3: "The Trigger Date is the date
  from which the Wider Cancellation Charge applies". The register prints
  neither the Charging Date nor the Construction Agreement date. **This
  investigation reads `MW Effective From` as the Charging Date and applies
  branch (a) only**: trigger = 1 April of (the calendar year in which the
  financial year holding the connection date begins, minus three)
  (`trigger_date`). Branch (b) and any contractual variation are the
  caveat the expert corner carries: the trigger reconstructed here is the
  rule of thumb Ofgem itself uses ("generally 1 April three financial years
  ahead"), not the contractual date.
- **K2. Clock A** (headline): the trigger from the connection date printed
  in the copy of last sighting. **Clock B**: from the connection date in
  the chain's first copy. **Clock C** (exposure only): the trigger from the
  connection date printed in each copy, so that a chain's position on the
  clock moves as its date moves; under C an exit's band is the band at its
  last sighting, which is clock A's.
- **K3. Bands**, for an event or an exposure month at date d with trigger
  T (`band`): more than 24 months before (d < T by 24 whole months or
  more); 12 to 24 months before; 0 to 12 months before; 0 to 12 months
  after (d on or after T, less than 12 whole months after); more than 12
  months after; and **no connection date**. Whole months by
  `months_between`.
- **K4. Exposure.** A chain is at risk in every calendar month from the
  month of its first sighting to the month of its last sighting inclusive
  (gaps between copies included: the register's silence is not the
  project's absence). Each exposure month is placed in a band under each
  clock; exits are placed in the band of their exit copy's date.
- **K5. Hazard** per band = exits ÷ chain-months at risk, with a 95 %
  interval by Byar's approximation to the exact Poisson interval (lower
  k(1 − 1/(9k) − 1.96/(3√k))³, upper (k+1)(1 − 1/(9(k+1)) +
  1.96/(3√(k+1)))³, divided by exposure; lower 0 when k = 0). Hazards are
  per chain-month and also shown per hundred chain-years (× 1,200).
- **K6. Flatness** (kill (c)): the hazard by band is **flat within its own
  uncertainty** when the five bands' intervals share a common value (the
  largest lower bound is at or below the smallest upper bound). Tested on
  storage, old regime, clock A. Flat is a finding, not a failure.

## Strata, declared now

Every table is cut by: **S1** plant family (storage against other;
storage-only beside); **S2** status family at last sighting; **S3**
agreement family at last sighting; **S4** HOST TO at last sighting, as
printed; **S5** first-observation cohort (calendar year of first sighting;
chains first seen in the first copy, 2014-01-31, are the "2014 opening"
cohort, since their true first sighting is unknown). Storage is the
headline; the rest is the control.

## Regimes, declared now

- **R1.** Copies dated 2025-12-01 or later are the **reformed regime**
  (014's break). An exit whose exit copy is dated 2025-12-01 or later is a
  reformed-regime exit; exposure months from December 2025 are
  reformed-regime exposure. The old-regime series runs from January 2014 to
  November 2025.
- **R2.** Reformed-regime exits are reported separately with the Gate
  column at last sighting; they are not pooled with the old regime in any
  hazard.
- **R3.** The register's row count through the Gate 2 reset (2,236 on
  2025-11-04, 2,229 from 2025-12-05) is reported as an observation beside
  the reformed-regime exits.

## Reconciliation to Ofgem, declared now

- **O1. Annual snapshots.** Ofgem had the queue at annual intervals. Four
  snapshot copies: the first kept copy on or after 1 January of 2023, 2024
  and 2025, and the last old-regime copy (2025-11-28). For each snapshot
  and status family, the storage chains present; of them, the share that
  left (E1) with last sighting before the next snapshot, and the share
  reclassified (I7) between the snapshots. Reported beside Ofgem's 72,
  6.7 % a year, 7.4 % / 3 % / 0 %.
- **O2.** Storage exits with exit copy in 2023-01 to 2025-11, by status
  family; and the number of reclassifications among storage chains in the
  same window, so that "exited or changed classification" can be read as
  two numbers.
- **O3.** Nothing is adjusted to meet 72; a difference is reported as a
  difference, with the candidates that explain it (snapshot dates,
  classification, co-located storage, embedded projects below the
  register).

## Joins, declared now (addendum of 22/10/2026), run after the series

Each join classifies exits only; it never changes whether a chain left.
Each is run on **storage exits of the ID era** first, with its matched
share; the addendum's threshold applies: **if REPD or Capacity Market
matching covers fewer than 70 % of storage exits in the ID era, the matched
subset is reported and the join stops there.** Company names are compared
by `companies_house.normalise_company_name`; places by **place tokens**:
the normalised words of four letters or more that are not in the stop list
(`bess, battery, batteries, energy, storage, system, systems, facility,
farm, solar, wind, power, station, substation, grid, national, road, lane,
land, site, project, limited, ltd, park, extension, phase, tertiary, north,
south, east, west, new, connection, generation, renewables, renewable,
plant, works, development, developments, holdings`).

- **J1. REPD** (rows with Technology Type `Battery`). Key: **(a)** customer
  equals operator as company names **and** the chain's project name and
  the REPD site name share a place token; **(b)** place token shared
  **and** REPD Installed Capacity within 1 MW of the chain's stage MW at
  last sighting; **(c)** customer equals operator and the REPD row is the
  operator's only battery row. A key accepted only when it names exactly
  one REPD row; several rows is **ambiguous**, none is **unmatched**.
  Coordinates are not used: the register prints none and no public
  gazetteer of connection sites is held; the addendum's tiebreak is
  recorded as not available. Classes at the exit month m (the first day of
  the exit copy's month): **refused, withdrawn or expired before exit**
  when `Planning Permission Refused`, `Appeal Refused`, `Planning
  Application Withdrawn`, `Appeal Withdrawn` or `Planning Permission
  Expired` is dated before m and no grant is dated after that and before
  m; **abandoned** when Development Status (short) is `Abandoned` (undated
  in the extract); **consented at exit** when `Planning Permission
  Granted`, `Appeal Granted` or `Secretary of State - Granted` is dated
  before m and no refusal, withdrawal or expiry falls between it and m;
  **application pending at exit** when submitted before m with no decision
  before m; **no event before exit** otherwise; **no planning record** when
  unmatched.
- **J2. Capacity Market Register** (CMU rows with Primary Fuel Type
  `Storage - Battery`, with their components by CMU ID). Key: **(a)**
  applicant or parent equals customer as company names **and** the CM Unit
  Name or a component's Location and Post Code shares a place token with
  the chain's project name or connection site; **(b)** applicant or parent
  equals customer **and** Connection or DSR Capacity within 1 MW of the
  chain's stage MW; **(c)** place token shared **and** capacity within
  1 MW. Accepted when the key names exactly one CMU ID (all its delivery
  years). Classes at m: **agreement held at exit** when any row of the CMU
  has Capacity Agreement Awarded `Yes`, Date of Issue before m, and is not
  terminated before m; **terminated before exit** when Capacity Agreement
  has been Terminated `Yes` with Date of Termination before m (months
  between, signed, reported); **terminated after exit**; **never held**
  when matched but no agreement awarded; **no record** when unmatched.
- **J3. Companies House**, refreshed from 019's join. For each exit chain
  the customer name at last sighting is looked up in 019's held links
  (`investigations/019-who-holds-the-queue/evidence/links.ndjson`, rule
  version `019-r2-v2`, run 2026-09-30, with its admissions); names 019 did
  not resolve are **not linked** (nothing new is resolved here). For every
  linked company number the profile and charges are fetched once at run
  time, pinned under `data/raw/companies-house/<run date>-025/`, journalled
  and digested, with the key the repository already holds; this fetch is
  authorised by the addendum ("refreshed from 019's join at run time").
  Classes: **dissolved within twelve months of exit** (`date_of_cessation`
  within twelve months after m, either way of m counted separately: before
  and after); **live charge at exit** (a charge created before m and not
  satisfied before m); **neither**; **not linked**.
- **J4. DNO Embedded Capacity Registers.** Recorded as a source (the held
  SSEN register of September 2026, `archives/ssen-ecr*`); **not run**: the
  reformed series is eight months of copies and the addendum leaves the
  join as a candidate until it is long enough. Entered in CANDIDATES.md.
- **J5. Outputs added.** The hazard-by-band table split by J1 class and by
  J2 class (storage, old regime, clock A); the termination-against-exit
  timing table (months between a Capacity Market termination and the exit
  month, signed); the share of exits with a live charge at exit; and in the
  appendix every chain's **join key for Ofgem**: project name, customer
  name, connection site, Project ID and Project Number where printed, and
  MW, each as printed at first and at last sighting.
- **J6. Validation to request, not compute.** An EIR request to NESO for
  the monthly count of terminated connection agreements and cancellation
  charges issued since CMP376 took effect is drafted as
  `EIR-REQUEST-NESO-TERMINATIONS.md` for the sponsor to send; nothing is
  sent from here.

## Checks each run must pass, or it stops

- **C1** Every copy read hashes to its recorded digest; the series ends at
  2026-10-20 and no later copy is read.
- **C2** The schema report cited above hashes to `fa3cbb802f61d3b6…`; the
  pinned documents and join files hash to the manifest.
- **C3** Every chain is in exactly one of: exit, open, completed (Built),
  present at series end, not determinable; the classes sum to the chains.
- **C4** Every exit is in exactly one band under each clock; bands sum to
  exits; exposure months sum to the chains' spans.
- **C5** The per-chain lines (`evidence/chains.ndjson`, held) are a pure
  function of the inputs: a line already on disk that would change on
  recompute stops the run (the runner refuses to change a committed row).
- **C6** Every join match names exactly one row or CMU; the classes of a
  join sum to the exits it was run on.

## Falsifiers and kill conditions, declared in advance

- **(a)** The ID-era not-determinable share exceeds 10 %: stop and say so.
- **(b)** Fewer than 200 storage exits (E1) in the old regime: the series
  is reported as thin and no hazard is called a pattern.
- **(c)** The hazard by band is flat within its own uncertainty (K6): a
  finding, published as such.
- **(d)** The 70 % threshold on the joins (above).
- **F1** If the reconciliation (O1) gives a storage exit count for 2023 to
  2025 that differs from Ofgem's 72 by more than a factor of two in either
  direction after reclassifications are added back, the difference is the
  headline of the reconciliation section and the candidates in O3 are
  reported, none asserted.

## What this never claims

- Securities posted or liabilities accrued by any project (only NESO and
  the TOs hold them). The clock is the published rule applied to a printed
  date.
- Why any chain left. A termination under CMP376 milestones, a
  withdrawal, a reclassification that changed key, a merger into another
  agreement and a re-offer look the same in the register unless the stitch
  catches them.
- Anything about projects below the register's threshold or never on it.
- That bunching, if seen, is caused by securities. Consents, Gate 2 and
  CMP376 milestones fall on the same clock; the strata are a partial
  answer, not a full one.
- No project is named in FINDINGS beyond the appendix.

## Second phase: the zone mapping, decided now

The Wider Cancellation Charge statements price by zone codes (A1 to T6 in
2024-25, 96 zones) that refer to ETYS Appendix A diagrams; NESO publishes
no list of connection sites by zone, and the only public zone geometry
found (the GIS boundaries of the 27 TNUoS generation charging zones) is a
different zoning. **The gap is recorded and the second phase stops here.**
No liability profile is reconstructed.

## Forward

A watch is raised in the research record on freeze: **w-025-monthly-exit-
series**, due monthly from 30/11/2026, reading: the series extended by the
copies the capture has added since the last reading, under this
declaration's rules, each reading appending exits to the held lines (C5).
Candidate entered in CANDIDATES.md, not opened: exits in the reformed
regime by Gate once the reformed series is long enough; J4 with it.

## Order of work

1. This file is frozen. 2. Format check (`--phase format`): every copy's
and every pinned file's format as the readers depend on them, against the
schema reports. 3. Compute under the seal (`--phase compute --seal`),
archive and pinned files only, Companies House fetch excepted (J3). 4.
Joins (`--phase joins`). 5. Render (`--phase render`, `--phase figures`).
6. FINDINGS to the sponsor before anything public; nothing to Ofgem or the
introducer until sealed. Time box: two working days for 3 to 5, one more
for the joins; if stitching eats the first day, stop and report.

## Outputs

Held out of the public repository until the sponsor says (they name
projects and companies): `evidence/chains.ndjson` (append-only, every
chain with every sighting run and its join key), `evidence/exits.ndjson`,
`evidence/joins.ndjson`, `FINDINGS-APPENDIX.md`. Committed: this file and
its proofs, `evidence/sources-manifest.json`, `evidence/acquisition-log.json`,
`evidence/format-check.json`, `evidence/results.json` (aggregates only),
`evidence/rule-sources.json`, `evidence/run-log.json`, `FINDINGS.md`,
`figures/captions.md`, the code and its tests.
