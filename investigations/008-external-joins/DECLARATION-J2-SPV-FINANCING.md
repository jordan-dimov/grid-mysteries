# 008 · J2 — SPV financing events and TEC connection-date volatility

**Frozen**: 2026-08-27, before any Companies House record has been
requested. First committed at `e8ee111` (sha256 `540ede41…`); **amended
the same day, before the seal and before any fetch**, to add the sponsor's
age/timing guard (below). Sealed by the commit that adds this amended
text. Builds on 005 (`data/derived/tec-history/project-metrics.csv`) and
006's attribution.

## Age/timing guard (sponsor's amendment, binding)

> Stage 1 may **screen** charge incidence, but it **cannot pass J2
> commercially by itself.** Built projects and their companies are older
> and have simply had more time to accumulate charges. Any positive
> Stage-1 result must survive Stage 2 using the **first charge created
> after the project first appears in TEC**, with project age and
> observation time controlled by the placebo design.

Consequences fixed now: a Stage-1 pass triggers Stage 2 immediately and
is **not interpreted** on its own; no decision sentence is attached to
Stage 1; the Stage-1 figures are published only as the screen that they
are, with company incorporation age reported per arm so the reader can
see the confound's size.

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

**Survival is only a screen.** Under the age/timing guard, a Built-arm
excess ≥ 15 pp proves nothing about credibility of dates; it only
justifies the Stage-2 fetch. Reported with it: median company age
(incorporation to last TEC vintage) per arm, and charge incidence
restricted to charges created **after** the project's `first_observed`
TEC vintage — the Stage-2 clock — so that the "older companies have more
charges" explanation is visible in the same table.

## Stage 2 — the event study (only if stage 1 survives)

**Event clock**: the **first charge whose `created_on` is after the
project's `first_observed` TEC vintage** ("first financing charge").
Charges created before the project appeared in TEC are ignored for the
event study (they cannot have hardened a date that did not yet exist) and
are counted separately.

**Population**: all resolved 005 projects (any plant type) whose first
financing charge falls inside the project's TEC observation span with
≥ 12 months of vintages on each side. Minimum **n ≥ 60**.

**Primary measure** — *does connection-date volatility fall after the
first financing charge?* Per project, TEC revision rate (revisions of
`MW Effective From` per 12 months of observation) in the 12 months
**before** the first financing charge and the 12 months **after**; and
the share of 006's "project-led" slips (from `attribution.csv`,
`outcome`) that fall before versus after it, among projects present in
both tables.

**Sister outcome** (reported, scored only as stated in bar 4) — *does the
first financing charge raise P(moves to construction/built)?* Among
projects observed ≥ 24 months after the charge, the share whose TEC status
reaches Under Construction/Commissioning or Built within 24 months,
against the same share for the placebo date in the same projects.

**Bars**
1. Median post/pre revision-rate ratio **≤ 0.5** with the paired sign test
   p < 0.05 → **(a) financing hardens dates**.
2. Median ratio in [0.8, 1.25], or the after-charge share of project-led
   slips ≥ 40 % → **(b) financing does not harden dates**.
3. Otherwise indeterminate, reported as such.
4. **Age control, binding on (a)**: (a) is awarded only if the median
   post/pre ratio around the first financing charge is at least 0.25
   lower than the same ratio around the **placebo date** — the midpoint of
   each project's observation span — in the same projects. If the placebo
   shows a fall of the same size, the result is "dates stop moving with
   age, not with financing" and (b) is recorded.
5. Sister outcome: P(construction/built within 24 months) after the
   charge minus after the placebo date, with n; reported with a 95 %
   Wilson interval, not thresholded.

The placebo is what carries the age/observation-time control: every
project is its own comparator at a date that has nothing to do with
financing.

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
