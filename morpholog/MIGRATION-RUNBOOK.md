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
| `grid_mysteries_tec` | the TEC record engine (live; `tec/tec-register.morph`, its own signing key) | the same steps, below |
| `grid_mysteries_bill` | the Balancing Bill record engine (live; `bill/bill-register.morph`, key `bill-2026`) | the same steps, below |
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
#    Stop every process on the database first (nothing scheduled touches
#    these three: tec-watch, the vintage watchdog and the crons read files,
#    not the record; scripts/record, the engines' `import`/`checkpoint`
#    and check-record are run by hand).
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

# 3. Managed indexes and statistics, for EVERY programme deployed on the
#    database (from v0.0.12 the interpreted ones too: a proposal's loads seek
#    through them), named together in ONE call (from v0.0.13: the plan is
#    their union, a conflict in any applies nothing, and --prune acts once
#    after all are recorded, so indexes no programme needs are dropped).
#    Naming them one at a time would prune each other's indexes.
PROGS="morpholog/research.morph morpholog/research-v2-draft.morph morpholog/research-v3-draft.morph"
morpholog provision indexes $PROGS --dry-run --database-url $LIVE
morpholog provision indexes $PROGS --prune   --database-url $LIVE
morpholog provision indexes $PROGS --dry-run --database-url $LIVE   # every line KEEP

