# 020 — Did it energise: amendment 3 (version 1: the join at project level, the walk, the intervals)

**Written 2026-10-12 on the sponsor's handover of that day (etrmbiz
`notes/2026-10-12-grid-mysteries-drift-paper-handover.md`: "schema pass,
amendment written from the schema reports alone, acquire, J1 proposals,
admission, compute"; robustness intervals declared before computing; S3
and S4 settled by amendment rather than left silent).** Frozen by
`scripts/freeze` before any J1 proposal is computed and before any B1610
window is requested. It completes amendments 1 (`cc01e3cf…`) and 2
(`3ef7240c…`) for **version 1**: the realised delay from the register's
date to the first metered output, for the projects version 0.2 measured.

## Prior exposure, stated

The author has seen versions 0, 0.1 and 0.2 (register only): 164 projects
measured, 152 under the reading without later stages, 12 *only later
stages*; median months from the reference date to the first `Built` copy
3.4 with later stages and 5.1 without; by year of the `Built` copy, medians
of about 2 months in 2016 to 2019 and 11 to 14 in 2024 to 2026, small n.
The author has seen the plant types of the 164 as printed (71 `Wind
Onshore`, 40 `Energy Storage System`, 20 `Wind Offshore`, the rest gas,
biomass, CHP, hybrids and single cases), 149 in the old regime and 15 in
the new. From the schema reports: S1's fields (`elexon-bmunits-020`,
`0f0902e1…`: 3,112 units, no date field, `fuelType` blank on 2,522), S2's
(`elexon-b1610-020`, `fb8c80c8…`: one day, 9,152 units, `quantity`,
`psrType`), S3's. While designing J1 the author looked up two names in the
pinned S1 vintage: Carrington (the register's 910 MW project) is two BM
units of 470 MW each under one lead party, and the BM unit at Markinch
(Glenrothes) is named "Rothes Bio-Plant CHP1" under a lead party whose
name shares no token with the register's. The distinct spellings of
`Agreement Type` across the 447 copies that print it were listed (no other
value read): `Directly Connected`, `Direct Connection`, `Embedded`, `BCA`,
`BEGA`, blank and `Null`. To fix B4's request shape, the author probed
`datasets/B1610/stream` (not pinned): a supplier unit (`2__AALAB000`)
returns no records under the `bmUnit` filter, and `T_DRAXX-1`, which
turned out to be a unit of a population project (Drax), returned 48
records for 01/09/2026 and 336 for the seven days 26/08 to 01/09/2026
with periods 1 to 50, fields as the S2 report. Only record counts, dates
and field names were read, no `quantity`, and nothing earlier than
26/08/2026. **No J1 candidate list has been computed, and no B1610
quantity for any population project has been read.**

## B1 — the population of version 1

The 164 projects of `evidence/projects-v02.ndjson` (version 0.2): every
project with a first `Built` copy, a kept copy before it and at least one
capacity-bearing dated stage there. The 1,414 *Built at first sight*, 21
*undated before Built* and 9 *not sighted in the copy before* keep their
version 0.1 labels and get no link in this version. P2 (the 103 Gate 2
rows, figure 4) and the placeholders (figure 3) are **deferred to a later
version**; nothing in version 1 depends on them.

## B2 — J1 at project level

The declaration's J1 was written for units; amendment 1 made the project
the unit of measure. For each project of B1, against the S1 vintage pinned
under the declaration's seal (`data/raw/elexon/020/2026-09-30/bmunits.json`,
SHA-256 `0f0902e1…`; no new vintage is fetched):

- **Text.** The project's side is its key's normalised project name,
  customer name and connection site (005's rule, `tec_register.normalise`).
  A BM unit's side is its normalised `bmUnitName` and `leadPartyName`.
- **Tokens.** Space-separated words of the normalised text, four
  characters or more, at least one of them a letter. A token **counts**
  only if it occurs in the text of fewer than 1 % of S1's units (fewer
  than 32 of 3,112), computed once over the pinned vintage, so that words
  like *wind*, *farm*, *power*, *energy* or *limited* never make a
  candidate alone. The list of excluded tokens is written with the
  proposals.
