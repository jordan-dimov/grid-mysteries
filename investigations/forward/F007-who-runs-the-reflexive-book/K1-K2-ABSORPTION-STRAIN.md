# F007 — K1 absorption and K2 strain, six functions in the frozen order

**Frozen order**: size bound first, then R2 → R5 → R6 → R1/R3 → R4.
Verdicts carry their reason (v4 §6). Every quotation is from a pinned
artefact; the source's own caveats are quoted beside every number (P7).

## K2, first: the size bound on the German reflexive book

Declared at freeze: the book is bounded by the intersection of (i)
households with an intelligent metering system, (ii) households with a
battery, (iii) households on a dynamic tariff.

| term | value | source and caveat |
|---|---:|---|
| (i) iMSys installed, all cases, 31 Dec 2025 | **3 094 346** (5.5 % of all metering locations) | `bnetza-imsys-rollout-article`: "Betrachtet man die Einbauquote aller Messlokationen in Deutschland … liegt diese für intelligente Messsysteme bei 5,5 Prozent"; based on "insgesamt 866 Rückmeldungen. Hier sind wettbewerbliche Messstellenbetreiber enthalten, sofern eine Meldung abgegeben wurde" |
| (i′) mandatory cases (6–100 MWh and § 14a devices), 31 Dec 2025 | **1 095 715 of 4 709 487** (23.3 %) | same page: "Die Daten zum Pflichtrollout basieren auf der Erfassung von 813 grundzuständigen Messstellenbetreibern"; the 20 % quota "bezieht sich ausschließlich auf verpflichtenden Einbaufälle" |
| by operator size | > 500 000 locations: 27.1 % (19 operators); 100–500 k: 19.7 % (66); 30–100 k: 17.5 % (129); < 30 000: **14.6 %** (599) | same page: "Da es sich um eine Durchschnittsbetrachtung handelt, ist nicht ausgeschlossen, dass z. B. einzelne, kleine Messstellenbetreiber auch deutlich höhere Quoten aufweisen" |
| enforcement | **77 proceedings** opened 27 March 2026 | `bnetza-press-2026-03-27-aufsichtsverfahren-messwesen`: "Betroffen hiervon sind vor allem kleinere und mittelgroße Unternehmen"; "Weitere Aufsichtsverfahren werden nun sukzessive eingeleitet"; enforced "über Zwangsgelder" |
| (ii) battery units in operation, < 30 kW, 4 Sep 2026 | **2 724 073** | `mastr-json-storage-units-in-operation-lt30kw`; units, not households; one-month registration lag |
| (ii′) batteries with a § 14a agreement (mandatory iMSys cases) | **128 475** + 867 | `bnetza-monitoringbericht-2025-pdf`, § 14a table, data year 2024, as reported by distribution operators |
| (iii) households on a dynamic tariff | **unmeasured** | first public series: the § 35 No. 10 monitoring, expected in the November 2026 Monitoringbericht |
| suppliers offering a dynamic tariff | 412 in 2024 (90 in 2023, 52 in 2022, 10 in 2021) | `bnetza-monitoringbericht-2025-pdf`, Abbildung 93; the regulator's survey; 2025 not yet reported |

**Reading.** Today the German book cannot exceed about 3.1 million
metered households in total and about 1.1 million in the case group that
contains § 14a batteries; against 2.7 million battery units that is a
binding constraint but not an order of magnitude, and the § 45 quotas
(90 % of new mandatory cases in 2025–26 and 2027–28) let the
intersection reach the high hundreds of thousands by 2028. The
bottleneck is real and is now being enforced against small default
operators; the specialists route around it by installing their own
meters ("Den Smart Meter installiert Octopus Energy", `octopus-de-
intelligent-octopus-newsroom`; "Ein Smart Meter – Wir schenken dir die
Installation", `tibber-smart-battery`; Osnabrück's customer-wish rollout
at "100 Euro plus 30 Euro jährlich", `stw-osnabrueck-blog-zwischenbilanz-
2025-08`). **F2 does not fire on (i) ∩ (ii); (iii) is unmeasured until
November 2026.** GB: "50% of all Industry MPANs migrated" (`mhhs-
programme-home`, undated banner); M14 "on track" per the Programme
Steering Group on 2 September 2026; smart time-of-use customers 835 000
at July 2025, 2.8 % of the domestic market (`ofgem-state-of-market-
retail-jan-2026-pdf`). No GB size falsifier fires.

## R2 — reflexive imbalance

