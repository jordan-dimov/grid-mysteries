# Grid Mysteries

Grid Mysteries investigates Britain's electricity system using public data. The goal is not hot takes or anomaly hunting for its own sake; it is **small, reproducible investigations that experts can falsify**.

The project runs **two tracks under one philosophy** — *don't accept the obvious story; reconstruct what reality permits*:

- **Forensic Mysteries** (`investigations/`, ids `001`, `002`, …): *something happened that looks strange — what actually caused it?* Observed anomaly → explanation → methodological lesson.
- **Forward Mysteries**, or **Inevitability Studies** (`investigations/forward/`, ids `F001`, …): *something is already changing — what future problem does that make hard to avoid, and who has not realised they will have to solve it?* Present facts → constraint → consequence → recognition gap → opportunity.

They are the same discipline pointed at different tenses. A Forward Mystery is not a forecast and never a trend list; it is an argument that a consequence is **more determined than it appears**, published with the evidence that would refute it.

## Research doctrine

- Separate **observation**, **interpretation**, and **conclusion**. Never smuggle one into another.
- Prefer the narrowest defensible claim. “Publicly unexplained from the state reconstructed here” is often stronger than “wrong”, “wasteful”, or “inefficient”.
- A price inversion, skip, forecast error, negative price, curtailment, or unusual dispatch is an **investigation candidate**, not a conclusion.
- Reconstruct what was knowable **at the relevant time**. Treat publication time, data vintage, superseded values, and later corrections as first-class evidence.
- Preserve corrections and failed hypotheses. Being falsified is useful research; silently rewriting the past is not.
- Distinguish realised facts from counterfactuals. Never label a counterfactual price difference as a saving or loss without proving substitutability and executability.
- Prefer primary public sources and official methodology for market rules and data semantics. Do not guess changing API schemas or current rules.
- **Public-as-of time is the forward analogue of the untouched window.** A Forward Mystery freezes, at a declared date, what was publicly knowable, how we read it, what we assumed, what we derived, what would falsify it, and what action looked attractive. Later knowledge never rewrites that record — it is appended as outcome. This is what makes the project accumulate an *authentic* prediction record rather than a collection of essays explaining why we were right all along.
- **The irreversible boundary differs by track.** For forensic work it is *acquisition* — looking at unseen data — so the human seal gates the fetch. For forward work it is *publication* — a prediction, once public, cannot be un-predicted — so the human gate belongs at release, and the falsifier must be published with the claim, not after it.
- A Forward Mystery must earn three separate propositions before it may name an opportunity: **the problem is coming**, **a buyer will be compelled to solve it**, and **existing solutions solve it inadequately**. The third is the hardest and is never assumed from the first two. Absent the third, the honest output is a described problem, not an opportunity.
- **Before predicting a new market from a future problem, ask whether the economy has already assigned that problem to an existing job.** This is the first-order question, established by F001: a need can be highly predictable, valuable and growing while producing almost no opportunity, because an existing profession simply adds one line to its scope. **Absorbability is a variable, not an afterthought** — `CategoryPotential ∝ Necessity × FailureOfAbsorption × ValueOfExternalisation`.
- **The cheapest absorption kill runs before the sophisticated thesis.** The order is: establish the structural change *only enough to justify looking*; then ask **"who already gets paid to perform this function — and is that absorption economically stable as the forcing variable grows?"** Absorbed-successfully and absorbed-badly-but-not-externalised are different answers: if required work can grow fivefold while delivery capacity grows a fifth, something must change, and the candidate survives the kill. Not "does a startup exist", not "is there software". Proceed only if the function is unabsorbed, or absorption is visibly breaking. F001 took several rounds of causal reasoning to reach a conclusion that one dated press release and one Companies House record settled in minutes.
- **Absorption fails for identifiable reasons, and those are what to hunt** — the following ten are **hypotheses under test, not settled doctrine**, and a generator built on them may have false negatives: volume beyond bespoke human scaling; frequency shifting from per-transaction to continuous; coordination across organisations no incumbent controls; independence the performing party cannot self-supply; comparability across many assets; data intensity exceeding judgement; liability someone must stand behind; latency intolerance; standardisation of repetitive work; and economics where adviser cost outgrows transaction value. **Find necessary functions that existing jobs are beginning to fail at absorbing** — that is where categories are actually born.
- **A strong publishable fact that fails the monetisation threshold is published and moved on from.** Not every investigation must become a business; explaining a near-miss into relevance is the failure mode, not the miss (calibrated on 005/006, 2026-08-26).
- **Research is chosen by leverage, not by uncertainty**: prefer the evidence with the highest *(probability of changing the conclusion × economic importance) ÷ cost of obtaining it*. The standing question is **"what is the cheapest piece of evidence capable of killing this?"**
- **Forecast correctness is a vector, never a verdict**: `(need, timing, adoption, capture)`. A study whose causal forecast is right while its *economic transmission* forecast is wrong has failed differently from one whose predicted problem never materialised, and scoring them alike would teach the machine nothing. **Need failure** and **capture failure** are recorded separately.
- Forward work reports a **profile across dimensions** (constraint strength, evidence quality, scenario robustness, recognition gap, buyer pain, solution adequacy, action lead, reflexivity), never a single score. A composite number converts judgement into false precision and hides which branch actually needs more research.
- Selection rules are pre-declared and committed before their window's data is touched, and an **amended rule never runs against a window that taught the amendment**. Week N teaches the method; a fresh, untouched chronological window tests it. Improving the method from a lesson is legitimate; re-mining the same corpus until it yields the hoped-for mystery is not.

