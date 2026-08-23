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

---

## Amendment 6 — 2026-08-23: four outcomes, and a prohibition on moving the goalposts

**The single most important methodological upgrade to the forward track
so far, and it generalises past F001.**

### F-5 is a chain, not a test

"An adequate solution exists" decomposes into four distinct claims, each
requiring its own evidence:

> **ProvisionExists ≠ ProvisionPurchased ≠ AdequateFor(actor, decision,
> time) ≠ MarketSaturated**

A product page establishes only the first. The ABL mandate (Working note
3) was stronger evidence than any website because it evidenced
**purchase**. This chain is now the standard F-5 must be argued against.

### Four commercially distinct outcomes

The track had implicitly assumed one interesting answer — an unserved
need. There are at least four, and they are not ranked by desirability:

- **White space** — the problem is real and nobody meaningfully serves
  it.
- **Category emergence** — real, and the first specialised providers
  have just appeared.
- **Workflow transition** — already served manually, with
  standardisation or software beginning to displace bespoke work.
- **Efficiently served** — real, but incumbents solve it well. *No
  opportunity demonstrated.*

**Category emergence may be the strongest signal of the four**, and this
is the counter-intuitive part worth stating plainly. Pure white space is
ambiguous: perhaps nobody built it because nobody wants it. But if
several small firms have independently converged on the same obscure
friction while the structural driver accelerates, that is *the future
leaking into the present* — a prediction being confirmed by other
people's capital allocation rather than by our argument.

### The prohibition

**The study may not narrow its definition of the problem in order to
restore a gap after F-5 bites.** Each time an incumbent is found, the
honest move is to update the outcome classification, not to redraw the
boundary until white space reappears. That failure mode — endlessly
moving the goalposts — would let the forward track manufacture the
conclusion it wants, which is precisely what it was built to prevent.

### The forcing question, restated

Replacing "is there a gap?":

> **Is F001 observing a category close to its birth, or rediscovering
> one already established?**

Measurable, and therefore falsifiable: when the products appeared;
evidence of customers; funding and headcount; number of transactions;
pricing; whether major technical advisers are building this internally;
whether buyers procure *continuous monitoring* or only transaction DD;
and whether Gate 2 reform is visibly moving demand.

**If five mature vendors with hundreds of customers exist, F001 dies
completely.** If instead there are two or three young firms, some AI
entrants, traditional advisers still working manually, and regulation
increasing the information burden, the finding is a category near birth
— which is a better result than an empty market, and a different kind
of publication.

## Working note 4 — 2026-08-23: incumbents, and a public-as-of problem

**These observations are dated 2026-08-23 — one day AFTER F001's
declared public-as-of cutoff — and are pinned in
`evidence/post-cutoff-manifest.json`, deliberately separate from
`public-as-of-manifest.json`. They are NOT admitted to the 22 August
evidence set.** Folding them in quietly would make the public-as-of
claim theatre; this separation is the discipline actually working, at
the first moment it cost something.

**Observed (post-cutoff).** **Cairnel** (cairnel.co.uk) markets
"Independent evidence for UK grid projects": *Gate 2 Assurance* for
portfolio holders with active obligations, and *Project Monitoring* of
named projects. Features listed include milestone and evidence control,
**public/private discrepancy detection**, regulatory change mapped to
named projects, portfolio and transaction assurance reporting, verified
alerts with evidence trails, and **four evidence states** (confirmed
change, no evidence found, coverage gap, conflict). Named buyer
categories: project owners and developers, infrastructure investors,
lenders and transaction teams, law firms, grid consultants. Advertised
pricing: £3,600/yr (Monitor, ≤20 projects), £7,200/yr (Adviser),
£15,000+/yr (Enterprise). Adjacent software: **Noda**, **Tetrax**,
**Cepter**. Separately, **Natural Power** has described advising Alpiq
on a multi-country BESS portfolio by assessing project maturity and
assigning a **probability of successful delivery** including
grid-connection requirements.

**This is close enough to F001's forming hypothesis to be treated as an
adverse F-5 candidate**, including the time-varying element the study
had isolated as its sharpest object.

