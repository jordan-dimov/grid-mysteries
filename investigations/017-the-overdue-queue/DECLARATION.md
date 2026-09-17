# 017 — The queue that is past its own date: declaration

**Written 2026-09-17, before any figure in it was computed inside this
repository.** Frozen by `scripts/freeze`, which witnesses these bytes with
OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert and
commits the file with its proofs. Results come only after that commit,
from `run.py`, which refuses to change a committed row.

## The mystery

NESO's TEC Register publishes, for every transmission connection, a date
the capacity is expected to take effect and a status. In the copy
published on 15 September 2026, how many entries carry an effective date
that has **already passed** while their status is something other than
**Built** — and how much capacity is on those entries?

The claim this investigation may publish is deliberately narrow, and is
about the document rather than the world: **not** that any capacity is
late, which the register cannot support, but that this many entries *say
the date has passed and do not say Built*. What such an entry means is the
second question, and the answer given here is that the register does not
say.

## Why this needs a declaration at all

The Eggborough exhibit published beside this census is a pure application
of 014's declared and witnessed method (`certify.py`, the As-of Connection
Record Certificate) and takes no rule from this file. The census does not:
it is a new selection over the register, with a new unit, a new measure
and a new exclusion, and it produces a number intended for an outbound
document. Under the project's doctrine a selection rule is pre-declared
and committed before its figures are computed, and the schema pass comes
before the declaration. So this file is written after the schema pass and
before the run, and is frozen in between.

## Prior exposure (recorded, not hidden)

The author has seen ungoverned figures for this question, produced on
2026-09-17 by an ad-hoc script outside this repository, over the same
copy: 98 rows carrying 12,034.9 MW; a composition of 5,175 MW Energy
Storage, 4,800 MW Wind Offshore, 897 MW OCGT, 380 MW CCGT and 556 MW Wind
Onshore; by due year 2020 380 MW, 2022 75 MW, 2023 337 MW, 2024 1,280 MW,
2025 4,792 MW, 2026 5,171 MW; an oldest entry of Powersite @ Drakelow,
380 MW, due 1 October 2020, reading "Under Construction/Commissioning";
about 586 GW of future-dated capacity of which about 504 GW "Scoping"; two
project ids appearing twice among the 98; and eight of the 98 carrying
0 MW. **None of those are results.** They are the reason to run the
census. The rules below are written so that the run can contradict them,
and if it does, the run is what is published and the difference is
reported.

## The schema pass this is written against

`archives/tec-register/schema-report.json`, SHA-256
`ce3c61d735ff6349b553e6956d43ee042bd45a85995696dc15fff8620d33f570`,
committed at `419fde5`. It is cited for four facts used below: the copy of
2026-09-15 carries 2,200 rows and the fifteen columns of the current era;
362 of its `MW Effective From` cells are blank and the remaining 1,838 are
all in the UK `DD/MM/YYYY` spelling, with no date cells, no ISO spellings,
no `DD-Mon-YY`, no serials and nothing unparseable; the copy carries no
flag (no partial export, no undated majority); and the register has
printed nine spellings of `Project Status` over the archive, of which this
copy carries five — Scoping 1,484, Built 377, Consents Approved 172,
Awaiting Consents 148, Under Construction/Commissioning 19 — and no
blanks.

## Inputs

One copy of the register and nothing else: the journalled vintage
`data/raw/neso/tec-history/2026-09-15_neso-ckan.csv`, SHA-256
`d13406e495746f1b80e725321a5c7f95e21e0da16830bb6bd1f94ece172c9d5b`,
fetched live from the NESO data portal on 2026-09-15 and journalled with
its resource URL and `last_modified` basis. It is read with
`tec_register.read_vintage` and the reading rules of 014's declarations
(column aliases, date spellings), which are inherited here and not
restated. No other copy takes part in any census figure. Nothing is
fetched for this investigation.

## Reading rules

**R1 — the copy.** The census reads the latest journalled copy published
on or before the census date. Its publication date is the **as-of date**
of every statement made here. If the latest copy is not 2026-09-15 the run
refuses, because this declaration names that copy by digest.

**R2 — past its date.** A row's date has passed if its parsed
`MW Effective From` is **strictly earlier than the copy's own publication
date**, 2026-09-15. Not earlier than the day the run happens: what is
claimed is what the register said on the day it said it.

