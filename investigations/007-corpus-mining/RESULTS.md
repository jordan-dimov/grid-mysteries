# 007 — corpus mining: results

**Run**: 2026-08-26, one day, existing repository data only. Declaration
`9ccfbe9e…` (commit `57a19e9`) frozen before any of the three results was
computed. Evidence: `evidence/t1-t2-summary.json`, `evidence/t3-summary.json`.
Runners: `run_tec.py`, `run_skip.py`.

## The funnel

**13 datasets → 8 latent questions → 3 frozen tests → 1 decision-relevant
finding** (plus one modest negative and one test that was mis-built).

## T3 — skip persistence by unit: PASS, strongly

*Population*: BM units × direction with positive in-merit volume in both
months of NESO's in-merit stack files (May 2026: 797 unit-directions; July:
912; August, earlier vintage: 863). *Metric*: monthly skip share =
Σ skipped ÷ Σ in-merit volume (summed across NESO's stack stages 0–5, the
same way in every month).

| transition | units in both | top-quartile in first month | still top-quartile in second | conditional | unconditional | Spearman (share, month to month) |
|---|---|---|---|---|---|---|
| May → July | 748 | 187 | 125 | **66.8 %** | 25.0 % | **0.73** |
| July → August | 809 | 214 | 139 | **65.0 %** | 25.5 % | **0.69** |

Both transitions clear the frozen bar (≥ 50 %, n ≥ 100) by a wide margin.
By fuel, May → July persistence among top-quartile units: gas 95 % (n 21),
wind 72 % (29), CCGT 61 % (18), **battery 53 % (66)**; July → August: wind
100 % (23), gas-reciprocating 89 % (19), **battery 69 % (51)**, CCGT 56 %
(25). Batteries are the largest fuel among persistently skipped units in
both transitions (35 of 125, 35 of 139) — because they are the largest
population, not because they persist most.

**Decision sentence, completed.** *If I were buying or siting a BESS, a
unit's skip share is a persistent month-to-month property — a unit in the
most-skipped quartile stays there about two-thirds of the time, and the
rank correlation of skip share across months is ~0.7 — so I would treat
skip exposure as an attribute of the unit and its location to be
diligenced and priced, not as monthly noise to be averaged away.*

**What this does not say, fixed in the declaration.** A skip is not an
inefficiency (001, 001B–D: deliverability and system-flag reasons account
for most naive "skips"). T3 shows persistence, not cause. Persistence is
compatible with a locational constraint *and* with a unit's own repeated
pricing at the margin; distinguishing those needs the exclusion-reason
field (dataset #6), which is a cheap next test and was deliberately not
run — the mandate stops at the first strong survivor. Three months of
data (May, July, August 2026) is the whole corpus; the August file is the
earlier of two retained vintages.

## T1 — slip persistence: FAIL

Exposed (a first ≥ 6-month slip, ≥ 24 months of observation remaining):
n 197, further ≥ 6-month slip within 24 months **36.5 %**. Control (no slip
in the first 12 months, ≥ 36 months observed): n 374, slip in months 12–36
**27.5 %**. Ratio **1.33**, gap **+9.0 pp**; direction holds in both
cohorts (2014–18: 40.3 % vs 31.6 %; 2019–24: 30.1 % vs 20.4 %). Frozen bar:
ratio ≥ 1.5 and gap ≥ 15 pp. **Not met.**

Banked as: a first observed slip raises the 24-month probability of
another by about nine points — a real but modest signal. *If I were a
lender, a first slip would make me… only slightly more cautious than the
base rate already warrants.* Not a decision-changer on its own.

## T2 — attrition by attribute: passes the letter of a test that was mis-built; economically irrelevant

Two pairs meet the frozen mechanics (plant type: Wind Offshore vs
"Energy Storage System; PV Array", and PV Array vs the same; ratio ≥ 2 on
the name-keyed table, direction confirmed in the Project-ID window). But
the numbers show the test measuring the wrong thing:

- name-keyed "disappearance" over 2014–2025 runs **72–86 % for every
  status**, including *Built* (81 %) — that is identity churn across the
  register's three naming eras (F-2), not withdrawal;
- in the Project-ID-keyed 13-month window, where renames cannot split
  identities, overall disappearance is **3.9 %**, and the "confirmed" pairs
  are 8.6 % and 7.5 % against 7.2 % — differences of one to two points;
- the low-attrition stratum ("Energy Storage System; PV Array") is a
  vocabulary that exists only from ~2022, so it is younger by construction:
  the effect is age, not technology.

The outcome as declared cannot distinguish withdrawal from a rename or a
completed connection, and the materiality bar was applied to the
contaminated key. That is an instrument-eligibility failure of my own
declaration (L11, first-hand). **No decision sentence can be completed.**
Recorded as a test defect; not rescued with a new variable.

## Not run, deliberately

Q4–Q7 (dependency concentration, upsizing, day-ahead headroom versus
constraint cost, publication revision) and Q8 (Bulgarian node
concentration, parked with F004). One strong survivor is the stop
condition.

## What the corpus has already paid for

One fact worth a decision: **being skipped in the Balancing Mechanism is a
persistent property of a unit, month to month.** It came from three NESO
files the project fetched for a different purpose (001B's skip-methodology
comparison) and never asked this question of. Cheapest next step if
wanted: the exclusion-reason split (dataset #6) to say whether persistence
is locational or behavioural — a new declaration, not an extension of this
one.
