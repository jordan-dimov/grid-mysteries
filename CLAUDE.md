# Grid Mysteries

Grid Mysteries investigates surprising events in Britain's electricity system using public data. The goal is not hot takes or anomaly hunting for its own sake; it is **small, reproducible investigations that experts can falsify**.

## Research doctrine

- Separate **observation**, **interpretation**, and **conclusion**. Never smuggle one into another.
- Prefer the narrowest defensible claim. “Publicly unexplained from the state reconstructed here” is often stronger than “wrong”, “wasteful”, or “inefficient”.
- A price inversion, skip, forecast error, negative price, curtailment, or unusual dispatch is an **investigation candidate**, not a conclusion.
- Reconstruct what was knowable **at the relevant time**. Treat publication time, data vintage, superseded values, and later corrections as first-class evidence.
- Preserve corrections and failed hypotheses. Being falsified is useful research; silently rewriting the past is not.
- Distinguish realised facts from counterfactuals. Never label a counterfactual price difference as a saving or loss without proving substitutability and executability.
- Prefer primary public sources and official methodology for market rules and data semantics. Do not guess changing API schemas or current rules.
- Selection rules are pre-declared and committed before their window's data is touched, and an **amended rule never runs against a window that taught the amendment**. Week N teaches the method; a fresh, untouched chronological window tests it. Improving the method from a lesson is legitimate; re-mining the same corpus until it yields the hoped-for mystery is not.

## Architecture

- **Python owns analytics**: ingestion, validation, reconstruction, calculations, investigation logic, and rendering.
- **Morpholog owns the defensible research record**: source artefacts, investigation lineage, registered hypotheses, findings, and later corrections where warranted. Do not turn Morpholog into the analytics engine.
- Raw public downloads stay local and immutable under `data/raw/`; derived datasets go under `data/derived/`. Commit only small fixtures when licensing permits.
- Content-address source artefacts and retain enough metadata to reproduce them: publisher/dataset identity, URL or query identity, publication time when available, fetch time, and digest.
- Put source-specific behaviour in `src/grid_mysteries/sources/`, reusable analytical logic in `src/grid_mysteries/investigations/`, and presentation in `src/grid_mysteries/rendering/`.
- Each public investigation gets its own `investigations/<id>-<slug>/` directory. Keep the canonical method in tested Python modules, not in an opaque notebook.
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
