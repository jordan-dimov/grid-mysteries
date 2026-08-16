# The six fell too

*Method Study 001D research note. Cases fixed by 001C's committed
evidence; per-cell detail in `evidence/six-anatomy.json`.*

## Verdict

The registered hypothesis (`hyp-ms-001d-six-explainable`) is
**confirmed: all six unmatched unit-day cells are explained**, and by a
single mechanism — the one 001C had already crowned, seen from the other
side of the comparison.

001C attributed disagreement through NESO exclusion rows keyed by the
*alternative* unit. But NESO's Exclusion Reasons data also excludes
**accepted-side** actions from its skip-comparison stack
(`excluded_from_accepted_or_feasible_merit_stack = "Accepted"`). For
every one of the six cells, the accepted bids our screen compared the
unit against are dominated by exactly such exclusions on that date and
direction — overwhelmingly **"Behind constraint"** — corroborated by
SO-flagged acceptances in the exact qualifying settlement periods:

| Cell | Qualifying periods | Accepted-side exclusion rows (top reason) | SO-flagged counterpart acceptances |
|---|---:|---|---:|
| 2026-08-05 bid BHOLB-1 | 21 | 43,752 Behind constraint | 70 |
| 2026-08-06 bid BHOLB-1 | 24 | 12,841 Behind constraint | 16 |
| 2026-08-06 bid THMRB-1 | 22 | 11,504 Behind constraint | 14 |
| 2026-08-09 bid BHOLB-1 | 18 | 36,233 Behind constraint | 28 |
| 2026-08-09 bid CUMHW-1 | 3 | 760 Behind constraint (+724 System-tagged) | 5 |
| 2026-08-10 bid THMRB-1 | 22 | 6,241 Behind constraint | 8 |

The SO-flagged counterparts are constraint-management actions on wind and
hydro units (Seagreen, Viking, Edinbane; Cruachan, Sloy; plus Grain
CCGT): NESO paid them to move for locational reasons, then — by its own
published methodology — removed those acceptances from the stack against
which skips are judged. Our screen made precisely the comparison NESO's
methodology declines to make. No skip is recorded because, in the
operator's accounting, there was nothing comparable to skip.

Mechanism statuses per the explanation protocol: accepted-side exclusion
**explained** (rows and flags cited above, per cell); granularity and
de-minimis headroom (BHOLB-1's deliverable bound was 0–7 MW throughout)
**contribute** context; battery state of charge was **not needed**.

## What this does to the story

The residue of the entire week is now **zero unmatched unit-days**. The
four-layer narrative gains its true ending: price screamed 3.86 million
inversions; physics deleted the entire top of the ranking; the operator's
published availability and location context explained 99.7% of what
survived; and when the last six cells were inspected at period level and
on *both sides* of the comparison, they dissolved into the same
locational mechanism. Public data, read at the right resolution, and
with the operator's own exclusion semantics respected on both sides,
explained everything this week — which is itself the strongest possible
statement of why naive readings of it mislead.

001C's finding stands as published; this study extends its attribution
method (alternative-side keying) with the accepted-side keying it lacked,
and the lesson is recorded for 002+: **disagreement attribution must key
the operator's exclusions on both sides of every comparison.**

## Reproduction

Commands in `METHOD-STUDY-001D.md`. New pinned evidence: 89 BOALF
artefacts (`evidence/boalf-manifest.json`). All other inputs are the
already-pinned artefacts of Method Studies 001, 001B and 001C.
