# C4 kill record — BESS degradation and warranty verification across portfolios

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-26, ninth in the frozen kill order (researched concurrently
with C8, C10, C9, C2; recorded in order).
**Verdict**: **absorption strain plausible but not measured → downgraded.**
The most diagnostic instrument (disputes) is private by construction; the
most observable one (insurer pricing) measures a peril the function does
not touch — insurers exclude degradation rather than price it; the one
named GB purchase is in-house absorption by an asset manager.

Research performed by a background agent under the v3 kill discipline; the
record below is its report, unedited except for this header and light
trimming of the source list.

**Tooling caveat up front:** the session's WebSearch budget was exhausted
before the first query. Evidence was gathered through direct fetches of
known URLs, the energy-storage.news site search, a reader proxy, and
`pdftotext` on two GB fund annual reports (~45 tool calls). Stopped because
the verdict stabilised, not because of budget.

## 1. Existing job — who performs the function today

- **OEM / integrator warranty teams.** Capacity and degradation guarantees
  are written at the DC battery terminals against throughput/cycle/
  temperature/SOC envelopes; annual capacity testing is "a negotiated point
  whether developer or supplier is responsible" (Norton Rose Fulbright, Aug
  2022). The integrator holds the data chain and the LTSA.
- **Owner's engineers / independent engineers.** Engaged at financing and
  commissioning: lenders expect "a robust review from the independent
  engineer on capacity degradation" (Morgan Lewis, Mar 2026); DNV, Bureau
  Veritas, Intertek CEA sell OE and factory/handover test verification.
  Point-in-time, not continuous.
- **Asset managers in-house.** Gore Street Capital runs its own monitoring
  platform on a "majority" of projects, has integrated ACCURE, and signed
  "a framework agreement with a second platform to standardise data
  capture" (GSF Annual Report FY to Mar 2025); Gresham House's manager
  reports in-house technical/commercial management.
- **Specialist analytics vendors.** TWAICE (warranty/performance-guarantee
  tracking), ACCURE ("Warranty Tracker", Jan 2025), PowerUP, Peaxy;
  claims-management consultancies.
- **Insurers' own engineering.** Insurers verify fire mitigation and BMS
  monitoring; they do not verify degradation because they do not cover it
  (§3).
- **Regulator-adjacent check (GB).** Capacity Market Extended Performance
  Testing: units with long-term agreements must demonstrate extended
  performance at least one winter day every three years or face
  termination. An independent capacity check that exists regardless of OEM
  SOH reporting.

## 2. Eligibility of the frozen instruments (before numbers)

- **Publicly reported warranty disputes.** GB BESS supply contracts route
  disputes through confidential arbitration. The fraction that can surface
  publicly is small: listed-fund disclosures if material, OEM insolvency
  proceedings, High Court claims that escape arbitration. Well under 10% of
  real disputes would be visible, biased toward insolvency-driven cases.
  **The instrument can confirm strain but cannot refute it.**
- **Insurer commentary.** Marketing-prone. Separation rule applied: count
  only (i) statements of what is and is not covered, (ii) rate movements
  with a number, (iii) capacity withdrawals/entries with dates, and (iv)
  insured parties' own reports of premium change in audited documents.
  Advisory pieces and vendor-authored articles count as "provision exists"
  only.
- **Third-party assurance spend.** No public GB dataset. Observable: named
  purchases and vendor financing rounds. ProvisionExists ≠
  ProvisionPurchased ≠ RepeatPurchase applied explicitly in §5.

The instrument set can detect *insurer repricing* and *named assurance
purchases* reasonably well; it can detect *dispute growth* only if large or
insolvency-driven.

## 3. Frozen forcing observation — results

### 3a. Insurance market commentary, in date order

