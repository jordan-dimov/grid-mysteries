# Date structure: 024-ons-sap-gas

`data/raw/ons/024/systemaveragepriceofgasdataset151026.xlsx` (SHA-256 `c84b724a95245987e111d3c14f3f1c5a95b0ca997053d769af04c959c234b72e`), sheet `1.Daily SAP Gas`, header on row 5: `Date`, `SAP actual day`, `SAP seven-day rolling average`. 3,206 body rows, 3,206 with a date cell in column A, from 2018-01-01 to 2026-10-11; duplicate dates 0; dates missing inside the range: none; times on the date cells: 00:00:00. Written by `run.py --phase schema`; no price is read.

Forms of the `SAP actual day` cells: number 3206.

