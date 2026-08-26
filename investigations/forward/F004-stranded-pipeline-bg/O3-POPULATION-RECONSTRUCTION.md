# F004 — Forcing observation O3: public reconstruction of the Bulgarian data-centre connection population

Run date: 2026-08-26. Status: COMPLETE. Budget: ~121 web searches, ~52 fetch/curl calls (budget cap 150 searches; stopped because the last ~30 searches yielded one new row).
Labels: [V] source fetched and read; [S] search-snippet only; [N] searched, not found.

## 0. Population rule (frozen, from task)
One row per project/entity with any public trace of a data-centre grid application / Naredba-6 connection opinion / declared investment intention in Bulgaria, against ESO's 3 Aug 2026 aggregate (9,330 MW total; 5,535 MW intentions; ~3,795 MW opinions).

## 1. The aggregate as ESO/press stated it (all verified)
| t_public | Source | Statement |
|---|---|---|
| 2026-05-26 | Mediapool, K. Georgiev (ESO CEO) interview [V curl] | "В ЕСО вече имаме искания за присъединяване и заявени инвестиционни намерения за дейта центрове с обща мощност от близо 9 хил. МВ, като за 3710 МВ има изготвени становища с условията за присъединяване към преносната мрежа. Най-крупните намерения са в Пловдив – 2610 МВ, във Варна – 1650 МВ, в Бургас – 1360 МВ, и в София – 920 МВ, но има намерения за такива центрове и в Монтана, Плевен, Русе, Горна Оряховица, Шумен, Стара Загора и в Софийска област." |
| 2026-06-29 | eurocom.bg [V curl] | Georgiev: 9,000 MW; "заявките за присъединяване са подадени от началото на годината"; "Инвеститорите търсят локации до големите градове с летища като София, Пловдив, Варна и Бургас." |
| 2026-07-08 | Capital interview with Georgiev [N — paywalled (tollbit/402); not read] | title only: "Имаме заявки за близо 9000 MW дейта центрове". |
| 2026-08-12 | economic.bg [V] | as of 3 Aug 2026: 9,330 MW; 5,535 MW intentions; 3,795 MW opinions under Naredba 6. Regional: Plovdiv 2,260; Burgas 1,860; Pleven 1,140; Montana 970; Sofia-city 920; Stara Zagora 510. |
| 2026-08-19 | Capital "Идва цунами от центрове за данни" [V curl] | ESO as of 10 May 2026: 8,980 MW; 5,270 intentions; 3,710 opinions. Varna+Burgas >3,000 MW; Montana >670 MW. Existing DC stock ~27–30 MW (Data Center Map). |

Note the two regional lists are not reconcilable as the same partition (May: Varna 1,650 / no Pleven figure; Aug: Pleven 1,140 / no Varna figure; Burgas jumps 1,360 → 1,860). Either the grouping basis changed (city vs. ESO grid region) or there is churn; neither source explains it. Kept as observation.

## 2. STRUCTURAL REASON FOR THE GAP (exact quotes)
- Capital 19 Aug 2026 [V]: "Изпълнителният директор на ЕСО Кирил Георгиев посочва, че всички заявки идват от български компании, но имената им не са публични."
- ESO publishes registers for RES-generator connection applications and temporary-access objects (24chasa/BPVA on the RES e-register), but **no public register of consumer (load) connection requests or Naredba-6 opinions** exists. No KEVR document, no parliamentary question/answer, no ESO press release naming any data-centre applicant was found [N].
- BFIEC's Ivaylo Naydenov (economic.bg EN, 28 Oct 2025) [V]: "we do not know, at least publicly, what consumer capacity we are talking about".
Consequence: the population is only reconstructible where an applicant *chose* to go public (MoU, press, municipal land request). The 9.33 GW is an ESO-internal count.

