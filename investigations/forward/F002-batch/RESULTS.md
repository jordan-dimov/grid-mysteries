# Batch 01 — kill results

Batch frozen at `5f352ebb096b6194571732bed281623879038d9c156b70fb6b36c2f6f80ba8a6`.
`BATCH-01.md` is never edited; results accumulate here.

**Batch complete, 2026-08-26.** C5, C1, C6, C7, C3 were run on 2026-08-23.
The remaining five (C8, C10, C9, C4, C2) were researched concurrently on
2026-08-26 for speed and are recorded in the frozen order; each ran only its
own frozen forcing observation, blind to the others and to the commissioned
studies F003/F004. Generator v3 was not modified at any point.

| # | Candidate | Verdict | Record |
|---|---|---|---|
| C5 | Constraint/curtailment settlement reconciliation | **absorption stable** (externalisation already completed) | [KILL-C5.md](KILL-C5.md) |
| C1 | MHHS settlement data quality assurance | **absorption stable** (transition mistaken for structural change) | [KILL-C1.md](KILL-C1.md) |
| C6 | Small flexible asset prequalification/delivery | **strain plausible but not measured** → downgraded, blocked on non-public data | [KILL-C6.md](KILL-C6.md) |
| C7 | TO/DNO outage and access coordination | **absorption strain EVIDENCED** | [KILL-C7.md](KILL-C7.md) |
| C8 | DNO→DSO whole-system asset visibility | **not determinable** (two of three symptoms unobservable by construction; the measurable one leans stable) | [KILL-C8.md](KILL-C8.md) |
| C3 | Grid Code compliance for inverter-based resources | **strain plausible but not measured** (unit cost published, failure rate not) | [KILL-C3.md](KILL-C3.md) |
| C10 | Grid/consent evidence for large new demand | **strain plausible but not measured** → downgraded (instruments type-blind; adviser absorption of the new NSIP route observed) | [KILL-C10.md](KILL-C10.md) |
| C9 | Granular clean-energy claim verification | **strain plausible but not measured** → downgraded (spend unobservable; transient IT strain only; forcing standard slipped to 2027–28) | [KILL-C9.md](KILL-C9.md) |
| C4 | BESS degradation and warranty verification | **strain plausible but not measured** → downgraded (disputes private; insurers exclude the peril; one in-house purchase) | [KILL-C4.md](KILL-C4.md) |
| C2 | Post-Gate-2 connection evidence (**quarantined**) | **strain plausible but not measured** → downgraded; resolving series (CMP448 activation metric, 0 MW on 3 Aug 2026) next publishes 1 Feb 2027 | [KILL-C2.md](KILL-C2.md) |

## Score, exactly as pre-declared in `BATCH-01.md`

C2 is quarantined and excluded. Of the **nine** counted candidates:

- absorption strain **evidenced**: 1 (C7)
- strain **plausible but not measured**: 5 (C6, C3, C10, C9, C4)
- absorption **stable**: 2 (C5, C1)
- **not determinable**: 1 (C8)

