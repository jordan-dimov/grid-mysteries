# C11 kill record — LV connection assessment and quotation at volume, as EV chargers and heat pumps arrive

**Batch**: 02 (`45639418…`) · **Generator**: v4 (`2ac6efa8…`)
**K0**: PASS, class C (SI 2015/698; ED2 LV Services Volume Driver).
**Instrument state at gate**: eligible now.
**Run**: 2026-08-26, first of six in the frozen K1/K2 order.

**K1 — current absorber**: the 14 DNO licensees' own connections /
minor-connections / service-alteration teams under SLC 15A and SI
2015/698, and the ENA-governed **Connect & Notify / Apply to Connect**
process — under which most domestic chargers and heat pumps (≤60 A
maximum demand) are *notified after installation* and never assessed or
quoted at all; only the 60–100 A band and above triggers an assessment
(10 working days) and the statutory quotation standards.
**K1 — absorption status**: **ADEQUATE** — sub-reasons *the bulk of the
forcing volume has been designed out of the function* (notification) and
*the residual assessed segment is measurably improving, with in-house
automation (self-serve) arriving ahead of any capacity break*. The
forcing variable, as Ofgem measures it, has not arrived at the scale
assumed: LCT uptake "remains below projections".
**K2 — measured strain**: **MEASURED STABLE (improving)** on both frozen
symptoms, FY2023-24 → FY2024-25, all 14 DNOs. Neither symptom moved in
the predicted direction. The only genuine deterioration in the series —
GSoP failure share 0.27% → 1.17% over 2021/22–2023/24 — predates the
frozen window and has plateaued.

Research performed by a background agent under the v4 kill discipline;
the record below is its report, unedited except for this header.

## Sources [V] fetched

| Item | Vintage | Digest |
|---|---|---|
| Ofgem RIIO-2 ED Annual Report 2023-24 PDF + supplementary XLSM | 7 Apr 2025 | f249a1e7… / bf8483f7… |
| Ofgem RIIO-2 ED Annual Report 2024-25 PDF + supplementary XLSM | 15 Jan 2026 | 736a7b12… / b4c8ca61… |
| Ofgem RIIO-ED1 Annual Summary Report 2022-23 XLSM (ED1 baseline) | 8 Aug 2025 | 13aab685… |
| SI 2023/887 (Standards of Performance amendment; made 31 Jul 2023, in force 1 Oct 2023); SI 2024/984 | — | — |
| ENA "Connecting electric vehicles and heat pumps to the networks" (Wayback 2024-02-28) | — | — |

## Answer 1 — current absorber

Primary-source detail [V, ENA archived page]: "Electric vehicle and heat
pump connection forms and processes share the same documentation"; "The
form is the same whether the installation is a 'Connect & Notify' or an
'Apply to Connect'"; "an installer should use the EVCP database to
cross-reference their equipment to assist in determining whether they can
'Connect & Notify' … or 'Apply to Connect'"; "For residential properties
with new Maximum Demand (MD) between 60A and 100A inclusive – the
installer must apply for a connection prior to installation … the
network operator will confirm whether the new equipment can be connected
within 10 working days"; the process "is maintained and governed by our
Low Carbon Technologies Working Group [ENA]".

So the low end of the function is **absorbed into a notification** — no
assessment or quote is performed; the DNO receives an emailed form after
the fact.

Automation inside the incumbent [V, Ofgem 2024-25]: "The company [SSES]
introduced self-serve functionality for minor connections in 2024-25 and
plans to extend this to service alterations by the end of 2025-26 … self-
serve is expected to improve customer experience by enabling faster
quotations". Ofgem: "a positive step, but sustained improvement will
require robust resource planning and operational resilience."

[N] Not verified (ENA/NGED live pages 403): current Connect Direct portal;
exact C&N thresholds in G98/G99/G100.

## Answer 2 — absorption status

**ADEQUATE.**

Volume evidence (kept separate from performance):

