# Bulgaria — evidence-availability reconnaissance for siting a 50–150 MW transmission-connected load

Reconnaissance date: 2026-08-25 (all "verified" fetches performed that day).
Scope: SOURCES only. No node ranking, no substation-level or regional utilisation/request values are reported here, by design. Where a source contains such values, the record says so at field/table level.

Verification legend used throughout:
- **[V]** = fetched and inspected directly (curl/pdftotext/WebFetch) on 2026-08-25.
- **[S]** = seen only in a search-engine snippet or a third-party summary; not fetched.
- **[F]** = fetch attempted and failed (HTTP 402/403/404 or paywall); details in section 8.
- **[I]** = my inference from fetched material (e.g. undocumented JSON field names); not confirmed by the publisher.

Method note: WebSearch budget (200 calls) was exhausted before the announcement sweep (section 6) was complete; section 6 is therefore a partial list of what surfaced, not a census.

---

## 0. Executive map of the evidence landscape

| Layer | Best source found | Node resolution | Access | Status |
|---|---|---|---|---|
| Per-substation connection capacity (existing, contracted, remaining), 400/220/110 kV and 110 kV/MV | ESO "Свободен капацитет за присъединяване" map + its undocumented GeoJSON/JSON endpoints (`webapps.eso.bg/joining/public/map`) | substation × voltage level | public, no auth, no licence text | [V] |
| 10-year transmission plan (approved) | ESO plan 2025–2034, KEVR Decision ДПРМ-2/25.09.2025 | national + named projects, no per-substation loading tables | public PDF | [V] |
| 10-year transmission plan (latest draft) | ESO draft plan 2026–2035 (published 17.03.2026) — adds municipality-level load and generation maps | municipality choropleths, named projects | public PDF | [V] |
| Reinforcement list with years | KEVR working-group report on the 2025–2034 plan (23.07.2025) | named line/substation × start/end year; no per-item cost | public PDF | [V] |
| Connection rules for consumers | Naredba 6/28.03.2024, consolidated to ДВ 35/14.04.2026 (KEVR); Energy Act чл. 81г, 116, 117, 21(3)8 (lex.bg, consolidated to ДВ 70/04.08.2026) | — | public | [V] |
| DSO hosting capacity (110/20 kV) for **consumers** | none found; DSOs publish RES-producer yes/no lookups only | settlement | public | [V] |
| Data-centre connection-request statistics | ESO statements in press (May–Aug 2026): national totals and a breakdown by region | region (press), substation (not public) | press | [V]/[S] |
| Regional electricity consumption (statistical) | NSI publishes national series; regional electricity consumption not found | national | public XLSX | [V] |
| Industrial-zone site data | BAI Interactive Investment Map (investmap.government.bg); NKIZ site | zone/parcel (electricity capacity field present but heterogeneous units) | public HTML/PDF | [V] |

---

## 1. ESO EAD — ten-year transmission development plans (Десетгодишен план за развитие на преносната електрическа мрежа)

### 1.1 Where the plans live [V]
- Page: **ESO → "Развитие на ЕЕС"**, `https://www.eso.bg/doc?93=` [V]. Lists exactly two documents:
  - "План за развитие на преносната електрическа мрежа на България за периода 2025-2034 г." (обновен 03.11.2025) → `https://www.eso.bg/fileObj.php?oid=5665`
  - "Проект на 'План за развитие на преносната електрическа мрежа на България за периода 2026-2035 г.'" (обновен 17.03.2026) → `https://www.eso.bg/fileObj.php?oid=5850`
- Legal basis: Energy Act чл. 81г (operator submits a 10-year plan to KEVR annually by 30 April; must show infrastructure planned for the next 10 years, all decided investments, new investments for the next 3 years, and a schedule for all projects) [V lex.bg]; KEVR approves under чл. 21(3) т. 8 [V]. Plans also cite ПУЕЕС глава 2 раздел 3 [V plan text].
- Older editions found as ESO fileObj PDFs (all "10 Year Plan" titled) [V pdfinfo]: oid=398 (2017, 54 pp), oid=1088 (2018, 58 pp), oid=2512 (2020, 62 pp), oid=3505 (2022, 32 pp), oid=5010 (2024–2033, Apr 2024, 38 pp), oid=5272 (2024–2033, Dec 2024, 38 pp), oid=5354 (2025–2034, Mar 2025, 40 pp). KEVR also hosts an old one: `dker.bg/uploads/_CGCalendar/2020/10_Year_Net_Dev_Plan_20-29.pdf` [S].
- No English version of any plan was found. CMS Law and IV Law Firm publish English summaries of the 2025–2034 plan [S].

