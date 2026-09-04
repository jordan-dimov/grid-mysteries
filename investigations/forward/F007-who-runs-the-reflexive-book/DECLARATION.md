# Forward Mystery F007 — who runs the reflexive book?

**Generator**: v4 (`investigations/forward/CANDIDATE-PROTOCOL.md`,
`2ac6efa8e873100d4d06937d61e3f06e38cdcccd86b4fc50fca7ef3d911b2558`).
**Generated**: 2026-09-04. **Public-as-of**: 2026-09-04.
**State**: GENERATED. Committed in this state so that the generation
digest predates any pinned primary document, any metadata reading and
any market evidence. §6 (pinned forcing variables, with each source's own
caveats), §7 (instrument states) and §8 (freeze: kill order, thresholds)
are appended afterwards; nothing above §6 is edited. The file's digest at
the freezing commit is the study's identity. For the forward track the
human gate is **publication**: the falsifiers are frozen here, with the
claim, and nothing is released without the sponsor's seal.

**Standing note.** The 2026-08-26 recalibration limits desk research on a
new opportunity to two hours before a buyer conversation. The sponsor
commissioned this study on 2026-09-04 as an explicit exception, on the
same terms as F006: the forcing variables are dated statutory obligations
whose text can be pinned, and the falsifiers are built to kill the study
early. F006 is the precedent for what an honest kill looks like; this
study is allowed to end the same way. That decision is the sponsor's and
is recorded, not re-argued.

## 1. The question

Three things are true at once. Germany has required every electricity
supplier to offer a **dynamic tariff** to household customers since
1 January 2025, against an installed base of well over a million home
batteries, with the smart-meter-gateway rollout as the binding constraint
on how many customers can actually take one. The EU electricity directive
requires suppliers above a customer threshold to offer dynamic price
contracts wherever smart meters are installed. Great Britain moves every
customer onto **half-hourly settlement** under MHHS, so a supplier's
imbalance is settled on what its customers, batteries included, actually
did in each half hour.

> **When a supplier's customers hold batteries that respond to the
> supplier's own prices, whose problem is the resulting position — and is
> that job being done?**

Deliberately *not* "will dynamic tariffs grow" or "will home batteries be
aggregated". The object is the **supplier's book**: a retail portfolio
that has become a trading position because its load now moves *against*
the supplier's own price signal, and which must be forecast, hedged,
balanced, settled half-hourly (quarter-hourly in Germany) and explained
to each customer. The reflexivity is the point: an ordinary retail load
is exogenous to the tariff; a battery on a dynamic tariff is a function
of it.

## 2. Prior exposure, recorded

- **Investigation 010** (sealed run 2026-09-03, results at commit
  `79781e3`, not published) established from pinned Octopus terms that a
  household battery's earnings are bounded by **which import and export
  products the supplier permits together** and by the **export
  connection**, and that the household's optimum is computable from the
  16:00 information set. The pairing rules (Flux exclusive; Go only with
  SEG, Outgoing and Agile Outgoing) are therefore already in the record
  as a named instance of function R4 below. Used here as adjacency, not
  as evidence.
- **F006** (frozen 2026-09-03) established that the GB load-control
  licence carries no per-signal proof duty, and recorded — as a hindsight
  guard — Kraken's consultation question whether a supplier whose
  customers "use the supplier's tariff information to optimise their
  device" is a load controller. That question is the reflexive book seen
  from the licensing side; it is disclosed here so it cannot later be
  presented as a K1 finding.