**Evidenced or plausible: 6 of 9.** Against the declared thresholds (≤2
weak; 3–4 doing something weakly; ≥5 "locates economic systems under
adaptation pressure"), **Generator v3 clears the top threshold.**

That is the pre-declared result and it stands. The following is
interpretation, recorded separately so the score is not quietly rewritten:

**The declared scale cannot tell instrument failure from candidate signal.**
Five of the six "hits" are *plausible but not measured*, and in every one
the recorded reason is that the frozen instrument could not contain the
predicted symptom — a series that is unpublished (C6, C3, C2, C4-disputes,
C9-spend), an instrument that aggregates the population away (C10), or a
third party that does not bear the relevant risk (C4-insurers). The
declaration's fourth clause ("many `not determinable` → the failure is the
forcing observations") anticipated this pattern but keyed it to the wrong
verdict label: under v3, instrument blindness lands in *plausible*, not in
*not determinable*, because a candidate whose mechanism is real and whose
instrument is blind is by definition "plausible but not measured".
Formally only C8 is *not determinable*; substantively, the batch has one
measured strain (C7), two measured stabilities (C5, C1), and **seven
candidates whose verdict is a statement about the public record rather
than about the economy.** Both readings are true and both are kept: v3
does point at systems under pressure — every "plausible" has a real,
documented mechanism — and v3's forcing observations mostly cannot
measure them.

## Instrument defects, now tallied over the whole batch

Held unapplied until the batch completed, per `../LESSONS-PENDING.md`.

| lesson | recurrences | count |
|---|---|---|
| **L1 · eligibility** — instrument could not contain the failure by construction | C5, C1 (half), C8 (two of three symptoms), C10 (all three), C9 (spend, administration), C4 (insurer pricing measures a different peril) | **6 of 10** |
| **L7 · eligible, unpublished** — the series exists operationally and is not public | C6, C3, C2, C4 (disputes), C9 (admin capacity) | **5 of 10** |
| **L5 · no timing sensor** — adaptation finished, or not yet observable | C5, C1 (finished); C2 (symptom cannot exist before 2027); C9 (forcing standard slipped) | 4 |
| L2 · already externalised | C5 | 1 |
| L4 · transition ≠ category | C1 | 1 |
| L6 · scarce unit of work | C6 | 1 |
| L9 · process adaptation is weak evidence | C6 | 1 |

**Eight of ten candidates had at least one frozen symptom that no public
instrument could register.** That is the batch's dominant finding about
the generator, and it is a finding about *symptom and instrument design*,
not about candidate choice: the incumbent guess was right in every one of
the ten rows.

## Comparison with the commissioned studies F003 / F004

Recorded because the sponsor asked three specific questions before the
batch was completed, and answering them from the completed batch is the
point of having completed it.

**Did v3 surface the data-centre / large-demand family blind?** Yes: C10,
generated on 2026-08-23 before F003 was commissioned.

**Did C10 kill it for approximately the right reason?** Partly. Its
verdict is *plausible but not measured* because its instruments are blind,
not because of an explicit absorption argument — but its reading of the
2026 section 35 record ("providers exist and are visibly being paid … that
is absorption working, and it must not be promoted into buyer pain") is
the correct absorption logic, and it points the same way as F001. C10
never asked the buyer question, and in GB it did not need to: the three
s35 applicants are buyers paying advisers today. So of the three outcomes
the sponsor named in advance, this is closest to the first (v3 found the
family and killed it in the right direction), with the qualification that
the kill was delivered by instrument blindness rather than by reasoning.

**Was lack of buyer evidence a recurrent generator failure, or specific to
one family?** Specific. In eight of the nine counted candidates a paying
buyer class demonstrably exists — usually a regulated or incumbent one
(Elexon, DNOs, NESO, developers paying consultancies, lenders, asset
managers) — and the candidate fails by *absorption* or by *instrument
blindness*, not by absent demand. The one batch candidate with the
F003/F004 shape is C9: the state supplies verification free, and the
standard that would compel spend slipped from 2027 to 2028. The same
forcing variable produced two different failure modes in two markets: in
GB (C10) the large-load consent function is absorbed by advisers whom
buyers pay; in Bulgaria (F003/F004) the buyer does not exist. **The buyer
term is market-specific; the instrument term is universal.**

Consequence for the v4 design, stated as evidence and not yet applied:
the batch supports an **instrument-eligibility gate at freeze time**
(publication existence, type-identifiability, earliest observable date,
risk-bearing of any third-party pricing signal) as the first change, and a
**K0 buyer kill** as a cheap first kill justified by F003/F004 and C9 —
not as a generation filter, and not as the batch's main lesson.

## Three distinct ways a candidate fails — final

| | mechanism | candidates |
|---|---|---|
| absorbed successfully | the incumbent scales, usually as software, and cost per unit falls | C1, C8 (leaning), C10 (advisers), C4 (in-house) |
| already externalised successfully | the function left the incumbent years ago and the category matured | C5 |
| unresolvable from public data | the strain is structurally plausible and the series is not published or cannot exist yet | C6, C3, C2, C9, C4 (disputes) |
| no compelled buyer | the party that would pay is not compelled, or the compulsion slipped | C9 (and, outside the batch, F004) |

None is "no demand". The need was real in all ten. The batch's one
measured survivor, C7, has propositions 2 and 3 (compelled buyer; existing
solutions inadequate) still unearned, and its buyer is a regulated
monopoly with a live reform programme.

## Retrieval limitation for the 2026-08-26 kills

The session's shared web-search budget was exhausted early in the run; C8,
C10, C9, C4 and C2 proceeded by direct fetch of known primary sources
(regulator and operator PDFs, open-data APIs, registry CSVs, Wayback) and
local text extraction. This biases those five records toward first-party
publications and against trade-press or practitioner testimony; each
record says so. No instrument was substituted for a frozen one.