**K1 absorber**: the balancing-group responsible party — for most
Stadtwerke a portfolio manager (Trianel: "mehr als 200 gemanagten
Bilanzkreisen"; EnBW Energy Factory: "Bilanzkreis- und
Fahrplanmanagement", "Top-Down-Prognose des Endkundenbedarfs"; Vattenfall:
"Schedule nomination and renomination … Closing of open balancing group
positions in the day-ahead and intraday market"), for the specialists
themselves. **What the pinned tariffs say about the price the load
follows**: Stadtwerke Aschaffenburg — "Der Einkaufspreis des Stroms wird
bei einem dynamischen Stromtarif vom Lieferanten 1:1 an Sie verrechnet",
"Trading Modality: Auction, Auction Name: SDAC" (the day-ahead coupling);
Stadtwerke Solingen — "Verbrauchspreis für Beschaffung (Spotmarkt)";
Oerlinghausen — "Dynamischer Spotmarktpreis … entspricht den
Spotmarktpreisen der Stromhandelsbörse EPEX Spot"; Osnabrück — "Der
Tarif Strom dynamisch orientiert sich am Day-Ahead-Spotmarkt. Für jede
Stunde des Folgetags wird dort ein eigener Strompreis festgelegt";
1KOMMA5° — "Die Börsenstrompreise reichen wir 1 zu 1 an dich durch";
Octopus Germany — "15-minütigen Preisinfos nah dran am Börsenstromtarif".
**Consequence for the book**: on a § 41a pass-through tariff the price
the batteries respond to is the day-ahead auction's, fixed before the
balancing-group party nominates its schedule; the supplier does not set
it. The position is therefore not reflexive to the supplier — it is a
*response-forecast* problem against a known price, exactly what a
day-ahead forecast team is paid for ("Tägliche Day-Ahead-Analyse durch
das Prognose-Team", Trianel). Genuine reflexivity exists only where the
supplier sets its own price *and* moves the devices (Intelligent
Octopus's fixed price plus control; Tibber Smart Battery; Heartbeat AI;
Enpal.One), and there the loop is closed by control, not by forecasting.
**Already externalised?** No: the function has stayed with the
balancing-group party since the contract regime began; what left is the
*control* book, to the specialists (below). **K1: absorbed successfully.**
**K2 on the eligible-now instrument** (rules for price-following load):
the 2024 standard balancing-group contract contains no provision naming
dynamic tariffs or price-following load (zero occurrences of
"dynamisch"; forecasting duty generic); Elexon's change register page
pinned, spreadsheet not opened. `measured stable (weak — a rule-text
null)`. **Falsifier F1 fires for R2.**

## R5 — interval billing and explanation

**K1 absorbers**: the billing vendors, who market the function to the
buyer class as a compliance product (Wilken: "Dynamische Tarife –
Pflicht für Energieversorger"; Schleupen: "Continuous Billing bereit für
dynamische Tarife", Stadtwerke Brühl and Rosenheim named as customers;
cortility for SAP), and in GB ENSEK and Gentrack for MHHS. **Already
externalised**: yes, to vendors, as an ordinary billing-system release —
dated by the vendors' "ab dem 1. Januar 2025" framing. **What the bill
explains**: cortility's SAP solution bills "ein Durchschnittspreis …
anhand des individuellen Verbrauchs und dem zugeordneten Preisprofil" —
an average price, not 35 040 lines; no vendor page offers an explanation
of what a battery earned against a permitted pairing. **K1: absorbed by
assignment (vendors), at the standard the law demands.**
**K2 on the eligible-now instrument** (`sse-taetigkeitsbericht-2025-pdf`,
section "Dynamische Tarife"): "die Einführung von dynamischen Tarifen
sowohl mit Umsetzungsschwierigkeiten auf Seiten der beteiligten
Unternehmen als auch mit Verständnisproblem[en] auf Seiten der
Verbraucher verbunden ist"; "Bei der tatsächlichen Umsetzung des Einbaus
sowie des ordnungsgemäßen Betriebs der Messstelle sowie der Übertragung
der Messwerte an die Lieferanten sind jedoch zum Teil noch erhebliche
Bearbeitungs- und Kommunikationsprobleme erkennbar"; "Häufig sind in
solchen Tarifen maximal für den ersten Belieferungsmonat bestimmte
Fixpreise festgelegt". *Caveat*: narrative, no count; the cause table
has no dynamic-tariff category and is by multiple mention. The strain the
dispute body sees sits at the **metering-operator-to-supplier data
chain**, not in billing. `measured strain (weak — acknowledged by the
dispute body; located upstream of the function)`. Proceeds to K3.

## R6 — inverter-versus-meter reconciliation

**K1 absorber**: the supplier's complaints route and the Schlichtungs-
stelle, with the meter as the legal measure; no party is compelled to
reconcile to an inverter log. **K1: absorbed at the standard demanded
(answer the complaint); the higher standard is unforced.** **K2**: the
cause table aggregates the symptom away ("Streitiger Verbrauch",
"PV-Anlagen 1.256", "Zählerstand 1.926" — none distinguishes an
inverter-versus-meter dispute). `unmeasured — instrument ineligible`,
recorded against the gate: check 2 (population resolution) was marked
"unverified" and fails.

## R1 and R3 — reflexive forecast and segment hedge

**K1**: as R2 established, the price the segment follows is the
market's; the forecast function is the balancing-group party's ordinary
day-ahead work, and the residual to hedge is the imbalance term plus the
supplier's fixed components against a volume that moves. Absorbers: the
portfolio managers' forecast and risk services (Trianel's tools "damit
Sie für Ihr Portfolio eigenständig Prognoselastgänge für den Stromabsatz
erstellen und bepreisen können"; Syneco's "Risikoprämien in volatilen
Märkten kalkulierbar"; EnBW's "KI-gestützte Portfolioprognose").
**The P6 question — has the job left the incumbent, and when?** The
*control* book — setting a price and moving the devices against it —
sits with the specialists and Kraken licensees, dated from their own
releases: Kraken licences to E.ON, EDF Energy and Origin "previous deals"
before 12 October 2023 (`kraken-press-tokyo-gas`), Tenaska 7 June 2023,
Tokyo Gas 12 October 2023, Plenitude and National Grid US by 18 September
2025 (`kraken-press-spin-off-2025-09`); Enpal.One 25 March 2024;
Intelligent Octopus Germany 6 May 2025; Tibber's Smart Battery page
undated with "Grid Rewards" for 2026; 1KOMMA5°'s customer evaluation
"Anfang Mai 2024 bis Ende August 2024". **That book never belonged to the
Stadtwerke** — their § 41a tariffs do not control anything — so this is
not lateness against an incumbent but a category the specialists built
between 2023 and 2025. **K1: absorbed successfully (the market-price
forecast) / already externalised to the specialists, 2023–2025 (the
control book).** **K2** on R1(a)/R3(b): no portfolio-manager page names a
dynamic-tariff or flexible-retail-load service — `measured stable (weak
— a marketing-page null)`. On R1(b): the only dated supplier-side
statement of difficulty is the 2023 bill's own recital of the industry's
objection ("geringe Margen und hohe Kosten bei einer geringen Zahl von
Kunden mit intelligenten Messsystemen", `bt-drucksache-20-5549-gndew-
pdf`); the BDEW statement of 17 October 2025 addresses § 41a only on the
fixed-price and information duties (section 7); the vzbv frames dynamic
prices as "kurzfristig vom Lieferanten festgelegt" (2023) — contradicted
by the pinned terms, which pass the auction through. Stadtwerke
Osnabrück, 22 August 2025: "Die ersten Rückmeldungen sind positiv",
"Nur wer seine Stromverbräuche gezielt verschieben und anpassen kann,
profitiert wirklich von diesem Tarif", "Wir stehen am Anfang einer
Entwicklung". `measured stable`. On R1(c) (withdrawal or punitive
pricing): the five pinned Stadtwerke products are genuine pass-throughs
with a visible fixed layer — Oerlinghausen "Basispreis 22,89 ct/kWh"
plus spot, "Grundpreis 12,90 €/Monat"; Aschaffenburg "Umlagen,
Dienstleistungs- und Vertriebskosten sowie ein verbrauchsunabhängiger
Grundpreis und Messpreis", with the warning "Finanzielle Risiken aufgrund
hoher Börsenstrompreise tragen Kund*innen in vollem Umfang" — and Enpal's
own page says the same of every dynamic tariff: "Selbst wenn der
Börsenpreis auf null fällt, bleiben rund 15–17 Cent/kWh an fixen Kosten
bestehen". **Falsifier F3 does not fire on the pinned terms**; take-up
is `eligible later (2026-11)`.

## R4 — pairing and export rules

**K1**: split at K0. For the specialists the rules are product design
performed in-house (Octopus GB's terms, 010; Intelligent Octopus
Germany's single fixed price with control; Enpal's marketing of the
surplus). For the Stadtwerke class there is no rule to write: the export
is the state feed-in tariff. **K1: already externalised to the
specialists (2024–2026), and unforced elsewhere.** **K2** on the GB direct
instrument: the pinned Octopus terms (smart-tariff terms; Go v1.6 of
10 April 2025; Intelligent Go v2.6 of 16 February 2026) carry the pairing
exclusions 010 found — the incumbent maintaining its own rules, not a
symptom of strain. `measured stable`.

## Funnel after K1/K2

| stage | count | functions |
|---|---:|---|
| generated | 6 (+1 rider) | R1–R6; S1 |
| K0 buyer-real | 6 (R4 split) + S1 | A: R1, R2, R3, R5; B: R4 (specialists); C-weak: R6; S1 (C) |
| reached K1 | 6 | R2, R5, R6, R1/R3, R4 |
| K1 absorbed successfully | 3 | R2 (balancing-group party), R1, R3 (the price is the market's) |
| K1 absorbed by assignment | 1 | R5 (billing vendors), input chain strained |
| K1 absorbed at the demanded standard, higher standard unforced | 1 | R6 |
| K1 already externalised (late) | the control book of R1/R3/R4 | specialists and Kraken licensees, 2023–2025 |
| K2 measured stable | 4 | R1, R2, R3 (weak nulls), R4 |
| K2 measured strain | 1 | R5 (weak; upstream of the function) |
| K2 unmeasured — instrument ineligible | 1 | R6 |
| K2 eligible later (2026-11) | R1(c)/R3(c) take-up and markup series | — |
| proceeding to K3 | 1 | R5 |
