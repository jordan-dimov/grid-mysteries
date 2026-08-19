# Research programme v2: the governed research state machine

Status: **drafted, control-tested, not yet deployed.**
`research-v2-draft.morph` is check-clean under the pinned release
(fingerprint in `V2_DRAFT_HASH.json`) and its gates are exercised by
negative tests (`controls/`, run by `scripts/check-controls` in CI
against a disposable database: 35 lifecycle transitions must commit,
13 violations must be refused by their exact named rules, and the derived
retention ratio is read back from the kernel). The deployed
programme remains `research.morph` (v1) until Investigation 002 opens.

## What v2 makes executable

1. **Sealing authorises acquisition.** `seal_protocol` — gated by
   `SealAuthority(actor)` — is the only emitter of
   `DataAcquisitionAuthorised`. The fetcher consumes that intent through
   Morpholog's outbox lease protocol (`outbox claim` →` fetch` → propose
   the evidence manifest → `outbox complete`); delivery is at-least-once,
   so the manifest-registering transformation is idempotent by gate.
   Ordering is proven by audit-log sequence, never caller timestamps.
2. **Human/machine separation is kernel-enforced, twice over.**
   Authority claims (`SealAuthority`, `PublicationAuthority`, admitted
   only for the human actor by the one-transition `establish_governance`
   bootstrap) gate *what an actor may do*; the reserved
   `ActorAssertionRestricted`/`ActorAssertionAuthority` claims bind *who
   may assert an actor* to an exact PostgreSQL `session_user`. The
   machine's connection must never hold the human's credential — the
   adapter enforces policy, it does not prove authorship. Actor names are
   underscore-form (`jordan_dimov`, `claude_fable_5`): `#` literals
   cannot contain hyphens.
3. **Quantitative claims are governed values with enforced provenance.**
   `EvidenceMetric(metric, inquiry, artifact, metric_name, metric_value)`
   binds each number (bare `Decimal`, unit in the name) to an artefact
   that must be attached to the same inquiry, after evidence seal;
   `ConclusionUsesMetric` may only link a metric of the conclusion's own
   inquiry; `draft_publication` refuses a conclusion with no bound
   metrics; CI recomputes metrics from artefacts and refuses drift. The
   renderer reads governed values — prose never carries a number
   authoritatively.
4. **Standing is a pointer, not an edit.** Native three-predicate
   supersession: append-only `Conclusion` (content), retractable
   `CurrentConclusion` (`current pointer by (inquiry) superseded via
   SupersedesConclusion`), and the lineage with a generated no-fork
   invariant plus `unique by (successor_conclusion)`. "Current" is the
   pointer claim, read positively; history answers "what did we conclude
   on date X" via the audit log.
5. **In-sample work is unpromotable.** Prior exposure is enforced at
   corpus assignment (`prospective_corpus_unexposed`, see item 9), a
   prospective conclusion requires an assigned corpus, and an
   `#explained` conclusion requires an `#explained` mechanism assessment.
6. **Publication is governed, and approval binds a digest.** The order
   is: render the draft → compute its content digest →
   `draft_publication` registers exactly that digest → the human's
   `approve_publication` approves *that digest* → `PublicationAuthorised`
   releases the already-rendered artefact for distribution. Rendering
   after approval is forbidden by design: the human must approve the
   bytes that get published, not a promise of them.
7. **Every gate is named**, so control tests and refusal receipts pin the
   exact rule (`rule` field), never prose.
8. **Pre-registered parameters are governed values.** A parameter that
   can change which evidence is selected or what conclusion is reached
   has one executable authoritative value: `DeclaredParameter` (Decimal
   only — deliberately not a configuration language), declarable only
   between `declare_protocol` and `seal_protocol`, immutable after, one
   value per (inquiry, name). Analysis code reads the governed value;
   prose merely displays it.
9. **Corpora are first-class and prior exposure is overlap-based.** The
   registry (`ResearchCorpus`/`InquiryCorpus`/`CorpusConsumed`) models
   identity, allocation and consumption separately; the gate refusing a
   prospective inquiry an exposed corpus fires **at assignment** (time is
   modelled by audit sequence, so an inquiry lawfully consuming its own
   corpus later cannot retro-invalidate anything), and it refuses date
   OVERLAP with any consumed window, not just id equality. Corpus bounds
   are Decimal YYYYMMDD day-keys: v0.0.9 accepts Date-vs-Date comparisons
   at check time but refuses them at proposal time (worth reporting
   upstream). Deployment seeds July 2026 and 2026-08-04..10 as
   *historical* consumption facts via `record_historical_consumption`
   (human-gated; the consumer is a v1 subject, exempt from the v2
   assignment invariant) — legitimate backfill of facts that occurred,
   never of lifecycle acts that did not.
10. **The kernel derives the public ratios.** Every published
    quantitative claim lives in governed state; *algebraically trivial*
    publication arithmetic (ratios over declared numerator/denominator
    pairs via `RetentionSpec` → derived `MetricRetention`) is computed by
    the kernel from provenance-gated `EvidenceMetric` claims
    (unique per (inquiry, metric_name); artifact must be attached to the
    same inquiry; evidence sealed). Percentiles, correlations, interval
    integration and bounds stay in Python: those are analytical methods,
    and the kernel is not a numerical programming language.
11. **`#hypothesis_not_evaluable` is a lawful outcome.** A system
    governing falsifiable research needs a state for "the experiment did
    not yield evidence capable of deciding the hypothesis" (e.g. an
    empty panel under a declared coverage gate); without it the ontology
    pressures toward false certainty.

## Deployment model: one database, one audit chain

