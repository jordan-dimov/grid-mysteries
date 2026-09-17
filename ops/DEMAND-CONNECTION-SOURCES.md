# Demand-connection sources: inventory, 2026-09-17

*Job 1 of the session brief of 2026-09-17: before anything is fetched, every
public list that names demand or data-centre electricity connection projects
in Great Britain, with publisher, URL, cadence, whether the publisher archives
or overwrites, and whether it discloses on request. Discovery only: landing
pages, dataset metadata, consultation and FOI PDFs were read; **no data file
(CSV, XLSX, JSON rows) was opened**, so no column, MW or status below comes
from a register's rows. The schema pass and the first fetch wait for the
seal (see §4). The raw discovery notes, with every URL and quotation, are in
`DEMAND-CONNECTION-SOURCES-notes-2026-09-17.md` beside this file.*

Why now: the vintage archive is the TEC Register, which is generation and
storage (NESO, FOI/25/074: "Demand-only connections on the transmission
system are not shown in the TEC Register"). Gate 2 Phase 2 demand offers land
September 2026 to March 2027, and Ofgem's data-centre commitment fee decision
(etrmbiz slot `gb-data-centre-queue-commitment-fee-2026`) is due before year
end, so whatever demand lists exist have to be captured from now, in vintages.

## 1. The finding in one paragraph

**There is no public register of demand connections in Great Britain, and
NESO says so in its own words.** FOI/25/174 (response 18 December 2025,
`https://www.neso.energy/document/374976/download`): "We do not currently
have a register of demand connections. We are not required under the
Connection and Use of System Code (CUSC) to maintain or publish one in the
way that we are for generation connections … We have previously had enquiries
about providing a demand register and are considering this as a development
piece, but it would take considerable time to produce." The same position is
in FOI/25/074 (5 August 2025). The Perplexity report's attribution of this to
aprs.scot (ref 40) is wrong: that page carries no such passage; the source is
NESO's own disclosure log. What exists instead is **one NESO spreadsheet that
names demand projects without outcomes**, one **anonymised** DNO demand list,
a handful of DNO aggregates, and a set of confidential project-level datasets
(NESO's mandatory demand IRN, the DNO call for input) from which Ofgem's
315-project / 73 GW figure was built and which are not published.

## 2. Inventory

Columns: what it lists; fields (from metadata or documentation only);
cadence; archive or overwrite; disclosure on request. "Not knowable without
opening the file" is written where that is the case.

### 2.1 Lists that name individual demand or data-centre projects

| # | Source | Publisher | URL | Names projects? | Fields known without opening | Cadence | Archive / overwrite | On request |
|---|---|---|---|---|---|---|---|---|
| 1 | **Existing Agreements (EA) Register v.2.0** (XLSX, document 373996) | NESO | `https://www.neso.energy/document/373996/download`, linked from `https://www.neso.energy/industry-information/connections-reform/connections-reform-results` | **Yes.** All projects that applied for Gate 2 where consent to inclusion was given, transmission and DNO-submitted. Per FOI/25/174 it "can be filtered by 'Transmission Connected Demand' in 'Technology Type' (Column F). Some Transmission Connected Demand projects have 'Data Centre' in their 'Project Name' (Column A)." Shows **no** Gate outcome or phase. | Column A Project Name, Column F Technology Type; everything else not knowable without opening the file. HEAD 2026-09-17: XLSX, 168,268 bytes, Last-Modified 11 Jun 2026 12:56:32 GMT | NESO calls it "a static dataset (i.e., it will not be updated)" (FOI/26/136, Aug 2026) — yet it is at v.2.0, and a known duplication was left uncorrected (FOI/26/034, May 2026) | **Overwrites in place** under one document id. Wayback holds one capture, 2026-01-22, 167,793 bytes, so the January bytes differ from today's and are recoverable there; nothing between | NESO refuses per-project status under EIR 12(5)(e) and Utilities Act 2000 s.105 (FOI/25/219, 25/293, 26/032, 26/034, 26/136) and points to the TEC and EA registers |
| 2 | **Large Demand List** | UK Power Networks | `https://ukpowernetworks.opendatasoft.com/explore/dataset/ukpn-large-demand-list/` | **Anonymised.** Live, committed, not-yet-energised import projects: demand-only ≥ 5,000 kVA and BESS | licence_area, grid_supply_point, anonymised_name, demand_technology_type, required_import_capacity_kva (rounded), application_date; 496 records | "Reviewed monthly", but last modified **2025-11-04** | Single live dataset; Opendatasoft keeps no public version history | CC BY 4.0; no FOI needed |
| 3 | NGED "Connections Reform Register" (CSV dated 251212) and "Projects Connections Reforms Outcomes" (CSV dated 260709, modified 9 Jul 2026) | National Grid Electricity Distribution | `https://connecteddata.nationalgrid.co.uk` | CMP435 projects NGED manages; **whether demand rows are present is undetermined** (field lists are not in the data-sharing PDFs, and embedded demand is outside CMP435 scope per Ofgem's decision) | Not knowable without opening the files | Irregular, dated file names | Dated file names suggest versions are kept; not verified | Open data portal |

### 2.2 Aggregates and counts that carry demand but name nothing

| # | Source | Publisher | URL | What it carries | Cadence | Archive / overwrite |
|---|---|---|---|---|---|---|
| 4 | Ofgem Curate consultation, 29 Jul 2026, Table 1 "Analysis of data centre queue" | Ofgem | `https://www.ofgem.gov.uk/sites/default/files/2026-07/Proposed-data-centre-connection-reforms-curate-consultation-document.pdf` | Five size bands: 0–10 MW 11 projects / 76 MW; 10–50 MW 47 / 1,370; 50–100 MW 51 / 3,492; 100–500 MW 166 / 36,632; 500+ MW 40 / 31,408. Sums to **315 projects / 72,978 MW** — the Bloomberg figures are this table. No snapshot date beyond "current demand queue" (capex "as of April 2026"). Para 2.3 names the basis: NESO's voluntary demand call for input (Nov 2025, summary Mar 2026), **project-level data from NESO's mandatory information request notice (IRN) to demand projects in the transmission queue, issued 13 March 2026**, a DNO voluntary call for input (Mar 2026) aggregated by NESO, aggregated transmission-queue data, ENA-aggregated distribution data-centre data, and Companies House comparison. Para 2.9: ≥ 9 GW modified from battery to data centre, May 2024 to Aug 2025. Consultation page shows closing 17 Sep 2026 (press: 16 Sep) | One-off | Dated PDF, stable |
| 5 | NESO Demand Call for Input, high-level summary (Mar 2026) | NESO | `https://www.neso.energy/document/378226/download` | 243 responses, 92,947 MW; Data Centre 50,802 MW across 152 project phases. Aggregate only | One-off | Dated PDF |
| 6 | NESO Connections Reform Detailed Results Data (PDF, 33 pp, last-modified 9 Jan 2026) | NESO | `https://www.neso.energy/document/374936/download` | Phase 1/2 MW by technology and zone for the CP30 technologies. **Zero occurrences of the word "demand".** The 8 Dec 2025 announcement carries the only demand aggregate seen: "99 GW in transmission-connected demand … around 13 GW before 2030, 86 GW 2030–35" (search snippet, not fetched) | One-off | Dated PDF |
| 7 | ENA Connections Data Dashboard | Energy Networks Association | `https://www.energynetworks.org/industry/connecting-to-the-networks/connections-data` | Offers issued by technology at ≥ 1 MW/MVA, aggregate; "Data correct as of Wednesday 9th September. The Dashboard will be next be updated on Friday 18th September". Whether a demand row exists is not knowable from the HTML (widget loads dynamically). Page still carries lorem-ipsum placeholders. Ofgem's "41 GW to 125 GW" demand-application figure (letter of 6 Nov 2025) is sourced to "Recent Energy Networks Association data"; no ENA publication of it was found | Roughly weekly | **Overwrites**; zero Wayback captures |
| 8 | UKPN "Data Centres by Local Authority" (45 rows, 2026-04-24); "Longest Demand Modification Application Lead Times at GSPs" (70 rows, 2026-04-28; about very large data centres referred to NESO); "Overall Queue Insights" (technology × status × MW) | UK Power Networks | `https://ukpowernetworks.opendatasoft.com/` | Operational vs pipeline data-centre MVA per local authority; lead times per GSP; queue totals. No names | Irregular | Single live datasets |
| 9 | NPg "Large Scale Demand" (406 rows, 2026-01-08); "Connection Queue Information" (445 rows, generation only) | Northern Powergrid | NPg open data portal | Accepted demand kVA aggregated to EHV by type, no data-centre category; the queue dataset carries export capacity, transmission_gate, phase, final_queue_rank for generation only | Irregular | Single live datasets |
| 10 | LTDS connection-interest tables: UKPN Table 6 (933 rows, 29 May 2026); NPg Appendix 8 (476 rows, login); SPEN Appendix 6 (SPD 708 rows, SPM variants) | UKPN, NPg, SPEN | DNO LTDS pages | Counts and kVA of demand enquiries per substation. No names | Six-monthly | SPEN publishes mid-year vintages as separate datasets; others overwrite |
| 11 | ENWL "GSP Connection Queue" | Electricity North West | ENWL data portal (login) | Per-GSP project slots with project, capacity, date, technology; "currently unavailable"; demand inclusion unknown | — | — |

### 2.3 Registers that do **not** carry demand, checked so nobody re-checks

- **NESO TEC, Embedded and Interconnector registers** (all modified 2026-09-15): CKAN `package_search` for demand, connection, register, queue, modification returns only these three. No "demand register", "connections queue", "modification applications" or "CION" dataset exists on the portal, and the reports-and-registers page lists none.
- **DNO Embedded Capacity Registers** (UKPN, NGED, SPEN, SSEN, ENWL, NPg): scope is "generation and storage resources (≥ 50 kW)" under DCP 350; demand appears only as flexible demand or storage import (ENWL keeps a separate "ECR Part 3 – DSR" for DSR sites ≥ 1 MW). The ENA ECR schema carries import fields (Import MPAN, Maximum Import Capacity MW/MVA, Change to Maximum Import Capacity), but no DCUSA or ENA change extending the ECR to demand was found; the only trace is a 2023 consultation-response suggestion. **Archiving differs by DNO and matters for the capture plan: SSEN keeps monthly XLSX/CSV vintages from Oct 2023 to Sep 2026 as separate CKAN resources** (`https://data-api.ssen.co.uk/dataset/embedded_capacity_register`); NGED, UKPN, NPg, SPEN and ENWL overwrite one live dataset.
- **CUSC CMP434 / CMP435** create no published demand queue list; CMP435 excludes embedded demand; NESO's gated-modification guidance page publishes no window counts.
- **NESO Demand IRN** (`https://www.neso.energy/industry-information/connections/demand-information-request-notice-irn`): mandatory under NESO's statutory information-gathering powers, sent to every customer with a transmission-level demand connection agreement; responses "will be treated confidentially". This is the project-level list behind Ofgem's count, and it is not published.
- **NESO Gate 2 Phase 2 demand**: NESO contacts a defined cohort of "Gate 2 Phase 2 demand customers" directly (NGET high-voltage information-gathering request, 22 May to 15 Jun 2026); no list, no demand-specific timetable. FOI/25/293 (24 Feb 2026): "NESO will not be disclosing information on the status of individual projects at this time."
- **DESNZ**: the March 2026 consultation says "we will designate a strategic plan including a list of strategically important demand projects, including AIGZs" — promised, not published. Five AI Growth Zones are named in press (Culham, North East, North Wales, South Wales, North Lanarkshire); no register with grid MW.

## 3. What does not exist on the public record, stated plainly

1. A NESO register of transmission demand connections (NESO's own words, twice).
2. Any published list of Gate 2 demand outcomes or offers, Phase 1 or Phase 2.
3. NESO data-portal datasets for a demand register, connections queue, modification applications or CION.
4. The project-level list behind Ofgem's 315 projects / 73 GW (NESO IRN plus DNO call for input, held confidentially).
5. The ENA dataset behind "41 GW to 125 GW".
6. A DCUSA or ENA extension of the Embedded Capacity Register to demand.
7. A DNO list that names demand or data-centre projects (UKPN's is anonymised; the rest are aggregates).
8. DESNZ's designated strategic demand list.
9. A register of AI Growth Zones with grid capacity.
10. The FOI passage the Perplexity report attributed to aprs.scot.

## 4. Schema pass: not done, and why

The doctrine's schema pass inspects columns, spellings, blank rates and row
counts, which means opening the files, which is the fetch the seal gates.
Nothing in §2 was opened. Once Jordan seals the first fetch, the pass runs
`scripts/schema-report csv <file> <archive>` on each CSV export and
`scripts/schema-report xlsx <file> <archive>` on the EA Register and the SSEN
vintages (the `xlsx` branch is added alongside this inventory so the pass can
run the day the seal lands), producing `archives/<name>/SCHEMA.md` and
`schema-report.json` for: `neso-ea-register`, `ukpn-large-demand-list`,
`nged-connections-reform`, `ssen-ecr` (the archived vintages, which are the
one place a DNO's own history can be read back) and, if their exports prove
readable, the UKPN and NPg aggregates. A declaration over any of them cites
that report's digest, as the TEC work does.

## 5. Caveats carried from the discovery pass

- The IRN page fetch printed 2025 dates while Ofgem's Curate document says
  13 March 2026; the year was not independently verified.
- The 99 / 13 / 86 GW demand aggregate comes from search snippets of the
  8 December 2025 announcement, not from a fetched document.
- WhatDoTheyKnow was Cloudflare-blocked and not inspected.
- Web page summaries via WebFetch are model-condensed; quotations above are
  from PDFs read as text or from verbatim-prompted fetches, and are marked as
  such in the notes file.
