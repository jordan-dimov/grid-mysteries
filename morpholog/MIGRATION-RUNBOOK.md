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
morpholog-<old> audit export    --database-url $LIVE > "$OUT/pack.before.json"
morpholog-<old> audit verify    --database-url $LIVE

# 1. Rehearse on a copy (no other session may be connected to the source).
createdb -T grid_mysteries_morpholog gm_migrate_rehearsal
morpholog migrate --check --database-url postgres:///gm_migrate_rehearsal
morpholog migrate         --database-url postgres:///gm_migrate_rehearsal
morpholog audit verify    --database-url postgres:///gm_migrate_rehearsal
#    claims and pack must be byte-identical to the baseline:
morpholog inspect claims --database-url postgres:///gm_migrate_rehearsal | cmp - "$OUT/claims.before.json"
morpholog audit export   --database-url postgres:///gm_migrate_rehearsal | cmp - "$OUT/pack.before.json"

# 2. Back up, then migrate the live record.
pg_dump -Fc -f "$OUT/grid_mysteries_morpholog.dump" grid_mysteries_morpholog
morpholog migrate --check --database-url $LIVE
morpholog migrate         --database-url $LIVE
morpholog migrate --check --database-url $LIVE      # exits zero: current
morpholog audit verify    --database-url $LIVE
morpholog inspect claims  --database-url $LIVE | cmp - morpholog/claims-export.json
morpholog audit export    --database-url $LIVE | cmp - morpholog/evidence-pack.json

# 3. Indexes for compiled programmes (only research.morph compiles today).
morpholog provision indexes morpholog/research.morph --dry-run --database-url $LIVE
morpholog provision indexes morpholog/research.morph           --database-url $LIVE

dropdb gm_migrate_rehearsal
```

Recovery is restore, not reverse: `pg_restore --clean --if-exists -d
grid_mysteries_morpholog "$OUT/grid_mysteries_morpholog.dump"` and keep
using the old binary (`~/.local/bin/morpholog-<old>`) until the cause is
understood.

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