### 1.2 Draft plan 2026–2035 (LATEST) [V]
- Publisher: ЕСО ЕАД. Title: "ПЛАН ЗА РАЗВИТИЕ НА ПРЕНОСНАТА ЕЛЕКТРИЧЕСКА МРЕЖА НА БЪЛГАРИЯ ЗА ПЕРИОДА 2026 – 2035 г." (Transmission Network Development Plan of Bulgaria 2026–2035), marked as a *draft (проект)*.
- URL: `https://www.eso.bg/fileObj.php?oid=5850` — fetchable: yes. PDF text (not scanned), 49 pages (48 numbered). PDF CreationDate 2026-03-17. SHA-256 `6691fc880baba971278fa40fc77371987637a19c3ea16b522b9fc8100bd62d0f`.
- t_public: page says "обновен на 17.03.2026". KEVR approval: **not found** — no ДПРМ decision in KEVR's 2026 decisions list and no ESO-plan consultation notice on KEVR's news page (visible range 29.07–21.08.2026; pagination not functional) [V]. Status as of 2026-08-25: draft; approval status unverified.
- Structure (TOC identical to 2025 edition): 1 Introduction; 2 Consumption analysis/forecast; 3 Generation analysis; 4 Power/energy balances (reference & alternative scenarios); 5 Flexibility (base, priority, balancing/reserve); 6 Network development (6.1 planning, 6.2 load-flow principles, 6.3 model inputs, 6.4 load-flow analysis for 2035, 6.5 RES connection, 6.6 PCI CARMEN, 6.7 NEK pumped storage, 6.8 new NPP units, 6.9 DSO proposals, 6.10 security problems from replacing conventional plants, 6.11 voltage control); 7 Short-circuit currents; 8 Fibre/ASDU (SCADA/EMS, telemechanics, telecoms, backup supply); 9 Investment estimate; 10 Conclusions; Приложение 1.
- Contents at table/figure level:
  - Table 2.1: three national gross-consumption scenarios 2026–2035 (ИНПЕК, максимален, минимален), GWh per year (national only; e.g. ИНПЕК 43,360 GWh in 2035).
  - Table 3.1–3.3: RES/storage foreseen for connection (transmission vs distribution), new capacity by technology (MW), net installed capacity per ИНПЕК.
  - **New in this edition**: Figures 3.2–3.6 — choropleth maps of installed HPP, PHS, PV, wind and battery-storage capacity **by municipality** for target year 2030; **Figure 4.1 — distribution of electrical loads by municipality for 2030**. (Images; not extractable as data from the PDF text.)
  - Tables 4.1–4.8: national power balances (max winter, extreme winter, max summer, min spring, min summer), utilisation factors, energy balance, RES/PHS output.
  - Table 6.1: named 400 kV projects (new 400 kV lines along existing 220 kV corridors, new 400 kV switchyards, a new 400/110 kV substation) to be built by 2035; Table 6.2: named 110 kV corridor-uprating projects; Table 6.3: load-flow results for the 2035 average-winter regime (system losses, the most-loaded 400/220 kV lines and 400/110, 220/110 autotransformers with % loading, flows through AT groups); Table 6.4: expected max/min voltages. **Per-substation loading exists only for the handful of "most loaded" elements; there is no full per-substation/per-transformer table.**
  - Section 7: short-circuit current levels at key substations (start and end of period).
  - Section 9: investment estimate — heading present; the figures are in a table not captured by text extraction (likely image). The 2025 edition total was ~BGN 1.985 bn per KEVR/press [V 3e-news].
  - Приложение 1: **list of ESO's letters to DSOs, NEK, NPP, thermal, CHP and industrial plants (Nov 2025–Jan 2026) whose investment intentions fed the plan** — it is a correspondence register, not a data annex.
- Data-centre mentions (two, national-level) [V]: (i) "сключените договори за присъединяване на ВЕИ, ОСЕЕ, ОЗРМ и дейта центрове са изчерпали преносната възможност на съществуващата електропреносна мрежа във всички райони на страната" (signed connection contracts for RES, storage, closed DSOs and data centres have exhausted the transmission capability of the existing grid in all regions); (ii) future low-voltage problems expected from large data centres with power factor below 0.95 inductive (6.11).
- Modelling notes [V]: 110 kV node loads come from ESO winter control measurements and DSO data; N-1 check per scheme (stated, results not tabulated); scenario of full coal stop modelled; 2035 peak 7,920 MW / average working day 7,050 MW (conclusions).
- Can support: national scenarios, list of committed 400/110 kV reinforcements and their corridors, qualitative statement that contracted capacity is exhausted, municipality-level load/RES maps (visual). Cannot support: per-substation headroom, project costs per item, project dates (see KEVR WG report for dates), consumer-connection queue.
- Change frequency: annual (draft ~March, KEVR approval ~September in 2025 cycle).