- On 2026-09-03 a **Perplexity research run in another repository**
  produced counts of Kraken licensees and descriptions of VPP payout
  models. **Nothing from that run enters this record unpinned.** Every
  count used in a kill is replaced by a pinned primary (the licensee's
  own release, the regulator's table) or recorded as *not found in a
  primary source*.
- Batch 01 C1 (MHHS as a transition programme) and Batch 02 C18 (Elexon
  as market facilitator) characterised MHHS and Elexon in this project's
  record; disclosed as adjacency.

## 3. The forcing variables, as hypothesised (to be replaced by §6)

Three co-present external changes, each a hypothesis with a known author
until §6 pins its text:

1. **Germany, EnWG §41a.** Every electricity supplier must offer a
   dynamic tariff to household customers from 1 January 2025 (previously
   only suppliers above 100,000 customers, and only where a smart meter
   is installed). Hypothesised context: the Marktstammdatenregister
   records well over a million home battery storage units; the smart
   meter gateway (iMSys) rollout under the MsbG, restarted by the GNDEW
   of 2023, is the binding constraint on how many households can take a
   dynamic tariff, because a quarter-hourly-settled tariff needs a
   quarter-hourly meter. A 2025 amendment package (the "Smart-Meter-
   Rollout" / EnWG revision) may have altered the obligation or its
   timetable — to be pinned, not assumed.
2. **EU, Directive (EU) 2019/944, Article 11.** Member states ensure that
   final customers with a smart meter can request a dynamic electricity
   price contract from every supplier above a threshold (hypothesised:
   200,000 final customers, with the option to lower it); suppliers must
   inform customers of the opportunities, costs and risks; regulators
   monitor and report on dynamic-tariff take-up and risk. The 2024
   electricity market design reform (Directive (EU) 2024/1711) may have
   amended Article 11 — to be pinned.
3. **Great Britain, MHHS.** Ofgem's decision (CR055, approved
   29 November 2024, already pinned in F006 as
   `ofgem-mhhs-cr055-decision-page`) sets migration from October 2025
   with the migration window ending May 2027 and cutover July 2027;
   every MPAN is settled on its own half-hourly data, so a supplier's
   imbalance position is its customers' actual half-hourly behaviour.

**What is not hypothesised.** Nothing about how many suppliers offer a
dynamic tariff, how many customers hold one, what the portfolio managers
charge, or whether any supplier has withdrawn or repriced a dynamic
tariff. Those are instrument values and incumbent-market facts, and are
not read before the freeze.

## 4. Generation — the v4 chain, run blind

Force vocabulary as v2/v3: `continuous` · `cross-organisational` ·
`data-intensive` · `high-volume` · `latency-sensitive` · `standardisable`
· `independence-required` · `liability-bearing` · `comparable-across-assets`
· `specialist-human-workflow` · `rising-transaction-volume` ·
`expensive-adviser-labour`.

**The chain.** External change (a statutory duty to offer a price that
moves; a stock of batteries that can respond to it; settlement on what
actually happened at each meter point) → the supplier's load becomes a
function of the supplier's price → functions that an ordinary retail
supplier never had to perform become mandatory → each is either absorbed
by an existing job or is not.

**Buyer classes**, named blind for every function: **(i)** German
municipal utilities (Stadtwerke) and regional suppliers, of which there
are several hundred, most without a trading desk; **(ii)** GB domestic
suppliers not operating on Kraken; **(iii)** Australian retailers, as a
comparator only (a pinned count, nothing more). The dynamic-tariff
specialist suppliers (Tibber, Octopus Germany, 1KOMMA5°, Enpal, and in GB
Octopus itself) are **not** buyers here: they are named as incumbents,
because the blind hypothesis is that the job has already gone to them.

**Incumbent candidates**, named blind before any incumbent-market
evidence is read: Kraken and its licensees; the German portfolio managers
that serve municipal utilities (Trianel, Thüga's energy-trading arm,
Syneco, and the service arms of the large utilities — EnBW, E.ON,
RWE Supply & Trading, Vattenfall); the German dynamic-tariff specialists
that are themselves suppliers (Tibber, Octopus Germany, 1KOMMA5°, Enpal);
the GB billing and settlement vendors (Kaluza, ENSEK, Gentrack,
Utiligroup); the German billing platforms (SAP IS-U / S/4HANA Utilities,
Schleupen, Wilken, powercloud) and the Stadtwerke IT service houses; the
supplier's own trading desk where one exists; and, for disputes, the
metering point operator and the statutory dispute bodies
(Schlichtungsstelle Energie; the Energy Ombudsman).

| # | Forced function (what the supplier's book now requires) | Forces | Buyer class | Incumbent guess (blind) | Predicted strain symptoms | Candidate public series (named for the gate, values unread) |
|---|---|---|---|---|---|---|
| **R1** | **Forecasting a load that responds to the supplier's own tariff**: the day-ahead and intraday load forecast for the dynamic-tariff segment, where the segment's batteries charge into the supplier's own troughs and discharge into its peaks, so that the forecast depends on the price the supplier is about to publish | continuous, data-intensive, latency-sensitive, comparable-across-assets | (i), (ii); (iii) comparator | the supplier's own trading desk where one exists; otherwise the portfolio manager's standard-load-profile-plus-adjustment forecast; for the specialists, their own platform (Kraken, Tibber's) | (a) portfolio-management contracts or service descriptions add a dynamic-tariff or "flexible load" line, or price it separately; (b) suppliers state in consultation responses or annual reports that dynamic-tariff load is unforecastable or costly to balance; (c) suppliers withdraw, close to new customers, or punitively price their §41a tariff | Bundesnetzagentur / Bundeskartellamt Monitoringbericht (annual; counts of suppliers offering dynamic tariffs and customers on them); portfolio managers' published service pages and price lists; BNetzA §41a consultation / association responses (BDEW, VKU) |
| **R2** | **Balancing-group and imbalance management of a reflexive position**: holding the balancing group (Bilanzkreis) or the BSC imbalance account for a segment whose deviation from schedule is correlated with the supplier's own price and with every other dynamic-tariff supplier's, so that the segment's imbalance is systematically one-sided in exactly the quarter hours when imbalance is most expensive | continuous, latency-sensitive, liability-bearing, high-volume | (i), (ii) | the balancing-group responsible party: the portfolio manager for most Stadtwerke; the supplier's trading/settlement function or an outsourced trading service in GB; the specialists themselves | (a) TSOs or Elexon tighten balancing-group / imbalance rules for load that follows price (data obligations, schedule granularity); (b) imbalance cost share attributable to dynamic-tariff suppliers is reported or complained of; (c) portfolio managers exclude or surcharge reflexive load in their balancing-group service | Netztransparenz reBAP (quarter-hourly imbalance price, publisher-level, no supplier split); TSO Bilanzkreisvertrag versions and BNetzA balancing-group determinations (metadata); Elexon BSC modification register (metadata); portfolio managers' service pages |
| **R3** | **Hedging the dynamic-tariff segment**: the segment passes spot through, so energy-price risk is small but the residual — forecast error times price, and the fixed components the supplier still owes (network charges, levies, margin) against a volume that moves — must be hedged and priced into the markup, and the segment's tariff structured (pass-through plus fee, cap, "smart" variant) so the supplier's residual stays bounded | data-intensive, comparable-across-assets, expensive-adviser-labour | (i), (ii) | the portfolio manager's structuring service; the supplier's own trading desk; for the specialists, in-house product economics | (a) dynamic-tariff terms restructured within the year (caps, fixed components, hybrid products) across many suppliers; (b) portfolio managers publish a "dynamic tariff" product or advisory line; (c) regulator monitoring reports a dynamic-tariff markup dispersion | supplier tariff terms (versioned pages); portfolio managers' service pages; Monitoringbericht; ACER/CEER Market Monitoring Report, retail volume (annual) |
| **R4** | **Designing the tariff-pairing and export rules that cap the household's arbitrage against the supplier**: which import and export products may coexist, what export price the supplier pays, whether a battery may charge from the grid on the export tariff — the rules 010 found decide the household's optimum, written by the supplier against its own customers | standardisable, liability-bearing, comparable-across-assets | (i), (ii); the specialists write these already | the supplier's own product and legal function; for the specialists, product design (Octopus's smart-tariff terms are the pinned instance from 010); in Germany the AGB of Tibber, Octopus Germany, 1KOMMA5°, Enpal | (a) terms versions add pairing exclusions, export caps or "no grid charging" clauses; (b) consumer bodies or the regulator challenge such clauses; (c) Stadtwerke §41a tariffs carry no export product at all (the arbitrage cap by omission) | supplier AGB / terms pages (versioned; 010's Octopus pins already exist); Verbraucherzentrale / BNetzA consumer complaint statistics (metadata); Monitoringbericht |
| **R5** | **Quarter-hourly / half-hourly settlement and bill explanation for prosumers**: producing a bill from 35,040 (DE) or 17,520 (GB) priced intervals a year, reconciling it against the metering point operator's values and the settlement run, and explaining to a household why its battery earned what it did | high-volume, standardisable, data-intensive, rising-transaction-volume | (i), (ii) | billing vendors — GB: Kaluza, ENSEK, Gentrack, Utiligroup; DE: SAP IS-U / S/4HANA Utilities, Schleupen, Wilken, powercloud, the Stadtwerke IT service houses; the specialists' own apps | (a) MHHS migration slippage concentrated in particular suppliers; (b) billing complaints for dynamic tariffs rising in the dispute bodies' category counts; (c) billing vendors announce dynamic-tariff or MHHS modules (`ProvisionExists`, not strain); (d) suppliers cite billing-system readiness as the reason not to offer §41a tariffs | Elexon MHHS programme migration dashboards (cadence: programme reports); Schlichtungsstelle Energie Tätigkeitsbericht (annual; complaint categories); Energy Ombudsman complaint data (GB); BNetzA §41a monitoring |
| **R6** | **Reconciling the supplier's settlement data against the customer's inverter and meter when disputed**: when a household's inverter log says it exported 40 kWh at 18:00 and the settlement says 12, someone must decide which is right, on evidence, in a form a dispute body accepts | independence-required, liability-bearing, cross-organisational | (i), (ii); the household; the dispute bodies | the supplier's complaints function; the metering point operator (MSB in DE, the meter operator/data service in GB); Schlichtungsstelle Energie and the Energy Ombudsman | (a) dispute-body case categories for metering / settlement data rise; (b) dispute bodies publish guidance on inverter-versus-meter evidence; (c) MSBs or suppliers cite disputed prosumer data in consultation responses | Schlichtungsstelle Energie Tätigkeitsbericht; Energy Ombudsman data; BNetzA consumer statistics (metadata) |

**Second candidate, same batch, run K0 only unless the first dies:**

| # | Forced function | Forces | Buyer class | Incumbent guess (blind) | Predicted strain symptoms | Candidate public series |
|---|---|---|---|---|---|---|
| **S1** | **Substantiating a household battery earnings claim**: the companies selling and financing home batteries on "up to £x / €x a month" claims owe a substantiated figure to customers under consumer-protection and advertising rules and to their lenders in portfolio financing; the substantiation is a computation against the supplier's permitted pairs and the export connection — what 010 computes | liability-bearing, comparable-across-assets, standardisable | battery sellers and installers (1KOMMA5°, Enpal, Zolar in DE; the GB installer chains); their lenders and portfolio financiers; consumer regulators | the consumer codes and certification schemes for installers (GB: MCS, RECC, HIES; DE: the installer guilds and the VDE/RAL marks, if any); the installers' own calculators; the advertising regulator's rulings (ASA in GB; in DE the Wettbewerbszentrale and the courts under the UWG); the lenders' own credit models | (a) advertising rulings against battery earnings claims; (b) lenders' securitisation documents disclose an earnings-substantiation covenant; (c) consumer bodies publish "up to" warnings | ASA rulings database (searchable; metadata); Wettbewerbszentrale case reports; securitisation prospectuses / investor reports of named battery financiers (metadata) |

**Blind priors, written now.** The functions most likely to be
**absorbed successfully** by existing jobs are **R2** (balancing-group
management is exactly what a portfolio manager sells, and imbalance is
priced by the TSO whoever holds it), **R5** (billing vendors already sell
interval billing to the specialists) and **R6** (dispute machinery
exists in both markets). The functions most likely to have **already left
the incumbent** — the P6 "late" outcome — are **R1, R3 and R4** together:
the blind hypothesis is that Kraken and the specialist suppliers took the
whole reflexive book in-house between 2023 and 2025, and that a
Stadtwerk on a portfolio-management contract either offers a §41a tariff
its portfolio manager treats as ordinary load, or offers one priced so
that nobody takes it. The function most likely to be **unabsorbed at the
Stadtwerke level** is **R4**, because writing pairing rules that cap
arbitrage requires the computation 010 performs and few small suppliers
have anyone to perform it. **S1** is expected to fail K0 on class A/B and
survive, if at all, on class C (advertising law). Recorded so K1 can
score the priors, not to steer them.

**The P6 question, flagged.** The likeliest honest outcome is not
"absorbed" but "late": if the job migrated to Kraken and the specialists
in 2023–2025, the study must say *late* and name the date, not *stable*.

## 5. Evidence used only to justify generation

Only the hypothesised forcing variables in §3 and facts already in this
project's record: Investigation 010 (Octopus pairing rules; the
household optimum from the 16:00 information set), F006 (the licence's
absence of a per-signal proof duty; the MHHS CR055 pin), Batch 01 C1 and
Batch 02 C18. **No incumbent-market evidence, buyer evidence or
instrument values were examined before this section was committed.**
The Perplexity counts from 2026-09-03 are disclosed in §2 and not used.