| Date | Source | Statement (own words) | Class |
|---|---|---|---|
| Feb 2024 | GCube, "Batteries Not Excluded" (via T&D World) | BESS failures "increased tenfold since 2016"; ">50% of BESS failures occur within the initial two years"; "their comfort in supporting coverage availability remains uncertain". | Coverage/appetite |
| 26 Mar 2024 | NARDAC | USD 50m per-location capacity from "eight A-rated Lloyd's syndicates"; "older, and typically smaller, battery projects in the U.S. and the U.K. are deprioritised, leaving operators with punitive terms and conditions." | Capacity entry |
| 30 Apr 2024 | energy-storage.news | Gore Street uses ACCURE analytics to obtain improved terms from HDI Global via PIB on Stony (80 MW) and Lower Road (10 MW); driver stated as thermal-runaway safety, not degradation. | Insured-party report |
| 3 Nov 2025 | Marsh | Degradation listed as a risk; performance degradation cover "not confirmed offering". | Advisory |
| 6–7 Nov 2025 | Oliver Litterick, TMGX (ex-GCube) | "We do not cover degradation. There has to be damage, and degradation would not be defined as damage." "We have seen a shift in the levels of indemnification under the OEM's warranties" — cover "decreased and in some cases is barely above the deductible". | Coverage boundary + OEM-warranty observation |
| 17 Jun 2026 | Willis (WTW) Renewable Energy Market Review (via Insurance Business) | "Pricing reductions of between 20% and 30% are available for Tier 1 risks"; "Tier 2 … up to 10% to 15%"; "credible performance data increasingly required before insurers commit capacity". | Rate movement |
| 24 Jul 2026 | Insurance Business UK (Allianz UK) | "A number of insurers have restricted or withdrawn capacity from the sector following battery fires"; Allianz UK expanding mid-market BESS underwriting. | Capacity movement |
| Apr 2026 | Gresham House Energy Storage Fund plc Annual Report 2025 (audited) | "securing significantly lower insurance costs across the portfolio … the cost per MW to insure the projects should decrease." | Insured-party report |
| Jul 2025 | Gore Street Energy Storage Fund plc Annual Report FY25 | Analytics-led asset management "has resulted in a material reduction in insurance premiums". | Insured-party report |

Performance/degradation cover as a *product*: Munich Re launched a
long-term battery performance plan in March 2019, and in Oct 2023 agreed
warranty reinsurance for Hithium "against performance degradation and the
risk of defects, with coverage of up to 15 years"; Altelium (UK MGA,
Lloyd's Lab 2022; 1–10 employees) offers warranties and analytics on
battery health; a UK broker lists "performance and degradation extensions
where the warranty profile supports it". No GB take-up data found.

Reading: insurers have not "priced differently" for degradation; they have
*excluded* it by construction and are pricing the fire/damage peril, where
GB rates are falling for well-engineered portfolios. The one genuine
movement relevant to C4 — OEM warranty indemnification shrinking — shifts
risk to owners, not to insurers.

### 3b. Publicly reported warranty / performance disputes 2023–2026

- **GB: none found.** No named GB BESS warranty or degradation dispute in
  trade press, case-law prompts, law-firm commentary, or the two listed
  funds' annual reports. Both GB legal notes are *anticipatory*: Burges
  Salmon (1 Oct 2024) lists "battery degradation" among dispute areas but
  cites no cases; KYOS/Simon Ede (summer 2026) predicts disputes and names
  none. GRID (Dec 2025) and GSF (Mar 2025) mention warranty claims only in
  the generic counterparty-credit-risk note.
- International, GB-relevant-OEM filter: Powin Chapter 11 (9 Jun 2025) —
  no GB exposure identified, excluded. US practitioner panel (15 Apr 2026):
  "The industry isn't seeing a wave of chemistry-based warranty claims yet,
  instead, we're seeing systems that can't hit their nameplate discharge",
  with "finger-pointing between cell manufacturers, OEMs, and integrators".
- Structural drift (Intertek CEA, Jun 2026, vendor-adjacent): end-of-life
  SOH thresholds moving "from 70% in older contracts to 65%, and in some
  cases 60%"; "the MSA tests performance at the DC battery terminals, while
  the LTSA requires reporting at the medium- or high-voltage
  interconnection" so "the developer cannot track the degradation curve
  from beginning to end of life"; "6% of battery energy storage systems
  initially fail their capacity test at the factory".

### 3c. Third-party assurance spend / mandates

