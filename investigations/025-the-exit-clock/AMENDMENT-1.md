# 025, the exit clock: Amendment 1 of the reading (a row is admitted only if it is a project row)

*Frozen on its own by `scripts/freeze` (OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert, committed with the file). `DECLARATION.md` (SHA-256 `bc05298419069041ae21b75d0fc556f5ecb48224eb947806325f704f4eb4cd78`, frozen 22/10/2026) stands unchanged with its proofs; the results computed under it alone are kept at `evidence/results-declaration-alone.json` (SHA-256 `f5db2ec0396f669a4f64edc0c79c7455253eba26cf638f1bc8d02f6bcfe87aed`, committed at 945cfda). Both sealed texts stay on record.*

**Dated 2026-10-22, night (UTC).** Raised on the sponsor's instruction of 22/10/2026 (night), after the sponsor read the close-out and before any recompute. Taught by the rendered appendix of the compute of 22/10/2026, in which two of the 494 chains that "left the register" were the footer text of the copy of 2020-12-15 read as rows (a confidentiality line and a copyright line), and written against a schema-pass addendum that reads blankness only: `archives/025-exit-clock-inputs/blank-patterns.json` (SHA-256 `c9db2dd4a2008786f76643f28dd6d893563ca2d7a030350750d7c64051cb2ab6`), beside the schema report the declaration cites (`fa3cbb802f61d3b6…`).

## What the schema pass shows

Over the 800,834 rows of the 791 kept copies, `Project Name` is never blank. Exactly two rows in the whole series print a `Project Name` and nothing else, both in the copy of 2020-12-15. One row prints a `Project Name` and a `Customer Name` only. Every other row prints at least three fields. No row prints other fields without a name. The declaration's rule I1 keys a row by its Project ID or by the (name, customer, site) triple, so a row that prints only a name is keyed on the name alone and becomes a chain of one sighting, which rule E1 then counts as having left the register.

## The amendment

**I10, the admissible row.** A row of a kept copy is admitted to chain-building (I1 and after) only if it prints a `Project Name` and at least one other field of the register: `Customer Name`, `Connection Site`, `Project Status`, `Plant Type`, `HOST TO`, `Agreement Type`, `MW Connected`, `MW Increase / Decrease`, `Cumulative Total Capacity (MW)`, `MW Effective From`, `Stage`, `Project ID`, `Project Number` or `Gate`. A row that prints a name alone, or no name, is a print artefact of the sheet (a footer, a note, a heading) and is refused before keying. Nothing else about the row is read to decide: not what the name says, not which copy it is in. The rule is the narrowest the schema pass supports: it refuses only what no genuine project row in 791 copies looks like, and admits the one row that prints a name and a customer only (its chain is listed in `results.json` under `amendment_1.sparse_rows_admitted`, and whatever it is, it is reported, not excluded by hand).

**Refusals are counted, by copy.** `results.json` carries, under `amendment_1.refused_rows`, each kept copy that held a refused row with the count refused; no refused row's text is printed anywhere.

**What is unchanged.** 014's partial-export rule and the declaration's R3 (the row count through the Gate 2 reset) read the printed row count of a copy, before this rule, as the declaration states them. Every other rule (I1 to I9, E1 to E5, K1 to K6, S1 to S5, R1 to R3, O1 to O3, J1 to J6, C1 to C6) is unchanged in text and in code.

**C5 under the amendment.** The held `evidence/chains.ndjson` is append-only. The amended compute must reproduce, line for line, every chain line it builds that the file already holds, or refuse. A chain the declaration-alone compute built from refused rows only is not built by the amended compute; its line stays in the held file as the record of the first compute and is counted in `results.json` under `amendment_1.chains_held_under_declaration_alone`. `exits.ndjson`, the appendix, FINDINGS, the sponsor's sheet and the figures are rendered from the amended compute.

**Every figure that moves is listed.** The amended compute compares its `results.json`, leaf by leaf, with `results-declaration-alone.json` (all keys except `computed_at` and the amendment block) and writes the list of leaves whose value changed, with the old and the new value, to `results.json` under `amendment_1.moved`; FINDINGS prints it in full, and says first whether any storage figure moved.

**Expectation, stated before the run.** Two chains fewer (2,644 to 2,642) and two exits fewer (494 to 492), both from the copy of 2020-12-15 (exit copy 2020-12-24), both of blank plant family, blank agreement and no connection date; so the all-technology hazard table's "no connection date" band, the 2020 row of the monthly series, the class counts and the exposure totals move, and no storage figure moves. If a storage figure moves, FINDINGS says so first and this expectation is recorded as wrong.

**Rendering, in the same pass.** Four breakdowns that FINDINGS printed as Python dictionaries (the reformed regime by status and by Gate; the O2 window by status; the J1 and J2 match tiers; J3's company status and classes) are rendered as tables. Presentation only; no figure is computed differently.

**Rule version.** `results.json` names the declaration and this amendment by digest (`declaration_sha256`, `amendments`); `run.py --phase compute` refuses to run unless both files hash as expected and both carry their proof sidecars.

## Tests

`I10.1` a row printing a name alone is refused; `I10.2` a row printing a name and one other field is admitted; `I10.3` a row printing no name is refused; `I10.4` the admitted set of a copy is the printed rows minus the refused, and the printed count is what the partial-export rule and R3 see. Mapped in `evidence/rule-sources.json`.
