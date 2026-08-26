# Romania — evidence-availability reconnaissance for siting a 50–150 MW transmission-connected load

Reconnaissance date: 2026-08-25/26. Scope: what public or requestable electricity-system evidence exists; NOT which nodes look attractive. No node-level numbers are reported.

## Verification legend

- **[FETCHED]** — document/page retrieved and inspected (WebFetch, or curl + pdftotext) in this session.
- **[SNIPPET]** — seen only in search-engine result text; not opened.
- **[BLOCKED]** — fetch attempted and failed (reason given). URL is from search results or a linking page.
- Tooling notes: `legislatie.just.ro` was unreachable from this environment on every attempt (curl HTTP 000; WebFetch "socket hang up"), so every consolidated-law fact below comes from secondary hosted copies (lege5 free excerpts, DSO-hosted PDF printouts) and is labelled accordingly. Web-search budget was exhausted (200 calls) before the last few DSO/INS checks; those gaps are stated explicitly.

---

## 0. Headline map of what exists (one paragraph per question the ranking would need)

| Need | Best public source | Node resolution | Verified? |
|---|---|---|---|
| Present loading of RET elements, per-station consumption | PDRET 2026-2035 Annexes B-1, B-3, B-4, G (Transelectrica; ANRE consultation copy) | per 110 kV bus / per line / per (auto)transformer | FETCHED (PDF, text layer) |
| N-1 regime analysis and reinforcement needs 2028/2030/2035 | PDRET 2026-2035 ch. 6.3.1 + Annex 3 + Annex A + Annex G | per RET section (S1…S5) and per element | FETCHED |
| Consumption forecast by zone | PDRET Annex C-1 "Prognoza consumului pe zone 2026-2035" | zone (Transelectrica planning zones) | FETCHED (exists; not extracted) |
| Generation forecast by node | PDRET Annexes C-2, C-3, C-4 — marked "nu se publică" | — | FETCHED (confirmed withheld) |
| Reinforcement project list with dates | PDRET ch. 7.2 + Annex F-3 (project, PIF year previous vs current edition, slippage, stage) | per project | FETCHED |
| Project costs | PDRET ch. 8 (aggregate) — Annexes F-1, F-2 "nu se publică (cu valori)" | aggregate only | FETCHED |
| Available connection capacity per zone | Transelectrica "Hărți capacități de racordare disponibile" + annual 15-Jan allocation publication | 10 zones (A–J) of the 110 kV network + RET 400/220 kV per zone | FETCHED — **generation only**; no consumer equivalent exists |
| Queue / register of connection requests | (a) Government ATR list 25 Apr 2026 (≥1 MW holders), (b) Transelectrica "Centralizatorul cererilor de alocare", (c) DEER Anexa 9.1/9.2/9.3 xlsx | (a) county + operator, (b) zone, (c) 110 kV/MV connection station | FETCHED — all generation-oriented; **no register of large-load applications** |
| Planned outages | Transelectrica "Programul anual de retrageri RET" 2008–2026 xlsx | per equipment | FETCHED (page) |
| Consumer connection rules, ATR validity, guarantees | ANRE Ord. 59/2013 as amended by Ord. 20/2025 and Ord. 15/2026 | — | FETCHED via secondary copies (see §3) |
| DSO hosting-capacity maps | Delgaz Grid HV capacity map (2022 image PDF), MV consum/generare maps (access-code); DEER Anexa 9 lists; RER/DEO: none found | 110 kV station / MV feeder | Partly FETCHED |
| Load by county | energymap.ro (Senate initiative, 2021-2024); INS TEMPO (not verified) | county | FETCHED / not verified |
| Industrial parks registry | MDLPA/dpfbl.mdrap.ro xls | park | FETCHED (files exist; cells not parsed) |
| Coal closure calendar | OUG 108/2022 + renegotiated PNRR calendar + OUG 20/2026 + Aug-2026 parliamentary amendment | unit | SNIPPET only |
| Data-centre announcements | Press (DCD, Profit.ro, Romania Insider, baxtel) | site | FETCHED individually (§6) |

---

## 1. Transelectrica ten-year RET development plan (PDRET)

### 1.1 PDRET 2026-2035 (latest edition) — under ANRE consultation, NOT yet approved as of 2026-08-25