- **Capacity.** A unit's capacity is its `generationCapacity`; where the
  project's `Plant Type` names energy or battery storage, also the
  absolute value of its `demandCapacity`, either one qualifying. The
  project's figures are its capacity (the sum of its positive stage MW in
  the copy before, as version 0.2 records) and its cumulative MW (the
  largest `Cumulative Total Capacity (MW)` among its rows in that copy,
  where printed).
- **A unit candidate**: at least one counted token shared, and capacity
  within 25 % of either project figure.
- **A set candidate**, for a project split across units (J2 already
  admits "a set of units"): the units that share a counted token with the
  project, grouped by the stem of their `nationalGridBmUnit` (the id with
  a trailing `-<digits>` or trailing digits removed: `CARR-1` and `CARR-2`
  are stem `CARR`), when a stem holds two or more such units and their
  summed capacity is within 25 % of either project figure.
- **Score**, written with every candidate: the counted tokens shared, the
  capacity ratio (candidate over project capacity), and fuel agreement:
  `match` where the S1 `fuelType` is the one the project's plant family
  (B5) implies, `differs` where it is another, `unknown` where S1 prints
  none. **Exact** (the declaration's J2 tier) is: the normalised project
  name equal to a normalised `bmUnitName` or `leadPartyName` of the
  candidate, capacity within 5 %, fuel `match`.
- Candidates are listed by counted tokens shared (more first), then by
  the distance of the capacity ratio from 1. All are written to
  `evidence/links-proposed.json`, reproducible offline from the pinned
  bytes (C5).

## B3 — J2, admission

A person admits, for each project, **one candidate** (unit or set), or
records *no unit found*, dated and initialled, in
`evidence/links-admitted.json`. A unit or set that J1 did not propose
cannot be admitted: a missed link is a finding about J1, re-proposed only
under a further amendment against the same pinned bytes (F4's route), with
both proposals kept. The session prepares a pre-screen of the proposals
(its reading of each, as for 019) for the sponsor's one sitting, and
writes the admissions file from his answers; the pre-screen advises, the
person decides.

**J3** is now read from `Agreement Type` in the copy before: a project
all of whose capacity-bearing stages print `Embedded` or `BEGA` is
*embedded or distribution*. Where the copy prints no `Agreement Type`
(about a third of copies, mostly before 2016), J3 is *not determinable
from the register* and the project stays in the base of F2.

## B4 — the walk (amendment 1's A2, made exact)

For each admitted unit or set, B1610 is requested from
`datasets/B1610/stream` in windows of seven settlement days
(`from` = day − 6, `to` = day, periods 1 to 50, every unit of the set as a
`bmUnit` parameter), walking backward from the run date to the floor
amendment 1 named (2015-01-01, since every first sighting is later), and
stopping at the first window with no record after a window with records.
Each response is pinned once under `data/raw/elexon/<run-date>-020/b1610/`
with its digest in `evidence/manifest.json`. The **proxy** is the earliest
settlement day with `quantity` > 0 for any admitted unit of the project.

- **Format check, before any value is read.** Every pinned window is
  checked against the S2 schema report (`fb8c80c8…`): UTF-8 without a
  byte-order mark; JSON; a top-level array (or the `data` array of an
  object, as the report's sample was read); every record carrying the
  report's always-present fields (`dataset`, `psrType`, `bmUnit`,
  `settlementDate`, `settlementPeriod`, `halfHourEndTime`,
  `settlementRunType`, `quantity`), `bmUnit` among the requested units.
  A window that departs stops the compute; only a further amendment reads
  it.
- **Left-censored**: a project whose records reach the floor window has
  output before the walk could see; its proxy is not measured and it is
  labelled `metered-before-the-walk`.
- **Run-type**: the earliest day is taken over every `settlementRunType`
  the window returns; the run type of the proxy record is written beside.
- The labels are amendment 1's (`metered`, `registered-not-metered`,
  `no-metered-record`, `embedded-or-distribution`) plus `unmatched`
  (candidates proposed, none admitted), `no-candidate`, and
  `metered-before-the-walk`; every project of B1 is in exactly one (C4).

## B5 — what is computed, and the intervals, declared before computing

- **Realised delay**: months (version 0.2's arithmetic: days ÷ 30.4375, to
  one decimal) from the reference date to the proxy day, under **both**
  readings of amendment 2 (with later stages; without, for the 152 that
  have a date under it), side by side, neither preferred.
- **Register's lag**: months from the proxy day to the first `Built`
  copy, with each project's copy gap (copy before to first `Built` copy)
  written beside as its resolution. The archive's cadence bounds it:
  roughly weekly before 2021, twice weekly 2021 to 2024, the 301-day hole
  of July 2025 to May 2026, daily capture from 15/09/2026.
- **Distributions**: n, min, p25, median, p75, max (version 0.2's
  `quantiles`), overall, **by year of the first `Built` copy**, and **by
  plant family**: *offshore wind* (`Wind Offshore`), *onshore wind*
  (`Wind Onshore`), *solar* (`PV Array`), *storage* (`Energy Storage
  System` or `Battery Storage`, alone or with `Demand` or `Reactive
  Compensation`), *hybrid* (storage with a generation family, or
  `HYBRID`), *thermal* (`CCGT`, `OCGT`, `CHP`, `Thermal`, `Biomass`, gas,
  coal, nuclear), *other*; mixed generation families are *hybrid*.
- **Intervals**: every median carries a 95 % percentile bootstrap
  interval: 10,000 resamples with replacement of the group's projects,
  the same `quantiles` median on each, Python's `random.Random(20261012)`
  drawn in the order the groups are listed. A group with n < 5 gets no
  interval and says so. The shares metering **before** the reference date
  (delay < 0), **within six months after** (0 to 6.0) and **later** carry
  95 % Wilson intervals.
- **Coverage, reported first**: projects by label; F1 and F2 below; the
  MW of each label.

## B6 — the falsifiers, restated for projects

- **F1**: if fewer than half of the admitted projects have any B1610
  record, the realised delay is published for the covered projects only,
  with the coverage, and the question is *partly determinable*.
- **F2**: if fewer than 60 % of B1's projects, less those J3 labels
  *embedded or distribution*, receive an admitted link, the realised-delay
  distributions (figures 2 and 3 of the declaration) are *not
  determinable* and the labels are the outcome.
- **F3** fired at the schema pass (no registration date; amendment 1).
- **F4** unchanged: more than 5 % of admitted links failing C6 re-proposes
  every link under an amended J1.

## B7 — sources settled

- **S3 REMIT** is **not read in version 1**. Amendment 1's REMIT sighting
  beside the proxy is deferred to a later version; no label or figure of
  version 1 depends on it.
- **S4 ENTSO-E** stays outside (no token, no schema pass).
- **S1** is the 30/09/2026 vintage only (B2). A unit deregistered before
  that day and absent from the vintage cannot be proposed; where that
  happens it shows as `no-candidate`, and F2 counts it.

## What does not change

The declaration's question, P1, the "never claims" list, C1 to C6, the
reference dates of amendments 1 and 2, the labels of version 0.1, and the
sponsor's instruction that the results renderings, the proposals and the
admissions stay out of the public repository until he says (held on disk,
ignored by git, like 019's).

## Order

1. This file is frozen. 2. J1 proposals from the pinned S1 (no fetch);
the pre-screen to the sponsor. 3. His admissions, written by the session.
4. The walk for admitted projects, under this file's seal; the format
check over every window. 5. Compute version 1; RESULTS to the sponsor
before anything public.