## 6. Pinned forcing variables — appended after acquisition, before freeze

*(empty until the primary documents are pinned; each date beside the
source's own caveat; every 404 recorded as unavailable)*

## 7. Instrument states — appended by the gate

*(empty until the gate runs; metadata only; see v4 §3)*

## 8. Freeze — appended after the gate

*(kill order, K0 evidence classes, falsifiers restated against pinned
text, thresholds, freeze digest)*

---

## 6. Pinned forcing variables — appended 2026-09-04, before freeze

Everything below is read from documents pinned under
`data/raw/forward-f007/public-as-of/` (SHA-256 per file in
`evidence/public-as-of-manifest.json`, **61 artefacts**, fetched
2026-09-04; **17 refusals** in `evidence/public-as-of-unavailable.json`,
none retried by other means). Every number carries the source's own
caveat. Where §3's hypothesis differs, the pinned text replaces it. **No
incumbent page was read beyond its title and headings, and no symptom
series value was opened**; the leaks that happened anyway are listed in
the hindsight guard at the end of §7.

### 6.1 Germany — the offer duty

**EnWG § 41a as in force** (`enwg-41a-gesetze-im-internet`, gesetze-im-
internet.de, read 2026-09-04). (1) Suppliers must, "soweit technisch
machbar und wirtschaftlich zumutbar", offer final customers a tariff that
incentivises saving or shifting, and households at least one tariff whose
data transmission is limited to the total consumed. (2) Suppliers with
more than 100 000 final customers at 31 December must, in the following
year, offer a supply contract **with dynamic tariffs** to final customers
"die über ein intelligentes Messsystem im Sinne des
Messstellenbetriebsgesetzes verfügen"; "**Die Verpflichtung nach Satz 1
gilt ab dem 1. Januar 2025 für alle Stromlieferanten.**" (3) From
1 January 2025 the same contract must be offered, at the customer's
choice, without bundled network use and metering. (4) Suppliers with more
than 200 000 final customers must also offer a **fixed-price contract**
of at least twelve months on the supplier's share of the price; (5)
dynamic-only suppliers are exempt from (4); (6) suppliers must inform
customers comprehensively about "die Kosten sowie über die Vorteile,
Nachteile und Risiken" of a dynamic-tariff contract and offer information
on installing a smart metering system; (7) a short summary of key terms
before conclusion. **Read for what is absent**: the duty is to *offer*, to
customers who *already have* an intelligent metering system; nothing in
§ 41a governs the price level, the markup, the export side, or what
happens to the supplier's position. The pinned page does not carry the
commencement date of paragraphs (4)–(7); the Bundesgesetzblatt was not
pinned.

**Legislative reasoning, 2023** (`bt-drucksache-20-5549-gndew-pdf`,
Bundestag Drucksache 20/5549, the GNDEW bill; Begründung to Article 1,
pp. 40–41): dynamic tariffs are central to a flexible system; "**Bislang
stehen solchen Angeboten branchenseitig jedoch vor allem geringe Margen
und hohe Kosten bei einer geringen Zahl von Kunden mit intelligenten
Messsystemen entgegen**"; with a broad rollout "werden … nun auch im
margenschwachen Massenkundengeschäft die notwendigen Investitionen (u. a.
in IT-Systeme) wirtschaftlicher. Rollout, verbesserte Datenkommunikation
und neue Tarife bringen sich dabei gegenseitig voran. Dynamische Tarife
können so aus der bisherigen Nische zum Standardprodukt werden." The path
already in § 41a(2) sentence 3 (threshold 100 000, falling to 50 000 by
2025) is "beschleunigt und konsequent zu einer flächendeckenden
Angebotsverpflichtung fortgeschrieben"; Article 1 strikes the words "die
bis zum 31. Dezember eines Jahres mehr als 50 000 Letztverbraucher
beliefern". *Caveat*: a bill's reasoning, not a finding; it names the
supply side's own objection (margins, IT cost, few smart-metered
customers) as the thing the rollout is meant to cure.

