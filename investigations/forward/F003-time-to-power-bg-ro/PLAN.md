# F003 — time-to-power in Bulgaria and Romania: proposed investigation plan

**Status: proposal, 2026-08-26. Not a declaration.** Nothing in this file is
frozen. When the study is opened, `DECLARATION.md` is written separately and
its digest sealed; this plan and `reconnaissance/` are the honest record of what
was already known when that happens.

## The commercial question this serves

> Can publicly available or legitimately requestable electricity-system data
> identify Bulgarian and Romanian grid nodes where a new 50–150 MW data-centre
> load has a materially better path to connection than competing nodes — well
> enough to decide where the first expensive private diligence is spent, and
> early enough that the knowledge is not already priced?

Two propositions are bundled in that question and this plan keeps them apart:

- **P-screen** — public evidence can rank where to spend the next ~£20k of
  private diligence better than a naive choice.
- **P-edge** — that ranking is *not already available* to the parties the
  sponsor must beat (land developers, data-centre developers, the TSOs
  themselves), so acting on it captures mispriced time-to-power.

P-screen can be true while P-edge is false. The money is in P-edge.

## 0. The early answer — what reconnaissance already settled

Project doctrine says the cheapest kill runs before the sophisticated thesis.
It ran during reconnaissance, before any candidate site was looked at, and it
**fired against P-edge in Bulgaria at first contact**. This is stated up front
because the brief asked for it: *if this investigation cannot plausibly create
that advantage, say so early.*

**Observed (pinned, `evidence/reconnaissance-manifest.json`):**

- ESO EAD publishes a public, unauthenticated, machine-readable map
  (`webapps.eso.bg/joining/public/map`) covering **474 substations and 810
  lines**, which for each substation and voltage level returns *total
  transfer capacity for connection*, capacity *reserved* for generation,
  consumption, mixed, storage and DSOs, and **"remaining capacity for
  connection of new capacities"** — each split by **queue stage** (opinion,
  preliminary contract, contract) — plus a "future free capacity" layer and
  the planned reconstruction/new-substation works attached to each node.
  Records carry `updated_at` timestamps from 2026-01-29 to 2026-08-05; the
  older 2021 map states updates "once a quarter or more often".
- The older ESO map (2021, still live) accepts **"Потребител" (consumer)** and
  MW as inputs and returns connection voltage, an approximate connection
  price, and the lines threatened with overload with their length and
  approximate reconstruction cost.

