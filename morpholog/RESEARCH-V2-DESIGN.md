# Research programme v2: the governed research state machine (design)

Status: **draft, not deployed**. `research-v2-draft.morph` is check-clean
under the pinned Morpholog release; `research-v2-evaluate.json` scores it
against the committed v1 history. The deployed programme remains
`research.morph` (v1) until the migration decision below is taken.

## Why v2

v1 records that research acts happened; the project's most distinctive
claim — *the method was committed before the data was seen* — is enforced
by git discipline and behaviour. v2 makes the lifecycle executable, so
certain forms of retrospective cheating become structurally difficult:

1. **Sealing authorises acquisition.** `seal_protocol` is the only act
   that emits `DataAcquisitionAuthorised`, and `attach_source` *requires*
   a sealed protocol. The fetcher is triggered by the emitted intent
   (Morpholog's outbox is the natural delivery path), and the fetch
   tooling refuses to run without the authorisation. The audit sequence
   then genuinely reads: protocol sealed → acquisition authorised →
   evidence admitted → analysis authorised → finding.
2. **Ordering is proven by audit-log sequence, never by timestamps.**
   Caller-supplied `fetched_at`/`declared_at` values are recorded but
   deliberately carry no invariant force: a dishonest client could fake
   them, whereas it cannot fake its position in the Merkle-chained log.
3. **Conclusion classes have governed semantics.** An `#explained`
   finding requires at least one `#explained` mechanism assessment; a
   `#publicly_unexplained` finding is refused if any mechanism is
   assessed `#explained`; assessment statuses are restricted to the
   five-word protocol vocabulary at the transformation gate.
4. **In-sample work cannot be promoted.** Investigations carry a `kind`
   (`#prospective` / `#descriptive` / `#method_study`) and a declared
   `CorpusStatus`; a finding on a `#prospective` investigation is refused
   unless its corpus was declared `#untouched`. Method studies stay
   method studies forever.
5. **Corrections are supersession, not annotation.** A finding is never
   edited; `supersede_finding` admits a new finding and a
   `SupersedesFinding` edge (each finding superseded at most once, so
   standing forms a chain). "What did we conclude on 16 August?" and
   "what do we conclude now?" are both answerable truthfully; the current
   finding is the one nothing supersedes.

## Per-kind lifecycles

The v2 skeleton enforces the shared spine (declare → seal → acquire →
seal evidence → analyse → publish). Kind-specific orderings — e.g. a
prospective test requiring the hypothesis to be registered *before*
`seal_protocol`, or a descriptive search requiring `record_selection`
before its explanation-protocol seal — are phase-2 refinements, added as
gates on the existing transformations once Investigation 002 exercises
the spine. Deliberately not speculated into the draft.

## What `evaluate` says about v1 history

Replaying the 12 committed v1 transitions under v2's invariants
(`research-v2-evaluate.json`): `attached_source_has_sealed_protocol`
would have refused 1 transition, and `hypothesis_has_investigation`
1 more (v2's four-field `Investigation` does not match v1's three-field
claims). That is the honest statement that **v1 history does not satisfy
the v2 lifecycle** — as expected, since sealing did not exist.

Migration therefore has two defensible options:

- **A (preferred): fresh start.** Deploy v2 for Investigation 002
  onward in a new programme; v1 claims remain governed by v1, replayable
  and audit-anchored exactly as today. No history is rewritten, and the
  earliest v2 investigation is the first with machine-enforced
  pre-registration.
- **B: backfill.** Re-admit v1 history under v2 with synthetic
  `ProtocolDeclared`/`ProtocolSealed` claims dated by the git evidence.
  Rejected for now: it would fabricate lifecycle acts that never ran
  through the kernel, which is the exact behaviour v2 exists to prevent.

## Adoption plan

1. Investigation 002 (earliest legitimate start: ~2026-08-21) opens under
   v2 as `#prospective`-style descriptive search with `CorpusStatus
   #untouched`.
2. The 002 fetch tooling consumes `DataAcquisitionAuthorised` (outbox or
   a pre-flight `morpholog inspect` check) and refuses to run without it.
3. `scripts/replay-research` grows a second programme section (v2 batches
   replayed under the v2 hash) alongside v1.
4. After 002 lands, revisit the phase-2 kind-specific gates with real
   usage behind them.
