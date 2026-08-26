# 005 — results: connection-date slippage is measurable and partly predictable from the TEC register's history; the declared materiality bar was missed by 0.6 points

**Run**: 2026-08-26, one working day. Declaration `ee48de78…` (commit
`4101286`), frozen before any vintage was opened. Method amendment and
findings in `AMENDMENTS.md`. Evidence: `evidence/tec-slippage-summary.json`
(post-Amendment-1), `evidence/tec-slippage-summary-PRE-AMENDMENT-1.json`,
`evidence/cohort-tables.json`; per-project metrics under
`data/derived/tec-history/project-metrics.csv`; raw vintages and their
journal under `data/raw/neso/tec-history/` (751 journal rows, SHA-256 per
file). Runner: `run.py`; logic and tests:
`src/grid_mysteries/investigations/tec_slippage.py`,
`tests/test_tec_slippage.py`.

## The archive (kill condition (a): not met)

NESO's EIR response FOI/25/036 (19 Jun 2025) states: "NESO holds an
archive of the TEC Register … available on the EIR/FOI disclosure log";
FOI-24-0031 released every register from 7 Jan 2021 to 23 Jan 2025 and
FOI-24-0040 every register from 31 Jan 2014 to 31 Dec 2020; FOI-25-129
added 1 Apr and 1 Jul 2025; FOI-26-051 a 19 May 2026 extract. With
Wayback captures and the live CKAN resource: **731 distinct vintages,
2014-01-31 → 2026-08-25**; 699 parsed (32 early-2014 `.xls` files and one
2021 file failed parsing and are listed in the summary). Twice-weekly
through 2021–2024. One material hole: **2025-07-22 → 2026-05-19** (301
days), the connections-reform re-baselining period — fillable only by a
further EIR request or NESO's mooted data-portal archive.

The three vintages from December 2025 onward were excluded from Q1–Q3 as
declared (regime break) and are not analysed here.

## Three-column reading

**Observed** (699 vintages, 2014-01-31 → 2025-07-22, keyed on (name,
customer, site, stage)):

- 7,778 project-stage identities; 5,498 disappear before the last vintage
  (reported separately from slip; identity churn is a large part of it —
  see F-2 finding).
- Population for Q1–Q3 as declared (observed ≥ 2 years, first seen before
  2025, a slip observable): **1,161**.
- Net slip (last effective date − first, months): p10 0 · p25 0 · **p50
  0** · p75 17 · p90 41. Revisions per project: 0 for 650, 1 for 256, 2
  for 120, ≥ 3 for 135.
- **Q1 — dispersion: PASS.** IQR 17 months (bar ≥ 12); 21.4 % slipped ≥ 24
  months (bar ≥ 20 %); 63.5 % slipped < 6 months (bar ≥ 20 %).
- **Q2 — predictability: PASS on two of five pre-listed
  stratifications**, direction holding in both first-observation cohorts
  (2019–2021 and 2022–2024):

| stratification | high stratum | rate ≥ 24 m | low stratum | rate ≥ 24 m | ratio | cohort A (high / low) | cohort B (high / low) |
|---|---|---|---|---|---|---|---|
| first-observed status | Awaiting Consents (n 190) | **35.8 %** | Under Construction/Commissioning (n 38) | **10.5 %** | 3.4 | 34.0 % / 18.2 % | 19.0 % / 0.0 % |
| initial lead time | 3–5 years (n 274) | **35.8 %** | > 5 years (n 474) | **12.4 %** | 2.9 | 35.1 % / 2.7 % | 20.2 % / 3.9 % |

  Other strata, for the record: Scoping 16.8 % (n 619), Consents Approved
  25.5 % (204), Built 19.0 % (105); < 3 years 23.3 % (344). Plant type
  showed the largest raw contrast (CCGT 45.5 %, n 55, versus Energy
  Storage System 8.9 %, n 190; ratio 5.1) but **fails the cohort test**
  because the vocabulary splits across eras (see AMENDMENTS) and cohort
  cells are small. Host TO (ratio 1.5) and capacity band (ratio 2.1, one
  cohort) do not pass.

