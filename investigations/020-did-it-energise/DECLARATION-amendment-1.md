# 020 — Did it energise: amendment 1 (the project, the date, and the proxy)

**Written 2026-09-30 after the schema pass and the register-only version 0
under `DECLARATION.md` (SHA-256 `fb8a3428…`); the sponsor asked for it the
same day.** Frozen by `scripts/freeze` before any recompute. It states
the reading rules the declaration left to the schema pass: the unit of
measure on the register side, the date the measure runs from, the
first-metered-output proxy, and what the schema pass removed.

## Prior exposure, stated

The author has seen version 0: 215 per-unit transitions, 201 measured, a
median of 4.0 months from the last printed date to the first `Built`
copy, and the post-hoc observation that 146 of the 201 measured units
carry a stage MW of 0, with the largest negative values on such rows. The
per-project rule below is written knowing that. Version 0 stands as
computed (`evidence/population.ndjson`, append-only); this amendment's
recompute is version 0.1 and is written beside it, never over it.

## A1 — the project, and the last dated capacity-bearing stage

- **The project** is 014's project group: the normalised (project name,
  customer name, connection site) triple, which is also the group of
  `tec-identity-content-v1`. Every unit of the group belongs to the
  project; a project can have several stages in one copy.
- **The first `Built` copy** of a project, per regime, is the first kept
  copy in which any of its units prints `Project Status` = `Built`.
- **The reference date** is read from the kept copy immediately before
  that one. Among the project's units in that copy whose stage MW
  (`MW Increase / Decrease`) is greater than zero and whose effective date
  parses under 014's reading (swap test included), the reference date is
  the **latest** such date: the last dated capacity-bearing stage, the
  date by which the project's capacity was, as then printed, to be
  connected. Zero-MW and negative-MW stages never supply the date.
- **Declared sensitivity**: the earliest such date, reported beside.
- **Labels**: a project whose first sighting already prints `Built` is
  *Built at first sight*; a project with no capacity-bearing dated stage
  in the copy before is *undated before Built*; both are counted, neither
  measured. A project that prints `Built` on one stage and not another in
  the same copy is measured from the first copy any stage prints it, and
  the split is listed.
- **The measure** is unchanged in arithmetic: months from the reference
  date to the first `Built` copy's publication date, published as a
  distribution by year of that copy and by plant type as printed, with
  the shares before, within six months after, and later; plus the
  project's capacity, the sum of its positive stage MW in the copy before.
- Version 0's per-unit measure is not recomputed and is not compared as
  if it were the same quantity.

## A2 — the first-metered-output proxy

For a project with one or more admitted BM units (J1, J2 of the
declaration), read only after admission:

- **B1610** (`datasets/B1610/stream`, per settlement day, filtered to the
  admitted units) is requested in windows of seven settlement days,
  walking **backward** from the run date to the earlier of the project's
  first sighting in the archive and 2015-01-01, and stopping early at the
  first window the API answers with no record for the unit after a window
  with records (the unit's metered series has begun). Every window is
  pinned once. The **proxy** is the earliest settlement day in the pinned
  windows on which `quantity` is greater than zero for any admitted unit.
  Testing output counts, as the declaration says.
- **Labels**: `metered` (a proxy day exists); `registered-not-metered`
  (records exist but none above zero); `no-metered-record` (no B1610
  record in any window); `embedded-or-distribution` (J3, from the row's
  `Agreement Type` and `HOST TO`, only when no unit was admitted).
- **The realised delay** is months from A1's reference date to the proxy
  day; the register's own lag is months from the proxy day to the first
  `Built` copy. Both are distributions, never one number.
- **REMIT** (S3): the earliest `eventStartTime` among messages whose
  `affectedUnit` or `affectedUnitEIC` names an admitted unit, from the
  by-event history the schema pass showed is served (2018 onward), is
  reported beside the proxy as a second sighting of commissioning. It is
  never combined with B1610 into one date.

## A3 — what the schema pass removed or changed

- **Registration date** leaves the question: `reference/bmunits/all`
  serves no date field (F3's route). S1 names units, lead parties,
  capacities and fuel types; it is J1's candidate list, nothing more.
- **The BM-unit threshold** of J3 is withdrawn: B1610 on the sample day
  covered 9,152 units including supplier units, so absence from B1610 is
  not explained by size. J3 keeps only its distribution test.
- **ENTSO-E (S4)** is outside this version until a token is held and a
  schema pass is committed; no label depends on it.
- **B1610 is never read whole**: one day is about 100 MB; it is read per
  admitted unit as A2 says.

## Order

1. This file is frozen. 2. Version 0.1 (A1) is computed from the archive
alone and reported to the sponsor beside version 0. 3. J1 proposals are
written from S1 for the projects of P1 and P2; the sponsor admits. 4. A2
runs for admitted units only. 5. Compute; findings to the sponsor before
anything public. The sponsor has directed (30/09/2026) that the results
renderings stay out of the public repository until the admissions and
this amendment are in; they are held on disk and ignored by git.
