# 022 — Amendment 3 to the declaration: the page that reports a financial year

**Status: drafted 2026-10-01 (night) after amendment 2 was computed
(`0192909`) and before the sponsor read its `FINDINGS.md`; not frozen.
On the sponsor's word it is frozen with `scripts/freeze` and `compute`
runs under `--amendment-seal <prefix of this file's SHA-256 as frozen>`,
the rule version becoming `b8e6d53b.3d937633.<this file's prefix>`; the
rows under `b8e6d53b` and under `b8e6d53b.3d937633` remain in the evidence
as computed.** `DECLARATION.md` and `AMENDMENT-2.md` are not edited.

## The defect amendment 2 produced

Amendment 2's R-R5(f2) read a fund's financial-year outturn from a page
that states a period, when the stated period is a year. HEIT's
net-asset-value and trading updates of 2025-02-26 (`…/net-asset-value-and-trading-update/8752688`
and its replacement `…/8753297`) report the quarter to 31 January 2025
but state, earlier on the page, the financial year ended 31 October 2024
whose results were published the same day. The rule anchored their
quarter's figures to that year: `£97.8k/MW/Yr` ("Portfolio revenues of
£9.7 million (£97.8k/MW/Yr) for the Period") five times across the two
pages, and the previous quarter's `£62.4k/MW/Yr` twice, beside the
results RNS's own `£58.2k/MW/Yr` ("Total net revenue generation for the
Period was £16.3 million (£58.2k/MW/Yr) based on a weighted average
operational capacity of 280.4 MW", `…/results-for-financial-year-ended-31-october-2024/8752544`).
R-M2 then took the first of equal overlaps, `£97.8k`, for the lead row.
The defect was found by the author on reading the rendered table before
the sponsor did, and is recorded in the commit that computed it.

## The rule restated (R-R5(f2), second sentence)

A page reports a financial year's outturn only if its **title names the
full-year results** (`Results for Financial Year`, `Final Results`,
`Full-Year Results`, `Annual Results`, `Annual Report`, or a financial
year ended), whatever kind of period the page states (`year ended`,
`financial year ended`, `twelve months ended`, `period ended`). A page
whose title does not (a trading update, a NAV announcement, an interim)
has its "for the Period" figures listed as a stated period that is not a
year, not compared. Amendment 2 attached the title condition to the kind
`period` only; this amendment attaches it to every kind. `previous
quarter` joins the partial markers. The period words (`for/over/during/in/
throughout the period`, `the year`, `the financial year`) are looked for
in the figure's clause or the clause before it, as the subset words
already are, so "During the Period, the portfolio generated total revenue
of £9.9 million (equating to £99k / MW/Yr)" on HEIT's results for the year
ended 31 October 2023 is that year's outturn. Nothing else changes: R-M2 still
lists the fund's assumption against its own financial-year outturn with
the overlap in months, both figures printed, nothing adjusted, the fleet
outturn beside it.

Under this rule HEIT's year to 31 October 2024 has one outturn, `£58.2k`
per MW per year from the results RNS (printed twice there, one figure),
and the lead row reads: HEIT assumed £123,000 for calendar 2024, excluding
the Capacity Market; its own outturn for the year to 31 October 2024 was
£58,200; ten of twelve months overlap; nothing adjusted. The verdicts are
unchanged.
