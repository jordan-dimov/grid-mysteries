# 006 — amendments and working notes

`DECLARATION.md` is frozen (commit `0d8a470`, digest `be3cce73…`).

## Amendment 1 — 2026-08-26: works completion dates are not in the disclosed TWR; a proxy is declared before any join or slip is computed

**Recorded after inspecting the structure of four TWR vintages (headers,
row counts, how many distinct dates a project and a scheme carry) and
before any join, any revision count or any slip value was computed.**

What the FOI-25-133 material is: 31 workbooks, 2017-05-04 → 2025-10-03,
roughly quarterly, each listing **project → scheme** rows — the customer,
project, connection site, a scheme (works) identifier such as
`SHET-RI-025c`, its description, and a date column ("Connection Date",
later "MW Effective From"). That date is the **project's** connection date
repeated on every scheme row: in the 2017-05-04, 2021-01-06, 2023-06-01
and 2025-10-03 vintages, 0, 2, 11 and 20 projects respectively (of 173,
268, 759 and 1,299) carry more than one distinct date, while single
schemes attached to many projects carry many dates (the 2025 vintage has
681 such schemes; `SHET-RI-025c` is attached to 43 projects). The
declaration assumed per-works completion dates, as CUSC describes the
TWR; the disclosed reports do not carry them.

**The proxy, declared now.** In each TWR vintage, a scheme's *effective
completion date* is the **earliest connection date among the projects that
depend on it** — works must be complete by their first dependent's date.
The works history, `slipped_before(t)`, is then a later move of ≥ 6 months
in that minimum across TWR vintages published before t. Two ambiguities
are recorded rather than resolved: the minimum can move later because the
works slipped **or** because the earliest dependent project withdrew or
re-dated; and shared schemes (F-4) make the proxy a property of a
substation's works programme rather than of one project. T4's F-1
clustering check applies to the proxy unchanged.

Everything else in the declaration — join rule, population, attribution
windows, T1–T4, thresholds, kill conditions — is unchanged. Under
Generator v4 §3 this is a substitute symptom on the same causal chain,
selected on metadata before outcome values were seen, with the rejected
original preserved above.

**Scheme identity across eras.** Identifiers drift: `SHETL-RI-089` (2017)
becomes `SHET-RI-089` (2021+); some early schemes are numeric
(`32313SI`, `33585`); placeholder rows are labelled `Blank` or `Works`.
Normalisation: upper-case, whitespace collapsed, `SHETL-` → `SHET-`;
placeholders excluded. Recorded before use.

**Join keys.** TEC vintages from 2023-02 carry `Project No` / `Project
Number`; TWR vintages from 2023 carry `Project Number` (`PRO-nnnnnn`).
Where both are present the exact number is used; otherwise the declared
(customer, site) then (project name, site) normalised match.