**Pre-cutoff existence: partly established.** The site lists dated
issues for weeks of **7 July, 11 July, 14 July and 1 August 2026**,
which evidences that the *operation* existed before 22 August. It does
**not** establish that every currently advertised feature existed then,
and that distinction is preserved rather than smoothed over.

**Purchase: not established.** The page states **no case studies, no
testimonials and no named clients**. Under Amendment 6's chain this is
`ProvisionExists` — and, on public evidence, not yet
`ProvisionPurchased`. It kills "nobody has built this". It does not
establish that anyone buys it, that it works, or that the market is
served.

**Provisional classification: category emergence**, not white space and
not efficiently served — held as a classification under test, with the
measurements of Amendment 6 as the way to settle it.

## What F001 may be becoming

Recorded so the shift is visible rather than retrofitted: F001 looks
increasingly likely to **fail as a startup thesis and succeed as a
category-discovery experiment**. The causal reasoning predicted a
friction; independent entrepreneurs appear to have found fragments of
the same friction; the structural driver is still accelerating. If that
holds, the publishable result is not "here is a business" but:

> A new infrastructure market is forming around something most people do
> not yet treat as an asset attribute — the quality and durability of a
> grid connection.

That is a legitimate outcome under the declaration, and arguably a
better demonstration of the method than a business idea would have been.
It is **not yet earned**.

---

## Amendment 7 — 2026-08-23: correcting Amendment 6's own overclaim

Amendment 6 said that several small firms converging on the same
friction is "a prediction confirmed by other people's **capital
allocation**". **That is too strong, and it is my overclaim to fix.**
Firms existing is founder attention. It is not investment, and it is
certainly not purchase:

> **FounderAttention ≠ InvestorCapital ≠ BuyerSpend ≠ RepeatBuyerSpend**

All four are signals; they are not the same signal, and the weaker may
never be promoted into the stronger. Amendment 6's four-outcome
taxonomy and its prohibition on narrowing both stand unchanged — only
the strength claimed for supply-side evidence is corrected. The
promotion rule is now written into `STAGE-TEST.md`.

## Amendment 8 — 2026-08-23: the stage test is declared before it is run

The "birth or rediscovery?" question introduced in Amendment 6 was
itself movable: nothing fixed how it would be answered, so the answer
could have been fitted to whatever was found. It is now pre-declared in
**`STAGE-TEST.md`** (frozen, digest
`6d36070a57ed3e5dcc4d905d702d39e528a1f1b4b8116fafb0e14d7e1db613fc`),
written **before any stage research was performed**.

Three substantive changes to what Amendment 6 proposed:

- **The arbitrary threshold is gone.** "Five mature vendors with
  hundreds of customers" was falsifiable but wrong-shaped for a market
  of few, high-value transactions. Replaced by a **nine-stage ladder**
  (latent problem → vocabulary → specialist supply → buyer
  experimentation → repeat procurement → budget line → standardisation
  → incumbent absorption → mature market), each with its own required
  evidence class.
- **The denominator is penetration of the addressable workflow**, never
  vendor or customer counts. Ten providers serving 70% of relevant GB
  transactions is a different world from ten serving 2%; where
  penetration is not estimable, that is recorded as not determinable.
- **Two clocks are separated.** *Knowability* (public-as-of) protects
  the prediction and still limits what F001's thesis may rest on.
  *State-of-world* governs the stage measurement: facts about the world
  on or before 22 August are admissible however late they are
  discovered, provided their date is independently established. Facts
  about the world *after* the cutoff are outcome data for a later
  reassessment, not inputs here. This distinction is what lets the
  quarantined post-cutoff findings be used honestly — as **leads**
  telling us where to look, never as improvements to what F001 knew.

## Amendment 9 — 2026-08-23: what the discovery machine is actually for

Recorded because it changes the machine's objective, not just F001's.

The machine should not search primarily for **white space**. It should
search for **category phase transitions**:

> structural pressure → repeated pain → specialist solutions → repeat
> procurement → standard category

The highest-value observation is not "no competitors" but:

