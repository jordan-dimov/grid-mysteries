# The governed research record

This directory *is* the defensible record. Nothing in it requires trusting
the machine it was produced on:

| File | What it is |
|---|---|
| `research.morph` | the governing v1 programme (rules) |
| `research-v2-draft.morph` | the v2 research state machine — check-clean, control-tested, **deployed for Investigations 002 and 004** (batches `090-*.v2.ndjson`, `100-*.v2.ndjson`); v1 remains frozen for the earlier investigations (see `RESEARCH-V2-DESIGN.md`) |
| `research-v3-draft.morph` | the v3 forward/verifier vocabulary — sealed declarations for any frozen artefact, verdicts with reasons, dated watches, reopening triggers, evidence classes with three clocks — check-clean, control-tested (`controls-v3/`, `scripts/check-controls v3`), **not yet deployed**; launch rows in `launch-forward/` (see `RESEARCH-V3-DESIGN.md`) |
| `PROGRAMME_HASH.json` / `V2_DRAFT_HASH.json` / `V3_DRAFT_HASH.json` | stable ruleset fingerprints (`morpholog hash`); no programme identity is stored in the database, so these files are the out-of-band record |
| `batches/*.ndjson` | **the canonical input**: every governed transition as a replayable proposal batch, in replay order |
| `controls/` | negative tests: transitions that must be **refused**, with the exact refusing rule pinned (`scripts/check-controls`, CI-run against a disposable database) |
| `claims-export.json` | derived convenience export of the admitted claims |
| `audit-anchor.json` | externally-held Merkle checkpoint over the audit log — **signed** (Ed25519, key `audit-2026`) from tree_size 34 onward |
| `evidence-pack.json` | portable audit pack; verifies **offline** against the anchor with no database (embedded signatures crypto-checked; key authority folded from the pack's own `AuditSigningKey` claim; the signer pinned to `trust/audit-2026.pub` from tree_size 34 on) |
| `trust/audit-2026.pub` | the signing public key the verifier pins (`audit verify-pack --require-signing-key`): a checkpoint signed by any other key fails, even one authorised by a claim in the log |
| `MIGRATION-RUNBOOK.md` | how each database is migrated when the Morpholog pin moves (forward-only; rehearse on a copy, back up, migrate, verify byte-identical). Audit rows written before schema 14 (v0.0.11) carry no parameter names; later rows do |

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
3. record a new signed checkpoint over the extended log, witnessed by
   two RFC 3161 authorities (freetsa.org, DigiCert), into
   `audit-anchor.json`, and re-export `evidence-pack.json`.

Checkpoints before tree_size 140 carry no witness. freetsa.org's tokens
are stored but reported `unsupported` by Morpholog v0.0.11, which cannot
yet check their signature algorithm (ECDSA with SHA-512); DigiCert's
verify against `trust/tsa/`.

`scripts/replay-research` fails if any of these drift, so CI enforces the
discipline. The research doctrine for *what* belongs in the record (narrow
claims; manifests, not bulk artefacts; corrections, not rewrites) is in
`CLAUDE.md`.
