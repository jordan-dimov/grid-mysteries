# Job 3: NESO forecast behind Montel/Times 3.2bn figure

Started 2026-09-17.

## Finding 1: The Times original (via WindAction repost)
- URL: https://www.windaction.org/posts/56974 (repost of The Times, Emily Gosden & Geraldine Scott, 26 July 2026, headline "£3.2bn to switch off power plants when network cannot cope")
- Seen (via fetch summary): £3.2bn = NESO forecast CONSTRAINT costs for coming 12 months "to July 2027"; £2.2bn = actual over past 12 months "to June 2026"; NESO previous forecast for 2025-26 was £2.6bn; ~£10 on household bill; NESO quote: "over 75 per cent of the forecast cost is due to the limitations of the current network"; NESO quote: "To reduce this element of constraint costs, new network should be built. However, to do so requires outages - increasing constraint costs in the short-medium term."; NESO quote re "at least £1.2 billion" saved. Times mentions "internal Neso reports obtained by The Times" (constraints breached on five lines) - separate story.
- The Times article does NOT name the NESO publication. NOTE: The Times says constraint costs (not "balancing and constraint costs" as Montel paraphrased).

## Finding 2: NESO Balancing costs page
- URL: https://www.neso.energy/industry-information/balancing-costs
- Definition seen: Balancing costs = "those expenses associated with (A) the Balancing Mechanism, (B) balancing services, and (C) energy trading."
- Lists Monthly Balancing Cost Reports (latest Apr-Jul 2026), 2025 Annual Balancing Costs Report (12 Jun 2025, doc 362561), MBSS datasets updated 17 Jul 2026, Daily balancing costs archive.
- July 2026 Monthly Balancing Cost Report PDF: https://www.neso.energy/document/386501/download (saved locally; to read with pdftotext)

## Finding 3: expose-news 6 Jul 2026 - cites Beyond 2030 update + 2025 ABCR; NOT the 3.2bn figure. (Balancing 2025/26 "over £3.1bn" vs £2.7bn 2024/25 - from monthly report / ABCR.)

## Finding 4: July 2026 Monthly Balancing Cost Report (NESO PDF) - NO 12-month forward forecast in it
- URL https://www.neso.energy/document/386501/download ; pdfinfo CreationDate Mon 7 Sep 2026 11:48 BST; 24 pp; author "West, James".
- Seen: July 2026 total balancing cost £302m vs benchmark £257m; constraint costs £221.2m (June £232.3m); non-constraint £80.9m; YTD Apr-Jul 2026/27 outturn £1,167m vs benchmark £1,096m; "Thermal constraints currently make up the largest share of balancing costs (~60%)"; £536m savings Apr25-Mar26.
- Text search for "forecast", "12 month", "3.2", "75" -> no forward 12-month figure. So the 3.2bn is NOT from the MBCR.
- Appendix "Types of constraint costs" defines Voltage synchronisation, Inertia, Thermal constraint costs (quoted in final report).
- "Previous months' outturn balancing costs are updated every month with reconciled values."

## Finding 5: 24 Months Ahead Constraint Cost Forecast (NESO data portal) - most likely carrier
- Page: https://www.neso.energy/data-portal/24-months-ahead-constraint-cost-forecast
- CKAN metadata (api.neso.energy package_show): created 2022-04-20; metadata_modified 2026-09-10T09:38:53; update frequency Monthly; version 1.0; ONE resource only:
  - name "24 Months Ahead Constraint Cost Forecast", CSV, 384 bytes, created 2024-04-02, last_modified 2026-09-10T09:38:53
  - URL https://api.neso.energy/dataset/51bb8f5a-3c95-4f7f-9a72-3b36cb7f1dc0/resource/28b85d3f-a1cc-4bb9-80af-600f2cca266a/download/24-months-ahead-constraint-cost-forecast_sept26.csv
  - Description: "24-month ahead constraint costs on a monthly basis for the main boundaries on the transmission system"; includes thermal/voltage/stability boundary management + voltage requirement costs; EXCLUDES inertia and largest-loss-of-infeed.
  - Page note: column IDs to be updated 9 Sep 2026.
- Inference: single resource, filename suffix _sept26 -> overwritten in place monthly (the July 2026 vintage the Times reported is presumably replaced). Wayback has a snapshot 2025-12-12 of the page. Need to check for 2026 snapshots.
- NOT DOWNLOADED (data file).
- Its figure would be the 24-month total; the Times' "£3.2bn over 12 months to July 2027" would be a 12-month sum of the Aug26-Jul27 rows (inference, not seen).

## Finding 6: Constraint Breakdown Costs and Volume (data portal) - outturn by category, weekly, per-financial-year CSVs (2017-18 .. 2026-27); 2.2bn year-to-June outturn would need summing from these or from MBSS/Daily Balancing Costs. Not downloaded.

