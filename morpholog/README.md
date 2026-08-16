# The governed research record

This directory *is* the defensible record. Nothing in it requires trusting
the machine it was produced on:

| File | What it is |
|---|---|
| `research.morph` | the governing v1 programme (rules) |
| `research-v2-draft.morph` | the v2 research state machine — check-clean, control-tested, **not yet deployed** (see `RESEARCH-V2-DESIGN.md`) |
| `PROGRAMME_HASH.json` / `V2_DRAFT_HASH.json` | stable ruleset fingerprints (`morpholog hash`); no programme identity is stored in the database, so these files are the out-of-band record |
| `batches/*.ndjson` | **the canonical input**: every governed transition as a replayable proposal batch, in replay order |
| `controls/` | negative tests: transitions that must be **refused**, with the exact refusing rule pinned (`scripts/check-controls`, CI-run against a disposable database) |
| `claims-export.json` | derived convenience export of the admitted claims |
| `audit-anchor.json` | externally-held Merkle checkpoint over the audit log — **signed** (Ed25519, key `audit-2026`) from tree_size 34 onward |
| `evidence-pack.json` | portable audit pack; verifies **offline** against the anchor with no database (embedded signatures crypto-checked; key authority folded from the pack's own `AuditSigningKey` claim) |
| `trust/audit-2026.pub` | the signing public key, committed as documentation — verification reads the key from the checkpoint itself and judges authority against the governed claim, never from this file |

## Verify it yourself

```bash
./scripts/install-morpholog
./scripts/replay-research   # needs PostgreSQL
```

A precision note on what is and is not in the audit log: only **committed
transitions** are Merkle-audited (the anchor's `tree_size` is their exact
count). **Refusals are not transitions** — a business rejection (such as
001C's finding being lawfully refused until its provenance was attached)
leaves a receipt and an operational rejection-log row, not an audit row,
and actor-assertion refusals appear in neither. The audit chain proves
what was admitted; the controls prove what gets refused.

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
