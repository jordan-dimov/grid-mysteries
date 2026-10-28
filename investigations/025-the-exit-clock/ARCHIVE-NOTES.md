# 025 the exit clock: archive notes (dated findings; nothing here is frozen)

The declaration (`bc052984…`) and Amendment 1 (`4a76ec63…`) are the sealed
texts. This file records what later happens to the archive they read, before
any amendment answers it.

## 2026-10-28: 76 copies added inside the series, and a reader defect

**Copies.** The archive gained 51 TEC Register publication dates from NESO's
EIR response FOI/26/245 and 25 from NESO's published response FOI-26-226
(`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-245.md`).
Inside this series (to 2026-10-20) that makes 76 copies (44 in 2025, 31 in
2026, 2023-06-30). 2025, the series' thinnest year in the old regime, goes
from 57 copies held to 101. The format check, replicated read-only on
2026-10-28 (`evidence/format-check.json` not rewritten), refuses all 76 as
"copy not in the schema report". No copy the compute read has changed or
gone: further copies of held dates are journalled `further_copy` and never
chosen. **No figure moved, because nothing was recomputed.** Figures 1 and 8 of
`SPONSOR-SHEET.md` stand as restated under Amendment 1.

**The reader defect.** From 2020-06-18 to 2024-05-30 the published register
prints a project's name on its first stage row only, and `read_vintage`
keeps only rows that print a name: 40,107 rows in 346 copies were never
read (`archives/tec-register/SCHEMA.md`, "Rows the reader drops"). In the
Project ID era most of them carry the ID of the named row above (86 of 99
on 2022-06-30, 148 of 183 on 2024-04-26). The rest carry their own ID and
usually a customer, which is a project this series never chained. Before
2021-11 nothing on the row says which. What this means for 025's figures,
not computed:

- a stage or project on unnamed rows is invisible until 2024-05-31 and
  then appears, which is an entry and not an exit, so exposure before
  2024-05-31 is understated;
- one that left the register before 2024-05-31 was never seen, so its exit
  is not counted; the old regime's exits for multi-stage projects, storage
  among them (`Energy Storage System` and `Energy Storage System; PV Array`
  are the commonest plant types on the dropped rows), are a lower bound;
- Amendment 1's schema-pass addendum ("Project Name is never blank",
  `blank-patterns.json`) counted rows the reader returned, so it could not
  see these rows; its two name-only rows are a different thing and stand.

**What an Amendment 2 would have to state**, for the sponsor: (a) admit the
76 copies, with a fresh schema report and format check; (b) a reading rule
for unnamed rows, which the counts show is not simply "carry the name
down", with the FOI-26-226 month-end CSVs (which print the name on every
row, 37 dates from 2021-08-31 to 2024-04-26) as its check; (c) as in
Amendment 1, every leaf that moves listed with its old and new value. Under
the doctrine, the expectation is stated before the run. Until then
`SPONSOR-SHEET.md` figures 1 and 8 (adopted in BEDROCK as
`tec-exit-clock-*-2026-10`) are unmoved but carry this open question.
