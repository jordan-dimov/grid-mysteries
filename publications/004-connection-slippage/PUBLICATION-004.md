# Publication Pack 004 — how much should you believe a grid connection date?

No new analysis. Every number here and in the visuals
(`slip-by-status.svg`, `works-history.svg`, rendered by `render.py` **from
the committed evidence of Investigations 005 and 006, never typed by
hand**) is in `investigations/005-connection-date-credibility/evidence/`
and `investigations/006-connection-slippage-attribution/evidence/`, with the
declarations that were frozen before the data was opened. **Human gate:
publication. Nothing here is released until the sponsor approves the
rendered bytes.**

## Draft post copy

> **A grid connection date is not really a date.**
>
> It is a risk estimate pretending to be one.
>
> I reconstructed 12 years of NESO's historical connection register — 731
> versions, following 1,161 project positions through time.
>
> **21% ended up at least two years later than their first-observed
> contractual connection date.**
>
> But that wasn't the interesting part.
>
> Projects first seen **Awaiting Consents** slipped by 2+ years **35.8% of
> the time**.
>
> Projects already **Under Construction: 10.5%**.
>
> Same system. Same kind of contractual date.
>
> **3.4× different historical risk.**
>
> If you're buying, financing or developing a battery, wind farm or solar
> project, that distinction matters.
>
> A project valued on a 2030 connection date can look very different if
> meaningful revenue actually begins in 2032.
>
> Yet connection due diligence still tends to start with:
>
> **"What is the connection date?"**
>
> The better question may be:
>
> **"How much should I believe it?"**
>
> This dataset is from the old GB connections regime, so I'm not claiming
> Gate 2 will behave the same way.
>
> In fact, that creates the next interesting question:
>
> **Will connections reform actually make a contracted MW in 2030 more
> bankable — or merely give it a new label?**
>
> We'll be able to measure that.

## The visuals

1. **`slip-by-status.svg` — attached to the post.** Headline "Same
   connection date. 3.4× different historical risk." (the ratio is
   computed by `render.py` from the evidence file, not typed). Five
   statuses; *Awaiting Consents* and *Under Construction* carry the hue,
   the other three recede; the pooled 21.4% stays as a hairline.
2. **`works-history.svg` — record only, not attached.** The failed
   second hypothesis (006) strengthens the research record and is in the
   expert corner, but the post is about one thing: connection-date
   credibility is part of asset quality.

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