## 3. Applicant-type characterisations (exact quotes, with source)
- Georgiev/ESO, Capital 19 Aug 2026 [V]: "Част от заявителите според Георгиев водят разговори с големи международни корпорации. Българските инвеститори искат първо да си осигурят достъп до електропреносната мрежа, тъй като получаването на положително становище увеличава стойността на проекта и позволява той да бъде продаден на стратегически инвеститор." — "Ако един инвеститор резервира 300 MW днес, конкурентът му може след година вече да няма откъде да се присъедини. Това създава стимул заявленията да бъдат за по-големи мощности от реално необходимите." — "И не - капацитет за присъединяването на всички тях няма."
- Mediapool 24 Jul 2026 [V curl]: "По данни на Mediapool сред резервиралите капацитет от мрежата инвеститори в дейта центрове има фирми с капитал от 1 евро, такива за преработка на маслодайни суровини и свързвани с фирми, които се занимават с изграждане на ВЕИ и батерии." Kamen Georgiev (CEO Novatel): "Тези заявки за присъединяване от 9000 МВ, дори само одобрените от близо 4000 МВ, са нереални не само за България, но и за Югоизточна Европа"; the sum "потвърждава съмненията за спекулативно задържане на капацитет от мрежата и опити на собственици на терени в близост до подстанции на ЕСО да осребрят имотите си от бъдещи наистина сериозни инвеститори". He proposes screening by requiring dual-substation connection.
- Mediapool 4 Aug 2026 (K. Georgiev) [V]: example of a small landowner with a €2-capital company; "въпросният предприемач може без никакъв реален инвестиционен интерес отзад да запази огромен капацитет".
- Nikola Gazdov (APSTE chair), Investor.bg 29 Jul 2026 [V]: "поне половината от тях са реални проекти".
- 24may.bg 5 Aug 2026 (Vihra Pavlova) [V]: attributes to ESO chief "тези обеми са нереални и опасни за енергийната ни мрежа" (secondary; not found verbatim in a primary interview).
- Delyan Dobrev (then MP), Oct 2025 [V a-specto]: "Има инвеститор, който обикаля страната и търси земя за инсталиране на дейта център с възможност за консумация на електроенергия между 100 и 600-700 МВтч" — wants direct NPP/NEK supply at €65/MWh.
- Naredba-6 process (economic.bg 12 Aug [V]): ESO does not sign preliminary contracts with these applicants; it issues opinions valid one year.

## 4. Reconstructed rows
Columns: project | legal entity (registry facts) | MW claimed | region / site / substation | grid stage | land | permits | disclosed partner/capital | source | t_public | label

