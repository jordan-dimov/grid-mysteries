# V2 launch runbook — Investigation 002

Two sessions touch the research database on launch day: **Jordan's own
shell** (the human credential, never shown to Claude) and **the Claude
Code session** (the machine credential only). Every step below was
rehearsed end-to-end on a disposable database with two real PostgreSQL
login roles (`scripts/rehearse-v2`, run in CI) and the exact H1/M1/H2
rows were dry-run in order (templates in `morpholog/launch-002/`).

**Ordering is load-bearing.** The rehearsal demonstrates that on an
ungoverned database *any* connection can run `establish_governance` and
define the trust root — the kernel cannot know who is human until the
bootstrap says so. Therefore: **H3 happens before the machine role can
propose anything.** Do not reorder.

Credential rules, absolute:
- Jordan's human password is typed only at interactive `psql`/`\password`
  prompts in Jordan's own shell. Never pasted into Claude Code, never in
  a command argument, `.env`, repo file, or shell history.
- The machine credential may be held by the Claude session (env var or
  `~/.pgpass`), and grants no seal or approval power *through the governed
  path* — but see the three-layer threat model at the end: with raw table
  DML it can bypass that path, so the launch posture is cooperative-machine,
  not adversarial capability security. Read that section before relying on
  any "the machine cannot X" statement.

---

## Human-only steps (Jordan's shell, outside Claude Code)

**H1 — provision the least-privilege floor and create the login roles,
granting propose-capability ONLY to the human for now** (as the
PostgreSQL admin). This closes the bootstrap race (threat-model layer A):
until governance is established, *any* propose-capable connection can
define the trust root, so the machine gets writer membership only after
H3. Section H of `scripts/rehearse-v2` proves a role that cannot write
`claims` cannot propose at all — so a reader-only `gm_machine` genuinely
cannot race the bootstrap.

First retrofit the **least-privilege floor** onto the existing database
(`morpholog init --least-privilege` is idempotent and, with
`--skip-if-exists`, safe on a database that already holds v1's history —
it never drops or migrates):

```
morpholog init --database-url postgres:///grid_mysteries_morpholog \
  --least-privilege --skip-if-exists
```

That revokes PUBLIC from the governed tables, creates the
`morpholog_writer` / `morpholog_reader` group roles, and makes the audit
log **append-only even for the writer**. Then create the two logins,
granting writer membership only to the human for now:

```
psql -d grid_mysteries_morpholog
  CREATE ROLE gm_human LOGIN;
  \password gm_human          -- typed at the prompt, nowhere else
  CREATE ROLE gm_machine LOGIN;
  \password gm_machine        -- machine credential; given to Claude AFTER H3
  -- Writer membership is what confers propose-capability.
  GRANT morpholog_writer TO gm_human;
  GRANT morpholog_reader TO gm_machine;   -- read only until H3 completes
  \q
```

*(PostgreSQL role administration. If `pg_hba.conf` does not already
allow password logins on localhost, add a `host … scram-sha-256` line
and reload.)*

**H2 — connect as the human role** (password at the prompt):

```
psql "postgres://gm_human@localhost/grid_mysteries_morpholog"
```

Verify: `select session_user;` → `gm_human`. Disconnect.

**H3 — Morpholog governance bootstrap** (the one-time trust root; this
is a Morpholog act, not a PostgreSQL one). From the repo root, in
Jordan's shell, with the human URL (password prompted by libpq if not
in Jordan's own `~/.pgpass`):

```
export DATABASE_URL="postgres://gm_human@localhost/grid_mysteries_morpholog"
while IFS= read -r row; do
  scripts/record 090-inv-002-launch.v2.ndjson "$row"
done < morpholog/launch-002/H1-bootstrap.v2.ndjson.template
```

This establishes governance (`jordan_dimov`→`gm_human`,
`claude_fable_5`→`gm_machine`), registers the four corpora, and
backfills the three genuinely consumed historical windows (May 2026 →
inv-003; July 2026 → bess-001; 2026-08-04..10 → inv-001 and the four
method studies). **June 2026 and 2026-08-11..17 are deliberately NOT
consumed** — June is Investigation 004's *frozen, unconsumed*
investigation window (004's declaration records partial June exposure:
BESS schema probes, July boundary slices, and June rows present in 003's
pinned FY26-27 CSVs — so it is 004's reserved window, not pristine
untouched data); the August week is 002's reserved window and is
consumed only at acquisition.

**H3a — grant the machine role its write privileges NOW** (governance
exists, so the race window is closed):

```
psql -d grid_mysteries_morpholog
  GRANT morpholog_writer TO gm_machine;
  \q
```

