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

## Addendum, 25/09/2026: the launch as run

- One more machine step, **M3** (`M3-watches-2026-09.v3.ndjson.template`):
  ten `open_watch` rows for the dated obligations the September work left
  in documents and nowhere else, each with its resolving observation and
  holder taken from the document that states it. `w-005-eir-response`
  (due 2026-10-13, `EIR-REQUEST-TEC-2025-26.md`); `w-007-t3-september`
  (NESO's full-month September file, "expected early October",
  `DECLARATION-T3-SEPTEMBER.md`; read date 2026-10-15 chosen here);
  `w-018-sf-post-days` (C5 of 018's declaration; read date 2026-10-03
  chosen here); three F006 watches and four F007 watches from the
  "Watches (dated)" tables of their RESULTS files (a month-only date is
  the last day of that month). `w-005-tec-hole` stays as drafted in
  August (due 2027-02-26): `RESULTS.md` of 005 says the watch "moves to"
  2026-10-13, and a watch is append-only, so the interim obligation is a
  second watch rather than an edit.
- `scripts/launch-forward <step-file>` runs a step through
  `scripts/record` row by row and stops at the first row that does not
  commit; `{SEALED_AT}` is filled with the wall-clock time of proposing.
- The three 005 verdicts (`v-005-q1/q2/q3`) cite `evidence_digest`
  `a25ea2ae…`, the SHA-256 of `005/RESULTS.md` at commit `0d8a470`
  (26/08/2026). The file has since grown (the EIR request of 15/09), so
  that digest matches no file on disk today; it is recoverable from git
  (`git show 0d8a470:investigations/005-connection-date-credibility/RESULTS.md`).
  A verdict names the evidence it was given, not the file's later state.
- Every `declared_at` and `recorded_at` is still the August commit time;
  every `sealed_at` is the time Jordan sealed on 25/09/2026. The record
  shows, truthfully, git as the seal until then and Morpholog from then on.
- Rehearsed first on a restored copy of the live record on a throwaway
  cluster, through the real login roles (see `V2-LAUNCH-RUNBOOK.md`,
  25/09 amendment): all 94 rows commit, `check-record` lists 20 watches
  with none overdue and verifies the 9 sealed digests against disk.