dropdb gm_migrate_rehearsal
```

Recovery is restore, not reverse: `pg_restore --clean --if-exists -d
grid_mysteries_morpholog "$OUT/grid_mysteries_morpholog.dump"` and keep
using the old binary (`~/.local/bin/morpholog-<old>`) until the cause is
understood.

The TEC record (`grid_mysteries_tec`, programme `tec/tec-register.morph`,
its own signing key) and the Balancing Bill record (`grid_mysteries_bill`,
programme `bill/bill-register.morph`) follow the same steps, each with its
one programme; their baseline is `audit verify --trusted-tsa-file
trust/tsa/digicert-trusted-root-g4.pem` and their packs are not committed
(TEC's live under `data/derived/tec/packs/`).

**Binaries and databases move together.** From v0.0.13 every command
that opens a database, `init` and `migrate` apart, refuses one behind or
ahead of the binary by name before its first query, and the generated
client's `open_session()` refuses a binary of another version than it was
generated for. So the pin in `scripts/install-morpholog`, the vendored
client, the `morpholog` on `PATH` and the three live schemas change in one
move, in this order: prepare the repo (pin, client, docs) and rehearse on
copies; then, when Jordan says, migrate and provision each live record;
then switch `~/.local/bin/morpholog` to the new binary (keep the old one
beside it as `morpholog-<old>`). Between the first and the last step
`scripts/check` fails on the old binary (client drift) and passes on the
new one, and the engines' `Morpholog(...)` (constructed directly, so
unchecked) still run on whichever binary `PATH` gives them.

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

## v0.0.12 to v0.0.13 (schema 17 to 19), rehearsed 2026-09-30

Migrations 018 (`date_ordinal`, the coordinate the compiled checks order
dates by) and 019 (`requirement_position`, each index requirement records
the argument position it seeks on). Release v0.0.13 was published
2026-09-30 19:46 UTC; the three published `.sha256` files match the
release assets' digests and the x86_64 binary extracted from the tarball
(`06afb386…`). Rehearsed the same evening on template copies of all
three live records (`createdb -T`, nothing connected to the sources);
baselines with the 0.0.12 binary and `pg_dump -Fc` of each in
`~/backups/morpholog-20260930T210303Z/`:

- `grid_mysteries_morpholog` (233 transitions, 240 claims, 207
  checkpoints, 13 MB): `migrate` 0.03 s; `audit verify` replay
  consistent, tree intact; claims and pack byte-identical to the 0.0.12
  baseline and to the committed `claims-export.json` and
  `evidence-pack.ndjson`. `provision indexes` naming v1, v2 and v3 in one
  call: 47 indexes KEEP, 50 CREATE, 8 statistics CREATE, nothing stale,
  0.3 s; a second dry run reports all 105 KEEP. The 50 are v3's (deployed
  25/09 after the v0.0.12 provisioning, never provisioned) and the ones
  for v2 and v3 invariants that now compile.
- `grid_mysteries_tec` (137,384 transitions, 127,456 claims, 1 witnessed
  checkpoint, 353 MB): `migrate` 0.03 s; `audit verify` 13.6 s in 300 MB,
  replay consistent, DigiCert witness verified; claims and pack (334 MB)
  byte-identical to the baseline. `provision indexes`: 15 KEEP, 21
  CREATE, 16 statistics CREATE, 1.3 s; second dry run all 52 KEEP.
- `grid_mysteries_bill` (84 transitions, 85 claims, 1 witnessed
  checkpoint, 8.7 MB): `migrate` 0.03 s; `audit verify` consistent and
  intact, DigiCert verified; claims and pack byte-identical. It had never
  been provisioned (it went live 26/09): 59 indexes and 22 statistics
  CREATE, second dry run all 81 KEEP.
- Cross-version, read-only: the 0.0.13 binary against the unmigrated
  live record is refused by name before any query ("the database schema
  is behind this binary (2 migration(s) pending, from 18 (date_ordinal))
  … run `morpholog migrate`"); the 0.0.12 binary against a migrated copy
  still reads (`inspect claims`, `audit verify` consistent) and its
  `migrate --check` lists 018 and 019 as `unknown`, exit 1. As the release
  says, the old binary cannot be retrofitted with the refusal, so switch
  `PATH` in the same move as the migration.
- Decisions unchanged on 0.0.13, on a throwaway cluster (initdb, port
  55434; 55432 is taken by the `morpholog_test` cluster now): both control
  suites (v2 35 commits + 13 refusals, v3 16 + 14, every rule as
  expected), `replay-research` (programme hash, pack, replay, claims
  equality, audit self-check) and `check-record` on the replayed record
  (20 watches open, none overdue), `rehearse-v2` (60 assertions). The
  full `scripts/check` passes with 0.0.13 on `PATH` (573 tests; TEC and
  Bill programmes still `invariant checks: compiled`, pinned hashes
  unchanged; the regenerated client current).
- Route changes, no rule changes: v1, TEC and Bill stay wholly compiled;
  v2 now runs `mixed, 32 compiled, 3 interpreted` and v3 `mixed, 16
  compiled, 5 interpreted` (the interpreted ones are the `or`
  vocabulary invariants). `check -v` prints the split.

Things that changed shape, not meaning:

- `hash` reports carry `morpholog_version`; `scripts/check`,
  `replay-research` and the engines read only `hash` and are unaffected.
- The generated client is stamped 0.0.13 and gains `open_client()` (a
  one-shot client checked against the package's version and model hash
  before its first call), `provision_indexes()` and the `ProvisionReport`
  envelope; `open_session()` now refuses a binary of another version at
  the handshake. The engines construct `Morpholog(...)` directly, on
  purpose: the client is generated from the v2 programme, whose model
  hash a pinned client would hold the TEC and Bill programmes to.
- `provision indexes` takes every programme in one call and prints
  statistics lines beside the index lines; `--json` is the
  `provision_report` envelope. The `propose` error-code set is unchanged
  (`NOT_COMMITTED_CODES` in the Bill importer and `scripts/record` still
  match).
- freetsa.org witnesses are still `unsupported` (ECDSA P-384 with
  SHA-512); DigiCert's verify.

Live migration done the same evening (Jordan's go-ahead, in chat), after
a fresh `pg_dump -Fc` of each record into
`~/backups/morpholog-20260930T202350Z/` (nothing connected to any of
them): all three 17 to 19, `audit verify` consistent and intact with the
DigiCert witnesses verified, claims and packs byte-identical to the
0.0.12 baselines and, for the research record, to the committed
`claims-export.json` and `evidence-pack.ndjson`; indexes and statistics
provisioned with `--prune` in one call per database (research 47 keep +
50 create + 8 statistics, TEC 15 + 21 + 16, Bill 59 + 22), every line
KEEP on the following dry run; the provision reports kept beside the
dumps. Controls and replay databases re-initialised at the new schema;
`~/.local/bin/morpholog` switched to 0.0.13 (0.0.12 kept as
`morpholog-0.0.12`); `check-record` against the live record clean (20
watches open, none overdue); full `scripts/check` green on `PATH`.
