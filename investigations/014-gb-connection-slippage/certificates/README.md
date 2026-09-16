# As-of Connection Record Certificates

A certificate states what NESO's TEC Register published about one project on
each of two dates, and every change between them with the copy of the
register that first showed it. It is a factual record of publication: no
forecast, no view on cause, no opinion on entitlement. The standard claim
wording is the one in the certificate's own header.

## Producing one

    uv run --group registers python investigations/014-gb-connection-slippage/certify.py \
        --project "<project name as the register prints it>" \
        --from YYYY-MM-DD --to YYYY-MM-DD [--stage N] [--issued YYYY-MM-DD]
    scripts/timestamp certificates/<bundle>/MANIFEST.json
    scripts/timestamp certificates/<bundle>/CERTIFICATE.md

Inputs are the project name (matched on letters and digits, case ignored),
an optional stage, and two dates (an investment paper's date, a signing
date). The copy in force on a date is the latest copy published on or before
it. A bundle is never overwritten; a re-issue is a new directory.

## What a bundle contains

| File | What it is | Listed in the manifest |
|---|---|---|
| `certificate.json` | the record: as-of state on each date, every change, counts | yes |
| `extracts.ndjson` | one line per copy consulted: date, copy digest, matching rows as published | yes |
| `journal-extract.ndjson` | the archive's journal line per copy: source, URL, publication basis, digest | yes |
| `registers/` | the two full register copies in force on the certified dates | yes |
| `MANIFEST.json` | the files above with SHA-256 and size; its own SHA-256 is the certificate id | — |
| `CERTIFICATE.md` | the two-page certificate, rendered from the record and the manifest; quotes the id | no (it quotes the manifest, so listing it would be a hash cycle) |
| `verify.py` | stdlib-only offline check of every digest and of the as-of copies against the journal | no |
| `*.ots`, `*.tsq`, `*.tsr`, `*.timestamps.json` | OpenTimestamps and RFC 3161 proofs for the manifest and the certificate | no |
| `delivery/CERTIFICATE.pdf`, `delivery/COVER-NOTE.md` | the PDF rendering of the certificate (`scripts/certificate-pdf`, two A4 pages, witnessed) and the cover note that goes with it | no |

## Verifying one, offline

    cd certificates/<bundle> && python3 verify.py
    scripts/verify-timestamp certificates/<bundle>/MANIFEST.json
    scripts/verify-timestamp certificates/<bundle>/CERTIFICATE.md

The first recomputes every digest in the manifest and checks that the two
register copies hash as the journal says. The second and third verify the
RFC 3161 tokens against the roots committed under `trust/tsa/` and check
that the OpenTimestamps proof is for the file (the Bitcoin attestation needs
`ots verify`, online, once the proof has been upgraded). Anyone holding the
archive of copies can re-run `certify.py` and diff the result.

## Rules the certificate follows

- Tracking is by the register's own project name and, where given, stage.
  Customer name and connection site are attributes whose changes are
  recorded; the series in `DECLARATION.md` uses the full identity instead,
  and says so. A copy with no matching row is an absence; one with several
  matching rows is ambiguous. Both are changes of presence.
- Values are compared as published: dates parsed (a respelling is not a
  change), numbers numerically, text ignoring case and whitespace. The
  printed values are the published spellings.
- Two label unifications are declared (`connection_record.LABEL_VARIANTS`
  and `SALESFORCE_ID_LENGTH`): the project id is compared on its
  15-character form, because the register alternates between the
  15-character Salesforce id and the 18-character form that appends a
  checksum to it; and the agreement-type labels "Directly Connected" and
  "Direct Connection", which alternate between source files, are one label.
  Any further variant is added here before it is used, never after a
  certificate has been read. The Clash Gour exemplar was issued before
  these unifications and shows those flips as changes 2, 3, 9 to 12, 16
  and 18; a re-issue would not.
- Every change is dated by the first copy that showed it and by the last
  copy that still carried the previous value. No copy is held between the
  two, so the change entered the published register in that interval.
- A copy whose row count falls by more than a fifth against the previous
  copy and whose successor recovers by more than a fifth is a *suspect
  copy* (a partial export; `connection_slippage.partial_exports`). The
  certificate names the suspect copies it consulted, and an absence from
  one is reported as "absent from a suspect copy", never as an absence
  from the register. The Clash Gour exemplar predates this rule; its change
  5 (absent on 2023-11-28) is exactly such a copy.
- The archive's own reading rules apply (every era's column names, every
  date spelling, day-month swapped copies read back), as declared for the
  series.

## Exemplar

`clash-gour-2021-03-31-2025-07-22/`: Clash Gour (EDF Energy Renewables,
210 MW, SHET), chosen because its published target date moved through five
distinct values across the archive (2023, 2024, 2025, 2027 and 2029), all
on unambiguous dates, and it is still on the register. Chosen from 005's
per-project metrics table, which is disclosed in the series declaration.
