# 024 — The gas in the spread: Results

Computed 2026-10-15 under the frozen declaration `739471d0…` (`DECLARATION.md`, proofs beside it) from the files pinned 15/10/2026 (`evidence/sources-manifest.json`). Method: Julien Jomaux's for Germany (GEM Energy Analytics, "The evolution of the spread: 2026 update", 24/09/2026), carried to Great Britain with attribution. Power: NESO N2EX GB day-ahead hourly price, 44,448 hours from 2021-09-20 to 2026-10-16. Gas: ONS daily SAP times ten, 3,206 days to 2026-10-11. Carbon: gov.uk UK ETS monthly average UKA price, 65 months 2021-05 to 2026-09, plus Carbon Price Support GBP 18/t. Every figure is a simple mean over the days counted beside it; ratios are 3 d.p., money 2 d.p.

## Falsifiers

- **F1** (does not fire): ratio A for 2026 to date 1.789 against 2.255 for the same dates of 2025, a change of -20.7 %; the rule fires if the 2026 ratio is not below 2025's by more than 5 %.
- **F2** (does not fire): September 2026 mean spread on the printed day 121.70 against Modo's published 122.00, tolerance 2.00.

## The headline measure (printed day)

September 2026 against September 2025: spread 121.70 against 76.30, up 59.5 %. Bloomberg says 80 %; Modo's "GBP 45/MWh wider" implies 58.7 % on this September. **The difference is not resolved here** (caveat 5).

| period | days measured | spread mean GBP/MWh | days with gas | gas mean GBP/MWh | days with both | ratio A | ratio B | days with legs | negative leg | merit-order leg | scarcity leg | negative share | merit-order share | scarcity share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 365 | 157.63 | 365 | 71.16 | 365 | 2.215 | 2.598 | 365 | 0.44 | 42.11 | 115.07 | 0.3 % | 26.7 % | 73.0 % |
| 2023 | 365 | 70.92 | 365 | 34.41 | 365 | 2.061 | 2.088 | 365 | 0.43 | 36.20 | 34.29 | 0.6 % | 51.0 % | 48.4 % |
| 2024 | 366 | 61.21 | 366 | 28.67 | 366 | 2.135 | 2.114 | 366 | 0.53 | 34.06 | 26.62 | 0.9 % | 55.7 % | 43.5 % |
| 2025 | 365 | 68.56 | 365 | 30.42 | 365 | 2.254 | 2.258 | 365 | 0.44 | 35.78 | 32.33 | 0.6 % | 52.2 % | 47.2 % |
| 2026 to date | 288 | 77.65 | 284 | 43.14 | 284 | 1.789 | 1.802 | 273 | 0.40 | 43.42 | 31.89 | 0.5 % | 57.3 % | 42.1 % |
| 2025 same dates | 288 | 71.66 | 288 | 31.78 | 288 | 2.255 | 2.261 | 288 | 0.55 | 36.25 | 34.86 | 0.8 % | 50.6 % | 48.7 % |

Days: `days measured` are the period's printed dates with 23 to 25 prices; `days with gas` its dates with an ONS SAP; `days with both` the dates entering the ratios (gas ends 11/10/2026); `days with legs` those with a carbon month too (October 2026 has none yet). Legs are means over the days with legs, in GBP/MWh; shares are each leg's mean over the spread's mean on those days and sum to 100 %.

## The same on the local day (each printed hour read as UTC, assigned to its Europe/London date)

