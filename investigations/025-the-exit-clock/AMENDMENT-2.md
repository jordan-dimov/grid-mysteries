# 025, the exit clock: Amendment 2 of the reading (the 76 copies admitted, and rows that print no name read as continuations)

*Frozen on its own by `scripts/freeze` (OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert, committed with the file). `DECLARATION.md` (SHA-256 `bc05298419069041ae21b75d0fc556f5ecb48224eb947806325f704f4eb4cd78`) and `AMENDMENT-1.md` (`4a76ec63daa74f697ba353ae636392ff4eb3e9e1af836aa9522a00ff3dbecce5`) stand unchanged with their proofs. The results computed under them are kept at `evidence/results-amendment-1.json` (SHA-256 `6fc3d59ecc012763a152ed27f81bdd092f6bf1f9edbff7c23e98994761307664`, the `results.json` committed at 305dbe8). All three sealed texts stay on record.*

**Dated 2026-10-28.** Raised on the sponsor's instruction of 28/10/2026, before any recompute. The sponsor asked for the 76 copies to be taken in and for the unnamed rows to be read by whichever rule rebuilds NESO's complete exports of the same dates. Taught by the schema pass of 28/10/2026 over the archive after FOI/26/245 and FOI-26-226 (`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-245.md`; `archives/tec-register/schema-report.json`, SHA-256 `5f9a7c2858682c46a85f8ba7dfbdca5824605dac8c946d44897b6c9dd2896a02`). Written against two artefacts committed at 92c7c40 before this text:

- the rule test, `archives/tec-register/continuation-rule-test.json` (SHA-256 `8b61625eed212a457086c0ed0804d0c7b309350a20d8ee76a88ba49ee6e73084`, `scripts/continuation-rule-test`);
- the schema pass under the rule, `archives/025-exit-clock-inputs/amendment-2/schema-report.json` (SHA-256 `15711a92f8c5a67a60ab77de7adb9daf59938be273f0dab8610d93ade8f3af04`, `run.py --phase schema-a2`).

## What the schema pass shows

**Amendment 1's schema statement was true only of the rows the reader returned.** "No row prints other fields without a name" holds of what `read_vintage` keeps. It does not hold of the copies. From 2020-06-18 to 2024-05-30 the published register prints a project's name on its first stage row only, and the reader drops every row without a name: 40,107 rows in 346 copies, all inside this series, each printing at least six cells and each below a named row. In the Project ID era (from 2021-11-26, which is also the first copy that prints the Project ID column) most of these rows carry the Project ID of the named row above them. Some carry their own ID. Amendment 1's I10 and its two refused footer rows are unaffected.

**The rule test.** FOI-26-226 holds NESO's exports of 38 month-ends from 2021-01-29 to 2024-04-26 that print the name on every row. The journal also holds the published copy of each of those dates. Three readings of the published copy were scored against the export at this investigation's unit: per chain key (`exit_clock.row_key`, admitted rows only), the rows' read columns, names compared by 005's normaliser. 2023-11-28, the flagged partial export, is left out.

| reading | ID era (27 dates): keys exact | before the ID era (10 dates): keys exact |
|---|---|---|
| rows without a name dropped (the declared reader) | 25,492 of 28,245 | 5,153 of 6,234 |
| name, customer and site always taken from the named row above | 28,237, plus 8 differing only by NESO's artefact rows; 61 rows given a customer NESO does not print | 5,829 |
| **the continuation rule (I11 below)** | **28,237, plus the same 8; no customer NESO does not print** (63 left blank) | **5,829** |

Before the ID era the residual is 372 keys from the published copy of 2021-07-30, which prints another plant type than NESO's export on 349 of its 628 rows. That is a publication error, not a reader's: this amendment reads that copy as printed. It also includes 29 keys where a stage row sits under another project's named row.

**The schema pass under the rule**, to the series end of 2026-10-20: 869 usable copies and 867 kept, which is 76 more than the declaration's 793 and 791. Every one of the 76 is a new publication date journalled on 2026-10-28 (44 in 2025, 31 in 2026, and 2023-06-30). The two suspect copies are unchanged (2015-05-08, 2023-11-28), as are the 14 high-churn pairs. There are five re-keyings: the declaration's three, with 690 and 838 matched where there were 682 and 827, and **two in the reformed regime**. From 2026-05-19 to 2026-05-22, and back from 2026-06-19 to 2026-06-23, the FOI-26-226 copies print a per-row identifier (prefix `a1f`, one per row) in the Project ID column in place of the per-project one (`a0l`). Project Number is stable throughout. At the first, 139 chains are unmatched. At the second, 276 are unmatched and 127 appear. Whether NESO published those identifiers or its export took another field is not known: no published copy of that window is held.

