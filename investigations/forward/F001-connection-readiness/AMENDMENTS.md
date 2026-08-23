# F001 — amendments and working notes

`DECLARATION.md` is frozen at public-as-of 2026-08-22 and is never
edited. Everything that changes after it is written here, with dates, so
the difference between what was declared and what was learned stays
visible.

---

## Amendment 1 — 2026-08-22: a date is not a falsifier

**Recorded before any layer-2 or F-5 evidence was analysed.**

The declaration says the closing of Ofgem's consultation on 16 September
2026 gives the study "a hard, dated falsification point: what Ofgem
actually decides." **That is wrong, and the error matters more than it
looks.** Ofgem's consultation informs subsequent policy decisions; the
proposals do not become true or false when the window shuts. Treating a
scheduled information event as a falsifier lets a date masquerade as
evidence — precisely the sleight-of-hand a prediction record exists to
prevent.

Corrected structure:

- **16 September 2026 is a pre-declared reassessment checkpoint.** On
  that date the study revisits its evidence and records what changed. It
  refutes nothing by itself.
- **F-1 is restated as an outcome test, not a date test.** The study's
  central argument is refuted if the final policy **materially removes
  the progression-evidence requirement**, or if the required evidence
  **turns out to be satisfiable trivially through existing
  network-operator processes**.

The declaration's other four falsifiers stand unchanged.

## Amendment 2 — 2026-08-22: reorder by information value, not by layer number

**Recorded before any layer-2 or F-5 evidence was analysed.**

The declaration lists five layers "in order". Completing them
mechanically would spend the study's effort where it has least
information value. Layer 1 is close to settled already: Ofgem proposes a
commitment fee and data-centre-specific queue-management milestones
requiring evidence of credible end-users, long-lead equipment
procurement, and financial and technical capability, and NESO already
runs an evidence-based Gate 2 process. Proving harder that "readiness
evidence is becoming important" adds almost nothing.

The work therefore proceeds as: **close layer 1, then attack layer 2 and
F-5 together.** The ordering constraint that remains binding is the one
that matters — **no opportunity may be named before layer 5's three
propositions are each earned** — not the sequence in which evidence is
gathered.

**Layer 2 is reframed as an evidence-burden decomposition.** For each
proposed readiness requirement: what evidence object proves it; who
originates it; who can verify it; is it confidential; how often does it
change; what is its lead time; what happens when it fails; **can the
network operator verify it directly**; and is somebody already doing
this. The last two are the questions most likely to kill the study, so
they are asked first rather than last.

Three worlds are held open deliberately, and the study tries to discover
which one it is in rather than to confirm any:

- **A — it is paperwork.** Contracts and declarations handed to the
  network operator; existing consultants absorb it. Interesting
  regulation, poor business.
- **B — it is ongoing evidence coordination.** Evidence originates
  across end-users, OEM procurement, financing and engineering
  workstreams, changes over time, and is commercially sensitive;
  somebody must assemble an audit-ready picture and keep it current.
- **C — the binding pain is financial, not evidential.** If the
  commitment mechanism is what actually hurts, the opportunity is
  guarantees, insurance or underwriting rather than software or
  assurance.

## Amendment 3 — 2026-08-22: the buyer hypothesis is widened

**Recorded before any layer-2 or F-5 evidence was analysed.**

The declaration implicitly frames the compelled party as the developer
satisfying Ofgem. That may be the least interesting buyer. If queue
position becomes contingent on demonstrated progression, **credibility
becomes an attribute of the asset**, and the parties who need it
measured include the lender deciding whether a connection assumption is
bankable, the investor or acquirer buying the project, the end-user
signing capacity, the infrastructure fund valuing a pipeline, and the
OEM relying on procurement milestones.

The candidate stronger thesis, recorded now as **a hypothesis and not a
finding**, so that its later status is checkable:

> Britain is turning grid connection readiness into a measurable project
> attribute, but the parties financing and acquiring those projects
> still lack a reliable way to diligence it.

F-5 applies to this formulation with full force, and the buyer-workflow
reconstruction must cover these parties, not only developers.

---

## Working note 1 — 2026-08-22: the first F-5 signal is adverse

Pinned: NESO's Gate 2 / G2WQ evidence resources page
(`evidence/public-as-of-manifest.json`).

**Observed.** NESO already operates an evidence-based readiness process
with its own instruments: a **Readiness Declaration** form, pro forma
templates for **Secured Land Rights** (including leases under 20 years
and authority-to-sign), an **Evidence Submission Handbook**, "Customer
Guidance Essentials" and "Detailed Checks Guidance", submitted through
the existing connections portal. **Assessment is performed by NESO, DNOs
and IDNOs.** The Connections Reform Evidence Window closed 23:59 on
11 August 2025, with a subsequent validation process for submitted
evidence.