| period | days measured | spread mean GBP/MWh | days with gas | gas mean GBP/MWh | days with both | ratio A | ratio B | days with legs | negative leg | merit-order leg | scarcity leg | negative share | merit-order share | scarcity share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 365 | 156.92 | 365 | 71.16 | 365 | 2.205 | 2.581 | 365 | 0.44 | 41.72 | 114.76 | 0.3 % | 26.6 % | 73.1 % |
| 2023 | 365 | 70.40 | 365 | 34.41 | 365 | 2.046 | 2.072 | 365 | 0.42 | 35.69 | 34.29 | 0.6 % | 50.7 % | 48.7 % |
| 2024 | 366 | 60.59 | 366 | 28.67 | 366 | 2.113 | 2.092 | 366 | 0.51 | 33.46 | 26.62 | 0.8 % | 55.2 % | 43.9 % |
| 2025 | 365 | 68.29 | 365 | 30.42 | 365 | 2.245 | 2.248 | 365 | 0.43 | 35.52 | 32.33 | 0.6 % | 52.0 % | 47.3 % |
| 2026 to date | 288 | 77.33 | 284 | 43.14 | 284 | 1.781 | 1.795 | 273 | 0.40 | 43.20 | 31.89 | 0.5 % | 57.2 % | 42.2 % |
| 2025 same dates | 288 | 71.39 | 288 | 31.78 | 288 | 2.246 | 2.251 | 288 | 0.54 | 35.99 | 34.86 | 0.8 % | 50.4 % | 48.8 % |

Excluded on the local unit: 2021-09-20 (1 prices); on the printed unit: 2021-09-20 (2 prices), 2026-10-16 (22 prices). The local figures rest on the UTC reading of the file's hours, which NESO does not document (declaration, 'what a day is').

## Every month, printed day

