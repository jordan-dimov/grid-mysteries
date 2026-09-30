# 020 — Did it energise: outcome labels for the TEC Register, declaration

**Status: draft for the sponsor's eye, written 2026-09-30. Not frozen, not
sealed, nothing fetched, no figure computed.** On the sponsor's word it is
frozen by `scripts/freeze` and run under the seal the sponsor gives.
Changes after the freeze are amendments.

## The question

> For every project the archive of NESO's TEC Register shows moving to
> `Built` since 2014, and for every row the latest copy prints in the
> confirmed tier (`Gate` = `2`), what do public, dated sources outside the
> register say about whether and when the plant actually produced: the
> Elexon registration of a balancing-mechanism unit, its first metered
> output, its REMIT history, and its presence in ENTSO-E's unit lists?

The register's series (014) measures how a printed date moved. This
measures how far the plant came on after the date it carried: the
**realised delay**, in months, from the last date the register printed
before `Built` to the first metered output. It also labels the rows whose
date never moved and whose plant never appeared anywhere: the register's
placeholders. That label is the missing half of 014 and 017, and the
number a lender or underwriter asks for.

## What must happen before any reading rule is final

The sources below are named from public documentation and from what the
repository already holds; **their schemas for this purpose have not been
inspected**. The doctrine is schema pass, freeze, results. This file is
therefore frozen with the questions, the population, the join rule, the
checks and the falsifiers, and with the *candidate* sources; the reading
rule for each source is completed as a **witnessed amendment written from
its schema report alone**, before any figure. The order is: pin one
sample of each source, `scripts/schema-report` over it, amendment,
acquire, compute.

## Population, declared now

