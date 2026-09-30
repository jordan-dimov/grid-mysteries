# 019 — Who holds the queue: amendment 2 (a name borne by two companies in succession)

**Written 2026-09-30, after the recompute that closed column B under
`DECLARATION.md` (SHA-256 `877682f7…`) and amendment 1 (`9ba963ee…`); the
sponsor directed it the same evening.** Frozen by `scripts/freeze` before
any figure under it. It amends rule R4's classing of a name-change event
and nothing else. Every line in `evidence/links.ndjson` and every
admission stands.

## Prior exposure, stated

The author has seen figure 3 as recomputed with the copy-date admissions:
870 renames, 767 transfers, 95 not determinable, rename lag median 116
days over 259 events. The author has also seen the two events this
amendment is about: on project `a0l4L0000005iw2`, *Chickerell Solar
Limited* (last printed 2022-08-24, borne then by company 11505358) to
*CHICKERELL SOLAR LIMITED* (first printed 2023-08-29, borne then by
14891278), and *CHICKERELL SOLAR LIMITED* (last printed 2023-08-29,
14891278) to *CHICKERELL STORAGE LIMITED* (first printed 2026-05-19,
11505358). R4 as declared classed both as **rename**, with lags of −800
and +1,091 days, because the later company's `previous_company_names`
carry the earlier name. This amendment is written knowing that; its
purpose is to make R4 say what the copy-date rule shows, not to move the
median.

## Why R4 misreads it

R4's rename test has three branches and applies them before its transfer
test: same company; the later name among the earlier company's previous
names; the earlier name among the later company's previous names. The
third branch was written for the case in which the **earlier** name does
not resolve at all (the company that bore it has since been renamed, so
the register's old name is only a previous name of the company now
printed). When **both** names resolve, the branch fires wrongly: two
companies bore the same name in turn, the register's rows passed from
one to the other, and the event is a transfer of the name, not a rename
of a company. The Companies House date the branch finds belongs to the
later company's own renaming, which is why the lag it yields is negative
or years long.

## A1 — the classing, restated

An event is classed, in this order:

- **rename** — both names resolve (by rule or admission, at the event's
  copy dates under the copy-date rule) to the **same** company number;
- **transfer** — both names resolve to **different** company numbers,
  whatever either company's previous names say;
- **rename** — exactly one name resolves, and the other name appears in
  that company's `previous_company_names` (the earlier name with a
  `ceased_on`, or the later name with an `effective_from`);
- **not determinable** — otherwise.

The Companies House date of a rename, and the lag, are reported as
before, for renames only. For a transfer whose later company once bore
the earlier name, that date is still recorded beside the event (it says
when the later company stopped using the name), but it enters no lag.

## A2 — versions

Figure 3 is recomputed under this amendment and reported with the
amendment's digest; `evidence/results.json` records
`amendment_2_sha256`. No link line, admission or pinned resource changes.
Figures 1, 2 and 4 are unaffected.

## What does not change

R1 to R3, R5, R6, the copy, the schema pass, C1 to C7, F1 to F4, the
admissions file and its two stated rules, and the sponsor's instruction
that the ownership tables and RESULTS.md stay out of the public
repository.
