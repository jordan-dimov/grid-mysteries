# FOI/26/216: the 301-day hole closed (acquired 2026-10-15)

NESO's response to 005's EIR request of 2026-09-15 (`EIR-REQUEST-TEC-2025-26.md`),
reference FOI/26/216, arrived by email on 2026-10-13 (the watch
`w-005-eir-response` was read as resolved on 2026-10-15,
`watch-readings/w-005-eir-response-2026-10-15.md`). The disclosure was
journalled on 2026-10-15 by `scripts/journal-foi-26-216` on the sponsor's
instruction of that day, following the etrmbiz handover
`notes/2026-10-13-foi-26-216-handover.md`.

## What was pinned

- The originals, kept beside the archive: `data/raw/neso/foi-26-216/FOI-26-216 - Response.pdf`
  (SHA-256 `c11095dc904d367bcb7434f4722689fca05502feaa69e11a53fa9406d475d495`)
  and `FOI-26-216 - TEC&TWR.zip` (`69a2943014b58a5dadde38ef918fea7eae7ee234234bc1078fcfa5fb4e9d9323`,
  133 members: 83 TEC Register CSVs under `Q1 TEC/`, 24 TWR reports under
  `Q2 TWR/`). The zip's entry timestamps are NESO's extraction of
  12 and 13 October 2026, not publication dates.
- **83 TEC Register copies**, `data/raw/neso/tec-history/<date>_neso-foi-email.csv`,
  journalled under the source label **`neso-foi-email`** (an emailed EIR
  disclosure with no NESO document URL; `url` is null and the provenance
  is the FOI reference, the email date, the zip's digest and the member
  path). Publication dates from the filenames, 2025-07-25 to 2026-05-15,
  twice weekly; the only skipped publication days are 2025-12-26 and
  2026-04-03 (bank holidays); one filename breaks the pattern
  (`TEC Register 23 Dec 2025.csv`). Every file begins with a UTF-8
  byte-order mark (the reader reads `utf-8-sig`). Rows 2,229 to 2,280.
  Stored bytes are the zip's originals.
- **24 Transmission Works Register reports**, `data/raw/neso/twr/vintages/<date>_TWR.xlsx`,
  2025-10-17 to 2026-10-02, journalled in `data/raw/neso/twr/journal.ndjson`
  under `neso-foi-email FOI/26/216`. Probable missing issues around
  2025-10-31 and 2026-07-24; NESO says these are all it holds dated after
  2025-10-03.

## The archive after it

The journal holds 835 rows, 815 distinct publication dates from 2014-01-31
to 2026-09-15; the schema pass (`archives/tec-register/`, regenerated) reads
783 usable copies. **No copy is missing between 2025-07-22 and 2026-05-19
for more than 7 days.** The gaps over 14 days that remain since 2021:
2025-01-28 to 2025-03-21 (52 days), 2025-04-01 to 2025-07-01 (91 days),
2025-07-01 to 2025-07-22 (21 days), 2026-05-19 to 2026-08-22 (95 days),
2026-08-25 to 2026-09-15 (21 days). "Twice weekly since 2021 with no gap"
is therefore **not** true of the archive; "no gap longer than 95 days
since 2021, and none longer than 7 days across the reform period" is.

## NESO's written position on the TWR

The letter says there is no version of the Transmission Works Register
other than the published one, and that CUSC 6.36.2's "Completion Date(s)"
is the `MW Effective from` column. The TWR therefore carries no per-scheme
completion date distinct from the dependent project's connection date, and
the register cannot split delay caused by grid works from delay caused by
projects; 006's attribution stays a separate method.

## What the copies do to the investigations that read the archive

Decided by each investigation's own rules after the journalling, recorded
in each (`014/AMENDMENTS.md`, 020, 021), never here.
