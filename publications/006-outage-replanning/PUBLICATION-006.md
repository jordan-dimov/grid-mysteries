# Publication Pack 006 — the plan gets better, the changes come faster

No new analysis. The post copy is `POST-C7.md` (from Batch 01 candidate C7,
`investigations/forward/F002-batch/KILL-C7.md`, including its same-day
correction and the FY25 verification). The visual (`within-year.svg`,
rendered by `render.py` from `evidence.json`, transcribed from the verified
KPI table) shows the one series the finding rests on. **Human gate:
publication.**

## The visual

**`within-year.svg`** — within-year outage requests by phase, FY24 versus
FY25: +51%, +35%, +52%. Two series, one legend, the FY25 values labelled.

## Expert corner

- **Instrument.** NGET *Network Access Planning KPIs*, July 2026 (FY25 /
  T2Y4), published under the GB Network Access Policy; earlier editions
  July 2023 and July 2024. KPI 3a/3b/3c = new within-year outage requests
  before optimisation / in optimisation / in delivery. KPI 1c = share of
  the year-ahead plan delivered: 61% (FY22), 50%, 46%, **50% (FY25)** —
  NGET: "reversing the prior decline". KPI 5, "Outage coordination",
  remains unreportable in all four years because of how eNAMS records
  work bundling; NGET states 91% of outages carry more than one piece of
  work.
- **The workload.** NESO's own description, fetched and verified: a
  typical year-ahead plan of ~2,500 outages; over 17,000 TO outage
  changes processed against it in a typical year; "any outage changes
  received following the initial TO submission means the NESO detailed
  outage assessment needs to begin again"; a team of 65 engineers.
- **What was withdrawn, and why it is on the record.** The first version
  of this finding rested on a fall in system faults (260 → 64) that NGET's
  own commentary attributes to a recording change; on a 2,846 repeat-
  outage figure later revalidated to 1,480; and on a 3.62% non-firm
  curtailment figure arising from a single busbar outage. All three were
  withdrawn the same day, before publication, and the finding re-based on
  the within-year request series and NESO's workload statement. The
  correction is in `KILL-C7.md`.
- **Verdict under the batch protocol.** *Absorption strain evidenced* —
  replanning volume is growing faster than the plan is improving. What is
  *not* established: that any of this is externalisable. Both institutions
  are adapting and say so (System Access Reform; NGET's planning and
  delivery transformation into RIIO-T3). It is an adaptation race with a
  measured numerator, not a failure.
- **Reproduce.** `uv run python publications/006-outage-replanning/render.py`.
