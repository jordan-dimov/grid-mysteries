# 016 — the day-ahead wind forecast on the record day

**This is a data pack, not an investigation.** There is no declaration, no
sealed result and no conclusion here. It exists so that someone who knows
numerical weather prediction can answer a question we are not qualified to
answer, from bytes we have already pinned and can prove we did not touch
afterwards.

**Analysis: Gökberk Görür. Data pack and cost figures: Grid Mysteries, A115.**

## The question

On 8 September 2026, Britain's balancing mechanism paid out **£33.6 million** in
a single day — the most expensive balancing day on record (investigation 012).
£3.77 million of it went to wind farms paid to stop generating, while
£26.8 million went to gas plant paid to start (investigation 015). The whole day
was constrained: all 48 settlement periods carried accepted wind bid volume.
**How good was the day-ahead wind forecast that morning, and how much of that
bill came from the forecast being wrong rather than from the network being
full?** Nobody has answered it.

## What is in the pack

Seven CSVs in `data/`, all for settlement day 2026-09-08, all UTC. Read
`DATA-DICTIONARY.md` before the data — it is one page per file and it carries
the traps.

| File | Rows | What it is |
|---|---|---|
| `forecast_issues.csv` | 384 | NESO's wind forecast (WINDFOR), **every one of the 16 issues** published on 7 and 8 September, hourly, with its publish time. The forecast's evolution, not just its final value. |
| `b1440_day_ahead.csv` | 144 | The day-ahead wind and solar forecast (DGWS, ex-B1440), 48 periods × offshore / onshore / solar. |
| `wind_units.csv` | 284 | Every wind BM unit in the register — **not just the Scottish ones** — with capacity, lead party, and which side of the B6 boundary it sits on, graded. |
| `pn_final.csv` | 12,416 | Final physical notifications for 227 wind units, all 48 periods: what each generator said it intended to do. |
| `b1610_actuals.csv` | 11,136 | Metered half-hourly output for 232 wind units, all 48 periods. |
| `fuelinst_wind_5min.csv` | 288 | Five-minute wind outturn for the day, re-exported from 012's pinned file. |
| `cost_context.csv` | 14 | The 012 and 015 cost figures you may cite, each with the evidence file it comes from. |

`evidence/` holds the acquisition manifest, the SHA-256 of every fetched and
every exported file (`pack.json`), and an RFC 3161 and OpenTimestamps witness
over the manifest, so the acquisition time of this pack is provable against
roots we do not control: `scripts/verify-timestamp` checks it offline against
the TSA roots committed under `trust/tsa/`. The fetch journal sits beside them
on disk but stays out of git, as in every investigation here — it is
restart-safety scaffolding, content-identical to the manifest, which is the
file that is digest-pinned. `run.py --phase export` rebuilds every CSV from the
pinned bytes and reproduces the digests exactly.

## What is deliberately not in the pack

**The weather.** No NWP fields, no reanalysis, no wind speeds — not for
7 September, not for any run. That side is yours to fetch, and which model,
which run and which vintage you choose is a research decision we should not
make quietly on your behalf. Tell us what you used and we will pin it here
beside the rest.

**Any forecast error, and any attribution of cost to it.** Not a single column
in this pack is a residual, a bias, an RMSE or a pound attributed to a missed
megawatt. That is the analysis, and the analysis is yours. We have deliberately
not looked, so that what you find is a finding and not a confirmation.

## The first deliverable

A short note — a few pages, not a paper — answering two things:

1. **Forecast versus actual, hour by hour.** How far off was the day-ahead wind
   forecast for 8 September, and where in the day did it go wrong?
2. **Did the error sit in the weather, or in turning weather into megawatts?**
   This is the question we cannot answer and you can. A wind speed forecast that
   was right, converted through a power curve or an availability assumption that
   was wrong, is a completely different failure from a wind speed forecast that
   missed — and it points at a different fix, a different responsible party and
   a different cost.

Write it so a practitioner can attack it. State what would have changed your
answer. If the honest result is "the forecast was fine and the bill was a
network constraint that no forecast would have avoided", that is a publishable
finding and we would rather have it than a more interesting one.

Three things about the house style, because they will save you rework:
**separate observation from interpretation from conclusion**; prefer the
narrowest defensible claim ("publicly unexplained from the state reconstructed
here" beats "wrong"); and never call a counterfactual price difference a saving
without proving the substitution was available and executable. A hypothesis you
tested and killed belongs in the note, not in the bin.

## How to contribute

1. Fork `https://github.com/jordan-dimov/grid-mysteries`.
2. Work in `investigations/016-day-ahead-wind-forecast/analysis/`. It is yours:
   your code, your notebooks, your figures, your note. Nothing outside it needs
   to change, and we would rather you did not edit `data/` or `evidence/` — if a
   figure in the pack is wrong, say so and we will correct it in the open.
3. If your analysis fetches anything, record where it came from, when, and its
   digest. Pinned bytes or it did not happen.
4. Open a pull request. `scripts/check` runs the project's checks if you have
   touched Python in `src/`; analysis code is not held to that bar.

Questions about what a column means, or about what the balancing mechanism was
actually doing that day, are welcome in the pull request — most of them are
worth answering in `DATA-DICTIONARY.md` rather than in a thread.

## Where the numbers come from

- **012 — the record day** (`investigations/012-the-record-day/`): the £33.6m,
  the gas offer premium, FUELINST, the pinned DISPTAV and system prices.
- **015 — support and storage on the record day**
  (`investigations/015-support-and-storage-on-the-record-day/`): wind bids by
  support scheme, the graded B6 classification, the energy-limited units, and
  the finding that 45 % of the wind bid money sits on units that cannot be
  linked to any public support register at all.

Both are frozen, externally witnessed and reproducible from their own pinned
bytes. Neither has been touched to build this pack.
