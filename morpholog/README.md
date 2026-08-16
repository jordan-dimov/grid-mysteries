# The governed research record

This directory *is* the defensible record. Nothing in it requires trusting
the machine it was produced on:

| File | What it is |
|---|---|
| `research.morph` | the governing programme (rules) |
| `PROGRAMME_HASH.json` | the programme's stable fingerprint (`morpholog hash`), insensitive to formatting |
| `batches/*.ndjson` | **the canonical input**: every governed transition as a replayable proposal batch, in replay order |
| `claims-export.json` | derived convenience export of the admitted claims |
| `audit-anchor.json` | externally-held Merkle checkpoint over the audit log |
| `evidence-pack.json` | portable audit pack; verifies **offline** against the anchor with no database |

## Verify it yourself

```bash
./scripts/install-morpholog
./scripts/replay-research   # needs PostgreSQL
```

`replay-research` (also run by CI on every push, against a fresh service
database) checks that: the programme hash matches the pinned fingerprint;
the evidence pack verifies offline against the anchor; every batch row
commits under the rules into a fresh database; the replayed claims equal
`claims-export.json`; and the replayed audit log self-verifies. The
evidence pack additionally lets a third party verify transition ordering
(hypothesis-before-finding, source-before-finding) cryptographically,
without reproducing anything.

## Updating the record

Governed state changes **only** through `morpholog propose`. After any
accepted proposal, in the same commit:

1. append the proposal row to the investigation's batch file under
   `batches/`;
2. refresh `claims-export.json` (`morpholog inspect claims`);
3. record a new checkpoint over the extended log
   (`morpholog audit checkpoint > audit-anchor.json`) and re-export
   `evidence-pack.json`.

`scripts/replay-research` fails if any of these drift, so CI enforces the
discipline. The research doctrine for *what* belongs in the record (narrow
claims; manifests, not bulk artefacts; corrections, not rewrites) is in
`CLAUDE.md`.
