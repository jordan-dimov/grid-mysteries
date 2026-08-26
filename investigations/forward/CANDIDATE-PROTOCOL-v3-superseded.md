# Forward Mysteries — candidate generation and killing, Generator v3

**Declared 2026-08-23, before any candidate was generated.** Supersedes
v1 (`47148d6c…`) and v2 (`9dcabde7…`), both preserved byte-exactly. No
candidate had been generated under either. **This is the final revision
before the generator runs**; further changes must wait for evidence from
a completed batch, not argument.

## Defect in v2: the gradient was wrong-shaped

v2 tested `d(required function)/dt` versus `d(incumbent capacity)/dt`.
**Capacity is deceptive.** Fivefold workload against 20% more
consultants is comfortably absorbable if software makes each consultant
five times more productive; an apparent labour shortage evaporates if
prices rise enough to attract entrants. Headcount is not capacity.

The economically meaningful object is the **marginal cost of absorption
as required workload grows** — and it is measured by *revealed strain*,
not by input counts.

### Revealed strain: what to look for

Rising prices · lengthening queues or turnaround · falling service
quality · rapid hiring · work triaged or refused · customers
internalising work they would rather outsource · emergency automation ·
standardisation pressure · liability or coordination failures ·
unusually high margins attracting entrants.

**If workload rises fivefold and incumbent output rises fivefold at
roughly unchanged price, latency and quality, absorption is healthy —
regardless of headcount.**

### The kill returns one of four values, never a fake number

- **absorption stable** → stop.
- **absorption strain evidenced** → the interesting specimen; continue.
- **absorption strain plausible but not measured** → see below.
- **absorption not determinable** → recorded as such, never converted.

### Plausible strain does not promote indefinitely

A candidate may not sit in "plausible" while deep research accumulates
around it. It gets a **cheap forcing test** first:

> **What observable consequence should already exist if absorption is
> genuinely under strain?**

Then look for *that*, before anything expensive. If the theory is
"specialist grid engineers cannot absorb exploding study volumes", do
not begin with a week of modelling future applications — first ask
whether lead times, salaries, vacancies, consultant pricing or project
delays are already moving. If the symptom is absent, **kill or
downgrade**.

This extends research-leverage into a chain:

> externalisation force → predicted symptom of strain → **cheap forcing
> observation**

## Defect in v2: candidate-selection leakage

v2 did not say how many candidates to produce, which invited the worst
failure available: generate one, dislike it, ask the frozen generator
for another. Human taste re-enters through *selection* even though the
generator is frozen.

**Candidates are therefore produced as a frozen batch.** Before any
candidate is exposed to incumbent-market evidence, the batch file
records: every candidate produced; the evidence used only to justify
generation; externalisation-force tags; the generator's ordering; and
**the order in which absorption kills will be run**. Nothing is added,
removed or reordered afterwards.

That converts the experiment from *"can we find a good F002?"* into
**"what distribution of candidates does Generator v3 produce?"** — which
is the question actually worth answering.

## Scoring the batch, not the winner

The generator is scored on the **whole batch**:

- 8 of 10 comfortably absorbed → **Generator v3 is weak**, even if
  candidate 9 later becomes a brilliant company.
- 5 of 10 showing measurable strain → **enormously interesting**, even
  if all five resolve without creating standalone businesses.

Because in that case the generator has learned to locate **economic
systems under adaptation pressure** — and that, rather than "startup
opportunities", is what the machine is fundamentally trying to detect.
From adaptation pressure one can later ask where value accrues: to
software, specialists, incumbents, labour, assets, standards, suppliers
or investors. **The machine does not assume it accrues to a startup.**

## Carried unchanged from v2

Generation biased toward two or three co-present externalisation forces;
the four sought combinations; the exclusion rule scoped to *this
generator* and existing to be scored rather than obeyed; the false
negative log; the kill order; vector scoring `(need, timing, adoption,
capture)`; publication posture for negative studies.