v1 and v2 share the database and the Merkle-chained audit log — one
public evidence pack spans both histories. The load-bearing rule:
**vocabularies are fully disjoint** (v2's Inquiry/EvidenceArtifact/
Conjecture/Conclusion vs v1's Investigation/SourceArtifact/Hypothesis/
Finding), because a shared predicate name would be shared rows ungoverned
by the other programme's rules. No programme identity exists in the
database; `PROGRAMME_HASH.json` and `V2_DRAFT_HASH.json` are the
out-of-band record. v1 is frozen at deployment (no new v1 proposals
except audit-key rotation); v2 references v1 subjects by UUID via
`LineageFromV1` — deliberately claims about prior subjects, not imports.

## Causal intents: at irreversible boundaries only

Outbox-driven authorisation is reserved for the two epistemically
irreversible acts: **data acquisition** (looking at unseen data) and
**external publication** (releasing an approved digest). Pure
deterministic analysis that refuses to run without `AnalysisAuthorised`
in the record is already strongly governed; re-running arithmetic has no
epistemic side effect, so it does not need to become an outbox job.

`evaluate`-discovered regularities are **control hypotheses**, not
discovered controls: a historical regularity ("every conclusion happened
to cite ≥2 sources") is not yet doctrine. The loop is: evaluate finds a
regularity → it becomes a candidate rule → Hypothesis attacks it → the
human decides whether it is normatively intended → only then is it
promoted into the programme. This mechanism stays experimental until the
research history is larger.

## Audit signing

Checkpoints are signed (Ed25519, key `audit-2026`; private key outside
the repo, public key authorised by the governed `AuditSigningKey` claim
and embedded in each checkpoint). Verification is fully offline from a
prefix pack. Checkpoints before tree_size 34 predate the key and are
unsigned — recorded honestly; `scripts/replay-research` requires the
*current* anchor to be signed.

## Adoption plan

1. Investigation 002 (earliest legitimate start ~2026-08-21) opens under
   v2: `establish_governance` first (human PG role's credential withheld
   from the machine), then open → declare corpus `#untouched` → declare
   protocol → **human seals** → outbox-authorised fetch → evidence seal →
   selection → assessments → conclusion with bound metrics → drafted
   publication → **human approves**.
2. The 002 pipeline adopts `generate python-client` (same CLI path, typed
   models, `--check` drift gate) instead of hand-rolled shelling, and
   `scripts/record` (recoverable, fail-loud) remains the only way the
   repo-side record artefacts are updated.
3. Kind-specific lifecycle refinements wait for real usage.

## Launch readiness (2026-08-19)

`scripts/rehearse-v2` (CI, disposable database, two real PostgreSQL
login roles) proves the whole lifecycle with the actual adapter
session_user enforcement. Three facts it established are now doctrine:

1. **The bootstrap race is real**: on an ungoverned database any
   connection can run `establish_governance` and define the trust root.
   The kernel cannot prevent this — ordering does. The launch runbook
   (`V2-LAUNCH-RUNBOOK.md`) therefore puts the human bootstrap before
   the machine role can propose, and the machine's first act is to
   verify it cannot assert `jordan_dimov`.
2. **Verification trust is the repo-pinned public key**
   (`trust/audit-2026.pub`, asserted by `scripts/replay-research`),
   never the `AuditSigningKey` claim set: v1's key registration is
   ungated and the v1 file remains on disk for replay, so the claim set
   is mintable by the machine credential; the pinned key is not.
3. **Mixed v1+v2 history replays** by filename convention: batches named
   `*.v2.ndjson` are proposed against the v2 programme by both
   `scripts/record` and `scripts/replay-research`.

The 002 launch rows themselves (governance, corpora registry, the three
genuinely consumed historical windows, open/assign/declare, human seal)
are dry-run verified in order — templates in `launch-002/`. June 2026
and 2026-08-11..17 are deliberately never seeded as consumed.

### The boundary the rehearsal does NOT cross (2026-08-19 correction)

`scripts/rehearse-v2` section H forces the honest negative result:
governed-path enforcement holds only while every mutation goes through
the adapter. The `morpholog.claims` table is plain substrate storage (no
RLS/trigger/`SECURITY DEFINER`), and any role that can propose must hold
raw `INSERT` on it — the rehearsal shows a role *without* `INSERT` cannot
propose at all. So for a single connecting role, **propose-capability is
raw-forge-capability**: a process with the machine credential can
`INSERT SealAuthority(claude_fable_5)` directly and then seal through the
normal adapter, emitting `DataAcquisitionAuthorised` with no human. Replay
detects it (divergent log, forged claim `only_in_claims_table`) but only
post-hoc — too late for the irreversible acquisition boundary.

Three layers, kept distinct:

- **A. Governed-path actor enforcement** — proven. Human/machine split
  holds for every adapter proposal.
- **B. Raw-database capability security** — *not* provided while the
  machine role has substrate DML. The only real fix is a separate
  trusted gateway process holding the writer role (e.g. a resident
  `morpholog session`), with the machine holding no direct DB write and
  submitting only rule-checked proposals; actor policy then binds
  `claude_fable_5` to the gateway role and never to `jordan_dimov`. This
  is a genuine capability boundary and larger than a launch-day change.
- **C. Acquisition capability security** — not provided by Morpholog at
  all: it governs claims, not the machine's network senses. A shell with
  internet can fetch unseen data regardless of any seal; enforcing "no
  unseen data before seal" needs process network isolation.

Launch posture is therefore **cooperative-machine**: A is enforced and
auditable; the untouched-data discipline is a declared human/process
guarantee, not an OS/network sandbox. See `V2-LAUNCH-RUNBOOK.md`.

## The boundary, stated durably

> **Morpholog owns what may be said, what may be done, and what declared
> facts a public statement rests on. Python owns measuring the world.**
