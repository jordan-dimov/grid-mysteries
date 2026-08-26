# Putting the forward and verifier tracks into the record — v3 launch rows

Generated 2026-08-26 from the files on disk; every `content_digest` and
`evidence_digest` is the SHA-256 of the named file at its last commit, and
every `declared_at` / `recorded_at` is that file's commit timestamp. Nothing
here is proposed yet: v3 is a draft until the sponsor runs H1.

Order, mirroring `launch-002/`:

| step | actor | file | what it does |
|---|---|---|---|
| H1 | human | `H1-bootstrap.v3.ndjson.template` | `establish_forward_governance(jordan_dimov)` — the seal authority, once |
| M1 | machine | `M1-declare.v3.ndjson.template` | nine `declare` rows: F001 declaration and stage test, Generator v3 and v4, Batch 01 and 02, the F004 kill, the K3 test for C18, Investigation 005 |
| H2 | human | `H2-seal.v3.ndjson.template` | nine `seal_declaration` rows — replace `{SEALED_AT}` with the wall-clock time of sealing |
| M2 | machine | `M2-record.v3.ndjson.template` | v4 supersedes v3; 51 verdicts (Batch 01 K1 ×10; Batch 02 gate ×8, K0 ×8, quarantines ×2, K1/K2 ×12, K3 ×1; F004 ×2; 005 Q1–Q3); 10 watches with due dates; the one reading already taken; F004's five reopening triggers; two F001 evidence-class claims |

**Credentials.** The record binds `jordan_dimov` to the PostgreSQL role
`gm_human` and `claude_fable_5` to `gm_machine` (v2 `establish_governance`).
H1 and H2 must be proposed from a shell whose `DATABASE_URL` connects as
`gm_human`; M1 and M2 from a session connecting as `gm_machine`. A default
local connection (session_user `jdimov`) is neither and every row would be
refused by actor policy — by design.

Each step goes through `scripts/record <batch-basename> '<row>'` row by row
(the batch files are `morpholog/batches/110-forward-launch.v3.ndjson` and
onward), which appends, re-exports and re-anchors after every committed
proposal. `scripts/check-record` then verifies every sealed digest against a
file on disk and refuses any overdue watch with no reading.

**What sealing after the fact means, said plainly.** These declarations were
frozen by git commit on the dates recorded, and their kills ran afterwards.
Sealing them now records the digests in the Merkle-chained audit log with a
`sealed_at` later than the work. The record will therefore show, truthfully,
that the forward track's seal was git until 2026-08-26 and Morpholog from
then on. That is the honest history; it is not a claim that the kernel
gated those kills.

Dry-run verified 2026-08-26 against a disposable database: H1, M1, H2 (with
a placeholder time) and M2 all commit under `research-v3-draft.morph`.