**R1. "Проект Титан" / Brinell Compute AI factory** | Brinell Compute GmbH, Munich, registered Sep 2025, capital €25,000, MD Tilo Marcel Braun, shareholders Brinell Group + Gordias Capital GmbH (Philipp Merk), equal stakes; Bulgarian entity: not reported as established (Feb 2026) | **MW not disclosed** (24may.bg: "заявената крайна мощност... е съпоставима с производството на цял един блок на АЕЦ „Козлодуй"" ≈ 1,000 MW — interpretation, not company statement; DCD/DataCentral: "No public MW figure, grid agreement, customer, financing package") | Plovdiv region; Industrial Park "Стряма" / Industrial Zone "Раковски" (Trakia Economic Zone), Rakovski + Maritsa municipalities; nearest ESO substation "Раковски" 110/20 kV (inferred from geography, not stated) | grid stage: **not stated**; press claims "discussions with large US technology companies" | land: 245 dka at "Назарица 1", Strama village (phase 1 ~200 dka plant + ~200 dka energy); total 2,000 dka; zone land historically municipal → Sienit (815 dka tender) — ownership of Brinell's plot not disclosed | permits: none reported; Rakovski council minutes of 23 Dec 2025 contain nothing on the project [V pdf]; Class A certificate "expected by end of August 2026" (plovdiv24 22 Jul) — not found issued as of 26 Aug [N] | Government MoU: CoM decision №59/2026, signed 21–22 Jan 2026 by T. Donchev; €3bn; groundbreaking "this autumn" (DCD 30 Jul) | podtepeto 3 Feb 2026; Mediapool Jan 2026; plovdiv24/marica/standart 21–22 Jul 2026; DCD 30 Jul; DataCentral 31 Jul | 2026-01-21 → | [V]

**R2. Campus Tenevo (AI data-centre park, Okop/Tenevo)** | „Кампус Тенево" ЕООД, Sofia; sole owner Renalfa AD (EIK 204399851, est. 9 Jan 2017, capital €51,000 per papagal snippet); Ivo Prokopiev named as principal shareholder of parent by the company's manager Dimo Petrov; EIK/capital of the EOOD not obtained (papagal blocked) | MW not disclosed; €100m; ~50 jobs | Yambol district, Tundzha municipality; plots at "Парцелите-2" (Okop, 179,204 m²) and "Адата" (Tenevo, 9,007 m²), adjacent to Tenevo Solar Park (Renalfa/Eurowind JV: 238 MW PV + 315 MW/760 MWh BESS + 250 MW wind) | grid: "an additional substation next to the existing one at the solar park"; will not use the village grid — implies behind-the-meter/own connection; ESO opinion not mentioned | land: municipal; council preliminary consent to sell without tender under the Investment Promotion Act, 28 May 2026 (24-month validity, conditional on class-A/priority certificate); **revoked unanimously 19 Jun 2026** after residents' meeting 11 Jun | permits: none; EIA: nothing on RIOSV Stara Zagora [N] | partner: none disclosed | BTA regional 11 Jun 2026; yambolnews 28 May, 11 Jun, 19 Jun 2026 | 2026-05-28 | [V]
This is the only fully identified case of the "RES/BESS developer re-purposing a site" pattern.

**R3. Delyan Dobrev / Rumen Radev / Nikolay Pavlov — "дейта център с голям капацитет"** | two unnamed companies, Dobrev executive director; boards include former energy ministers Rumen Radev and Nikolay Pavlov; names withheld "заради подписани споразумения за конфиденциалност" | MW not stated ("голям капацитет"); paired with a large BESS project | location not stated | grid stage not stated | land not stated | partners: "едни от най-големите американски компании в секторите на информационните технологии и енергетиката", unnamed; "изцяло на пазарен принцип и на собствен риск" | Mediapool, Dnevnik, Actualno, boulevardbulgaria, 27 Jul 2026 | 2026-07-27 | [V]

**R4. Schwarz Digits (Schwarz Group / STACKIT)** | Шварц Диджитс България ЕООД, EIK 205158327 (Sofia, Hladilnika) — registry details not obtained | MW not disclosed | location not disclosed | grid stage not stated | none | Government MoU (one of three; "най-напреднали бяха преговорите със Schwarz Digits" — Donchev, 12 May 2026); BTA (Iotova meeting, 2026): "планира създаването на голям център за данни" | BTA 12 May 2026; dbr.bg; economy.bg | 2026-05-12 | [V/S]

**R5. Unnamed "много голяма американска компания"** | — | — | — | MoU per Donchev 12 May 2026; "два от трите проекта са реалистични за изпълнение" | — | BTA 12 May 2026 | [V]

**R6. Helios Power — "технологичен център за данни", Targovishte Industrial Park** | „Хелиос Пауър" ООД, EIK 200972175 (registry details not obtained); park owners Dimitar Popov, Petar Gospodinov | MW not disclosed; park grid: existing ESO opinion №ЦУ-ЕСО12098#3/14.11.2023 for the park; planned 110 kV line from substation "Търговище 2" to new 110/20 kV 80 MVA park substation [V concept PDF, mi.government.bg] | Targovishte | grid: park-level, not DC-specific | private park (€17.7m) | — | Capital 19 Jun 2026 (industrial parks) [S; article body paywalled] | [S]

**R7. IBM AI gigafactory (Sofia)** | none | ≥70 MW initial, up to 500 MW; 50–200 ha | Sofia (unspecified) | no application reported | — | announced by PM Zhelyazkov Oct 2025; Mediapool 24 Jul 2026: "Оттогава обаче нищо не е споменавано за развитието на намерението" | [V]

**R8. Meta — AI gigafactory near Kozloduy** | none | ~1,000 MW (paragraf.bg); up to 1,500 MW for an InvestAI gigafactory (economic.bg) | Kozloduy NPP area | no ESO application mentioned; economic.bg: Meta representatives said investment only possible after 2028, excluding InvestAI | — | PM meeting with Joel Kaplan 25 Sep 2025 | [V]

**R9. State-sponsored DC sites at Kozloduy NPP** | АЕЦ Козлодуй – Нови мощности ЕАД (state) as host, no investor | 200–250 MW on the nearer site (Stankov, May 2025); ministry: two DCs, ~€3bn each, 3–5 yrs | Kozloduy | concept only | state land | — | bTV 16 May 2025; economic.bg 4 Jun 2025; ME 20 Jul 2025 (Washington: CEBA, IP3, Phillips 66, BCIU) | [V]

**R10. BRAIN++ / Discoverer++ (EuroHPC AI factory)** | Sofia Tech Park + INSAIT | MW not disclosed; €90m | Sofia Tech Park | existing site | — | EU/EuroHPC | 2025 | [V] — small; not a 9-GW-class applicant.

**R11. Digital Realty / Telepoint** | Telepoint (acquired 2 Mar 2026) | existing 14.8 MW across 2 Sofia + 1 Montana sites; Sofia East 9 MW | no expansion MW disclosed | — | Capital 12 Mar & 19 Aug 2026; PR 2 Mar 2026 | [V]

**R12. Incumbents with no disclosed new application**: Equinix SO1/SO2 (700 racks, no MW), Neterra (5.13 MW; Stolnik, Ruse), S3 Company (2 MW), A1, Vivacom, Evolink, Daticum — none has a public 2026 transmission-level application [N].

**R13. Land-market trace (not an applicant)**: prodavambiznes.bg listing 16 Jul 2026, 135 dka near Varna "подходящ за Батерии с ФЕЦ и Дата център", 2.5 km from a 110 kV substation, approved cable-route parcel plan; **no ESO opinion or MW claimed** [V]. Included only as evidence of the "land near substation" pattern.

**R14. Kardesa landing station, Ahelой (Novatel / Vodafone / NEQSOL)** | Novatel (Magyar Telekom/Deutsche Telekom) | not a DC load | Burgas region | — | — | — | Capital 28 Jan 2026 | [V] — context for Burgas/Varna interest, not an applicant.

**R15. Radomir–Niš "cross-border digital hub"** — mentioned only in 24may.bg 5 Aug 2026; no independent trace found [N].

## 5. Coverage arithmetic (honest)
- Rows with a **stated MW** that could sit in ESO's count: none with a company-stated figure. Press-inferred: Brinell ~1,000 MW (interpretive), Meta ~1,000–1,500 MW (no application), IBM ≤500 MW (dormant), Kozloduy state sites 200–250 MW (no investor).
- Rows with identified legal entity + site + municipal act: **1** (Campus Tenevo, MW undisclosed, ~€100m ⇒ likely tens of MW at press-cited €10m/MW for shell — inference only).
- Rows with government MoU: 3 (Brinell, Schwarz Digits, unnamed US).
- **Share of the 3,795 MW of opinions attributable to a named applicant: 0 MW confirmed.** No source links any named company to an issued Naredba-6 opinion. Share of the 9,330 MW attributable to named applicants even by generous inference: ≤ ~1.5 GW (Brinell + Tenevo + Dobrev + Schwarz, all MW-undisclosed) — i.e. **≥ ~85% of the population is publicly untraceable**, and 100% of the opinion-stage MW is.
- Geographic sanity: Plovdiv 2,260–2,610 MW has one named project (Brinell). Burgas 1,360–1,860, Varna 1,650, Pleven 1,140, Montana 670–970, Stara Zagora 510, Sofia 920 MW: **zero named applicants** despite city-by-city, municipality-by-municipality and RIOSV-by-RIOSV searches.

## 6. Negative searches (preserved)
- Municipal ПУП/ПРЗ decisions "център за данни"/"дейта център" 2026: only Tundzha (Okop/Tenevo). Sofia (СОС), Plovdiv, Maritsa, Kuklen, Saedinenie, Rakovski (Dec-2025 minutes read in full), Burgas council, Pleven council, Montana council, Varna/Devnya/Aksakovo/Beloslav, Pomorie/Kameno/Aytos/Karnobat/Sozopol, Kozloduy/Hayredin/Oryahovo/Valchedram, Belene/Svishtov/Nikopol/Gulyantsi, Radnevo/Galabovo: [N].
- RIOSV first-notification pages scraped and grepped (Plovdiv, Varna, Pleven, Montana, Sofia-region 2026 list, Burgas, MOEW national list): 0 data-centre notices [N]. RIOSV Stara Zagora (covers Yambol) for Okop: only an unrelated construction-waste notice [N].
- БАИ class A/B certificates for data centres 2026: none issued/publicised [N] (Brinell "expected end Aug"; Tenevo applied, consent revoked).
- ESO site, KEVR decisions 2026, parliamentary energy committee, parliamentary questions: no applicant-level data [N].
- ESO "temporary access" register: exists for generation/BESS objects, no DC entries found [N].
- Companies register: papagal.bg returned Cloudflare 403 to both WebFetch and curl; brra.bg is interactive-only. Registry facts for Campus Tenevo EOOD, Helios Power OOD, Schwarz Digits Bulgaria EOOD **not obtained** [N]. Only Brinell GmbH (Munich) facts are press-verified.
- Named RES/BESS developers (Rezolv, Enery, Sunterra, Solarpro, Eurohold, Electrohold) + "дейта център": no DC announcements [N] — despite Mediapool's claim that such firms are among opinion-holders.
- Foreign-nationality investor searches (Greek/Turkish/Israeli/Chinese/Gulf): [N].
- LinkedIn/English trade press: only Brinell (DCD, DataCentral, BeBeez, IDCNova) [V]; datacentermap Brinell entry 429.
- Yettel/CETIN, A1–Renalfa PPAs: supply contracts for existing DCs, not new applications.

## 7. Method notes / caveats
- Capital and Dnevnik are paywalled via tollbit; the 19 Aug Capital article was retrievable with a browser UA, the 8 Jul ESO interview was not (402). Its content may contain further ESO process detail (deposits, one-year expiry, selection principle) not captured here.
- Two regional partitions (May vs Aug) are reported by different outlets; treat MW-by-city as press transcription of ESO briefings, not an ESO publication.
- No project was judged; MW figures marked "interpretation" are press inferences, not company disclosures.
