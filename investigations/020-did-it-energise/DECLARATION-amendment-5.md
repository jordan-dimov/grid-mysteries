# 020 — Did it energise: amendment 5 (the population over the archive with the hole filled)

**Written 2026-10-15 on the sponsor's decision of that day (etrmbiz
`notes/2026-10-15-grid-mysteries-prompt-020-amendment-5.md`).** Frozen by
`scripts/freeze` before any value is computed under it. It amends
amendments 3 (`f84367c3…`) and 4 (`fab5665e…`) in one respect: the
population is drawn again over the archive **as it now stands**, with the
83 copies of NESO's EIR response FOI/26/216 (publication dates 2025-07-25
to 2026-05-15) journalled on 2026-10-15 under the source label
`neso-foi-email` (`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-216.md`).
Every other rule stands. The purpose is the joint paper with Mark Moore
(outline due 23/10/2026, draft 13/11/2026): the register-lag figures for
2025 and 2026 that he holds were computed under amendment 4 with a 301-day
copy gap bounding every value in the hole, and the bound is gone. The aim
is a computed amendment by 21/10/2026; if that cannot be met, the
grid-mysteries session says so by 20/10 and the outline carries the
amendment-4 figures labelled as bounds.

## Prior exposure, stated

- **The finding of 2026-10-15** (`AMENDMENTS.md`), measured in memory and
  never written: over 791 usable and 789 kept copies, 1,719 units have a
  first `Built` sighting against 1,672 committed lines; 1,296 unchanged;
  373 would change, all reformed regime, their first `Built` copy moving
  from 2026-05-19 into the hole (the first to 2025-12-02), 11 changing
  customer, 3 changing the copy before; 50 units new (29 reformed, 21 old
  regime); 3 committed units lose their first `Built` sighting under the
  same key.
- **The archive's gaps** after the journalling: no gap over 7 days between
  2025-07-22 and 2026-05-19; gaps over 14 days remain at 2025-01-28 to
  2025-03-21 (52 days), 2025-04-01 to 2025-07-01 (91), 2025-07-01 to
  2025-07-22 (21), 2026-05-19 to 2026-08-22 (95), 2026-08-25 to
  2026-09-15 (21); the `Gate` column's era dates from 2025-11-21.
- **The figures Mark holds**, computed 2026-10-12 under amendment 4
  (`evidence/results.json` SHA-256 `ae26cda21c0ea18a…`, `RESULTS.md`
  `83e2ebc3b2881cf6…`, `figures/captions.md` of 14/10/2026), which are the
  "before" column of every comparison this amendment prints: realised
  delay median 4.1 months (95 % interval 3.0 to 6.0; interquartile range
  2.0 to 8.4; n 59; 9 before the date, 28 within six months, 22 later;
  storage 5.5, onshore wind 3.4, offshore wind 3.6); register's lag median
  3.0 months (1.3 to 4.4); by year of the `Built` copy about 1 month in
  2022 and 2023 (0.9 and 1.8), 6.0 in 2024 (1.3 to 10.6, n 9), 7.1 in 2025
  (2.0 to 13.1, n 15), 8.1 in 2026 (4.2 to 9.8, n 9).
- **The author expects the 2025 and 2026 lags to fall.** That expectation
  is exposure, not a result, and F5 below is written so that the finding
  is said either way.
- No population line, proposal, walk or figure has been computed under
  this amendment.

## A5.1 — the population over the archive as it stands

The population step (`run.py --phase population`), the per-project rule
(A1, `--phase projects`) and the later-stages reading (A1′ and A1″,
`--phase projects-v02`) are re-run over every copy the repository holds on
the run date: the journal at SHA-256 `81d37bc3f4b430e0…` (835 rows, 815
publication dates, 2014-01-31 to 2026-09-15) and the daily capture's
manifests to the run date, read as the declaration reads them (one copy
per publication date, each verified against its recorded digest, 014's
reading rules, the partial-export rule, the day-month swap test, the
content identity stepped copy by copy). **The evidence of amendments 1 to
4 is not touched**: this amendment's lines are written under
`evidence/a5/` (the same file names), each file append-only from its first
line under C2, and `RESULTS.md` as computed under amendment 4 is kept as
`RESULTS-a4.md` beside the new one (as `RESULTS-v0.md` is kept), since the
14/10 captions cite it.

- The copy gap at a project's first appearance is, as amendment 4's A1
  says, the days since the kept copy before it in the combined sequence,
  now without the 301-day value. **The 95-day gap of 2026-05-19 to
  2026-08-22 is the bound that remains** for first sightings in that span,
  and it is stated wherever a 2026 figure is printed.
