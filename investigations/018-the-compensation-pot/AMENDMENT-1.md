# 018 — Amendment 1 to the declaration: the byte-order mark

**Status: drafted 2026-10-03, after the sealed acquisition of that morning
and after `compute` stopped on its first unreadable file, before any window
figure was computed; not frozen.** On the sponsor's word it is frozen with
`scripts/freeze`, and `compute` refuses to run until this file has its proof
sidecar. `DECLARATION.md` (`3ebd9015…`) is not edited; everything in it
stands except the one reading step below.

## What stopped the compute

The daily cron acquired 144 S0142 files at about 07:25 BST on 2026-10-03
under the seal `3ebd9015`. `compute` then raised `UnicodeDecodeError: 'ascii'
codec can't decode byte 0xef in position 0` and wrote nothing beyond the rows
described under *Prior exposure*.

Eight of the 144 files begin with the three bytes `EF BB BF`, the UTF-8
byte-order mark, immediately before `AAA|S0142013|`. Each carries the mark
once, at the start only. In all 146 S0142 files on disk (the 144 and the two
of the schema pass) there is no other byte above `0x7F`. The reader opened
every file as strict ASCII, which the declaration never states; the schema
pass's two files carry no mark, so the question did not arise before.

| File | Read in |
|---|---|
| `S0142_20260219_R3_20260924153711.gz` | FEB, C4-LATEST |
| `S0142_20260220_R3_20260925081324.gz` | FEB, C4-LATEST |
| `S0142_20260221_R3_20260925080832.gz` | FEB, C4-LATEST |
| `S0142_20260222_R3_20260925090033.gz` | FEB, C4-LATEST |
| `S0142_20260603_R2_20260924163249.gz` | SERIES |
| `S0142_20260805_R1_20260924152439.gz` | SERIES |
| `S0142_20260901_SF_20260924075713.gz` | POST |
| `S0142_20260902_SF_20260925075754.gz` | POST |

None is in PRE or among C4's SF runs. Their file-name stamps run from
2026-09-24 07:57:13 to 2026-09-25 09:00:33 (no zone printed). Every file
stamped 2026-09-23 11:07:50 or earlier, and every one stamped from 2026-09-25
11:04:39 onward, carries no mark: a publication-side episode of about a day, not a
change of format.

## The reading

**A1 — the byte-order mark.** Before a file is read, one UTF-8 byte-order
mark at its first byte is removed. The rest of the file is read as ASCII, as
before; a non-ASCII byte anywhere else, a second mark included, stops the
compute, and reading such a file would need a further amendment. C1 is then
applied, unchanged, to the text that remains.

The mark is an encoding marker and carries no field. With it removed, each
of the eight files begins with the `AAA` record C1 asks for, and every byte
that R1 to R3 read is the byte the file printed.

## What the choice decided, stated before any figure

The alternative was to leave the mark in the text, where the first record id
reads `﻿AAA`, the `AAA` record is not found, and the file fails C1 and
is excluded. FEB would then have four days missing (19 to 22 February), over
the declared limit of two, and **H1-FEB, H2-VTP and H2-SUP would be "not
decided"**; POST would have two missing, at the limit. The sponsor chose A1
on 2026-10-03 knowing this and knowing no figure: no window total, no C4
comparison and no hypothesis input had been computed.

This amendment is taught by the windows' own files, which the doctrine
normally forbids. It is admitted here because what taught it is three bytes
of encoding before the first record, not any value, and because both readings
were set out before either was computed.

## Prior exposure

- Before stopping, `compute` appended 71 rows to `evidence/days.ndjson`
  (committed as written at `c9d28cf`), one per file read without error, in settlement
  date order from 2025-09-03; none is one of the eight files. `compute` now
  re-reads every file and **refuses if the row it computes differs from a row
  already written**, so these rows are shown to be the same under A1 rather
  than assumed to be.
- While diagnosing, the author printed the first 600 characters of the first
  of those rows (`S0142_20250903_II_20250910120421.gz`, an H3 restatement day
  read on II): per-party paid amounts for eight parties. No total of any
  window, no C4 figure and nothing else from `days.ndjson` was read.
- Of the eight marked files, only their first line (the `AAA` header), their
  leading bytes and their count of non-ASCII bytes were inspected.

## The record

`evidence/format-check.json`, written by the runner's `format` phase on
2026-10-03 (field counts of the record types the reader uses, encoding and
flow version; no value), lists exactly these eight files as departing from
the schema pass, each by the leading mark alone; `compute` refuses any
departure that no frozen amendment admits, and A1 admits this one.
`evidence/results.json` gains this file's SHA-256 (`amendment_1_sha256`) and
the list of files read with a leading mark (`leading_byte_order_mark`). The
rows of `days.ndjson` keep their declared shape. The rule is tested in
`tests/test_p415_compensation.py` and mapped in `evidence/rule-sources.json`.