Note this membership is exactly the substrate-bypass capability of
threat-model layer B, and least-privilege does **not** remove it: the
writer role necessarily holds `INSERT` on `claims` and `audit`, so from
here a process with the machine credential *could* forge a claim (and
forge its audit row's attestation) by raw SQL. What least-privilege does
buy is real but narrower — PUBLIC is revoked, and the audit log is
append-only even for the writer, so a forger can **append** but can
neither erase nor rewrite its own tracks (`UPDATE`/`DELETE` on
`morpholog.audit` are refused; both are asserted in the rehearsal). The
launch posture accepts the rest under the cooperative-machine model.

The signing key `audit-2026` is already registered in the shared claims
table (v1 row); v2's `key_not_already_registered` correctly refuses a
re-registration — nothing to do.

**H4 — disconnect.** Unset `DATABASE_URL` in that shell. Commit the
`morpholog/` changes scripts/record produced (git add/commit/push can be
done from either session; the rows are already in the database).

Only now: give Claude the **machine** URL, e.g. by setting in the Claude
session `DATABASE_URL="postgres://gm_machine:<machine-password>@localhost/grid_mysteries_morpholog"`.

---

## Machine steps (Claude Code session, machine credential only)

**M1 — prove the boundary before doing anything else:**

1. `psql "$DATABASE_URL" -tAc "select session_user"` → must be `gm_machine`.
2. Attempt a proposal as `jordan_dimov` — it MUST fail with the adapter's
   "not authorised to propose as actor" error.
3. Inspect claims: exactly one `ActorAssertionAuthority(jordan_dimov, gm_human)`
   and one `ActorAssertionAuthority(claude_fable_5, gm_machine)`.

If any check fails, STOP and report; do not proceed.

**M2 — open 002** (only on/after 2026-08-21, and only after the 002
declaration document is committed): fill
`morpholog/launch-002/M1-open-and-declare.v2.ndjson.template`
placeholders (title, timestamps, the sha256 of the committed declaration,
one `declare_parameter` row per declared Decimal parameter), then record
row-by-row via `scripts/record 090-inv-002-launch.v2.ndjson '<row>'`.

**H5 — Jordan seals** (human shell again, as in H3):

```
scripts/record 090-inv-002-launch.v2.ndjson \
  '{"transformation": "seal_protocol", "actor": "jordan_dimov", "args_named": {"inquiry": "inq-002", "sealed_at": "<UTC now>"}}'
```

The seal — and nothing else — emits `DataAcquisitionAuthorised(inq-002)`.

**M3 — machine consumes the authorisation and first touches the window:**

```
morpholog outbox claim --intent-type DataAcquisitionAuthorised --worker-id inv-002-fetcher
# the fetcher itself re-checks the seal and refuses without it:
uv run python investigations/002-hardened-selector/selection.py fetch
# register_evidence/attach_evidence rows via scripts/record
# (idempotent: a re-delivered registration is refused by artifact_is_new, never duplicated)
morpholog outbox complete <intent-id> --outcome delivered --worker-id inv-002-fetcher
# then: consume_corpus(corpus-2026-08-w2, inq-002)
uv run python investigations/002-hardened-selector/selection.py select
```

**Outbox at-least-once discipline** (verified guidance from Morpholog;
`scripts/rehearse-v2` exercises the happy path):
- **Idempotency is by gate, and the gate must be matched by name.** A
  re-delivered `register_evidence`/`attach_evidence` is refused by
  `artifact_is_new`/`attach_is_new` — treat *that specific rule* as
  success. Any other rejection is a real failure (`complete … --outcome
  failed`), and a *commit* on a retry means the first attempt did not
  land — never mark a state change `delivered` on a refusal you did not
  expect.
- **Every value written must derive from the intent payload**, never
  from per-attempt fresh state: a `new Subject()` / fresh id minted on
  each retry defeats the `is_new` gate and duplicates. The artifact id,
  sha256, etc. come from the fetch, keyed deterministically.
- **`lease_lost` from `complete` means another worker owns the row** —
  it is not retryable; stop and reconcile, do not re-fetch.

Analysis reads sealed parameters via
`grid_mysteries.governance.declared_parameter` (generated client, pinned
model hash) — never from constants in code or prose.

**H6 — later, publication approval** (recurring human act, once per
publication, human shell): after the machine renders the draft and
registers its digest via `draft_publication`, Jordan reviews those exact
bytes and records `approve_publication`. Approval binds that digest
only; changed bytes are a new unapproved draft.

---

## Programme freeze and batch convention

From launch, `research.morph` (v1) is **frozen by doctrine**: no new v1
proposals. v2 rows live in batches named `*.v2.ndjson` —
`scripts/record` and `scripts/replay-research` both dispatch the
programme by that suffix, so the mixed v1+v2 history replays.

## Threat model — stated precisely, in three layers

The rehearsal proves exactly one of these, and it is important not to
claim more. All three are evidenced by `scripts/rehearse-v2`.

### A. Governed-path actor enforcement — PROVEN

*Every mutation that goes through the Morpholog adapter obeys the
human/machine split.* After H3, a proposal carrying the machine
credential cannot assert `jordan_dimov` (adapter refusal at the session
layer), re-run `establish_governance` (`governance_not_yet_established`),
seal (`seal_requires_authority`), approve (`approval_requires_authority`),
backfill consumption (`historical_requires_seal_authority`), or register
a signing key (`key_registration_requires_seal_authority`). The
rogue-*key* path is closed at the verifier: v1's
`register_audit_signing_key` is ungated and the v1 file stays on disk
for replay, so the `AuditSigningKey` claim set is mintable — therefore
verification trust is the **repo-pinned** `trust/audit-2026.pub`
(asserted by `scripts/replay-research`), never the claim set.

### B. Raw-database capability security — NOT PROVIDED

*A process holding the machine credential can bypass the adapter
entirely.* The `morpholog.claims` table is plain storage — no RLS, no
trigger, no `SECURITY DEFINER` wrapper — and `gm_machine` holds raw
`INSERT` on it. Section H of the rehearsal forces the whole chain on a
disposable database: the machine `INSERT`s `SealAuthority(claude_fable_5)`
directly, then seals `inq-forged` through the *normal* adapter (the gate
now sees the forged claim), and `DataAcquisitionAuthorised` is emitted —
**with no human involved.** `audit verify` later reports the log as
divergent (the forged claim is `only_in_claims_table` with no
transition), but that is **post-hoc**: it runs when someone runs it, and
by then the seal has already authorised acquisition.

This is not fixable by narrowing `gm_machine`'s grants: the rehearsal
also shows a role *without* `INSERT` cannot propose at all (`permission
denied for table claims`). For a single connecting role,
**propose-capability and raw-forge-capability are the same privilege.**
The only true fix is a *separate trusted gateway process* holding the
writer role and exposing only rule-checked proposals (e.g. a long-lived
`morpholog session`), with the machine holding **no direct database
write** — a real capability boundary, and more than a launch-day change.
See RESEARCH-V2-DESIGN.md for the sketch.

**What `attestation.authenticated_by` is, precisely.** Every audit row
Morpholog writes through the runtime carries the PostgreSQL `session_user`
that committed it, inside the Merkle leaf. This is **trustworthy evidence
of the authenticated DB login for rows written through the governed path**
— but it is **NOT an unforgeable identity assertion against a credential
holding raw `morpholog.audit` DML.** The schema only checks that
`attestation` is a non-null JSON object; nothing binds `authenticated_by`
to the real `session_user` for an arbitrary SQL write. `scripts/rehearse-v2`
§H2 forces this: `gm_machine` raw-inserts an audit row reading
`{"authenticated_by":"gm_human"}` just as easily as it forges the claim.

So the standing `replay-research` check — every `establish_governance` /
`seal_protocol` / `approve_publication` row must attest the human login —
catches only **(1) misconfiguration** (a governance row committed by the
wrong login through the legit path) and **(2) a naive forger** who
doesn't also fake the attestation. It does **not** catch the modelled
layer-B attacker. Keep it (both cases are real), but do not claim it
restores adversarial detective security.

**What actually survives a raw-DB attacker (layer C, tamper evidence):**

- An **externally-retained signed checkpoint** proves its committed
  prefix was not rewritten. The signing key (`~/.config/.../audit-signing-2026.pem`)
  is **not held by the machine**, so the attacker cannot forge a valid
  signature over a tampered tree. `scripts/rehearse-v2` §H2 confirms the
  attacker's own re-checkpoint comes out **unsigned**, which
  `replay-research`'s pinned-key assertion refuses.
- **Claims-vs-audit replay divergence** exposes a forgery that leaves
  the claims table and the audit log inconsistent (the claims-only
  `SealAuthority` forgery shows as `only_in_claims_table`).
- **Not** protected: a *consistent* forgery appended **after the latest
  external anchor** (append is legal in an append-only log, so the prefix
  consistency proof passes). Only the next human-signed checkpoint — and
  a human choosing to notice — closes that window. This is inherent to
  the cooperative-machine posture, not a bug to fix before Friday.

### C. Acquisition capability security — NOT PROVIDED by Morpholog

Even with a perfect database boundary, Morpholog governs *claims*, not
the machine's senses. A process with shell and network access can
`curl` NESO/Elexon directly, before any seal. Nothing in the state
machine sandboxes that. Technical enforcement of "no unseen data before
the human seal" would require network/data-access isolation of the
machine process — out of scope here.

### The honest launch posture (Friday)

> **Operationally ready under a cooperative-machine threat model.** The
> human/machine authority split is enforced for every governed Morpholog
> proposal (A); replay/audit detects substrate bypass after the fact;
> and the untouched-data discipline (2026-08-11..17 not contacted before
> the seal) rests on a declared human/process guarantee — Claude is
> instructed not to bypass the governed tooling or touch the reserved
> window — **not** on an OS/network sandbox (B, C not provided).

If Jordan wants to raise this to adversarial capability security before
002, the gateway-process separation (B) and machine network isolation
(C) are the two required pieces; neither is needed for a cooperative
launch, and both are larger than a Friday change. A cheap partial
hardening available today: restrict `pg_hba.conf` so the machine role
cannot reach a superuser/peer-auth login (defence in depth; the governed
record's tamper-evidence does not depend on it).
