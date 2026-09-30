# Dated public sources on the offer side of a grid connection

*Research note, 30/09/2026, item D of the etrmbiz data-quality plan. It
inventories where a project's connection offer, agreement or expected
energisation is publicly dated independently of NESO's TEC Register, and
records which of the four watch-list projects has such a source. It draws
no conclusion about lags; it is the inventory the offer-lag candidate in
`investigations/CANDIDATES.md` said was missing. Desk research by a
research agent under this session's instruction, every dated fact carrying
the URL it was read at and the date the page prints (or "read 30/09/2026"
where it prints none); items the agent could not confirm on a fetched page
are marked UNVERIFIED and stay so here. Nothing was pinned into the
archive; the fetched files sit in a scratch directory and are not
evidence. **Section 1 names the watch-list projects; it is for the
sponsor before anything leaves the repository.***

## The practitioner's number, and what NESO says

The number to test: about three months from signing to the register,
"very random" (a practitioner, by role only; etrmbiz slot
`gb-tec-register-lag-after-signing`).

What NESO has said in writing, all public:

- Data portal page, read 30/09/2026: update frequency "Twice weekly"; the
  Gate column "will be populated once agreements have been countersigned.
  Until that point, the field will remain blank"; "some data correction
  updates may take longer than usual while a temporary data change
  governance process is in place to support Connections Reform".
- FOI/25/199, 14/01/2026: "The TEC Register is published twice weekly, and
  is updated when contracts are signed or terminated, and when
  contractual milestones are met."
- FOI/26/173 and FOI/26/175, both 16/09/2026 (PDFs read this session,
  kept locally at `data/raw/neso/foi-responses/`, SHA-256 `b70a0ffc…` and
  `4558dd13…`): "published twice weekly, and is updated when contracts are
  signed, modified or terminated, and when it is confirmed to us via
  established channels that contractual milestones are met." FOI/26/173
  also refuses project-level information on applications, offers,
  renames and transfers under EIR regulation 12(5)(e), and describes the
  Existing Agreements Register as "a static dataset (i.e., it will not be
  updated)" of Gate 2 applicants that "does not outline any outcomes".
- Historic: CUSC amendment proposal CAP068 proposed that offers "shall be
  recorded on the TEC Register within 5 Business Days of such offers being
  made". Whether the current CUSC 6.30.3 still binds the register to any
  interval was **not verified** (current text not fetched).

**No public NESO statement quantifies the interval between a
countersignature and the register printing it.** Nothing found supports
or refutes three months. The register's own words say *signed, modified,
terminated, milestone confirmed*, which is a list of triggers, not a
clock.

## Generic sources, by what they date

