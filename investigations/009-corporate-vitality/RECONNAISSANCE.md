# 009 — corporate vitality of the TEC queue: schema-only reconnaissance (2026-08-27)

Seeded by an incidental observation in 008/J2: a dissolved company
(`ORGANIC POWER LTD`, 03432968) still holds a Scoping position in the TEC
register. Mandate: determine, **without reading any new Companies House
outcome**, whether a pre-declared test can estimate how much
transmission-contracted MW sits with corporate entities carrying strong
public evidence of inactivity.

## What was touched

TEC side: the register archive (identity, status, MW — cohort sizing only).
Companies House side: the **field names** of the 31 profile objects and 62
charge objects pinned by J2 (keys only, no values read), and the official
enumerations (`api-enumerations/constants.yml`,
`filing_history_descriptions.yml`). No company was looked up.

## Companies House facts available per company (profile endpoint)

`company_status` ∈ {active, dissolved, liquidation, receivership,
converted-closed, voluntary-arrangement, insolvency-proceedings,
administration, open, closed, registered, removed};
`company_status_detail` ∈ {active, dissolved, converted-closed,
transferred-from-uk, **active-proposal-to-strike-off**,
petition-to-restore-dissolved, …}; `date_of_creation`; `date_of_cessation`;
`accounts.overdue`, `accounts.next_due`, `accounts.last_accounts.type`
(includes **dormant**), `confirmation_statement.overdue` / `next_due`;
`has_insolvency_history`; `has_been_liquidated`; `previous_company_names[]`
(name, effective_from, ceased_on); `registered_office_is_in_dispute`;
`undeliverable_registered_office_address`. Filing history (separate
endpoint) gives **dated** items with description keys including
`gazette-notice-voluntary` / `gazette-notice-compulsory` (first Gazette),
`gazette-dissolved-*` (final), `gazette-filings-brought-up-to-date`
(compulsory strike-off discontinued), `liquidation-*`,
`liquidation-administration-*`, `accounts-with-accounts-type-dormant`.

Every state in the declaration's hierarchy is therefore an objective,
machine-readable, and — for the leading-indicator test — **dated** fact.

## TEC cohorts (sized now, before any fetch)

| cohort | how keyed | rows | MW | distinct customers |
|---|---|---|---|---|
| **Scoping ≥ 3 years**, present in the 2026-08-22 register, never advanced | 005 name key, `first_observed` ≤ 2023-08-22 | **229** | **64,325** | **164** |
| **Built / Under Construction** in the 2026-08-22 register | register status | **393** | **79,379** | **275** |
| Scoping < 3 y or advanced (excluded) | 005 name key | 703 | 232,770 | 467 |
| Scoping rows with no pre-hole archive history (first seen 2026; < 3 y by construction; excluded) | — | 552 | 212,877 | — |
| **Disappeared while Scoping**, current Project-ID regime (IDs first seen ≥ 2024-04, vintages 2024-04-02 → 2026-08-25), observed ≥ 6 months | Project ID | **73** (114 incl. < 6 m) | 44,606 (all 114) | 84 (all 114) |
| Present Scoping, same regime (control pool) | Project ID | 1,426 | 514,519 | 928 |

Stage MW = |`MW Increase / Decrease`| if non-zero, else `MW Connected`,
else `Cumulative Total Capacity`. The sponsor's "80 GW Scoping ≥ 3 y"
guess is 64 GW on this key.

Identity facts that shape the test: NESO's `Project ID` changes regime
(1,713 + 1,744 new IDs in 2024-04/05 are a Salesforce re-key, not new
projects), so Project-ID disappearance is only meaningful **within** the
current regime; the archive hole 2025-07-22 → 2026-05-19 makes 27 of the
disappearances datable only to a ten-month window; name-keyed
disappearance across eras is 72–86 % identity churn (007/T2) and is not
used.

## Cost

~440 distinct customer names → ~440 searches + ~440 profiles + filing
histories for every resolved company in the two leading-indicator arms
(~84 + 150) and for every strong-signal company in the materiality arms.
About 1,300 calls, ~12 minutes at the documented rate limit.
