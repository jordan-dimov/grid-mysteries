# 020 — Did it energise: amendment 2 (stages dated after the first `Built` copy)

**Written 2026-09-30 after version 0.1 under amendment 1 (SHA-256
`cc01e3cf…`); the sponsor's word to freeze came the same day.** Frozen by
`scripts/freeze` before any recompute. It amends amendment 1's per-project rule A1 by
naming a population A1 left inside the measure: the capacity-bearing stages
whose printed date lies **after** the copy in which the project first
prints `Built`. Under A1 such a stage can be the "last dated
capacity-bearing stage" and pull the project's reference date into the
future, so that a project reads as `Built` before its date by years. This
amendment separates that population and reports the measure with and
without it, both medians shown.

## Prior exposure, stated

The author has seen version 0.1: 164 projects measured, median 3.4 months
from the latest capacity-bearing dated stage to the first `Built` copy,
27 projects negative, minimum −113.8 months, and the sensitivity on the
earliest date (median 4.3). The author has also seen, in the per-unit
version 0, that the most negative values were stages with a future date
against a project already `Built`. This amendment is written knowing
that; its purpose is to name that population and count it, not to choose
the median the sponsor prefers.

## A1′ — the later stages, as a population of their own

For each project (014's group, per regime) with a first `Built` copy and a
kept copy immediately before it, the project's capacity-bearing (MW > 0)
dated stages in that copy before are split by their printed date against
the **publication date of the first `Built` copy**:

- **on-or-before stages**: date on or before the first `Built` copy's
  date;
- **later stages**: date strictly after it.

Later stages are a population of their own, listed per project with their
stage label, MW and date, and counted in aggregate: projects with at
least one later stage, their number of later stages, and the MW those
stages carry. They are neither dropped nor called wrong; a later stage is
a further connection the register still expects, printed against a
project that is already `Built` for its earlier capacity.

## A1″ — the measure, twice

The per-project measure of amendment 1 is computed **twice** over the same
projects and reported side by side, each with its own n, quartiles and
median, its shares before, within six months and later, and its
breakdowns by year of the `Built` copy and by plant type:

- **with later stages** (amendment 1's A1 exactly: the latest date among
  all capacity-bearing dated stages);
- **without later stages**: the latest date among the on-or-before stages
  only.

A project whose capacity-bearing dated stages are **all** later stages has
no reference date in the second measure; it is labelled *only later
stages* and counted, and it stays in the first measure. The difference
between the two medians is reported as a number with its sign, and the
projects that move from negative to non-negative are listed.

The earliest-date sensitivity of amendment 1 is kept for both.

## What does not change

The project, the first `Built` copy, the copy immediately before, the
exclusion of zero-MW stages, the labels *Built at first sight*, *undated
before Built* and *not sighted in the copy before*, C1 to C6, F1 to F4,
the proxy A2, and the sponsor's instruction that the results renderings
stay out of the public repository until the admissions and amendments are
in. Version 0 and version 0.1 stand as computed; this recompute is
version 0.2, written beside them in `evidence/projects-v02.ndjson`
(append-only) and `evidence/projects-v02-summary.json`.

## What this never claims

- That the second measure is the true one. Which stage a lender's date
  refers to is a fact about the contract, not the register; both
  measures are the register's own account under two readings.
- That a later stage will be built, or will not.

## Order

1. The sponsor's word; `scripts/freeze`. 2. Version 0.2 computed from the
archive alone; both medians to the sponsor by 5 October 2026. 3. Nothing
else changes.