## Finding 7: 24MA dataset schema (datastore_search limit=0, no rows read)
- Fields: _id (int), Month (text, "MMM-YY"), Constraint Cost (numeric, "Modelled constraint cost in £m"). Total records: 24. -> a single 24-row monthly GB total; no boundary split, no driver split (network vs gas vs outages).
- Wayback CDX (curl): page snapshots 2025-02-19, 2025-06-13, 2025-12-12 only; NO 2026 snapshot. Resource captured once: ..._feb25.csv (302). So the July-2026 vintage (the one The Times reported on 26 Jul 2026) is NOT recoverable from the Wayback Machine; the current file is _sept26.csv (last_modified 2026-09-10). Overwritten in place.

## Finding 8: BSUoS Forecast Reports (monthly PDFs, dated, archived as separate documents)
- Page: https://www.neso.energy/industry-information/charging/balancing-services-use-system-bsuos-charges
- BSUoS Forecast Report - June 2026: doc 381886 (published 15 May 2026); July 2026: doc 383021 (15 Jun 2026); August 2026: doc 384581 (15 Jul 2026); September 2026: doc 385726 (14 Aug 2026).
- BSUoS Outturn - May 2026: 383031 (15 Jun); June 2026: 384586 (15 Jul); July 2026: 385731 (14 Aug); August 2026: 387136 (15 Sep).
- Jun-26 edition (read via pdftotext; pdf created 14 May 2026): 24-month rolling table May-26..Apr-28; "Balancing Costs (Central) £m" row; 6-month category breakdown (Energy_Imbalance, Positive_Reserve, Negative_Reserve, Frequency_Control, Constraints, Other, Restoration). Constraints May-26..Oct-26: 179.4/192.3/173.7/178.9/202.6/269.1 of totals 257.0/265.3/250.1/256.2/279.6/346.8 (~70-78%).
- Sum of Balancing Costs (Central) Jul-26..Jun-27 in Jun-26 edition = 3,400.9 £m (my arithmetic). 
- Quote: "The constraints forecast is one of the inputs into the model that we use for forecasting BSUoS. The constraint model was updated in March 2026 to use a new set of boundary limits for the two-year forecasting period. These limits were derived from the new Year-Ahead plan, which starts delivery in April 2026. Many of the updated limits are lower than those in the previous Year Ahead plan due to a challenging outage plan... resulting in an increase in the forecast constraint costs." "The latest constraints forecast is available on the NESO data portal."
- Quote: "This report shows the forecast costs for the next 24 months, not the recovery against the fixed tariff."
- BSUoS definition (charging page): "The BSUoS charge recovers the cost of day-to-day operation including the cost of balancing the electricity transmission system."

## Finding 9: BSUoS Forecast Report - August 2026 (doc 384581, published 15 Jul 2026; pdf created 15 Jul 2026 12:32 BST) - the vintage live when The Times ran (26 Jul)
- 24-month table Jul-26..Jun-28. Balancing Costs (Central) £m Aug-26..Jul-27 sum = 3,460.8 (my arithmetic); Jul-26..Jun-27 sum = 3,448.7.
- 6-month constraints: Jul-26 166.0, Aug 177.1, Sep 205.4, Oct 286.0, Nov 266.6, Dec 228.8 (of totals 251.6/255.6/281.2/359.6/342.3/306.0) -> constraints ~75% of Aug-Dec total.
- "The August forecast is 6% (£14m) higher than the prior forecast published on 15 June (£241m). This change reflects a 9% (£14m) increase in the constraints cost forecast..."; forward curve window 2-6 July 2026.
- Categories: Energy_Imbalance, Positive_Reserve, Negative_Reserve, Frequency_Control, Constraints, Other, Restoration.
- No 3.2bn / 45% / 75%-network statement in this document.
- Sep-26 edition (doc 385726, 14 Aug 2026): Balancing Costs (Central) Aug-26..Jul-27 sum = 3,674.3; constraints Aug-26 187.8 .. Jan-27 214.2; "September forecast is 9% (£24m) higher than the prior forecast published on 15 July (£281m)... 7% (£14m) increase in the constraints cost forecast".

