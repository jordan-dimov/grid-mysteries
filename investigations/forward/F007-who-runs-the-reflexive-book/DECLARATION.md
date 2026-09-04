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