| period | days measured | spread mean GBP/MWh | days with gas | gas mean GBP/MWh | days with both | ratio A | ratio B | days with legs | negative leg | merit-order leg | scarcity leg | negative share | merit-order share | scarcity share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022-01 | 31 | 214.21 | 31 | 65.77 | 31 | 3.257 | 3.672 | 31 | 2.83 | 52.08 | 159.31 | 1.3 % | 24.3 % | 74.4 % |
| 2022-02 | 28 | 117.18 | 28 | 65.12 | 28 | 1.800 | 1.805 | 28 | 0.00 | 63.62 | 53.56 | 0.0 % | 54.3 % | 45.7 % |
| 2022-03 | 31 | 159.53 | 31 | 101.29 | 31 | 1.575 | 1.565 | 31 | 0.00 | 43.26 | 116.27 | 0.0 % | 27.1 % | 72.9 % |
| 2022-04 | 30 | 98.45 | 30 | 62.03 | 30 | 1.587 | 1.760 | 30 | 0.00 | 36.87 | 61.58 | 0.0 % | 37.5 % | 62.5 % |
| 2022-05 | 31 | 87.43 | 31 | 35.02 | 31 | 2.496 | 3.058 | 31 | 0.00 | 28.04 | 59.39 | 0.0 % | 32.1 % | 67.9 % |
| 2022-06 | 30 | 99.80 | 30 | 48.27 | 30 | 2.067 | 2.584 | 30 | 0.08 | 24.51 | 75.20 | 0.1 % | 24.6 % | 75.4 % |
| 2022-07 | 31 | 164.05 | 31 | 78.32 | 31 | 2.095 | 2.188 | 31 | 0.00 | 27.92 | 136.13 | 0.0 % | 17.0 % | 83.0 % |
| 2022-08 | 31 | 216.46 | 31 | 128.83 | 31 | 1.680 | 1.693 | 31 | 0.00 | 24.95 | 191.52 | 0.0 % | 11.5 % | 88.5 % |
| 2022-09 | 30 | 213.72 | 30 | 91.58 | 30 | 2.334 | 2.417 | 30 | 0.00 | 41.94 | 171.78 | 0.0 % | 19.6 % | 80.4 % |
| 2022-10 | 31 | 128.76 | 31 | 37.56 | 31 | 3.428 | 4.520 | 31 | 0.00 | 47.89 | 80.88 | 0.0 % | 37.2 % | 62.8 % |
| 2022-11 | 30 | 161.12 | 30 | 43.62 | 30 | 3.694 | 3.411 | 30 | 0.57 | 40.07 | 120.48 | 0.4 % | 24.9 % | 74.8 % |
| 2022-12 | 31 | 225.02 | 31 | 94.64 | 31 | 2.378 | 2.423 | 31 | 1.73 | 75.45 | 147.84 | 0.8 % | 33.5 % | 65.7 % |
| 2023-01 | 31 | 116.64 | 31 | 54.10 | 31 | 2.156 | 2.141 | 31 | 0.00 | 69.86 | 46.77 | 0.0 % | 59.9 % | 40.1 % |
| 2023-02 | 28 | 69.85 | 28 | 46.18 | 28 | 1.513 | 1.523 | 28 | 0.00 | 27.97 | 41.88 | 0.0 % | 40.0 % | 60.0 % |
| 2023-03 | 31 | 73.72 | 31 | 38.56 | 31 | 1.912 | 1.931 | 31 | 0.00 | 32.14 | 41.58 | 0.0 % | 43.6 % | 56.4 % |
| 2023-04 | 30 | 57.67 | 30 | 34.18 | 30 | 1.687 | 1.684 | 30 | 0.00 | 26.47 | 31.20 | 0.0 % | 45.9 % | 54.1 % |
| 2023-05 | 31 | 43.84 | 31 | 25.20 | 31 | 1.739 | 1.794 | 31 | 0.00 | 20.51 | 23.33 | 0.0 % | 46.8 % | 53.2 % |
| 2023-06 | 30 | 51.58 | 30 | 27.42 | 30 | 1.881 | 1.901 | 30 | 0.00 | 22.79 | 28.79 | 0.0 % | 44.2 % | 55.8 % |
| 2023-07 | 31 | 60.48 | 31 | 24.73 | 31 | 2.446 | 2.494 | 31 | 3.25 | 29.51 | 27.72 | 5.4 % | 48.8 % | 45.8 % |
| 2023-08 | 31 | 57.46 | 31 | 28.71 | 31 | 2.001 | 2.009 | 31 | 0.00 | 24.99 | 32.47 | 0.0 % | 43.5 % | 56.5 % |
| 2023-09 | 30 | 75.63 | 30 | 31.72 | 30 | 2.384 | 2.370 | 30 | 0.85 | 37.24 | 37.55 | 1.1 % | 49.2 % | 49.6 % |
| 2023-10 | 31 | 100.19 | 31 | 37.21 | 31 | 2.693 | 2.728 | 31 | 0.39 | 61.65 | 38.15 | 0.4 % | 61.5 % | 38.1 % |
| 2023-11 | 30 | 76.55 | 30 | 36.62 | 30 | 2.090 | 2.102 | 30 | 0.00 | 38.45 | 38.10 | 0.0 % | 50.2 % | 49.8 % |
| 2023-12 | 31 | 66.61 | 31 | 29.15 | 31 | 2.285 | 2.314 | 31 | 0.59 | 41.34 | 24.67 | 0.9 % | 62.1 % | 37.0 % |
| 2024-01 | 31 | 48.47 | 31 | 25.70 | 31 | 1.886 | 1.916 | 31 | 0.01 | 23.77 | 24.69 | 0.0 % | 49.1 % | 50.9 % |
| 2024-02 | 29 | 40.13 | 29 | 21.49 | 29 | 1.867 | 1.835 | 29 | 0.00 | 23.91 | 16.23 | 0.0 % | 59.6 % | 40.4 % |
| 2024-03 | 31 | 45.41 | 31 | 23.33 | 31 | 1.946 | 1.940 | 31 | 0.26 | 24.63 | 20.53 | 0.6 % | 54.2 % | 45.2 % |
| 2024-04 | 30 | 56.37 | 30 | 24.66 | 30 | 2.286 | 2.301 | 30 | 1.84 | 38.16 | 16.37 | 3.3 % | 67.7 % | 29.0 % |
| 2024-05 | 31 | 44.21 | 31 | 26.37 | 31 | 1.676 | 1.680 | 31 | 0.00 | 24.81 | 19.40 | 0.0 % | 56.1 % | 43.9 % |
| 2024-06 | 30 | 59.32 | 30 | 28.18 | 30 | 2.105 | 2.110 | 30 | 0.82 | 39.17 | 19.34 | 1.4 % | 66.0 % | 32.6 % |
| 2024-07 | 31 | 47.19 | 31 | 25.53 | 31 | 1.848 | 1.842 | 31 | 0.87 | 26.70 | 19.62 | 1.8 % | 56.6 % | 41.6 % |
| 2024-08 | 31 | 73.13 | 31 | 28.70 | 31 | 2.548 | 2.550 | 31 | 1.66 | 53.48 | 18.00 | 2.3 % | 73.1 % | 24.6 % |
| 2024-09 | 30 | 63.38 | 30 | 29.84 | 30 | 2.124 | 2.109 | 30 | 0.15 | 34.57 | 28.66 | 0.2 % | 54.5 % | 45.2 % |
| 2024-10 | 31 | 83.24 | 31 | 33.85 | 31 | 2.459 | 2.461 | 31 | 0.50 | 39.80 | 42.93 | 0.6 % | 47.8 % | 51.6 % |
| 2024-11 | 30 | 75.72 | 30 | 37.79 | 30 | 2.004 | 2.036 | 30 | 0.15 | 27.55 | 48.03 | 0.2 % | 36.4 % | 63.4 % |
| 2024-12 | 31 | 96.88 | 31 | 38.28 | 31 | 2.531 | 2.569 | 31 | 0.04 | 51.67 | 45.16 | 0.0 % | 53.3 % | 46.6 % |
| 2025-01 | 31 | 136.16 | 31 | 42.22 | 31 | 3.225 | 3.217 | 31 | 0.14 | 34.12 | 101.90 | 0.1 % | 25.1 % | 74.8 % |
| 2025-02 | 28 | 59.81 | 28 | 42.65 | 28 | 1.402 | 1.435 | 28 | 0.00 | 27.30 | 32.50 | 0.0 % | 45.7 % | 54.3 % |
| 2025-03 | 31 | 66.85 | 31 | 34.76 | 31 | 1.923 | 1.935 | 31 | 0.21 | 32.49 | 34.15 | 0.3 % | 48.6 % | 51.1 % |
| 2025-04 | 30 | 61.66 | 30 | 29.17 | 30 | 2.114 | 2.095 | 30 | 0.22 | 34.21 | 27.23 | 0.4 % | 55.5 % | 44.2 % |
| 2025-05 | 31 | 62.46 | 31 | 28.43 | 31 | 2.197 | 2.208 | 31 | 1.48 | 42.66 | 18.32 | 2.4 % | 68.3 % | 29.3 % |
| 2025-06 | 30 | 74.58 | 30 | 29.72 | 30 | 2.509 | 2.526 | 30 | 1.62 | 53.98 | 18.98 | 2.2 % | 72.4 % | 25.5 % |
| 2025-07 | 31 | 47.83 | 31 | 27.69 | 31 | 1.727 | 1.733 | 31 | 0.02 | 23.73 | 24.08 | 0.0 % | 49.6 % | 50.4 % |
| 2025-08 | 31 | 56.07 | 31 | 27.12 | 31 | 2.068 | 2.072 | 31 | 0.73 | 33.52 | 21.82 | 1.3 % | 59.8 % | 38.9 % |
| 2025-09 | 30 | 76.30 | 30 | 27.16 | 30 | 2.809 | 2.808 | 30 | 0.55 | 47.58 | 28.17 | 0.7 % | 62.4 % | 36.9 % |
| 2025-10 | 31 | 76.91 | 31 | 26.84 | 31 | 2.865 | 2.878 | 31 | 0.35 | 39.98 | 36.58 | 0.5 % | 52.0 % | 47.6 % |
| 2025-11 | 30 | 56.92 | 30 | 25.61 | 30 | 2.223 | 2.226 | 30 | 0.00 | 28.82 | 28.10 | 0.0 % | 50.6 % | 49.4 % |
| 2025-12 | 31 | 46.16 | 31 | 24.49 | 31 | 1.885 | 1.899 | 31 | 0.00 | 30.86 | 15.30 | 0.0 % | 66.9 % | 33.1 % |
| 2026-01 | 31 | 52.51 | 31 | 30.64 | 31 | 1.714 | 1.768 | 31 | 0.00 | 24.89 | 27.62 | 0.0 % | 47.4 % | 52.6 % |
| 2026-02 | 28 | 39.65 | 28 | 27.33 | 28 | 1.451 | 1.464 | 28 | 0.00 | 19.07 | 20.58 | 0.0 % | 48.1 % | 51.9 % |
| 2026-03 | 31 | 88.52 | 31 | 45.07 | 31 | 1.964 | 1.997 | 31 | 0.00 | 54.49 | 34.03 | 0.0 % | 61.6 % | 38.4 % |
| 2026-04 | 30 | 79.20 | 30 | 38.83 | 30 | 2.039 | 2.030 | 30 | 2.39 | 54.96 | 21.84 | 3.0 % | 69.4 % | 27.6 % |
| 2026-05 | 31 | 48.31 | 31 | 40.37 | 31 | 1.197 | 1.197 | 31 | 0.00 | 24.69 | 23.61 | 0.0 % | 51.1 % | 48.9 % |
| 2026-06 | 30 | 90.36 | 30 | 37.55 | 30 | 2.406 | 2.465 | 30 | 0.76 | 41.21 | 48.39 | 0.8 % | 45.6 % | 53.6 % |
| 2026-07 | 31 | 78.35 | 31 | 44.16 | 31 | 1.774 | 1.798 | 31 | 0.40 | 47.34 | 30.61 | 0.5 % | 60.4 % | 39.1 % |
| 2026-08 | 31 | 81.42 | 31 | 51.59 | 31 | 1.578 | 1.605 | 31 | 0.00 | 43.35 | 38.07 | 0.0 % | 53.2 % | 46.8 % |
| 2026-09 | 30 | 121.70 | 30 | 64.33 | 30 | 1.892 | 1.902 | 30 | 0.10 | 79.88 | 41.71 | 0.1 % | 65.6 % | 34.3 % |
| 2026-10 | 15 | 112.87 | 11 | 63.52 | 11 | 1.781 | 1.778 | 0 | — | — | — | — | — | — |