### 1.3 Approved plan 2025–2034 [V]
- Two ESO PDFs: oid=5354 (Mar 2025 draft, 40 pp) and oid=5665 (dated 16.10.2025, "обновен 03.11.2025", 40 pp; SHA-256 `589063ccbd638a90fa35031a5213b7e118cc77dac5bbe8115bdea7802c52ecb9`). Text diff between the two is limited to formatting/pagination (908 diff lines of re-flowed text; same TOC and figures) — substantive changes not identified.
- KEVR record [V]:
  - Application вх. № Е-13-41-40 от 30.04.2025; working group order 15.05.2025; ESO supplement 28.05.2025 (decided investments; 3-year new investments; 2024 investment report per ДПРМ-2/19.09.2024).
  - **Working-group report** (23.07.2025, 24 pp, TLP-GREEN): `https://www.dker.bg/uploads/_CGCalendar/2025/rep_TYNDP_2025-2034_25.pdf`. Contains a **project list table**: lines (incl. OPGW installations) and substations, grouped "own financing" / "attracted financing" / "RES connection" (with investor names for RES-driven works), each with **start/end year**; no per-item cost. Also mentions n-1 checks per scheme and four new 400/110 kV substations.
  - Public consultation 30.07.2025 (KEVR news 1258; BTA 939647; BIA; 3e-news 29.07.2025 — investment total ~BGN 1.985 bn: substations 48.27%, lines 41.39%).
  - **Decision № ДПРМ-2 от 25.09.2025 г.** (32 pp): `https://www.dker.bg/uploads/reshenia/2025/res_dprm_2_25.pdf` — "Одобрява План за развитие … 2025–2034 г." without conditions in the operative part. Records DSO submissions (e.g. ER Yug annexes: lists of expected new substations on its territory, proposals for ESO substations, generation connected/contracted/forecast to 31.12.2024/2025/2034) — those annexes are described, not published.
  - Closed-session Protocol № 279/25.09.2025 (233 pp): `https://www.dker.bg/uploads/protokoli/zz/2025/prot-zz-279-25sep2025.pdf`.
- Contents mirror 1.2 minus the municipality maps. Table 6.2 (2025 edition) gives losses and most-loaded elements with % loading for 2034. 2034 figures: consumption ≤41,600 GWh; peak 7,680 MW; average working day 6,800 MW [V].

### 1.4 What the plan PDFs do NOT contain (checked) [V]
No per-substation transformer loading table; no maps of the 400/220/110 kV network as data (a JPEG scheme exists separately, see 2.6); no connection-request register; no consumer-load projections by node; no per-project cost; no N-1 result tables. Plan explicitly says annual substation 110 kV/MV reinforcement needs cannot be pre-listed because Naredba 6/ЗЕВИ/ЗУТ deadlines are shorter than the plan cycle.

---

## 2. ESO EAD — open data, maps, registers, portals

### 2.1 "Свободен капацитет за присъединяване" — new interactive map (2026) [V]
- Publisher: ЕСО ЕАД. Name: "Свободен капацитет за присъединяване" (Free capacity for connection), linked from eso.bg home. URL: `https://webapps.eso.bg/joining/public/map` — React/Azure Maps SPA; fetchable, no login.
- Geography: Bulgaria; **resolution: individual substation × voltage level (220/110/20/10 kV)**; transmission lines 400/220/110 kV as geometries.
- UI layers/labels found in the JS bundle [V]: "Свободен капацитет", "Бъдещ свободен капацитет", "Активни предварителни договори", "Сключени договори", "Сключени ДС по временна схема", "Обекти в процедура по присъединяване към електропреносната мрежа", "Обекти, присъединени към електропреносната мрежа" (consumption / production / storage / closed-DSO objects), "Присъединена генерация ВН/СрН", "Капацитет на подстанция СрН", "Трансформатор 1/2/3", "Планирана реконструкция и планирано изграждане (развитие) на електропреносната мрежа до 203x" (planned line reconstruction / new line / new substation; "по договор с инвеститор" / "по проект"), "Предстояща подмяна/изграждане", "Съществуваща подстанция", "Чужда подстанция", search by name.
- **Undocumented data endpoints** (base `./api` relative to the map) [V, all HTTP 200 without auth on 2026-08-25]:
  - `https://webapps.eso.bg/joining/public/map/api/get-points.php` — GeoJSON FeatureCollection, 474 point features (283 "Подстанция 110kV", 27 "Подстанция 400kV", 15 "Подстанция 220kV", 149 "Подстанция външна собственост"). Properties: `id, mer` (ESO grid region), `name, name_a, name_b, name_en, status, color, max_voltage_kv, at1_mva…at6_mva` + `atN_description` (autotransformer ratings), `joined_sum, delivered_sum, installed_sum, new_installed_sum, joined_sum_ccee, joined_power, assigned_projects` (list of project-name strings), `str1/str2/str3/new_str1/new_str2/aditional_str`, `created_at, updated_at`, and ~200 coded fields of the form `{epm|erm}_kind{6|7|8}_{ccee|delivered|installed|ozrm}_{g0|g1|g2|g55|g85|g90|gvn}` and `kind{6|8}_…_v{04|6|10|20|35|110|220|400}_st_{90|6785|5560657075}` — [I] apparently breakdowns by object kind, voltage level and status code; semantics undocumented.
  - `…/api/get-lines.php` — GeoJSON, 810 LineString features (694 × 110 kV, 63 × 400 kV, 53 × 220 kV); properties `id, name, name_en, volt, color, status, visible, description, assigned_projects, updated_at`.
  - `…/api/get-point-json.php` (POST `id=<pstId>`) — per substation: `title, substation, stationLabel, description, plannedProject`, and `voltages[]` (220/110/20/10 kV) each with `rows[]`: `capacity_total` "Общ преносен капацитет за присъединяване", `reserved_generation`, `reserved_consumption`, `reserved_mixed`, `reserved_standalone_ccee`, `reserved_gen_ccee`, `reserved_ozrm`, `remaining_total` "Оставащ капацитет за присъединяване на нови мощности"; each row has `powerMw` plus `pd / opinion / contract` sub-fields (preliminary-contract / opinion / contract stage) [I on sub-field meaning].
  - `…/api/get-lines-steps.php` (27 records: `id, no, lat, lng, sap_no, id_power_line`), `…/api/get-network.php` (returns caller IP and `"network":"external"` — implies an internal view may differ).
