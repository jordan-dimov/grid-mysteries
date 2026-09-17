# 013 against NESO's forecast: what was found, and why the tracker does not report against it yet

*Job 3 of the session brief of 2026-09-17. Held, not published, and nothing
in 013's declaration, evidence or page is changed by it. The discovery notes
with every URL are in `forecast-discovery-notes-2026-09-17.md` beside this
file. No CSV or XLSX data file was opened; NESO's PDFs and web pages were
read.*

## 1. The figure, as the register holds it, and as its source printed it

The business register holds the forecast second-hand (etrmbiz slot
`neso-balancing-cost-forecast-2026-27`): Montel, 27 July 2026, reporting The
Times — "balancing and constraint costs to rise 45 percent year on year to
GBP 3.2bn over the twelve months from mid-2026, from GBP 2.2bn over the year
to June 2026, with more than 75 percent of the forecast attributed to
limitations in the existing network".

The Times article itself (Emily Gosden and Geraldine Scott, 26 July 2026,
"£3.2bn to switch off power plants when network cannot cope",
`https://www.thetimes.com/uk/politics/article/wind-farms-paid-switch-off-grid-costs-32bn-rz7qx8bc6`,
read via a verbatim repost because the Times site is unreachable from here)
says something narrower than Montel's paraphrase:

> Neso forecasts total **constraint costs** of £3.2 billion over the coming
> 12 months, to July 2027. That compares with £2.2 billion incurred over the
> past 12 months to June 2026 — which came in below Neso's £2.6 billion
> forecast for that period.

> It said that "over 75 per cent of the forecast cost is due to the
> limitations of the current network".

Two corrections to carry back to the slot: the figure is **constraint
costs**, not "balancing and constraint costs"; and the Times attributes it to
"Neso said" and "Neso forecasts", naming **no document, dataset or report**.
The period is "the coming 12 months, to July 2027", which reads either as
August 2026 to July 2027 or July 2026 to June 2027.

## 2. NESO's own publication: not found as printed

No NESO publication prints £3.2bn, 45 percent, £2.2bn or the "over 75 per
cent" sentence. What NESO does publish, and how each relates:

| NESO publication | URL | Dated and archived? | What it says |
|---|---|---|---|
| **24 Months Ahead Constraint Cost Forecast** (data portal dataset) | `https://www.neso.energy/data-portal/24-months-ahead-constraint-cost-forecast` | **Overwritten in place**: one CKAN resource, created 2024-04-02, last modified 2026-09-10, 384 bytes, filename `…_sept26.csv` (earlier captures `_feb25.csv`). Wayback holds page snapshots for 2025-02-19, 2025-06-13 and 2025-12-12 only, and the resource once (feb25). **The July 2026 vintage the Times reported is not publicly recoverable.** | Schema via `datastore_search?limit=0` (no rows read): `Month` (MMM-YY) and `Constraint Cost` ("Modelled constraint cost in £m"), 24 rows, monthly. Definition on the page: the costs of managing thermal, voltage and stability boundaries plus meeting voltage requirements, **excluding** inertia and largest loss of infeed. The most plausible origin of "£3.2bn" is a 12-month sum of this series at its July vintage; that is an inference, not verified, because the vintage is gone and the file was not opened. Both this dataset and its sister (constraint limits) carry a note that column ids changed on 9 September 2026. |
| **BSUoS Forecast Report, August 2026 edition** (the vintage live when the Times ran) | `https://www.neso.energy/document/384581/download`, published 15 Jul 2026 | **Dated and archived** as separate `/document/` PDFs per month (Jun-26 381886, Jul-26 383021, Aug-26 384581, Sep-26 385726) and as per-month CSVs on `data-portal/bsuos-monthly-forecast` (note a `-v2` reissue of September) | 24-month table of Balancing Costs (central, upper, lower), Jul-26 to Jun-28; six-month category split: Energy Imbalance, Positive Reserve, Negative Reserve, Frequency Control, **Constraints**, Other, Restoration. Constraints Jul–Dec 2026: 166.0 / 177.1 / 205.4 / 286.0 / 266.6 / 228.8 £m of monthly totals 251.6 / 255.6 / 281.2 / 359.6 / 342.3 / 306.0 — about 75 % of the total (discovery arithmetic, from the PDF text). The 12-month central total Aug-26 to Jul-27 is about £3,461m (Jul-26 to Jun-27 about £3,455m). The text: "The August forecast is 6% (£14m) higher than the prior forecast published on 15 June (£241m). This change reflects a 9% (£14m) increase in the constraints cost forecast", and "The constraint model was updated in March 2026 to use a new set of boundary limits … derived from the new Year-Ahead plan … Many of the updated limits are lower … due to a challenging outage plan". The report also says "The latest constraints forecast is available on the NESO data portal", pointing at the dataset above. So £3.2bn is **not** this report's 12-month total balancing figure (about £3.46bn), and 75 % of that would be about £2.6bn, not £3.2bn. |
| **BSUoS Outturn, June 2026** | `https://www.neso.energy/document/384586/download`, 15 Jul 2026 | Dated and archived | Monthly Balancing Costs Jul-25 to Jun-26 sum to about **£3,246m** (discovery arithmetic), so "£2.2bn to June 2026" is not total balancing costs; June constraints outturn £155m (May £168m). A constraint run-rate near £180m a month makes £2.2bn plausible as a constraint-component sum, but that sum would have to be computed from data files, not read from a publication. |
| **Monthly Balancing Cost Report, July 2026** | `https://www.neso.energy/document/386501/download` | Dated PDFs per month; "previous months' outturn balancing costs are updated every month with reconciled values" | No forward 12-month forecast. July outturn £302m against a £257m benchmark; "constraint costs" £221.2m (June £232.3m); "thermal constraints currently make up the largest share of balancing costs (~60%)". **Its "constraint costs" (which include Constraints–Ancillary Services, Sterilised Headroom, Scotland/Cheviot and E&W lines) is materially larger than the BSUoS-model Constraints line (£155m for June).** |
| Annual Balancing Costs Report 2025, Operational Transparency Forum 22 Jul 2026 | `/document/362561`, `/document/384776` | Dated | 2024/25 outturn and the 2030 peak; June costs only. Neither carries the Times figure. |
| Monthly Balancing Services Summary | `https://www.neso.energy/data-portal/mbss` | The page now returns 403 / "doesn't exist"; the MBSS data are eight `/document/` XLSX downloads, all re-dated 17 Jul 2026 under unchanged document ids: **overwritten in place** | Not opened. |