1. **Regulated LV connection caseload is flat-to-falling** [V, XLSM "Ch2
   outputs - connections", "Total number of cases where the Connection
   GSOPs apply"]: 2015/16 405,833 → 2018/19 387,637 → 2020/21 364,242 →
   2021/22 397,226 → 2022/23 368,588 → **2023/24 341,400 → 2024/25
   341,123**. −15.9% since 2015/16, −7.5% since 2022/23. Caveat: GSoP cases
   are quotation/connection events; a notify-only charger never enters the
   count — which is the point: the "millions" are routed around the
   function.
2. **Ofgem's own force-side reading** [V, 2024-25, Ch4]: "Lower-than-
   forecast uptake of Low Carbon Technologies (LCTs): Growth in EVs and
   heat pumps remains below projections, reducing immediate reinforcement
   requirements." "Expenditure on connections remains materially below
   allowances for all DNOs, ranging from £10.5m (39%) in SPEN to £127.4m
   (71%) in UKPN." UKPN "forecasts a £124m (19%) underspend … lower
   reinforcement needs from slower low-carbon technology uptake."
3. **EV capacity connected (MW, reputational)** [V]: fast charge 2022/23
   1,149.8 → 2023/24 1,860.8 → 2024/25 2,043.3 MW (+9.8%). Vintage warning:
   the 2023-24 file reported 2023/24 as 1,662.1 MW; the 2024-25 file
   restates it. Public-charging-style MW, not domestic counts.
4. **Indirect volume signal**: NPg "attributed this outcome [missing TTC
   targets] to a significant increase in service upgrade work" [V]; Ofgem
   notes LVSVD cost pressure "driven by customer requests" (unlooping) —
   framed as a unit-cost issue, not quotation capacity.
5. **[N] NGED CKAN "LCT Connections" / "LCT Enquiries"** (monthly counts by
   primary substation since April 2017, modified 2026-08-01): datastore
   "Access denied: Resource access restricted to registered users"; CSV
   403. **Unmeasured — access-gated (NGED).** No other open LCT count
   series found without search.

Absorption-failure hypotheses tested: *volume beyond human scaling* — not
met (volume removed by design; assessed caseload shrinking); *latency
intolerance* — not met (time to quote 2.3 working days against a 5-day
statutory standard; time to connect down 15–17%); *standardisation of
repetitive work* — being captured **inside** the incumbent (self-serve);
*externalised to a supplier market* — no evidence; the only external step
is the ENA-run equipment database installers use to self-classify.

## Answer 3 — measured strain

### (a) Connection GSoP failures and compensation — "Ch2 outputs - connections" (£ in 2020/21 prices)

| DNO | 23/24 cases | not met | £ | % | 24/25 cases | not met | £ | % |
|---|---|---|---|---|---|---|---|---|
| ENWL | 21,399 | 66 | 24,605 | 0.31 | 19,686 | 32 | 3,720 | 0.16 |
| NPgN | 17,237 | 499 | 250,865 | 2.90 | 27,536 | 516 | 128,495 | 1.87 |
| NPgY | 23,566 | 744 | 252,025 | 3.16 | 28,953 | 484 | 183,345 | 1.67 |
| WMID | 30,627 | 32 | 12,280 | 0.10 | 29,002 | 41 | 13,445 | 0.14 |
| EMID | 32,874 | 132 | 21,680 | 0.40 | 30,269 | 12 | 4,200 | 0.04 |
| SWALES | 14,939 | 3 | 530 | 0.02 | 14,717 | 24 | 4,345 | 0.16 |
| SWEST | 32,429 | 79 | 41,430 | 0.24 | 29,300 | 416 | 182,900 | 1.42 |
| LPN | 16,400 | 0 | 0 | 0 | 14,872 | 3 | 460 | 0.02 |
| SPN | 22,645 | 10 | 3,495 | 0.04 | 20,809 | 7 | 1,910 | 0.03 |
| EPN | 39,706 | 5 | 5,010 | 0.01 | 38,423 | 8 | 780 | 0.02 |
| SPD | 12,221 | 284 | 316,370 | 2.32 | 11,561 | 164 | 98,075 | 1.42 |
| SPMW | 11,201 | 22 | 17,845 | 0.20 | 10,826 | 45 | 13,215 | 0.42 |
| SSEH | 15,046 | 66 | 42,070 | 0.44 | 14,589 | 31 | 31,605 | 0.21 |
| SSES | 51,110 | 2,058 | 1,013,165 | 4.03 | 50,580 | 2,077 | 826,110 | 4.11 |
| **Total** | **341,400** | **4,000** | **2,001,370** | **1.17** | **341,123** | **3,860** | **1,492,605** | **1.13** |

