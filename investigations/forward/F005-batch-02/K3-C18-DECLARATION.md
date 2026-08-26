# K3 — capture test for C18, declared before it is run

**Declared 2026-08-26, after K1/K2 (`dff9548`) and before any K3 evidence
was examined. Frozen on commit.**

C18 is the only Batch 02 candidate to reach K3: registering and
maintaining flexible-asset data across DSO and ESO markets. K1 found the
function regulator-declared inadequate and assigned to Elexon (FMAR,
March 2025); K2 measured strain in FMAR's delivery (milestones missed,
Ofgem rating 2/5 "Poor", 30 Jul 2026).

## The question, narrowed

Not "can something be built around flexibility registration". Only:

> **Does the observed FMAR delivery strain create unmet demand that an
> external entrant can actually capture — or is it an implementation
> problem inside an already-funded Elexon programme?**

Prior, recorded so it cannot be adjusted afterwards: the strain is
regulator-recognised, assigned, BSC-funded, and expressed as missed
milestones rather than as buyers purchasing workarounds. That is the
shape of *an incumbent replacement struggling*, not *a buyer need
escaping the incumbent*. Only the second is white space. **C18 is
expected to die here.**

## Pass conditions — at least one, evidenced with dated primary sources

1. **External spend caused by the strain.** Market participants, DNOs,
   aggregators or Elexon itself are paying identifiable third parties
   specifically to bridge or mitigate the registration problem (multi-
   platform registration, data re-entry, reallocation between FSPs)
   while FMAR is undelivered.
2. **A necessary function left unserved.** Users are demonstrably
   duplicating work, building parallel systems, delaying market entry, or
   bearing a measurable cost that Elexon's programme does not absorb —
   evidenced by their own statements, filings or consultation responses,
   not by inference from the delay.
3. **An addressable supplier role exists.** A function an independent
   entrant could sell *without* replacing Elexon or obtaining a regulatory
   mandate — e.g. an integration, data-quality, or reallocation service
   that FMAR's declared Day-1 scope (sub-1 MW assets; four platforms; no
   single market-entry portal) leaves outside it.

And, for a pass to count commercially: a **plausible route to repeat
spend** — recurring or repeatable across buyers — not one consultancy
engagement.

## Kill condition

None of 1–3 evidenced → **K3 kill: strain exists, but capture remains
internal to the incumbent programme.** Recorded as the batch's
distinction between *measured strain* and *commercial opportunity*.

## Evidence rules

Primary and dated: procurement notices, vendor announcements naming a
buyer, consultation responses (Ofgem/Elexon FMAR minded-to, SLC 31E
reports), job specifications, DNO/aggregator statements. A vendor's
marketing is `ProvisionExists`, not spend. Elexon's own contractor spend
on delivering FMAR is *inside* the programme and does not satisfy
condition 1 unless the buyer is a market participant bridging the gap.
Budget: one agent, ~40 tool calls. No broadening of the candidate.
