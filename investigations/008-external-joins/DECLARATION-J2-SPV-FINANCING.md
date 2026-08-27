# 008 · J2 — SPV financing events and TEC connection-date volatility

**Frozen**: 2026-08-27, before any Companies House record has been
requested. Sealed by the commit that adds this file. Builds on 005
(`data/derived/tec-history/project-metrics.csv`) and 006's attribution.

## Hypothesis under test

> A registered lender charge at a project's SPV — public financial close —
> is followed by a sharp fall in the project's TEC connection-date
> volatility, and the slips 006 attributed to the project side occur
> predominantly before such an event or in its absence.

The null, equally publishable: TEC-date volatility does not change after a
charge, or charges are rarely present at the SPV.

## Stage 1 — the cheap kill (run first; stage 2 only if it survives)

**Population**: from 005's population (project-stages observed ≥ 2 years,
first seen before 2023-12), storage projects (`plant_type` containing
"Storage") with `first_status` in {Awaiting Consents, Consents Approved,
Scoping}, split by outcome in the latest register: **Built** (or last
status Under Construction/Commissioning) versus **still Scoping** with
≥ 3 years observed and no status advance. Minimum **n ≥ 40 per arm**.

**Identity resolution**: TEC `Customer Name` → Companies House company
number by exact legal-name search (case-, punctuation- and suffix-
insensitive). A customer name resolving to more than one live company, or
to none, is *unresolved* and excluded; the unresolved rate is reported per
arm. Customers holding ≥ 5 TEC projects are flagged as portfolio companies
and reported separately (a charge at a portfolio company is not project
finance).

**Measure**: fraction of resolved SPVs with ≥ 1 charge (`GET /company/{n}/charges`)
with `created_on` before the project's last observed TEC vintage.

**Kill**: if the Built arm's charge incidence exceeds the Scoping arm's by
< 15 pp, or the resolved rate is < 60 % in either arm, the charge carries
no usable information at SPV level and **stage 2 is not run**. Banked as:
*project finance is not visible at the TEC customer entity for most GB
storage projects* — itself a fact about where delivery risk sits.

## Stage 2 — the event study (only if stage 1 survives)

**Population**: all resolved 005 projects (any plant type) with ≥ 1 SPV
charge whose `created_on` falls inside the project's TEC observation span
with ≥ 12 months of vintages on each side. Minimum **n ≥ 60**.

**Measure**: per project, TEC revision rate (revisions of `MW Effective
From` per 12 months of observation) in the 12 months **before** the first
charge and the 12 months **after**; and the share of 006's "project-led"
slips (from `attribution.csv`, `outcome`) that fall before versus after
the first charge, among projects present in both tables.

**Bars**
1. Median post/pre revision-rate ratio **≤ 0.5** with the paired sign test
   p < 0.05 → **(a) financing hardens dates**.
2. Median ratio in [0.8, 1.25], or the after-charge share of project-led
   slips ≥ 40 % → **(b) financing does not harden dates**.
3. Otherwise indeterminate, reported as such.

Control (reported, not scored): the same before/after ratio around a
*placebo* date — the midpoint of each project's observation span — for the
same projects, to separate the charge effect from the general tendency of
older projects to stop revising.

## Outcomes, fixed now

- **(a)** → *If I were lending against or buying a pre-construction project,
  I would read a registered SPV charge as the public event after which the
  TEC date becomes credible, and I would treat pre-charge TEC dates as
  developer intent rather than commitment.* 006's project-led bucket is
  restated as predominantly pre-financing.
- **(b)** → *Financial close does not harden connection dates: post-close
  slips are as frequent as pre-close ones*, which places the residual
  delivery risk on the transmission side and gives 006's negative result
  an independent, non-TWR check.
- **Stage-1 kill** → *Charges are not where GB project finance shows*, and
  the join is closed with that fact.

## Identity and data-quality risks, declared

Customer-name changes across TEC's three naming eras and project transfers
between customers (F-2); holdco-level financing invisible at the SPV;
portfolio companies; aggregator-held projects; `created_on` versus
`delivered_on` (created_on is used); Companies House name normalisation;
API rate limit (documented as 600 requests per 5 minutes — to be verified
against the current documentation before the run, and the run throttled
accordingly). Every company number → TEC customer mapping is written to
`evidence/` so the resolution can be challenged.

## Gate

Acquisition after the human seal. Stage 1 is ~200 API calls against a
free key; stage 2 ~1,500. Company profiles and charge lists are pinned
under `data/raw/companies-house/` with fetch time and digest. No record is
requested before the seal.
