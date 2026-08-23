# C5 kill record — constraint and curtailment settlement reconciliation for generators

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-23, first in the frozen kill order.
**Verdict**: **absorption stable** — sub-outcome **externalisation already completed**.

## 1. Existing job

In GB this function is **contractually assigned before it can become a
market**. Under a Route to Market Agreement the generator holds one
contract with a supplier/optimiser rather than separate arrangements with
suppliers, aggregators and the system operator; that counterparty is the
BSC party and performs BM participation and settlement. Central
settlement is computed by Elexon, not assembled per-asset. The frozen
guess ("route-to-market providers; in-house analysts") was correct, but
understated how completely the RTM structure pre-assigns the work.

## 2. Workflow

Two layers, and they behave differently:

- **Invoice level** — "was I paid £X?" Computed centrally by Elexon,
  delivered through the RTM counterparty. Errors have a named correction
  route (Trading Disputes, £3,000 materiality).
- **Attribution level** — "is £X the economically correct £X, given
  optimiser decisions, constraints, availability and contractual
  allocation?" This is the part that could not sit inside the incumbent,
  because the incumbent is the party being assessed.

C5's frozen force tags included `comparable-across-assets`, so the
attribution layer was inside the declared boundary before any evidence
was seen. This is not a redrawn thesis.

## 3. Declared strain symptom (frozen, not chosen now)

> Trading-dispute volumes rise; analyst hiring accelerates.
> Forcing observation: Elexon trading disputes register; BSC panel papers.

## 4. Forcing it

**The frozen observation does not measure this function.** Elexon's
2024/25 performance assurance reporting gives ~£38.56m corrected and
~232,030 MWh via Trading Disputes, with root-cause categories that are
demand-side metering — Large EAC/AA, Energisation Status. Trading
Disputes exist to correct *Settlement Errors* under the BSC. An owner's
disagreement with its optimiser is **contractual, not BSC**, so it cannot
appear in that register at any volume. The proxy was measuring a
different population, and no BM- or constraint-specific dispute series
was found. Elexon's 2024/25 annual report mentions Trading Disputes only
once, as a control in its risk table — no volume trend is published.

**What is measurable is that the function externalised, around 2020.**
Modo Energy was founded in 2019, when by its own account most GB battery
owners had "only one analyst (if they were lucky)"; the Leaderboard began
in January 2020 as an emailed manual report. Its benchmarking adjusts for
location, contracts and availability specifically to isolate what
optimisers control, and it exists because "every optimizer pitching an
asset owner claims top-quartile performance" — the independence problem,
named by the supplier. Over 90% of GB BESS are owned or operated by Modo
users, and the ME BESS GB Index is now an FCA-authorised benchmark
underpinning fixed-for-floating revenue swaps.

That is not a struggling incumbent. It is a function that left the
incumbent six years ago, formed a category, and has since been
financialised into a regulated index.

## 5. The bridge C5 did not earn, and must not pretend to

> hard for an outsider to reconstruct **⇏** hard for a participant to settle

This project reconstructs constraint economics from public data and knows
how unpleasant it is. That experience is precisely what would have
manufactured a buyer pain here. Participants hold contractual, metering
and settlement data we do not. Nothing found says they cannot reconcile;
the attribution gap they genuinely had was solved commercially in 2020.
The inference was available, attractive, and is refused.

## 6. Verdict

**Absorption stable.** Not because an incumbent grew to meet the load —
because the load was externalised long before our public-as-of date and
the resulting category is mature. Proposition 3 (existing solutions
inadequate) fails outright.

## 7. What this says about the generator — recorded, not acted on

- **The force tags were right.** `data-intensive` +
  `comparable-across-assets` + independence really did produce
  externalisation. Modo is the proof that the generator's physics works.
- **The timing was wrong by about six years.** v3 has an absorption kill
  but no *already-externalised* kill. The mirror question — "has this
  function already left the incumbent, and when?" — is unasked.
- **The forcing observation was badly designed**: it named a register
  that structurally cannot contain the disputes in question. That is a
  defect in this file's column, not in the candidate.

Per the standing instruction, the instrument is **not repaired now**. One
result cannot distinguish a local defect from a systematic one. These
observations wait for the batch.

## Sources (accessed 2026-08-23)

- Elexon, Annual Performance Assurance Report 2024/25 (dispute totals and
  root-cause categories); Elexon Annual Report and Financial Statements
  2024/25, `assets.elexon.com` (risk table mention only).
- Elexon BSC Section W (Trading Disputes) and Trading Disputes Process
  guidance; £3,000 materiality.
- Modo Energy: Leaderboard history and methodology; benchmarking
  methodology pages; ME BESS GB Index / FCA authorisation.
- Lexology, "Route to market agreements: an overview" (RTMA structure).

**Retrieval limitation, recorded honestly**: `elexon.co.uk` returns HTTP
403 to this environment (Cloudflare), so the dispute-decisions register
was read only through search-tool summaries and the `assets.elexon.com`
PDF, not fetched and pinned by digest. The verdict does not rest on a
dispute count — it rests on the register being the wrong population and
on the externalisation being complete — but the pinning gap is real.
