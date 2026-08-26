# C9 kill record — independent verification of granular/temporal clean-energy claims

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-26, eighth in the frozen kill order (researched concurrently
with C8, C10, C4, C2; recorded in order).
**Verdict**: **absorption strain plausible but not measured → downgraded.**
The frozen instrument cannot see assurance spend; the administration
proxies it can see show a mild, transient strain that tracks an IT
migration, not certificate volume; the temporal forcing variable slipped
between freeze and test.

Research performed by a background agent under the v3 kill discipline; the
record below is its report, unedited except for this header.

**Retrieval limitation, stated up front.** The session's WebSearch budget
was exhausted before the first C9 query. Everything below comes from direct
fetches of Ofgem, gov.uk, GHG Protocol and EnergyTag pages, `pdftotext` on
Ofgem PDFs, and the RER public CSVs. No auditor, Big-4 or trade-press
statements on assurance demand could be retrieved; no instrument was
substituted.

## 1. Existing job — who verifies clean-energy claims in GB today

- **Ofgem** administers REGO for DESNZ (GB) and the NI Utility Regulator,
  issuing one certificate per MWh from accredited stations, running a
  technical audit programme "primarily to guard against fraud", and
  operating the register that suppliers' Fuel Mix Disclosure (FMD) claims
  are checked against. The scheme charges **no fees** (REGO guidance v4.0,
  9 Mar 2026); its administration cost is funded by DESNZ and is **not
  published** separately.
- The register moved to the **Renewable Electricity Register (RER)** on 13
  May 2025, "launched as a public beta with a baseline level of
  functionality".
- **Granular/hourly**: no Ofgem or DESNZ hourly-REGO workstream was found.
  DESNZ's CPPA call-for-evidence response (7 Jul 2026) records that
  "several respondents called for reform of the … REGO scheme … including
  time-matched certificates" — no commitment, no dates. The GB hourly
  products that exist (TotalEnergies UK; Ecotricity "Real Time REGOs", 17
  Jun 2025) are supplier products built on **Granular Energy**, an
  EnergyTag-accredited *issuer*; EnergyTag's accredited list has no UK
  registry or verifier, and neither product page names an independent
  verifier or publishes volumes.
- **Financial auditors**: Scope 2 assurance sits inside sustainability
  assurance (ISAE 3000 / CSRD / ISSB), but hourly matching is not in any
  adopted standard yet. GHG Protocol's Scope 2 consultation ran 20 Oct 2025
  – 31 Jan 2026; GHGP's 29 Jul 2026 update says it is "exploring multiple
  reporting approaches", with "an integrated public consultation planned
  for Q2 2027". EnergyTag (13 Aug 2026, secondary) reports "the publication
  timeline has been extended to 2028". **The regulatory forcing variable
  for temporal verification has slipped, not tightened.**

## 2. Eligibility of the frozen instrument

- **"Third-party assurance spend rises"** — not observable in REGO registry
  volumes or Ofgem administration reporting by construction. Private
  audit-firm revenue; no public GB series exists.
- **"Certificate scheme volumes grow faster than administration"** —
  *partly* eligible. Volumes are fully observable (RER public CSVs).
  Administration capacity is not published for REGO (no cost, headcount or
  KPI series), so it must be inferred from proxies the register itself
  reveals: issue lag, availability of public reporting, and the RO cost
  letter's narrative about the shared RER.
- **Granular scheme volumes in GB** — no GB granular certificate registry
  publishes volumes. That half of the candidate is unmeasurable with the
  frozen instrument.

## 3. Frozen forcing observation — results