October 2026 is partial (to 15/10 for the spread, 11/10 for gas) and has no carbon month.

## Explanations tested

- **Gas-shock artefact.** Monthly ratio A against monthly gas, 2025 and 2026:

| month | gas mean | spread mean | ratio A |
|---|---|---|---|
| 2025-01 | 42.22 | 136.16 | 3.225 |
| 2025-02 | 42.65 | 59.81 | 1.402 |
| 2025-03 | 34.76 | 66.85 | 1.923 |
| 2025-04 | 29.17 | 61.66 | 2.114 |
| 2025-05 | 28.43 | 62.46 | 2.197 |
| 2025-06 | 29.72 | 74.58 | 2.509 |
| 2025-07 | 27.69 | 47.83 | 1.727 |
| 2025-08 | 27.12 | 56.07 | 2.068 |
| 2025-09 | 27.16 | 76.30 | 2.809 |
| 2025-10 | 26.84 | 76.91 | 2.865 |
| 2025-11 | 25.61 | 56.92 | 2.223 |
| 2025-12 | 24.49 | 46.16 | 1.885 |
| 2026-01 | 30.64 | 52.51 | 1.714 |
| 2026-02 | 27.33 | 39.65 | 1.451 |
| 2026-03 | 45.07 | 88.52 | 1.964 |
| 2026-04 | 38.83 | 79.20 | 2.039 |
| 2026-05 | 40.37 | 48.31 | 1.197 |
| 2026-06 | 37.55 | 90.36 | 2.406 |
| 2026-07 | 44.16 | 78.35 | 1.774 |
| 2026-08 | 51.59 | 81.42 | 1.578 |
| 2026-09 | 64.33 | 121.70 | 1.892 |
| 2026-10 | 63.52 | 112.87 | 1.781 |

  Read: where gas jumps month on month and the ratio falls in the same month and recovers after, the fall is the artefact Jomaux describes; the table is the record, the reading is etrmbiz's.

