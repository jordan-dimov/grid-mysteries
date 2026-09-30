# 017 version 3, amendment 1: the next copy's date spelling

*Drafted 2026-09-30 after N0 failed and before any figure of the next copy was
computed (draft at `drafts/AMENDMENT-v3-1-DRAFT.md`, commit `14fbe88`), approved
by the sponsor as drafted on 2026-09-30, and frozen by `scripts/freeze`, which
witnesses these bytes with OpenTimestamps and RFC 3161 tokens from freetsa.org
and DigiCert and commits the file with its proofs. Written from the schema
reports alone, as N0 requires. It amends `DECLARATION-v3.md` (`dd396986…`) for
the next copy only; everything else in version 3 stands as frozen.*

## What N0 found

`evidence/v3/n0.json` (commit `7a1bd6f`) records that the next copy
under R1′, CKAN `last_modified` 2026-09-29T12:18:57, NESO filename
`tec-register-28-september-2026.csv`, SHA-256 `d1ccd9e2…`, captured
2026-09-30, meets four of N0's five conditions and fails one. The capture
schema report it was read from is `archives/tec-register-capture/schema-report.json`,
SHA-256 `857dfc88…`, committed at `f14c960`.

- Pass: the same fifteen columns; only the five `Project Status`
  spellings; only `1`, `2` and blank under `Gate`; no flag.
- Fail: every dated `MW Effective From` cell, 1,834 of them, is spelled
  `iso-dash` (`YYYY-MM-DD…`) and none `uk`. 365 are blank. The four
  earlier captured copies print `uk` (`DD/MM/YYYY`) only.

The archive schema report (`archives/tec-register/schema-report.json`)
shows the register has printed `iso-dash` before, on 2024-09-27,
2024-12-20, 2026-08-22 and 2026-08-25. Version 2's G6 already read the
last two with the inherited reading rules.

## The reading

**A1 — the spelling.** The next copy's dates are read by
`tec_register.parse_date`'s ISO rule, year then month then day, which is
014's inherited reading rule and the one version 2 already applied to the
copies of 22 and 25 August. For this copy, N0's condition on date spellings
is therefore met by `iso-dash` and blank; its other four conditions stand and
are rechecked. No other rule of version 3 changes.

**A2 — a check first, from 014's declared test.** A change of spelling
between two consecutive copies is the case the series' day-month swap test
exists for. Before the next census, 014's swap test
(`connection_slippage.swap_test`, at least 3 disagreements and at least half
of all disagreements explained by exchanging day and month) is run between
the reference copy and the next copy over every row matched by 014's unit
key. Its counts are published with the census. **If it flags the next copy,
no next census is computed under this amendment**, and the comparison is
not run.

**A3 — R3's sensitivity, unchanged in form.** The day-month sensitivity is
computed on parsed dates, so it is the same computation for either spelling.
It is published for the next copy as for the reference, with one added
sentence: in an ISO copy the other reading would be `YYYY-DD-MM`, which is
not a spelling the register has used.

**A4 — D2 compares dates, never spellings.** "The same date in both copies"
in D2(b) and "date on or after the next as-of date" compare parsed dates.
A row whose date is printed `24/09/2026` in one copy and `2026-09-24` in the
other has the same date. A change of spelling alone never moves a row
between classes.

## Falsifier added

- **F11** If A2's swap test flags the next copy, F8 applies as if N0 had
  failed: no next census, no comparison, and the outcome is recorded.

## Prior exposure (recorded, not hidden)

The author has seen the reference census (`evidence/v3/2026-09-25/`, commit
`62e8b67`), the N0 verdict (`evidence/v3/n0.json`, commit `7a1bd6f`) and the
capture schema report's whole-copy counts for the next copy (rows 2,199;
status and Gate counts as printed; date spellings). No census figure, no
swap-test count and no row of the next copy has been computed.

## Order of work

1. This file is frozen. 2. A2's swap test is run and its counts committed
with the next census, which is computed only if the test does not flag.
3. D1 and D2 are computed once the next census is committed, as version 3
declares. The findings go to the sponsor before anything is said outside
the repository.
