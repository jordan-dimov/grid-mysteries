# 019 — Who holds the queue: the Companies House join, declaration

**Written 2026-09-30 as a draft for the sponsor's eye (committed at
`6ce2452`, amended once for prior exposure at `6a55f13`); approved by the
sponsor the same day, with the fetch sealed in the same word.** Frozen by
`scripts/freeze` (OpenTimestamps and RFC 3161 witnesses, committed with its
proofs); nothing was fetched before this freeze, and the fetch runs under
the seal, this file's digest prefix. Changes after the freeze are
amendments, never edits.

## The question

> Of the customer names printed in one copy of NESO's TEC Register, how
> many resolve to one company at Companies House, and what does the public
> register of companies then say about who holds the queue: how many rows
> sit under a company less than a year old; how many of the register's own
> customer-name changes are a company renaming itself against a transfer to
> a different company; and how many projects sit under a company with a
> registered charge against none?

This is an **ownership layer**, not a verdict. Nothing about any company,
owner, lender or project is published from this run; the output is a
governed table of admitted links and four counts, held in the repository
for the sponsor's use.

## Why it is asked now

The register prints a customer name and nothing else about the customer.
Three scratch reads made outside this repository on 30/09/2026, unsealed
and recorded here as **prior exposure**, showed the name changing under a
project without the project changing: a battery project's customer moving
from a group company to a project company of the same group; a project
company renamed from a generic development vehicle to a site-named one; a
power station whose customer printed three names in turn. The register
cannot say which of these is a rename and which is a sale. Companies House
can, dated. 009's records (2026-08-27) are of other names for another
question and are not reused. **Further prior exposure, recorded after the
first draft:** on 30/09/2026, for the offer-date inventory
(`ops/OFFER-DATE-SOURCES.md`), a research agent under this session read
the public Companies House pages of the three watch-list customers
(Zenobe Stalybridge Limited, Hunterston Grid 1 Ltd, Middleton Energy
Storage Limited): company numbers, incorporation dates, previous names
with their dates, and the names of sibling companies at one address. No
persons with significant control and no charges were read. Those three
names will resolve under R2 whatever this exposure; nothing about them is
counted before the run, and the exposure is stated so a reader can weigh
it.

## Inputs

- **The copy.** The captured copy of the TEC Register with CKAN
  `last_modified` 2026-09-29T12:18:57.526163 (NESO filename
  `tec-register-28-september-2026.csv`), SHA-256
  `d1ccd9e210b4f6bc8f3b0e83d54032dc61f247dbbc1d9e469a342b7766ee5746`,
  440,851 bytes, recorded in `data/manifests/2026-09-30.ndjson`, read from
  the local mirror after its bytes are checked against that digest.
- **The schema pass it is written against.**
  `archives/tec-register-capture/schema-report.json`, SHA-256
  `857dfc88949a95b3553d96fa25bd84fbed6f4ed433f1090f324140b644975ebd`,
  committed at `f14c960`. It is cited for three facts about this copy:
  2,199 rows; the fifteen columns of the current era, `Customer Name` and
  `Project ID` among them; and no blank `Customer Name` cell. No count of
  distinct names is in that report. The author has since run one command
  over the copy that counted **1,375 distinct printed customer names (1,374
  case-insensitively), of which 9 carry no company suffix (Ltd, Limited,
  PLC, LLP)**. That count selects nothing and is recorded as prior
  exposure; it is recomputed and published by the run.
