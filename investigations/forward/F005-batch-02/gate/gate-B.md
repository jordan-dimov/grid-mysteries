# Gate B — pre-freeze instrument gate (C16–C19), 2026-08-26 — FINAL

METADATA ONLY. No outcome-series values recorded. All pins in ./pins/ ; machine log ./pins/pins.jsonl (url, effective url, http, sha256, fetched_utc, bytes). Extra pins (zips/xlsx/pdf/sitemaps) hashed inline in transcript and listed below.
WebSearch budget was exhausted (200/200) before this gate began; discovery done via curl on publisher URLs, gov.uk search API, data.gov.uk CKAN API, sitemaps, Wayback CDX.
Leak note: one DNO PDF grep line contained a directional statement about a DNO time-to-quote metric (digits masked). It is excluded from this report and must not be used.

## C16 — EA permitting / MCPD-SG
(a) determination times: EA corporate scorecard measures "Percentage of permits issued within timescales (category N permits)", N=1..4, quarterly HTML on gov.uk (Q1 pub 2025-10-07, Q2 2026-01-08, Q3 2026-03-26, Q4 2026-07-09). Population = all EPR permits by complexity category; MCP/SG not separable. Installations register CSV has Permission Date but no application date. → PROXY ONLY.
(b) backlog: no pending-applications series; SR2018 standard-rules SG applications are not advertised. → NO VIABLE PUBLIC INSTRUMENT.
(c) enforcement/compliance: Enforcement Actions register CSV (Action Number, Offender, Address, Action Date, Relevant Legislation, Action Type, Agency Function) — no permit linkage. CCS (annual zip 2014–2024) and National Compliance Assessment (annual zip 2014–2024) are per-permit; MCP/SG resolvable by joining Permission Number to installations register whose Activity Type Description carries labels "Specified Generator", "Tranche A/B SG Permitting Date…", "Medium Combustion Plant and Specified Generator". "Large loads" not resolvable. → PROXY ONLY.
Defra MCPD reporting: nothing on gov.uk/CKAN → NO VIABLE PUBLIC INSTRUMENT.
STATE: proxy only.

## C17 — ICP 33/132 kV
(a) ICP lead times: no public series. NO VIABLE.
(b) NERS register: not found at lr.org / lrqa.com (8 URLs 404/000; LR sitemap 2413 URLs, no NERS; Wayback CDX no hit). EXISTENCE UNVERIFIED.
(c) DNO POC/adoption: ECGS standards (e.g. "2a Provide information on point of connection within 30 WD") reported quarterly to Ofgem under RIIO-ED2 RIGs Annex G (Appendix 12/13 templates); Ofgem publication of ED2-period data not located (ED2 annual report URLs 404; data portal chart "Average time to connect" is ED1). DNO Major Connections Annual Reports (per DNO, annual; ENWL 2025-26 pinned) carry TTQ/TTC by Relevant Market Segment incl. Demand EHV+, DG HV/EHV, non-contestable vs contestable. → PROXY ONLY.
STATE: proxy only (NERS unverified).

## C18 — flex asset registration
(a) registration backlogs: FMAR not yet built; design consultation Sept 2026; "FMAR solution design baselined" milestone after; go-live undated in extracted plan text. → ELIGIBLE LATER (date not fixed; not before 2027).
(b) milestone slippage: Elexon delivery plan 2026-2028 original + "Reviewed July 2026" version, archived versions page, FMAR update posts, Deadline tracker, implementation & compliance tracker (Power BI). Observable by version diff. → ELIGIBLE NOW.
(c) tender under-subscription attributed to registration: Ofgem SLC 31E Flexibility Procurement Reports + Supporting Data (annual, per DNO, 2021-22..2024-25, latest published 2025-10-06); Elexon flexibility market catalogue (Power BI). Attribution not observable. → PROXY ONLY.
STATE: eligible now via (b).

## C19 — HV authorisation
(a) AP vacancies: no series (NSAR is rail; EU Skills WDE 2024–30 one-off). NO VIABLE.
(b) HSE: RIDKIND (kind of accident × broad industry; annual, Nov), RIDDO (DO categories incl. "Fire and explosions caused by electrical short circuit or overload", "Contact with overhead electric lines"), ESQCR (dutyholders = generators, TOs, DNOs, suppliers, meter operators; "public electricity supply equipment"). Private HV networks not identified. → PROXY ONLY.
(c) outsourced HV-operation contracts: Contracts Finder OCDS search (publishedFrom/publishedTo/limit/stage/status; no keyword param) + Find a Tender API; public-sector buyers only; text classification needed. → PROXY ONLY.
STATE: proxy only.
