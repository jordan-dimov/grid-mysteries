# FOI/26/245 and FOI-26-226: the 2025 and 2026 holes closed (acquired 2026-10-28)

NESO's response to the EIR request of 2026-09-30, reference FOI/26/245, arrived
by email on 2026-10-28 (letter of that date, from informationrights@neso.energy,
15:40 UTC). It points to FOI-26-226, another requester's response on NESO's
disclosure log, for copies already disclosed there. Both were journalled on
2026-10-28 following the etrmbiz handover
`notes/2026-10-28-foi-26-245-handover.md`, by `scripts/journal-foi-26-245` and
`scripts/journal-foi-26-226`. This record follows `ACQUISITION-FOI-26-216.md`.

## What was pinned

- **FOI/26/245**, kept under `data/raw/neso/foi-26-245/`: the letter
  `FOI-26-245 - Response.pdf` (SHA-256 `ded6872e321a18842b86be37a7ebdae33437669785f315afa56b2af9966cff9d`)
  and `FOI-26-245 - information.zip` (`37eebbd44468a1c954edfb8d41cc7188e6047c374d442f84cc7d4a0b6d034f44`).
  The zip's entry timestamps record NESO's extraction on 2026-10-28, not publication.
  - Item 1: **69 TEC Register CSVs** (`Q1 TEC Register/`), dated by filename
    from 2025-01-03 to 2025-07-18 and from 2026-08-14 to 2026-09-28, twice
    weekly. The only publication days skipped are 2025-02-21 and 2025-04-18
    (Good Friday). Every file begins with a UTF-8 byte-order mark, has no title row, and
    has 14 columns (15 from August 2026, with `Gate`). Rows run from 1,973 to 2,242.
    These are stored as `<date>_neso-foi-email.csv` under the source label
    `neso-foi-email`, with `url` null.
  - Item 2: **31 CSV re-exports of 2014 copies** (`Q2 TEC Register/`) that the
    journal holds as `.xls` files the declared reader rejects (xlrd
    AssertionError). These are stored as `<date>_neso-foi-email-rendering.csv`. Each line carries
    `renders` (the `.xls` line's path, digest, archive member and row count),
    takes the `.xls` line's `t_public`, and is never a publication of its
    own. Every rendering's row count equals its `.xls` line's. The `.xls` files
    are members of FOI-24-0040 (a) (NESO document 357306); the request of
    2026-09-30 cited FOI-24-0031 in error, and the journal keeps the true
    provenance.
- **FOI-26-226** (another requester's; letter of 2026-10-19, received
  2026-09-21), found on NESO's disclosure log by its search widget
  (the page renders by JavaScript) and fetched on 2026-10-28 from
  `https://www.neso.energy/document/389106/download` (Last-Modified
  2026-10-21 15:57:07 GMT; `foi-26-226.zip`, SHA-256
  `71d7ab6a9cc2efe4066b16e853c4baa3c11e39057bd0ecbe2dcd7ba8338a2a0c`).
  It is kept under `data/raw/neso/foi-26-226/` with its inner zip
  `FOI-26-226 - Copies of TEC.zip` (`8ad807460a21cb78c21706327a45297164d13e5cfde1ccd98ed1d6214bea4eb5`),
  the letter (`f01f0f83c64e43a4f6c6f72538031f66f057fdfb0f2673fe098d7ed41cae43fc`)
  and the download headers. It holds **129 TEC Register CSVs**: the last copy of each month
  from 2021-01 to 2026-07, the copy of 2025-11-21, and every Tuesday and
  Friday copy from 2025-12-09 to 2026-08-11. All carry a byte-order mark. They are stored as
  `<date>_neso-foi-26-226.csv` under the source label `neso-doc` (a NESO
  document URL).

Stored bytes are the originals in every case.

## How each copy was journalled

There are three cases, decided by the script and recorded on each line.

| case | FOI/26/245 | FOI-26-226 | journal field |
|---|---|---|---|
| a new publication date | 51 | 25 | none |
| a date the journal already holds | 13 | 104 | `further_copy`, `same_date_as` (rows compared with each held copy) |
| the same publication already held under another date, or as a daily capture copy | 5 | 0 | `duplicate_of`, `t_public_witnesses` |
| a rendering of a held `.xls` | 31 | n/a | `renders` |

**The choice rule.** Journalling a copy never changes which copy of a held
date a reader reads. `one_per_date` (reading rule 1) passes over
`duplicate_of`, `renders` and `further_copy` lines, so on every date the
journal held before 2026-10-28 the same file is read as before; this was
checked on all 783 copies of the previous schema report, and on 025's
series (no copy changed or disappeared). Admitting a further copy in place
of a held one is a reader's amendment, never a side effect of journalling.
The rule was set this way because of what the further copies showed:

- **FOI/26/245 on held dates.** Rows equal after normalising numbers, dates
  and whitespace on 2025-01-07, 01-10, 01-21, 01-28, 03-21 (wayback),
  04-01, 2026-08-25 and 09-15. They differ in text only on 2025-01-03 (6
  rows), 01-17 (7), 01-24 (6) and 07-01 (19). There the FOI copy prints
  company names without a comma (`BUCCLEUCH ESTATES LTD (THE)` against
  `BUCCLEUCH ESTATES, LTD. (THE)`) and once ` - ` for a comma in a project
  name. NESO's published series itself alternates between the two spellings
  (0 or 6 such rows from copy to copy through late 2024), so neither copy is
  "cleaner". They are two exports of one date. On 2025-07-01 the mangled
  apostrophe in the held copy (`Blanket�s Farm`) is this repository's reader
  decoding a cp1252 file as UTF-8, not NESO's text. **2025-01-14** is a real
  disagreement: the published xlsx has 1,977 rows and NESO's archive copy
  1,974. New Marton GEC, Strath Oykel Wind Farm and West Botley High Impact
  Green Energy Hub are in the first and not the second, and nothing is
  missing the other way. Both are journalled and the published file stays the
  one read.
- **FOI-26-226 on held dates.** From 2021-08-31 to 2024-04-26 every
  month-end copy has 94 to 183 rows the held copy of that date does not
  (886 on 2023-11-28, the copy the schema report flags as a partial
  export). These rows are not new information. The held xlsx files print a
  project's name on its first stage row only, and the declared reader drops
  every row without a name (see the next section). The extra rows are those
  later stages. On these dates reading rule 1 would have preferred the
  larger file. That would have given readers stage rows on month-ends only,
  appearing and vanishing between neighbouring copies, which is why further
  copies are never chosen.
- **Five FOI/26/245 copies duplicate a held publication.** NESO's archive
  names three September 2026 files a day before the portal changed. Monday
  21/09 went live Tuesday 22/09 at 07:57 (CKAN `last_modified`), Thursday
  24/09 on Friday 25/09 at 09:06, and Monday 28/09 on Tuesday 29/09 at 12:18.
  18/09 matches the capture copy of the same day, and 21/08 matches the
  journal's 2026-08-22 line, whose own basis says its date is approximate
  (taken from a local filename). The rows are equal in each case, so these are
  journalled as `duplicate_of` the held copy with both dates as witnesses.
  Without that, `tec.sources.copies()` would stop on 18/09 (two files
  claiming one date) and count the other four publications twice. **The
  date in NESO's filename can precede public availability by a day**: three
  of six witnessed 2026 cases do, three match. The FOI copies dated only by
  filename (2025 and the new 2026 dates) carry that uncertainty.

## A reader defect found: rows without a project name (2020-06-18 to 2024-05-30)

The regenerated schema report (`archives/tec-register/`, SHA-256
`5f9a7c28…`, section "Rows the reader drops") counts, for every parsed
copy, the rows below the header that print no Project Name but print other
cells. `read_vintage` (`rows_from_matrix`) keeps only rows with a name. **346 copies, from the
first Stage-era copy of 2020-06-18 to 2024-05-30, drop 40,107 such rows (27
to 183 a copy); from 2024-05-31 NESO prints the name on every row and no
copy drops any.** In the Project ID era most dropped rows are later stages
of the named project above them (same Project ID, customer blank: 86 of 99
on 2022-06-30, 148 of 183 on 2024-04-26). The rest carry a different Project
ID and usually a customer, so whole projects, or stages under their own ID,
are unseen. Before the ID era (to 2021-11) nothing on the row says
which. Every investigation that reads the register through `read_vintage`
has read first-stage rows only across those four years: 014, 020, 021, 023,
025 and the TEC record engine. No reader is changed here. A rule for these
rows is a reader amendment per investigation, and as the counts show,
"carry the name down" is not one obvious rule. The FOI-26-226 month-end
CSVs repeat the name on every row and are a check on any such rule for
their 37 dates.

## The 2014 renderings

The schema report reads the 31 renderings for their schema only (section
"Renderings of unparseable copies"). They have the 2014 column vocabulary,
row counts equal to the `.xls` lines', and one unparseable date cell in
each of 2014-04-17 and 2014-04-23. No investigation reads them unless a declaration
says so. `tec_register.rendering_for` finds a file's rendering by path and
digest.

## The archive after it

The journal holds 1,064 lines over 896 dates. The schema pass parses 859
copies; 32 stay unparseable to the declared reader, 31 of them now
rendered. Over every publication the repository holds (journal and daily
capture, one per date, `tec.sources.copies()`), 903 from 2014-01-31 to
2026-10-27, **no gap since 2021 is longer than 14 days**. Those over 7
days are 2021-12-22 to 2021-12-31 (9), 2022-12-23 to 2023-01-06 (14),
2024-04-26 to 2024-05-07 (11) and 2024-12-24 to 2025-01-03 (10). "Twice
weekly since 2021, no gap longer than two weeks" is now true of the archive's
publication dates. It says nothing about each copy's completeness: see the
reader defect above, and the partial exports of 2015-05-08 and 2023-11-28.

## What the copies do to the investigations that read the archive

Each investigation's own rules decide, recorded in its own file and never here.
On 2026-10-28: 014 version 4's check refuses (the version-2 side of 10 rows
on 2023-07-04, 2024-07-02, 2025-03-21, 2025-04-01 and 2025-07-01 differs);
021's C1 refuses (schema report digest); 025's format check would refuse
(76 copies inside its series are not in its schema report: 44 in 2025, 31
in 2026, 2023-06-30). 020 was not re-run; its amendment 5 pins the journal before these
copies (`81d37bc3…`, 835 rows), so a recompute over them is an amendment 6.
Nothing was recomputed and no figure moved.