| source | what it dates | offer date itself? | notes |
|---|---|---|---|
| **Capacity Market Register** (NESO data portal, weekly; CMU file 18,191 rows, 70 columns on 30/09/2026) | `Date of Issue of Capacity Agreement`; `Earliest`/`Latest Date SCM is expected to be achieved`; `Long Stop Date for the Minimum Completion Requirement`; `Date for provision of deferred Connection Agreement`; `Date for provision of deferred TEC`; flags for connection-agreement and TEC deferral | **No.** It dates the CM agreement and the applicant's expected completion window; the deferral columns date when a connection agreement or TEC *must be shown*, for applicants that deferred | The **CMU History** file is a change log (`Attribute`, `Previous`, `Latest`, `Change Date`) from its first release on 10/12/2025, so changes to SCM dates are themselves dated from then on. Download needs a browser user-agent. Not in the capture plan today. |
| **Planning portals** (Idox: Tameside, Lancaster verified; North Ayrshire layout not verified) and the **Scottish Energy Consents Unit** (Section 36, cases determined from 01/06/2016) | received, validated, committee, decision-issued and permission-expiry dates; ECU prints received and determined dates | No | Committee reports sometimes describe the connection programme in words ("delays to the grid connection programme", Tameside 26/00396/FUL report) without a date. |
| **NESO Existing Agreements Register** (xlsx, "last updated 11/6/25", 3,475 data rows; the repository's pinned copy of 18/09/2026 has 3,397 after blank rows, `archives/neso-ea-register/`) | `Existing Connection Date` per project name and connection point | No; it is the pre-reform register date, printed once and never updated | Inclusion is by developer consent, so absence says nothing (two of the four watch projects are absent). No customer name. |
| **Connections-reform results** (NESO PDF, aggregated by zone and technology; NGET Clearview, regional) | nothing per project | No | "does not reflect updates on the progression of specific customer connections" (NESO page). |
| **DNO outcome files**: NGED "Projects Connections Reforms Outcomes" (CSV, 879 rows, updated 09/07/2026, yearly) | `DNO_Acceptance_Date`, `Customer_Acceptance_Date`, `TQE_Date`, `Firm_Connection_Date`, `Non-Firm_Connection_Date`, Gate and phase outcomes; dates as Excel serials | **Yes, for distribution offers**, but anonymised: no project or customer name | The only file found that carries offer-side acceptance dates. SSEN publishes guidance only; UKPN and ENWL pages were not readable (403 or not fetched); UNVERIFIED. Already inventoried for demand in `DEMAND-CONNECTION-SOURCES.md`. |
| **Ofgem generation-licence notices** | application and grant dates per company | No | A dated corporate milestone, useful as a bound. |
| **Company announcements and RNS** (Investegate, company news pages) | whatever the company chooses: acquisition, "expected to connect no later than…", financial close, notice to proceed, COD guidance, sale process | Sometimes a *stated* connection date, never the offer date or its signing date | Secondary coverage is not adopted; the RNS itself must be read. |
| TNUoS forecasts and charging statements; REMIT | not checked; REMIT covers operating assets | UNVERIFIED as sources | |

So the offer side is publicly dated only indirectly: by the Capacity
Market's agreement and completion-window dates, by planning decisions, by
licence grants and by what the developer says. **No public source states
when a connection offer was made or signed**, and NESO refuses that per
project. The register's lag behind the offer is therefore measurable
publicly only (a) where a developer publishes the date, or (b) against a
dated proxy such as a Capacity Market SCM change, from 10/12/2025 onward.

## The four watch-list projects

Public facts only, each with its source and date; the register's readings
are from the daily capture (`data/derived/tec-watch/`, private) and from
scratch reads recorded as prior exposure in `CANDIDATES.md`.

### Zenobe Stalybridge Project (150 MW, Stalybridge 275 kV, NGET)

- Register: 30/09/2027, Scoping, Gate blank, unchanged across the five
  captured copies (15/09 to 29/09/2026).
- Existing Agreements Register ("last updated 11/6/25"): 167.4 MW,
  existing connection date **30/09/2026**, Stalybridge 275kV. So the
  register moved the date a year later between mid-2025 and August 2026;
  the scratch read in `CANDIDATES.md` says the journal's copies print
  September 2026 up to July 2025 and September 2027 from August 2026.
- Planning (Tameside): 23/00770/FUL approved, decision issued
  **15/12/2023**; variation 26/00396/FUL approved **28/07/2026**, whose
  committee report says the applicant cited "delays to the grid connection
  programme" and needs a lawful start before the permission expires on
  15/12/2026. The report prints no connection date.
- Capacity Market: two CMUs (150 MW 2-hour for 2026/27 T-4; 75 MW 4-hour
  for 2027/28 T-4), both "Not Prequalified"; no agreement, no dates.
- Companies House: company 14299411, incorporated 16/08/2022, no previous
  names shown.
- Developer statements: none found naming Stalybridge (UNVERIFIED that
  none exists).
- **Dated offer source: none.** The owner's own reading of the offer
  (2029, from a conversation, secondary, not adopted) has no public
  counterpart. The lag cannot be measured publicly for this project
  today.

### Hunterston Battery Storage Facility and Hunterston Energy Storage Facility (200 MW each, Hunterston Grid 1 Ltd, SPT)

- Register: 10/03/2028 (Hunterston East 400 kV) and 17/03/2028 (Ayrshire
  Grid 400 kV), Gate 2; status **Scoping on the 15/09 copy, Consents
  Approved from the 18/09 copy** (the watch's only material movement).
- Consent: the developer's release of 26/01/2022 says both sites
  "received planning consent from the Scottish Government Energy Consents
  Unit on the 5th January 2022" and were "due to be operational in April
  2024" as two 400 MW facilities (Hunterston and Kincardine). ECU
  reference not found; UNVERIFIED.
- Capacity Market: two CMU groups under Hunterston Grid 1 Ltd, agreements
  issued **31/03/2023** (2026/27 T-4), SCM expected between 29/09/2024 and
  **29/09/2026**, long-stop dates 27/08/2029 and 03/09/2029; deferral
  columns blank. Which group is which register row is not stated;
  UNVERIFIED.
- Financing and construction: trade press dated 15/06/2026 (final
  investment decision, substation under construction, construction from
  Q3 2026) and **24/09/2026** (project financing closed, notice to proceed,
  "commercial operations expected in 3Q28"). Neither names the substation
  or a connection date.
- Companies House: company 10683876, incorporated 22/03/2017, previous
  name FLEXIBLEGRIDPOWER2 LTD until **26/06/2025**; sibling companies at
  the same address (Hunterston Grid 2 and 3, Hunterston Grid Complex,
  Kincardine Grid 1, Windyhill Grid 1).
- Existing Agreements Register: no row for either facility.
- **Dated offer source: indirect.** The Capacity Market's SCM window
  (energisation expected by 29/09/2026) and the 24/09/2026 COD guidance
  (3Q28) bracket the register's March 2028, which the register already
  printed on 15/09/2026, before the financing announcement. Which copy
  first printed March 2028 is a journal question not answered here. The
  offer's own date is not public.

### Middleton BESS (200 MW, Middleton 400 kV, NGET)

- Register: 30/11/2026, Scoping, Gate blank, unchanged across the captured
  copies (and, per the scratch read, since February 2023).
- Acquisition coverage dated 31/10/2022 and November 2022: the buyer said
  the project "is expected to be connected to the grid no later than the
  fourth quarter of 2026", "grid connection and land rights have also been
  secured". The RNS itself was not located; UNVERIFIED wording.
- Capacity Market: CMU KA1MID, agreement issued **31/03/2023** (2026/27
  T-4, 15 years), SCM expected between 01/10/2025 and **29/10/2029**,
  long-stop 29/10/2029; deferral columns blank.
- Ofgem generation licence: application notice 09/09/2024, granted
  **30/10/2024**.
- Planning (Lancaster): 21/01069/FUL, 200 MW at land north of the A683 and
  Heysham substation, permitted **23/05/2022**, permission expiry
  23/05/2025; whether it was implemented in time is not read. That this
  is the same project is matched by capacity, site and date only;
  UNVERIFIED on a primary page.
- Owner's reports: July 2025 results list it as pre-construction; July
  2026 results say a sale process has been initiated for it. No
  connection date in either.
- Companies House: company 13524329, incorporated 22/07/2021, previous
  name KONA ASSET 1 LIMITED until 01/11/2022.
- Existing Agreements Register: no row.
- **Dated offer source: one, old.** The Q4 2026 statement of October 2022
  agrees with the register's 30/11/2026; nothing public since dates the
  offer. The Capacity Market's latest-SCM date of 29/10/2029 is the only
  public later date, and it is the applicant's window, not an offer.

## What follows for the offer-lag candidate

- For the four projects, **no public source dates the offer itself**, so
  the practitioner's three months cannot be tested on them from public
  data today. What can be measured is weaker: the register's date against
  the Capacity Market's dated fields and against dated company statements.
- The cheapest public proxy with dates on both sides is the **Capacity
  Market CMU History change log** (field changes dated from 10/12/2025)
  joined to the **daily TEC capture** (copies from 15/09/2026): when an
  applicant's SCM dates or deferral dates change, does the register's date
  for the same project change, and how many days apart? That is a
  candidate, not opened; it would need a declaration naming the join rule
  (CMU to register row has no key either) and a schema pass over both
  files. The CMU and CMU History files are not in the capture plan; adding
  them is a sponsor decision (`src/grid_mysteries/capture/plan.py`).
- The developer's stated dates are the other side where they exist. For
  a watch-list project, the practical route is the buyer's own copy of the
  offer, which is private and which the register can then be measured
  against privately.

## Sources read

NESO data portal (TEC Register page; Capacity Market Register dataset and
CKAN metadata); NESO connections-reform results page and Existing
Agreements Register xlsx; NESO reports-and-registers page; NESO FOI/25/199,
FOI/25/076, FOI/24/0010, FOI/25/118, FOI/26/173, FOI/26/175; NESO
connections FAQs (updated 06/09/2024); CUSC CAP068 proposal form; Tameside
and Lancaster planning portals and committee papers; energyconsents.scot
search and one detail page; NGED connected-data dataset page and CSV;
SSEN connections-reform page; Ofgem licence notices for Middleton Energy
Storage Limited; Investegate RNS for Gore Street Energy Storage Fund
(17/07/2025, 15/07/2026); Companies House pages for the three customer
companies; trade press (Solar Power Portal 26/05/2022 and 31/10/2022,
Norton Rose Fulbright November 2022, QuotedData 27/02/2023, Enerdata
27/01/2022, Kyodo PR Wire 26/01/2022, ess-news 15/06/2026, Energy Global
24/09/2026). Pages that could not be read: NESO disclosure-log search
interface, SPEN Hunterston East page, UKPN connections-reform page.