## Finding 10: BSUoS Outturn - June 2026 (doc 384586, published 15 Jul 2026) - the 2.2bn candidate
- 12-month table Jul-25..Jun-26 "Balancing Costs £m" = 168.96, 238.52, 286.58, 326.67, 268.57, 234.70, 300.49, 203.09, 371.73, 309.02, 235.69, 302.30 -> sum 3,246.3 (my arithmetic). So TOTAL balancing costs year to June 2026 ~ £3.25bn, NOT 2.2bn.
- Constraint outturn only given for latest months: June 2026 constraints £155m (May £168m); "Constraint costs outturned 19% (£37m) below the June forecast". July 2026 (doc 385731): constraints £169m implied (9% / £14m above June's £155m); July total £298m.
- Inference: £2.2bn = constraint-cost component only over Jul-25..Jun-26 (~£180m/month avg is consistent), but no NESO document seen states the 12-month constraint sum. It would have to be summed from Daily Balancing Costs / Constraint Breakdown data files (not opened).
- NOTE definitional gap: MBCR July 2026 says constraint costs £221.2m (June £232.3m) - the MBCR "constraints" grouping (incl. Constraints-Ancillary Services, Sterilised Headroom, Scotland/Cheviot, E&W) is larger than the BSUoS-forecast "Constraints" category (£155m June, ~£169m July).

## Finding 11: Times wording (WindAction verbatim fetch)
- Original URL: https://www.thetimes.com/uk/politics/article/wind-farms-paid-switch-off-grid-costs-32bn-rz7qx8bc6 (26 Jul 2026, Gosden & Scott)
- "...set to increase by £1 billion to £3.2 billion over the coming year, according to the National Energy System Operator (Neso)."
- "Rising gas prices are driving the bulk of the forecast increase in so-called 'constraint costs' because they will make it more expensive to run replacement gas plants, Neso said."
- "It said that 'over 75 per cent of the forecast cost is due to the limitations of the current network'."
- "Neso forecasts total constraint costs of £3.2 billion over the coming 12 months, to July 2027. That compares with £2.2 billion incurred over the past 12 months to June 2026 - which came in below Neso's £2.6 billion forecast for that period."
- Attribution is "Neso said" / "Neso forecasts" - reads as a NESO statement to the paper, not a named publication. Montel's "balancing and constraint costs" is a paraphrase; the Times says constraint costs.

## Finding 12: 24 Months Ahead Constraint Limits (sister dataset) - single CSV, filename _sept26.csv, last_modified 2026-09-10, created 2021-12-14 -> same overwrite pattern. Column-id change note dated 9 Sep 2026 on both datasets.
## Finding 13: bsuos-monthly-forecast CKAN package: 117 resources, metadata_modified 2026-08-14; monthly forecast summaries retained as separate CSVs (Dec 2025 .. Sep 2026 listed on portal page). Archived, not overwritten.
## Finding 14: NESO data-portal package_search finds no MBSS package (q=mbss, "balancing services summary" -> none); the /data-portal/mbss page returns 403 to the fetcher. Balancing-costs page says MBSS = eight datasets updated 17 Jul 2026 with archives 2019/20-2024/25.

## Finding 15: MBSS - https://www.neso.energy/data-portal/mbss returns 403 with "Sorry it doesn't look like this page exists anymore" (curl, 2026-09-17). CKAN package_show?id=mbss -> no result. MBSS appears to have moved/retired as a data-portal dataset; the balancing-costs page still lists MBSS datasets (updated 17 Jul 2026).
## Finding 16: Thermal Constraint Costs dataset (outturn, weekly): per-FY CSVs retained (19-20 .. 26-27); 25-26 last_modified 2026-04-07; 26-27 last_modified 2026-09-14. Notes: "Thermal constraints are taken when the amount of energy that would flow naturally from one region to another exceeds the capacity of the circuits connecting the two regions."
## Finding 17: 2025 ABCR (doc 362561, 12 Jun 2025): "Overall balancing costs totalled £2.7bn in 2024/25"; "Thermal constraint costs have increased by 64% in 2024/25, totalling £1.7bn"; "Balancing costs are expected to rise in the short term, reaching a peak of ~£8bn in 2030"; BSUoS ~3.4% of domestic bills 2024/25. EDF cites ABCR 2025 constraint forecast for 2025 as £2.6-4.2bn range (not verified in text - chart). The Times' "£2.6bn forecast for the period" may be that lower bound or a 24MA vintage; NOT confirmed.
## Finding 18: BSUoS monthly forecast CSVs on data portal are dated & retained: bsuos-forecast-august-2026.csv last_modified 2026-07-15T14:59; september-2026-v2.csv 2026-08-14T15:24 (a v2 - reissued). Times 26 Jul falls between the Aug-26 edition (15 Jul) and Sep-26 edition (14 Aug).

## Finding 19: MBSS data files are now NESO /document/ downloads (same document ids, re-dated 17 Jul 2026 -> overwritten in place): Total Balancing Costs doc 366341; Overall Costs doc 366331; etc. MBCR PDFs: Apr 382411, May 383801, Jun 385101, Jul 386501.

## SUMMARY (2026-09-17)
- No NESO document found that prints "£3.2bn", "45%", "£2.2bn" or "over 75% ... limitations of the current network". Times attributes to "Neso said"/"Neso forecasts" (statement), not to a named publication.
- Closest NESO carriers: (1) 24 Months Ahead Constraint Cost Forecast CSV (24 rows Month/Constraint Cost £m; single file overwritten monthly; current _sept26, last_modified 2026-09-10; July vintage not archived anywhere found); (2) BSUoS Forecast Report Aug-26 (15 Jul 2026) - balancing costs central Aug-26..Jul-27 = £3.46bn total, constraints ~75% of monthly totals; (3) BSUoS Outturn Jun-26 (15 Jul 2026) - total balancing costs Jul-25..Jun-26 = £3.25bn (constraint component not totalled; June constraints £155m).
