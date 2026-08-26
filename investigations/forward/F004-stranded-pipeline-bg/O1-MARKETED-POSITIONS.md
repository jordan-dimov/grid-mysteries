# F004 — Forcing observation O1 (run 2026-08-26) — FINAL

**Question (frozen):** Are Bulgarian sites/projects holding an ESO connection opinion ("становище от ЕСО") or other early grid position for a DATA CENTRE being offered for sale/JV — and do any transact? **Falsifier F-A:** has any DC developer/hyperscaler acquired or contracted a Bulgarian site at >=50 MW?

**Budget used:** ~84 web searches (BG + EN), ~40 page fetches (WebFetch + curl). Stopped because the last three waves returned only the same cluster of sources. Labels: [V] fetched and read; [S] snippet only; [N] searched, not found.

**Headline (observation only):**
1. No Bulgarian site/SPV is found publicly advertised as "data centre + ESO opinion for X MW" for sale or JV. Two sites are marketed with DC framing but neither claims an ESO DC opinion (A1, A2). One regional-chamber article records an unnamed investor's interest in a fragmented site next to an ESO substation (A3).
2. The TSO's chief executive states on the record (capital.bg, 2026-08-19) that Bulgarian applicants seek ESO opinions first because a positive opinion "increases the project's value and allows it to be sold to a strategic investor" — but names no applicant, listing or transaction (A4).
3. No transaction of a DC-opinion-holding site/SPV is evidenced [N].
4. F-A: NOT falsified. Largest evidenced acquisitions/contracts: Digital Realty–Telepoint 14.8 MW operating (+ adjacent land "up to 14 MW"); Top Systems Burgas 2 MW; Brinell Compute has a government MoU and a stated site but no evidenced land purchase/lease, MW, ESO opinion/contract or permit. Schwarz Digits and the "US company" are MoU/negotiation only.

---

## A. Offers for sale / JV of DC-positioned sites in Bulgaria

### A1. prodavambiznes.bg — 135 dka parcel, Varna region, "for batteries, FEC and data centre" [V]
- Offered: 135 dka private UPI; PUP "за електроенергийно производство"; approved parcel plan for cable route along municipal roads to a 110 kV substation 2.5 km away; optical fibre parallel to plot. "изключително подходящ за Батерии + Дата център + ФЕЦ ... сигурна, постоянна и непрекъсваема мощност при висока консумация".
- MW: none stated. Stage: no ESO opinion / preliminary contract / contract claimed — only PUP + cable parcel plan. Region: Varna (NE Bulgaria).
- Terms: €35/m² (≈€4.7m). t_public 2026-07-16 11:29; seller "Stefan" (private; account registered same day; tel 0888375250). Same seller also lists an operating 11.4 MW PV plant and a 60 dka industrial plot.
- URL: https://www.prodavambiznes.bg/продавам-голям-парцел-135-дка-подходящ-за-батерии-с-фец-и-дата-център-393
- Note: DC is one of three suggested uses; the core asset is an energy-production PUP. Not a DC project with an ESO DC opinion.

### A2. "Project Provadia" (projectprovadia.com) — 129.65 ha, Provadia (30 km from Varna) [V]
- Offered: "ready-to-build" RES site: 100 MW AC / 107.8 MWp PV, "100 MW bidirectional" grid interconnection to a "newly refurbished TSO substation" (33/110 kV), 400 kV corridor ~2 km, CCGT backup, Kardesa 500 Tbps fibre passing through the plot (via Bulgartransgaz pipe route). Marketed as real estate for "next-generation, AI-ready data centers" with behind-the-meter hourly-matched PPA; "+70 ha adjacent land available".
- Stage: claims "grid connection" and CPPAs; no ESO opinion number, no DC connection opinion stated; "JV with a strategic investor (EPC contractor) in place". Seeking equity €16.4m of €65.7m; IRR 31.83%; COD "January 2026" (page stale). No offeror name; contact Sofia, Vitosha 39, +359899235777.
- Transaction/buyer: none announced [N]. Bulgarian-language press coverage of this project: none found [N].
- URL: https://projectprovadia.com/
- Note: a RES/BESS project with DC narrative bolted on; the 100 MW grid position is a generator/bidirectional claim, not a DC-load opinion.