- **Solar depth.** The negative leg's share of the spread by year: 2022 0.3 %; 2023 0.6 %; 2024 0.9 %; 2025 0.6 %; 2026 to date 0.5 %. Whether that shows GB's lower ratio to be a solar-depth effect is a reading, not a finding, unless the share is material and rising.

## Scratch comparison (prior exposure, not results)

| figure | scratch 15/10 (unsealed, outside this repository) | declared measure | period here |
|---|---|---|---|
| September 2026 spread | 121.7 | 121.70 | 2026-09 |
| September 2026 gas | 64.5 | 64.33 | 2026-09 |
| 2026 to 14/10 spread | 77.5 | 77.65 | 2026 to date |
| 2025 same dates spread | 71.4 | 71.66 | 2025 same dates |
| 2026 to 14/10 ratio A | 1.79 | 1.789 | 2026 to date |
| 2025 same dates ratio A | 2.25 | 2.255 | 2025 same dates |
| September 2026 ratio A | 1.89 | 1.892 | 2026-09 |
| September 2025 ratio A | 2.81 | 2.809 | 2025-09 |

The scratch 2026 window ended 14/10; the declared one ends 15/10 (spread) and 11/10 (ratio, where gas ends). The scratch read took the printed day.

## Caveats, in the order the piece must carry them

