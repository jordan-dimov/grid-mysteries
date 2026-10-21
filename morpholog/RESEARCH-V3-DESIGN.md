# Research programme v3: the forward and verifier vocabulary

Status: **deployed 25/09/2026** on the live record, same database and audit
chain as v1 and v2 (batch `110-forward-launch.v3.ndjson`, 94 rows: the
bootstrap and nine seals by Jordan as `gm_human`, the declarations, verdicts,
watches, triggers and evidence claims by the machine as `gm_machine`).
`research-v3-draft.morph` carries one respelling and one amendment since the
draft (fingerprint in `V3_DRAFT_HASH.json`, the file name kept so the pinned
hash and the batch dispatch stay as they were); `scripts/check-controls v3`
proves 20 lifecycle rows commit and 18 violations are refused by their exact
named rules. The launch rows and how they were run are in `launch-forward/`.

**Amended 21/10/2026, on the sponsor's word:** a watch past due with no
reading is a lapse the record itself admits. `sweep_watch(watch, as_of)`
admits `Lapsed(watch, as_of)` under three gates (not yet lapsed; the due
date before `as_of`; no reading on or before `as_of`) and three invariants
(a lapse names a watch, follows its due date, and precedes any reading), the
shape of Morpholog's gallery examples 09 and 17: an outside sweep hands the
kernel the date, never a clock inside a rule. `scripts/sweep-watches`
proposes exactly the sweeps the kernel says it would admit (`morpholog
explain`, nothing recorded), through `scripts/record` (batch
`121-watch-sweeps.v3.ndjson`). `scripts/check-record` no longer compares
dates itself: it asks the kernel whether a sweep would commit, and fails
on an unswept lapse (run the sweep) and on a lapsed watch with no reading
(record it). The pin moved from `sha256:ef203533…` to `sha256:b5227df4…`;
the stored claims are untouched (one predicate added, none changed).

**Respelled 08/10/2026, on the sponsor's word:** `three_clocks_ordered` now
binds the `claim` it guards (`EvidenceClaim(claim, _, _, _, t_event,
t_public)` instead of `EvidenceClaim(_, _, _, _, …)`). Same rule, same
decisions: every evidence claim's event clock still has to be on or before
its public clock. Morpholog v0.0.14's `check --strict` names the old
spelling as a case wider than the claim it guards (#446), and from that day
`scripts/check-programmes` checks every programme strictly. The pin moved
from `sha256:0cd623d3…` to `sha256:ef203533…`; the record replays under the
respelled programme (`scripts/replay-research` on a fresh cluster, 242
claims identical) and the live database's provisioning is unchanged by it.
Audit rows written before 08/10 carry no programme hash (migration 020 is
not backfilled); rows from the respelling on carry the new one.

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
   not_available)`; from 21/10/2026 `Lapsed(watch, as_of)`, admitted by a
   dated sweep under the programme's own rule. `check-record` fails when a
   watch is past due with no reading, swept or not, so "we'll look again in
   November" cannot silently lapse.
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