### A3. Former ATZ site, Stara Zagora — 1,000+ dka, chambersz.com 2026-05-26 [V]
- "Наскоро инвеститор прояви интерес за изграждане на Дейта център" attracted by "обширното пространство и наличието на подстанция с голяма мощност" owned by ESO on-site. Investor unnamed; MW not stated; stage: interest only.
- Ownership fragmented (~100 owners); DBank holds most and has announced sale of >200 dka; land €20–40/m²; municipality-led infra (new 110/20 kV substation from OHL "Феникс", €13.66m JTF grant) to complete by Feb 2028. Site offered for sale, not as a DC SPV.
- URL: https://chambersz.com/2026/05/26/1000-dekara-ot-bivsheto-atz-kraj-stara-zagora-sa-novata-nadezhda-za-moderna-industrialna-zona/
- Note: ESO figures show Stara Zagora region at 510 MW of DC applications (economic.bg 2026-08-12); no link to a specific applicant is public.

### A4. TSO statement that opinions are sought for resale — capital.bg 2026-08-19 "Идва цунами от центрове за данни" [V via curl; paywalled to WebFetch; body saved capital_body.txt]
- ESO figures as of 2026-05-10: 8,980 MW requests, of which 5,270 MW investment intentions and 3,710 MW with Наредба 6 opinions issued. Installed DC ≈30 MW.
- Kiril Georgiev (ESO exec. director), verbatim: "всички заявки идват от български компании, но имената им не са публични. ... И не – капацитет за присъединяването на всички тях няма."
- Author's paraphrase of Georgiev: "Част от заявителите ... водят разговори с големи международни корпорации. Българските инвеститори искат първо да си осигурят достъп до електропреносната мрежа, тъй като получаването на положително становище увеличава стойността на проекта и позволява той да бъде продаден на стратегически инвеститор."
- Georgiev, verbatim: "Ако един инвеститор резервира 300 MW днес, конкурентът му може след година вече да няма откъде да се присъедини. Това създава стимул заявленията да бъдат за по-големи мощности от реално необходимите."
- Also names: Telepoint 3 sites (2 Sofia + Montana) 14.8 MW, Sofia East 9 MW; Neterra 4 sites 5.13 MW; S3 2 MW; Equinix (no MW disclosed; SO2 doubled to 700 racks in 2023).
- URL: https://www.capital.bg/biznes/tehnologii_i_nauka/2026/08/18/4935484_idva_cunami_ot_centrove_za_danni/ (t_public 2026-08-19 08:00)

### A5. Speculation reported, no listing — mediapool.bg 2026-07-24 [V]
- Kamen Georgiev (Novatel): 9,000 MW applied / ~4,000 MW approved "unrealistic ... for Southeast Europe"; article: suspicions of "спекулативно задържане на капацитет от мрежата и опити на собственици на терени в близост до подстанции на ЕСО да осребрят имотите си от бъдещи инвеститори"; applicants include €1-capital firms, oil-seed processors, RES/BESS-linked companies.
- URL: https://www.mediapool.bg/treskata-za-deita-tsentrove-spekulatsii-ili-realni-proekti-news385791.html