- **P1 — Built transitions.** Under 014's identity (`tec-identity-content
  -v1`, `src/grid_mysteries/tec/identity.py`, as version 4 declares it),
  every unit whose `Project Status` reads `Built` in a copy and did not in
  the copy before, across every copy in the tec-history journal and the
  daily capture from January 2014 to the copy named in P2. For each: the
  last copy before `Built` and the date it printed (`MW Effective From`,
  014's reading rules with the swap test), the first copy printing
  `Built`, the customer name, the connection site, the stage MW, the
  `Project ID` where the era prints one. Units first seen already `Built`
  are a separate class, *Built at first sight*, labelled but not
  measured.
- **P2 — the confirmed tier now.** Every row with `Gate` = `2` in the
  captured copy with CKAN `last_modified` 2026-09-29 (SHA-256
  `d1ccd9e2…`, `data/manifests/2026-09-30.ndjson`), 103 rows by the
  capture schema report (`857dfc88…`, `f14c960`), whatever their status.

Prior exposure: the author knows the copy-level counts of `Built` rows
per captured copy (377 to 381, from the schema report) and 014's published
series; no per-unit transition list has been computed for this question.

## Candidate sources, and what each can say

| source | what it dates | where it is, as far as is known now | schema pass needed |
|---|---|---|---|
| **S1 Elexon BM-unit reference** (`reference/bmunits/all`, Insights API; one vintage pinned at `data/raw/elexon/case-001/bmunits.json`, 3,053 units) | a unit's existence, lead party, capacities, fuel type. **The pinned vintage carries no registration date.** | pinned; the API's current fields must be re-read | whether any field or any other Elexon reference (the BSC's registered-BM-unit reports on the Elexon Portal) carries an effective-from date; if none, "registration date" is dropped from the question and S1 serves only to name the unit |
| **S2 Elexon metered output per unit** | the first settlement day with non-zero metered volume: the *first metered output* | B1610 (`datasets/B1610/stream`, per settlement day and unit, already used by 012/015/016 through `sources.elexon`); and the settlement reports S0142 (`archives/elexon-s0142/`, every unit's metered volume per period, Elexon Portal key) | B1610's unit coverage (it is understood to cover only larger units; the report says which of P1's units appear at all); S0142's per-unit metered record type and its date range on the portal; the cost of the earliest year needed |
| **S3 REMIT** (Elexon Insights REMIT endpoints; captured daily since 15/09/2026 by the capture plan's `ELEXON-REMIT` resource; historical listing by event via the same API) | a unit's first and later unavailability messages, with `eventStart`, `publishTime`, revision and withdrawal; a message before first output dates commissioning | the daily capture holds only messages published since 15/09/2026; earlier messages must be listed from the API by event time | field names, the asset identifiers used (BM unit, EIC, asset name), the earliest event date the API serves |
| **S4 ENTSO-E Transparency** (production and generation units, installed capacity per unit) | a unit's presence in a yearly list, with EIC and installed capacity; **no commissioning date** | Transparency Platform REST API with a registered token (repository holds none) | which years of the list are served for GB after Brexit (GB data on the platform thins after 2020, which the report must state), the EIC join to S1's `eic` field |
| **S5 the register itself** | the `Built` transition and the copy bounds around it (P1) | archive | done (the capture report and 014's journal report) |

No other source is read. Planning portals, company announcements and
news are not sources for this question; they date promises, not output.

## The join, declared now

Register units carry a name, a customer, a site and MW; Elexon units carry
a `bmUnitName`, a `leadPartyName`, capacities and (S4) an EIC. There is no
key. The join is therefore **proposed by rule and admitted by a person**,
the doctrine already in force:

- **J1 — proposal.** For each population unit, candidate BM units are
  those whose `bmUnitName` or `leadPartyName`, normalised (005's rule),
  shares a token of four letters or more with the project name, customer
  name or connection site, **and** whose `generationCapacity` (or, for
  storage, `demandCapacity`) is within 25 % of the stage MW or of the
  unit's cumulative MW. Each candidate is written with its score (tokens
  shared, capacity ratio, fuel type against `Plant Type`).
- **J2 — admission.** A person admits at most one BM unit (or a set of
  units for a project split across several) per population unit, or
  records *no unit found*, in `evidence/links-admitted.json`, dated and
  initialled. A candidate with all three of: an exact normalised project
  name match, capacity within 5 %, and matching fuel type, is *proposed as
  exact*; it is still admitted by a person, because the reference has no
  key and names are reused.
- **J3 — embedded plant.** A Built transition whose row's `Agreement Type`
  or `HOST TO` show a distribution connection, or whose MW is below the
  BM-unit threshold the schema pass records, is expected to have no BM
  unit; it is labelled *embedded or below threshold*, not *unmatched*.

## What is computed, declared now

For P1 (Built transitions), per unit and in aggregate:

1. **Label**: `metered` (an admitted unit with a first metered day),
   `registered-not-metered` (admitted unit, no output in S2 by the run
   date), `embedded-or-below-threshold`, `unmatched` (candidates
   proposed, none admitted), `no-candidate`.
2. **Realised delay** for `metered`: months from the last date the
   register printed before `Built` to the first metered day; distribution
   by year of the `Built` transition and by `Plant Type`; the share of
   units metering before, within six months after, and later than that
   date. Also the months from first metered day to the first copy printing
   `Built`: how long the register takes to say so.
3. **Placeholders**: units whose printed date never moved across their
   life in the archive **and** whose label is `unmatched` or
   `no-candidate`, listed by year of the date, MW and status; published as
   a count and a list, never as "phantom capacity".

For P2 (Gate 2 rows now): 4. label as above, and whether any admitted unit
already meters (a Gate 2 row already producing is either a stage of a
built site or a register lag; both are listed, neither is asserted).

## Checks each run must pass, or it stops

- **C1** Every copy read hashes to its journal or manifest digest.
- **C2** P1 is a pure function of the archive under 014's identity; a
  committed transition line that would change on recompute stops the run.
- **C3** Every source response is pinned once, digest in the manifest,
  before it is read.
- **C4** Every population unit is in exactly one label class; classes sum
  to P1 and to P2.
- **C5** J1's proposals are reproducible offline from the pinned bytes
  (`links-proposed.json` line for line).
- **C6** No first-metered day precedes the unit's first appearance in any
  register copy by more than the archive's own gap at that point (a
  metering day years before the project existed is an identity error and
  sends the link back to the person).

## Falsifiers, declared in advance

- **F1** If the schema pass shows S2 covers fewer than half of P1's units
  above the threshold it records, the realised-delay distribution is not
  published as a population figure; it is published for the covered
  units with the coverage stated, and the question is marked *partly
  determinable*.
- **F2** If fewer than 60 % of P1 units above threshold receive an admitted
  link, figures 2 and 3 are *not determinable* and figure 1 is the
  outcome.
- **F3** If no Elexon source carries a registration date (S1 column of the
  table), "registration date" leaves the question by amendment and the
  finding says so.
- **F4** If more than 5 % of admitted links fail C6, the join rule J1 is
  unfit and every link is re-proposed under an amended rule against the
  same pinned bytes, with both proposals kept.

## What this never claims

- That a `Built` row without a BM unit is not built; most connections
  below the balancing-mechanism threshold, and every distribution
  connection, leave no trace in S1 to S4.
- That the first metered day is commissioning; testing output is output.
- That a placeholder row is fictitious; it is a row whose date never moved
  and whose plant has left no public trace in these sources, and that is
  all the label says.
- Anything about the register's *future* dates; the realised delay is
  measured only where the outcome is already public.

## Order of work

1. Sponsor reads this; freeze. 2. One sample of each of S1 to S4 pinned
under the seal; `scripts/schema-report` for each; **amendment 1** states
the reading rules and the thresholds from the reports and is frozen. 3. P1
and P2 computed and committed (archive only, no source read). 4. Acquire:
S1 vintage, S3 listing, S4 list, then S2 for admitted units only, from
their first register appearance to the run date. 5. Proposals to the
sponsor; admissions. 6. Compute; RESULTS.md to the sponsor. Findings go to
the sponsor before anything public. One to two weeks after the freeze.

## Outputs

- `evidence/population.ndjson` (P1 and P2, append-only),
  `evidence/links-proposed.json`, `evidence/links-admitted.json`
  (human-written), `evidence/labels.ndjson`, `evidence/results.json`,
  `RESULTS.md`, `evidence/rule-sources.json`.
- `archives/elexon-bmunits/`, `archives/elexon-b1610/`,
  `archives/elexon-remit/`, `archives/entsoe-units/`: the schema reports.
- Raw responses under `data/raw/<source>/<run-date>-020/`, local, digests
  in `evidence/manifest.json`.
