# Research programme v3: the forward and verifier vocabulary

Status: **drafted, control-tested, not yet deployed.** `research-v3-draft.morph`
is check-clean under the pinned release (fingerprint in `V3_DRAFT_HASH.json`);
`scripts/check-controls v3` proves 16 lifecycle rows commit and 14 violations
are refused by their exact named rules. Launch rows for everything the
forward track produced in August 2026 are in `launch-forward/`.

## Why a third programme

v1 records that acts happened; v2 makes the forensic lifecycle executable.
Neither can hold what F001–F005, Batch 01/02 and Investigation 005 forced:
frozen artefacts that are not inquiries, verdicts that carry a reason, dated
promises to re-observe, parked theses with reopening conditions, and evidence
whose *class* matters more than its content. The forward track ran a week on
"frozen on commit" — a git digest, an amendable history — and every one of
its declarations, twelve kill records, one K3 and ten dated watches sat
outside the governed record. v3 is the vocabulary that week discovered; it
was deliberately not designed in advance (F001's rule), and it is proposed
now because the forcing evidence exists.

## What v3 makes executable

1. **Any frozen artefact can be sealed.** `Declaration(kind ∈ generator |
   batch | forward_study | kill_test | forensic_study, content_digest)` and
   `DeclarationSealed`, human-gated by `DeclarationSealAuthority`.
   `scripts/check-record` verifies every sealed digest still hashes to a file
   on disk, exactly as for v2 protocols. Supersession is a pointer
   (`DeclarationSupersedes`), one prior per successor, a prior superseded once.
2. **Verdicts carry their reason and cannot precede a seal.**
   `Verdict(declaration, about, stage, code, reason, evidence_digest)` with a
   closed code vocabulary — the v4 reason codes (`measured_stable` …
   `not_yet_observable`), the v3-era absorption codes, K0's buyer classes,
   the gate's instrument states, and `pass/fail/killed/quarantined` — one
   verdict per (declaration, subject, stage). "Plausible but not measured" is
   not in the vocabulary: the kernel refuses the retired code.
3. **A dated watch is an obligation.** `Watch(about, resolving_observation,
   holder, due)` and `WatchReading(outcome ∈ resolved | unchanged |
   not_available)`. `check-record` fails when a watch is past due with no
   reading, so "we'll look again in November" cannot silently lapse.
4. **Reopening triggers fire once, against evidence.** `ReopenTrigger` and
   `TriggerFired(evidence_digest, fired_on)`.
5. **Evidence classes with the three clocks.** `EvidenceClaim(evidence_class
   ∈ provision_exists < provision_purchased < repeat_purchase < standardised
   < penetration_measured, t_event, t_public)` with `t_event on_or_before
   t_public` enforced. The promotion ban itself — a stronger class may not
   be admitted from weaker evidence — remains doctrine rather than a gate:
   the kernel cannot judge evidence quality, only record which class was
   claimed, by whom, with what digest, and when.

## Deployment model

As v2: same database and audit chain, fully disjoint predicate vocabulary.
Actor policy (`ActorAssertionRestricted` / `ActorAssertionAuthority`) is
already established by v2's bootstrap and is read by the adapter regardless
of programme; v3 declares only its own authority predicate. Batches are
dispatched by filename (`*.v3.ndjson`) in `scripts/record` and replayed by
`scripts/replay_v2.py` through the actor's bound login role. The same
threat model applies (RESEARCH-V2-DESIGN.md, three layers): governed-path
enforcement holds; substrate capability security does not.

## What is deliberately not in v3

A composite opportunity score; buyer evidence at generation time; a kernel
judgement of whether a proxy "counts" as measured (L15/L16 make that a
declared property of the next batch file, reported as two rates); and any
predicate for Grid Mysteries' verifier role beyond `EvidenceClaim` — a claim
from a conversation is recorded with its class and clocks like any other.