> **the world has moved from repeated pain to specialist solutions, and
> has not yet recognised that this is becoming a category.**

That enlarges the output space well beyond "a startup idea": build one
of the emerging providers, invest in the best, supply infrastructure
underneath all of them, identify upstream and downstream beneficiaries,
create the standard or benchmark, acquire scarce complementary data, or
simply predict which incumbents must eventually buy or build the
capability.

Stated as the objective: **find economically important categories after
necessity becomes structurally visible, but before procurement becomes
routine.**

### The structure F001 is forcing, watched but not yet proposed

Consistent with the rule that vocabulary is discovered, not designed,
the transitions above appear to want distinct evidence predicates —

`EvidenceOfProvision → EvidenceOfPurchase → EvidenceOfRepeatPurchase →
EvidenceOfStandardisation → EvidenceOfPenetration`

— with the kernel **refusing to let one be promoted into another**.
That is the same class of error as `AdequateFor` in Amendment 4, and the
same class humans make constantly. It is recorded as a candidate, and
will be proposed only if F001 actually forces it.

## Next work, deliberately narrow

**Determine F001's category stage as of 22 August 2026**, under
`STAGE-TEST.md`. Not another product hypothesis; not another narrowing.
Hunt specifically for purchase → repeat purchase → recognised budget
line → standardisation → incumbent absorption: named mandates, multiple
transactions using the same capability, lender or IC requirements,
procurement scopes, recurring monitoring contracts, internal teams and
job specifications, and category terminology used **independently by
buyers rather than vendors**.

The post-cutoff findings stay quarantined throughout.

---

## Amendment 10 — 2026-08-23: the frozen instrument was defective, and is replaced before use

`STAGE-TEST.md` v1 was frozen at digest `6d36070a…` and is preserved
byte-exactly as `STAGE-TEST-v1-superseded.md`. **No measurement was
taken under it.** Replacing an instrument before it is used is an
instrument correction; replacing one after seeing results would be
result-fitting, and is not what happened here. The distinction is the
whole reason the timing is recorded.

**The defect.** v1 assigned "the highest stage for which the required
evidence class is met" on a 0–8 ladder. That forces a single ordinal and
assumes category formation is monotone — that later stages presuppose
earlier ones. It does not. A regulator can standardise an evidence
format before commercial purchasing exists; an incumbent can absorb a
capability before specialists appear; lenders can repeatedly buy work
inside generic technical DD for years while no category vocabulary ever
emerges. Each is a legitimate state v1 could only mis-record.

**The replacement.** v2 measures **eight independent axes** — problem
recognition, specialist supply, buyer spend, repeat spend,
institutionalisation, standardisation, penetration, incumbent absorption
— each scored from its own evidence, with **no axis inferable from
another**, and *not determinable* preserved as a legitimate answer. The
nine-stage language survives only as human shorthand with no authority
over the result.

## Amendment 11 — 2026-08-23: three clocks, and visibility lag as a finding

v1 separated two clocks. Operationally there are **three**, and every
material fact needs all of them:

- **t_event** — when it happened;
- **t_public** — when it became publicly knowable;
- **t_discovered** — when we found it.

A September case study saying "we have been buying since March" has
t_event March, t_public September, t_discovered October. It is
legitimate evidence for *what the market was doing in August*; it is not
evidence that an observer *could have known* in August.

So the study now produces **two profiles, always reported together**:
`CategoryStateActual(2026-08-22)` using any evidence with t_event ≤
cutoff, and `CategoryStateObservable(2026-08-22)` restricted to t_public
≤ cutoff.

**The gap between them is visibility lag, and it is a first-class
finding rather than an error.** If a later disclosure shows the category
was further along than it appeared, that does not mean F001 failed — it
may mean F001 detected the category *from public information before
buyer activity became publicly visible*, which is more interesting than
merely being early. F001's own thesis may rest only on the observable
profile.

## Amendment 12 — 2026-08-23: what the machine is actually hunting

Superseding the "category phase transitions" formulation of Amendment 9
with something sharper. Four curves move through time:

- **N(t)** — structural necessity;
- **A(t)** — actual adoption;
- **V(t)** — visible or recognised adoption;
- **C(t)** — capital and competitive response.

