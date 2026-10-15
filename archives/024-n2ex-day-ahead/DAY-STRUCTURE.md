# Day structure: 024-n2ex-day-ahead

`data/raw/neso/024/n2ex-day-ahead-dump-2026-10-15.csv` (SHA-256 `ab8202a72eae9716964dcf334915776c38c46a8f0ebf0e602ce1f5be49295adc`): 44,448 rows, columns `Date`, `Delivery Period`, `Price`; 1,853 printed dates from 2021-09-20 to 2026-10-16, none missing inside the range: True. Written by `run.py --phase schema`; no price is read.

Rows per printed date: 2 rows on 1 dates, 22 rows on 1 dates, 24 rows on 1851 dates.

Period labels, in order of first appearance (24): `22:00 - 23:00`, `23:00 - 00:00`, `00:00 - 01:00`, `01:00 - 02:00`, `02:00 - 03:00`, `03:00 - 04:00`, `04:00 - 05:00`, `05:00 - 06:00`, `06:00 - 07:00`, `07:00 - 08:00`, `08:00 - 09:00`, `09:00 - 10:00`, `10:00 - 11:00`, `11:00 - 12:00`, `12:00 - 13:00`, `13:00 - 14:00`, `14:00 - 15:00`, `15:00 - 16:00`, `16:00 - 17:00`, `17:00 - 18:00`, `18:00 - 19:00`, `19:00 - 20:00`, `20:00 - 21:00`, `21:00 - 22:00`.

Repeated (date, label) keys: 0.

Dates without exactly 24 distinct labels:

| date | rows | missing labels | repeated labels |
|---|---|---|---|
| 2021-09-20 | 2 | 00:00 - 01:00, 01:00 - 02:00, 02:00 - 03:00, 03:00 - 04:00, 04:00 - 05:00, 05:00 - 06:00, 06:00 - 07:00, 07:00 - 08:00, 08:00 - 09:00, 09:00 - 10:00, 10:00 - 11:00, 11:00 - 12:00, 12:00 - 13:00, 13:00 - 14:00, 14:00 - 15:00, 15:00 - 16:00, 16:00 - 17:00, 17:00 - 18:00, 18:00 - 19:00, 19:00 - 20:00, 20:00 - 21:00, 21:00 - 22:00 | none |
| 2026-10-16 | 22 | 22:00 - 23:00, 23:00 - 00:00 | none |