**Why this matters, stated plainly.** The declaration's F-5 asks whether
an adequate solution already exists. The immediate answer is not a
competitor — it is the **network operator itself**, which originates the
forms, receives the evidence and performs the checks. "Can the network
operator verify it directly?" is the question flagged as capable of
destroying a service thesis, and the public record's first answer is
that it substantially does.

**Not yet determined.** Whether that process covers the *new*
data-centre-specific requirements Ofgem proposes (credible end-user,
long-lead procurement, financial capability); whether it serves the
wider buyers of Amendment 3 at all, or only NESO's own allocation
decision; and whether developers or financiers experience any residual
burden it does not address. Those are the live questions, and this note
records only that the study starts from an adverse position on F-5
rather than a hopeful one.

---

## Amendment 4 — 2026-08-22: adequacy is a relation, not a property

**Recorded before the buyer-workflow reconstruction was attempted.**

Working note 1 treated F-5 as though "an adequate solution exists" were
a property of a solution. It is not. **Adequacy is a relation between a
provision, an actor, a decision, and a time.** NESO's process can be
entirely adequate for the decision it was built to make — *should this
project hold a place in the connections process?* — while saying nothing
about whether it is adequate for a different actor making a different
decision: *should I lend £150m against this?*, *what should I pay to
acquire it?*, *which 500 MW of this 3 GW pipeline is credible?*

Both of these can be true at once, and the study must be able to hold
them simultaneously:

- `AdequateFor(NESO process, NESO, queue allocation)` — plausibly yes.
- `AdequateFor(NESO process, lender, credit decision)` — **not
  established either way**, and that is the live question.

This is the first structure F001 has *forced* rather than invented, and
it is the correction to a common analytical error — "there is already a
solution", with no answer to *for whom, to make what decision*. It is
recorded here as discovered vocabulary; whether it becomes programme
vocabulary waits until the study is done.

## Working note 2 — 2026-08-22: what an external party can actually observe

Pinned this session: NESO's **TEC Register** and **Embedded Register**
(`evidence/public-as-of-manifest.json`).

**Observed.** The public TEC Register carries 2,198 rows and exposes:
Project Name, Customer Name, Connection Site, Stage, MW Connected, MW
Increase/Decrease, Cumulative Total Capacity, MW Effective From, Project
Status, Agreement Type, HOST TO, Plant Type, Project ID, Project Number,
and **Gate**.

So a readiness signal *is* public — the Gate field. Its coverage:

| Gate | projects | capacity | share of register capacity |
|---|---:|---:|---:|
| 2 | 83 | 12,005 MW | 2.0% |
| 1 | 733 | 268,691 MW | 44.6% |
| *blank* | 1,382 | 321,776 MW | 53.4% |
| total | 2,198 | 602,473 MW | |

**Supported inference.** The closest thing to a public readiness marker
is present but thin: **blank for 53% of registered capacity**, and only
2.0% of capacity carries Gate 2. An external party can observe *that* a
project reached a gate; it cannot observe from this source what evidence
was supplied, when it was assessed, whether it still holds, what
exceptions applied, or what has changed since.

**Not publicly determinable from this source.** Why a Gate value is
blank — pre-reform vintage, not yet assessed, or not applicable to that
agreement type — is not distinguishable in the register, and is not
assumed here.

**What this does and does not support.** It supports the claim that the
register publishes an *outcome* rather than the *evidence or its
currency*. It does **not** yet establish that capital providers
experience a material information gap: they may obtain the underlying
evidence directly from developers in a data room, which is precisely
what the buyer-workflow reconstruction must test. Three plant types
dominate the register by capacity — energy storage (176.9 GW), storage
co-located with PV (139.3 GW) and offshore wind (86.8 GW) — which also
tests Amendment 3's suspicion that the question generalises well beyond
data centres.

## The provisional thesis, restated — 2026-08-22

Superseding the formulations in the declaration and Amendment 3.
Recorded as **a hypothesis under test**, not a finding:

> As GB grid capacity becomes allocated partly on evidence of project
> progression, the quality of a project's connection position comes to
> depend on facts that can change over time. The network operator's
> verification is designed for its own allocation decision, not
> necessarily for the capital providers who must value and rely on that
> position. **Does that create a material information gap around the
> bankability and transaction value of grid connections?**

If the answer is **no**, F001 has still succeeded: it will have killed a
superficially attractive thesis before anyone spent money on it. If
**yes**, the natural next question is whether connection quality is an
under-measured asset attribute across generation, storage and large
demand projects generally — which the register's composition above
suggests is worth asking.

