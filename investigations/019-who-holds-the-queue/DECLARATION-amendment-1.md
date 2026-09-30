# 019 — Who holds the queue: amendment 1 (the names the rule could not see)

**Written 2026-09-30, after the first run under `DECLARATION.md`
(SHA-256 `877682f7…`) and approved by the sponsor the same day.** Frozen by
`scripts/freeze` before any request or figure under it. It amends rule R2's
search set and its previous-name route and nothing else. `DECLARATION.md`
stands; every line already in `evidence/links.ndjson` stands.

## Prior exposure, stated

The author has seen the first run's four figures: resolution 1,302 of
1,375 names (F1 and F2 silent); one row under a company under a year old;
1,732 name-change events with both names resolved for 30 % of them, so
**F3 fired**; 633 rows under a company with a live charge. The author has
also seen the 73 proposals (26 ambiguous, 47 unresolved) with their
candidate titles, among them a name whose current company is a renamed
one that R2 could not reach. This amendment is written knowing all of
that. Its purpose is to let the rule see names it was blind to by
construction, not to reach a figure; F3 is re-tested under it and may
fire again.

## Why F3 fired

R2 searched **the names printed in the copy** (R1). Figure 3 compares
**consecutive names on one project id across the history**, and the
earlier name of a pair is, by definition, usually no longer printed. It
was therefore never searched, and the pair could not be classed. The
count of such names is written by the run, not stated here.

The second blindness is the previous-name route: R2 reached previous
names only through the advanced search, which matches **current** names.
A company renamed away from the register's name never appears there. The
public search endpoint itself marks a hit matched on a previous name (its
`snippet` carries the previous name); the first run pinned 1,375 such
responses, and the schema report shows the field present on 3,549 hits.

## A1 — the search set

R2 runs, unchanged in its steps, over one further set: every distinct
printed customer name (R1's normalisation) that `evidence/name-history
.json` records against any project id present in the copy and that is
**not** printed in the copy (*the earlier names*). Each is searched once,
classed by R2 as amended below, and written to `links.ndjson` under the
rule version of this amendment. Earlier names carry no rows or MW of the
copy; they enter **figure 3 only**. The identity guard applies to them
with their own first-seen date.

## A2 — previous names through the search endpoint

For a name with no exact candidate (either set), before the advanced
search: a search hit whose `snippet` normalises (`normalise_company_name`)
to the name is a **previous-name candidate**. Its profile is pinned. It
resolves, class `previous-name`, only if the profile's
`previous_company_names[].name` normalises to the name (the snippet
proposes, the profile confirms). Exactly one confirmed candidate resolves;
several are `ambiguous`; none sends the name on to the advanced search as
R2 already says. The identity guard applies.

## A3 — versions

The rule version becomes `019-r2-v2`. Lines under `019-r2-v1` are never
rewritten; the run appends v2 lines for every name in both sets (a name
whose v2 class equals its v1 class still gets its v2 line, so v2 is
complete on its own). Admissions (`links-admitted.json`) apply to v2 as
they applied to v1. Figure 1 is reported under v1 and v2 side by side;
figures 2 and 4 under v2; figure 3 under v2 with F3 re-tested. Nothing
already computed is deleted.

## A4 — requests

At most one search per earlier name, the advanced search and candidate
profiles where R2 calls for them, and the four resources of every company
newly resolved, at the declared rate; C5 unchanged.

## What does not change

R1, R3 to R6, the copy, the schema pass, C1 to C7, F1 to F4, the PSC-name
rule, and the sponsor's instruction that nothing about ownership leaves
the repository from this run. The sponsor has further directed
(30/09/2026) that the ownership tables and RESULTS.md stay out of the
public repository until the admissions and this amendment are in; they
are held on disk and ignored by git, and that deviation from the
declaration's "Outputs" is recorded here.
