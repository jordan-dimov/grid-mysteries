# Reconnaissance: pan-European grid-model and system datasets for BG/RO load-siting screening

Date of reconnaissance: 2026-08-25 (all fetches live on that date). Purpose: evidence *availability* only — what exists, at what granularity, under what terms, and how to obtain it. No data was analysed beyond opening files to check granularity.

Verification legend used throughout:
- **[FETCHED]** — page/file retrieved and the quoted text read directly.
- **[FILE OPENED]** — dataset downloaded and its contents inspected.
- **[SNIPPET]** — seen only in a search-result snippet or in a secondary source; not independently verified against the primary page.
- **[NOT DETERMINED]** — could not be established from public pages.

Web-search budget was exhausted near the end (200 searches); the last items (JRC-PPDB, GridKit, new-TP API docs) were verified by direct fetch instead.

---

## 0. Executive summary (the decision-relevant facts)

1. **There is no public bus-level (substation) grid model for Bulgaria or Romania from ENTSO-E.** All *public* TYNDP 2024/2026 grid files are zonal: one node per bidding zone (`BG00`, `RO00`) with border NTCs. Verified by opening `StartingGrid2030.xlsx`, `Nodes.zip` and `Line-data.zip` [FILE OPENED].
2. **The nodal TYNDP grid model exists (CGMES, bus-branch, ≥220 kV explicit, loads aggregated to EHV nodes) and is obtainable only "upon request"** via the ENTSO-E "TYNDP Dataset Request Form" at `https://stum.entsoe.eu/` [FETCHED]. The form asks who commissions the study and discourages generic e-mail domains; the conditions of use are **not shown on the form** and were **[NOT DETERMINED]** from any public page. The closest published analogue (ENTSO-E's "Request for Confidential Information" form for the Initial Dynamic Model) is an NDA: results may be published only if shared with ENTSO-E beforehand and contain no confidential information [FETCHED].
3. **Operational Common Grid Models (CGM/IGM) are TSO/RCC-only**; no public access route exists [FETCHED, absence of any public route].
4. **CGMES public sample models are not real BG/RO grids.** The "RealGrid" test configuration is an anonymised real system (4,875 substations, numeric names, no country identifiable) under **CC BY-NC-SA 4.0** (non-commercial) [FILE OPENED].
5. **The Transparency Platform (TP) is the only ENTSO-E source with named BG/RO assets**: production units ≥100 MW with "location" and "voltage connection level" (Art. 14.1.b), unit-level generation (16.1.a), unit outages (15.1), transmission-asset outages with asset identification/location unless the TSO invokes the critical-infrastructure exemption (10.1.a/b). Access is free with a token (register, e-mail `transparency@entsoe.eu`, subject "RESTful API access"). Listed data items are **CC-BY 4.0** — commercial re-use permitted with attribution — per the "List of Data available for free re-use" (18 Oct 2023) [FETCHED].
6. **Capacitypedia (launched 22 May 2026)** is a *directory* of national hosting-capacity pages, not a dataset. Bulgaria is listed (DSO entry only, solar-oriented, "binary" available/not-available); **Romania is not listed at all** (country list checked; `/capacitypedia/romania` returns 403) [FETCHED].
7. **The two national TSO tools are the real substation/zone-level sources for load siting**: ESO's "Електронна карта за свободен капацитет" at `https://webapps.eso.bg/capacity/` lets a user pick a *substation*, choose **"Потребител" (consumer)** or producer, enter MW, and get an indicative connection voltage/cost [FETCHED]; Transelectrica's `https://web.transelectrica.ro/harti_crd_tel/` publishes zone-level (10 zones A–J) connection capacity 2021–2030, with a machine-readable `date/date.json` [FETCHED, FILE OPENED].
8. **Best open bus-level topology for BG/RO** is PyPSA-Eur's OSM-based network (Zenodo record 18619025, v0.7, 12 Feb 2026, ODbL 1.0; 35 countries; `buses.csv`, `lines.csv`, `transformers.csv`, `links.csv`, `converters.csv`) [FETCHED]. It is a topology/parameter reconstruction, not TSO data; capacities come from standard line types.

---

## A. ENTSO-E TYNDP 2024 and TYNDP 2026

### A.1 TYNDP 2024 — what is published and where [FETCHED]

Source page: `https://www.entsoe.eu/outlooks/tyndp/2024/`. The download list on that page reads verbatim: "Starting grid 2030 · System needs study investment candidates · TYNDP 2024 projects portfolio and CBA results - Transmission Projects · TYNDP 2024 projects portfolio and CBA results - Storage Projects · **Aggregated grid model available upon request** · Scenarios data". The "Aggregated grid model available upon request" link points to `https://stum.entsoe.eu/`.

Direct file URLs (all resolved, HTTP 200):
- Starting grid 2030 (IoSN): `https://eepublicdownloads.blob.core.windows.net/public-cdn-container/tyndp-documents/TYNDP2024/foropinion/StartingGrid2030.xlsx` (30 KB) [FILE OPENED]. Sheets: `ReadMe`, `E_2030` (143 rows), `E_Offshore (for info)`, `H_2030/2040/2050`. Columns: `Border | Summary Direction 1 | Summary Direction 2`. **Content is border NTCs between bidding-zone nodes.** BG/RO rows: `BG00-GR00 1700/1400`, `BG00-MK00 400/400`, `BG00-RO00 2190/2190`, `BG00-RS00 380/350`, `BG00-TR00 900/500`, `HU00-RO00 1617/1435`, `RO00-RS00 1984/1800`, `RO00-UA01 150/150`, `MD00-RO00 480/950`, `RO00-UA00 800/800` (MW). No substations, no lines.
- Investment candidates and cost assumptions: `.../TYNDP2024/foropinion/investmentCandidates_and_CostAssumptions.xlsx` (not opened).
- Transmission project portfolio and CBA: `https://tyndp2024.entsoe.eu/projects-map/transmission` (JavaScript app; page text not extractable by fetch — project-sheet content **[NOT DETERMINED]** by fetch; the older 2022 platform provided project sheets plus spreadsheets, and the TYNDP 2026 news page confirms an Excel portfolio download exists for 2026, see A.3).
- Scenarios data: `https://2024.entsos-tyndp-scenarios.eu/download/` [FETCHED]. Items include "Electricity & Hydrogen Reference Grid & Investment Candidates (XLSX, zipped)", "Line Data", "Nodes", "PEMMDB 2.5", "PECD 3.1", demand/supply inputs, and outputs.
  - `https://2024-data.entsos-tyndp-scenarios.eu/files/scenarios-inputs/Nodes.zip` → `Nodes/LIST OF NODES.xlsx`, sheet `Electricity` has 52 nodes; BG/RO rows are exactly `BG00` and `RO00` [FILE OPENED].
  - `https://2024-data.entsos-tyndp-scenarios.eu/files/scenarios-inputs/Line-data.zip` → `ReferenceGrid_Electricity.xlsx` (same border/NTC structure as StartingGrid2030; BG/RO rows identical), `ReferenceGrid_Hydrogen.xlsx`, `Prosumer Wheeling Charge.xlsx` (`BG00 42.627 €/MWh`, `RO00 146.444 €/MWh`) [FILE OPENED].
  - Licence on the download page, verbatim: "all data that is published in the Visualisation Platform and Data files are released under a Creative Commons Attribution 4.0 International License." Attribution as "TYNDP 2024 Scenarios".
- Reports: Infrastructure Gaps Report, System Needs Report, CBA Implementation Guidelines (`.../TYNDP2024/foropinion/CBA_Implementation_Guidelines.pdf`), IoSN Implementation Guidelines (`.../TYNDP2024/foropinion/SystemNeedsMethodology.pdf`) [FETCHED, text extracted].
- Contact stated on the page: "Stakeholders wishing to engage further with ENTSO-E are welcome to contact us at tyndp@entsoe.eu".

**Conclusion on granularity: every public TYNDP 2024 grid file is zonal (bidding-zone nodes + border NTCs). Nothing public is nodal.**

### A.2 What the (non-public) TYNDP grid model is [FETCHED]

TYNDP 2024 CBA Implementation Guidelines, §3.3.1: "All load-flow simulations for merging the grid models are performed on models collected from TSOs for the NT 2030 and NT 2040 scenario in ENTSO-E Common Grid Model Exchange Specification (CGMES) format, for reference hours selected from a market …" §3.3.2: "The market models cover in general bidding zones (market nodes), but their outcome feeds into grid models which have a more detailed level and cover all individual nodes. The network models collected by ENTSO-E contain all the information required to map the market simulation results, namely the identification of all grid parts corresponding to a market node…" §3.3.4: grid models are per synchronous area (CE, Baltic, Nordic, GB, IE/NI); excluded: CY, Corsica, IS, MT, TR, UA, MD, GE, MedTSO. §3.4.7 (redispatch input data): "Three data categories can be defined dependent on the confidentiality level: 1. Data publicly available 2. Data only available on request (Due to data size) 3. Data for which an NDA is necessary". Tools listed with the models: PSS/E, PowerFactory, Integral, Powsybl, GridSuite, Convergence, GridCal.

IoSN Implementation Guidelines 2024 §7.1: "Classical market study (1 node on average per country or Zonal clustering, NTC between countries, no mesh rule implemented)" and "CIM merged grid model (base case): The network model to be used as base case for IoSN 2040 of TYNDP 2024 is built from the grid model of TYNDP 2024 with 2030 NTCs used as a starting point … The grid model is built in CIM (CGMES) format."

The most detailed public description of the *content* of an ENTSO-E TYNDP dataset is the **TYNDP 2020 ENTSO-E dataset specification** (`https://eepublicdownloads.entsoe.eu/clean-documents/CIM_documents/Grid_Model_CIM/TYNDP_2020_ENTSO-E_dataset_specificationv01.pdf`, Oct 2020/Mar 2021) [FETCHED]:
- "According to ENTSO-E decision the data set will be provided in CGMES 2.4.15 format."
- "The models submitted for 2025 Refgrid are aggregated bus branch models with the generation and load connected to the nearest High Voltage node. For transmission lines rated voltages present in the model range from 110 kV to 750 kV. All elements connected at 220 kV and above are modelled explicitly. Representation of the non-radial 150 kV, 132 kV and 110 kV shall be represented at the 220-kV level. Branches and substations of the network under the 220-kV voltage level shall not be represented in detail. Loads shall be aggregated at the closest extra-high voltage (EHV) node…"
- "Substations are usually represented as one busbar per substation."
- "All TSOs have provided the CGMES profiles EQ, TP, SSH, SV. So, a solved model is provided." Attributes include "Active Power limits for generators Pmax, Pmin", "Thermal ratings AC lines"; HVDC as equivalent injections.
- Country table for the CE merged model includes **RO** (186 ACLineSegment, 128 BusbarSection, 88 ConformLoad in the class-count table) and **BG** appears in the balance tables (BG installed 10,986 MW; load 5,292 MW); the class-count table column list printed as AL AT BA BE CH CZ DE DK ES FR GR HR HU IT LU ME MK NL PL PT RO RS SI SK — BG column not visible in the extracted text (layout artefact; BG is present in the balance and load-flow annexes, "Grid: BG"). So **BG and RO are represented at (aggregated) substation level in the TYNDP 2020 dataset**; a 2024 vintage in the same style is what "Aggregated grid model available upon request" refers to.
- The document contains no licence and no statement on publication of derived results **[NOT DETERMINED]**.

### A.3 TYNDP 2026 [FETCHED]

- Draft Scenarios released 11 June 2026: `https://www.entsoe.eu/news/2026/06/11/entso-e-and-entsog-release-their-joint-draft-scenarios-for-tyndp-2026/` — "main scenario report, a methodology report, enhanced data and visualisation platform with downloadable input and output datasets".
- Download page `https://2026.entsos-tyndp-scenarios.eu/download/`: package `ENTSOs_TYNDP2026_Scenarios_Package_20260701.zip`, model inputs as ZIPs including "Line Data", "Nodes", PECD, demand etc. Licence statement verbatim: "All data published in the Visualisation Platform and Data files are released under a Creative Commons Attribution 4.0 International License." Same zonal structure as 2024 (Line Data/Nodes); not opened.
- Project portfolio: 199 transmission and 69 storage projects (news 2 Apr 2026); draft portfolio published 29 Oct 2025 with a downloadable `TYNDP2026_Draft_project_portfolio.xlsx`; map at `https://tyndp2026.entsoe.eu/projects-map/`; "The results will be released with the draft TYNDP 2026 in late 2026." CBA results are therefore **not yet available** as of 2026-08-25.
- IoSN methodology for consultation: `https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/tyndp-documents/TYNDP2026/TYNDP_2026_identification_of_system_needs_methodology_for_consultation.pdf` [SNIPPET].

### A.4 TYNDP 2022 / 2020 / 2018 grid models and how they were released [FETCHED]

ENTSO-E's legacy "Maps & Data" page (`https://tyndp-data.netlify.app/maps-data/`) lists, with direct links:
- **TYNDP 2022**: "Model data — Reference grids for the cost-benefit analysis of projects" → `https://eepublicdownloads.blob.core.windows.net/public-cdn-container/tyndp-documents/TYNDP2022/data/TYNDP2022_CBA_reference-grids.xlsx` [FILE OPENED: 107 rows, project list with `Project ID, Project Name, Commissioning Year, Border, Transfer capacity increase A-B/B-A (MW)` — a project/NTC list, not a network]; "Starting grid of the System needs study" → `.../TYNDP2022/data/TYNDP2022_IoSN_starting-grid.xlsx`; CBA results `.../TYNDP2022/CBA-results/TYNDP2022_CBA_EU27_all-scenarios.xlsx`. The tyndp.entsoe.eu resource page "TYNDP 2022 model data – reference grids…" is a client-rendered Next.js page whose content could not be extracted **[NOT DETERMINED beyond the netlify listing]**.
- **TYNDP 2020**: "Model Data — Grid Dataset" (links to the request portal) and "Reference grid for CBA and IoSN" → `https://www.entsoe.eu/Documents/TYNDP%20documents/TYNDP2020/Reference Grid 2025 - TYNDP 2020.xlsx`. The nodal dataset is the CGMES set described in A.2, on request.
- **TYNDP 2018**: "Model Data — Grid Dataset" (request portal), plus scenario load series/generation capacities (Excel).
- **TYNDP 2016 and 2014**: "Grid data set"; 2014: "Input grid datasets for the preparation of the TYNDP 2014 (Available on request)".
- No licence text appears on that page.

Historical context from the openmod wiki (`https://wiki.openmod-initiative.org/wiki/Transmission_network_datasets`) [FETCHED]: "ENTSO-E STUM 1 … 2015 … CIM … Requires registration … Restrictive"; "ENTSO-E STUM 2/3 … 2015/2016 … 2030 … GB, Ireland, Baltics, Finland, Continental Europe … 1000s substations … Topology, Impedances … Requires registration … Restrictive … Excel". The wiki adds (via snippet) that "It is not totally clear what one may and may not do with it (e.g. whether it is possible to publish results derived from it or an aggregation of the nodes, etc.)" [SNIPPET].

### A.5 The exact request route [FETCHED]

**URL:** `https://stum.entsoe.eu/` (also served at `https://www.entsoe.eu/stum/`; `https://docstore.entsoe.eu/stum/` no longer resolves — DNS failure).

Page title: "ENTSO-E TYNDP Dataset Request Form". Verbatim instructions:
- "Please fill out the below form to request access to the ENTSO-E TYNDP Dataset. Please note that all the below fields* are mandatory."
- "1. Identity of the person and organisation requesting access to ENTSO-E information." Fields: `fname`, `lname`, `company` (Organisation), `street`, `streetnb`, `zipcode`, `city`, `country` (select), `phone`, `fax` (optional), `email`.
- "Please use your organisation/company email address when completing the request form as access will also be based on the provided address."
- "Request Dataset*" select `dataset` with options: **`TYNDP Study Model`** and `Bidding Zone Review`.
- "2. If different from the name given in 1., please provide the name of the legal entity commissioning the study or project." (same field set, suffix `_1`). "We discourage from the usage of generic emails (for instance, yahoo, gmail, hotmail, etc.)"
- "3. If different from 1. and/or 2., please provide the name of the legal entity commissioning the study or the project." (suffix `_2`).
- "In case of difficulties or for more information on the ENTSO-E Dataset, please contact servicedesk(at)entsoe.eu".
- The form has a hidden `nonce` and a JavaScript `checkForm()` submit; no terms-of-use text, no eligibility statement ("universities" vs companies), no statement about commercial use, TSO consent, or publication of results appears on the form. **All of those are [NOT DETERMINED].**

What ENTSO-E's *published* confidential-data terms look like (the nearest analogue, used for the CE Initial Dynamic Model): `https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/SOC%20documents/230308_IDM_Request_Form_General_locked.pdf` — "REQUEST FOR CONFIDENTIAL INFORMATION" [FETCHED]. Key clauses verbatim:
- Procedure: "Please fill in the form and send it to the ENTSO-E Secretariat (idm@entsoe.eu) for a formal check. When the ENTSO-E Secretariat confirms a formal correctness of the form, please print the form and all annexes out, sign, scan and send them back as a PDF file and by registered mail or courier at the address rue de Spa 8, 1000 Brussels, Belgium."
- Form asks: "3. Describe the concrete and specific study or project for which you are requesting the data. Give copy of any official document(s) on the study or on the project and describe your relationship with the persons or entities having commissioned the project or the study. Provide information on the financing and on the timing of your project or your study"; "5. Define the preferred format of data requested"; "7. Will the requested information be used by other persons of entities?"
- Terms: "3. Non-Disclosure and Use Commitments. The Recipient commits: (i) to use and exploit the Confidential Information only for the Authorized Purposes …"; "6. Project Results. (i) The Recipient shall inform the Disclosing Party about the results of the Project ('Results') and provide a copy of it … (v) The Recipient may publish the Results provided it: a) shares the Results with the Disclosing Party for information prior to the publication; and b) does not publish any Confidential Information with the Results."; "9. Term … minimum period of at least five (5) years"; "7. Liability … compensation … equivalent to € 25.000 per breach, with a limitation … € 100.000 per contractual year."; "(vii) Title. All rights, title and interest in and to the Confidential Information shall be retained by the Disclosing Party."
- Whether the TYNDP Study Model uses the same or a lighter undertaking is **[NOT DETERMINED]**; treat this as the likely shape.

---

## B. ENTSO-E CGMES datasets

### B.1 CGMES conformity test configurations [FILE OPENED]

Page: `https://www.entsoe.eu/data/cim/cim-conformity-and-interoperability/` [FETCHED]. Package: `https://www.entsoe.eu/Documents/CIM_documents/Grid_Model_CIM/CGMES_ConformityAssessmentScheme_TestConfigurations_v3-0-3.zip` (25.2 MB, 437 files). Contents: `MicroGrid`, `MiniGrid`, `SmallGrid`, `RealGrid`, `PowerFlow`, `Disclaimer.docx`, `README.md`.
- `README.md` verbatim: "This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License." (The web page says CC BY-SA 4.0; the package README says **CC BY-NC-SA 4.0** — the package is the stricter and more specific statement.)
- `Disclaimer.docx`: "The test configurations (models), documents and application profiles are owned by ENTSO-E and are provided by ENTSO-E 'as it is' … Any use … shall include a reference to ENTSO-E."
- `RealGrid/RealGrid-Merged/`: `RealGrid_EQ.xml`, `RealGrid_TP.xml`, `RealGrid_SSH.xml`, `RealGrid_SV.xml` (profiles EQ/TP/SSH/SV; no DL/GL/DY). Counts in EQ: Substation 4,875; ACLineSegment 7,561; PowerTransformer 1,509; SynchronousMachine 1,347; OperationalLimitSet 18,140; EnergyConsumer 0; GeographicalRegion 1 (named `1555284823`), SubGeographicalRegion 7. Substation names are numeric IDs (e.g. `18614`, `20492`). **Anonymised; no country identifiable; not BG/RO.**
- Unofficial mirrors exist at `github.com/cgmes/real_grid` and `github.com/cgmes/small_grid` (the first returned 404 when fetched; "unofficial" per snippet) [SNIPPET].

### B.2 Common Grid Models for operations (CGM/IGM) [FETCHED]

- `https://www.entsoe.eu/news/2021/12/09/go-live-of-the-common-grid-model/`: the CGM process runs "using the Physical Communication Network (PCN), ENTSO-E's Operational Planning Data Environment (OPDE) Platform, and relevant business applications for secure pan-European data exchange" for "TSOs and RCCs". No public access is mentioned anywhere.
- CGM Methodology (SO GL Art. 67/70, `https://www.entsoe.eu/Documents/nc-tasks/SOGL/SOGL_A67_70_180222_CGM%20methodology_180314.pdf`) [FETCHED]: only quality indicators and the methodology itself are to be published; there is no clause providing third-party access to models.
- Conclusion: **the pan-European CGM (all timeframes) is TSO/RCC-only; no request route for third parties exists.** [Absence verified across the CGM pages; a positive statement "restricted" was not found verbatim.]

### B.3 The TYNDP grid model in CGMES

See A.2: CGMES 2.4.15, EQ/TP/SSH/SV, solved, bus-branch, ≥220 kV explicit, loads aggregated at EHV nodes, generator P limits and line thermal ratings included, one busbar per substation. Model years: TYNDP 2020 = NT2025 reference grid; TYNDP 2024 = NT2030 and NT2040 (reference hours 685 and 2491 for merging). BG and RO are included in the CE merged model. Available **only via `stum.entsoe.eu`**.

### B.4 CGMES library and boundary set [FETCHED]

`https://www.entsoe.eu/data/cim/cim-for-grid-models-exchange/`: CGMES 2.4.15 ("version for CGM programme go-live in 2021") and CGMES 3.0 (IEC 61970-600 Ed1 since 2021). Application Profiles Library under Apache 2.0; reference data under CC BY-SA 4.0. "ReliCapGrid (Open-Source, Synthetic and Anonymous Test Model)" is mentioned on GitHub. No operational or planning grid models are offered on the page.

---

## C. ENTSO-E Transparency Platform (TP) — BG/RO coverage, access, licence

### C.1 Platform state (August 2026) [FETCHED]

- The platform was migrated to a new technology; "After the migration is complete, all data (historical and new publications) will be available only from the new Transparency Platform website" (`https://transparencyplatform.zendesk.com/hc/en-us/articles/30195539966865-…`). The temporary URL `https://newtransparency.entsoe.eu/` now requires JavaScript; legacy KB pages under `transparency.entsoe.eu/content/static_content/...` return HTTP 400. The Zendesk knowledge base (`https://transparencyplatform.zendesk.com/`) is the current documentation.
- The legacy RESTful endpoint `https://web-api.tp.entsoe.eu/api` is **still live**: an unauthenticated probe on 2026-08-25 returned a well-formed `Acknowledgement_MarketDocument` with reason "Unauthorized. Missing or invalid security token" [FETCHED]. Interface spec: "Sitemap for Restful API Integration" (`.../articles/15692855254548`). REST responses now use curve type A03 (variable-size blocks) and may return decimals.
- File Library (bulk CSV extracts with `_r3` suffix) replaces SFTP (decommissioned 20 Nov 2025); guide at `.../articles/35960137882129-File-Library-Guide` (returned 403 to the fetch tool; title and existence verified via the KB search API).

### C.2 Token / access conditions [FETCHED]

`https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token` (updated 2026-08-25): "1- Register Transparency Platform … https://transparency.entsoe.eu/ … 2- Send an email to transparency@entsoe.eu with 'RESTful API access' in the subject line and the registered e-mail address in the body. 3- … You will be granted within 3 working days and will receive an email 4- Login … 'My Account' … Generate a (new) token". Free of charge; no organisational eligibility condition.

### C.3 Data items relevant to BG/RO siting (definitions from the KB and the Regulation) [FETCHED]

Regulation (EU) 543/2013 text (from `legislation.gov.uk/eur/2013/543/article/...`, EU-origin text):
- **Art. 14(1)(b)** — "information about production units (existing and planned) with an installed generation capacity equalling to or exceeding 100 MW. The information shall contain: the unit name, the installed generation capacity (MW), the location, the voltage connection level, the bidding zone, the production type". KB article "Installed Capacity Per Production Unit [14.1.B]" (updated 2026-08-19) adds "the control area; … the commissioning date (when available); and the decommissioning date (when available)"; "Information should refer to the 1st January of each year for the 3 following years".
- **Art. 15** — unavailability of generation/production units ≥100 MW with "the name of the production unit, the name of the generation unit, location, bidding zone, installed generation capacity (MW), the production type, available capacity during the event, reason…".
- **Art. 16.1.a** — actual generation output per generation unit ≥100 MW (KB file `ActualGenerationOutputPerGenerationUnit_16.1.A_r3`).
- **Art. 10(1)(a)/(b)** — planned/actual unavailability in the transmission grid reducing cross-zonal capacity by ≥100 MW, "specifying: the identification of the assets concerned, the location, the type of asset, the estimated impact on cross zonal capacity per direction…". KB article 10.1.A/B (updated 2026-06-12) verbatim caveat: "TSOs may choose not to identify the asset concerned and specify its location if it is classified as sensitive critical infrastructure protection related information in their Member States as provided for in point (d) of Article 2 of Council Directive 2008/114/EC" and "the Data Provider may refrain from disclosing the asset identity, location and type." New r3 extracts split this into `UnavailabilityInTheTransmissionGridAffectedAssets_10.1.A_B_r3` and `...AffectedAreas_10.1.A_B_r3`.
- Load (Art. 6) is per bidding zone/control area only — **not nodal**. Physical flows (Art. 12.1.g) per border. Cross-zonal capacities (Art. 11) per border. Congestion management (Art. 13: redispatch internal/cross-border, countertrading, costs) per control area.
- **Whether ESO and Transelectrica actually name transmission assets in 10.1 outage publications, and whether the BG/RO ≥100 MW unit lists carry usable "location" strings, was [NOT DETERMINED]** — it requires a token query. The rules make it likely (names are mandatory unless the CIP exemption is invoked); this is the first thing to verify once a token exists.

### C.4 Licence and commercial use [FETCHED]

- Terms of Use, version 29/03/2023 (`https://transparencyplatform.zendesk.com/hc/article_attachments/40921869376401`, "230329_ENTSOE_Transparency_Terms_Conditions_MC_APPROVED.pdf"), clause 2.5 "Open Source License" verbatim: "ENTSO-E currently publishes a subset of the Transparency Platform data available under an open source license (CC-BY 4.0) for the free use of Data Users (hereinafter 'Open Data')." Clause 3.1 obliges the Data User to "mention the ENTSO-E Transparency Platform as the source of publication of the data", not to imply "sponsorship or … endorsement", and, for data not on the open list, to "seek the prior agreement of the holder of the copyright or related right" (the Primary Owner of Data).
- "List of Data available for free re-use", last modified 18 October 2023 (`https://transparencyplatform.zendesk.com/hc/article_attachments/40921869379729`) verbatim: "ENTSOE below publishes the list of data which can be freely re-used by the Data Users in conformity with the open data standards and licenses under a Creative Commons Attribution 4.0 International License (CC-BY 4.0). Data Users may freely copy, redistribute, and adapt the listed data for any purpose, by giving appropriate credit (attribution) to its source and indicating if they have made any changes, with no need to seek for the prior agreement of the respective Primary Owner of Data." Exclusions: "data from Moldova (MD) and Turkey (TR)"; certain items from Ukraine, BritNed, IFA and Nemo Link. **Bulgaria and Romania are not excluded.** The list includes items 10.1.a/b (transmission unavailability), 14.1, 15.1, 16.1 etc. (item numbering verified for 10.1.a/b; the list runs to item ~35 covering the Transparency, Balancing and SO Regulations).
- Conclusion: **BG/RO TP data on the list is CC-BY 4.0 → commercial use and publication of derived results are permitted with attribution to "ENTSO-E Transparency Platform"** and with an indication of changes made.

---

## D. Capacitypedia [FETCHED]

- Launched 22 May 2026 by ENTSO-E and DSO Entity (`https://www.entsoe.eu/news/2026/05/22/...`). Portal: `https://www.tsodsoplatform.eu/capacitypedia`. It is "a single-entry point to grid hosting capacity information websites" (About page) implementing EU Grid Action Plan Action 6; content is "hosting capacity information voluntarily provided by participating Distribution System Operators (DSOs) and Transmission System Operators (TSOs)"; "The information presented in this portal does not represent a complete picture and/or an exhaustive list of all existing EU system operators."
- Country list on the overview page (verbatim): Austria, Belgium, **Bulgaria**, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Slovakia, Slovenia, Spain, Sweden, Switzerland. **Romania is absent**; `/capacitypedia/romania` returns HTTP 403 "You are not authorized to access this page." ESO EAD and Transelectrica are not in the TSO list.
- Bulgaria page (`/capacitypedia/bulgaria`) verbatim: "In Bulgaria, grid hosting capacity information is published by both the TSO and DSOs. TSO capacities are reported at the country level based on primary substations, while DSO capacities are location-based within their licensed territories. … Currently, capacity information considers mainly solar generation and indicates whether requested capacity is available." Only one entry is linked: DSO "Elektrorazpredelenie Yug EAD", whose page lists the three DSO check tools (ERP Sever, ERM Zapad, Elektrorazpredelenie Yug `https://www.elyug.bg/ProduceCapacity/ProduceCapacity.aspx`), "Voltage Level Coverage: DSOs are responsible to publish available capacity for MV grid (6, 10 and 20 kV)", "Grid hosting capacity downloadable & format: No, the available capacity information can be queried via a form", "Grid user types covered: Solar", "API Availability: Openly available" (sic), "Connection request rules/principles: First come, first served."
- No dataset download; platform terms (`Terms and Conditions_TSO-DSO Cooperation Platform.pdf`) say content "is the property of the Associations … You may not reproduce, distribute, or create derivative works" and downloads are "only for non-commercial, personal use" — but this governs the portal's own pages, not the national sources it links to.
- **Verdict: no use for screening beyond a directory; for BG/RO go to the national TSO tools (section E.4).**

---

## E. Grid map and derivative open datasets

### E.1 ENTSO-E Grid Map [FETCHED]

- `https://www.entsoe.eu/data/map/`: "Network elements are not located at their exact geographic location. The map shows existing elements and those under construction: power plants, converters, substations and high-voltage cables/lines. PDF maps are available on our Grid Map downloads page". The interactive viewer is an iframe to `https://entsoe-grid-map-viewer.netlify.app/` (ArcGIS JS app; the bundle references ArcGIS basemaps and vector tiles; no GeoJSON/shapefile download endpoint was found in the bundle).
- Downloads page `https://www.entsoe.eu/data/map/downloads/`: 2024, 2023, 2019 PDF maps only (1:4,000,000 / 1:3,000,000 / 1:2,500,000). "No shapefile, GeoJSON, KML" and no licence text on the page. Older "Electronic 2017 ENTSO-E Interconnected Network Maps … free of charge subject to terms of use" [SNIPPET, docstore page].

### E.2 PyPSA-Eur OSM-based network [FETCHED]

- Zenodo `https://zenodo.org/records/18619025` — "Prebuilt Electricity Network for PyPSA-Eur based on OpenStreetMap Data", **version 0.7, 12 February 2026, ODC Open Database License v1.0**. Files: `buses.csv` (805 kB), `lines.csv` (19.8 MB), `links.csv` (323 kB), `transformers.csv` (122 kB), `converters.csv` (9 kB), `map.html`. "35 European countries"; 220–750 kV; "substations within 500 meters aggregated into single buses"; "Persistent OpenStreetMap identifiers".
- Method paper: arXiv 2408.17178 / *Scientific Data* 2025 (`https://www.nature.com/articles/s41597-025-04550-7`): "European high-voltage grid, including and above 200 kV"; "published under the Open Data Commons Open Database (ODbL 1.0) licence"; "compares the dataset with official statistics". Earlier snippet: "6001 lines … and 3657 substations"; "Although accuracy cannot be guaranteed, as only TSOs have access to the real grid data". Line capacities come from standard line types by voltage (PyPSA-Eur convention; the per-country BG/RO validation figures were **[NOT DETERMINED]** — the paper PDF could not be parsed).
- PyPSA-Eur docs page for the base network moved (both `/en/stable/data-base-network.html` and `/data-base-network/` returned 404 on 2026-08-25) **[NOT DETERMINED]**.
- **BG/RO coverage**: both are in the 35-country ENTSO-E area build; whether OSM completeness in BG/RO matches TSO reality is unverified here (validation table not extracted). A quick check against ESO's "297 electrical substations / >15,000 km of lines" statistic [SNIPPET, bgenh.com] and Transelectrica's RET data would be the first calibration step.

### E.3 Other derivatives

- **GridKit** (Wiegmans, Zenodo 47317, 10 Mar 2016, ODbL 1.0): `gridkit_euorpe.zip` (1.8 MB) of `vertices.csv`/`links.csv` — a 2016 topological extract [FETCHED]. Stale for 2026 use.
- **Open-TYNDP** (Open Energy Transition + ENTSO-E; `https://github.com/open-energy-transition/open-tyndp`, Zenodo 18494363): PyPSA-Eur workflow implementing the TYNDP 2024 *reference grid* (bidding-zone level; "Electricity Reference Grid xlsx"). Zonal only, by construction [FETCHED docs; node count and licence not stated on the docs home].
- **TYNDP 2024 data bundle for PyPSA-Eur** (Zenodo 14230568, 1.3 GB, CC-BY 4.0, "Originally published by ENTSO-E and ENTSOG under Creative Commons Attribution 4.0") [FETCHED].

### E.4 National TSO hosting-capacity tools (the actual siting sources) [FETCHED]

- **ESO EAD (Bulgaria)** — `https://webapps.eso.bg/capacity/` "Електронна карта за свободен капацитет". Explanation PDF (`https://webapps.eso.bg/capacity/Еxplanation_bg.pdf`) verbatim: "Под свободен капацитет трябва да се разбира – максималната активна мощност в MW на обекти за производство или потребление на електроенергия, която може да бъде присъединена към дадена подстанция, собственост на ЕСО, без да се предизвиква претоварване на елементи от електропреносната мрежа"; "Електронната карта дава възможност на потенциалните инвеститори във всяка подстанция, собственост на ЕСО, да посочат вида на присъединяваната мощност (производител или потребител) и прогнозната максимална стойност на активната мощност … В резултат се визуализира информация за ниво напрежение на присъединяване и приблизителна стойност на присъединяването"; "Данните за електронната карта се актуализират веднъж на тримесечие или по-често"; "не може да се ползва за резервиране на мощност"; map "отразява приблизително реалното географско разположение". UI has layers for 110/220/400 kV substations and lines, a selector "Производител / Потребител", an MW input, and "Електропроводи за рехабилитация" (lines at risk of overload, with length and indicative reconstruction cost). It is an ASP.NET WebForms app (postbacks); no documented API; substation detail pages are of the form `Binga.aspx?pst=<id>`. **This is the only public per-substation, load-side (consumer) capacity signal for Bulgaria.** Scraping it programmatically is feasible but is a per-substation query, not a bulk download.
- **Transelectrica (Romania)** — `https://web.transelectrica.ro/harti_crd_tel/` "Harti Capacitati de Racordare Disponibile": 10 RET zones (A–J), years 2021–2026 and 2030, per zone `CR / ATR / Studii / Cereri / TOTAL`, "Capacități de racordare RED 110 kV", "Capacitate transfrontaliera totala". Machine-readable data: `https://web.transelectrica.ro/harti_crd_tel/date/date.json` (15 kB; keys `zone, harti, capacitati, solicitari, granite, transfront`; e.g. 2021 zone B 1,600 MW, zone D 1,200 MW) [FILE OPENED]. Notes state the method: capacity computed under N-1 "fără considerarea întăririlor de rețea", updated per ANRE Order 137/2021; note 8 says consumer connections *increase* generation hosting capacity — i.e. the map is **generation-oriented**, not a load-connection map. No licence stated.

### E.5 CCRs and JAO [FETCHED]

- All-TSO CCR determination (30 Nov 2023, `https://eepublicdownloads.entsoe.eu/clean-documents/nc-tasks/231130_ALL%20TSOs_Determination_of_CCR_methodology.pdf`), Art. 11 verbatim: "The CCR SEE shall include the bidding zone borders … a) Greece - Bulgaria (GR - BG), Independent Power Transmission Operator S.A. and Elektroenergien Sistemen Operator (ESO) EAD; and b) Bulgaria - Romania (BG - RO), Elektroenergien Sistemen Operator (ESO) EAD and … 'Transelectrica' S.A." Romania's other borders (HU-RO) are in **Core**; Bulgaria is **not** in Core.
- JAO Publication Tool (`https://publicationtool.jao.eu/`) lists only: Core, CoreID, Italy North/IBWT IDA, Nordic, SWE, Cross-CCR CID APIs. **No SEE section.** Core FBMC data (CNECs, PTDFs, RAM) therefore covers Romania's Core borders (published CNEC names are the only public "critical network element" list touching RO); nothing equivalent for Bulgaria.

---

## F. Generation closure/addition data

- **ERAA 2025** (ENTSO-E; ACER Decision 06/2026, March 2026). Modelling data page `https://www.entsoe.eu/eraa/2025/modelling-data/` [FETCHED] offers ZIPs: `ERAA_2025_CommonData.zip`, `ERAA_2025_DemandData.zip`, `ERAA_2025_NTCs.zip`, `ERAA_2025_FBDomains.zip`, `ERAA_2025_PECDRES.zip`, `ERAA_2025_PECDWeather.zip`, `ERAA_2025_EconomicTechnicalInvestmentParameters.zip`, `ERAA_2025_OtherData.zip`, `ERAA_2025_Dashboard_RawData.zip`, all under `https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/sdc-documents/ERAA/`. Explanatory note: study zones are bidding-zone level; PECD4.1 "under a CC-BY-4.0 licence"; no explicit licence for the TSO-provided supply data was found in the note **[NOT DETERMINED]**. Granularity: technology aggregates per study zone, not unit/location. ERAA 2026 modelling data page also exists (`/eraa/2026/modelling-data/`).
- **TP Art. 14.1.b** (above) is the only ENTSO-E source with unit names, location, voltage level and (when provided) commissioning/decommissioning dates for BG/RO units ≥100 MW, three years ahead.
- **JRC Open Power Plants Database (JRC-PPDB-OPEN)** (`https://data.jrc.ec.europa.eu/dataset/9810feeb-f062-49cd-8e76-8d8cfd488a05`, Zenodo 10.5281/zenodo.3266807): unit-level, coordinates, commissioning/decommissioning years, EU coverage, **CC BY 4.0**, last modified 25 July 2019 [FETCHED] — useful as a geocoded seed for BG/RO ≥100 MW units, but stale.
- NECPs: not fetched (search budget); BG/RO final updated NECPs (2024/2025) are the policy source for coal-closure schedules but are not unit-location datasets.

---

## G. Legal/licensing summary

| Source | Licence / terms | Commercial use | Publish derived results | TSO consent needed |
|---|---|---|---|---|
| TP listed data (BG/RO incl.) | CC-BY 4.0 per List of Data 18/10/2023 | Yes | Yes, with attribution + note of changes | No |
| TP data not on list | Terms 3.1: seek Primary Owner's agreement | Conditional | Conditional | Possibly |
| TYNDP scenario/zonal files | CC-BY 4.0 (stated on 2024 and 2026 download pages) | Yes | Yes | No |
| TYNDP nodal grid model (stum.entsoe.eu) | Not published; likely NDA-type undertaking (IDM analogue: pre-publication sharing with ENTSO-E, no confidential data in outputs, 5-year term) | [NOT DETERMINED] | [NOT DETERMINED] | [NOT DETERMINED] — ENTSO-E is the disclosing party; TSO consent not mentioned on the form |
| CGMES test configurations | CC BY-NC-SA 4.0 (package README) | **No** | Share-alike | n/a |
| Operational CGM | TSO/RCC only | n/a | n/a | n/a |
| PyPSA-Eur OSM network / GridKit | ODbL 1.0 | Yes | Yes (share-alike for derived *databases*) | No |
| JRC-PPDB-OPEN | CC BY 4.0 | Yes | Yes | No |
| ESO capacity map / Transelectrica map | No licence stated; explicitly "not a commitment", "not for reservation" | Unstated | Unstated (facts are public; quote with date) | Not for reading |
| Capacitypedia portal pages | "non-commercial, personal use" (portal T&C) | No (portal content) | n/a | n/a |

---

## H. Recommended obtaining plan (cheapest evidence first)

1. **TP token today** (free, ≤3 working days): register at `https://transparency.entsoe.eu/`, e-mail `transparency@entsoe.eu`, subject "RESTful API access". First queries: 14.1.b unit list for `10YCA-BULGARIA-R` and `10YRO-TEL------P` (check the "location" strings), 10.1.a/b affected-assets extracts (check whether ESO/Transelectrica name lines/substations), 16.1.a per-unit generation.
2. **Download and pin** (all free, CC-BY/ODbL): TYNDP 2024 `StartingGrid2030.xlsx`, `Nodes.zip`, `Line-data.zip`, `investmentCandidates_and_CostAssumptions.xlsx`; TYNDP 2026 scenario package; ERAA 2025 ZIPs; PyPSA-Eur OSM v0.7 CSVs; JRC-PPDB-OPEN; Transelectrica `date/date.json`; ESO explanation PDF and per-substation query results (with fetch timestamps).
3. **Submit the STUM request** in parallel (below) — expect weeks and an undertaking to sign; do not build the method on the assumption it arrives.
4. Treat Capacitypedia as a bookmark only.

---

## I. Draft request wording — ENTSO-E TYNDP Dataset Request Form (`https://stum.entsoe.eu/`)

The form has no free-text field. Fill section 1 with the requester (use an `@a115.bg` or company-domain address — "access will also be based on the provided address"; generic mail domains are discouraged), select **"TYNDP Study Model"**, and fill sections 2/3 only if a different legal entity commissions the work (for self-funded research, repeat A115 Ltd or leave identical; the form marks the fields mandatory, so repeat the requester's details). Because the form carries no purpose statement, send a covering e-mail the same day to `servicedesk@entsoe.eu` (the contact named on the form), cc `tyndp@entsoe.eu` (the contact named on the TYNDP 2024 page):

> Subject: TYNDP Dataset Request Form submitted – TYNDP Study Model (TYNDP 2024 aggregated grid model) – A115 Ltd
>
> Dear ENTSO-E Service Desk,
>
> I have today submitted the ENTSO-E TYNDP Dataset Request Form (stum.entsoe.eu) selecting "TYNDP Study Model", on behalf of A115 Ltd, an independent research and software company (Bulgaria/United Kingdom). This e-mail gives the context the form does not allow us to state.
>
> Dataset requested: the TYNDP 2024 aggregated grid model referenced on entsoe.eu/outlooks/tyndp/2024 ("Aggregated grid model available upon request"), in CGMES format (EQ/TP/SSH/SV) for the Continental Europe synchronous area, NT2030 (and NT2040 if available), including the Bulgarian and Romanian individual grid models. If only a subset can be released, the ESO EAD and Transelectrica IGMs with the CE boundary set would suffice.
>
> Purpose: a small, reproducible, publicly documented research study ("Grid Mysteries") on where new 50–150 MW electricity loads could plausibly connect in Bulgaria and Romania. The model would be used for DC load-flow / PTDF-based screening of the ≥220 kV network under the TYNDP starting-grid assumptions, combined with public Transparency Platform data and the ESO and Transelectrica hosting-capacity publications.
>
> Intended outputs: (a) a published methodology; (b) aggregated, non-attributable results (e.g. regional rankings, sensitivity of screening outcomes to model vintage). We would not publish the model, any extract of it, per-element parameters, or anything allowing reconstruction of TSO data. We would be glad to share draft results with ENTSO-E (and, if you prefer, with ESO EAD and Transelectrica) before publication, and to sign ENTSO-E's standard data-use undertaking.
>
> Commercial context, stated for transparency: A115 Ltd is a private company; the study is self-funded research, not commissioned by a third party, and the model would not be resold, redistributed, or used to provide grid-model-derived services to clients. If ENTSO-E's conditions for the TYNDP Study Model differ for companies and for academic institutions, or if a different dataset (e.g. an older TYNDP 2020/2022 study model) is what can be released to a company, we would welcome that guidance.
>
> Practical details: preferred format CGMES 2.4.15 or 3.0 XML; alternative formats (PSS/E RAW, UCTE-DEF) acceptable. Users: [names], all A115 Ltd staff. Timing: analysis planned for Q4 2026; results to be published in 2027.
>
> Requester: [Name, role], A115 Ltd, [registered address], [company e-mail], [phone].
>
> Kind regards, …

If ENTSO-E replies with a "Request for Confidential Information"-style undertaking (as used for the Initial Dynamic Model), note the clauses that constrain the project: results must be shared with ENTSO-E before publication; no confidential information in publications; five-year minimum term; €25,000-per-breach liquidated damages. Decide before signing whether the publication workflow can meet the pre-publication-sharing clause.

---

## J. Item-by-item verification status

| # | Item | Status |
|---|---|---|
| A | TYNDP 2024 download list and "Aggregated grid model available upon request" → stum.entsoe.eu | FETCHED |
| A | StartingGrid2030.xlsx, Nodes.zip, Line-data.zip are zonal (BG00/RO00) | FILE OPENED |
| A | TYNDP 2024/2026 scenario data CC-BY 4.0 | FETCHED |
| A | TYNDP grid model: CGMES, EQ/TP/SSH/SV, bus-branch, ≥220 kV, loads at EHV nodes; BG/RO included | FETCHED (2020 spec; 2024 IG) |
| A | STUM form fields, e-mail-domain rule, dataset options, contact | FETCHED |
| A | STUM conditions (eligibility, commercial use, publication, TSO consent) | NOT DETERMINED |
| A | IDM "Request for Confidential Information" undertaking terms (analogue) | FETCHED |
| A | TYNDP 2022/2020/2018 model-data links and "requires registration / restrictive" history | FETCHED (netlify page, openmod wiki) |
| A | TYNDP 2026 draft scenarios (11 Jun 2026), portfolio (199+69), CBA "late 2026" | FETCHED |
| B | CGMES test configurations: RealGrid anonymised, EQ/TP/SSH/SV, CC BY-NC-SA | FILE OPENED |
| B | Operational CGM TSO/RCC-only; no public route | FETCHED (absence) |
| C | TP token procedure, free | FETCHED |
| C | TP legacy REST endpoint still answering | FETCHED (probe) |
| C | TP Terms 2023 clause 2.5; List of Data CC-BY 4.0; BG/RO not excluded | FETCHED |
| C | 14.1.b / 15 / 16.1.a / 10.1 field definitions incl. location and CIP exemption | FETCHED |
| C | Whether ESO/Transelectrica actually name outage assets / unit locations | NOT DETERMINED (needs token) |
| D | Capacitypedia launch, portal, country list (BG yes, RO no), BG DSO-only entry | FETCHED |
| E | ENTSO-E grid map: PDFs only, viewer is ArcGIS app, no GIS download | FETCHED |
| E | PyPSA-Eur OSM v0.7 (Feb 2026), ODbL, file list, 35 countries | FETCHED |
| E | PyPSA-Eur BG/RO validation figures | NOT DETERMINED |
| E | SEE CCR = GR-BG, BG-RO; RO's other borders in Core; JAO PuTo has no SEE | FETCHED |
| E | ESO capacity map: per-substation, consumer option, quarterly updates | FETCHED |
| E | Transelectrica map: 10 zones, 2021–2030, date.json | FILE OPENED |
| F | ERAA 2025 modelling-data ZIP URLs; zonal granularity | FETCHED |
| F | JRC-PPDB-OPEN CC BY 4.0, unit-level, 2019 | FETCHED |
| F | NECP unit-level closure lists | NOT FETCHED |
| G | Licence table | derived from the above |

Local working copies (scratchpad, not pinned): `StartingGrid2030.xlsx`, `Nodes.zip`, `Line-data.zip`, `TYNDP2022_CBA_reference-grids.xlsx`, CGMES test-configuration zip, TP terms 2018/2023 PDFs, List of Data 2023 PDF, IDM form PDF, TYNDP 2020 dataset spec PDF, CCR determination PDF, CBA/IoSN implementation guidelines PDFs, ERAA 2025 data-release note, ESO explanation PDF, Transelectrica `date.json`. Note: the scratchpad directory was cleared once during the session; re-download before pinning digests.