- Temporal: data vintage from `created_at/updated_at`: 2026-01-29 to 2026-08-06 (points and lines) — i.e. maintained continuously; this replaces the old quarterly map. Historical snapshots: none published (would need to be captured by the user).
- Machine readability: JSON/GeoJSON. Licence: none stated on pages fetched. Access conditions: no auth, no terms page found; the older map's explanation (2.2) says results are indicative, not a commitment, and do not reserve capacity — presumably applies here too [I].
- Can support: identification of substations, their voltage levels, transformer ratings, categories of already-committed capacity (generation/consumption/mixed/storage/closed DSO) and stated remaining capacity per voltage level; planned reinforcements attached to each node/line. Cannot support: N-1-verified firm capacity, simultaneity between neighbouring requests, timing of remaining capacity, or any commitment (see Naredba 6 for the binding route). Codes must be decoded before use.
- Obtainable by an ordinary company: yes.

### 2.2 "Електронна карта за свободен капацитет" — older map (2021) [V]
- URL: `https://webapps.eso.bg/capacity/` (ASP.NET WebForms; legend: 110/220/400 kV substations; dropdown Producer/Consumer; MW input → "approximate value"; list "Power lines for rehabilitation"). Explanation PDF: `https://webapps.eso.bg/capacity/Еxplanation_bg.pdf` (1 p., Word 2016, 25.06.2021) [V].
- Definitions: free capacity = max active power (MW) of production **or consumption** objects connectable to an ESO substation without overloading transmission elements; for MV, limited by 110 kV/MV transformer capability under security criteria; for 110 kV, by element capability per ПУЕЕС чл. 13–14 and power-quality impact; shows voltage level and approximate connection cost; for requests above free capacity, shows threatened lines, lengths and approximate reconstruction cost in some substations; does **not** account for simultaneous competing requests or ring topologies; is not a reservation; data updated "once per quarter or more often". Still online but superseded in practice by 2.1.

### 2.3 Connection portal, registers and forms [V]
- "Присъединяване" page `https://www.eso.bg/doc/?joining`: access to the Information Portal requires registration with qualified electronic signature (КЕП) at `https://cc.eso.bg:8443/joining/public/certcard/`; login `https://webapps.eso.bg/joining/public/`.
- "Регистър по ЗЕВИ" — electronic register of **RES producer** connection applications under ЗЕВИ чл. 28(5) (announced 13.10.2023, ESO news 611): requested/permitted MW, filing date, admissibility, decisions, validity of opinions. Not a consumer register. Capital (22.01.2024) reported the public register is "limited" [S].
- "Регистър на желаещите да се присъединят към мрежата при временна схема на достъп" (temporary access scheme) — `https://www.eso.bg/doc/?542` [V page exists; contents behind portal].
- No public register of **consumer** connection requests or signed consumer contracts was found. Aggregate consumer (data-centre) request figures are released only through ESO statements to press (section 6).
- Forms: producer application template (Part 3 of Naredba 6) `https://www.eso.bg/fileObj.php?oid=191` [S]; bank-guarantee template `fileObj.php?oid=5296` [V link]. Joining page states a guarantee of BGN 50,000/MW under Naredba 6 чл. 84а for **storage** objects (page text predates euro redenomination; the regulation now says €25,564.59/MW) [V].
- Price list page "Ценоразпис за услугата Присъединяване" `https://eso.bg/doc?joining-price-list=` [V page loads; the tariff text was not extractable]. Search snippet: study fee for consumer/producer connection studies approved by KEVR Decision Ц-27/28.07.2016 [S]; KEVR URL for Ц-27/2016 not located (two URL guesses 404).

### 2.4 Operational data / JSON endpoints [V]
- Page `https://www.eso.bg/doc/?460` (real-time generation and load; load + forecast). Public JSON verified: `https://www.eso.bg/api/last24load.json.php` (24 hourly load points, JSON), `https://www.eso.bg/api/load_plus_forecast.json.php` (daily 24-h load curves incl. forecast days). Blocked to external callers (returns "ЕСО ЕАД :: internal" page): `/api/rabota_na_EEC_json.php`, `/api/scada_live_json_pure.json`. Other pages: cross-border physical flows (`doc/?34`), planned exchanges (`?35`), used NTC by border (`?38`), operational energy balance (`?39`), ACE (`?445`), historical generation (`doc/?generation_per_day` — form with reCAPTCHA), imbalance-price forecasts. Metering data portal PRCL (`webapps.eso.bg/prcl/`) requires login. Third-party dashboard (softel.bg/energy) documents the same endpoints and notes CORS limits [V].
- Node resolution: national/system only. Not useful for siting beyond system-level load shape.

