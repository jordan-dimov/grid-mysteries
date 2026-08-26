# C3 — conversation brief (built only from the existing record; no new research)

**Purpose**: five conversations in two weeks that answer one question and
produce one of six kinds of "would pay" evidence, or kill C3. Written
2026-08-26 under the recalibration rule (≤2 hours desk work). Everything
below is already in `KILL-C3.md`, F001 and the batch lessons; nothing was
newly researched.

## What the record already establishes (do not re-research)

- **The loop, first-party from NESO's EMT Model Requirements FAQ**: models
  due 3 months before ION and 1 month before LON; first review 3–4 weeks;
  "each re-submitted or revised model will be treated as a new
  submission. NESO requires three weeks (15 working days) to validate
  each revised model"; "If a model is rejected multiple times due to
  non-compliance, the responsibility for any delays in issuing the
  ION/FON rests on the customers." **Each failed iteration costs a project
  three weeks of energisation.**
- **Volume rises by construction**: GC0141 and GC0168 require
  manufacturer-validated EMT models; GC0168 seeks retrospective
  submissions for connections commissioned before September 2022 — a
  stock of legacy work on top of the flow.
- **What is not published**: the iteration count / rejection rate. NESO
  publishes the cost of a rejection, not its frequency.
- **Absorption so far**: partly externalised to power-systems
  consultancies as expensive human judgement sold by the day — not as a
  product, benchmark or instrument. Vendor voice claims studies are
  critical-path and OEMs are often new to PSCAD; treated as a signal of
  where pain is claimed, not as evidence.
- **Why it matched the commercial prior**: an expensive decision by
  scarce specialists over fragmented inputs (OEM models, network models,
  tool and compiler versions), rising in frequency with every connection,
  with failure priced in weeks.

## The decisive unanswered question

> **When a model fails NESO review, how much of the correction work is
> repetitive and pre-checkable — consistency, configuration,
> initialisation, documentation, evidence packaging — versus genuinely
> bespoke control-engineering judgement?**

If "half our failures are stupid consistency and evidence problems" →
there may be something immediately sellable. If "virtually every failure
is plant-specific control engineering" → kill C3.

## Who to talk to (10–15 approaches for 5 conversations)

Buyer classes and adjacent specialists, in the order most likely to hold
a *real failed model*:

1. **Developer / owner grid-compliance leads** (BESS and solar
   developers with 2024–26 energisations) — they bear the ION/FON delay.
2. **Inverter / PCS OEM modelling engineers** — they produce the EMT model
   and receive the rejection.
3. **Power-systems consultancies** doing Grid Code compliance studies —
   they see many failures across clients (and are the incumbent
   absorber; ask what they would *not* want automated).
4. **Former NESO / TO compliance engineers** — they know what the review
   actually checks and what fails first.
5. **EPC / owner's-engineer compliance managers** — they hold the
   submission calendar and the cost of a slipped ION.

## The one question, and its follow-ups

> "Tell me about the last model that didn't pass first time. What exactly
> was wrong?"

Then, only as needed:
- How many iterations did it take, and how many weeks of energisation did
  that cost? Who paid for the rework (day rates, internal time, OEM)?
- Of the things that were wrong, which could a machine have caught
  before submission — naming conventions, parameter consistency,
  initialisation, version/compiler mismatch, missing evidence — and which
  needed an engineer to think?
- What do you do *today* before you submit? Who does it, how long, what
  does it cost?
- If something checked the pre-checkable half before submission, what
  would it have to prove to you before you trusted it?
- Would you send us a real failed submission and its rejection
  correspondence?

Do not pitch. Do not describe a product. Listen for repetition across
conversations — three people naming the same check is the only build
trigger.

## What counts as "would pay" (stronger than enthusiasm)

Any one of these, dated and attributable:
- offers to send a real failed model and its rejection;
- agrees to a **paid** diagnostic;
- asks for a proposal;
- introduces the budget holder;
- provides historical rejection artefacts;
- names a price or cost they are already paying for this (day rates,
  internal FTE, weeks lost).

Enthusiasm, "that would be useful", and requests to "keep in touch" are
`FounderAttention`-grade and do not count.

## Kill condition

By 2026-09-09, none of the six evidence types obtained from any of the
five conversations, **or** the answer to the decisive question is
consistently "bespoke engineering" → **C3 killed**, recorded in
`KILL-C3.md` as a dated commercial outcome (not a research finding).

## What Grid Mysteries does with the conversations (its 10%)

Verifier role only: each consequential claim made in a conversation
("NESO rejects most first submissions", "GC0168 doubles the workload",
"a rejection costs us £X") gets the three-clock treatment (t_event,
t_public, t_discovered) and, where a public series can confirm or refute
it, a check against that series. Claims that cannot be checked are
recorded as claims. No batch, no generator, no new instruments.
