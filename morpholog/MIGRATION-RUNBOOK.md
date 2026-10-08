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
cluster, never beside the live record. `scripts/rehearse-v2` creates and
drops its own pair, `gm_rehearsal_writer` / `gm_rehearsal_reader`, with
its database (from v0.0.14 `init --least-privilege` refuses a pair that
exists on the cluster and is not this database's).

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
morpholog provision indexes $PROGS --check   --database-url $LIVE   # exit 0: current
#    (`--check` changes nothing and exits non-zero on anything to create,
#    repair or prune, from v0.0.14; it is the deploy gate. A programme
#    deployed after this step, as v3 and the Bill record were, is
#    unprovisioned until the step is run again: provisioning belongs in
#    every deploy, not only in migrations. From 08/10/2026 the gate also
#    runs by itself: `scripts/check-record` asks it of the research record
#    and every engine `import` asks it of its own before writing.)

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
  (`malformed_pack`); v0.0.12 reads both. The TEC engine names its packs
  `tree-<n>.ndjson`; its format-1 `tree-137384.json` was re-exported in the
  new form on 30/09/2026 (same anchor, verifies the same) and the engine
  reads only the streaming form since.
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

## v0.0.13 to v0.0.14 (schema 19 to 23), rehearsed 2026-10-08

Migrations 020 (`audit.model_hash`: the hash of the programme that
admitted the row), 021 (`audit.semantics_version`: the version of the
rules' meaning that decided it), 022 (`audit.drawn_subjects`: the fresh
subjects the act drew, in order) and 023 (`morpholog.deployment_roles`:
the least-privilege pair this database records). Release v0.0.14 was
published 2026-10-08 07:25 UTC; the three published `.sha256` files match
the release assets' digests and the x86_64 binary extracted from the
tarball (`46b306fe…`) is byte-identical to `~/.local/bin/morpholog-0.0.14`.
None of the audit columns is backfilled: the rows written before the
migration stay `NULL` there, keep their earlier Merkle leaf encodings, and
the record says so. Rehearsed the same morning on template copies of all
three live records (`createdb -T`, nothing connected to the sources);
baselines with the 0.0.13 binary and `pg_dump -Fc` of each in
`~/backups/morpholog-20261008T075426Z/`, with every rehearsal report
beside them:

- `grid_mysteries_morpholog` (235 transitions, 242 claims, 209
  checkpoints; the 235th is the 018 watch reading recorded that morning,
  before the baseline): `migrate` 0.03 s; `audit verify` `passes`, replay
  consistent, tree intact, **every freetsa.org witness now `verified`**
  (96 of 96, beside DigiCert's 96; they were `unsupported` since v0.0.11);
  claims and pack byte-identical to the baseline and to the committed
  `claims-export.json` and `evidence-pack.ndjson`. `provision indexes`
  naming v1, v2 and v3 in one call: every index and statistics object
  KEEP, nothing to create, `--check` exits 0. `deployment_roles` records
  `morpholog_writer` / `morpholog_reader`, the cluster pair.
- `grid_mysteries_tec` (137,384 transitions, 127,456 claims, 1 witnessed
  checkpoint): `migrate` 0.14 s; `audit verify` 12.5 s in 299 MB,
  `passes`, DigiCert verified; claims and pack (334 MB) byte-identical;
  provisioning all KEEP, `--check` current.
- `grid_mysteries_bill` (84 transitions, 85 claims, 1 witnessed
  checkpoint): `migrate` 0.02 s; `audit verify` `passes`; claims and pack
  byte-identical; provisioning all KEEP, `--check` current.
- `migrate` warns, on every one of the three, that `morpholog_writer` and
  `morpholog_reader` also hold privileges in the other two, in the four
  scratch databases and (until it was moved on 08/10) in `bizgov`. The
  warning is informational; the move to own roles is its own step, below.
- Decisions unchanged on 0.0.14, on a throwaway cluster (initdb, port
  55435): both control suites (v2 35 commits + 13 refusals, v3 16 + 14,
  every rule as expected), `replay-research` (programme hashes, pack and
  receipt offline, replay, 242 claims identical, audit self-check, then
  provisioned and `--check` current) and `check-record` on the replayed
  record (provisioned, no drift, 20 watches open, none overdue),
  `rehearse-v2` twice on the same cluster (60 assertions each). The full
  `scripts/check` passes with 0.0.14 on `PATH` (666 tests; every pinned
  programme hash unchanged; the regenerated client current).
- On a restored copy of the research record on the throwaway cluster,
  after the migration: a `declare` through `gm_machine` and a
  `seal_declaration` through `gm_human` commit, `gm_machine` asserting
  `jordan_dimov` is refused (`actor_assertion_unauthorised`), and the two
  new rows carry the v3 programme hash, semantics version 1 and an empty
  draw list, while the row before them carries `NULL`s. A checkpoint over
  them and an export give a pack of **format 13**, which the 0.0.13
  verifier refuses by name (`malformed_pack`: "pack_format_version 13 is
  newer than this binary understands") and 0.0.14 verifies. **So the
  committed `evidence-pack.ndjson` becomes unreadable to every verifier
  older than 0.0.14 at the first `scripts/record` after the migration**;
  the pack of 235 rows, format 4, stays readable to 0.0.12 and 0.0.13.
- `check --strict` on 0.0.14 newly fails v3 on one hint: invariant
  `three_clocks_ordered` leaves the declared-key field `claim` of
  `EvidenceClaim` unconstrained (#446, "a rule whose case is wider than
  the claim it guards"). `scripts/check-programmes` runs `check`, not
  `--strict`, so nothing fails; respelling the rule moves the pinned v3
  hash of a deployed programme and is the sponsor's call. The other five
  programmes are strict-clean.

Things that changed shape, not meaning:

- Every verification report leads with `passes` (#468), the same answer
  as the exit code. `exported_pack` in `src/grid_mysteries/record.py`
  reads it and no longer restates the rule (morpholog#435 is closed).
- `check --json` lists every invariant with its route (#445);
  `scripts/check-programmes` reads it there and no longer greps the prose
  of `check -v` (morpholog#410 is closed).
- `provision indexes --check` (#467) is the deploy gate: in the procedure
  above, in `scripts/check-record` (the research record), in
  `scripts/replay-research` (the replayed one) and, through
  `record.provisioned`, at the start of every engine `import`.
- Receipts (#462): `morpholog/receipts/metric-retention.json` is the
  record's one derived read (`MetricRetention`, v2) as a receipt naming the
  programme hash, the semantics version, the checkpoint and the answer;
  `scripts/record` re-issues it after every export and
  `scripts/verify-research-pack` recomputes it from the committed pack
  under the pinned key and the TSA roots. First issued at tree size 235
  (`inq-002`: 0.2363…).
- A raw-SQL forgery of an audit row must now supply `model_hash`,
  `semantics_version` and `drawn_subjects`, named (`scripts/rehearse-v2`
  §H2 does; a migrated database orders the columns differently from a
  fresh one, so positional SQL is wrong on one of them).
- The generated client is stamped 0.0.14: `Request` protocol and
  `submit_all`, `audit_receipt` / `audit_verify_receipt`,
  `provision_indexes(check=True)` with `ProvisionReport.is_current`,
  `CheckReport.route`, the audit-row envelopes with the three new fields
  (`AuditRow` refuses unknown fields from now on). The engines still
  construct `Morpholog(...)` directly, for the reason given under
  v0.0.13.

Live migration, run 08/10/2026 (12:06 to 12:30 UTC) on Jordan's word,
with the sequence below, from the repo root with nothing connected to
any of the three (the 10:30/22:30 watchdog and the TEC watch read files,
not the record); the `.pre-migration.dump`, `migrate`, `verify` and
`provision` reports of each database kept as `*.live.*` beside the
morning's baselines in `~/backups/morpholog-20261008T075426Z/`:

- all three 19 to 23 in one `migrate` each (020 to 023 applied, nothing
  pending); `migrate --check` current afterwards;
- `audit verify` `passes` on all three with the freetsa.org and DigiCert
  roots: the research record's 96 freetsa.org and 96 DigiCert witnesses
  all `verified`, the engines' DigiCert witnesses verified;
- claims and packs of all three byte-identical to the 0.0.13 baselines
  taken that morning (and so to the committed `claims-export.json` and
  `evidence-pack.ndjson`, format 4, tree size 235);
- `provision indexes --prune` in one call per database (research naming
  v1, v2 and v3): every line KEEP, nothing created or dropped, statistics
  re-analysed; `--check` exits 0 on all three;
- the move to each record's own roles, below, in the same session;
- `grid_mysteries_replay` and `grid_mysteries_controls` re-initialised at
  schema 23; `~/.local/bin/morpholog` switched to 0.0.14 (0.0.13 kept as
  `morpholog-0.0.13`; 0.0.10 to 0.0.12, which refuse every record from
  here on, removed); `check-record` against the live record clean
  (provisioned, no drift, 20 watches open, none overdue); `check-controls`
  OK; full `scripts/check` green on `PATH` (666 tests).

The sequence as run:

```bash
OUT=~/backups/morpholog-20261008T075426Z          # the baselines are already there
for db in grid_mysteries_morpholog grid_mysteries_tec grid_mysteries_bill; do
  pg_dump -Fc -f "$OUT/$db.pre-migration.dump" $db
  morpholog-0.0.14 migrate --check --database-url postgres:///$db || true
  morpholog-0.0.14 migrate         --database-url postgres:///$db
  morpholog-0.0.14 audit verify    --database-url postgres:///$db \
    --trusted-tsa-file <(cat trust/tsa/freetsa-cacert.pem trust/tsa/digicert-trusted-root-g4.pem)
  morpholog-0.0.14 inspect claims  --database-url postgres:///$db | cmp - "$OUT/$db.claims.before.json"
  morpholog-0.0.14 audit export    --database-url postgres:///$db | cmp - "$OUT/$db.pack.before.ndjson"
done
morpholog-0.0.14 provision indexes morpholog/research.morph morpholog/research-v2-draft.morph \
  morpholog/research-v3-draft.morph --prune --database-url postgres:///grid_mysteries_morpholog
morpholog-0.0.14 provision indexes tec/tec-register.morph   --prune --database-url postgres:///grid_mysteries_tec
morpholog-0.0.14 provision indexes bill/bill-register.morph --prune --database-url postgres:///grid_mysteries_bill
# then --check on each (exit 0), the role move below, re-init the controls and
# replay databases, switch ~/.local/bin/morpholog to 0.0.14 (keep 0.0.13 as
# morpholog-0.0.13), DATABASE_URL=postgres:///grid_mysteries_morpholog scripts/check-record,
# scripts/check.
```

## Each deployment's own roles (v0.0.14), rehearsed 2026-10-08

Before v0.0.14 every deployment on the cluster was provisioned on the one
pair `morpholog_writer` / `morpholog_reader`, so a login granted either
held it in every Morpholog database on the machine. Migration 023 records
that pair on each of the three records, and `migrate` warns as long as
the pair also holds privileges elsewhere. `bizgov` moved to `bedrock_`
roles on 08/10. The three records here moved the same way the same day,
each to its own prefix, as a separate step after the migration (`init
--least-privilege` refuses a database behind the binary):

| Database | Prefix | Logins to move |
|---|---|---|
| `grid_mysteries_morpholog` | `gm_research_` | `gm_human` (was a member of `morpholog_writer`), `gm_machine` (was a member of `morpholog_reader`, plus its direct per-table write grants of the 25/09 amendment, which the move leaves alone) |
| `grid_mysteries_tec` | `gm_tec_` | none: the engine runs as the owner |
| `grid_mysteries_bill` | `gm_bill_` | none |

Rehearsed on a restored copy of the research record on the throwaway
cluster, after the migration, with the install guide's sequence (`docs/
install.md`, "Moving a deployment to its own roles"):

```sql
-- as the owner, in the database
REVOKE ALL ON ALL TABLES IN SCHEMA morpholog, morpholog_read FROM morpholog_writer, morpholog_reader;
REVOKE ALL ON SCHEMA morpholog, morpholog_read FROM morpholog_writer, morpholog_reader;
DELETE FROM morpholog.deployment_roles;
```

```bash
morpholog-0.0.14 init --skip-if-exists --least-privilege --role-prefix gm_research_ \
  --database-url postgres:///grid_mysteries_morpholog
```

```sql
-- cluster-wide, for the research record only
GRANT gm_research_writer TO gm_human;    REVOKE morpholog_writer FROM gm_human;
GRANT gm_research_reader TO gm_machine;  REVOKE morpholog_reader FROM gm_machine;
```

Result on the copy: `deployment_roles` records `gm_research_writer` /
`gm_research_reader`; the cluster pair holds nothing on any relation of
the database; `gm_machine` keeps its direct INSERT/UPDATE/DELETE on the
five tables and three views of the 25/09 amendment; `migrate --check` no
longer warns; `audit verify` passes and the claims are identical; both
logins propose through the adapter and the actor binding still refuses
the machine asserting the human. The same `REVOKE` / `DELETE` / `init`
with `gm_tec_` and `gm_bill_` moves the engines' records; they have no
login to move. Re-creating nothing: the logins keep their OIDs, so
`role_rebindings` stays empty for the reason the 25/09 amendment gives,
not a new one.

**Done live on 08/10/2026**, right after the migration, exactly as
rehearsed: the three databases record `gm_research_writer` /
`gm_research_reader`, `gm_tec_writer` / `gm_tec_reader` and
`gm_bill_writer` / `gm_bill_reader`; `morpholog_writer` and
`morpholog_reader` hold nothing on any relation of the three and
`migrate --check` no longer warns on any of them; `gm_human` is a member
of `gm_research_writer` only and `gm_machine` of `gm_research_reader`
only, with `gm_machine`'s 17 direct grants of the 25/09 amendment intact;
both logins connect and read the 242 claims; `audit verify` passes after
the move. The cluster pair stays on the cluster for the Morpholog
development databases that still use it; nothing of this repository
grants it any more (`scripts/replay-research` creates its logins on a
fresh cluster and grants them nothing of the pair).