### A6. ESO aggregate figures, later vintages [V]
- economic.bg 2026-08-12 (ESO as of 2026-08-03): 9,330 MW total; 5,535 MW intentions; 3,795 MW with opinions. Regional: Plovdiv 2,260; Burgas 1,860; Pleven 1,140; Montana 970; Sofia-city 920; Stara Zagora 510. ESO: opinions valid one year; how many are realised "depends on investor behaviour". No names. URL: https://www.economic.bg/bg/a/view/zajavkite-za-dejta-centrove-v-bylgarija-na-hartija-nadhvyrljat-9-gw
- mediapool 2026-05-26 (end-May): ~9,000 MW; 3,710 MW with opinions; Plovdiv 2,610; Varna 1,650; Burgas 1,360; Sofia 920; also Montana, Pleven, Ruse, G. Oryahovitsa, Shumen, Stara Zagora, Sofia region. No resale statement in this piece. URL: https://www.mediapool.bg/sled-buma-na-vei-i-baterii-se-zadava-tozi-na-deita-tsentrove-news383484.html
- eurocom.bg 2026-06-29 [V via curl]: Georgiev: "2024-а беше годината на фотоволтаиците, 2025 г. е на батериите, а 2026-а ще е на дейта центровете"; applications since start of 2026; investors seek sites near Sofia/Plovdiv/Varna/Burgas; transformer capacity 12,000 MW vs 11,500 MW RES+BESS. No resale statement. URL: https://eurocom.bg/2026/06/29/eso-zayavkite-za-deyta-tsentrove-u-nas-sa-s-moshtnost-na-chetiri-aec-a/
- Naredba 6 (2024) [S]: opinion valid 1 year; preliminary contract valid 2 years; procedure terminated if no contract procedure begun within those windows. (Transferability of an opinion with the site/SPV not checked in the regulation text — open item.)
- capital.bg ESO interview 2026-07-08 "Имаме заявки за близо 9000 MW дейта центрове": NOT retrievable (403 / Cloudflare JS challenge). Unread.
- investor.bg 2026-07-29 (Nikola Gazdov, APSTE) [V]: ~9,000 MW inquiries, "at least half genuine"; no sites, no resale statement.
- 24may.bg 2026-08-05 [V]: lists AI Factory Plovdiv (2,000 dka; 200 dka halls + 200 dka energy), BRAIN++ (Sofia Tech Park, €90m), Kardesa, "Cross-Border Digital Hub Radomir–Niš", Schwarz Digits; no sites for sale.

### A7. Portals/brokers/marketplaces checked
- alo.bg / imot.bg / olx.bg / bazar.bg / bulgarianproperties.com: DC-specific listing with ESO opinion [N]. alo.bg "становище" hits are PV-opinion parcels only. imot.bg: generic parcels "with trafopost" / "900 ha near substation" (not DC-framed) [S]. bulgarianproperties.com: Stara Zagora plot with "design visa for 1500 MW PV" 170 m from city substation — PV, not DC [S].
- Colliers BG, Cushman & Wakefield Forton, MBL, Arco: no DC land/site listing [N].
- Power Loop (power-loop.eu, /bulgaria/) [V]: generic "up to 500 MW", "fully permitted land", no site, MW, location or dates disclosed.
- pfnexus.com: Bulgarian BESS SPVs only (430 MWh w/ grid contract; 50 MW/200 MWh w/ ESO statement); no DC project [N].
- LinkedIn (via web search): no post offering a BG DC site with ESO opinion [N]; one profile-post noting the 9 GW is "interest, not real projects" [S].
- Trakia Economic Zone, NCIZ, Sofia Tech Park, Mini Maritsa-Iztok: no DC plot offer [N]. NCIZ builds an EU "digital hub" (not a DC site sale) [S].
- Kozloduy/Belene "DC" offers: government statements only (Stankov 2025-05-16: 200–250 MW, €3bn, 3–5 yrs, "in talks with potential investors", none named [V bTV]); Dobrev 2025-10-02: unnamed investor "обикаля страната и търси земя" for a DC of 100–700 MW(h), wants €65/MWh from NEK/Kozloduy [V svobodnoslovo]. No site transaction.