Report's own words [V, 2024-25]: "In Year 2 (2024-25), performance
improved, with 13 of 14 DNOs achieving green RAG ratings. NPgN, NPgY and
SPD showed particularly strong progress." "Total GSoP payments under
Connections standards fell to £1.5m from £2.0m in Year 1, with SSEN
accounting for just over 55% (£0.86m), although this represents an 18%
reduction." The one mover in the predicted direction is **SWEST (79 → 416
failures)** — still Green, not commented on by Ofgem; SSES flat at ~4.1%,
attributed by Ofgem in 2023-24 to "personnel changes in specific roles"
and severe-weather diversion — staffing/weather, not volume.

**ED1 baseline** [V]: total failures 840 (2015/16), 920, 1,015, 1,480,
907, 987, **2,710 (2021/22), 4,097 (2022/23)**, 4,000, 3,860; failure
share 0.21% → 0.27% (2020/21) → 0.68% → 1.11% → 1.17% → 1.13%. **A genuine
step-up 2021/22–2023/24 (≈4× the ED1 norm), concentrated in SSES, NPg and
SPD, that predates the frozen window and has since plateaued.** A
candidate reframed on that deterioration would be a different candidate;
within the frozen window the direction is wrong.

### (b) Time to Quote / Time to Connect (LV segments LVSSA / LVSSB, working days)

| | TTQ-A | TTC-A | TTQ-B | TTC-B |
|---|---|---|---|---|
| 2013 (ED1 baseline) | 9.14 | 46.38 | 14.46 | 57.01 |
| ED1 2019-23 avg (= ED2 target) | 4.07 | 35.67 | 6.84 | 44.30 |
| 2023/24 | 2.57 | 31.00 | 5.00 | 38.99 |
| 2024/25 | 2.33 | 25.81 | 4.60 | 33.35 |

Year on year: TTQ-A −9.3%, TTC-A −16.8%, TTQ-B −8.1%, TTC-B −14.5%. Reward
£6.03m → £8.73m; "twelve DNOs have improved since Year 1. All DNOs, except
NPgN, have earned rewards." The only DNO whose TTC-A lengthened is NPgN
(31.1 → 39.1); WMID/EMID slipped marginally while remaining above target.

### Report's own caveats
- Coverage: "Time to Quote and Time to Connect for two different types of
  LV connections"; LVSSA/LVSSB not defined in either PDF or XLSM [N]; the
  incentive covers "smaller customers (low voltage connections)" only.
- Method: "We acknowledge there are differing views on the calculation of
  the TTC performance chart; however, this methodology aligns with the
  approach adopted since the start of RIIO-ED1."
- Row relabelling between vintages; £ basis "2020/21 prices"; RAG
  thresholds not stated.

### Confounders separated
1. **SI 2023/887 (in force 1 Oct 2023)** [V] did not change the standards'
   definitions or periods; it raised prescribed sums (quotation 5 wd
   £20/day; 25 wd £75; 35 wd £160; 65 wd £235) and indexed them to CPIH
   from April 2024. **£ penalties in 2024-25 sit on a higher tariff — and
   still fell 25%.** Failure counts and shares are the clean series; they
   fell too.
2. SI 2024/984 concerns severe-weather restoration only.
3. The caseload denominator fell 8% since 2022/23, so a constant count
   would read as a rising share; share still fell.
4. 2023/24 EV MW restated in the later vintage.

### Forcing variable present?
**Not as measured in the eligible instrument.** GSoP cases flat and 16%
below 2015/16; Ofgem: LCT uptake "below projections"; the only rising
series (EV MW, +9.8%) is not an application count; the domestic notify
volume that could show the true force is **access-gated (NGED LCT
Connections / LCT Enquiries)**.

## Verdict

**K1: adequate — the function is absorbed largely by not being performed
(connect-and-notify), and the residual is speeding up with in-house
automation. K2: measured stable (improving) on both frozen symptoms.**
This is the batch's cleanest case of *measured successful absorption*.
The only live threads: the pre-window 2021–24 rise in failure share
(SSES/NPg/SPD), and the unmeasured domestic notify volume behind NGED's
login wall.

## Failed fetches
WebSearch exhausted; Ofgem slug guesses 404 (resolved via sitemap);
energynetworks.org and nationalgrid.co.uk 403 (ENA content via Wayback
CDX); NGED CKAN datastore authorisation error, CSV 403, DSA PDF login
page; UKPN Opendatasoft search surfaced no LCT-count dataset.
