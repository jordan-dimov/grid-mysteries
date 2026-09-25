# Morpholog schema migration runbook

Migrations are forward-only. A binary refuses to write to a database
whose schema is behind it ("not committed ... run `morpholog migrate`"),
and `migrate --check` refuses a database that is *ahead* of it. Reads
still work while writes refuse, so the record never silently changes.

## The databases

All run on Jordan's laptop cluster, owned by the `jdimov` login, which
also owns the `morpholog` schema and every table in it (so `migrate`
runs as the schema owner; there is no separate writer role in force
here).

| Database | What it is | How it is migrated |
|---|---|---|
| `grid_mysteries_morpholog` | **the governed record** (live) | by hand, below, after a rehearsal; Jordan decides when |
| `grid_mysteries_replay` | disposable, rebuilt by `scripts/replay-research` | `init --reset` each run |
| `grid_mysteries_controls` | disposable, rebuilt by `scripts/check-controls` | `init --reset` each run |
| `gm_rehearsal` | disposable, dropped and recreated by `scripts/rehearse-v2` | recreated each run; **never name a migration rehearsal copy this** |
| CI service containers | fresh `postgres:16` per job | always at the pinned binary's schema |

`scripts/replay-research` provisions the `gm_human` and `gm_machine`
login roles the record names, cluster-wide, and never drops them; it
refuses to run where they already exist. Run it in CI or on a throwaway
cluster, never beside the live record.

## Procedure for the live record

```bash
LIVE=postgres:///grid_mysteries_morpholog
OUT=~/backups/morpholog-$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$OUT"

# 0. Baseline, read-only, with the binary that matches the live schema.
morpholog-<old> inspect claims  --database-url $LIVE > "$OUT/claims.before.json"
morpholog-<old> audit export    --database-url $LIVE > "$OUT/pack.before.ndjson"
morpholog-<old> audit verify    --database-url $LIVE

# 1. Rehearse on a copy (no other session may be connected to the source).
createdb -T grid_mysteries_morpholog gm_migrate_rehearsal
morpholog migrate --check --database-url postgres:///gm_migrate_rehearsal
morpholog migrate         --database-url postgres:///gm_migrate_rehearsal
morpholog audit verify    --database-url postgres:///gm_migrate_rehearsal
#    claims and pack must be byte-identical to the baseline:
morpholog inspect claims --database-url postgres:///gm_migrate_rehearsal | cmp - "$OUT/claims.before.json"
morpholog audit export   --database-url postgres:///gm_migrate_rehearsal | cmp - "$OUT/pack.before.ndjson"

# 2. Back up, then migrate the live record.
pg_dump -Fc -f "$OUT/grid_mysteries_morpholog.dump" grid_mysteries_morpholog
morpholog migrate --check --database-url $LIVE
morpholog migrate         --database-url $LIVE
morpholog migrate --check --database-url $LIVE      # exits zero: current
morpholog audit verify    --database-url $LIVE
morpholog inspect claims  --database-url $LIVE | cmp - morpholog/claims-export.json
morpholog audit export    --database-url $LIVE | cmp - morpholog/evidence-pack.ndjson

# 3. Managed indexes, for EVERY programme deployed on the database (from
#    v0.0.12 the interpreted ones too: a proposal's loads seek through them),
#    with --prune on the last run so indexes no programme needs are dropped.
morpholog provision indexes morpholog/research.morph          --dry-run --database-url $LIVE
morpholog provision indexes morpholog/research-v2-draft.morph --dry-run --database-url $LIVE
morpholog provision indexes morpholog/research.morph                    --database-url $LIVE
morpholog provision indexes morpholog/research-v2-draft.morph --prune   --database-url $LIVE

dropdb gm_migrate_rehearsal
```

Recovery is restore, not reverse: `pg_restore --clean --if-exists -d
grid_mysteries_morpholog "$OUT/grid_mysteries_morpholog.dump"` and keep
using the old binary (`~/.local/bin/morpholog-<old>`) until the cause is
understood.

The TEC record (`grid_mysteries_tec`, programme `tec/tec-register.morph`,
its own signing key) follows the same steps; its baseline is `audit verify
--trusted-tsa-file trust/tsa/digicert-trusted-root-g4.pem` and its pack is
not committed (it lives under `data/derived/tec/packs/`).

## v0.0.10 to v0.0.11 (schema 11 to 15), rehearsed 2026-09-23

Migrations 012 (claims keyed by a digest of their arguments), 013
(checkpoint witnesses), 014 (audit rows name their parameters) and 015
(the registry of managed indexes). Measured on a copy of the live
record (139 transitions, 146 claims, 113 checkpoints, 9 MB):

- `migrate`: 0.03 s. `audit verify`: replay consistent, tree intact,
  113 checkpoints, tree_size 139.