1. SAP is a within-day system price (National Gas Transmission's On-the-Day Commodity Market), not the NBP day-ahead assessment; no free daily NBP day-ahead series was found.
2. The N2EX hourly auction is one of two GB day-ahead auctions.
3. 2022 is the first full year of the file and includes the crisis.
4. The merit-order proxy (2 × gas + 0.4 × carbon) is Jomaux's, uncalibrated for GB, on a monthly carbon price (gov.uk's CCM monthly average of the December UKA future's daily settlements) plus CPS 18; the boundary is coarse.
5. September 2026 on this measure is up 59.5 % on September 2025; Bloomberg says 80 %, Modo's "GBP 45 wider" implies 58.7 %. Unresolved; not resolved by picking the measure that matches Bloomberg.

## Expert corner

- Declaration `739471d07edd727f64805ba538d76ee7ec0cdc3960d6162851197a685b67a3e7`; sources: `govuk-ukets-ccm-monthly-average-prices` `932725ca74e4…` fetched 2026-10-15T18:44:29Z; `govuk-ukets-markets-guidance` `07cd65e8ab5c…` fetched 2026-10-15T18:52:19Z; `neso-n2ex-day-ahead` `ab8202a72eae…` fetched 2026-10-15T18:42:54Z; `neso-n2ex-day-ahead-resource-metadata` `4097147bf8cb…` fetched 2026-10-15T18:44:29Z; `ons-sap-gas-daily` `c84b724a9524…` fetched 2026-10-15T18:42:54Z; `ons-sap-gas-dataset-page` `58b37e4cd54b…` fetched 2026-10-15T18:44:30Z.
- The file prints 24 hours on every date including clock-change dates; the printed date is the primary unit, the local day the secondary. Hour labels `HH:00 - HH:00`; prices to six decimals, read as Decimals.
- Carbon months read: 2021-05 to 2026-09 (65); every month printed in several rows of the gov.uk tables printed one value (C3).
- `evidence/days.ndjson`: one line per unit and day (0 kept, 3706 added this run; C5 append-only). `evidence/format-check.json`: no departure from the schema pass.
- Reproduce: `uv run --group registers python investigations/024-the-gas-in-the-spread/run.py --phase compute --seal 739471d0`; tests `uv run pytest tests/test_gas_in_the_spread.py`; rule map `evidence/rule-sources.json`.

