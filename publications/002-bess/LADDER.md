# The Counterfactual Integrity Ladder

*A one-page test for any "missed revenue", capture-rate or
benchmark-underperformance number attached to a battery asset. Each level
is an upper bound on the one below it; a benchmark figure is only as
defensible as the highest level it has actually established. Send this to
whoever produced the number and ask which level it lives on.*

| Level | The claim it can defend | Established from |
|---|---|---|
| **Observed** | this revenue / action actually happened | settlement data |
| **Power-feasible** | the MW movement was not provably impossible | public physical notifications and export/import limits (FPN, MEL/MIL) |
| **Duration-feasible** | the storage asset's published delivery envelope permitted sustaining it | public GC0166 MDO/MDB data — *and this level exists in two versions that provably differ: the **final published envelope** and the **envelope publicly observable when the decision had to be made*** |
| **Operationally comparable** | the opportunity was genuinely in the relevant dispatch comparison set | operator-published availability, exclusion and skip context (volumetric — presence can be disclosed publicly; adjudication cannot) |
| **Asset-feasible** | *this particular battery* could have done it | **owner data**: actual state of charge, degradation and cycling constraints, simultaneous market commitments, outage/derating state, operating restrictions |
| **Decision-feasible** | the optimiser could reasonably have chosen it | **owner/optimiser data**: the information actually held at gate closure, forecasts, mandate, risk limits, response latency |

## Why the ladder matters — measured, not asserted

In July 2026 — the first full month for which the public MDO/MDB data
exists — we rebuilt a deliberately naive battery opportunity benchmark
level by level for the GC0166 early-submitter panel (four units,
mechanically selected):

- **95.3%** of the price-only construct failed *power-feasible*.
- The new duration envelopes removed **another 44.8%** of what physics
  alone had permitted.
- The two duration views **provably differ in both directions**: the
  final envelope supported **£4.69m** that was not publicly observable at
  decision time, and *withdrew* **£3.43m** that the contemporaneous
  public data had supported. Any benchmark built on final data is
  grading historical decisions against a revised information set.
- After the operational-context disclosure, **0.05%** of the original
  construct remained free of published exclusion context.

All figures are arithmetic on public numbers — never savings, missed
revenue, or achievable value. Full method, evidence digests and
reproducible pipeline: github.com/jordan-dimov/grid-mysteries
(BESS Study 001; every rule pre-committed before the data was fetched).

## The questions this ladder asks of any benchmark number

1. Which level does the number live on, and can its producer show the
   level's evidence?
2. Which *information set* defined it — final published data, or data
   observable when the decision had to be made?
3. Was the residual "missed" opportunity in the asset's dispatch
   comparison set at all?
4. What did the asset's actual state (charge, commitments, outages)
   permit — and has anyone with access to that state checked?

**Public data can test whether a claimed opportunity survives public
reality. Establishing whether *your* asset could actually have captured
it requires the asset's private state.** That boundary is where a
benchmark stops and an assurance exercise begins.