NESO's own definitions, quoted: balancing costs are "those expenses
associated with (A) the Balancing Mechanism, (B) balancing services, and (C)
energy trading" (balancing-costs page); the 24-month dataset's constraint
costs are "costs of managing constraint boundaries (for thermal, voltage or
stability constraints) plus the cost of meeting voltage requirements, and do
not include the cost of managing inertia or the largest loss of infeed".

## 3. How it maps to what 013 measures

013 publishes, per settlement day: **paid out**, the gross positive
indicative Balancing Mechanism cashflow from Elexon's EBOCF; the two cuts
(wind-unit bids, gas-unit offers); Disaggregated BSAD net; and, as an
outcome appended when NESO's file reaches the day, **L1 = NESO's
`Constraints` £ from Daily Balancing Costs 2026-27**, NESO's own attribution.

- **Paid out is not like for like with any forecast above.** It is
  indicative, pre-settlement, BM-only, gross, and includes actions NESO does
  not attribute to constraints. The declaration already forbids reading it
  as a constraint figure, and the L1 ÷ two-cuts ratio exists precisely
  because the two are different accountings.
- **L1 is the only 013 figure that could be laid against a NESO constraint
  forecast**, and only if the forecast uses the same constraint accounting
  as the Daily Balancing Costs file. §2 shows NESO publishing **at least
  three constraint definitions** that differ materially (the 24-month
  boundary model excluding inertia and loss of infeed; the BSUoS forecast's
  Constraints line, £155m for June; the Monthly Balancing Cost Report's
  constraint costs, £232m for June). Which of them the Daily Balancing Costs
  `Constraints` category follows is not established here, and which of them
  produced "£3.2bn" is not established either, because the Times names no
  document and the candidate dataset's July vintage is gone.

**Verdict: the figures are not like for like as things stand, and this note
stops here.** The tracker does not gain a forecast column. Nothing is
proposed for `TRACKER.md` or the public page.

## 4. The cheapest evidence that would change the verdict

Listed by leverage, none of it fetched:

1. **Ask NESO which publication "£3.2bn" came from.** One press-office or
   EIR question. If the answer is the 24-month constraint forecast at its
   July vintage, the definition is the dataset's, and the comparison can only
   be against a **captured** vintage from now on.
2. **Capture the 24-month constraint forecast daily** (384 bytes, CKAN,
   overwritten monthly): resource
   `28b85d3f-a1cc-4bb9-80af-600f2cca266a` under dataset
   `51bb8f5a-3c95-4f7f-9a72-3b36cb7f1dc0`. This belongs in the capture
   plan whether or not the comparison is ever published, because the vintage
   the Times cited has already been lost. Proposed in `ops/VINTAGE-CAPTURE.md`
   §12 with the demand sources.
3. **Capture the BSUoS monthly forecast CSVs and their dated PDFs** (already
   archived by NESO; cheap insurance against a page reorganisation like the
   MBSS one).
4. **A schema pass over the Daily Balancing Costs file's categories against
   the BSUoS forecast's categories**, to establish whether L1's `Constraints`
   and the forecast's `Constraints` are one accounting. That pass reads
   column names and category labels, not values, and needs its own seal
   because the 2026-27 file is inside 013's acquisition gate.

Only if 1 and 4 both resolve in favour of one accounting would a reporting
form be worth designing; at that point it would be **cumulative L1 over the
tracked days against the pro-rata forecast for the same days, from the
forecast vintage in force at the start of the window, with each later vintage
listed as a revision and never substituted**, the definition differences
stated in the column header, and paid out kept out of the comparison
entirely. That sentence is the whole of the proposal, conditional on evidence
not yet held.

## 5. Corrections for the register, proposed and not made

For slot `neso-balancing-cost-forecast-2026-27`, a superseding claim: the
Times says *constraint costs*, not "balancing and constraint costs"; the
period is "the coming 12 months, to July 2027"; the £2.2bn "came in below
Neso's £2.6 billion forecast for that period"; NESO's own publication of the
figure has been searched for and not found; the closest published series is
the 24-month constraint cost forecast, overwritten monthly with the July
vintage unrecoverable. Amending the register is Jordan's act.
