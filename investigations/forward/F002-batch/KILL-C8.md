# C8 kill record — whole-system distributed asset visibility during the DNO→DSO transition

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-26, fifth in the frozen kill order. The five remaining kills
(C8, C10, C9, C4, C2) were researched concurrently for speed and are
recorded in the frozen order; each ran only its own frozen observation.
**Verdict**: **absorption not determinable** — two of three frozen symptoms
cannot register in the instrument; the measurable one leans *stable*.

Research performed by a background agent under the v3 kill discipline; the
record below is its report, unedited except for this header.

## 1. Existing job

The function is already paid for, several times over:

- **DNO DSO/data teams**, funded under RIIO-ED2 (2023–28) and scored
  annually under the **DSO Output Delivery Incentive**, whose evaluation
  criteria include Role 2.1 "Promote operational network visibility and data
  availability" and a weighted criterion "Data and information provision".
  Ofgem's ED2 annual report notes NPg's "IT costs are rising due to data and
  digitalisation programmes" and sector business-support cost pressure
  "driven by IT investment, cyber resilience, and transformation"
  (cumulative £910m vs £868m allowance).
- **Ofgem Data Best Practice (DBP) Guidance** (licence obligation; v3
  October 2024) requiring open-by-default publication, metadata, and
  recorded Open Data Triage (clause 3.34).
- **ENA Open Networks** (2017–July 2025), which produced the common Embedded
  Capacity Register format (monthly, within 10 working days of month-end,
  per DCUSA), primacy rules, the Whole System Coordination Register, and
  >350 products; flexibility-market rule development handed to **Elexon as
  market facilitator** (handover plan approved by Ofgem, 24 May 2025;
  go-live "late 2025").
- **NESO** as recipient of DNO operational data (ICCP links, primacy data).

So the incumbent guess in the frozen row is correct: this is a regulated,
incentivised, budgeted function.

## 2. Eligibility before numbers

The frozen instrument is **only partly eligible**, and the eligible part
points in one direction by construction:

- **"Data-request turnaround lengthens"** — *ineligible.* No DNO publishes a
  request-to-fulfilment turnaround. DBP guidance contains no word "request"
  and no timescale; it requires recording *when triage took place* (3.34),
  not when a request arrived. NPg's `data-triage-assessments` (104 records)
  carries `data_triage_date` only; ENWL's `sp-enw-dataset-triage` records
  API returns 403; UKPN/SPEN catalogs contain no triage/turnaround/KPI
  dataset. The symptom cannot appear in the instrument.
- **"Open-data completeness stalls"** — *eligible but confounded.* Dataset
  counts and modified-dates are observable, but "dataset" is not a stable
  unit (the same panel cites NGED at 96 datasets in 2023/24 and 88 in
  2024/25 while saying the catalogue "doubled"; the live CKAN API returns 92
  today). Counts and update cadence also move for ordinary reasons (rebrands
  resetting timestamps — ENWL/"SP ENW" shows 100% of datasets modified
  within 365 days after the ScottishPower acquisition; catalogue
  consolidation; automation of live feeds). A stall would be
  indistinguishable from re-cataloguing.
- **"Programme milestones slip"** — *eligible in principle,* but the only
  programme-level milestone record (ENA Open Networks) is unreachable from
  here (see §7), and what is reachable (Elexon handover) concerns
  flexibility-market rules, not asset visibility.

## 3. Frozen observation — what the instrument shows over time

**Ofgem DSO Incentive Report 2023/24** (published 26 Sep 2024) [V] and
**2024/25** (published 26 Sep 2025) [V]:

| DNO | Panel 23/24 | Panel 24/25 | "Data & information provision" 23/24 | 24/25 | Total reward £m 23/24 → 24/25 |
|---|---|---|---|---|---|
| UKPN | 8.91 | 9.36 | 9.0 | 9.30 | 8.84 → 11.05 |
| NGED | 8.24 | 8.45 | 8.6 | 8.40 | 5.97 → 14.92 |
| SSEN | 7.59 | 7.81 | 7.50 | 8.10 | 2.17 → 5.29 |
| NPg | 6.58 | 7.34 | 7.40 | 8.10 | 0.72 → 2.57 |
| ENWL | 6.19 | 6.71 | 7.10 | 7.30 | 0.19 → 2.14 |
| SPEN | 5.08 | 6.08 | 5.10 | 6.90 | 0.59 → 3.65 |