- **Q3 — materiality: FAIL, as declared.** Pooled rate 21.4 %. Largest
  gaps among passing strata: Awaiting Consents +14.4 pp; 3–5 years
  +14.4 pp; Under Construction −10.8 pp; > 5 years −8.9 pp. The frozen bar
  was ≥ 15 pp. Missed by 0.6.

**Supported inference.**

- Slippage is real and skewed: most contracted dates do not move, a fifth
  move by two years or more. That is a base rate an investor does not
  currently have.
- Two things visible on the day a project first appears carry
  information: being at *Awaiting Consents* roughly triples the chance of
  a ≥ 24-month slip relative to a project already under construction, and
  a 3–5-year initial lead time carries about three times the slip risk of
  a > 5-year one. The lead-time result is **not** an observation-span
  artefact: mean observation span is similar across bands (3.0–3.6 years)
  and slip per observed year is 4.9 months for 3–5-year projects against
  1.2 for > 5-year ones.
- The counter-intuitive direction of the lead-time result (further-out
  dates slip *less*) is consistent with far-dated positions being
  placeholders that are not actively re-dated until they approach, and
  with reform-era re-baselining being excluded — it is a supported
  inference about *register behaviour*, not about project delivery.

**Not publicly determinable from this record.** Why a date moved (network
works, consents, the developer, NESO administration) — F-1 stands
untested until the Transmission Works Register is joined (phase 2); how
much of "disappearance" is attrition versus renaming; whether old-regime
relationships survive Gate 2 (the post-December-2025 vintages are three
snapshots and are not analysed).

## Verdict under the declaration

Kill condition (a) not met; (b) not met (Q1 passes); (c) not met (Q2
passes); **(d) not met (Q3 fails by 0.6 pp)**. The outcome is not one the
declaration enumerated (see AMENDMENTS). Consequently:

- **The snapshot instrument is not started** on the strength of a
  near-miss. The declaration said all three must pass.
- The measured facts stand as facts: `P(slip ≥ 24 m) = 21.4 %` pooled;
  `35.8 %` for Awaiting Consents; `10.5 %` under construction; `35.8 %`
  for 3–5-year lead times; `12.4 %` for > 5 years — on 1,161 GB
  transmission-connected generation project-stages observed ≥ 2 years,
  2014–2025, old regime.
- Whether a 14.4-point gap against a 21.4 % base rate is an underwriting
  input is a commercial judgement the declaration deliberately reduced to
  a threshold, and the threshold said no. A phase-2 declaration may argue
  a different bar *before* touching the Transmission Works Register, and
  must say why 15 was wrong rather than why 14.4 is enough.

## What would change the verdict

- **Phase 2 (TWR join)**: if the slips attributable to enabling-works
  delay separate cleanly from developer-side slips, the stratified rates
  would likely sharpen; that is a new declaration, not an amendment.
- **Filling the 2025-07 → 2026-05 hole** by EIR request, which would also
  let the reform re-baselining be measured rather than excluded.
- **Plant-type harmonisation declared in advance** (one-to-one relabels),
  which the current run deliberately did not apply after seeing results.

## Sources

NESO EIR/FOI documents 363736 (FOI/25/036), 355266 (FOI-24-0031), 357306
(FOI-24-0040), 371461 (FOI-25-129), 382396 (FOI-26-051); NESO data portal
TEC Register (CKAN resource `17becbab…`); Wayback captures listed in the
journal with capture timestamps. Column vocabularies per era are recorded
in the journal; effective-date column names were "TEC Effective from
Date" (2014), "MW Effective Date" (2014–2020) and "MW Effective From"
(2020–). NESO's own caveat applies throughout: project status is its
best-known classification, not authoritative project information.