### 2.5 Статистическа книжка (Statistical booklet) [V]
- "Статистическа книжка 2025", `https://www.eso.bg/fileObj.php?oid=5908` (18 pp, PDF created 30.03.2026); earlier editions oids 5390, 4990, 4528, 3572, 3178, 2679 (page `doc/?pbook`). Contains national installed capacity by type, generation by type, **substation counts by voltage with total transformer MVA**, line lengths by voltage (400/220/110/60 kV, cable km), list of 400 kV interconnectors with neighbour TSO and length, monthly load. National aggregates only; annual, ~Q1 lag.

### 2.6 Network scheme image and structure [V]
- `https://www.eso.bg/doc?13=` describes 13 grid operating regions (МЕР) + 15 sub-regions with seat cities; links a JPEG single-line scheme of the 400/220/110 kV system `fileObj.php?oid=5186` (2244×1289 px, ~1.2 MB). Image only; no GIS download.

### 2.7 Projects and EU-funded programmes [V]
- `http://projects.eso.bg/` — PCI pages: Maritsa East–Nea Santa (GR), Maritsa East–Burgas, Maritsa East–Maritsa East 3, Maritsa East–Plovdiv, Dobrudzha–Burgas (400 kV cluster). CARMEN PCI page `doc?565`; GREENABLER (Modernisation Fund grid reinforcement) `doc?570`. Descriptive HTML.

### 2.8 Other ESO disclosures
- Quarterly procurement/expenditure disclosure to the Ministry of Energy under Наредба Е-РД-04-4 (e.g. `me.government.bg/uploads/manager/source/ESO_pril2_q2_2025.pdf.pdf`, 10 pp) — procurement lines, not grid data [V].
- data.egov.bg: no ESO dataset could be confirmed — portal returned HTTP 403 to both curl and WebFetch [F].

---

## 3. Regulatory framework for connecting consumers (KEVR / Energy Act)

### 3.1 Energy Act (Закон за енергетиката, ЗЕ) [V]
- Consolidated text: `https://lex.bg/laws/ldoc/2135475623` (HTML, cp1251; header shows amendments through **ДВ бр. 70 от 4 Август 2026 г.**, with 2025–26 amendments in ДВ 44, 47, 67, 81, 95/2025 and 16, 51, 55, 69, 70/2026). WebFetch is blocked (403) but plain curl works. Also on KEVR: `dker.bg/uploads/normative_docs/zakon_za_energetikata.pdf` (2023 vintage, poor text layer) and `dker.bg/files/DOWNLOAD/ze.pdf`.
- Relevant articles (as read on lex.bg):
  - **чл. 21(3) т. 8** — KEVR approves the 10-year transmission plan and monitors implementation.
  - **чл. 81г** — TSO drafts, consults and submits the 10-year plan to KEVR annually by 30 April; content requirements (see 1.1); KEVR public consultation (ал. 3).
  - **чл. 116** — duty to connect producers/storage; (2) operator determines technically feasible connection point per security criteria and approved development plans; (3, amended ДВ 47/2025) operator performs grid expansion/reconstruction needed for producer/storage connection up to the connection point (may be done by the producer under the contract); (4)–(5) ownership of HV/MV installations and lines; (7) connection procedure set by a KEVR ordinance (= Naredba 6); (8) TSO may not refuse a producer/storage on the basis of possible future transmission constraints.
  - **чл. 117** — duty to connect **every consumer object** that has compliant installations, has met connection conditions and has signed a connection contract at the regulated price; (3) procedure per the чл. 116(7) ordinance, connection term not longer than the object's commissioning term; (4) any refusal must be reasoned in writing; (5)–(6) HV/MV installations and non-network lines serving a single non-household client are built at the client's expense and remain its property.
  - Keyword scan of the consolidated text: no occurrence of "център за данни/дейта", "спекулатив", or a connection-application guarantee for consumers in ЗЕ itself. ESO's publicly requested power to refuse "speculative" projects (eurocom, 29.06.2026) is therefore **not visible in the Act as consolidated on lex.bg**; whether a bill is pending is unverified.
  - Guarantee for RES producers is in ЗЕВИ чл. 29(1) (referenced by Naredba 6); not extracted here.