## Architecture

- **Python owns analytics**: ingestion, validation, reconstruction, calculations, investigation logic, and rendering.
- **Morpholog owns the defensible research record**: source artefacts, investigation lineage, registered hypotheses, findings, and later corrections where warranted. Do not turn Morpholog into the analytics engine.
- Raw public downloads stay local and immutable under `data/raw/`; derived datasets go under `data/derived/`. Commit only small fixtures when licensing permits.
- Content-address source artefacts and retain enough metadata to reproduce them: publisher/dataset identity, URL or query identity, publication time when available, fetch time, and digest.
- Put source-specific behaviour in `src/grid_mysteries/sources/`, reusable analytical logic in `src/grid_mysteries/investigations/`, and presentation in `src/grid_mysteries/rendering/`.
- Each public investigation gets its own directory: `investigations/<id>-<slug>/` for forensic work, `investigations/forward/F<nnn>-<slug>/` for Forward Mysteries. Existing top-level investigation directories are forensic by convention and are **not** relocated: their evidence is byte-pinned and referenced by digest, and tidiness is never worth disturbing a sealed record.
- **The frozen declaration lives in its own file** (`DECLARATION.md`), never the document that later grows results. Its SHA-256 is what the governed record seals, so those bytes must remain recoverable forever; `scripts/check-record` enforces that every sealed digest still matches a file on disk. Keep the canonical method in tested Python modules, not in an opaque notebook.
- Version pins belong in their operational files (`.python-version`, `pyproject.toml`, installer/lockfile/CI), not in this file.

## Engineering rules

- Use `uv` for Python environments and dependency locking.
- Target the Python version declared by the project; use modern stdlib features freely within that contract.
- Use `Decimal` for prices, money, and other values where binary floating-point would weaken a claim.
- Keep dependencies few and justified by a concrete need.
- Analytical rules need tests, especially boundary cases and counterexamples.
- Keep pure domain logic separate from network I/O and rendering so investigations can be replayed from fixtures.
- Make network-derived inputs explicit; tests must not depend on live public APIs.
- Before finishing a change, run the project check command (`scripts/check`) or its constituent checks if the full toolchain is unavailable. State clearly what was not run.
- When changing the Morpholog pin, verify the official release and published checksums, then keep installer, documentation, and CI consistent.

## A publishable investigation

A publishable mystery should contain:

1. **The mystery** — one sentence a non-specialist can understand.
2. **The evidence** — the smallest public-data reconstruction supporting the question.
3. **Explanations tested** — what was checked, what was ruled out, and what remains unknown.
4. **The conclusion** — narrow, falsifiable, and explicit about uncertainty.
5. **Expert corner** — exact identifiers, assumptions, timestamps, source artefacts, and enough detail for a practitioner to challenge it.
6. **Reproducibility** — code/tests plus pinned evidence sufficient to rerun the material calculation.

Optimise for credibility and cumulative knowledge, not posting frequency. A clean “explained” result or a public correction is a successful investigation.
