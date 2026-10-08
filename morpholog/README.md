# The governed research record

This directory *is* the defensible record. Nothing in it requires trusting
the machine it was produced on:

| File | What it is |
|---|---|
| `research.morph` | the governing v1 programme (rules) |
| `research-v2-draft.morph` | the v2 research state machine — check-clean, control-tested, **deployed for Investigations 002 and 004** (batches `090-*.v2.ndjson`, `100-*.v2.ndjson`); v1 remains frozen for the earlier investigations (see `RESEARCH-V2-DESIGN.md`) |
| `research-v3-draft.morph` | the v3 forward/verifier vocabulary — sealed declarations for any frozen artefact, verdicts with reasons, dated watches, reopening triggers, evidence classes with three clocks — check-clean, control-tested (`controls-v3/`, `scripts/check-controls v3`), **deployed 25/09/2026** (batch `110-forward-launch.v3.ndjson`; the file keeps its draft name so the pinned hash and batch dispatch stand); launch rows and the run in `launch-forward/` (see `RESEARCH-V3-DESIGN.md`) |
| `PROGRAMME_HASH.json` / `V2_DRAFT_HASH.json` / `V3_DRAFT_HASH.json` | stable ruleset fingerprints (`morpholog hash`); no programme identity is stored in the database, so these files are the out-of-band record |
| `batches/*.ndjson` | **the canonical input**: every governed transition as a replayable proposal batch, in replay order (`*.v2.ndjson` and `*.v3.ndjson` are proposed against v2 and v3, through the actor's bound login role) |
| `controls/` | negative tests: transitions that must be **refused**, with the exact refusing rule pinned (`scripts/check-controls`, CI-run against a disposable database) |
| `claims-export.json` | derived convenience export of the admitted claims |
| `audit-anchor.json` | externally-held Merkle checkpoint over the audit log — **signed** (Ed25519, key `audit-2026`) from tree_size 34 onward |
| `evidence-pack.ndjson` | portable audit pack (Morpholog pack format 4: a manifest line, the checkpoints, then one audit row per line, so it streams; `evidence-pack.json`, the single-document form, until 25/09/2026); verifies **offline** against the anchor with no database (embedded signatures crypto-checked; key authority folded from the pack's own `AuditSigningKey` claim; the signer pinned to `trust/audit-2026.pub` from tree_size 34 on) |
| `trust/audit-2026.pub` | the signing public key the verifier pins (`audit verify-pack --require-signing-key`): a checkpoint signed by any other key fails, even one authorised by a claim in the log |
| `MIGRATION-RUNBOOK.md` | how each database is migrated when the Morpholog pin moves (forward-only; rehearse on a copy, back up, migrate, verify byte-identical, re-provision the managed indexes). Audit rows written before schema 14 (v0.0.11) carry no parameter names; later rows do |

## Verify it yourself

```bash
./scripts/install-morpholog
./scripts/replay-research   # needs PostgreSQL
```

The offline check alone, with no database, pins the signing key (a
checkpoint signed by any key other than the committed `audit-2026` fails,
even one the log itself authorises; checkpoints are signed from tree size
34 on):

```bash
morpholog audit verify-pack morpholog/evidence-pack.ndjson \
  --anchor-file morpholog/audit-anchor.json \
  --require-signing-key morpholog/trust/audit-2026.pub --require-signatures-from 34
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
   `audit-anchor.json`, and re-export `evidence-pack.ndjson`;
4. re-issue `receipts/metric-retention.json`, the record's one derived
   read (`MetricRetention`, v2) as a receipt naming the programme hash,
   the semantics version, the checkpoint and the answer, which
   `scripts/verify-research-pack` recomputes from the pack alone
   (`morpholog audit verify-receipt`, v0.0.14).

`scripts/record` does all four. `scripts/read-watch <watch> <outcome>
<artefact> <note>` records a dated watch's reading through it in one
command (the artefact's SHA-256 is the reading digest; the note, kept under
the investigation's `watch-readings/`, must name the watch and the digest).
A pack that discloses a row written on
Morpholog v0.0.14 or later is pack format 13 and needs a verifier of that
version (an older one refuses it by name); the rows written before
08/10/2026 carry no programme hash, semantics version or draw list, and
the pack says so rather than guessing them.

Checkpoints before tree_size 140 carry no witness. Both authorities'
tokens verify against the roots in `trust/tsa/` from Morpholog v0.0.14
(morpholog#470); freetsa.org's were stored but reported `unsupported` by
v0.0.11 to v0.0.13, which could not check their signature algorithm (ECDSA
P-384 with SHA-512; morpholog#386), so a report of that era says
`unsupported` for them and nothing weaker.

`scripts/replay-research` fails if any of these drift, so CI enforces the
discipline. The research doctrine for *what* belongs in the record (narrow
claims; manifests, not bulk artefacts; corrections, not rewrites) is in
`CLAUDE.md`.
