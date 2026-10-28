# 021 — amendments and dated findings

`DECLARATION.md` is frozen (SHA-256 `76ad7dc3…`). A failed check is
recorded here before any rerun; there is no `--amend`, and a changed figure
is a new declaration beside this one.

## Refusal, recorded — 2026-10-15: C1 fails after the archive grew (FOI/26/216)

On 2026-10-15 the archive gained the 83 TEC Register copies of 2025-07-25
to 2026-05-15 (NESO EIR response FOI/26/216,
`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-216.md`)
and `archives/tec-register/schema-report.json` was regenerated over 783
usable copies. `run.py --seal 76ad7dc3 --phase check` then refused:

    refusing (C1): the schema report hashes to 8404e69a2abbec6a…, not 9ed878f499db8a8c…

C1 binds this cut to the schema report it was declared against
(`9ed878f4…`, committed at `a399a35`, recoverable from git) and to 014
version 4's evidence digests, and 014 version 4 is not recomputed over the
filled hole (its own refusal is recorded in
`investigations/014-gb-connection-slippage/AMENDMENTS.md`, 2026-10-15).
**Nothing was written; the committed rows, `summary.json` and
`FINDINGS.md` stand as computed on 2026-10-01**: every window this cut
reads (2014 to 2024 and the headline 2024-07-19 to 2025-07-22) closes
before the first new copy, so no figure here depends on the hole. A cut of
a recomputed 014 series would be a new declaration beside this one.

## Refusal, recorded — 2026-10-28: C1 fails again after the archive grew (FOI/26/245, FOI-26-226)

The archive gained 76 publication dates
(`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-245.md`)
and `archives/tec-register/schema-report.json` was regenerated. It now also
lists the 2014 renderings, every journalled file reading rule 1 does not
choose, and the rows the reader drops. `run.py --seal 76ad7dc3 --phase check`
refused:

    refusing (C1): the schema report hashes to 5f9a7c2858682c46…, not 9ed878f499db8a8c…

Nothing was written. The windows this cut reads close before the first new
copy, as on 2026-10-15, but one finding reaches them. From 2020-06-18 to
2024-05-30 the declared reader drops rows that print no Project Name, which
are mostly later stages of multi-stage projects (40,107 rows in 346 copies).
The cut's 2020 to 2024 windows therefore count first-stage rows only, and
its by-technology shares may lean towards technologies that are rarely
staged. That lean is not measured here. A recomputed 014 with a reader rule
for those rows would be a new declaration beside this one.