**Next, in order of information value:** (1) does NESO's verification
leave the project holding a reusable artefact, or only "NESO knows we
passed"; (2) what a financier or acquirer can independently reconstruct;
(3) whether readiness persists or decays — `R(project, t)` rather than
`Ready(project)`; (4) whether anyone already sells the *external
decision layer*, tested by evidence of purchase (mandates, DD scopes,
deal announcements, job specifications) rather than marketing copy.

---

## Amendment 5 — 2026-08-22: the object is evidence portability, and the test narrows to one decision

**Recorded before the incumbent-market probe below.**

F001 has surfaced a sharper object than "readiness". Three things that
the study had been running together must be separated:

> **verified outcome ≠ underlying evidence ≠ decision-grade evidence**

NESO may hold enough evidence for *its* decision; the developer may hold
enough to satisfy NESO. Whether that evidence is **portable across
decisions and across time** is the open question. A lender needs to know
what was actually evidenced, which party supplied it, whether it remains
true, what NESO assumed, whether later events weakened it, and what
follows if it fails.

Relatedly, the economically interesting quantity is not `Gate2(project)`
but something closer to `Gate2(project, assessed_at=t₀)` combined with
facts at t₁ — end-user changed, procurement delayed, land rights
changed, milestone missed — i.e. **P(connection survives | evidence at
t)** rather than a static flag. **If readiness deteriorates materially
between formal assessments, the currency of evidence may be worth more
than the original verification.** That is a testable proposition and is
now on the list.

**The test narrows to one concrete decision**, rather than "how
investors diligence connections" in general:

> A fund is considering buying a development-stage GB BESS project
> tomorrow. What exactly must its investment committee and lender
> establish about the connection before paying for it?

BESS is chosen because the connection can be a large share of
development value, transaction activity is high, and the pinned TEC
register shows storage is the largest single population (176.9 GW, plus
139.3 GW co-located with PV). For each artefact in the chain — offer,
Gate status, land and readiness evidence, milestones, correspondence,
technical assumptions, modification history, termination risk, DD
opinion — the study asks: does the buyer receive it, from whom, how
current is it, can it be independently checked, who checks it today, and
what does failure cost.

## Working note 3 — 2026-08-22: F-5 first pass, and it bites

**Instrument: a single web search of public marketing and news pages.
This is a weak instrument and is labelled as such.** It cannot establish
scope, price, frequency or adequacy, and no conclusion below rests on it
alone.

**Observed.** Grid connection review is already a **standard line item
in commercially available BESS technical due diligence**, sold by
multiple established firms to investors and lenders. Phase 1 technical
DD is described as covering site review, plant design, contracts,
operational concept, route to market, **grid connections**, planning
approvals and financial model review. At least one documented
**mandate** exists rather than mere advertising: ABL Group announced
appointment as **lender's technical adviser to a UK BESS portfolio**.
Others advertising BESS DD for investors and lenders include
SgurrEnergy, Sinovoltaics, 3E and Solarif.

**What this establishes.** The naive form of the opportunity — "nobody
assesses grid connections for investors" — is **dead**. An incumbent
advisory workflow exists, is purchased, and includes the connection.
F-5 was correctly flagged in the declaration as the falsifier most
likely to fire, and on first contact it fires against the naive
formulation.

**What this does not establish**, and must not be allowed to drift into:
whether that review addresses the *durability and currency* of the
connection position — the object Amendment 5 isolates — or whether it is
a point-in-time desktop read of the connection offer and its dates.
"Review of grid connections" in a Phase 1 scope is compatible with
either. Marketing pages are incapable of settling it.

**Consequence for the study.** The live question is no longer whether
the need is served, but the one the incumbent pattern suggests:

> **Which parts of a repeated, data-intensive, poorly standardised
> advisory workflow are capable of becoming infrastructure?**

That is a different and arguably better proposition than an unserved
need, and it has its own evidential bar: it requires showing the work is
*repeated and fragmented*, not merely that it is expensive. The
progression to watch is consultancy → repeated methodology →
standardised evidence model → data infrastructure; being early at the
middle transitions is where value would sit, and F001 has not yet
established which transition GB is at.

**Better instruments needed**, in descending order of strength: actual
technical-DD and lender-adviser scopes of work; investment-committee
requirements; job specifications naming connection-position assessment;
transaction announcements naming grid advisers; vendor DD pack contents.
Evidence of *purchase and repetition*, not of *offering*.

## Recorded but not adopted — the larger prize

If — and only if — the study earns its propositions, the eventual
category would not be data-centre readiness assurance but
**connection-quality intelligence** for any asset whose economics depend
on a scarce connection: storage, offshore and onshore wind, solar,
electrolysers, large industrial load, data centres. The asset attribute
set would gain something like *connection confidence / durability*
alongside MW, COD, technology, location and lease status.

**F001 has not earned this and it is recorded only so that it cannot
later be presented as a finding that emerged from evidence.**