## B. Comparator — Resita Data Infrastructure (RO) [V + DCD S]
- Offer: majority equity in SRL (CUI 54450187) holding a 49-yr municipal concession (~3 ha, scalable to 31 ha) adjacent to Transelectrica 400/220/110 kV node (commissioned Nov 2024); alt. tripartite JV with municipality. Phase 1 50–100 MW indicative; Studiu de Soluție Nr. 29067 registered 2026-05-29; ATR pending (6–12 months); HCL vote pending Q3 2026. Terms only in VDR under NDA. Strategic partnership with Municipality 2026-03-27; land allocation initiated Apr 2026; DCD coverage May 2026 ("partners actively sought").
- Buyer/JV since April 2026: NONE announced [N]. Page "Live Project Status" last entry 2026-05-29; no July/August news found.
- URL: https://www.resitadata.com/ ; DCD: https://www.datacenterdynamics.com/en/news/plans-announced-for-municipal-data-center-in-reșița-romania/

## C. Falsifier F-A — DC developer/hyperscaler acquisition or contract at >=50 MW

| Item | MW | Stage | Site acquired/contracted? | Date | Label |
|---|---|---|---|---|---|
| Digital Realty – Telepoint (Sofia ×2 + Montana) | 14.8 MW operating; adjacent Sofia land "up to 14 MW IT" | Acquisition closed, €66.5m | Yes (operating assets + adjacent parcel) | 2026-03-02 | [V globenewswire snippet; IR page 403] |
| Brinell Compute – Rakovski IZ / Stryama (Maritsa & Rakovski municipalities) | none disclosed | Gov't MoU 2026-01-21; "final stage of site selection"; press: first phase 200 dka halls + 200 dka energy, final 2,000 dka (marica.bg 2026-07-20); groundbreaking "this autumn" (DCD/bebeez 2026-07-30) | NOT evidenced: no land purchase/lease, no ESO opinion/contract, no permit, no customer, no financing, no contractor (DataCentral 2026-07-31). Company itself has not commented. Company registered Munich Sep 2025, €25k capital. | 2026-01 → 2026-07 | [V BTA, marica.bg, bebeez, DataCentral] |
| Schwarz Digits | none | MoU ("most advanced" of three) | No | 2026-05-12 | [V BTA] |
| Unnamed "major German company"; unnamed "very large American company" | none | Negotiations | No | 2026-05-12 | [V BTA/dbr.bg] |
| Equinix Sofia | undisclosed (SO2 700 racks after 2023 phase 2) | No 2026 expansion/new site found | No | — | [S] |
| Neterra SDC-2 | 2 MW | Operating | n/a | — | [S] |
| Top Systems Burgas ("BOJ") | 2 MW | Land 10,000 m² bought 2020; permit 2023; completion 2026; "in front of 400/110 kV substation" | Yes, 2 MW | 2020–2026 | [V] |
| BRAIN++ AI Factory, Sofia Tech Park | none disclosed | EuroHPC, €90m | No new site | 2026 | [S] |
| Kozloduy / Belene DC | 200–250 MW (minister's figure) | Government idea; investors unnamed | No | 2025-05-16; 2026-05-12 | [V] |
| Blue Bird Energy / SGE SMR LoI | n/a (generation) | LoI 2025-12-22 | No | 2025-12-22 | [S] |
| Hyperscaler (MS/Google/AWS/Meta/Oracle) BG land purchase | — | — | None found | — | [N] |

Observed unit discrepancy (record, do not resolve): Bulgarian sources say Brinell final phase = "2000 декара" (=200 ha); DCD/DataCentral/bebeez render "2,000 acres (809 hectares)". BAI investmap lists Rakovski IZ at 1,050,000 m² total / 300,000 m² free (bcci.bg: 815,000 m²); marica.bg says the project is an *expansion* of the zone via a SPUP across Rakovski and Maritsa municipalities.

**F-A verdict:** not triggered. No DC developer or hyperscaler is evidenced to have acquired or contracted a Bulgarian site at >=50 MW as of 2026-08-26.

## D. Explicit negative results
- "парцел становище ЕСО дейта център продава"; "продава дружество проект дата център становище ЕСО"; "терен за дейта център продава MW присъединяване"; "дейта център терен становище ЕСО продава/търси партньор/търси инвеститор 2026": no DC-opinion listing [N] (only A1 via a different query).
- "powered land Bulgaria for sale MW"; "Bulgaria data center site grid opinion/connection opinion for sale"; "Bulgaria data center SPV project rights for sale"; "ready-to-build/shovel-ready Bulgaria data center site": nothing beyond Power Loop generic page and Project Provadia [N].
- Regional probes — Varna 1,650 MW, Burgas 1,860/1,360 MW, Pleven 1,140 MW, Montana 970 MW, Plovdiv 2,610 MW, Ruse/G. Oryahovitsa, TPP Varna, Bobov Dol, Maritsa-Iztok: no named applicant, site or listing [N].
- Brinell land purchase / municipal council decision / ESO contract: [N].
- Schwarz Digits DC location/MW: [N] (economy.bg article 403).
- Digital Realty second Sofia site/new campus: [N]. Equinix SO3: [N].
- Radomir–Niš cross-border hub: only the 24may.bg mention; no MW/investor [N].
- Resita buyer/JV after April 2026: [N].
- capital.bg ESO interview 2026-07-08: unretrievable (403/Cloudflare) — potential additional ESO statements unread.

## E. Source list (fetched [V])
- https://www.capital.bg/biznes/tehnologii_i_nauka/2026/08/18/4935484_idva_cunami_ot_centrove_za_danni/ (curl; saved capital_body.txt)
- https://www.mediapool.bg/treskata-za-deita-tsentrove-spekulatsii-ili-realni-proekti-news385791.html
- https://www.mediapool.bg/sled-buma-na-vei-i-baterii-se-zadava-tozi-na-deita-tsentrove-news383484.html
- https://www.economic.bg/bg/a/view/zajavkite-za-dejta-centrove-v-bylgarija-na-hartija-nadhvyrljat-9-gw
- https://www.economic.bg/bg/a/view/dyrjavata-razglejda-marishkija-basejn-kato-mjasto-za-dejta-centrove
- https://www.economic.bg/en/a/view/german-company-may-build-3-billion-ai-factory-near-plovdiv
- https://eurocom.bg/2026/06/29/eso-zayavkite-za-deyta-tsentrove-u-nas-sa-s-moshtnost-na-chetiri-aec-a/ (curl; saved eurocom.html)
- https://24may.bg/2026/08/05/... (Дигитална експанзия и инфраструктурен канибализъм)
- https://www.investor.bg/a/566-novini-i-analizi/434293-...
- https://www.prodavambiznes.bg/...-135-дка-...-393
- https://projectprovadia.com/
- https://chambersz.com/2026/05/26/1000-dekara-ot-bivsheto-atz-kraj-stara-zagora-...
- https://www.bta.bg/en/news/economy/1124611-... and https://www.bta.bg/bg/news/economy/1124599-...
- https://www.bta.bg/en/news/1048042-cabinet-approves-memorandum-with-german-company-for-digital-infrastructure
- https://dbr.bg/balgaria-stroi-tri-novi-deita-centara-s-nemski-i-statski-kompanii~22454.html
- https://www.marica.bg/biznes-zona/startirat-fabrika-za-izkustven-intelekt-do-plovdiv (curl)
- https://bebeez.eu/2026/07/30/brinell-compute-prepares-for-construction-of-ai-data-center-in-maritsa-bulgaria/
- https://data-central.co.uk/bulgarias-e3bn-ai-campus-reaches-the-starting-line/
- https://investmap.government.bg/bg/publications/181 (curl)
- https://btvnovinite.bg/bulgaria/stari-moshtnosti-s-nova-rolja-...
- https://svobodnoslovo.eu/bulgaria/investitor-iska-700-mvtch-ot-aec-kozloduy-...
- https://topsystems.bg/datacenterburgas/
- https://power-loop.eu/data-centers-in-europe/ ; https://power-loop.eu/bulgaria/
- https://www.resitadata.com/
Failed fetches: investor.digitalrealty.com (403), globenewswire DLR (timeout), datacenterdynamics.com (timeout/403), economy.bg (403), capital.bg podcast + ESO interview (403/Cloudflare), web.archive.org (blocked).