- Claims export and evidence pack byte-identical to live and to the
  committed `claims-export.json` and `evidence-pack.json`.
- `provision indexes morpholog/research.morph`: 8 indexes created in
  0.03 s; a second dry run reports all 8 `KEEP`; v2 and v3 have no
  compiled invariants and nothing to provision.

Things that changed shape, not meaning:

- `morpholog.claims` gains a generated `arguments_hash` column. A fresh
  v0.0.11 schema places it third, a migrated one last, so raw SQL must
  name its columns (`scripts/rehearse-v2` does).
- `morpholog.audit` gains `parameters`, and new rows must carry it
  (`audit_parameters_required`, `NOT VALID`, so the 139 existing rows
  keep `NULL`). Rows written before the migration stay unnamed; any
  pack spanning the migration mixes unnamed and named rows. That is
  deliberate: a name would be a claim about the past.

## v0.0.11 to v0.0.12 (schema 15 to 17), rehearsed 2026-09-25

Migrations 016 (`timestamp_nanos`, a function ordering stored instants)
and 017 (`value_key_v1`, one equality key over every stored value, which
the compiled checks and the new keyed loads seek through). Measured on
template copies of both live records:

- `grid_mysteries_morpholog` (139 transitions, 146 claims, 113
  checkpoints, 9.6 MB): `migrate` 0.03 s; `audit verify` replay
  consistent, tree intact; claims byte-identical to the baseline and to
  the committed `claims-export.json`; the exported pack's 139 rows and
  113 checkpoints equal the format-1 pack's, and it verifies offline
  against the committed anchor with the pinned key.
- `grid_mysteries_tec` (137,384 transitions, 127,456 claims, 1 witnessed
  checkpoint, 352 MB): `migrate` 0.05 s; `audit verify` 22 s in 297 MB
  of memory (the streaming verifier of #395; the same record needed
  gigabytes on v0.0.11), replay consistent, DigiCert witness verified.
- `provision indexes`: the v0.0.11 `text` indexes are reported `STALE`
  (required by no programme) and dropped by `--prune`; new `value_key_v1`
  indexes are created for v1 (10), v2 (38, `AuditSigningKey` shared with
  v1 and kept) and the TEC register (15). v3 is not deployed and was not
  provisioned.
- The old binary reads a migrated database (`inspect claims` identical)
  but `migrate --check` reports the two migrations as `unknown` and exits
  non-zero; the new binary reads an unmigrated one (its `audit export` of
  the live record before migration was byte-identical to the rehearsal
  copy's after).
- Decisions unchanged: both control suites (v2 35 commits + 13 refusals,
  v3 16 + 14) decided on 0.0.11 and 0.0.12 into separate databases on a
  throwaway cluster, 78 of 78 receipts identical once transition ids and
  commit times are dropped; `rehearse-v2` identical on both (60
  assertions); the whole record replays under 0.0.12 into the committed
  claims export.

Things that changed shape, not meaning:

- `audit export` of a complete prefix writes NDJSON (pack format 4): a
  manifest line, then the checkpoints, then one audit row per line. The
  committed pack is now `evidence-pack.ndjson`, re-exported from the live
  record on 25/09/2026 before the migration (the rows and checkpoints
  are those of the format-1 `evidence-pack.json` it replaces, verified
  against the same anchor). A v0.0.11 binary cannot read the new form
  (`malformed_pack`); v0.0.12 reads both. The TEC engine names new packs
  `tree-<n>.ndjson` and keeps reading the format-1 `tree-137384.json`.
- `audit verify-pack` always prints the report (`verdict` plus
  `role_rebindings`); scripts that parsed a bare verdict must read
  `verdict.status`.
- freetsa.org witnesses are still `unsupported` (ECDSA P-384 with
  SHA-512 is not implemented in the verifier); DigiCert's verify.
- The generated client is stamped 0.0.12: `MorphologBatchIncomplete`,
  `RequestError`, `RoleRebindings`; `EvidencePack` is gone and
  `audit_export(path)` writes the pack to a path and returns its
  manifest. Nothing in `src/grid_mysteries` used either.

Live migration done the same evening (Jordan's go-ahead, in chat), after
`pg_dump` of both records into `~/backups/morpholog-20260925T210903Z/`:
`grid_mysteries_morpholog` 15 to 17, `audit verify` consistent and
intact (139 transitions, 113 checkpoints), claims export and pack
byte-identical to the committed files, indexes provisioned for v1 then
v2 with `--prune` (a further dry run of each reports every index KEEP);
`grid_mysteries_tec` 15 to 17, `audit verify` consistent and intact in
22 s with the DigiCert witness verified, indexes provisioned with
`--prune`, a fresh format-4 export holding all 137,384 rows. Controls
and replay databases re-initialised at schema 17; `check-record`
against the live record clean.