- **Publisher:** CNTEE Transelectrica SA (author); ANRE (consultation host).
- **Name:** "Planul de Dezvoltare a RET 2026-2035" / RET Development Plan 2026-2035. Internal: CTES aviz nr. 516/2025; project team decision nr. 513/19.06.2025; CTES internal approval 30 July 2025; Directorate note nr. 43817/17.10.2025 for shareholder (AGA) approval. [FETCHED: note PDF, 36 pp, https://www.transelectrica.ro/documents/10179/20107572/01_RET+2026_2036.pdf/1e9ecb0a-4ac4-4366-97cb-e3f90a1f0b89?version=1.0]
- **ANRE status:** Transelectrica filed the plan with ANRE under reg. nr. 290821/11.06.2026. ANRE opened public consultation **17 June 2026** (30-day window; comments to smie@anre.ro) with a *draft* decision "Proiect de Decizie nr. ___ din __.__.2026". [FETCHED: https://anre.ro/proiect-de-decizie-privind-aprobarea-planului-de-dezvoltare-a-retelei-electrice-de-transport-pentru-perioada-2026-2035/]. A site search of anre.ro for "2026-2035" on 2026-08-25 returned only the draft-decision page — **no final approval decision found** [FETCHED: anre.ro/?s=2026-2035]. Press (InvesTenergy) framed it as "pe masa ANRE" [SNIPPET].
- **Files (all verified downloadable, PDF with text layer):**
  - Plan: https://anre.ro/wp-content/uploads/2026/06/Planul-de-Dezvoltare-RET_2026-2035.pdf — **523 pages, 39.9 MB**, created 17 Jun 2026. Main body ~120 pp + all published annexes in one file.
  - Referat de aprobare (14 pp): https://anre.ro/wp-content/uploads/2026/06/Referat-de-aprobare_PDRET_2026-2035.pdf
  - Draft decision (3 pp): https://anre.ro/wp-content/uploads/2026/06/Proiect-Decizie-aprobare-PDRET-cons-publica.pdf — Art. 1 approves plan (annex 1) with obligations for the next edition (annex 2).
  - Transelectrica's own site page for 2026-2035 was not found; the 2024-2033 page does not link it [FETCHED].
- **Content (from TOC and spot reads):**
  - Ch. 5.2 consumption scenarios: national top-down econometric reference scenario (Tables 5.2.1–5.2.3: population, GDP, intensity, net internal consumption TWh, net peak MW, sectoral final consumption 2013-2024, forecast 2025/2026/2030/2035); text lists "apariția unor noi consumatori" among assumptions. The string "centre de date" returns **0 hits** in the whole plan text; "data center" 2 hits (one in a company-list context, one in a smart-grid taxonomy) — i.e. no explicit data-centre load scenario is visible in this document. (A Profit.ro article of 20 Aug 2026 attributes a 2030/2035 data-centre MW forecast to Transelectrica; I could not identify the source document — see §6.)
  - Ch. 6.3.1 "Necesități de întărire a RET 2026-2035": summary of regime analyses by RET **section (Secțiunea S1…S5)** for stage 2028; detailed results in Annex 3; N-1 mentioned 77 times.
  - Ch. 6.3.3 congestions 2017-2026 avoidable with projects; 6.3.4 RET–RED transfer capacity projects.
  - Ch. 7.1 comparison with 2024-2033 edition; 7.2 project list (retechnologisation and development, by station/line name); ch. 8 aggregate CAPEX (fig. 8.1, comparison with previous edition); ch. 9 financing; ch. 10.1 status of obligations under ANRE Decision nr. **2715/17.12.2024** (which approved the 2024-2033 plan).
  - Fig. 5.5.1 "Harta RET care include și stațiile electrice construite pe tarif de racordare" (RET map incl. stations built on connection tariff).
  - **Published annexes:** 1 (RET current state 2021-2025), 2 (adequacy ERAA 2024), 3 (regime analysis in perspective), 4 (energy efficiency), 5 (DigiTEL), 6 (technical state RET/RED), 7 (maintenance strategy), 8 (critical infrastructure), 9 (environment); A (case construction and regimes for dimensioning); **B-1 "Consumuri realizate pe stații"** (per 110 kV bus in Transelectrica stations: columns NOD, NUME_BARA, SIMBOL, DET, SD, T, then P/Q at characteristic instants coded VD_14, VS_22, GN_04, GS_4 — winter day/evening, summer night/day); B-2 RET components (stations, lines, reactors); **B-3 loading of RET equipment, winter peak 2025** (tables 1-5: 400 kV lines, 220 kV lines, transformers…: I [A], Iadm [A], I/Iadm %); **B-4 loading summer 2024-2025**; B-5/B-6 voltages; B-7 short-circuit currents; B-8 ancillary-service qualification; **B-9 reliability indicators for RET nodes and 110 kV nodes**; C (production/consumption balance 2026-2035) with **C-1 consumption forecast by zone 2026-2035**; D static stability; F (fixed-asset strategy) with **F-3 project monitoring** (columns: Nr, Denumire proiect, Inclus în PI (poz), An estimat PIF previous period, An estimat PIF current period, Decalare (ani), Etapa de realizare, Observații) and **F-4 interconnection projects list** vs 15 % target; **G "Încărcări elemente RET 2026, 2030, 2035"**; H R&I / smart-grid strategy.
  - **Withheld annexes ("nu se publică"):** C-2 evolution of generation fleet; C-3 unit loadings at characteristic instants; **C-4 available and generated power per network node at peak**; E-1/E-2/E-3 maintenance schedules & station technical state per zone; F-1 unit costs; F-2 CAPEX schedule with values.
  - A table headed "Nr. Crt. / Denumire proiect / Valoare estimată / 2026 … 2035" exists in the file; I did not verify whether the value column is populated (the annex list says F-2 is published "fără valori").
- **Machine readability:** text-layer PDF; annex tables are layout tables (pdftotext -layout parses them; numbers use decimal comma). No XLSX.
- **Geography/resolution:** national; per RET element and per 110 kV bus for realised data; per zone for forecasts; per section for N-1 summaries.
- **Temporal:** realised 2024-2025 snapshots; forecast stages 2026/2028/2030/2035. Historical + future.
- **Lag/frequency:** every 2 years by law (Law 123/2012 art. 35); 2026 edition data vintage mid-2025; next edition 2028.
- **Licence/access:** free download, no licence statement; ordinary company can obtain. Consultation comments possible.
- **Supports:** existence and 2024-25 loading of elements; forecast zone consumption; which reinforcements are planned and when; which sections are deficit/surplus; N-1 results as summarised.
- **Cannot support:** node-level available *consumption* capacity (never published); generation per node (withheld); project costs (withheld); anything post-approval (decision pending); the plan's own caveat that authorisations delay lines by 2-3 years.

### 1.2 PDRET 2024-2033 (last APPROVED edition)

- **ANRE approval:** Decizia președintelui ANRE **nr. 2715/17.12.2024** [FETCHED — cited in PDRET 2026-2035 ch. 10.1 and in the Oct-2025 Directorate note]. ANRE consultation page exists: https://anre.ro/proiect-de-decizie-privind-aprobarea-planului-de-dezvoltare-a-retelei-electrice-de-transport-pentru-perioada-2024-2033/ [SNIPPET]. Press: 9.49 bn lei, 12 new projects, four axes [SNIPPET, economica.net].
- **Transelectrica page:** https://www.transelectrica.ro/ro/web/tel/planul-de-dezvoltare-ret-2024-2033 [FETCHED] linking three PDFs, all verified downloadable:
  - Plan: https://www.transelectrica.ro/documents/10179/18209732/Planul+de+Dezvoltare+RET+2024-2028-2033.pdf/8df19499-8c2a-43e5-9c33-5a09f8e82610 — 134 pp, text layer, created 13 Oct 2024.
  - Anexe 1-9: https://www.transelectrica.ro/documents/10179/18209732/Anexe+1-9.pdf/99eca375-728e-41ed-8ae9-cc2e82e54f00 — 160 pp.
  - Anexe A-H: https://www.transelectrica.ro/documents/10179/18209732/Anexe+A-H+postare+site.pdf/a2513ac7-e2a3-489d-828e-57121122735c — 198 pp, incl. B-1 station consumption for January 2023 and July 2023, B-2 station/line/reactor inventories, B-3 loading tables (line, I, Iadm, I/Iadm %), B-4, B-5, B-6, B-7, B-8, C-1, D. Mirror copies at web.transelectrica.ro/noutati/noutati/word/ (PPDRET 2024-2028-2033.pdf; Anexe 1-9.pdf) [SNIPPET].
- Older editions (2022-2031, 2020-2029, 2016-2025) also online [SNIPPET; linked from the 2024-2033 page per FETCH].

### 1.3 Transelectrica annual investment programme

- "Nota privind stabilirea Programului de investiții pentru anul 2026 și estimări 2027-2028" (PAI 2026), Direcția Investiții nr. 20952/DI/16.04.2026, 44 pp, with Anexa 1 project list [FETCHED: https://www.transelectrica.ro/documents/10179/22143105/01_Nota-stabilirea+Programului+de+investi%C5%A3ii+pe+anul+2026+%C8%99i+a+estim%C4%83rii+cheltuielilor+de+investi%C8%9Bii+pentru+anii+2027+%C8%99i+2028.pdf/d61fb23c-efc0-4188-892e-02e2e8dc7a3f?version=1.0]. Press: programme up >30 % vs 2025 [SNIPPET]. Supports: which plan projects are funded in 2026-28; cannot support node capacity.

---

## 2. Other Transelectrica published data

### 2.1 Available connection capacity maps ("Hărți capacități de racordare disponibile")

- URL: https://web.transelectrica.ro/harti_crd_tel/ [FETCHED]. Interactive web app; **10 network zones (A–J) of the 110 kV distribution network plus cross-border**; year selector (2025 present, 2030 perspective); per-zone table with columns **CR, ATR, Studii, Cereri, Total** (MW of generation in each procedural stage); 10 methodology notes (N-1 criterion; capacity = RET-connectable generation + surplus of 110 kV RED zones; note 7: "Situația generală a puterilor instalate în centrale electrice în diverse stadii (CR, ATR, studiu de soluție avizat/în curs de avizare sau cerere cu documentație completă) **se actualizează lunar**"; note 8 lists "puterea consumată în zona analizată (racordarea consumatorilor cu CR sau ATR fără întărirea rețelei)" among factors that change the values). No XLS/PDF download links in the page HTML [FETCHED: zero matching hrefs]. Launched 15 Dec 2021 [SNIPPET, economica.net]. **Scope: generation/storage only. No consumer (absorption) capacity map exists on the Transelectrica site** — consumers appear only as a factor reducing generation headroom.
- Underlying rules: Ordin ANRE 137/2021 (procedure for available capacity for new generation; MO 1/3 Jan 2022; amended 99/2023, 108/2023) [SNIPPET; legislatie.just.ro/Public/DetaliiDocument/250117 BLOCKED]; Ordin ANRE 53/2024 allocation methodology (§3.6).

### 2.2 Capacity-allocation (auction) process and its registers

- Page: https://www.transelectrica.ro/procesul-de-alocare-a-capacitatii-retelei-electrice [FETCHED via WebFetch; curl returned a 16-byte bot block]. Documents: publication notice (June 2026); "Procedura privind alocarea capacității rețelei electrice pentru racordarea locurilor de producere" (June 2026 revision); Anexa 1 application; Anexa 2 bid; Anexa 3 allocation contract; **Anexa 4 "Zone de rețea RET și RED"** (zone definitions); Anexa 5 platform guide; bank-guarantee model; Ordin ANRE 15/2026 copy. Platform: https://licitatii.transelectrica.ro.
- **"Centralizatorul cererilor de alocare"** — table + map of allocation requests by network zone, requested MW, planned commissioning year, for the 1–14 July 2026 session. Production only.
- Earlier procedure version nr. 36553/2.10.2025, 15 pp [FETCHED: https://web.transelectrica.ro/noutati/noutati/word/Procedura_Alocare%20capacitati.pdf]: §I global study determines available capacity per zone at **400 kV and 220 kV (RET)** and **110 kV per DSO concession (RED)**, counting reinforcement works from valid ATRs/CRs/solution studies of both production and consumption sites; §II **by 15 January of year N the OTS publishes available capacities from year N+2 per zone per year**; §III requests 16 Jan–end Feb; §V by **15 June** publishes global-study results, available capacity per zone, extra capacity from additional works in N and N-1, requested capacity individually and total, estimated value of additional works, starting price, auction dates; §VI auctions from 1 July, participation guarantee = MW × 1 % of starting price (the ANRE 21 May 2026 release states **20,000 EUR/MW for 2026** and a weighted-average formula from 2027 — see §3.4). Scope: "loc de producere" is read to include "loc de consum și de producere" (co-located); **consumption-only sites are outside this procedure**.
- Supports: zone-level generation headroom, requested generation MW per zone, planned reinforcement value per zone. Cannot support: consumer headroom; node-level detail.

### 2.3 ATR / connection-contract registers

- **Government list of ATR holders (≥1 MW cumulative per holder)** — published 25 Apr 2026 by the Government (Bolojan cabinet) from data consolidated by Transelectrica incl. DSO data. Original: https://gov.ro/fisiere/stiri_fisiere/Lista_titularilor_care_detin_ATR.pdf [HEAD 200 verified]; XLSX mirror: https://www.economedia.ro//wp-content/uploads/2026/04/Lista-titularilor-care-detin-ATR.xlsx [HEAD 200, content-type xlsx]; PDF copy inspected: https://www.presshub.ro/wp-content/uploads/2026/05/Lista_titularilor_care_detin_ATR.pdf [FETCHED, 22 pp, source workbook "Lista titularilor care detin ATR.xlsx" created 25 Apr 2026]. **Columns:** Nr. și dată ATR; Denumire titular; CUI; MW; Județ; Operator; Etapa procesuală (verbatim sursa TEL); Data estimată PIF; Etapa procesuală (simplificat); Audit – fișier TEL sursă; Audit sheet; Rând. ~1,230 rows parsed (press: >1,400 ATRs, >1,000 holders, >80,000 MW). Operators: Transelectrica majority of rows; DEER, Rețele Electrice, Delgaz, Distribuție Oltenia also present. **No substation column; generation-oriented (the word "consum" does not occur); described as a snapshot "selecție, nu listă exhaustivă"; no update frequency stated** [FETCHED: economedia article text; Profit.ro FETCHED].
- **Transelectrica "situația generală" monthly** (CR/ATR/studii/cereri per zone) — only inside the map app (§2.1); no file export found.
- **DEER Anexa 9 lists** (§4.1) — per 110 kV/MV connection station, generation only.
- **No public register of consumer/large-load connection requests or of consumer ATRs was found at Transelectrica, ANRE or any DSO.**

### 2.4 RET map

- "Harta RET" PDF: https://web.transelectrica.ro/noutati/noutati/word/HARTA%20RET.pdf [FETCHED: 1 page, 298 KB, created 12 Aug 2025, **image only — no text layer**]. Older copy at https://www.transelectrica.ro/documents/10179/25146/Harta+RET.pdf/51440d46-eff2-4655-949f-c2a494fee2a3 [SNIPPET]. "Date generale" page (https://www.transelectrica.ro/web/tel/date-generale-management) is a JS shell to curl; WebFetch timed out [BLOCKED]. Network stats (81 stations: 1×750, 38×400, 42×220 kV; 8,834 km lines) [SNIPPET]. No GIS/shape download found. Supports: topology at map scale. Cannot support: capacity.

### 2.5 Operational/statistical data

- **Consumption page** https://www.transelectrica.ro/web/tel/consum [FETCHED]: actual national consumption per 15-min dispatch interval (archive 1 Feb 2021–30 Jun 2024; from 1 Jul 2024 in DAMAS II public platform); daily/weekly/monthly hourly forecasts (xls); 1–10-year consumption forecast (xls); long-term perspective (xls/pdf). **National only** — no zone/county split.
- **Real-time SEN**: https://www.transelectrica.ro/web/tel/stare-sen-in-timp-real and map/graph widgets [FETCHED listing]. Third-party mirrors (monitorenergie.ro, consumenergie.ro, sistemulenergetic.ro) [SNIPPET].
- **Network operation page** https://www.transelectrica.ro/web/tel/functionare-retea [FETCHED]: ex-post planned/unplanned outages of interconnection lines (equipment, zone, period, reason, ATC impact); monthly physical exchanges & balance xls 2009-2024; "Raport anual de funcționare SEN" PDF; performance-standard indicators (doc, 2009-2025).
- **Planned outages**: https://www.transelectrica.ro/ro/web/tel/retrageri-ret [FETCHED]: "Programul anual de retrageri din exploatare" (PAR) for equipment and for interconnection lines, 2008–2026, xlsx. Per-equipment rows (titles only seen). Also CREFECHIP internal procedure PDF [SNIPPET].
- **Operational planning study**: "Planificarea operațională a funcționării SEN în vara 2026", DEN, March 2026, public version 67 pp [FETCHED: https://www.transelectrica.ro/documents/10179/92180/Memoriu+studiu+vara+2026_public+final.pdf/18854b51-0b5c-44b0-8a8f-28cf6eb85afa]: TOC — realised consumption summer 2025, forecast summer 2026, capacity balances, N-schema load-flow regimes, regimes with outages, congestion management (some sections marked confidential/removed). Winter equivalents exist by analogy (2022 summer memo seen in search) [SNIPPET].
- **Adequacy study** "Studiu de Adecvanță SEN – etapele 2027, 2030, 2035": page https://www.transelectrica.ro/ro/web/tel/studiu-de-adecvanta-sen-etapele-2027-2030-2035 [page title verified by curl; content is a JS shell; WebFetch timed out — BLOCKED]. Press coverage (economedia, capital.ro, mediafax) says it models consumption growth from EVs, heat pumps and **data centres** and deficit scenarios to 2035 [SNIPPET]. This is the likeliest source of the "370–620 MW by 2030" data-centre figure cited by Profit.ro — **not verified**.
- **ENTSO-E Transparency Platform** (https://transparency.entsoe.eu, REST API): Romania bidding-zone load, generation per type and per unit ≥100 MW, outages, cross-border — national resolution only. Not fetched; standard source.
- **Monthly "Rapoarte lunare alocare"** are interconnection-capacity market reports (ACLI), not connection capacity [FETCHED].
- **data.gov.ro**: a dataset search for "transelectrica" returned a page whose dataset headings my parser could not extract; existence of Transelectrica datasets there is **unverified**.
- **Technical norms** relevant to consumers: "Norma tehnică – Condiții tehnice de racordare la rețelele electrice de interes public a consumatorilor" (Transelectrica-hosted PDF) [SNIPPET]; EU NC DCC implementation; "Modalități de acces la rețea" page https://www.transelectrica.ro/ro/web/tel/modalitate-acces [BLOCKED: JS shell / socket hang-up]; "Anexa 2 – Lista documentelor necesare obținerii ATR" and ANRE-avized "Procedura de emitere a ATR la RE deținută de OTS" (.doc on anre.ro) [SNIPPET]. Press: only connections >50 MVA go directly to Transelectrica [SNIPPET, economisi.ro — unverified rule].
- **Consumer connection tariffs**: methodology Ordin ANRE 11/2014 (amended by 20/2025 and 15/2026) and specific tariffs Ordin 141/2014 [SNIPPET]. No published table of RET connection charges per station found; charges are set per solution study.

---

## 3. ANRE rules for connecting CONSUMERS

### 3.1 Base act and consolidated-text access

- **Ordin ANRE nr. 59/2013** approving the "Regulament privind racordarea utilizatorilor la rețelele electrice de interes public" — MO Part I nr. 517 and 517 bis of 19 Aug 2013; in force 18 Dec 2013. Amended (non-exhaustive, from copies): 63/2014, 111/2018, 15/2019, 22/2020, 68/2020, 160/2020, 16/2021, 17/2022, 105/2022 (framework contracts), 20/2025, 15/2026.
- Consolidated text URLs: https://legislatie.just.ro/Public/DetaliiDocumentAfis/160289 (regulation) and https://legislatie.just.ro/Public/DetaliiDocument/150711 (order) — **[BLOCKED from this environment; URLs from search]**. lege5.ro consolidated: https://lege5.ro/gratuit/gm3tgnbugq/... (order shell only; regulation paywalled) [FETCHED]. ANRE archive index: https://arhiva.anre.ro/ro/energie-electrica/legislatie/norme-tehnice/racordare-la-retele-de-interes-public [SNIPPET].
- Copy actually read: Distribuție Oltenia-hosted lege5 printout of the regulation dated **10 Oct 2024** (53 pp, 76 articles) [FETCHED] — i.e. **pre-Ordin 20/2025 and pre-Ordin 15/2026**; amendments layered from lege5 free excerpts and a Delgaz Grid synthesis. Article numbers below are from that copy unless stated.

### 3.2 Article-level findings (consumer-relevant)

- **Definition** "lucrări de întărire a rețelei electrice": works in the operator's installations needed for evacuation *or consumption* of the additional approved power (annex, definitions).
- **Information request:** Art. 10 — user may ask the operator for connection possibilities; operator must reply with stages and estimated durations. **Application:** Art. 11–14 (content of cerere de racordare). No article found establishing a first-come queue or priority order for consumers (grep "ordinea"/"priorit": 0 hits).
- **Solution study:** Art. 17–18 — required when the regulation on solution setting so provides; contract between operator and user; **paid by applicant on a cost estimate**; delivered "avizat". Ordin 20/2025 (per lege5 summary): delivery 3 months for ≥110 kV, 1 month for MV/LV; ATR within 10 days after study; guarantee proof within 2 months of study communication else file closed (Art. 31(5^2)).
- **ATR validity:** Art. 32 — valid until the connection certificate is issued for the final approved power, unless Art. 33 applies. **Art. 33(1)** cessation: (a) 3 months if guarantee not proven — *production or consumption-and-production >1 MW evacuation only*; (b) **12 months from issue if no connection contract**; (c) at contract termination; (d)/(e) expiry of underlying permits; (f) court annulment of Art. 14(1^1) documents; (g) Art. 36(6) case; (h) at holder's request — then contract ceases, guarantees are executed, capacity is freed (33(3)). Ordin 15/2026 adds lit. (j): 6 months after the autorizație de înființare expires (lege5 excerpt). Art. 33(2): updating the ATR does not extend the (a)/(b) deadlines. Art. 34(1): contract request ≥30 days before ATR expiry (lege5 summary of Ordin 20/2025 says 45 days — unverified).
- **Milestones after contract:** Art. 36(5), (5^1): building permit proof within **12 months from CR signing and 18 months from ATR** — text reads "locuri de producere sau locuri de consum și de producere"; Art. 36(6): failing that the ATR ceases and the CR terminates de jure. Ordin 15/2026 inserts 36(5^2)–(5^8), (6^1), (6^2): ANRE **autorizație de înființare** required for production/cogeneration/storage >1 MW within the same 12/18-month limits, single 12-month extension for non-imputable reasons, automatic extension if operator silent 10 working days; ATR/CR lapse otherwise [FETCHED: Delgaz synthesis; lege5 excerpt]. **As read, the establishment-authorisation milestone does not apply to consumption-only sites; whether Art. 36(5) building-permit milestone applies to pure consumers is not explicit in the copy read — verify in the consolidated text.**
- **Financial guarantee (Art. 31):** (1) production / consumption-and-production >1 MW evacuation — guarantee required; **(2) new consumption site or power increase >1 MW consumption — guarantee required only "dacă sunt necesare lucrări de întărire a rețelei electrice în amonte de punctul de racordare"**; (3) 5 % of connection tariff (Ordin 15/2026: all bases ex-VAT; new (3^1) **20 % for production/consumption-and-production >1 MW**; consumer-only remains at the 5 % rule as read in the lege5 excerpt — unverified against MO); (9)-(10) executed guarantees may only finance reinforcement works in the operator's investment plan. Art. 40^1: extension of CR execution term needs guarantee 5 % rising 5 % per 12-month extension (Ordin 20/2025).
- **Transfer / change of holder:** Art. 6(3)(b) — "schimbarea titularului locului de consum și/sau de producere prin preluarea obiectivului … prin cumpărare, moștenire etc." is an *administrative* modification without technical change; Art. 5(2) obliges the user to request an ATR update; for already-connected sites the certificate is not updated; lege5 2017 excerpt (Art. 17 old numbering) says the updated ATR is issued within 10 working days free of charge. Update fee otherwise half the new-ATR fee (Ordin 141/2014) [SNIPPET]. **No article found restricting transfer of an ATR/CR with the site or on change of SPV ownership; Ordin 15/2026 lege5 excerpt contains no transfer provision.** Whether a change of shareholders of the same SPV triggers anything: nothing found.
- **Reinforcement cost allocation:** Art. 42(1): (a) works needed exclusively for the site; (b) works serving several sites. 42(2) operator executes (a) per CR; 42(3) (b) triggered by energisation requests; 42(4) user's share of (b) is paid per CR and **included in the connection tariff** per the tariff methodology; Art. 43(1) context: where the user opts to build via own contractor, category (a) works are borne integrally by the user through the tariff; Art. 44 execution terms; annex pt. 2.1: for LV households within 100 m, DSO bears reinforcement. Consumer ≥110 kV reinforcement share therefore flows through "tarif de racordare" set by Ordin 11/2014 methodology — the methodology itself was not read.
- **Speculative large-load constraint:** only the mechanisms above (12-month contract deadline; building-permit milestone if applicable; guarantee only if reinforcement needed). No MW-based screening, deposit-per-MW, or auction for consumers found. The 2025-26 reform (§3.4) explicitly targets generation/storage.

### 3.3 Ordin ANRE 20/2025
- MO 501/29 May 2025; in force 1 June 2025 (lege5 summary) [FETCHED lege5 page; legislatie.just.ro/Public/DetaliiDocumentAfis/298436 BLOCKED]. Amends 59/2013, 11/2014, 74/2014, 105/2022 etc. Changes cited above.

### 3.4 Ordin ANRE 15/2026 and companion licensing order
- MO 436/25 May 2026; in force 25 May 2026 [FETCHED: Delgaz Grid synthesis https://delgaz.ro/getattachment/76011c3e-38e3-49d5-b659-63fbec6e9bea/Ordin_ANRE_15_2026.pdf; lege5 page; legislatie.just.ro/Public/DetaliiDocument/310984 BLOCKED]. Amends 59/2013, 74/2014, 105/2022, and the 53/2024 allocation methodology. ANRE press release 21 May 2026 https://anre.ro/24931-2/ [FETCHED]: guarantee 5 %→20 % ex-VAT for production/storage >1 MW; 12/18-month establishment-authorisation deadlines; allocation-auction participation guarantee **20,000 EUR/MW in 2026**, from 2027 min(stated value, weighted-average prior-year auction price); operators may extend CR in 12-month steps for their own delays. Companion **Ordin 16/2026** amending licensing Ordin 6/2025: 30 EUR/kW guarantee for autorizație de înființare (all generation types) [FETCHED release; lege5 SNIPPET]. Press framing (Bolojan "ATR-uri care blochează rețeaua") [SNIPPET].

### 3.5 Household regulation
- Ordin ANRE 18/2022 (household users) — referenced on ANRE consumer page [FETCHED: https://anre.ro/consumatori/energie-electrica/cum-ma-racordez-la-retea/]. Not relevant to 50–150 MW.

### 3.6 Generation-capacity allocation methodology (for contrast)
- Ordin ANRE 53/2024 "Metodologia privind alocarea capacității rețelei electrice pentru racordarea locurilor de producere" (30 Jul 2024; legislatie.just.ro/Public/DetaliiDocumentAfis/286491 BLOCKED; lege5 partly FETCHED): Art. 1 scope ≥5 MW new production, power increases at production/consumption sites, production at existing consumption sites; Art. 7 OTS publishes by 15 Jan; Art. 5(1) 110 kV/MV; Art. 11(2) OTS finalises list of complete requests. **Not applicable to consumption-only sites.**

---

## 4. DSO hosting-capacity / free-capacity publications

### 4.1 Distribuție Energie Electrică România (DEER, Electrica group; 18 counties, zones TN/TS/MN)
- Producers page https://www.distributie-energie.ro/racordare-producatori-energie-electrica/ [FETCHED]. Files (all as of **30.06.2026**, XLSX, per zone MN/TN/TS), verified downloadable, e.g. https://www.distributie-energie.ro/wp-content/uploads/2026/07/Anexa-9.1_30.06.2026_TS_site.xlsx (219 KB), …Anexa-9.2_30.06.2026_TS_site.xlsx (5 MB), …Anexa-9.3_30.06.2026_TS_site.xlsx (24 KB); MN and TN equivalents. **Anexa 9.1 (Ord. 52/2021 format) columns:** Nr crt; Județul; Denumirea investitorului; Denumirea centralei; Adresa locului de producere și consum; Tipul sursei; Putere instalată (MW); Putere aprobată (MW); Capacitate stocare (Ah); **Stația de racordare** (named 110 kV station / MV feeder); Comentariu; Emitent; Număr ATR; Data emiterii ATR; Data expirării ATR; Număr CR; Data emiterii CR; Data expirării CR; Data estimată PIF. 9.2 = connection certificates (in operation), 9.3 = solution-study stage (per WebFetch). 2022 PDF version also online (31 pp) [FETCHED]. Updated at least semi-annually (file dates). **Generation only.** Also "Scheme de racordare la RED 110 kV" PDF (Nov 2024) and generator technical conditions. Portal: https://avize.distributie-energie.ro/. "Date de consum" page holds performance-indicator PDFs only, no consumption data [FETCHED]. No hosting-capacity map found.

### 4.2 Delgaz Grid (E.ON; 6 Moldova counties)
- "Harta de capacitate de înaltă tensiune" PDF https://delgaz.ro/getattachment/4dc42b63-6978-435a-bf7b-af2b6f9d1d93/Harta-de-capacitate-de-inalta-tensiune.pdf [FETCHED: 23.5 MB, **1 page, image only, created 31 Jan 2022**] — a 110 kV capacity map; legend not machine-readable; likely generation-oriented (not confirmed). Connection page https://delgaz.ro/energie-electrica/racordare-la-reteaua-de-energie-electrica [FETCHED]: MV maps per county, two variants each — **"Hartă Rețea MT Consum" and "Hartă Rețea MT Generare"** (PDF) — the only DSO product found that distinguishes consumption hosting capacity; page notes an access code is required. Also "Planul de dezvoltare a RED Delgaz Grid 2024-2033" (116 pp PDF, June 2023) [FETCHED] — 110 kV strategy text; no per-station headroom table found by grep.

### 4.3 Rețele Electrice România (ex E-Distribuție; PPC)
- Home page links /racordare/consumator, /racordare/producator, /racordare/dezvoltator, /racordare/spor-putere, /racordare/tarife [FETCHED home HTML]; /racordare/ page lists no capacity documents [FETCHED]; /racordare/producatori/ returned an image (404) [BLOCKED]. "Procedura din 2021 privind determinarea capacității disponibile" hosted PDF and a "capacitatea de racordare pentru fiecare zonă de rețea se actualizează conform Ordinului ANRE 137/2021" statement [SNIPPET]. No map/list verified. Search budget exhausted before a deeper check.

### 4.4 Distribuție Oltenia (Evryo; 7 counties)
- Site refused connections (ECONNREFUSED / empty curl) [BLOCKED]. From search: GIS page "Harta rețelei electrice DEO – consumatori de energie, dezvoltatori locali și autorități" (distance-to-network tool); "Actualizare avize tehnice de racordare" page; hosted copies of ANRE orders [SNIPPET]. No hosting-capacity publication verified.

### 4.5 Cross-cutting
- Under Ordin 137/2021 / 53/2024 and the Transelectrica procedure, DSOs supply 110 kV/MV data to the OTS and the OTS publishes zone capacities; DSO-level generation headroom therefore surfaces in Transelectrica's maps (zones A–J are 110 kV distribution zones). **No DSO publishes consumer hosting capacity at 110 kV in machine-readable form, as far as verified.**

---

## 5. Government / ministry / statistics datasets

- **energymap.ro** (initiative of Senator Antal Lóránt, Senate energy committee) [FETCHED: https://energymap.ro/en/]: interactive map of consumption (household/non-household) and production by **county and year (2021-2024 visible)**, installed capacity, prosumers, GDP correlation; sources stated as DSOs, industry associations, Transgaz, Transelectrica, ANRE; **no licence, no download** stated.
- **INS TEMPO-Online** (http://statistici.insse.ro/shop/index.jsp?page=tempo2&lang=ro&context=51) — JS application; a county-level electricity-consumption indicator was **not verified** in this session. INS monthly national releases exist (e.g. H1-2026 final consumption 24.1 TWh) [SNIPPET].
- **ANRE reports**: monthly electricity-market monitoring reports and annual reports at https://anre.ro/despre/rapoarte/ and arhiva.anre.ro [SNIPPET]; ANRE installed-capacity list (cited in PDRET as the source for 19,326.86 MW at 1 Jul 2025) — not fetched.
- **Industrial parks registry**: MDLPA page https://www.mdlpa.ro/pages/parcuriindustriale [BLOCKED: redirect loop]; legacy page http://www.dpfbl.mdrap.ro/parcuri_industriale.html [FETCHED] with files verified downloadable: situatia_parcurilor_industriale.xls (90 KB), distributia_pe_judete_a_parcurilor_industriale.xls (41 KB), harta_parcuri_pe_regiuni_2021.doc, coordonatele_pi.doc, Legea 186/2013, Ordin 2980/2013 (cell contents not parsed — no xlrd; vintage appears 2021). MDLPA: 100 titled parks (3,383 ha) as of Oct 2021 [SNIPPET]; APITSIAR association list [SNIPPET]. Supports: park identity/county; cannot support: power availability.
- **Energy strategy**: HG 1491/2024 (21 Nov 2024) "Strategia Energetică a României 2025-2035, cu perspectiva 2050", PDF on energie.gov.ro [SNIPPET].
- **Coal closures (CE Oltenia, CET Govora, Paroșeni/Mintia history)**: OUG 108/2022 decarbonisation law; renegotiated PNRR calendar — Rovinari 6 and Turceni 4 (plus a Govora unit; 710 MW) to cease commercial operation by **31 Aug 2026**; Rovinari 4, 5 and Turceni 5 (310 MW each) allowed to 2030; OUG 20/2026 (March 2026) reaffirming PNRR commitments; Chamber of Deputies on 5 Aug 2026 adopted an amendment conditioning closures on replacement low-carbon capacity being in commercial operation; government seeking further deferral from the Commission (May–Jul 2026) — **all [SNIPPET]**, not verified against legislatie.just.ro. The PDRET 2026-2035 Annex 2 (ERAA 2024 adequacy) and Annex C embed Transelectrica's own closure assumptions [FETCHED existence].
- **New generation/storage**: Transelectrica press (Aug 2026): >2,500 MW connected in 2026 (PV 1,331; storage 663; wind 496; gas 20; biogas 5), storage 989 MW at 1 Aug 2026, ~2,000 MW more expected incl. Mintia and Iernut CCGTs [SNIPPET]. Ministry of Energy PNRR/Modernisation Fund beneficiary lists — not searched (budget).
- **Interconnectors**: Black Sea Submarine Cable (Romania–Georgia HVDC, Topraisar–Anaklia; PMI list Dec 2025; Transelectrica–GSE MoU 4 Feb 2026; marine-survey preparation stage July 2026) [SNIPPET]; Moldova: LEA 400 kV Vulcănești–Chișinău completed Dec 2025, tested Jan 2026, commissioning announced for 27 Aug 2026; LEA 400 kV Bălți–Suceava contract signed, EBRD grant June 2026, expected 2027 [SNIPPET]. PDRET Annex F-4 lists interconnection projects with contribution to the 15 % target [FETCHED existence].

---

## 6. Data-centre / large-load announcements in Romania (list, no judgement)

No official register exists; the following is press-derived. Dates are publication dates.

| Date | Project | Location | MW (as stated) | Source | Status of fetch |
|---|---|---|---|---|---|
| Dec 2025 / 5 Jan 2026 | ClusterPower + Accelerated Infrastructure Capital equity partnership; MSC1 Mischii campus 3 phases RFS end-2026/2027/2028-29 (>500 MW), FRS1 Făurești (300 MW); "owned on-site substation, on-site gas trigeneration" | Dolj (Mischii) / Vâlcea (Făurești) | 800 total | DCD article (FETCHED, date not captured), baxtel news 2026-01-05, Structure Research 2026-01-07, ZF [SNIPPET] | partial |
| 20 Aug 2026 | WDP România + Lamas Invest, two data centres; requires **new 220 kV station at Ștefăneștii de Jos on LEA 220 kV Fundeni–Brazi Vest 1, target end-2030**; article also states ~100 MW operational nationally (industry estimate) and a Transelectrica forecast of 370–620 MW (2030) / 680–1,080 MW (2035) for data centres | Ștefăneștii de Jos, Ilfov | 2 × 190 = 380 | Profit.ro [FETCHED] | yes |
| 26–28 May 2026 (+ 12 Jun 2026) | DriverAI "Quantum AI" data centre, 4 × 20 MW phases, USD 1 bn first phase; in Leviatan Group industrial/technology park; partners E-INFRA, Carstens; announced by Senate President Abrudean | Luna, Cluj | 80 | DCD listing [FETCHED], Romania Insider [FETCHED], baxtel [FETCHED] | yes |
| undated (DCD) | "Sources say Microsoft to build its first data center in Romania" — land purchase in Otopeni reported by local media; rumour-level | Otopeni, Ilfov | not stated (aggregator sites claim 100 MW "planned" — unverified) | DCD [FETCHED page; date not extracted]; datacenterindex.ai [SNIPPET] | partial |
| 23 Mar 2026 | Sany International data centre plus two solar plants | Timișoara | not captured | DCD listing [FETCHED] | headline only |
| 8 May 2026 | Municipal data centre, developer Reșița Data Infrastructure; permits pending | Reșița | not captured | DCD [FETCHED page] | headline only |
| 24 Apr 2026 | Municipal data centre for NW Romania (Cluj-Napoca) | Cluj-Napoca | not captured | DCD [FETCHED page] | headline only |
| 4 Mar 2026 | Government Private Cloud operational: 4 STS data centres | Bucharest, Timiș, Brașov, Sibiu | not stated | Romania Insider [FETCHED] | yes |
| undated (older) | "Two data center developments totaling 45 MW" (Knight Frank via ZF); Knight Frank: ~100 MW potential | n/a | 45 | DCD [FETCHED page; date not extracted] | partial |
| ongoing | Existing operators: NXDATA-1/-2/-3 (Bucharest), GTS Telecom, M247, Infinite Chain Toplița (2 MW), ClusterPower Făurești (10 MW existing) — baxtel counts 15 facilities / 10 providers | various | see source | baxtel [FETCHED] | yes |
| market reports | Mordor: 93 MW (2026) → 232 MW (2031); EUDCA 2026 report; DataCenter Forum Romania 7 May 2026 ("initial project >100 MW", "12-month window") | national | — | [SNIPPET] | no |

Additional note: the government ATR list (§2.3) does not identify consumer ATRs, so it cannot be used to enumerate data-centre grid applications.

---

## 7. Gaps and what an ordinary company would have to request

- **Consumer-side available capacity per RET station is not published anywhere.** The only routes are: (i) Art. 10 information request to Transelectrica/DSO; (ii) a paid solution study (Art. 18); (iii) reconstruction from PDRET annexes B-1/B-3/B-4/G plus the generation-side zone maps.
- **Node-level generation data (Annex C-4) and CAPEX per project (F-1/F-2) are explicitly withheld**; costs surface only as aggregates or, for auctions, as "valoarea lucrărilor suplimentare" per zone.
- **No public queue/register for large loads**; DSO Anexa 9 files and the government ATR list are generation-only.
- **Consolidated law text**: legislatie.just.ro was unreachable here; article numbering above should be re-checked against MO 517 bis/2013 as amended by MO 501/2025 and MO 436/2026 before publication.
- **Not verified in this session** (search budget exhausted): INS TEMPO county indicator; Rețele Electrice and Distribuție Oltenia capacity pages; the exact content of the Transelectrica adequacy study; the legal text of the 2026 coal-calendar amendments; PNRR/Modernisation-Fund storage beneficiary lists; data.gov.ro holdings.

## 8. Local working copies (scratchpad, this session)

`pdret_2026_2035.pdf/.txt`, `referat_pdret_2026.pdf`, `proiect_decizie_pdret_2026.pdf`, `pdret_2024_2033.pdf`, `anexe_1_9_2024.pdf`, `anexe_A_H_2024.pdf`, `ret2026_note.pdf`, `tel_inv_2026_nota.pdf`, `procedura_alocare_2025.pdf`, `lista_atr_gov.pdf`, `harta_ret.pdf`, `delgaz_harta_IT.pdf`, `delgaz_plan_2024_2033.pdf`, `delgaz_ordin15_sinteza.pdf`, `deer_anexa9_2022.pdf`, `deer_a91/a92/a93_TS.xlsx`, `memoriu_vara_2026.pdf`, `reg59_deo_2024.pdf` (consolidated regulation printout 10 Oct 2024), MDLPA xls files. Note: the scratchpad was cleared once mid-session; only `reg59_deo_2024.*` was re-fetched afterwards — other files may need re-download from the URLs above.