- **The history, for the rename question only.** Every copy of the register
  that prints a `Project ID` column: the tec-history journal
  (`data/raw/neso/tec-history/journal.ndjson`) from the first copy that
  carries the column (November 2021, per `tec_register.py`'s era notes)
  to its last, and the five captured copies from 15/09/2026 to the copy
  above, each read after its digest is checked. The journal is not
  changed.
- **Companies House.** The Public Data API
  (`api.company-information.service.gov.uk`), read with the key in
  `COMPANIES_HOUSE_API_KEY` through `sources.companies_house
  .AuthenticatedFetcher` at no more than one request per 0.55 s. Four
  resources per company: the company profile, the persons-with-significant-
  control list and its statements, and the charges list; plus company
  search for each name. Every response is pinned once, bytes and digest,
  including 404 bodies (an empty charges list is evidence). Requests are
  sent once; no response is refreshed inside the run.

Nothing else is read. No web page, no news, no register other than the
two named.

## Schema pass of the fetched responses, before any figure

The Companies House responses do not exist yet, so no schema pass covers
them. The run therefore has three phases, each committed before the next:

1. **acquire** — search, resolve by rule (R2), and pin the four resources
   for every company the rule resolves or a person admits; write the
   proposed-links table.
2. **schema** — `scripts/schema-report companies-house` over the pinned
   responses: for each endpoint, the fields present and their blank rates,
   the spellings of `company_status`, PSC `kind`, charge `status`, and the
   date formats. Committed under `archives/companies-house-019/`.
3. **compute** — only if the schema report shows every field named in R3
   to R6 present in at least 99 % of the responses that should carry it,
   and only the spellings those rules name. Otherwise an amendment
   restating the affected rule is frozen first, written from the schema
   report alone.

The field names below are from Companies House's published API
specification. They are declared now so that the schema pass tests them
rather than teaches them.

## Reading rules

**R1 — the unit and the name.** The unit is the distinct **customer name as
printed** in the copy, after collapsing runs of whitespace; case is kept
(two names differing only in case are two names, and the run reports how
many such pairs exist). Each name carries the rows and the stage MW
(`MW Increase / Decrease`) printed against it, and the 15-character
`Project ID` of each row (017's `project_id`).

**R2 — resolution, proposed by rule, admitted by a person.** For each
name, `search/companies?q=<name>` (20 hits, pinned). Candidates are hits
whose `title` normalises to the name under `companies_house
.normalise_company_name` (case, punctuation, `&`, and LTD/LIMITED,
PLC, LLP, CO suffixes), dissolved companies included.

- **Exactly one candidate**: *resolved by rule*, class `exact`.
- **No candidate**: `advanced-search/companies?company_name_includes=
  <name>` (pinned); each hit's profile is pinned and its
  `previous_company_names[].name` checked for a normalised match. Exactly
  one such hit: *resolved by rule*, class `previous-name`. Otherwise the
  name is *unresolved by rule*, and the three search hits with the highest
  Companies House rank are written to the proposed-links table for a
  person to admit or refuse.
- **Several candidates**: none is chosen by rule. All are written to the
  proposed-links table with their `company_status`, `date_of_creation` and
  `date_of_cessation`; a person admits at most one.
- **Identity guard**: a rule-resolved company whose `date_of_creation` is
  later than the earliest register copy in which the name is printed
  against any of its current project ids is *not* resolved (a reused
  name); it goes to the proposed-links table with that fact stated.

Admission is a human act recorded in `evidence/links-admitted.json`: name,
company number, the class `admitted`, the date, and the initials of the
person. The machine never writes that file. A refused proposal is
recorded as `refused` with the same fields. The table of links
(`evidence/links.ndjson`) is append-only and versioned: every line carries
the rule version, the run date and the digest of the search response it
was proposed from, and a later admission adds a line, never edits one.

**R3 — age.** From the profile, `date_of_creation`. A company is *under a
year old* if that date is on or after 2026-09-29 minus 365 days, that is
on or after 2025-09-29. Rows and MW are counted, not names.

**R4 — the register's own name changes, rename or transfer.** For each
15-character project id present in the copy, the sequence of distinct
customer names printed against it across the history copies in
`t_public` order, one reading per distinct copy digest. Each pair of
consecutive distinct names is a *name-change event*, dated by the first
copy that prints the later name (the register cannot date it more
finely) and bounded below by the last copy that prints the earlier one.
An event is classed:

- **rename** — both names resolve (by rule or admission) to the **same**
  company number, or the later name appears in the earlier company's
  `previous_company_names` with an `effective_from`, or the earlier name
  appears in the later company's `previous_company_names` with a
  `ceased_on`; the Companies House date of the change is recorded beside
  the register's bounds;
- **transfer** — both names resolve to **different** company numbers;
- **not determinable** — either name unresolved.

For a rename, the run also reports the days between the Companies House
`effective_from` and the first register copy printing the new name: the
register's lag behind the company register, a by-product, published as a
distribution and never as one number.

**R5 — persons with significant control.** From
`persons-with-significant-control` (`items[]`): `name`, `kind`,
`notified_on`, `ceased_on`, `natures_of_control[]`, and for corporate
entities `identification.registration_number` and
`identification.country_registered`; and from the statements endpoint
any `statement` (for instance that no person with significant control
has been identified). Only PSCs with no `ceased_on` are *current*.
This run publishes, per company, the count of current PSCs and whether
any is a corporate entity registered outside the United Kingdom; **it
publishes no PSC name**. Names stay in the pinned bytes for the sponsor.

**R6 — charges.** From `charges` (`items[]`): `charge_code` or
`charge_number`, `status`, `created_on`, `satisfied_on`,
`persons_entitled[].name`, `classification.description`. A company *has
a registered charge* if any item's `status` is `outstanding` or
`part-satisfied`. Per company the run records the count of such charges,
the earliest `created_on` among them, and the chargee names (these are
lenders and security trustees, published in the pinned bytes and the
evidence table, since a charge is a public notice by design; the sponsor
decides what leaves the repository). Rows and MW are counted under
"charged" and "uncharged", with unresolved names a third class.

## What is computed, declared before any request is sent

1. **Resolution**: names, rows and MW by class (`exact`, `previous-name`,
   `admitted`, `refused`, `ambiguous`, `unresolved`, `identity-guard`,
   `no-suffix`), and the same after admissions, dated.
2. **Age**: rows and MW under companies under a year old on 2026-09-29;
   the distribution of company age in years over all resolved rows, by
   `Project Status` as printed.
3. **Name changes**: events found (R4), by class; for renames, the lag
   distribution; the ten largest transfers by MW listed by project id,
   MW, the two names and the two company numbers.
4. **Charges**: rows and MW charged, uncharged and unresolved, by
   `Project Status` and by `Gate` as printed; the count of distinct
   chargee names and the ten most frequent.

No other figure may be added after a run. Every figure carries the digest
of this file, the copy, the schema reports and the manifest of pinned
responses.

## Checks each run must pass, or it stops

- **C1** The copy's bytes hash to the digest above; its row count is the
  schema report's 2,199.
- **C2** Every distinct name is searched exactly once, and every request's
  response is pinned with its digest before the next request is sent.
- **C3** Resolution (R2) is a pure function of the pinned responses and
  the admitted-links file: rerun offline, it reproduces `links.ndjson`
  line for line.
- **C4** `links.ndjson` is append-only; a line that would change on
  recompute stops the run.
- **C5** No response other than 200 or 404 is accepted; more than 2 % of
  requests failing otherwise stops the acquire phase, which is resumed
  from its journal, never restarted.
- **C6** The four figure sets sum: every row of the copy is in exactly
  one class of each.
- **C7** No PSC name appears in any committed evidence file.

## Falsifiers, declared in advance

- **F1** If fewer than 70 % of distinct names (and, separately, fewer than
  70 % of the copy's MW) resolve by rule or admission, **the join is unfit**
  and figures 2 to 4 are not computed; figure 1 is published as the
  outcome.
- **F2** If more than 10 % of rule-resolved names fail the identity guard,
  the exact-name rule is unfit for this register and F1's test is rerun
  on admissions alone.
- **F3** If fewer than 70 % of name-change events have both names
  resolved, figure 3 is published as *not determinable* with the events
  listed and unclassed.
- **F4** If the schema pass shows a field named in R3 to R6 absent from
  more than 1 % of the responses that should carry it, compute waits for
  an amendment.

## What this never claims

- That a company under a year old is a speculative or weak holder; new
  project companies are how projects are financed.
- That a charge is distress, or that its absence is equity. A charge is a
  public notice that some lender took security at some date.
- That a transfer is a sale of the project, or a rename is not one; the
  company register records legal persons, not commercial substance.
- Anything about a named individual. PSC names are read to count and
  classify and are not published.
- That a name unresolved here is not a company; the search is by name,
  and names are reused, misspelt and abbreviated on the register.

## Order of work

1. Sponsor reads this file; changes are made before the freeze. 2.
`scripts/freeze`. 3. Sponsor's seal; `run.py --phase acquire --seal
<prefix>`. 4. Proposed links go to the sponsor; admissions written by
hand. 5. `scripts/schema-report companies-house` committed. 6. `--phase
compute`, RESULTS.md from the evidence, to the sponsor. **Nothing about
ownership is published from this run**; it is the ownership layer for
the sponsor's conversations and for a forced-sellers thesis that would
need its own declaration.

## Outputs

- `data/raw/companies-house/<run-date>-019/` (local, not committed): every
  response, journalled; `evidence/manifest.json` with each digest.
- `evidence/links.ndjson` (append-only), `evidence/links-proposed.json`,
  `evidence/links-admitted.json` (human-written).
- `evidence/companies.ndjson`: one line per resolved company, R3, R5
  counts and R6 facts.
- `evidence/results.json` and `RESULTS.md`; `evidence/rule-sources.json`
  naming the test behind every rule above.
- Scale for the sponsor's budget: about 1,400 searches and up to about
  4,200 further requests, under an hour at the declared rate; the key's
  documented limit is 600 requests per five minutes.
