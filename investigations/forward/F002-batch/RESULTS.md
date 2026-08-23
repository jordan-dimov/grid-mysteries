# Batch 01 — kill results

Batch frozen at `5f352ebb096b6194571732bed281623879038d9c156b70fb6b36c2f6f80ba8a6`.
`BATCH-01.md` is never edited; results accumulate here.

| # | Candidate | Verdict | Record |
|---|---|---|---|
| C5 | Constraint/curtailment settlement reconciliation | **absorption stable** (externalisation already completed) | [KILL-C5.md](KILL-C5.md) |
| C1 | MHHS settlement data quality assurance | **absorption stable** (transition mistaken for structural change) | [KILL-C1.md](KILL-C1.md) |
| C6 | Small flexible asset prequalification/delivery | **strain plausible but not measured** → downgraded, blocked on non-public data | [KILL-C6.md](KILL-C6.md) |
| C7 | TO/DNO outage and access coordination | pending | |
| C8 | DNO→DSO whole-system asset visibility | pending | |
| C3 | Grid Code compliance for inverter-based resources | pending | |
| C10 | Grid/consent evidence for large new demand | pending | |
| C9 | Granular clean-energy claim verification | pending | |
| C4 | BESS degradation and warranty verification | pending | |
| C2 | Post-Gate-2 connection evidence (quarantined) | pending | |

Running tally against the thresholds declared in `BATCH-01.md`:
**evidenced or plausible strain: 1 of 3 resolved** (C6, plausible; downgraded).

## Instrument defects observed, deliberately not repaired

Held until the batch is complete, so a local defect is not mistaken for a
systematic one. Full entries in [`../LESSONS-PENDING.md`](../LESSONS-PENDING.md).

- **L1 · instrument eligibility** — an observed population must be
  capable, by construction, of containing the hypothesised failure.
  **Recurred in C5 (whole observation) and C1 (half).** Two of two.
- **L2 · already-externalised** — v3 has no mirror to its absorption
  kill for functions that left the incumbent years ago. **C5.**
- **L3 · positive control** — C5 yielded a dated trajectory of a category
  that did form; kept for comparison, not as a template. **C5.**
- **L4 · transition expenditure ≠ category formation** — **C1.**
- **L5 · no timing sensor for unfinished adaptation** (`AdaptationGap`) —
  **C5, C1 (completed adaptation); C6 sharpens it — adaptation in flight,
  racing the load, with no public measurement of which is winning.**
- **L6 · scarce unit of work / exception tail** — pre-declared before C6,
  and its trap was wrong in a useful direction. **C6.**
- **L7 · eligible instrument, unpublished series** — a third outcome,
  distinct from ineligible and from silent. **C6.**

### Three distinct ways a candidate fails, so far

Both found in the first two kills:

| | mechanism | candidate |
|---|---|---|
| absorbed successfully | the incumbent scales, usually as software, and cost per unit falls | C1 |
| already externalised successfully | the function left the incumbent years ago and the category has matured | C5 |
| unresolvable from public data | the strain is structurally plausible and the operational series is not published | C6 |

None is "no demand". In all three the need was real. C5 and C1 are
**timing** errors in opposite directions — six years late at a formed
category, and early against an absorber already building for the load.
C6 is not a timing error at all: it is the first candidate whose verdict
is limited by **what the public record contains**, which is the forensic
track's oldest problem arriving in the forward track.