**2025 amendment** (`bt-drucksache-21-2793-pdf`, Drucksache 21/2793,
12 November 2025, committee report on the "Gesetz zur Änderung des
Energiewirtschaftsrechts zur Stärkung des Verbraucherschutzes"): No. 62
replaces the § 41a heading and inserts paragraphs (4)–(7) (fixed-price
duty above 200 000 customers; dynamic-only exemption; information and
summary duties), "unverändert" in committee; No. 49 rewrites § 35(1)
No. 10 so that the Bundesnetzagentur's monitoring covers "**das
Marktangebot von Verträgen nach § 41a sowie die Preisvolatilität bei
Verträgen nach § 41a**" (`enwg-35-gesetze-im-internet`, in force as
pinned). *Caveat*: this is the transposition of the ten-year monitoring
duty in Article 11(4) of the directive; the first report under it has not
yet appeared (the 2025 Monitoringbericht predates it).

**The regulator's own statement of the duty** (`bnetza-press-2025-12-02-
smard-dynamische-tarife`, press release 2 December 2025): "**Alle
Stromlieferanten müssen seit dem 1. Januar 2025 mindestens einen
dynamischen Stromtarif anbieten.**" The Bundesnetzagentur now publishes
*modelled* dynamic household prices on SMARD
(`smard-modellierter-dynamischer-strompreis`): spot prices weighted by a
standard load profile, "ohne Verhaltensannahmen und ohne
Lastverschiebungseffekte", the other price components "stützen sich auf
Daten der aktuellen Anbieter dynamischer Stromtarife. Diese hat die
Bundesnetzagentur in ihrem Monitoring erhoben"; service fees and
guarantees of origin are "ebenfalls im Rahmen des Monitorings erfasst".
Consumer portal (`bnetza-vportal-dynstromtarife`): "Wollen Sie einen
dynamischen Stromtarif abschließen, dann benötigen Sie ein intelligentes
Messsystem." *Caveat*: SMARD's model assumes no behavioural response — it
is the price of an *inelastic* household, the opposite of this study's
object.

### 6.2 Germany — the meter that gates the book

**MsbG** (`msbg-29/30/31/45-gesetze-im-internet`, as in force
2026-09-04). § 29(1): the default metering-point operator must, "soweit
dies nach § 30 wirtschaftlich vertretbar ist", equip with an intelligent
metering system (iMSys) final customers above 6 000 kWh/year (No. 1) and,
**with a control device at the connection point**, customers with a
§ 14a agreement and operators of generating units above 7 kW (No. 2);
§ 29(2) all other cases are optional. § 30 fixes annual price caps (for
§ 14a customers and 7–15 kW units: at most €130 gross, of which €50 to
the user; optional cases: at most €60, of which €30 to the user). § 31
permits an "agiler Rollout" with control and logging functions supplied
by application update "spätestens bis zum Ablauf des 31. Dezember 2025".
**§ 45(1) No. 4**: for the mandatory consumer cases the operator must begin
by 1 January 2025 and equip **at least 20 per cent of all metering points
to be equipped by 31 December 2025**, 90 per cent of those newly to be
equipped between 25 February 2025 and 31 December 2026, 90 per cent in
2027–2028 and 2029–2030, and 90 per cent of all by 31 December 2032;
§ 45(4): "**Die Bundesnetzagentur veröffentlicht auf ihrer Internetseite
regelmäßig unternehmensindividuelle sowie aggregierte Kennzahlen zum
Fortschritt**" — the statutory basis of the K2 instrument. **EnWG § 14a**
(`enwg-14a-gesetze-im-internet`): (3) "Anlagen … zur Speicherung
elektrischer Energie" are controllable consumption devices; (4) once an
iMSys is installed, control must run through the smart meter gateway.
*Caveats*: the quotas are per default operator and per case group, on
"auszustattende Messstellen", not on households with batteries; the
20-per-cent quota refers to mandatory cases only; a household battery
paired with a PV unit above 7 kW or under a § 14a agreement is a
mandatory case, a battery below that with consumption under 6 000 kWh is
optional.

**The rollout Kennzahlen exist and are pinned, unread**
(`bnetza-imsys-rollout-article`, headings only: "Erste halbjährliche
Erhebung 2026", "Ergebnisse der Datenauswertung Q4/2025", and an FAQ on
measures where operators miss the 20-per-cent quota; `bnetza-press-2026-
03-27-aufsichtsverfahren-messwesen`, "Bundesnetzagentur leitet Verfahren
wegen Versäumnissen beim Smart Meter-Rollout ein", title only). Their
values are the first K2 observation.

### 6.3 Germany — the batteries

**Marktstammdatenregister, public units overview, queried 2026-09-04**
(`mastr-json-storage-units-all`, `-in-operation`, `-in-operation-lt30kw`:
the register's own JSON grid endpoint, filter `Energieträger = Speicher`;
each response pinned with its `Total`):

| storage units (Energieträger "Speicher", technology "Batterie" in the first record) | count |
|---|---:|
| all registered | 2 774 462 |
| status "In Betrieb" | 2 734 713 |
| "In Betrieb" and gross power below 30 kW | 2 724 073 |

*Caveats, the register's own* (`bnetza-mastr-statistik`, `bnetza-ee-
statistik-mastr-pdf`): the legal registration deadline is one month after
commissioning and "Nachmeldungen können insbesondere die Werte der letzten
ausgewiesenen Monate noch beeinflussen"; the overview counts *units*, not
households; the 30 kW cut is the market's home-storage convention, not
the register's; the endpoint is undocumented and may change. The
hypothesis in §3 ("well over a million") is replaced by **about 2.7
million operating units under 30 kW**. Separately, the 2025
Monitoringbericht (`bnetza-monitoringbericht-2025-pdf`, table "Strom:
Steuerbare Verbrauchseinrichtungen nach den Festlegungen nach § 14a
EnWG") records **128 475** storage market locations under Module 1 and
867 under Module 2 — batteries that already have a § 14a agreement and
are therefore mandatory iMSys cases (as reported by distribution
operators for the report's data year 2024; "gem. Festlegung
BK8-22/010-A").

### 6.4 Germany — where the monitoring lives

`bnetza-monitoringbericht-2025-pdf` (Bundesnetzagentur and
Bundeskartellamt, published November 2025 per the press page
`bnetza-press-monitoringbericht-2025`; "13. gemeinsamer Bericht" on the
monitoring page; data year 2024 with 2025 developments): chapter "4.
Tarife" (p. 162) contains **Abbildung 93 "Anzahl der Stromlieferanten,
die dynamische Tarife anbieten"** and **Abbildung 94 "Modellierte
dynamische Strompreise"**; chapter "H. Mess- und Zählwesen" (p. 184)
contains Abbildungen 107–112 (metering locations, smart-meter-gateway
use, billing routes, remote-reading technologies, metering investment).
Values under the captions were not read (one sentence of the executive
summary was; see the hindsight guard).

### 6.5 European Union — Article 11

EUR-Lex returned an empty body for every route tried (nine URLs, HTML,
PDF and ELI; `evidence/public-as-of-unavailable.json`). Article 11 of
Directive (EU) 2019/944 is therefore pinned from the UK statute-book copy
(`uk-legislation-eudr-2019-944-art11`, legislation.gov.uk, "Since IP
completion day (31 December 2020 11.00 p.m.) no amendments have been
applied to this version"): (1) "Member States shall ensure that final
customers who have a smart meter installed can request to conclude a
dynamic electricity price contract with at least one supplier and with
every supplier that has more than 200 000 final customers"; (2) full
information on "the opportunities, costs and risks", and regulators
"shall monitor the market developments and assess the risks"; (3)
consent before switching; (4) "For at least a ten-year period …
Member States or their regulatory authorities shall monitor, and shall
publish an annual report on the main developments of such contracts,
including market offers and the impact on consumers' bills, and
specifically the level of price volatility." *Caveat*: the 2024 reform
(Directive (EU) 2024/1711) amended the directive and could not be pinned;
the German fixed-price duty above 200 000 customers inserted in 2025 is
consistent with such an amendment but is not relied on as evidence of
its text. The EU force is used here only as the frame that makes the
German duty non-idiosyncratic; no kill rests on it.

### 6.6 Great Britain — settlement on what actually happened

**MHHS milestones** (`mhhs-key-programme-milestones`, programme site,
read 2026-09-04): **M14, 28 October 2026** — "all Suppliers must have the
systems and services in place to accept MPANs under the new MHHS Target
Operating Model"; from M14 "MPANs cannot be moved back into the Non-Half-
Hourly (NHH) regime on change of supplier"; a non-compliant supplier
"will lose the ability to take on new customers / new MPANs until they
are compliant"; "On 2 September 2026 … PSG confirmed that the required
criteria and M14 decision are on track to be met." **M15, 7 May 2027** —
"all Suppliers must have migrated all MPANs into the new MHHS
arrangements". **M16, 2 July 2027** — cutover "from the legacy 14-month
settlement timetable to the new four-month settlement timetable". The
programme home (`mhhs-programme-home`, undated banner): "50% of all
Industry Meter Point Administration Numbers (MPANs) migrated". Ofgem's
CR055 decision page timed out on 2026-09-04 and is not re-pinned; F006's
pin of the same page (`ofgem-mhhs-cr055-decision-page` in
`F006-who-must-prove-control/evidence/public-as-of-manifest.json`,
fetched 2026-09-03) records approval on 29 November 2024. *Caveat*: the
programme's dates are the programme's; the banner is undated.

**The GB buyer class, sized** (`ofgem-retail-market-indicators`, read
2026-09-04): "There were 17 active suppliers in the domestic gas and
electricity retail markets as of March 2026 … 16 suppliers active in both
gas and electricity and 1 in electricity". `ofgem-state-of-market-retail-
jan-2026-pdf` (Ofgem, January 2026): "In the second quarter of 2025, the
six largest suppliers accounted for 92% of the domestic electricity and
gas markets"; "Smart tariffs remain in early adoption but are growing
rapidly: penetration reached 2.8% of the domestic market by July 2025,
with customers on smart Time-of-Use (ToU) tariffs increasing 68%
year-on-year to 835,000. EV-specific tariffs drove this growth (+84% to
653,000)"; "The Market-wide Half-Hourly Settlement (MHHS) rollout is
expected to increase the number of flexible tariffs in the market
throughout 2026"; "around 8.3% of smart meters are not operating in smart
mode". The market-shares chart page timed out twice (unavailable); the
indicators page names it ("Electricity supply market shares by company:
Domestic (GB)"). *Caveat*: Ofgem's "smart tariff" is not the directive's
"dynamic price contract"; GB has no offer duty, so the GB book forms by
choice, not by statute.

### 6.7 The balancing and dispute machinery (existence only)

- Standard balancing-group contract of the four German TSOs, 2024
  version (`uenb-standard-bilanzkreisvertrag-2024-pdf`), approved by the
  Bundesnetzagentur on 15 February 2024 per the Netztransparenz
  consultation page (`netztransparenz-bilanzkreisvertrag-konsultation-
  2023`); the imbalance price series page (`netztransparenz-rebap`)
  pinned. Contents not read beyond the table of contents.
- Elexon's BSC Change Register page (`elexon-bsc-change-register`): a
  weekly spreadsheet of open and closed modifications.
- Schlichtungsstelle Energie, Tätigkeitsbericht 2025 (`sse-
  taetigkeitsbericht-2025-pdf`): carries a complaint-cause table
  ("Beschwerdegrund (Mehrfachnennung) / Unterkategorie / Anzahl") and a
  section headed "Dynamische Tarife".
- Portfolio managers' pages, **titles and headings only**: Trianel
  ("Portfoliomanagement Strom und Gas": modules incl. "Kalkulation von
  Lastgängen"; "Liefer- und Bilanzkreismanagement": "Bilanzkreismanagement
  für Strom- und Gaslieferanten", "Analyse der Differenzzeitreihe",
  "Beratung bei gesetzlichen Änderungen"); Syneco ("Portfoliomanagement":
  "Energiebeschaffung und Risikoabsicherung", "Alternative zur
  Vollversorgung", "Kundenreporting und REMIT"); EnBW ("Einkauf und
  Beschaffung für Stadtwerke": "Stabiler Strom-Bilanzkreis für
  Stadtwerke"; Energy Factory: "Bilanzkreis- und Fahrplanmanagement",
  "Prognoseservice", "MaBiS (Rolle BKV)", "Portfoliomanagement");
  Vattenfall Energy Trading ("Portfolio Management", "Electricity & Gas
  Balancing Group Management"). A Thüga press release on the RWE–Syneco
  cooperation is pinned unread. **No page shows a price list.**
- Associations: the VKU URL redirected to a generic "Energiewende" page
  (no dedicated dynamic-tariff page found); BDEW's guessed page 404; the
  BDEW statement on the 2025 EnWG bill (`bdew-stellungnahme-enwg-2025-
  themenpapiere-pdf`, 17 October 2025) is pinned, with a section "7
  Festpreisverträge, § 41a Abs. 4-7 EnWG-E" seen in its table of
  contents; the vzbv position paper on dynamic tariffs (1 December 2023)
  is pinned, table of contents read.
- ACER/CEER 2025 retail market monitoring pages pinned (existence only).

**Unavailable** (17, `evidence/public-as-of-unavailable.json`): two
guessed Bundesnetzagentur consumer-portal URLs (404; the correct pages
were found and pinned), the BDEW guessed page (404), the MHHS migration
guessed URL (404; correct page pinned), Elexon's guessed modifications
URL (404; the change register pinned), nine EUR-Lex routes (empty body),
the Elexon TOG meeting-28 page (empty body), Ofgem's CR055 page and the
market-shares chart (timeouts).

## 7. Instrument states — appended by the gate, 2026-09-04 (metadata only)

Checks per v4 §3: 1 existence · 2 population resolution · 3 observability
· 4 earliest observable date · 5 risk-bearing. Guidance P8 applied: the
Bundesnetzagentur's monitoring and the Schlichtungsstelle are free public
functions, so their eligible symptoms are documentary and service-level,
never spend. L15/L16 carried: states are recorded as *direct instrument /
declared proxy / no instrument*, and the two rates (direct measurability;
screenable with direct + proxy) are reported separately in RESULTS.

| # | symptom → series | checks | **state** |
|---|---|---|---|
| **R1** reflexive forecast | (a) portfolio managers' own service descriptions add a dynamic-tariff / flexible-load line: the seven pinned pages (Trianel ×2, Syneco ×2, EnBW ×2, Vattenfall ×2), documentary, undated, no price list | 1✓ 2✓ (the absorber in its own words) 3✓ (presence or absence of the line is observed; absence is weak evidence) 4✓ 5✓ | **eligible now — direct, weak** |
| | (b) suppliers or their associations state that dynamic-tariff load is costly to forecast or balance: BDEW statement 17 Oct 2025; vzbv 2023; Schlichtungsstelle 2025 section "Dynamische Tarife"; GNDEW Begründung (the 2023 objection, dated) | 1✓ 2✓ 3✓ 4✓ 5✓ | **eligible now — direct** |
| | (c) withdrawal / punitive pricing of § 41a tariffs: Monitoringbericht Abb. 93 (count of suppliers offering; annual; 2024 data) resolves "offered", not "priced to deter"; the § 35 No. 10 series (market offer and price volatility of § 41a contracts) first reports in the 2026 Monitoringbericht | 1✓ 2 partial 3 ✗ for Abb. 93; 4 ✗ until ~2026-11 for § 35 No. 10 | proxy only now; **eligible later (2026-11)** |
| **R2** reflexive imbalance | (a) TSO / Elexon rules tightened for price-following load: ÜNB standard balancing-group contract 2024 and its consultation record; Elexon change register (weekly) | 1✓ 2 partial (rules are population-blind unless they name the load) 3✓ 4✓ 5✓ | **eligible now — direct, weak** |
| | (b) imbalance cost share attributable to dynamic-tariff suppliers: reBAP is a publisher-level price with no supplier split; no BSC series splits imbalance by tariff type | 2 ✗ aggregates away | no viable instrument |
| | (c) portfolio managers surcharge or exclude reflexive load: no published price list on any pinned page | 3 ✗ | proxy only (service pages, as R1(a)) |
| **R3** hedging the segment | (a) tariff restructuring across many suppliers within a year: no public series aggregates supplier terms; SMARD's modelled components ("Servicegebühr", "Beschaffungskosten & Vertrieb/Marge") are averages over "aktuelle Anbieter" | 2 ✗ | proxy only (gap: an average markup does not show restructuring) |
| | (b) portfolio managers publish a dynamic-tariff product or advisory line | as R1(a) | **eligible now — direct, weak** |
| | (c) markup / volatility dispersion: § 35 No. 10 series | 4 ✗ until ~2026-11 | eligible later (2026-11) |
| **R4** pairing and export rules | (a) supplier terms add pairing exclusions, export caps or no-grid-charging clauses: GB — Octopus terms pinned in Investigation 010 (versioned, dated: smart-tariff terms, Go v1.6 of 10 Apr 2025, Intelligent Go v2.6 of 16 Feb 2026); DE — the specialists' AGB exist as documents but are incumbent-market evidence and are pinned only at K1 | 1✓ 2✓ (single-supplier resolution) 3✓ 4✓ 5✓ for GB; DE existence unverified before freeze | **eligible now — direct (GB); DE pinned at K1** |
| | (b) consumer bodies or the regulator challenge such clauses: vzbv paper exists (2023); Verbraucherzentrale complaint statistics not located | 1 partial | proxy only |
| | (c) Stadtwerke § 41a tariffs with no export product: no public series enumerates tariff structures across several hundred suppliers | 1 ✗ | no viable public instrument for (c) |
| **R5** interval billing and explanation | (a) MHHS migration slippage concentrated in particular suppliers: programme banner is aggregate; per-supplier migration figures are in governance slides (TOG page returned empty); the M14 consequence ("lose the ability to take on new customers") is dated 2026-10-28 and its per-supplier publication is not assured | 2 ✗ now; 4: 2026-10-28 | proxy only now; **eligible later (2026-10-28, if per-supplier)** |
| | (b) billing complaints on dynamic tariffs at the dispute bodies: Schlichtungsstelle Tätigkeitsbericht (annual; cause table by billing category; a "Dynamische Tarife" section in 2025) | 1✓ 2 partial (the table is by billing cause, not tariff type; the section is narrative) 3✓ 4✓ 5✓ | **eligible now — direct (narrative), proxy (counts)** |
| | (c) billing vendors announce modules | `ProvisionExists`, not strain | not an instrument |
| | (d) suppliers cite billing-system readiness as a reason not to offer: BDEW / vzbv / Schlichtungsstelle, as R1(b) | as R1(b) | **eligible now — direct** |
| **R6** inverter-versus-meter reconciliation | (a) dispute-body categories for metering / settlement data: Schlichtungsstelle cause table (sub-categories not read; whether "Messstellenbetrieb" is split is unknown before the kill) | 1✓ 2 partial 3✓ 4✓ 5✓ | **eligible now — direct, resolution unverified** |
| | (b) dispute-body guidance on inverter-versus-meter evidence: Schlichtungsempfehlungen page exists (not pinned; pinned at K2) | 1✓ 3✓ | eligible now — documentary |
| | (c) metering operators' statements: BDEW, as R1(b) | as R1(b) | eligible now |
| **S1** earnings-claim substantiation | (a) advertising rulings against battery earnings claims: ASA rulings database (public, dated, searchable); Wettbewerbszentrale case reports (public) — neither pinned before freeze, both pinned at K0 if reached | 1✓ 2✓ 3✓ 4✓ 5✓ | **eligible now — direct**; K0 only per §4 |
| | (b) lender covenants in securitisation documents | 1 ✗ (private) | no viable public instrument |
| | (c) consumer-body "up to" warnings: vzbv 2023 exists | 1✓ | eligible now — documentary |

**Best state per function**: R1 eligible now (a, b); R2 eligible now (a);
R3 eligible now (b); R4 eligible now (a, GB); R5 eligible now (b, d); R6
eligible now (a, b); S1 eligible now (a). **No function is quarantined
for lack of an instrument**; the weakness is that most eligible symptoms
are *documentary* (the incumbent's own words) rather than *numeric*, and
the two numeric series that would settle R1(c)/R3(c) arrive with the
November 2026 Monitoringbericht.

**The K2 size bound, declared now.** Before any symptom is read, K2 reads
the Bundesnetzagentur rollout Kennzahlen (pinned, unread) and computes
the ceiling on the German reflexive book as the *intersection* of (i)
households with an iMSys, (ii) households with a battery, (iii)
households on a dynamic tariff. The public series give (i) from the
rollout page, (ii) from the register count above, and (iii) only from
the 2026 Monitoringbericht; until then (iii) is bounded above by (i). If
(i) is small against 2.7 million batteries, falsifier F2 fires whatever
the incumbents say.

**Hindsight guard.** In locating and pinning sources the following
values were seen and are recorded so that they cannot later be presented
as K2 findings; K2 must cite the pinned documents. From search-engine
summaries (unpinned, not evidence): a 23.3 % mandatory-case quota at
Q4 2025; about 3.09 million iMSys installed at 31 December 2025 (5.5 % of
all metering points); 77 supervisory proceedings; about 540 000
installations in 2024 and nearly two million in 2025; "50 % of industry
MPANs migrated by early August 2026"; MHHS data as 7.58 % of daily SVA
volumes in May 2026; "Trianel manages more than 70 procurement
portfolios"; Syneco "assumes … balance group and schedule management,
forecasts … billing"; EnBW "top-down forecasts of end-customer demand,
24/7 emergency support"; home storage "over one million", 561 000 new
units in 2024, 7.255 GWh added in 2025; ACER: fixed or regulated
contracts dominate households in 15 Member States. From pinned documents
while extracting metadata: Monitoringbericht 2025 executive summary,
"Die Zahl der Stromlieferanten mit einem dynamischen Tarif lag 2024
bereits bei 412"; Schlichtungsstelle 2025, "die Einführung von
dynamischen Tarifen sowohl mit Umsetzungsschwierigkeiten auf Seiten der
beteiligten Unternehmen als auch mit Verständnisproblem[en] auf Seiten der
Verbraucher verbunden ist", and three cause-table counts (2 010 disputed
billing; 970 billing periods; 1 763 other billing disputes).

## 8. Freeze — 2026-09-04

Nothing above this line is edited after this commit. The digest of this
file at the freezing commit is the study's identity.

**Kill order.** **K0** on R1–R6 and S1, in that order, from the pinned
statutes and rules plus dated primary evidence of spend, pinned in a
`kills` manifest. Then **K1** for every K0 passer among R1–R6, by
ascending cost of observation: **R2** (the balancing-group contract and
the portfolio managers' pages, already pinned) → **R5** (the
Schlichtungsstelle report; billing vendors' public product pages) →
**R6** (the same report; the Schlichtungsempfehlungen page) → **R1 / R3**
(the portfolio managers' pages read in full; association statements;
then the Kraken licensees' own releases and the specialists' own product
pages, pinned at that point — this is where the P6 question "has the job
already left the incumbent, and when?" is answered) → **R4** (the
specialists' German terms, pinned; the 010 Octopus terms). **K2** runs
first on the size bound (rollout Kennzahlen, then the register count),
then on the eligible-now symptoms in the same function order, quoting
each source's caveats. **K3** only for `measured strain`. **S1**: K0
only, unless every one of R1–R6 is killed, in which case S1 runs K1–K3.

**K0 evidence classes** (v4 §5). **A** is expected on its face for R1–R3
in Germany (suppliers pay named portfolio managers; a licensee pays
Kraken) and must be shown from a named contract, filing or release, with
*recurring* recorded. **C** is expected from the pinned text: § 41a(2)
(offer, from 1 January 2025), § 41a(6)–(7) (information and summary),
the balancing-group contract (schedule and forecast duties on the
balancing-group responsible party), MHHS M14/M15 (28 October 2026 /
7 May 2027) and BSC imbalance settlement, § 35 No. 10 (on the regulator,
not the supplier). K0 must say, per function, whether the obligation
compels *the function* or only *an outcome that the function would
serve*; a function whose only class-C support is the offer duty itself
is recorded as **C-weak**, because § 41a compels an offer, not a book.
**B** requires an identifiable owner (a Stadtwerk's or specialist's
trading, forecasting or product function) shown from a dated primary
(annual report, job specification, procurement notice).

**"Late", defined now.** If K1 finds the function performed in-house by
Kraken or by the specialist suppliers with a dated public statement from
2023–2025, and the portfolio managers' pages do not name it, the verdict
is `already externalised to the specialists (late, date D)` — not
`measured stable`. If the portfolio managers name it as an included
service, the verdict is `absorbed successfully` and **F1 fires**.

**Falsifiers, restated against pinned text.**
- **F1** — *absorbed*: the portfolio managers and Kraken already price and
  manage reflexive load as a line in existing contracts. Test: the pinned
  service pages read in full; the Thüga–RWE release; the licensees'
  releases; any Stadtwerk annual report naming its portfolio manager's
  scope. Fires if a dynamic-tariff or flexible-load forecasting and
  balancing service is named as included, or if Kraken's licence is shown
  to carry it.
- **F2** — *too small*: the reflexive book stays too small to matter
  through 2028 because the iMSys rollout caps dynamic-tariff take-up.
  Test: the rollout Kennzahlen against the 2.7 million register count and
  the § 45 quotas (20 % of mandatory cases by end-2025; 90 % of new
  mandatory cases 2025–2026 and 2027–2028). Fires if the number of
  households that *can* hold a dynamic tariff in 2028 is an order of
  magnitude below the number of batteries, and the mandatory-case
  definition does not pull batteries in.
- **F3** — *never forms*: suppliers comply with § 41a by offering dynamic
  tariffs priced or structured to be unattractive. Test: association and
  dispute-body statements (eligible now); the SMARD component data; the
  specialists' and any Stadtwerk's published § 41a tariff terms pinned at
  K1; the § 35 No. 10 series from November 2026. Fires if the pinned
  terms show the book being kept off the supplier's balance by design
  (no export product, no battery pairing, markups that make the tariff
  dominated) across the buyer class, not only at the specialists.

Any of the three fires the study; the honest output is then a described
problem, as F006 ended.

**What is scored.** A single mystery, not a batch: the funnel is
reported per function (6 generated + 1 rider → K0 → K1 → K2 → K3), with
L16's two instrument rates (direct; direct + proxy). No threshold is
declared; the three propositions (problem coming; buyer compelled;
existing solutions inadequate) are earned separately or the honest
output is a described problem. Publication waits for the sponsor's seal.
