# Investigation 006 — connection-slippage attribution: does the history of the enabling transmission works tell an investor more than the connection date itself?

**Declared 2026-08-26, before any Transmission Works Register (TWR) file was
opened. Frozen on commit; never edited. Results in `RESULTS.md`; amendments
in `AMENDMENTS.md`, dated.** Builds on Investigation 005 (declaration
`ee48de78…`, results at `9bd1ed3`), whose population, timelines and
post-Amendment-1 metrics are reused unchanged.

## The commercial question

> **Can connection-date risk caused by the project be distinguished from
> connection-date risk caused by the network works it depends on — and does
> that distinction materially improve identification of unreliable
> contracted dates?**

005 established that slippage is real and skewed (21.4% of positions slip
≥ 24 months), that development stage and initial lead time carry repeatable
information (ratios 3.4 and 2.9, both cohorts), and that the raw effect fell
0.6 points short of the declared materiality bar. The next question is not
"predict slippage better"; it is whether the *dependency graph beneath the
date* contains more information than the date. That is the version a lender
or acquirer would pay for: "your enabling works have already slipped twice"
is a different fact from "your cohort slips 3.4× more often".

## What is known at declaration

- CUSC requires NESO's Transmission Works Register to publish, per relevant
  project: project/customer, connection site, **completion dates** of the
  associated transmission works, and amendments as they occur.
- NESO disclosed TWR reports 2017–2025 under FOI-25-133 (document 371516,
  ~7 MB). Their structure, cadence and columns are **unknown** at
  declaration; the first act after freezing is to describe them, and kill
  condition (a) below is decided on that description before any join is
  attempted.
- 005's timelines: 699 TEC vintages 2014-01-31 → 2025-07-22 (old regime),
  7,778 project-stage identities, 1,161 in the declared population.

## Pre-declared method

**Works identity.** A works item is identified across TWR vintages by the
normalised (works description or works id, connection site) pair; where the
TWR carries an explicit works identifier, that is used. Splits and merges
are recorded, not repaired.

**Join.** TEC project-stages (005 keys) are joined to TWR works by the
normalised (customer, connection site) pair, then by (project name,
connection site). A TEC project with ≥ 1 matched works is *matched*. The
match rate is reported before any metric, and is kill condition (a).

**Works history, per works item and per date:** number of completion-date
revisions observed in TWR vintages up to that date; net slip of the
completion date (signed months); `slipped_before(t)` = at least one
completion-date revision of ≥ 6 months observed before t.

**Attribution of a TEC effective-date revision at vintage t** (one of three,
exhaustive):
- **works-led** — a dependent works' completion date moved in the same
  direction by ≥ 6 months in a TWR vintage published within the 180 days
  before t, or within 90 days after t;
- **project-led** — the project has ≥ 1 matched works and none moved in
  that window;
- **unattributable** — no matched works.

**Population.** 005's declared population (observation span ≥ 2 years,
first observed before 2025-01-01, slip observable), old regime only
(vintages before 2025-12-01), restricted to matched projects for T2–T4.

## Pre-declared tests and thresholds

**T1 — measurability (kill (a)).** The TWR material yields ≥ 5 distinct
vintages spanning ≥ 3 years **and** ≥ 50% of the 005 population is matched
to ≥ 1 works item. Otherwise: *not measurable from the public record*, with
the resolving observation named (a TWR archive at TEC cadence, held by
NESO; EIR route).

**T2 — discrimination.** Among matched projects, the subgroup whose matched
works had `slipped_before(first TEC observation + 12 months)` versus the
subgroup whose works had not: the rate of TEC slip ≥ 24 months differs by
**≥ 20 percentage points**, each subgroup n ≥ 30, and the direction holds
in both first-observation cohorts (2019–2021 and 2022–2024).

**T3 — reclassification.** Risk bands are defined from the pooled ≥ 24-month
rate p among matched projects: *low* < p − 10 pp, *high* > p + 10 pp, *mid*
otherwise. Stratify once by 005's best TEC-only stratification (first-
observed status) and once by (first-observed status × works-history flag).
T3 passes if **≥ 20% of matched projects change band** between the two
stratifications, with every contributing (status × flag) cell n ≥ 30.

**Pass** = T1 and (T2 or T3). **T4 (descriptive, always reported):** the
share of ≥ 24-month slips attributed works-led / project-led /
unattributable, overall and by first-observed status; and the F-1 check —
whether works completion-date moves cluster on a small number of TWR
publication dates (administrative re-baselining) rather than spreading
across them.

## Kill conditions

- **(a)** T1 fails → killed: *not measurable*, resolving observation named.
- **(b)** T1 passes, T2 and T3 both fail → killed for underwriting; recorded
  as: *interesting empirical evidence about GB connection slippage, suitable
  for publication, not a proprietary underwriting instrument.* 005's
  findings stand on their own as the publishable result.
- **(c)** Pass → the finding is stated as a decomposition — measurable
  developer risk and measurable network-delivery risk — and only then is a
  snapshot instrument (TEC and TWR, twice weekly) started, under a separate
  declaration.

## Declared falsifiers and confounders

- **F-1** works-date moves are administrative re-baselining across many
  works at once; tested by the clustering check in T4.
- **F-2** the join is wrong (customer renames, site-name variants); the
  match rate and a sample of 30 matches checked by hand are reported before
  T2/T3.
- **F-3** TWR cadence is too coarse for the ±180/90-day attribution window,
  making everything "project-led" by construction; the observed cadence is
  reported and, if the median gap between TWR vintages exceeds 180 days,
  T4's attribution is reported as *not resolvable at this cadence* rather
  than as a finding.
- **F-4** shared works (one works item serving many projects) make the
  works-history flag a proxy for a substation or TO, not a project; T2 is
  re-read within host TO as a check, reported descriptively.
- **F-5** reverse causation — projects that slip cause their works to be
  re-dated; the attribution window is asymmetric (180 days before, 90
  after) to lean against it, and the ordering is reported.

## Three clocks

Every TWR vintage carries its publication date; a works-date move is dated
by the first vintage in which it appears (t_public). No attribution rests on
a vintage whose publication date is not established.

## What this study will not do

Build a model or score; harmonise plant-type vocabulary (pre-declared as
out of scope: the CCGT/battery contrast looked large *after* 005's data was
seen); collect live snapshots before a pass; analyse post-December-2025
vintages beyond description; move 005's 15-point bar or its own 20-point
bar; run longer than two working days before reporting.