- The units that no longer have a first `Built` sighting under the same
  key (3 at the finding) are **recorded with the reason** in
  `evidence/a5/population-summary.json` and in RESULTS.md, not dropped
  silently; the reason is read from the sightings (the key's rows are
  carried differently by the content identity through the added copies,
  or the key's first sighting already prints `Built`).

## A5.2 — admissions carried over, and the pre-screen for the rest

J1 runs as amendment 3's B2 declares, over this amendment's version-0.2
projects, against the same pinned S1 vintage (`0f0902e1…`), into
`evidence/a5/links-proposed.json`. Then, per project with a candidate:

- **An admitted link stands** where the project's key is unchanged and the
  admitted unit or set is among the candidates J1 now proposes for it: it
  is carried into `evidence/a5/links-admitted.json` verbatim (decision,
  units, date, initials, reason), marked `carried_from_amendment_4`. A
  changed first `Built` copy or copy gap is not a new link.
- **A refusal stands** where the key is unchanged and J1 now proposes the
  same set of candidate units as it did on 2026-10-12.
- **Every other project with a candidate** (a key with no amendment-4
  decision, or one whose candidate set changed, or whose admitted units
  are no longer proposed) goes to a **pre-screen in the 12/10 form**
  (admit, doubtful with a lean, refuse, nothing found; the reading rule
  restated at the top), `evidence/a5/prescreen.md`, numbered from 1 under
  this amendment. The pre-screen goes to the etrmbiz session, which
  decides every row on the sponsor's standing delegation of 12/10/2026 and
  returns the answers; the grid-mysteries session writes the decisions
  into `evidence/a5/links-admitted.json` dated and initialled "JD
  (delegated to Claude)". **A unit J1 did not propose cannot be admitted**
  (B3). The pairs to report and the crossed unit names of 12/10 carry over
  where their keys do.

## A5.3 — walks

- For a carried admitted project whose B1610 walk of 2026-10-12 is pinned
  (`evidence/walks.json`, `data/raw/elexon/2026-10-12-020/b1610/`),
  **nothing is fetched again**: the walk ran backward from 2026-10-12 to
  the first empty window after records, so every window that could carry
  the project's earliest metered day is pinned, and a later run date would
  add only windows after 2026-10-12, which cannot move the earliest day.
  The pinned windows are re-hashed (C3) and format-checked as before.
- For a newly admitted project, B1610 is walked under amendment 3's B4 and
  amendment 4's A2 (the served floor), under the run date of the walk,
  pinned under `data/raw/elexon/<run-date>-020/b1610/`. If a carried
  project would need a re-walk for any reason, the run says which and why
  and stops.
- `evidence/a5/walks.json` names each project's pinned folder.

## A5.4 — what is computed

The labels, C6 (A1 of amendment 4, over the filled sequence), A3's second
sightings, A4's embedded plant, F1, F2 and F4, the realised delay under
both readings, the register's lag with each project's copy gap beside it,
by year of the first `Built` copy and by plant family, the bootstrap and
Wilson intervals with the declared seed, for the **whole** population of
this amendment, as amendments 3 and 4 declare. Then:

- **RESULTS.md** carries, after the amendment-4 sections rendered anew, a
  section **"Amendment 5 against amendment 4"** with one table: every
  figure Mark holds in the "before" column (from the amendment-4
  `results.json`, digest above), the amendment-5 figure beside it, n and
  intervals for both, and which of F5 and F6 fired.

## Falsifiers, published with the result

- **F5** The register-lag median for 2025 or 2026 (year of the first
  `Built` copy) moves outside its amendment-4 bootstrap interval (2025:
  2.0 to 13.1; 2026: 4.2 to 9.8): then the hole was carrying the finding,
  which is itself the paper's point about archive cadence, and it is said
  as such.
- **F6** The realised-delay median (with later stages, overall) moves by
  more than 1.0 month from 4.1: then the sample given to Mark was not
  representative, and the outline's number is **withdrawn**, not restated
  quietly.

## Figures

The two charts of 14/10/2026 are redrawn under this amendment to
`figures/` with the same conventions: the hole shading of chart 2 removed
and replaced by a shaded span for 2026-05-19 to 2026-08-22 labelled
"95-day gap, values are lower bounds"; the captions rewritten with this
amendment's medians, intervals and n; `figures/captions.md` carrying the
cadence line "no gap longer than 95 days since 2021, and none over 7 days
across the reform period, 22 July 2025 to 19 May 2026", never "no gap".

## What does not change

The declaration, amendments 1 to 4 and their evidence; the S1 vintage; the
pinned windows of 2026-10-12; the bootstrap and Wilson intervals and their
seed; the labels' vocabulary; and the instruction that the results
renderings, proposals and admissions stay out of the public repository
until the sponsor says (held on disk, ignored by git). Nothing goes to
Mark from the grid-mysteries session; etrmbiz writes the correction note
to him with the table.

## Order

1. This file is frozen. 2. Population, projects, projects-v02 under
`evidence/a5/`. 3. J1 proposals; admissions carried; the pre-screen to the
etrmbiz session. 4. Its answers written as admissions. 5. Walks for the
newly admitted. 6. Compute; RESULTS.md with the comparison; the charts.
7. Report to the sponsor.