**Observed (press carrier of a first-party ESO statement, pinned
2026-08-26; ESO's own publication of the figures not located):**

- ESO reported **9,330 MW of data-centre connection requests by 3 Aug 2026,
  3,795 MW already holding ESO opinions**, against a national peak of roughly
  7.9 GW forecast for 2035. Opinions cost €2.8–3.8k, are issued in 14 days,
  are valid one year, confer no legal reservation or exclusivity, and — for a
  new pure-consumption site — no financial guarantee. (Whether ESO's map
  nevertheless *counts* opinion-stage MW when stating "remaining" capacity
  is an accounting question answered from the endpoint's sub-fields, and is
  kept separate from the legal one throughout.) ESO's draft 2026–2035 plan says signed
  contracts have "exhausted the transmission capability of the existing grid
  in all regions".

**Supported inference.** In Bulgaria the information that P-edge assumes is
private is published by the counterparty, at node level, with the queue, and
has already been acted on by applicants at more than the country's peak load.
An observer cannot see Bulgarian MW *before* conventional developers see them;
they see them at the same moment, on the same public map. The scarce goods are
credibility with ESO and a *firm* instrument, and the firm instrument
(connection contract) requires an effective building permit — i.e. conventional
land-and-permits development, where Trakia Economic Zone, Power Loop and the
state's own MoU counterparties are already present.

**Not determinable from reconnaissance.** Whether the same holds in Romania.
Transelectrica publishes no consumer hosting capacity and no large-load queue;
the answer is *purchasable* (solution study, ~119–144k lei excl. VAT, ≤3 months,
site-specific) and the TSO's dispatch head publicly promises an ATR "in under
three months" to a serious investor. Romania is therefore where P-screen may
have value, and where P-edge is *weak rather than dead*: the information is
not public, but it is cheap and sold on demand by its owner.

**The honest reframing, recorded as a hypothesis and not a finding.** The one
Bulgarian information asset that is genuinely non-public is the **history** of
the public map. ESO publishes a state, not a time series. A sponsor who
snapshots the map daily learns things no single reading shows: which
opinion-stage reservations lapse at their one-year mark and free capacity;
which nodes churn; how fast freed capacity is re-reserved; which "future free
capacity" promises slip. That is cheap to acquire, nobody is known to hold it,
and it decays — the shape of a real, if small, edge. Its falsifier is written
into §4.

The prohibition from F001 applies: **this study may not narrow its definition
of "advantage" until white space reappears.** The map-history hypothesis is
allowed because it is a different object (a time series vs a state), not a
smaller slice of the same one. If it fails, the study reports no informational
edge in Bulgaria.

## 1. What already exists publicly (evidence availability map)

Full detail, with per-item verification labels, is in `reconnaissance/`. The
table below is the map at the resolution needed to plan; **R** = machine
readable, **P** = text-layer PDF, **I** = image only.

| Country | Source | What it gives | Resolution | Vintage / cadence | Form | Entitled to support | Not entitled to support |
|---|---|---|---|---|---|---|---|
| BG | ESO "ESO Map" 2026 + JSON endpoints | remaining/reserved capacity by type and queue stage; AT ratings; joined/installed sums; assigned planned projects; lines | substation × voltage (400/220/110/20 kV) | continuous, `updated_at` per record; no history kept | **R** (GeoJSON/JSON, no auth, no licence text) | node inventory; ESO's *stated* remaining capacity; queue composition by stage; which planned works attach to a node | firm capacity; N-1 headroom; simultaneity; timing; any commitment |
| BG | ESO 2021 capacity map + explanation PDF | consumer/producer free capacity, connection voltage, indicative price, threatened lines with reconstruction cost | substation | quarterly or better | **R** (inline JS arrays) | ESO's indicative price and reinforcement exposure per node | same as above; explicitly "not a reservation" |
| BG | ESO ten-year plans 2025–2034 (approved, KEVR ДПРМ-2/25.09.2025) and draft 2026–2035 (17.03.2026) | national balances; named 400 kV and 110 kV projects; most-loaded elements 2035; 2030 load and RES maps by municipality; short-circuit levels | project / municipality choropleth | biennial-plus; draft not yet approved | **P** (maps as images) | which reinforcements are planned, where, roughly when | per-substation loading; costs per project; the consumer queue |
| BG | KEVR working-group report 23.07.2025 | project list with start/end years | line / substation | annual | **P** | dates of planned works | costs |
| BG | Наредба № 6/2024 (consolidated to ДВ 35/14.04.2026); Energy Act чл. 81г, 116, 117 | process, deadlines, validity, transfer, guarantees | — | as amended | HTML/PDF | rules as of a date | how ESO applies discretion |
| BG | ESO statistical booklet; operational JSON (`last24load`, `load_plus_forecast`) | national series; substation counts by voltage | national | annual / live | **R**/P | context | anything nodal |
| BG | DSO RES capacity lookups (ERM Zapad, EVN, Energo-Pro) | yes/no for RES only | settlement | irregular | HTML | nothing for consumers | consumer hosting capacity |
| BG | BAI investmap, NKIZ | industrial-zone parcels, stated electricity fields | parcel | irregular | HTML/PDF | land candidates | power availability |
| RO | PDRET 2026–2035 (ANRE consultation copy, 523 pp) | Annex B-1 realised P/Q per 110 kV bus at four characteristic instants; B-3/B-4 per-element I/Iadm % (winter 2025, summer 2024–25); **G** element loading 2026/2030/2035; C-1 zone consumption forecast; F-3 project list with PIF slippage; ch. 6.3.1/Annex 3 N-1 needs by section | bus / element / zone / section | biennial; not yet approved | **P** (layout tables, decimal comma) | present loading; planned works and slippage; zone demand outlook | consumer headroom per node (never published); generation per node (withheld, C-4); costs (withheld, F-1/F-2) |
| RO | PDRET 2024–2033 (approved, ANRE 2715/17.12.2024) + annexes | same structure, 2023 data | as above | — | **P** | a second vintage for slippage measurement | as above |
| RO | Transelectrica capacity maps (`harti_crd_tel`) + `date/date.json` | generation headroom by zone with CR/ATR/study/request MW | **10 zones A–J**, 2025/2030 | monthly stage totals | **R** (JSON) / HTML | generation-side saturation by zone; where consumer connections would *increase* generation headroom (note 8) | consumer headroom |
| RO | Allocation process publications; government ATR list 25.04.2026; DEER Anexa 9.1–9.3 | generation queues, ATR holders with county/operator/stage; DSO-level ATRs with connection station | county / zone / station | annual–semi-annual | **R** (xlsx) / **P** | generation queue composition | consumer applications (word "consum" absent) |
| RO | Ordin ANRE 59/2013 as amended by 20/2025 and 15/2026; Ordin 11/2014, 53/2024, 137/2021 | process, ATR validity, guarantees, transfer, reinforcement allocation | — | as amended | secondary copies only (legislatie.just.ro unreachable here) | rules as of a date, **pending primary check** | — |
| RO | Transelectrica operational pages; summer-2026 operational planning memo; annual outage programmes | national consumption 15-min; outage schedules per equipment | national / equipment | live / annual | **R** (xlsx) / **P** | context; which elements are out when | nodal headroom |
| RO | DSO publications (Delgaz HV map 2022 image; MV consum/generare maps behind access code; DEER lists) | little for consumers | station | stale | **I**/**R** | — | consumer hosting capacity |
| RO | energymap.ro; MDLPA parks xls | county consumption 2021–24; industrial parks | county / park | irregular | HTML/xls | land and demand context | power |
| EU | ENTSO-E Transparency Platform (CC-BY 4.0, BG/RO not excluded) | units ≥100 MW with location and voltage; per-unit generation; unit and transmission outages (asset named unless CIP exemption); zonal load/flows | unit / asset / bidding zone | live | **R** (REST, free token) | generation geography; retirements; named transmission outages | nodal headroom |
| EU | TYNDP 2024/2026 public files (CC-BY 4.0) | zonal reference grid (`BG00`, `RO00`), scenarios, project portfolio | bidding zone / project | biennial | **R** (xlsx) | cross-border and scenario context | anything nodal |
| EU | TYNDP nodal grid model (CGMES, EQ/TP/SSH/SV, ≥220 kV explicit, loads aggregated to EHV nodes, BG and RO included) | bus-branch solved model | EHV substation | TYNDP 2020 vintage confirmed; 2024 "aggregated model available upon request" | CGMES | see §7 | 110 kV; anything the TSO nets against its queue |
| EU | CGMES public test models; operational CGM/IGM | none for BG/RO (RealGrid anonymised, CC BY-NC-SA); CGM TSO/RCC-only | — | — | — | pipeline testing only | evidence |
| EU | PyPSA-Eur OSM network v0.7 (ODbL) | ≥220 kV topology, synthetic ratings; BG 113 buses / 165 lines, RO 165 / 203 | substation (merged 500 m) | 2026-02 | **R** (csv) | topology, meshedness, path counting | ratings, loads, dispatch |
| EU | Capacitypedia (launched 2026-05-22) | directory of national hosting-capacity pages; BG (DSO, solar) listed, RO absent | — | — | HTML (non-commercial T&C) | nothing beyond pointers | — |

## 2. What must be requested (routes outside the repository)

| # | Request | Route | Cost / time | Why it matters | Terms unknown |
|---|---|---|---|---|---|
| R1 | ENTSO-E **TYNDP Study Model** (nodal CGMES) | `https://stum.entsoe.eu/` form ("TYNDP Study Model"), company e-mail address; covering e-mail to `servicedesk@entsoe.eu` cc `tyndp@entsoe.eu`. Draft wording in `reconnaissance/recon-entsoe.md` §I | free; weeks | only route to a BG/RO nodal model | eligibility of a company, commercial use, publication of derived per-node results, TSO consent — all **not determined**; closest analogue (IDM undertaking) is an NDA with pre-publication sharing and €25k per breach |
| R2 | Transparency Platform API token | register, e-mail `transparency@entsoe.eu`, subject "RESTful API access" | free; ≤3 working days | unit locations, named outages | none — CC-BY 4.0 |
| R3 | Transelectrica: how many **consumer** solution studies >50 MVA were registered 2025–26, and whether a solution study can be requested *without* a land right (only the ATR demonstrably needs one) | Art. 10 information request (Ordin 59/2013) or press-office question | free; weeks | decides whether the Romanian queue is crowded and whether screening precedes or follows land options | may be refused as commercial |
| R4 | ESO: whether the ESO Map data are licensed for re-use and whether historical snapshots exist | e-mail to ESO connections department | free | legality of the map-history instrument; whether the history is already available to others | — |
| R5 | One Bulgarian data-centre connection **opinion** (from a cooperating applicant) | private | — | tests whether the opinion states anything the map does not | confidentiality |
| R6 | Consolidated Romanian regulation text (MO 517 bis/2013 as amended by MO 501/2025, MO 436/2026) | legislatie.just.ro from a Romanian IP, or a Romanian counsel | trivial | every Romanian rule in this plan rests on secondary copies | — |

R1 is submitted in parallel and nothing depends on it (§7).

## 3. What can be machine-read today, without a scraper

- ESO Map: two GET endpoints (points, lines) and one POST endpoint (per
  substation) — a daily snapshot is ~2 MB and three requests plus one per
  substation. This is the only data the plan proposes to fetch on a schedule,
  and only after R4 clarifies re-use.
- ESO 2021 map: one page with inline arrays (447 substations).
- Transelectrica `date/date.json` (zones), DEER Anexa 9 xlsx, government ATR
  xlsx, outage programme xlsx.
- PDRET annexes B-1/B-3/B-4/G and F-3: `pdftotext -layout` parses the tables;
  a small Polars loader with Decimal handling is a day's work and is the first
  analytical module worth writing.
- Transparency Platform REST for the two bidding zones.
- TYNDP zonal xlsx; PyPSA-Eur csv; JRC-PPDB-OPEN.

## 4. Cheapest falsifiers, in leverage order

Each is a test the study commits to *before* candidate work, with the answer
that kills or downgrades. "Leverage" = P(changes conclusion) × importance ÷
cost.

| # | Test | Cost | Kills |
|---|---|---|---|
| K1 | **How crowded is the conversion race at the nodes the brief names?** Read the pinned snapshot for the ten named candidate areas: ESO's stated remaining capacity for consumption vs the MW ESO *counts* at opinion, preliminary-contract and contract stage. Terminology, fixed after review: an opinion **reserves nothing legally** (Naredba 6 — no exclusivity, no guarantee, one-year validity), but ESO's accounting may still *net* opinion-stage MW against total capacity when it states "remaining"; whether it does is read off the row sub-fields (`opinion`, `pd`, `contract`) before any ratio is computed. | hours (data already pinned) | Nothing — K1 no longer kills. P-edge for *state* information is already dead (§0) whatever K1 shows. K1 **measures** instead: opinion-stage MW ≫ remaining means many non-exclusive claimants racing to convert, not "the MW are gone"; contract-stage MW ≥ remaining means they are gone. The reading feeds F004, not a kill here. |
| K2 | **Does the map history contain information?** Take daily snapshots for 60 days; measure lapse events (opinion-stage MW that disappears), re-reservation lag, and node-level churn. | ~0 marginal; 60 days elapsed | the map-history hypothesis, if lapses are rare, or freed capacity is re-reserved within days, or ESO confirms it publishes history / re-use is barred (R4). |
| K3 | **Is Romanian consumer headroom purchasable faster than it is screenable?** R3, plus the 2011 TEL guide's 50 MVA threshold checked against current text (R6). | one letter | P-edge in RO if the TSO answers large-load studies in ≤3 months without land rights: screening then saves at most a few studies' cost. |
| K4 | **Does any CEE transaction price the connection position at all?** One documented sale of land + ATR / land + opinion with price and stage. | days of search; already tried once and found none | the *buyer value* term. If after a second, targeted attempt no price exists, the study reports buyer value as not determinable and no opportunity is named. |
| K5 | **Does PDRET Annex G discriminate?** Compute the distribution of 2030 loading across RET elements adjacent to the ~40 RET stations; if most sit in a narrow band, public loading cannot rank nodes. | 2–3 days (loader + one plot) | P-screen in RO. |
| K6 | **Is the Bulgarian opinion informative beyond the map?** R5. | one favour | the residual "interpretation edge" in BG. |

K1–K3 run before any candidate record is written. K4 is the falsifier for
naming an opportunity at all. K5 gates Romanian candidate work. K6 is
opportunistic.

## 5. First governed artefacts

1. **`DECLARATION.md`** (frozen, digest sealed via the existing
   `ProtocolDeclared` path — `scripts/check-record` already scans
   `investigations/*/*/DECLARATION.md`). Contents: the two propositions; the
   early answer of §0 stated as *known at declaration*; K1–K6 with their kill
   conditions; the ten Bulgarian candidate areas from the brief as a **frozen
   candidate list** so no area can be added after the map is read; the
   Romanian candidate rule (every Transelectrica 400/220 kV station — ~80 —
   rather than a hand-picked list, because no prior exists); the invalid
   inference stated verbatim ("X MW spare transformer capacity ≠ X MW
   available connection capacity"); the scenario and scoring rules for the
   RO screen; the three-clock rule; reflexivity (publishing a node ranking
   may itself attract applications to those nodes).
2. **`evidence/public-as-of-manifest.json`** — digests of everything the
   declaration relies on: the six ESO artefacts already pinned; ESO plans
   (oid 5665, 5850), KEVR decision and report; Naredba 6 PDF; PDRET
   2026–2035 and 2024–2033 with annexes; Transelectrica procedure and
   `date.json`; ATR list xlsx; TYNDP starting grid; TP extracts. All
   re-fetched through `grid_mysteries.sources.pinning` so the journal is
   restart-safe (the reconnaissance lost its working copies once already).
3. **`evidence/eso-map-snapshots/`** — a journalled daily snapshot of the
   three ESO endpoints, starting the day R4 is sent (not awaiting its
   answer, since the data are public and unauthenticated; stopping if ESO
   objects). This is the K2 instrument and the only scheduled fetch.
4. **`src/grid_mysteries/sources/eso.py`, `transelectrica.py`** — thin,
   tested loaders (JSON → Polars with Decimal MW; PDRET layout-table parser
   with fixtures cut from the pinned PDFs). No analytics yet.
5. **`CANDIDATES.md`** — written only after K1–K3, using the record format from
   the brief (positive / negative evidence; what public evidence is and is not
   entitled to say; cheapest next discriminating test; kill condition). One
   record per frozen candidate, including the ones that die at K1.
6. **Morpholog**: no new vocabulary proposed in advance, consistent with F001.
   The forward track still has no governed predicates; F003 will run on
   sealed file digests and propose vocabulary only if it forces some.

## 6. Where this lives

`investigations/forward/F003-time-to-power-bg-ro/` — the third forward study,
sibling of `F001-connection-readiness/` and `F002-batch/`. Country- or
source-specific behaviour goes in `src/grid_mysteries/sources/`; the screening
rules, once any exist, in `src/grid_mysteries/investigations/`; raw downloads
under `data/raw/eso/`, `data/raw/transelectrica/`, `data/raw/entsoe/`. The
study is *not* a Generator v3 batch candidate: it was commissioned, not
generated, and is recorded in `../FALSE-NEGATIVES.md` only if it turns out to
be an opportunity the generator would have missed.

## 7. Stop conditions before any power-flow modelling

Power-flow modelling is **not planned** and is gated by all of the following
being true. As of this plan none is.

| condition | status now |
|---|---|
| S1 — the public screens (BG map; RO PDRET annexes + zone maps) fail to discriminate between candidate nodes *and* the discrimination sought is worth more than a Romanian solution study (~€25–29k per site) | untested; K5 answers half of it |
| S2 — a nodal model covering BG and RO is in hand under terms that permit commercial site screening and publication of aggregated results | R1 not yet sent; terms **not determined** |
| S3 — the model contains the voltage level at which the candidates connect | the TYNDP model is ≥220 kV bus-branch with loads aggregated to EHV nodes; BG 110 kV (ESO-owned, where most of the 281 mapped substations sit) is **absent by specification**; RO 110 kV belongs to DSOs and is not in any obtainable model |
| S4 — operational limits cover the branches around the candidates (a screen with silent unlimited branches is not a screen) | unknown until a model is opened; pypowsybl reports zero violations with no warning where limits are absent |
| S5 — a pre-declared dispatch scenario set exists, so a ranking is conditional on named states rather than one snapshot | not written; would be part of a later amendment |
| S6 — the output would be phrased only as "under the reconstructed model and tested states, +100 MW at X creates fewer apparent thermal/voltage problems than at most comparison nodes", and that sentence would change a commercial decision | the TSO maps already say more than that sentence for BG; for RO the sentence competes with a purchasable ATR |

Technical legitimacy of the pipeline itself is not in doubt: pypowsybl 1.16.1
(MPL-2.0, Python 3.14 wheels) imports CGMES 2.4.15/3.0 with PATL/TATL limits,
runs AC load flow and N-1 security analysis, and was exercised end-to-end on a
conformity model during reconnaissance (`reconnaissance/recon-tooling.md`).
The evidential problem is the model and the voltage level, not the tool.
**Recommendation: do not build the model for screening purposes.** If it is
ever built, it is for a different reason — an independent, reproducible,
published reconstruction of EHV headroom to compare against the TSOs' maps —
and that is a publication decision, not a diligence one.

## 8. The residual study proposed

Small, sequential, each stage able to stop the next.

**Stage A — declare and pin (week 1).** Items 1–2 of §5; send R1–R4; start the
ESO snapshot. Output: sealed declaration, manifests.

**Stage B — Bulgaria kill (week 1–2).** K1 on the ten frozen candidate areas
from the pinned snapshot; K6 if R5 is available. Expected outcome: P-edge dead
in BG for *state* information; the study says so, with the node-by-node queue
composition as the evidence. Output: ten candidate records, most of them
killed.

**Stage C — Romania screen (weeks 2–5).** PDRET loader; K5; for every 400/220
kV RET station: 2025 loading of adjacent elements (B-3/B-4), 2030/2035 loading
(G), planned works and slippage (F-3), zone consumption forecast (C-1), zone
generation saturation (`date.json`), named outages and unit retirements (TP),
meshedness (PyPSA-Eur path count). Each signal paired with its counter-signal
(e.g. low loading ⇐ weak demand ⇐ no fibre/labour; slippage ⇐ permitting
⇐ the sponsor's own permits would slip too). Output: a ranked shortlist of
**where to buy a solution study first**, phrased exactly so, plus the
Bulgaria–Romania comparison the brief asked for (does the same method
discriminate more in one country than the other, and why).

**Stage D — map history (day 60).** K2 result. Either the one Bulgarian
non-public asset exists and its value is bounded (how many MW lapse per
quarter, at which nodes), or it does not.

**Stage E — profile and publication decision.** Report across the eight
forward dimensions (constraint strength, evidence quality, scenario
robustness, recognition gap, buyer pain, solution adequacy, action lead,
reflexivity) — no composite score — and score the forecast as a vector
`(need, timing, adoption, capture)` when outcomes arrive. Publication is the
human gate.

Budget: the analytical work in B–D is ~10–15 working days. The only external
spend is optional: one Romanian solution study (~€25–29k) at the top-ranked
station, which is also the ultimate falsifier of Stage C — if the study's
answer could have been read off public evidence, P-screen held; if it
surprises, it did not.

## 9. What this plan deliberately does not do

- It does not read node values for any candidate area before the declaration
  is sealed. The pinned snapshot is on disk; it has not been looked at below
  field-name level.
- It does not build a scraper beyond the three-endpoint daily snapshot.
- It does not request the CGMES model as a dependency; the request is sent
  because it is free and slow, and its answer becomes evidence about *access
  terms*, which is itself a finding (§2, R1).
- It does not treat missing evidence as permissive: "no consumer capacity map
  in Romania" is not "capacity is available in Romania".
- It does not name an opportunity. Three propositions must be earned first —
  the problem is coming, a buyer is compelled, existing solutions are
  inadequate — and reconnaissance found the third already contradicted in
  Bulgaria (ESO solves it by publishing) and unproven in Romania (Transelectrica
  solves it by selling). The most likely honest output is a **described
  method with a measured discrimination power**, a **killed edge in Bulgaria**,
  a **bounded edge in Romania**, and a **map-history instrument** whose value
  is a number, not a thesis.

## 10. Provisional profile (to be re-scored at each stage)

| dimension | now | basis |
|---|---|---|
| constraint strength | strong | grid capability "exhausted in all regions" (ESO draft plan); 9.3 GW requested vs ~7 GW peak |
| evidence quality | high for BG state, medium for RO, low for prices | primary machine-readable map; PDRET annexes; no CEE transaction price |
| scenario robustness | not assessed | no scenarios written |
| recognition gap | **small or negative** | the TSO publishes the state; 9.3 GW of applicants have recognised it; ENTSO-E and the Commission are pushing publication of hosting capacity EU-wide |
| buyer pain | real but thin in realised MW | BG realised demand at MW scale; RO tens of MW live, hundreds announced |
| solution adequacy (for the buyer's decision) | BG: adequate via publication; RO: adequate via purchase | the absorption kill |
| action lead | short | 1-year opinions in BG; ≤3-month ATR promise in RO |
| reflexivity | material | publishing a node ranking invites applications to those nodes |

That profile is the reason the plan is small.

---

## Amendment 1 — 2026-08-26, after external review, before any declaration

Recorded the same day as the plan, before any candidate value was read.

**A1.1 Terminology.** §0 and K1 conflated two things: *legal reservation*
(an opinion confers none) and *ESO's accounting* (its map may net
opinion-stage MW when stating "remaining"). They are now separated, and K1
is no longer a kill test — it is a measurement of how crowded the conversion
race is at a node. A node with 300 MW remaining and 500 MW at opinion stage
is not "gone"; it is contested by non-exclusive claimants. That reading
matters for F004 (below), not for F003's P-edge, which is dead on the
state-information question regardless.

**A1.2 Findings banked, effort cut.** Two findings are recorded now rather
than after Stages B–D:

- **F003-1 — Bulgaria, public-state information edge: absorbed.** The TSO
  publishes the state and the queue by node and stage; applicants at more
  than national peak load have already acted on it. High confidence; rests on
  pinned primary artefacts plus one pinned press carrier of ESO's figures.
- **F003-2 — Romania, public screening: potentially measurable,
  economically bounded.** The counterparty sells the answer per site for
  ~€25–29k in ≤3 months; a screen's value is bounded by the studies it avoids
  and by land-option sequencing. Worth K5 (2–3 days), not a company.

Stages B–D are cut accordingly: B becomes a half-day reading of K1 (a
measurement, banked); C is K5 only; D is unattended instrumentation with **no
human research time** — the map history is kept because it is free, and it is
re-purposed (A1.4). Total human effort ~3–4 days, not 10–15. The declaration,
when written, freezes F003-1 and F003-2 as *known at declaration*.

**A1.3 A new conjecture is not folded into F003.** The review proposes:

> Bulgaria's cheap, non-exclusive connection process has generated a
> speculative data-centre pipeline (9.33 GW requested, 3.795 GW with
> opinions) most of which cannot convert; the opportunity may be acquiring or
> JV-ing high-quality projects whose promoters cannot turn an opinion into a
> permitted, financed, buyer-backed project.

That is a different *function* (conversion and sponsorship) from F003's
(information). Under the F001 prohibition it may not be admitted as a
narrowing of F003; it gets its own pre-declared absorption kill, written
before any evidence is examined, in
`../F004-stranded-pipeline-bg/KILL-DECLARATION.md`. Two cautions are recorded
there and repeated here so they are not lost: the opinion itself is worth
approximately nothing by construction, so "stranded value" is land plus
permits plus local process — ordinary real-estate development, which existing
developers absorb routinely; and the very fact that makes projects strand (few
buyers) is the fact that makes them worthless to acquire, so the buyer
proposition must be earned first, not last.

**A1.4 The map history changes role.** In F003 it was a candidate edge and
the review is right that "two days earlier than another developer" is not a
business. As an instrument it is better than that: the per-node sub-fields
(`opinion` → `pd` → `contract`) make **conversion** and **lapse** separately
observable over time. Opinion-stage MW that disappears without appearing at
`pd` is a lapse; MW that moves to `pd` is a conversion. The lapse rate is the
strain sensor F004 needs and the cheapest one available. It costs nothing to
run.

**A1.5 Lead recorded, not verified.** The review states that Bulgaria was
required under its recovery-plan reform to publish substation-level
connection capacity, tied-up capacity, remaining capacity and planned
investments at least monthly (citing Council doc. ST 12334/2026 ADD 1). The
EUR-Lex fetch was refused (HTTP 202, empty body). If true it makes the
transparency structural rather than incidental — strengthening F003-1 — and
belongs in the declaration once pinned from the primary text.

**A1.6 Pinned this amendment.** The economic.bg article of 2026-08-12
carrying ESO's figures (t_event 2026-08-03, t_public 2026-08-12,
t_discovered 2026-08-25) — `evidence/reconnaissance-manifest.json`.
