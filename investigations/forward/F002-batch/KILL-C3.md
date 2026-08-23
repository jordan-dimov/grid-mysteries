# C3 — Grid Code compliance evidence for inverter-based resources

**Run**: 2026-08-23, shallow, after the commercial redirect.
**Verdict**: **absorption strain plausible but not measured** — same class
as C6, but with a sharper structure: **the unit cost of failure is
published; the failure rate is not.**

## The mechanism, first-party from NESO's own FAQ

- Users must submit models 3 months before ION and 1 month before LON.
- NESO aims to give feedback on the **first** submission in **3–4 weeks**.
- **"each re-submitted or revised model will be treated as a new
  submission. NESO requires three weeks (15 working days) to validate
  each revised model."**
- Failure gates energisation: **"If a model is rejected multiple times due
  to non-compliance, the responsibility for any delays in issuing the
  ION/FON rests on the customers."**

So compliance is a **serial re-validation loop with a published 15-working-day
quantum per iteration, sitting directly on the revenue-start date.** Each
failed iteration costs a project three weeks of energisation.

Volume is rising by construction: GC0141 and GC0168 require
manufacturer-validated EMT models, and GC0168 seeks **retrospective**
submissions from connections commissioned before September 2022 — a stock
of legacy work on top of the flow.

## What is not measured

The **iteration count**. NESO publishes the cost of a rejection and not
the rejection rate. That institutions write a whole FAQ entry about
repeated rejection, and assign blame in it, is suggestive — but L9 applies:
process language is not a measurement.

Corroboration exists but is **vendor voice** and is treated as such under
the C5 rule: consultancies report that power system studies are now a
critical path item, that OEMs are often new to PSCAD with limited in-house
expertise, and that vendor model problems cause "delays, rework and cost
overrun". Useful as a signal of where the pain is claimed to be. Not
evidence.

## Already-externalised check (the C5 lesson, run early)

The function **has** partly externalised — to consultancies (Aurora Power,
and the wider power-systems advisory market). But it externalised as
**expensive human judgement sold by the day**, not as a product. No
standardised instrument, no benchmark, no index. This is the opposite of
C5's endpoint: the category left the incumbent and then stopped.

## Why this one is different for us

C3 is the first candidate in the batch matching the stated commercial
prior directly: an expensive decision made by scarce specialists over
fragmented data (OEM models, network models, tool and compiler versions),
whose frequency is rising with every connection, where the information is
not trustworthy enough for software, and where failure has a published
price in weeks.

## Sources (accessed 2026-08-23)

NESO, *EMT Model Requirements FAQ* (`neso.energy/document/377131`),
fetched and extracted locally — submission timelines, 3–4 week first
review, 15 working days per revision, ION/FON responsibility. NESO Grid
Code compliance process pages; GC0141 and GC0168. Aurora Power Consulting
(vendor voice, corroboration only).