### 3.2 Naredba № 6 от 28.03.2024 г. за присъединяване на обекти към електрическите мрежи [V]
- **Note: the 2014 Naredba 6 named in the task has been repealed and replaced.** Current act: issued by KEVR, ДВ 28/02.04.2024 (in force 02.04.2024), amended ДВ 84/04.10.2024 and **ДВ 35/14.04.2026** (in force 14.04.2026). Consolidated PDF (78 pp, text): `https://www.dker.bg/uploads/normative_docs/naredbi/naredba_6_14042026.pdf` (KEVR ordinances page `dker.bg/bg/za-kevr/normativka-baza/naredbi.html`). Earlier consolidation: `Naredba_6_05042024.pdf`; ДВ text: `dv.parliament.bg/DVWeb/showMaterialDV.jsp?idMat=211280` [S]; EUR-Lex NIM:202405068 [S]. The 2014 text (`Naredba_6_06032023.pdf`) is historical only.
- April 2026 amendment: KEVR consultation 11–25.03.2026 (`strategy.bg/bg/public-consultations/12202`) — capacity sharing among RES producers, EV-charging simplification, storage at existing sites, hybrid plants, guarantees for closed-DSO operators; RRP milestones C4.R6 and C8.R5 [V].
- Structure: Глава 2 = consumer connection (Раздел I искане; II условия; III становище и предварителен договор; IV договор; V проектиране/изграждане; VI въвеждане; VII граница на собственост; VIII мощности); Глава 3 producers; Глава 4 storage; Глава 5 network operators/closed DSOs; Глава 6 misc.
- Key consumer provisions (article numbers verified in the consolidated text):
  - **чл. 7(1)** cases requiring an "искане за проучване на условията за присъединяване" (new object = т. 1); **чл. 7(2)** applicant for a new object must hold a right to build on the property (вещно право да строи).
  - **чл. 8** completeness check within 5 working days; 30 days to cure deficiencies. **чл. 9** contents of the request, incl. commissioning date and phases (т. 7).
  - **чл. 10(2)** DSO must coordinate with ESO within 14 days when a consumer connection to the distribution grid changes DSO–TSO contracts or requires works in the transmission grid; **чл. 10(4)** the other operator replies within 7 days with an indicative connection price for its network. (No numeric MW/kV threshold for transmission vs distribution connection is set in the ordinance; the level is determined by the operator's conditions, чл. 12.)
  - **чл. 14** refusal grounds (technical impossibility within the requested commissioning term; deterioration of transmission conditions for other objects due to lack/excess of capacity); refusal must state remedial measures aligned with network development plans.
  - **чл. 15(2) т. 1** opinion (становище) within **14 days** of the request for new consumer objects; extendable by agreement for complex schemes (ал. 4) and by the DSO–TSO coordination time (ал. 5).
  - **чл. 16 т. 3** opinion validity for consumer objects: **one year**.
  - **чл. 16а** (new 2024, amended 2026): guarantee (deposit or bank guarantee) of **€25,564.59 per MW** of *increased connected capacity*, due within 3 months of the opinion — but only for requests under чл. 7(1) **т. 15 and 17** (storage added to an existing consumption site that increases connected capacity). As read, **no application guarantee is imposed on a new pure consumption object**; the parallel guarantees are чл. 57а (producers) and чл. 84а (storage objects). [V text; legal interpretation should be confirmed by counsel.]
  - **чл. 17** request for a preliminary contract within the opinion's validity; **чл. 18(1)** operator issues draft within 15 days; **чл. 18(3) preliminary contract validity: 2 years**; чл. 18(4) procedure terminates if not returned signed within 15 days.
  - **чл. 19** design approval (operator responds within 15 working days; +≤30 days if another operator must agree).
  - **чл. 20(1)–(2)** connection contract is concluded with the holder of the opinion/preliminary contract **or with a person holding ownership or another real/obligational right of use over the site for which another person holds the opinion/preliminary contract** — this is the mechanism by which connection rights follow the site (SPV/owner change); **чл. 21** contract must be concluded before expiry of the opinion/preliminary contract and after building permit.
  - **чл. 40–46** предоставена/присъединена мощност: connected capacity set at 110–130% of contracted supplied capacity (чл. 41(2)); HV/MV loads >100 kW metered on 15-min basis (чл. 42).
  - Closed distribution networks: objects >40 MW (чл. 124-related) have connected capacity set jointly by the two operators [V].
- Can support: procedure, deadlines, validity, guarantees, transfer route. Cannot support: capacity data.

### 3.3 Other rules
- **ПУЕЕС** (Правила за управление на електроенергийната система) — N-1 criteria чл. 13–14, voltage limits чл. 21 (cited by ESO). Copies: `dker.bg/uploads/normative_docs/PRAVILA_UPR_na_EES_08_2022.pdf` (ДВ 62/2022 version) [S], `eso.bg/fileObj.php?oid=117` [S], EUR-Lex NIM:202507014 (2025 notification) [S]. Latest consolidated version not verified.
- KEVR connection-price decisions: e.g. Ц-6/22.01.2025 (ERM Zapad distribution connection prices) [V list]. Decision Ц-8/30.06.2026 (133 pp) is RES feed-in/premium prices, **not** ESO tariffs [V]. ESO transmission/access tariffs for 1.7.2026–30.6.2027 not located (KEVR 2026 decisions page lists none by that name) [V].
- Regulation (EU) 2016/1388 (DCC) applies to demand connection (cited in ESO explanation) [V].

---

## 4. DSOs — hosting-capacity / free-capacity publications [V]

| DSO | Tool | Coverage | Granularity | Output | Consumers? | Date |
|---|---|---|---|---|---|---|
| **ЕРМ Запад (Electrohold)** | "Проверка за наличие на капацитет … за ВЕИ производители" `ermzapad.bg/bg/za-klienta/uslugi/prisedinyavaniya/proverka-za-nalichie-na-kapacitet-na-erm-zapad-za-vei-proizvoditeli/` | West BG | област→община→населено място | yes/no availability, no MW | No (RES producers) | "last updated Feb 2025" (per fetch) |
| ЕРМ Запад | Public register under ЗЕВИ чл. 28 `info.ermzapad.bg/erm_vei/` | — | application-number lookup | status | No | — |
| ЕРМ Запад | Consumer connection page `…/prisedinyavane-na-potrebitel-km-elektrorazpredelitelnata-mrezha/` | — | — | procedure, fees (≤400 kW tabulated; >400 kW individual), guarantee text | Yes (procedure only) | — |
| ЕРМ Запад | "Предоставена мощност" page | — | — | how to change contracted capacity; no map | — | — |
| **Електроразпределение Юг (EVN)** | "ProduceCapacity" `elyug.bg/ProduceCapacity/ProduceCapacity.aspx` | 9 southern districts | GIS map by area | territorial RES connection potential | No (RES) | not shown |
| **Електроразпределение Север (Energo-Pro)** | "Проверка на капацитета на електроразпределителната мрежа" `erpsever.bg/bg/prisyedinjavane-kym-mrejata/proverka-na-kapaciteta-na-elektrorazpredelitelnata-mreja` | NE BG | област→община→населено място | "налична / няма налична свободна мощност" | No (RES) | not shown |

Finding: **no DSO publishes 110 kV or 20 kV hosting capacity in MW for consumers.** A 50–150 MW load would in any case be a transmission (110 kV+) connection or a DSO connection requiring ESO coordination under Naredba 6 чл. 10(2).

---

## 5. Government / statistical / other datasets

- **BAI Interactive Investment Map** `https://investmap.government.bg/` [V]: zone records (e.g. `/bg/publications/2`, `/61`, `/1`, `/47`) with fields: total/free area, year, status, ownership, infrastructure (electricity "капацитет" field — units inconsistent, e.g. kW figures), water/sewer/gas, distances to motorway/rail/port/airports, labour statistics, land price/rent, PDF presentation, cadastral link. No API; HTML + PDF. Supports site shortlisting, not grid capacity.
- **НКИЗ (National Company Industrial Zones)** `http://www.nciz.bg/` [V]: zone/project pages ("Проекти", "Терени в развитие"), press; no MW registry. Concept doc for Sofia–Bozhurishte park (mi.government.bg PDF) [S].
- **НСИ**: "Производство и доставки на електрическа енергия" `nsi.bg/statistical-data/81/293` → `Energy-1.4.Electricity.xlsx` (sheets 2019 and 2024–2026: monthly gross/net production, imports, exports, net consumption, national) [V]; "Крайно енергийно потребление по сектори" `…/77/278` [V]; prices for non-household clients `…/80/292` [S]. **No electricity consumption by област found** in NSI's regional statistics menu [V].
- **data.egov.bg**: HTTP 403 to automated access [F]; content unverified.
- **Ministry of Energy — Territorial Just Transition Plans** `https://www.me.government.bg/themes-c389.html` [V]: EC-approved plans for Стара Загора, Перник, Кюстендил (approval 21.12.2023 per BCCI/eufunds [S]) + drafts, PwC/World Bank reports, SEA documents. Coal closure schedules: not visible on the index page; press (economic.bg, Sept 2025 [S]) reports the RRP mandatory phase-out schedule for Maritsa East was removed and replaced by operating limits; HRW (Dec 2025) [S]. ESO plans model a full coal-stop scenario for 2034/2035 [V]. Plan 2025–2034 Приложение 1 lists the thermal plants consulted [V].
- **ENTSO-E Regional Investment Plan 2024 – Continental South East** (June 2025, 64 pp) `eepublicdownloads.blob.core.windows.net/…/entso-e_RIPs_2024_CSE_250612.pdf` [V]: Bulgaria-relevant needs/boundaries (BG–RO, BG–GR, BG–RS, BG–MK, BG–TR incl. project "TR 1066"), completed 400 kV BG–GR line; regional maps and capacity needs; no Bulgarian internal node data.
- **IBEX** `https://ibex.bg` reachable [V]; national day-ahead/intraday prices — no locational signal.
- **Company registry**: papagal.bg mirrors Trade Register entries (e.g. Schwarz Digits Bulgaria EOOD, EIK 205158327, renamed 02.03.2026) [S].

---

## 6. Data-centre / large-load announcements in Bulgaria (announcements only; no judgement)

### 6.1 ESO aggregate connection-request statistics (national totals only)
| t_public | Source | Statement | Status |
|---|---|---|---|
| 31.10.2025 | BTA 999209 (ESO ED A. Tsachev) | ESO ready to connect large consumers and offer telecom connectivity to data centres; regional interconnection funding gaps noted | [V] |
| 26.05.2026 | Mediapool news383484 (interview, ESO ED Kiril Georgiev) | ~9,000 MW of data-centre connection requests; ~3,710 MW with completed technical opinions; **a breakdown by region is given**; "some may not be realised" | [V] |
| 29.06.2026 (URL date; page cites data as of 03.08.2026) | eurocom.bg | 9,330 MW total (5,535 MW intentions + 3,795 MW with opinions); opinions valid 1 year under Naredba 6; ESO requested a legal change to refuse speculative projects; regional breakdown given | [V] |
| 08.07.2026 | Capital interview "Имаме заявки за близо 9000 MW" | — | [F 403] |
| 24.07.2026 | Mediapool news385791 | ~9,000 MW by end-May; 3,710 MW assessed; regional list; commentary on speculative applicants (€1-capital companies, RES/battery developers), suggestion to require dual-substation supply | [V] |
| Jul/Aug 2026 | economic.bg "надхвърлят 9 GW" | headline verified; body not extracted | [V partial] |
| 18.08.2026 | Capital "Идва цунами от центрове за данни" | per snippet: ESO data; regional breakdown | [F 402] |
Note the 3,710 vs 3,795 MW discrepancy between sources; both are as printed.

### 6.2 Named projects / deals (dates = t_public of the cited item)
| Date | Party | What was announced | Location | MW | Investment | Source / status |
|---|---|---|---|---|---|---|
| 12.05.2026 | Government (T. Donchev) | Three agreed memoranda for data centres: Schwarz Digits (DE), a second German company, a "very large" US company; "two of three realistic"; possible Belene NPP link | not stated | not stated | not stated | BTA bg 1124599 / en 1124611 [V]; dbr.bg [V]; banker.bg [F] |
| 02.03.2026 | Digital Realty | Acquisition of Telepoint (two Sofia data centres; interconnection hub) | Sofia | not disclosed (one snippet: Telepoint 3 sites incl. Montana, 14.8 MW total — [S]) | not disclosed | telepoint.bg [V], capacityglobal [V], DCD [F] |
| 30–31.07.2026 | Brinell Compute (DE) | AI data-centre campus; construction start autumn 2026; ~809 ha (2,000 acres) | Rakovski Industrial Zone, Maritsa municipality (Plovdiv area) | not disclosed | €3 bn | data-central.co.uk [V]; DCD [F]; BeBeez, idcnova [S] |
| Mar 2025 | EU/Sofia Tech Park | BRAIN++ AI Factory (Discoverer++ supercomputer) | Sofia | not stated | not stated | [S] |
| n.d. | TOP SYSTEMS | "first industrial green data centre", 2 MW, 1,200 m², completion 2026 | Burgas | 2 | not stated | topsystems.bg [S] |
| n.d. | VueNow InfoTech | "up to seven data centres in Bulgaria" | not stated | not stated | not stated | DCD [F]; [S] |
| 2025–26 | (directories) | datacentermap: 30 facilities/48 operators; aidatacenterindex: 1 AI location, 2 MW | — | — | — | [S] |

A comprehensive announcement register does not exist publicly; the closest is ESO's internal request list, of which only totals/regional aggregates reach the press.

---

## 7. Assessment of what the evidence can and cannot support (source-level, not site-level)

- **Exists and is machine-readable**: substation-level capacity categories and remaining capacity per voltage level (ESO map API, undocumented, no licence); line/substation geometries; planned reinforcements per node; national load/generation series.
- **Exists as PDF**: 10-year plans (approved 2025–2034; draft 2026–2035 with municipality-level load/RES maps as images), KEVR project list with years, regulations.
- **Does not exist publicly (as found)**: per-substation N-1 headroom studies; consumer connection queue/register; per-project costs; DSO consumer hosting capacity; regional electricity consumption statistics; a licence statement for ESO data.
- **Requestable**: formal "искане за проучване" to ESO yields a binding opinion within 14 days (+coordination), valid 1 year; the map explicitly is not a substitute.

---

## 8. Fetch failures, blocks and unverified items
- capital.bg (HTTP 403; tollbit redirect 402), datacenterdynamics.com (403), banker.bg (403), data.egov.bg (403 curl and WebFetch), lex.bg via WebFetch (403; curl OK), ESO internal JSON endpoints (`rabota_na_EEC_json.php`, `scada_live_json_pure.json`), KEVR Ц-27/2016 URL guesses (404), KEVR news pagination (`?page=N` returns page 1), KEVR `_CGCalendar/2026/rep_TYNDP_2026-2035_26.pdf` guess (404).
- Unverified [S] items are marked inline; notably: EC approval date of JTPs, removal of coal phase-out schedule, Telepoint 14.8 MW, VueNow, TOP SYSTEMS, BRAIN++, Ц-27/2016 as basis of ESO study fee.
- WebSearch quota exhausted (200/200) before completing the announcement sweep and before locating ESO's 2026/27 tariff decision.

---

## 9. Local artefacts saved (scratchpad `/tmp/claude-1000/-home-jdimov-dev-grid-mysteries/30929f2d-09f2-4442-b2ec-d902c76d3723/scratchpad/`)
`plan_oid5850.pdf` (draft 2026–2035; sha256 6691fc88…), `plan_oid5665.pdf` (2025–2034, Nov 2025; sha256 589063cc…), `plan_2025_2034.pdf` (oid=5354, Mar 2025), `oid5272.pdf`, `oid3505.pdf`, `oid1088.pdf`, `oid398.pdf`, `oid2512.pdf` (older plans), `kevr_dprm2.pdf`, `kevr_rep_tyndp_2025.pdf`, `kevr_prot_zz279.pdf`, `naredba6_2026.pdf`, `kevr_c8_2026.pdf`, `pbook_latest.pdf`, `rip_cse.pdf`, `me_eso_q2.pdf`, `points.geojson`, `lines.geojson`, `linesteps.json`, `network.json`, `pj.json` (one substation record — contains node-level values; do not publish), `azmap.js`, `map_index.js`, `map5186.bin` (network scheme JPEG), `lex_ze.html`, `nsi_el.xlsx`, and the corresponding `.txt` extractions. Fetch time for all: 2026-08-25.