The states that matter:

| pattern | reading |
|---|---|
| N↑, A≈0, V≈0 | white space — **ambiguous**: opportunity, or nobody cares |
| N↑↑, A↑, V→ | **emerging category** — reality has begun forcing it, the closest buyers have begun paying, the wider market has not noticed |
| N↑, A↑, V↑ | mature — too late |

The target is the middle row, and **RepeatBuyerSpend is the key
instrument** because it evidences that A(t) is moving for reasons
stronger than founder enthusiasm. Adding the fourth curve: if buyers are
quietly beginning to spend while funding, incumbent hiring and public
attention remain low, the window is at its most interesting.

The machine's objective, stated precisely enough to be operational and
replacing "predictability × value":

> **Find domains where necessity leads adoption leads recognition leads
> capital, and the lag between those curves is unusually large.**

Equivalently, the question F001 is building an instrument to answer
repeatedly:

> **Has economic reality begun moving before the evidence visible to
> most observers says that it has?**

## Next work, unchanged in scope

Determine F001's **CategoryStateActual** and **CategoryStateObservable**
as of 2026-08-22 under `STAGE-TEST.md` v2, axis by axis, with all three
timestamps recorded for every material fact. Post-cutoff findings remain
quarantined and may be used only as leads and as t_event evidence with
established dates.

---

## Amendment 13 — 2026-08-23: three candidates recorded, instrument untouched

Recorded as **candidates forced by the study**, deliberately **not**
built into `STAGE-TEST.md` v2. The instrument is now good enough to use,
and further improvement must earn its way out of evidence rather than
out of argument. F001 measures next.

**Candidate A — a third epistemic state.** Beyond
`CategoryStateActual` and `CategoryStateObservable` there may need to be
`CategoryStateInferred(T | E≤T)`: what the machine *concluded* at T from
evidence public by T. If no buyer purchase is publicly disclosed, yet
suppliers exist, incumbents hire, regulatory pressure rises and
terminology converges, the machine may legitimately infer high
probability of adoption already occurring. If disclosures six months
later confirm it, the demonstrated property is **inference preceded
disclosure** — a far stronger claim than "the information was not
public". The eventual scorecard: *what was directly knowable, what did
we infer, what was actually true?*

**Candidate B — necessity of the problem ≠ necessity of the category.**
The four curves start with N(t) as though structural necessity implies a
market. It does not. What becomes necessary is a **function**, which the
economy may satisfy through developers internally, incumbent advisers,
lenders' existing DD teams, NESO, transaction lawyers, software, a new
specialist category, or any mixture. So `N_P(t)` (necessity of solving
the problem) must be separated from `S(t)` (how the economy chooses to
solve it), and only under some conditions does S(t) externalise into a
category. This guards against a seductive inference the study is
currently exposed to: *this problem must be solved, therefore somebody
will build a big business solving it.* **Not necessarily** — the system
often absorbs a new function into an existing job almost frictionlessly.
The open question worth eventually modelling: *what causes a newly
necessary function to externalise into its own category rather than be
absorbed?* Likely factors: cross-organisational coordination, specialist
data, repeated workflow, independence requirements, liability,
standardisation, economies of scale.

**Candidate C — C(t) bundles incompatible things.** Founder capital,
venture funding, incumbent capex and market-price recognition are not
interchangeable. For business discovery, competitive capital matters;
for investment discovery what matters is closer to `P(t)`, the degree to
which the consequence is **already priced**. A category can be detected
very early while its one listed supplier trades at 80× earnings — great
forecast, terrible investment — or be well recognised while an obscure
upstream supplier stays mispriced. The mature chain is therefore
necessity → adoption → visibility → competitive response → **price
incorporation**, with different opportunities living in different gaps.

## The search target, restated

Superseding Amendment 12's formulation with the sharper version these
candidates imply:

> **Find economically necessary functions whose real adoption is
> beginning to outrun their public visibility, then determine whether
> the resulting value will form a new category, be absorbed by
> incumbents, or create a mispriced dependency elsewhere.**
