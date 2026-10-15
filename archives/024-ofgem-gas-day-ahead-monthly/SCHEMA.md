# Schema report: 024-ofgem-gas-day-ahead-monthly

`data/raw/ofgem/024/wmi-gas-day-ahead-monthly-everviz-inject-YFsS4g98P-2026-10-15.js` (SHA-256 `a304e0726a41a838d71b31d913c3505fa611a4e79b4392ec97871463e527ff57`), the everviz inject script Ofgem's data portal renders for chart node 175055 (`data/raw/ofgem/024/wholesale-market-indicators-page-2026-10-15.html`, SHA-256 `f8a6aef72fec57d4a19c01c8f780d8c521a9928af266030fadfe181d9828f112`, chart key `YFsS4g98P`). Chart title as printed: 'Gas Prices: Day Ahead Contracts - Monthly Average (Great Britain)'; credits: 'Ofgem analysis of broker data'; y-axis title: 'p/therm (GBp)\n'. Written by `run.py --phase schema-cross-check`; no value is read.

Embedded CSV: header `Category`, `Price`; 201 rows from `10/01/2009` to `06/01/2026` (month/day/year, the month's first day); date forms {'us-date-first-of-month': 201, 'other': 0}; price forms {'decimal': 201, 'other': 0}.

Ofgem's description of the chart, from the page:

    This chart shows the average price of gas for next day delivery on the wholesale market in Great Britain (England, Scotland and Wales). This does not include Northern Ireland. The data until 28 February 2021 comes from a third-party Price Reporting Agency’s price assessment of over-the-counter trading through brokers. See full explanation of that methodology here . From 1 March 2021, the data is Ofgem analysis of broker data and is an average monthly price weighted by volume. The data is averaged by month and covers around a 16-year time period.

