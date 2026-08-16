# Research programme v2: the governed research state machine

Status: **drafted, control-tested, not yet deployed.**
`research-v2-draft.morph` is check-clean under the pinned release
(fingerprint in `V2_DRAFT_HASH.json`) and its gates are exercised by
negative tests (`controls/`, run by `scripts/check-controls` in CI
against a disposable database: 25 lifecycle transitions must commit,
8 violations must be refused by their exact named rules). The deployed
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
3. **Quantitative claims are governed values.**
   `EvidenceMetric(metric, evidence_digest, metric_name, metric_value)`
   binds each number to a content-addressed artefact (bare `Decimal`,
   unit encoded in the name — rates cross denominations, so quantity
   kinds are deliberately not used); `ConclusionUsesMetric` ties them to
   conclusions; `draft_publication` refuses a conclusion with no bound
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
5. **In-sample work is unpromotable.** `#method_study` inquiries with a
   `#consumed` corpus can never yield a `#prospective`-grade conclusion
   (`prospective_conclusion_needs_untouched_corpus`), and an
   `#explained` conclusion requires an `#explained` mechanism assessment.
6. **Publication is governed.** `draft_publication` (machine) requires a
   current, metric-bound conclusion; `approve_publication` (human
   authority) emits `PublicationAuthorised` — the renderer's only lawful
   trigger.
7. **Every gate is named**, so control tests and refusal receipts pin the
   exact rule (`rule` field), never prose.

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
