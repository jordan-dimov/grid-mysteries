# The TEC record engine

NESO's TEC register as a governed record: every publication we hold,
imported in order, so that "what did the register print about project X on
date D" has an answer a stranger can verify without trusting this machine.
Brief and spike: `~/dev/etrmbiz/notes/2026-09-23-tec-record-engine-spike/`.

## Two layers

**The record** (`tec-register.morph`, database `grid_mysteries_tec`, never
the research record's) holds rows exactly as the declared reader extracts
them. No date is parsed, no day-month swap corrected, no identity inferred:

- a row is its fifteen canonical cells as text (numbers written canonically,
  spreadsheet date cells as ISO dates), and `RowKinds` says what each cell
  was (`t` text, `i` integer, `f` float, `d` date cell, `-` blank or absent),
  so the reader's values come back exactly (`tec/cells.py`; checked over all
  593,853 rows of the archive);
- a row's key is a digest of its cells plus its occurrence among identical
  rows of the same publication. The same line printed in a CSV, an xlsx and
  an xls copy is one row whose kinds change (`rekind`), not three rows;
- each publication imports as one `transact`: `publish`, then `drop_row`,
  `rekind` and `add_row` for what changed, then `close_import`, which also
  records the file's line order. Only the publication being imported can
  change the record, publications import in date order, and nothing changes
  it between imports. `Vintage` names each copy by the SHA-256 of its bytes.

**The analysis** (`src/grid_mysteries/tec/analysis.py`) reads the record
back through its audit log (`tec/replay.py`), never the source files, and
writes its claims under `tec/analysis/`, each naming its rule and the anchor
(tree size, root hash) it read:

| Rule | What it is |
|---|---|
| `014-v2` | investigation 014's declaration v2, computed by 014's own module. `differential-014.json` compares its rows with 014's committed `evidence/v2/rows.ndjson`, line by line |
| `tec-identity-content-v1` | 014 v2's reading rules and arithmetic, with units matched by content within each project group (`tec/identity.py`), never by row order |
| `spike-positional` | the spike's key, kept only to explain the spike's flapping |

`flapping.json` counts, per rule, date moves reversed by the unit's next
move, and whether the files themselves show each reversal (the group's
printed MW and dates moved that way). `series-content-v1.json` sets the
content rule's series beside 014's and decomposes the headline difference
group by group.

## Running it (the laptop, by hand)

```bash
# after the watchdog has synced data/manifests/ and data/raw/archive/
uv run --group registers python -m grid_mysteries.tec import
uv run python -m grid_mysteries.tec checkpoint --witness     # signs; DigiCert countersigns
uv run --group registers python -m grid_mysteries.tec analyse
uv run --group registers python -m grid_mysteries.tec certify --project "East Anglia One" \
    --on 2016-06-20 --on 2019-06-27 --on 2022-06-30
```

`import` refuses when a readable copy dated at or before the record's
current publication is missing from it (an EIR reply filling a gap, say):
the record is forward-only, so such a copy means rebuilding it into a fresh
database. `--accept-stranded` imports newer copies anyway and lists them.
`import` reads the journal (`data/raw/neso/tec-history/journal.ndjson`) and
the capture archive's TEC copies, dated by the CKAN `last_modified` captured
beside them; it writes neither. Nothing here runs on Render; the capture
and 013 jobs propose nothing to any Morpholog database.

**Recovery.** Each transact is guarded by a marker kept per database under
`data/derived/tec/`. It is cleared only on a rejection or an error code the
runtime documents as "nothing recorded"; anything else, including a killed
process, leaves it, and the next import refuses until someone has read the
record (`CurrentVintage`, `Importing`) and removed it.

## Certificates

`certify` writes `data/derived/tec/certificates/<project>-<dates>/`:

- `CERTIFICATE.md` and `certificate.json`: for each date, the lines as
  published in the latest publication the record holds on or before it, with
  that copy's SHA-256 and journal or capture provenance, the days between
  (flagged past 60), any copy held for the interval that the record does not
  include, and the transition that closed its import; then every publication
  in between where the project's lines changed;
- the **complete** audit pack (`pack.json.gz`) and its signed, witnessed
  `anchor.json`, the pinned key, DigiCert's root, `lines_from_pack.py` and
  `MANIFEST.json`.

Before writing, the generator checks that the runtime's own as-of read and a
fold of the verified pack give the same lines, and runs the bundled script on
the pack.

```bash
gunzip -k pack.json.gz
morpholog audit verify-pack pack.json --anchor-file anchor.json \
  --require-signing-key tec-2026.pub --trusted-tsa-file digicert-trusted-root-g4.pem
python3 lines_from_pack.py pack.json certificate.json
```

The complete pack proves both that the lines are authentic and that nothing
was left out; the register is public, so there is no reason to be selective.

## Files here

| File | What it is |
|---|---|
| `tec-register.morph` | the record's programme; must stay on the compiled route (`scripts/check` fails otherwise) |
| `PROGRAMME_HASH.json` | its pinned fingerprint (`scripts/check` fails on drift) |
| `trust/tec-2026.pub` | the checkpoint signing key verifiers pin (private key at `~/.config/grid-mysteries/tec-signing-2026.pem`, never committed) |
| `anchors/tree-<n>.json` | signed, witnessed checkpoints of the record, as printed |
| `analysis/` | the analysis claims, each naming its rule and anchor |

## Limits

- The record holds what the declared reader extracts: the fifteen canonical
  columns, not every column a copy carried; a spreadsheet's display format
  is not kept.
- 32 copies (31 early-2014 `.xls` files and 2021-06-22) do not parse and are
  not in the record; the importer lists them.
- The actor on every import is the assertion `tec_importer`, recorded by the
  gateway, not a signature (Morpholog #202 is open).