Every panel score, every survey score and five of six data-provision scores
rose; total DSO reward rose to £39.6m; sector-average panel score 7.63,
survey 8.85 (Ofgem ED annual report 2024/25 [V]). The 2024/25 panel's own
framing: evidence "increased in quality and their submissions were more
standardised"; best practice: "Accessibility of Data: Some DNO's approach
sets a benchmark for data transparency and stakeholder enablement."

Sources' own caveats, quoted:
- 23/24 §4.9/4.23: the DSO **Outturn Performance Metrics "will not be turned
  on in RIIO-ED2"**; "the development and inclusion of standardised metrics
  ... is strongly encouraged. Although not mandated". So the panel has no
  standardised measurement of data provision — scores are judgement on
  self-authored submissions.
- 23/24 §4.12: "expectations regarding evidence will rise in subsequent
  years" — i.e. the scale is not fixed year to year.
- 24/25 §4.16: "All DNOs have made progress in improving DER visibility and
  dispatch coordination. However, full real-time dispatch capabilities are
  still evolving, and the integration of DERs into NESO markets is not well
  evidenced."
- 24/25 NGED: "minimal evidence of real-time visibility tools like ANM or
  telemetry integration ... it's unclear whether NESO actively uses the
  shared primacy data. As DER volumes grow, NGED's limited digital
  infrastructure may indicate a shift toward physical asset reliance";
  "There are no supporting statistics about the number of users, frequency
  of enquiry."
- 24/25 SPEN: "critical datasets such as hosting capacity, constraint
  forecasts, or DER visibility were missing. SPEN lags sector leaders
  significantly"; "DER visibility is partial and not yet linked to
  real-time decision-making"; but "ECR validity improved significantly".
- 24/25 SSEN: "CIM is still not in place ... real-time data availability,
  API capabilities, and dataset interoperability with other platforms
  remain limited".
- Stakeholder call-for-evidence responses fell from ~30 (23/24) to 19
  (24/25) — the panel says stakeholder evidence "mainly support[ed]" its
  decisions.

**Portal completeness, live census 2026-08-26** (catalog APIs) [V]: UKPN
138 datasets (49 modified ≤31 days, 25 >365 days); NPg 100 (28 / 22); ENWL
149 (23 ≤31d; none >365d — timestamp-reset caveat); SPEN 153 (35 / 17);
NGED 92 (39 / 19). SSEN's portal has no catalog API found. Compared with
the panel's own counts (UKPN 189 incl. 127 third-party in 23/24 then "+50%"
in 24/25; NGED 96→88→92), the numbers are not a consistent series and
cannot support a "stall" claim in either direction. Roughly a third of
catalogued datasets on each ODS portal were touched in the last month; a
sixth-to-quarter have not been touched in a year. That is neither evidently
stalling nor evidently accelerating; it is not a time series.

**ENA programme milestone reporting:** not retrievable (see §7). What is
retrievable: Elexon's handover plan (22/24 May 2025) [V] lists the
transferred products — primacy rules, DSO baselining, dispatch API, "A
common Flexibility Market Asset Registration process" — i.e.
flexibility-market products; nothing in the handover list is an
asset-visibility product, and the ENA search snippet [S] says the programme
"concluded" July 2025. Whether the "late 2025" go-live milestone held could
not be confirmed (Elexon service page redirected to a workshop page).

## 4. Contradicting evidence (absorber investing ahead / improving)

- All six DNOs' DSO scores rose year on year; total reward up from £18.5m to
  £39.6m; NGED and UKPN at 100% of maximum.
- Explicit capacity-building inside the incumbent: UKPN "dedicated data team
  within-house", "exceeded Ofgem data maturity framework"; NGED "new DSO
  Scrum team focused on dashboards and the use of data", CIM being applied,
  Network Opportunities Map covering 190,000 substations; SSEN "newly formed
  Data Governance Steering Group", "four-fold increase in Level 1-assured
  datasets", NeRDA near-real-time portal; SPEN Informatica data-quality
  tooling, per-dataset "Data Quality Checks" published on its portal; NPg
  1,550 LV monitors in one year.
