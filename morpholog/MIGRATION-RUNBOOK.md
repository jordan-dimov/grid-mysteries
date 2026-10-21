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
| `grid_mysteries_replay` | disposable, rebuilt by `scripts/replay-research` on CI's container or a throwaway cluster; dropped from the laptop cluster 08/10/2026, where the script cannot run | `init --reset` each run |
| `grid_mysteries_controls` | disposable, rebuilt by `scripts/check-controls` | `init --reset` each run |
| `gm_rehearsal` | disposable, dropped and recreated by `scripts/rehearse-v2` | recreated each run; **never name a migration rehearsal copy this** |
| CI service containers | fresh `postgres:18` per job (16 until 08/10/2026; the laptop cluster is 18) | always at the pinned binary's schema |

`scripts/replay-research` provisions the `gm_human` and `gm_machine`
login roles the record names, cluster-wide, and never drops them; it
refuses to run where they already exist. Run it in CI or on a throwaway
cluster, never beside the live record. `scripts/rehearse-v2` creates and
drops its own pair, `gm_rehearsal_writer` / `gm_rehearsal_reader`, with
its database (from v0.0.14 `init --least-privilege` refuses a pair that
exists on the cluster and is not this database's).

## The environment

Every command below runs with the pinned binary on `PATH` (or named by
`MORPHOLOG_BIN`) and the project environment synced with every group:

```bash
uv sync --all-groups
```

`uv sync` alone drops the `capture` group, and the pre-commit gate then
fails on a proofs test (`ModuleNotFoundError: opentimestamps`) that does
not name the cause; CI syncs `--dev --group capture` for the same reason.

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
#    claims and pack must be byte-identical to the baseline (across a release
#    that changes their shape, as v0.0.15 did, compare what it did not change:
#    claims without `asserted_in`, packs below the manifest line):
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
client refuses a binary of another version than it was generated for (the
engines pass `expected_version` to `Morpholog(...)`, so they are held to it
too). So the pin in `scripts/install-morpholog`, the vendored client, the
binary the repository runs and the three live schemas change in one move:
prepare the repo (pin, client, docs) and rehearse on copies; then, when
Jordan says, migrate and provision each live record.

**Which binary runs.** From 12/10/2026 every caller in the repository
honours `MORPHOLOG_BIN` as the generated client does: the shell scripts
through a `morpholog` function, the Python call sites through
`os.environ.get("MORPHOLOG_BIN", "morpholog")`. Unset, the `morpholog` on
`PATH` runs (the scripts put `~/.local/bin` first). So a new release is
installed beside the old one as `~/.local/bin/morpholog-<new>`, and
`export MORPHOLOG_BIN=~/.local/bin/morpholog-<new>` runs the whole
repository on it (`scripts/check`, `replay-research`, `rehearse-v2`, the
engines) without touching `PATH`. Switching `~/.local/bin/morpholog` is the
last step, once the branch carrying the new pin and client is on main.
Keep the old binary as `morpholog-<old>`: it is the only verifier of the
packs it wrote.

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
  the claim it guards"). `scripts/check-programmes` ran `check`, not
  `--strict`, so nothing failed; respelling the rule moves the pinned v3
  hash of a deployed programme, so it waited for the sponsor's word. The
  other five programmes were strict-clean. **Respelled the same afternoon
  on that word** (`RESEARCH-V3-DESIGN.md`): the pin moved to
  `sha256:ef203533…`, the record replays under it (fresh cluster, 242
  claims identical), the live provisioning is unchanged, every programme
  is strict-clean and `check-programmes` checks strictly from here on.

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
- `grid_mysteries_controls` re-initialised at schema 23 (`grid_mysteries_replay`
  too, then dropped from the laptop later that day: nothing can use it there); `~/.local/bin/morpholog` switched to 0.0.14 (0.0.13 kept as
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

The move is the one step of the upgrade no verb owns: three SQL statements,
an `init`, and a GRANT/REVOKE pair per login, from the install guide.
Morpholog #512 (filed 08/10/2026 on this feedback) proposes `roles move
--role-prefix` to own it and to be named by the `migrate` warning; until
it ships, the sequence above is the procedure.

## v0.0.14 to v0.0.15 (schema 23 to 25), rehearsed and run 2026-10-12

Migrations 024 (`gate_witness`: a gate refusal carries a witness too) and
025 (`rejection_compared`: the rejection log keeps the comparison a
refusal failed, with both values). Release v0.0.15 was published
2026-10-12 14:04 UTC; the three published `.sha256` files, the release
API's asset digests and the downloaded tarballs agree, and
`scripts/install-morpholog` pins them. The x86_64 binary (`bcfb7d44…`) is
installed beside the old one as `~/.local/bin/morpholog-0.0.15`;
`~/.local/bin/morpholog` is still 0.0.14 and every command below names
the binary through `MORPHOLOG_BIN` (above). Baselines with 0.0.14 and
`pg_dump -Fc` of each record are in `~/backups/morpholog-20261012T141945Z/`,
with every rehearsal and live report beside them.

**Programmes.** `check --strict` on 0.0.15 newly failed one programme:
the identity register named a field of `LinkProposed`, and the parameter
of `propose_link`, `class`, which the new client-name hint (#532) refuses.
Renamed `link_class`; its pin moved `312e6e56…` → `bd4da45a…`
(`identity/RENAME-2026-10-12.md`; nothing is deployed). The other six are
strict-clean and hash as pinned. `check --json` now gives every invariant
`cases`; all of them, in all seven programmes, are `bound`, and
`scripts/check-programmes` holds the engines to that as well as to the
compiled route. Routes moved the other way: v2's three and v3's five
`*_in_vocabulary` rules (a definition whose body is an `or` chain) were
interpreted on 0.0.14 and compile on 0.0.15 (#544), so every invariant of
the research programmes is compiled.

**Rehearsal** on template copies of the three records (`createdb -T`,
nothing connected): `migrate` 0.01 to 0.02 s each, 024 and 025 applied;
`audit verify` passes (TEC in 13 s, 301 MB, with progress on stderr);
claims identical to the baselines once `asserted_in` is set aside (new on
every claim read, #551: the transition that made the claim present; every
claim has one); the exported packs' checkpoints and rows byte-identical to
the 0.0.14 exports, only the manifest line changing (format 17 and a
`morpholog_version` key). `provision indexes --check` on the research
copy wanted one index, `WatchReading[3]` (v3's `reading_outcome_known`,
now compiled); TEC and Bill all KEEP. `migrate` on each copy warned that
its roles also hold privileges in the source database: an artefact of
`createdb -T` copying the grants, gone once the copies were dropped.

**Decisions**, on a throwaway cluster (initdb, port 55438), before the live
run: `check-controls` v2 (35 commits, 13 refusals) and v3 (16, 14), every
refusing rule as expected; `replay-research` (235 rows commit, 242 claims
identical, the replayed log self-verifies, provisioned and current);
`check-record` on the replayed record (20 watches open, none overdue);
`rehearse-v2` twice (60 assertions each; it needs `REHEARSE_ADMIN_URL` as
well as `REHEARSE_HOST` on such a cluster, or it sets up on the laptop
cluster and proposes to the other). **No decision changed under semantics
version 3.** Every v3 control refusal now carries a `witness`; the one that
fails a comparison (`clocks_ordered`) carries `compared`
(`on_or_before`, 2026-09-01 against 2026-08-01).

**Live**, 14:27 to 14:28 UTC, nothing connected to any of the three: a
fresh `pg_dump -Fc` of each (`*.live.pre-migration.dump`), `migrate` 23 to
25, `migrate --check` current, `audit verify` passes (235, 137,384 and 84
transitions; 242, 127,456 and 85 claims), claims identical apart from
`asserted_in`, each live pack byte-identical to its rehearsal export,
`provision indexes --prune` in one call per record (research: the one
CREATE above; TEC and Bill all KEEP) and `--check` exits 0 on all three.
Afterwards `migrate` warns on none of them; both research logins read the
242 claims through 0.0.15; `check-controls` re-initialised
`grid_mysteries_controls` at 25; `check-record` against the live record is
clean; `scripts/check` passes with `MORPHOLOG_BIN` set.

**Evidence.** A verifier reads one format, its own (#517).
- The committed `evidence-pack.ndjson` (format 4, tree size 235) is
  `unsupported_pack` to 0.0.15. It was re-exported from the live record
  (format 17; same tree size, checkpoints and rows), and
  `receipts/metric-retention.json` re-issued from it: same checkpoint,
  same answer (`inq-002`: 0.2363…), `semantics_version` 3 where it was 1.
  The 0.0.14 receipt verifies its evidence on 0.0.15 but reports
  `not_re_evaluated` and does not pass, as the release notes say. The
  format-4 pack and the semantics-1 receipt stay in git at `b1ed9dd`;
  0.0.12 to 0.0.14 verify that pack, and 0.0.14 refuses the new one
  (`malformed_pack`, by name).
- `claims-export.json` is refreshed from the live record and now carries
  `asserted_in`; `replay-research` compares claims by predicate and
  arguments, so a replay's own transition ids do not enter the comparison.
- The engines keep one pack per tree size. `record.exported_pack` now
  moves a kept pack that the binary reports `unsupported_pack` aside as
  `tree-<n>.format-<f>.ndjson`, never overwriting it, and exports again.
  TEC's `tree-137384.ndjson` (format 4) is now `tree-137384.format-4.ndjson`
  beside a format-17 export that verifies against the same anchor;
  `record.pack_rows` streams every format (it reads the two counts it needs,
  not the client's `PrefixPackManifest`, which requires the format-17 key).
  The Bill engine verifies its record and keeps its format-4
  `tree-84.ndjson` until its next `checkpoint` asks for a pack.

**Changed shape, not meaning.** The client is stamped 0.0.15 (Python 3.12
floor; the project is on 3.14) and is strict: `EnvelopeError` and
`CodecError` where malformed output passed through before. The engines'
refusal message (`record.refusal_detail`) now names the comparison and the
witness the refusal carries, with no re-derivation of a rule's numbers.

## v0.0.15 to v0.0.16 (schema 25, unchanged), run 2026-10-21

No migration: the schema is still 25 and `migrate --check` reports each
of the three records current with nothing pending. Release v0.0.16 was
published 2026-10-21 14:15 UTC; the three published `.sha256` files and
the release API's asset digests agree, the x86_64 tarball (`3de51232…`)
extracts to the binary installed as `~/.local/bin/morpholog` and
`morpholog-0.0.16` (`1ab8ec4f…`), and `scripts/install-morpholog` pins
all three. `morpholog-0.0.15` stays beside it. Nothing was backed up or
restored: no command below writes to a record.

**Programmes.** A literal is now a parsed value and the canonical
encoding is 2 (#600), so a programme whose literals were not in their one
spelling gets a new hash. None of ours was: all six pinned programmes and
the kill-test programme are strict-clean on 0.0.16 and hash exactly as
pinned (`7ac617b4…`, `c9e4b937…`, `ef203533…`, `82603622…`, `a527463c…`,
`bd4da45a…`). No programme spells `P1Y`, `PT90M`, an offset instant or
`0 - x`, so the formatter rewrites nothing. `check --json` still reports
every invariant compiled and bound; `scripts/check-programmes` passes
unchanged. The `*_HASH.json` pins keep the `morpholog_version` they were
last recomputed under, as before: the field records the binary that
produced the hash, and a hash that did not move was not recomputed.

**The database checks the release adds** (#575), run against the live
records, read-only:
- `check --database-url` on each record: no stored claim misfits its
  declaration. On the research record alone, each programme sees the
  others' predicates as undeclared (hints); naming the two siblings with
  `--against` clears every hint for v3, and leaves one for v1 and v2:
  `AuditSigningKey` is written by `register_audit_signing_key` in both,
  each behind its own gate. That is the coexistence the v2 design chose
  (one database, disjoint vocabularies, one reserved signing predicate),
  not a finding. TEC and Bill are strict-clean against their databases.
- `provision indexes --check`, one call per record: research 106 KEEP
  (v1+v2+v3), TEC 52 KEEP, Bill 81 KEEP; every line now ends in the rule
  that needs it (`needed_by`, #578). Nothing to create or prune.

**Client.** Regenerated with 0.0.16 (`--check` reported all six files
stale under 0.0.15, as the release notes say it would, whether or not the
hash moved). `models.py` is unchanged in substance (the syntax tree is
identical; only line-wrapping moved), so no parameter contract changed
(#595, #597). What is new: `values.Quantity(amount, unit)` where a tagged
quantity was a bare `Decimal` (#564), and `MorphologWitnessFailed` /
`MorphologNotCovered` (#592, #589). Neither reaches our code: no
programme declares a tagged quantity, and every checkpoint is taken
through the binary (`record.checkpoint_and_export`, `scripts/record`),
whose exit status already carried a failed witness. No resident session
was running; the engines open a client per command.

**Evidence.** The pack format is still 17 and a 0.0.16 export of the
research record differs from the committed pack only in the manifest's
`morpholog_version`; `scripts/verify-research-pack` verifies the committed
pack and reproduces the receipt on 0.0.16, so nothing is re-exported. The
TEC and Bill records `audit verify` on 0.0.16 (137,384 and 84
transitions; the TEC anchor's DigiCert witness verified).

**Checks.** `scripts/check` is green on 0.0.16 (739 tests, ruff, mypy,
rule maps, 80 proofs, programmes, client current). `check-record` against
the live record is clean on drift (309 rows, 309 transitions), provenance
(14 metrics) and sealed digests (42), and fails only on the watch
`w-007-t3-september`, due 2026-10-15 with no reading, which predates the
upgrade and is unrelated to it.

**Derived views.** Not used by this project, so the view regeneration
and `refresh derived` steps did not apply; they would only have, had a
hash moved.

**Adopted the same day**, on the sponsor's decisions over the survey of
the release (the rest were declined or held: `periods` cannot yet express
a completeness rule over date-keyed rows, Morpholog #606; a named
definition call and unary minus have no site here; the rehearsal's
`explain` stays a shell-out):
- every claim pattern with three or more wildcards is spelled by the
  fields it reads, `Pred(field: x, ..)`, across the six programmes; the IR
  is positional, so no hash moved;
- `check --database-url` is a deploy gate: `scripts/check-record` runs it
  for each research programme with the two siblings `--against`, and
  `record.provisioned()` asks the client's `check(with_database=True)`
  before every engine import, refusing an error and reading a hint;
- a checkpoint after an import covers the import: the engines read the
  close transition from the record (`record.last_close`, the `Imported`
  claim's `asserted_in`) and ask `audit checkpoint --covering` for it;
  `scripts/record` covers the row it just committed. The one refusal that
  records nothing (`transition_not_covered`) is retried after 1, 2, 4, 8
  and 16 seconds, then handed back.

**Rehearsing a later programme.** `evaluate()` on the generated client
(or `morpholog evaluate <draft> --pack morpholog/evidence-pack.ndjson
--anchor-file morpholog/audit-anchor.json`) scores a candidate programme
against the committed history offline, naming per invariant the admitted
transitions it would have refused. That is how a v4 draft is rehearsed
against the record before it is deployed, as v2 was scored against v1 in
August 2026 (`research-v2-evaluate.json`): nothing is deployed, nothing is
written, and a programme the binary cannot score is "not evaluated",
which is not "refused".