**R3 — dates.** Parsed by `tec_register.parse_date`, which reads every
spelling the register has used. A row whose cell is blank or does not
parse is **undated**; it is never guessed, is outside the census, and its
count is published. The series' day-month swap correction is **not**
applied: it is a test between two consecutive copies, and one copy carries
no evidence of its own spelling. Instead, because every dated cell in this
copy is `DD/MM/YYYY`, the census publishes, as a declared sensitivity, how
many selected rows and how much selected MW have a day of 12 or less — the
rows that would read differently if the copy's spelling were `MM/DD/YYYY`
— and how many of those would then fall in the future.

**R4 — not Built.** A row is *not Built* when its `Project Status`, with
runs of whitespace collapsed and letter case ignored, is not `built`. The
census additionally publishes the count and MW of the selected rows by
status exactly as printed, so a reader who wants a different exclusion can
take it from the same table without rerunning anything.

**R5 — the measure.** Capacity is `MW Increase / Decrease` as published,
read as `Decimal` — the stage's own TEC, which is 014's declared measure.
The cumulative column is never added to it and never substituted for it. A
row whose MW cell is blank or unparseable has **no** capacity, not zero:
it is counted as a row, is excluded from every MW total, and its count is
published. A row whose MW cell is a parseable `0` is a row with zero
capacity: it is counted in the row count, adds nothing to the MW totals,
and the number of such rows is published. Negative values are summed as
published and reported separately if any occur.

**R6 — the unit, and the second reading.** The unit is **the register row
as published**; each row counts once. Because the register may print two
rows carrying one project id, the census publishes beside the row totals a
second reading: the number of **distinct project ids** among the selected
rows, compared on the 15-character Salesforce form (014's declared
unification), and the MW total when rows sharing an id are counted once by
keeping the **largest** `MW Increase / Decrease` among them. Every id that
appears more than once is listed with its rows as published. Both readings
are published; the row reading is the headline and the id reading is
stated in the same sentence wherever the headline appears.

**R7 — the breakdowns, declared before they are computed.** Exactly four,
and no others may be added after the run: by status as printed; by plant
type as printed (the register prints compound types, which are kept whole
and not split); by calendar year of the effective date; and the ten
earliest selected rows by effective date. For scale, and outside the
selection, the census also publishes the total MW of rows dated on or
after the as-of date, and of those the MW whose status is `Scoping`.

## What the census never claims

- That any capacity is late, delayed, or has failed to be delivered. The
  register's status is NESO's own best-known classification and NESO says
  so; a row may have connected without its status being refreshed, and
  that is the same staleness this investigation is about.
- That any party has failed at anything. Dates in a connection queue move
  for many reasons, most of them ordinary.
- Anything about a project not on this copy of the register, or about any
  value on any other copy.

## Checks the run must pass, or it fails

- **C1** The five status counts over all rows sum to the copy's row count,
  2,200, and equal the schema report's `project_status` for this copy.
- **C2** dated + undated = 2,200.
- **C3** selected + (dated, not Built, dated on or after the as-of date) +
  (dated, Built) + undated = 2,200.
- **C4** The copy is in 014 version 2's usable set with the same row count,
  and the partial-export rule does not make it suspect.
- **C5** Recomputing writes byte-identical rows; a committed row that would
  change stops the run.

## Falsifiers, declared in advance

- **F1** If more than a fifth of the selected MW sits in rows whose date
  could be read day-month swapped and whose swapped reading is on or after
  the as-of date, the headline is not robust on this copy alone, and it is
  published as a range with the swapped reading stated, not as one number.
- **F2** If the copy carries any schema-report flag, or the partial-export
  rule makes it suspect, no census is published from it.
- **F3** If the two readings of R6 differ by more than a tenth of the
  headline MW, neither is published as "the" figure; the sentence carries
  both numbers or the census is not published.

## Outputs

- `evidence/census.json` — the summary: as-of date, copy digest, counts,
  MW totals under both readings, the four breakdowns, the sensitivities,
  the checks and the falsifier verdicts.
- `evidence/rows.ndjson` — one line per selected row, as published,
  append-only; a line that would change on recompute stops the run.
- `evidence/rule-sources.json` — the test behind every rule above, checked
  by `scripts/check-rules`.
- `FINDINGS.md` — a pure function of the evidence and of the Eggborough
  certificates, which are governed by 014.

## The Eggborough exhibit, and what it is not

Published beside the census as the worked example of why a single copy is
not enough, it consists of As-of Connection Record Certificates issued
under 014's declarations, each with its own witnessed manifest. This
declaration governs none of their content. The certificates state what the
register published and when it changed; they contain no view on cause and
no opinion on entitlement, and the piece adds none.