**REGO issuance volumes** (RER `REGO_Certificates_26-08-2026_04-30.csv`,
781,019 rows, sha256 `6e5d496a…`; site caveat: "Reports are refreshed
overnight providing a snapshot of the data on RER"):

| Year | TWh (output period) | TWh (issue year) | Stations issued to | Median lag (d) | p90 lag (d) |
|---|---|---|---|---|---|
| 2019 | 104.0 | 104.5 | 5,909 | 29 | 76 |
| 2020 | 118.4 | 115.9 | 5,734 | 31 | 75 |
| 2021 | 110.5 | 111.6 | 5,575 | 32 | 63 |
| 2022 | 122.7 | 123.6 | 5,672 | 32 | 62 |
| 2023 | 122.9 | 120.9 | 5,861 | 30 | 64 |
| 2024 | 132.6 | 131.6 | 6,087 | 29 | 80 |
| 2025 | 137.8 | 134.5 | 6,511 | 30 | 87 |
| 2026 to Aug | 72.7 | 100.0 | 6,529 | 39 | 158 |

FMD-year (Apr–Mar) output volumes: 2022/23 122.6; 2023/24 125.2; 2024/25
129.5; 2025/26 144.7 TWh. Growth is 3–6 %/yr, +12 % in the latest year —
steady, not explosive.

**Accredited stations** (149,264 rows): 82,264 accreditations took effect
in 2023 (82,235 Solar PV — bulk small FIT sites), 7,916 in 2024, 7,212 in
2025, 60 in 2026 to date. Matches ARA 2024-25: "we have seen an increase in
the number of generators participating in the REGO scheme." Only ~6.5k
stations actually receive certificates in a year.

**Processing lag** (issue date minus end of output month; *caveat: includes
generator submission time*). Same-months Jan–May comparison:

| Jan–May of | rows | median lag | p90 | share >90 d |
|---|---|---|---|---|
| 2022 | 29,891 | 32 | 71 | 8.2 % |
| 2023 | 30,653 | 30 | 71 | 7.9 % |
| 2024 | 31,923 | 28 | 74 | 8.5 % |
| 2025 | 31,313 | 28 | 72 | 8.1 % |
| 2026 | 34,344 | 37 | 141 | 14.1 % |

June shows an annual spike each year (p90 147 / 223 / 294 d in 2024 / 2025
/ 2026). July–August 2026 returned to normal (median 30 / 23 d).

**Ofgem administration reporting**:
- RO cost letter 2025-26 (Oct 2025): RO admin £10.41m, +8 %; "amendments
  demand rose significantly in the 2025-26 financial year, with overall
  volumes increasing by 104% … staffing costs have increased
  incrementally"; RER "launched as a public beta with a baseline level of
  functionality"; "Increased investment in the RER, will minimise delays".
- RER news: 27 Jun 2025 — register available only "Monday to Friday between
  the hours of 08:00 – 17:00 whilst we undertake maintenance"; 4 Aug 2025 —
  public reports moved to an external SharePoint on request; **3 Aug 2026**
  — "The reporting function within the … RER platform is now available for
  use." Public scheme reporting was effectively degraded for ~12 months.
- RO SY23 annual report (Mar 2026): "Since launch, the main focus of updates
  has been on defect remediation."
- ARA 2025-26 (15 Jul 2026) service KPIs for Renewable Electricity Schemes:
  95 % emails within 10 working days, 84 % / 98 % complaints within 20
  working days — all above target. ARA 2024-25: "REGO usage has expanded
  beyond FMD with REGOs been used for carbon reporting … Ofgem are working
  together to ensure this is done in a way that supports scheme
  integrity."
- Fees: none, and no consultation on introducing them found. GoOs no longer
  recognised for GB FMD from April 2023 — no reversal found.

## 4. Contradicting evidence

- Volume growth is modest and the 2023 station surge was absorbed with no
  lag deterioration in 2023–2025.
- The 2026 lag deterioration coincides with an IT migration ("defect
  remediation") and reverted by July–August 2026; Ofgem's published KPIs
  stayed above target. A transition cost, not volume outrunning capacity.
- Independence is supplied by the state for free: the register *is* the
  independent verification layer for annual claims, and Ofgem's own audit
  programme covers fraud. There is no fee to rise and no published cost to
  rise.
- The hourly forcing variable (GHGP) has slipped to a Q2 2027 consultation
  and a reported 2028 publication, with "a large majority of companies …
  exempt" from hourly matching under the proposed thresholds. No GB body is
  compelled to verify hourly claims today.
- Granular products exist, but "a provider exists" (Granular Energy as
  issuer) is not "buyers pay for independent verification"; no verifier is
  named and no volumes are published.

## 5. Verdict: plausible but not measured → downgraded

The frozen instrument cannot see assurance spend at all, and can see REGO
administration only through proxies. Those proxies show a *mild,
transient* strain (2026 issue lags ~30 % longer, share >90 d nearly
doubled, public reporting offline for a year) best explained by the RER
migration rather than by certificate volumes, which grow 3–12 %/yr.
Nothing in Ofgem's reporting touches granular or temporal verification,
and no GB granular scheme publishes volumes. The candidate's core claim —
that temporal claims will need independent verification the incumbents
cannot absorb — remains untested by the frozen observation. Not
*absorption stable* (no incumbent performs the granular function, so there
is nothing to be stable); not *strain evidenced* (the strain seen is in
the annual scheme's IT, not in temporal verification). Not promoted to an
opportunity: the cheapest absorption path — Ofgem/DESNZ adding a
half-hourly stamp to REGOs using Elexon settlement data, funded like the
rest of the scheme — is exactly what respondents to DESNZ's CPPA call for
evidence asked for, and would leave the state again supplying independence
at zero marginal price.

## 6. What this says about the generator

The generator paired a genuinely independence-requiring function with a
forcing observation that cannot, by construction, see its predicted
symptom: it named "assurance spend" (private, unpublished) and
"administration" (Ofgem publishes no REGO cost or capacity series) as if
they were registry statistics. It also assumed a granular scheme with a
registry exists in GB to be counted; none does. The useful correction:
when the incumbent is a free public registry, the strain symptom to declare
is *service-level* (issue lag, report availability, uptime) rather than
*spend*; and a candidate whose forcing variable is a foreign voluntary
standard must carry that standard's timeline as a falsifier — here the
timeline slipped between freeze and test, which the frozen row could not
express.

## 7. Sources (accessed 2026-08-26)

[V] RER Public Reports dashboard and CSVs (Certificates sha256 `6e5d496a…`;
Accredited Stations `ee4d8ec2…`; by Technology and Month `8aa756e3…`); RER
homepage news 13 May 2025, 27 Jun 2025, 4 Aug 2025, 2 Jul 2026, 3 Aug 2026;
Ofgem ARA 2024-25 and 2025-26; Ofgem RO cost of administration 2025-26 (Oct
2025); RO SY23 Annual Report (Mar 2026); REGO Guidance v4.0 (9 Mar 2026);
Ofgem REGO scheme and public-reports pages; DESNZ response to CPPA call for
evidence (7 Jul 2026); DESNZ Fuel mix disclosure data table 2025-26 (3 Aug
2026); GHG Protocol Scope 2 Guidance page and 29 Jul 2026 update; EnergyTag
accredited organisations and UK hourly-matching case study; Granular
Energy / Ecotricity Real Time REGOs (17 Jun 2025).
[S] EnergyTag "GHGP Scope 2 Consultation Responses" (13 Aug 2026; 2028
timeline claim); EnergyTag "Top Misconceptions" (17 Jun 2026);
SmartestEnergy blog on Climate Group REGO proposals.
[N] Auditor / assurance-market statements on 24/7 CFE or hourly Scope 2
assurance demand; Ofgem REGO publications library (client-side table).
