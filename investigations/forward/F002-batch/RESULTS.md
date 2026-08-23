# Batch 01 — kill results

Batch frozen at `5f352ebb096b6194571732bed281623879038d9c156b70fb6b36c2f6f80ba8a6`.
`BATCH-01.md` is never edited; results accumulate here.

| # | Candidate | Verdict | Record |
|---|---|---|---|
| C5 | Constraint/curtailment settlement reconciliation | **absorption stable** (externalisation already completed) | [KILL-C5.md](KILL-C5.md) |
| C1 | MHHS settlement data quality assurance | pending | |
| C6 | Small flexible asset prequalification/delivery | pending | |
| C7 | TO/DNO outage and access coordination | pending | |
| C8 | DNO→DSO whole-system asset visibility | pending | |
| C3 | Grid Code compliance for inverter-based resources | pending | |
| C10 | Grid/consent evidence for large new demand | pending | |
| C9 | Granular clean-energy claim verification | pending | |
| C4 | BESS degradation and warranty verification | pending | |
| C2 | Post-Gate-2 connection evidence (quarantined) | pending | |

Running tally against the thresholds declared in `BATCH-01.md`:
**evidenced or plausible strain: 0 of 1 resolved.**

## Instrument defects observed, deliberately not repaired

Held until the batch is complete, so a local defect is not mistaken for a
systematic one.

- **C5**: v3 has an absorption kill but no *already-externalised* kill.
  The mirror question "has this function already left the incumbent, and
  when?" is unasked, so the generator can point at a mature category.
- **C5**: the frozen forcing observation named a register (BSC Trading
  Disputes) that structurally cannot contain the disputes the candidate
  is about — owner-vs-optimiser disagreements are contractual, not BSC.