- Sector business-support spend is above allowance because of IT/data
  programmes — the absorber is spending *more*, not rationing.
- Ofgem's own verdict (ED annual report 2024/25): "DNOs are responding
  positively to the DSO incentive, with year-on-year improvements across all
  groups."

## 5. Verdict

**Not determinable** (with the measured leg leaning *absorption stable*).

Two of the three predicted symptoms cannot register in the frozen
instrument — turnaround is unpublished by construction, and the programme
milestone record is unreachable and, where reachable, concerns a different
function. The one measurable symptom (open-data completeness) shows
improving panel scores, growing catalogues and heavy ongoing update
activity, with the principal caveat that the panel's scale and
dataset-counting definitions are not stable, so the improvement is also not
a clean time series. The panel's qualitative concerns (real-time DER
visibility "partial", NESO use of shared primacy data "unclear", CIM
incomplete at SSEN, SPEN lacking DER visibility datasets) are real, but
they are *ordinary transition incompleteness inside a funded programme*,
not evidence that the absorber's capacity is falling behind the forcing
variable. Nothing here shows a buyer paying an external party for
visibility because the DNO/NESO/ENA job failed — and the existence of
Opendatasoft/CKAN/Informatica vendors is tooling inside the incumbent, not
externalisation. "A provider exists" is not promoted to "buyers pay".

## 6. What this says about the generator

The frozen incumbent guess (DNO DSO teams; NESO; ENA) was right — the
function is regulated, budgeted and scored, and the absorber is visibly
investing ahead. The instrument, however, was mis-specified at
construction: the generator predicted a symptom ("data-request turnaround
lengthens") that no public source in the instrument class records, and a
second ("milestones slip") whose only public record sits behind a bot wall
and, in any case, concerns flexibility-market rules rather than
visibility. The third symptom was measurable but its unit ("dataset") is
unstable. **L1 recurs.** This candidate should have been sent back at
instrument-design time with "name a source that publishes turnaround",
rather than reaching the numbers. If C8 were ever retained, the honest
reformulation is *DER visibility adequacy for NESO/DSO real-time
operation*, whose eligible instrument would be the DSO panel's
DER-dispatch criterion and NESO's own statements on distribution-data
usability — a different, deeper observation belonging to a future batch,
not to this kill.

## 7. Sources and retrieval limitations (accessed 2026-08-26)

- [V] Ofgem, DSO Incentive Report 2023/24, 26 Sep 2024 —
  `ofgem.gov.uk/sites/default/files/2024-09/DSO_Incentive_Report_2023-24.pdf`
- [V] Ofgem, DSO Incentive Report 2024/25, 26 Sep 2025 —
  `ofgem.gov.uk/sites/default/files/2025-09/DSO_Incentive_Report_2024_25_V1.pdf`
- [V] Ofgem, RIIO-2 Electricity Distribution Annual Report 2024/25 —
  `ofgem.gov.uk/sites/default/files/2026-01/ED-annual-report-2024-2025.pdf`
- [V] Ofgem, Data Best Practice Guidance v3 track-changes, October 2024
- [V] Elexon, "Final handover plan from Open Networks to market
  facilitator", 22 May 2025
- [V] DNO portal catalog APIs (UKPN, NPg, ENWL, SPEN Opendatasoft; NGED
  CKAN), queried 2026-08-26; NPg `data-triage-assessments` schema/records
- [S] ENA, "World-leading ENA programme marks five years…" (programme
  concluded July 2025) — snippet only
- [S] DCUSA / SSEN / ENWL Embedded Capacity Register pages — snippets only
- [N] ENA Open Networks milestone reporting — energynetworks.org 403 /
  Cloudflare challenge; Wayback offline at run time
- [N] Ofgem-published DBP compliance assessments or independent audits
- [N] Any DNO-published data-request turnaround KPI
- [N] ENWL triage records API (403); SSEN catalog API

Retrieval limitation: the shared WebSearch budget was exhausted early in
this run; work proceeded via curl, portal APIs and pdftotext (~20 tool
calls). Ofgem PDFs were read by local text extraction.
