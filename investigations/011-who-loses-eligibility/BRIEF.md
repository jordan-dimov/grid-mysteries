# What the FPN rule does to a battery's response revenue — and what to ask the technical adviser instead

*One page for an investor or lender underwriting Dynamic Containment,
Moderation or Regulation revenue on a GB battery. Sources are the pinned
Ofgem decisions of June 2026, NESO's Response Services Service Terms v6
(effective 31 July 2026), the Elexon BM Unit register and NESO's EAC
results, all pinned by digest in 011 on 2026-09-04. Not published.*

## The rule as approved, not as reported

| what was reported | what the pinned text says | effect on a BM-registered battery |
|---|---|---|
| a battery with no valid FPN in a settlement period is deemed unavailable for that period | Service Terms 5.10: a BM Participating unit whose **registration FPN flag is set to FALSE** is deemed unavailable for all products **until the flag is reset**; Ofgem calls it a clarification against toggling between BMU and non-BMU status | none while the flag is TRUE; all 153 contracted battery BMUs had it TRUE at the pin |
| 80 % compliance over a rolling 28-day window as a condition of participation | Proposal 2, **effective 1 January 2027**: operational metering and baseline data at 80 % compliance over up to 28 EFA days before an auction; "mainly affects non-Balancing Mechanism Units" | none for BMUs, which already submit under the Grid Code |
| per-period and per-block deemed unavailability, 28-day suspension | Proposal 6 (Tiers 0–3) and Proposal 8 (suspension): **rejected** | none; Ofgem is open to a resubmission |

## No exposure clears the bar

The milestone test asked whether any unit, lead party or portfolio has
response revenue measurably at risk under the rule in force. The answer
is no:

| | post-rule window 2026-08-04..31 |
|---|---|
| battery BMUs holding response positions | 153 |
| gross availability held at clearing prices | £8,967,517 |
| deemed unavailable under the approved rule | 0 units, £0 |
| largest sensitivity (no PN published in a held period) | 1 unit, £13,892, 0.15 % of the fleet's revenue |

So a deal underwriting a BMU battery's DC/DM/DR stack is not repriced by
this decision. The press story should be struck from the diligence list.

## What a technical adviser would now be asked, and why public data cannot answer it

1. **Is every unit in the portfolio registered with its FPN flag TRUE,
   and does the SPA or O&M contract make keeping it TRUE someone's job?**
   The register shows the flag only at the moment it is read; it has no
   history. An adviser can obtain the registration record and any flag
   changes from the Lead Party; public data cannot.
2. **For non-BMU units, is operational metering and baseline submission
   ready for 1 January 2027 at 80 % compliance over the 28 EFA days before
   each auction?** This is the condition that can actually stop a unit
   being active in daily auctions, and it falls on the units Elexon
   cannot see. In the post-rule window 28 non-BMU battery units held
   about £101,000 of gross availability, roughly £1.3m a year at that
   rate; the largest participant, Gore Street Energy Trading, held about
   45 % of it, then Habitat Energy, Limejump, UK Power Reserve and
   Equinicity. No public series records any provider's submission rate,
   so compliance readiness is a question for the provider's own logs.
3. **Why did one BM-registered response unit publish no physical
   notification, export limit or import limit over its contracted
   periods, and stop taking positions after 6 August?** `E_GRFLB-1`
   (Conrad Energy (Trading) Ltd, 40 MW, embedded) is the only such unit
   in either window. It is not deemed unavailable under the rule and the
   sum is small. It is the kind of thing an adviser confirms with the
   route-to-market provider in an afternoon, and the kind of thing a
   public reconstruction can only flag.

## What this does and does not say

It says the approved rule catches no contracted battery BMU, and that the
binding change is a 2027 data duty on non-BMU providers. It does not say
what any provider actually submits, what NESO's control room received, or
what any unit earned. Every £ figure is gross availability at the clearing
price, before performance factors, and clearing prices can be negative.
