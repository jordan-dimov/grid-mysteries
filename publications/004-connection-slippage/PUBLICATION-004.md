# Publication Pack 004 — how much should you believe a grid connection date?

No new analysis. Every number here and in the two visuals
(`slip-by-status.svg`, `works-history.svg`, rendered by `render.py` **from
the committed evidence of Investigations 005 and 006, never typed by
hand**) is in `investigations/005-connection-date-credibility/evidence/`
and `investigations/006-connection-slippage-attribution/evidence/`, with the
declarations that were frozen before the data was opened. **Human gate:
publication. Nothing here is released until the sponsor approves the
rendered bytes.**

## Draft post copy

> Every large generator waiting to plug into Britain's transmission grid
> has a date written on its contract. How much should anyone — a lender,
> a buyer, a planner — believe that date?
>
> NESO publishes the list twice a week and, it turns out, has kept every
> old copy since 2014. It released them under environmental-information
> requests. I recovered 731 versions and followed each project from copy
> to copy to see what happened to its promised date.
>
> The short answer: most dates don't move. About one in five moves by two
> years or more.
>
> Across 1,161 project-stages watched for at least two years (first seen
> before 2025, so this is the old regime, before connections reform
> re-baselined everything), the median slip is zero, but 21% slipped by
> 24 months or more. A fifth of this historical sample ended up at least
> two years later than its first-observed contractual date. This is
> evidence about the old queue; it is not a claim that Gate 2 projects
> will behave the same way.
>
> And the risk is not evenly spread. A project first seen at "Awaiting
> Consents" went on to slip two-plus years 36% of the time. A project
> already under construction: 11%. Roughly three and a half times the
> odds, and the gap holds in two separate cohorts of projects.
>
> One result runs against intuition. Projects whose date was three to
> five years out slipped far *more* often (36%) than projects whose date
> was more than five years out (12%). Longer dates were not less
> reliable. I don't know why. I'm leaving it on the record as a fact
> that needs explaining.
>
> Then I asked the obvious next question. Connection dates depend on
> transmission works — new substations, reinforced lines — that NESO
> also lists, project by project. Does knowing that a project's enabling
> works have already slipped tell you its date is unreliable?
>
> Not in the disclosed data. Projects whose enabling works had already
> slipped went on to slip
> *slightly less* often (22%) than projects whose works were on plan
> (27%). The sign was the same in every transmission owner's area. I set
> myself a bar before opening the works register — a 20-point gap — and
> missed it by the width of a barn.
>
> So here is what the public record can and cannot say. It can tell you
> the base rate of slippage and which development stages carry more of
> it. In this test, the disclosed works register did not add useful
> information about which dates would slip. And I decided in advance
> not to turn any of this into a "credibility score": the facts are
> worth publishing; the product they might have become did not earn
> itself.
>
> Everything — the 731 register copies, the frozen thresholds, the code,
> the one amendment made mid-way and why — is in the repository.

## The two visuals

1. **`slip-by-status.svg`** — the rate of ≥ 24-month slippage by the
   status a project carried when first observed, with the pooled 21.4%
   as a hairline. Five statuses, one hue: this is magnitude, not identity.
2. **`works-history.svg`** — two bars, on the matched subset (74.3 %) of
   the same population: projects whose enabling works had already slipped
   within a year of first observation versus projects whose works had
   not. The bar the reader expects to be taller is shorter.

## Expert corner

- **Corpus.** 731 TEC Register vintages, 2014-01-31 → 2026-08-25, from
  NESO FOI-24-0031, FOI-24-0040, FOI-25-129, FOI-26-051 and Wayback
  captures; 699 parsed (32 early-2014 `.xls` files failed). Old regime =
  vintages before 2025-12-01. One 301-day hole (2025-07-22 → 2026-05-19)
  is the subject of an open EIR request.
- **Unit.** A project-stage identified by the normalised (project name,
  customer, connection site) triple plus the register's `Stage` — the
  register lists multi-stage projects as several rows from 2023
  (Amendment 1, 005). `Project ID` is *not* usable across years: the
  Salesforce id format changed in 2023 and again in 2024, sharing zero ids
  across each boundary.
- **Population.** Observed ≥ 2 years, first observed before 2025-01-01,
  slip observable: n = 1,161. Net slip = last observed `MW Effective From`
  minus first, in months, signed.
- **Pre-declared tests (005).** Q1 dispersion: IQR ≥ 12 months and ≥ 20%
  slipping ≥ 24 months and ≥ 20% slipping < 6 — passed (17; 21.4%;
  63.5%). Q2 predictability: a pre-listed stratification with a ≥ 2×
  ratio between strata of n ≥ 30, holding in both first-observation
  cohorts — passed on first status (3.4×) and initial lead-time band
  (2.9×). Q3 materiality: any passing stratum ≥ 15 pp from the pooled
  rate — **failed** at 14.4 pp; the bar was not moved.
- **Pre-declared tests (006).** T1 measurability: ≥ 5 TWR vintages over ≥
  3 years and ≥ 50% of the population matched — passed (31 vintages,
  2017–2025; 74.3% matched by normalised customer/site or name/site). T2:
  works-slipped vs works-clean subgroups differ by ≥ 20 pp — **failed**,
  −4.9 pp (21.7% vs 26.6%), negative in both cohorts and in NGET, SHET and
  SPT. T3: ≥ 20% of projects change risk band when the works flag is added
  — **failed**, 5.4%. T4 (descriptive): of 213 large slips, 26% coincide
  with a same-direction works move within −180/+90 days, 60% do not, 14%
  have no matched works.
- **The proxy, stated plainly.** The disclosed TWR carries the *project's*
  connection date on every project → scheme row, not the scheme's
  completion date. A scheme's completion date was proxied by the earliest
  connection date among its dependent projects, declared before any join
  was computed (006 Amendment 1). Whether NESO's internal register holds
  true per-scheme dates is the other subject of the open EIR request.
- **Caveats the sources carry.** NESO: project status is its best-known
  classification, not authoritative project information. Slip counts are
  observation-span dependent; the lead-time result survives a slip-per-
  observed-year check (4.9 vs 1.2 months per year), but is reported as a
  register regularity, not a delivery claim.
- **Reproduce.** `uv run --with openpyxl --with xlrd python
  investigations/005-connection-date-credibility/run.py` and the same for
  006; `uv run python publications/004-connection-slippage/render.py`.