- **Provision exists:** TWAICE; ACCURE "Warranty Tracker" (Jan 2025, "over
  5GWh" supported); Peaxy; DNV owner's engineering. TWAICE raised €24m EIB
  venture debt (6 Feb 2026) — a financing signal, not GB spend.
- **Purchased in GB (named):** Gore Street — ACCURE on UK sites from 2024,
  a second data-standardisation platform in 2025, and an in-house platform
  with "live tracking of warranties". A second GB user (BW ESS) inferred
  from a vendor authors page; no announcement located.
- **Mandates:** none continuous. Lender IE review is at financing; CM EPT is
  triennial and regulatory; Willis notes performance data "increasingly
  required before insurers commit capacity" (unquantified).
- **Repeat purchase / spend growth:** no public GB figure.

## 4. Contradicting evidence

- Insurance cost is **falling** for the two largest GB listed portfolios and
  Willis reports 20–30% reductions for Tier 1 BESS in 2026. The predicted
  symptom "insurers price differently" is not observed in the direction the
  row implies.
- Degradation is a **defined exclusion** in property-damage cover, so there
  is no channel through which degradation verification demand reaches
  insurers' pricing at all; performance-warranty products exist with no GB
  uptake evidence since 2023.
- The verification function is being **absorbed in-house plus one vendor**
  — textbook absorption by the incumbent the row named.
- GB regulation already supplies a periodic independent capacity check (CM
  EPT), lowering the marginal need for private continuous verification.
- No GB public dispute in three years despite ~10 GW online by June 2026.

Not contradicting, but weakening the row: "OEM SOH reporting standardised"
is *not* supported — contract measurement points and thresholds are
diverging. A strain mechanism stays alive; it has not produced an
observable symptom in GB.

## 5. Verdict: plausible but not measured → downgraded

1. *Warranty disputes rise* — not observable by construction; public
   channel shows zero GB cases; statements are anticipatory. Cannot be
   scored either way.
2. *Insurers price differently* — measured, and the evidence runs against
   the row: degradation is excluded, not repriced; GB premiums fell in
   2025–26. The one movement (OEM indemnification shrinking) transfers risk
   to owners, which strengthens the *need* but is absorbed by the owner.
3. *Third-party assurance spend grows* — ProvisionExists: yes.
   ProvisionPurchased in GB: one named owner, with a safety/insurance motive
   rather than warranty verification. RepeatPurchase / spend series: no
   public data.

Not killed as *stable*: the mechanism (thresholds drifting to 60%,
measurement-point mismatch, shrinking OEM indemnity, rising cycling) is
real and the strongest instrument is blind. Not *strain evidenced*: every
observable instrument shows either comfortable absorption (insurance) or a
single purchase (assurance). Under v3, downgraded. The cheaper falsifier
that would resolve it — GB listed-fund and Companies House disclosures of
warranty settlements or augmentation brought forward earlier than modelled
— is outside the frozen observation and is noted, not run.

## 6. What this says about the generator

C4 was built on a symptom set in which the *most diagnostic* instrument
(dispute volume) is structurally private and the *most observable*
instrument (insurer pricing) measures a peril the row's function does not
touch. The generator conflated "insurers care about BESS" with "insurers
price degradation verification", when insurers have defined degradation out
of the covered peril; a one-line coverage check would have caught that
before any thesis-building. Generalisation: when a predicted symptom is a
third-party pricing signal, first ask *whether that third party bears the
risk the function manages at all*. The row's incumbent model (in-house
asset managers) was right — the evidence shows exactly that absorption
happening — while its symptom model was wrong.

## 7. Sources (accessed 2026-08-26; labels [V] fetched, [S] snippet/secondary, [N] not retrievable)

[V] T&D World 21 Feb 2024 (GCube summary); Enlit World 19 Apr 2024;
Tamarindo 29 Feb 2024; pv magazine 26 Mar 2024 (NARDAC);
energy-storage.news 30 Apr 2024 (Gore Street/ACCURE/HDI), 3 and 7 Jan 2025
(ACCURE), 15 Apr 2026 (US panel), 26 Mar 2026 (Gore Street), 3 and 8 Jun
2026 (Intertek CEA), 12 Jan and 6 Feb 2026 (TWAICE), 20 Aug 2026
(Envision); Marsh en-gb 3 Nov 2025; ESS News 6 Nov 2025 and 19 Sep 2025;
pv magazine 7 Nov 2025; Insurance Business 17 Jun 2026 (WTW, secondary)
and 24 Jul 2026 (Allianz UK); Utility Dive 12 Mar 2019 (Munich Re);
Reinsurance News 26 Oct 2023 (Munich Re/Hithium); Lloyd's Lab Altelium
page; GMG and PIB broker pages; Gresham House Energy Storage Fund plc
Annual Report 2025 (Apr 2026, pdftotext); Gore Street Energy Storage Fund
plc Annual Report FY25 (pdftotext); DNV 27 Apr 2021; Norton Rose Fulbright
17 Aug 2022; Peaxy Dec 2025; Morgan Lewis Mar 2026; Burges Salmon 1 Oct
2024; KYOS summer 2026; Modo Energy 14 Aug 2024 (CM EPT).
[S] RTO Insider 25 Feb 2024 (paywall); Allianz Tech Talk vol. 26 landing;
Powin Chapter 11 sources (excluded as non-GB); Modo LinkedIn Sept 2024
snippet; LawGratis arbitration blogs (confidentiality point only).
[N] GCube report PDF; WTW originals (403); Munich Re product pages; TWAICE
customer pages; Businesswire; Modo GB degradation study (paywalled).