## The amendment

**I11, the continuation rule.** In a kept copy, a row that prints no Project Name but prints at least one other cell, below a row that prints one, is a continuation of that named row. It is read with that row's Project Name. It also takes the named row's Customer Name and Connection Site where it prints none of its own, but only when it continues the same project. In a copy that prints a Project ID column, that means its Project ID equals the named row's. In a copy without the column it always takes them, because nothing on the row says otherwise. Nothing else is taken from the named row. A row with no named row above it is not read. The rule is `tec_register.continue_row`, read through `read_vintage(..., continuation=True)`. I10 then applies unchanged: a continuation row prints a name and at least one other field, so it is admitted.

**I12, the copies.** The series is every copy `tec.sources.copies()` yields to the series end, which is unchanged at 2026-10-20: 869 usable. That includes the 76 new publication dates. It excludes the files the journal marks as further copies of a held date, duplicates of a held publication, or renderings of an unreadable file. The 31 renderings of 2014 are not read. Reading them is a separate question for the 2014 figures, not answered here.

**What else reads I11's rows.** 014's partial-export rule and the declaration's R3 read the copy's row count under I11 (the printed rows, continuation rows included), before I10, as Amendment 1 states for I10. Under that count the suspect copies are the same two.

**The schema report and the format check.** C2 and the format check compare against this amendment's schema report (`15711a92…`). The declaration's report (`fa3cbb80…`) stays where it is, as the record of what the declaration was written against.

**C5 under this amendment.** The held `evidence/chains.ndjson` is the record of the computes under the declaration and Amendment 1, and is not touched again. The amended compute writes its chain lines to `evidence/amendment-2/chains.ndjson`, which is append-only from its first write: every later compute must reproduce, line for line, every line it already holds, or refuse. `exits.ndjson`, the appendix, FINDINGS, the figures and the sponsor's sheet are rendered from the amended compute.

**Every figure that moves is listed.** The amended compute compares its `results.json`, leaf by leaf, with `results-amendment-1.json` (all keys except `computed_at` and the amendment blocks). It writes the leaves whose value changed, each with its old and new value, under `amendment_2.moved`. FINDINGS prints them, says first whether figure 1's storage exit count moved and whether any of figure 8's five trigger bands moved, and lists the re-keying outcomes of the two reformed-regime re-keyings.

**The joins.** J1 (REPD) and J2 (Capacity Market Register) are re-run on the amended exits from the files pinned on 22/10/2026, unchanged. J3 (Companies House) reads the records pinned on 22/10/2026. A linked company not among them is fetched on the run date into the same journal, which records each file's fetch time, and FINDINGS says how many were fetched after 22/10/2026.

**Expectation, stated before the run.**
1. Chains rise: rows under their own Project ID, and stages and projects that appear and leave between copies the declaration did not hold, become chains.
2. Old-regime exits do not fall, and storage exits (figure 1, 96) do not fall. Either falling is reported first and recorded as contrary to this expectation.
3. In the reformed regime the not-determinable count rises by the chains unmatched at the two new re-keyings. No reformed-regime exit comes from them, because an unmatched chain at a re-keying is not determinable (I5 and the declared stitch), so figure 9's exits are expected unchanged by them.
4. No rate is predicted. Figures 2 to 8 move or not as computed, and every leaf that moves is listed.

**Rule version.** `results.json` names the declaration and both amendments by digest. `run.py --phase compute` refuses to run unless all three files hash as expected and carry their proof sidecars.

## Tests

- `I11.1`: a row printing no name, below a named row with the same Project ID, takes its name, customer and site.
- `I11.2`: such a row with its own Project ID takes the name only.
- `I11.3`: in a copy without a Project ID column such a row takes all three.
- `I11.4`: a row printing no name and no named row above it, or printing nothing, is not read.
- `I12.1`: further copies, duplicates and renderings are never chosen as a date's copy.

Mapped in `evidence/rule-sources.json`.
