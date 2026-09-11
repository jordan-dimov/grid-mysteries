# The record day, reconstructed (draft, not published)

*Grid Mysteries 012. Draft of 2026-09-11; awaiting the second seal.*

On 8 September 2026, Kilowatts' *Dispatches* called it the most expensive
day of constraint management in at least five years, and said something
that cuts against the usual headline: most of the money did not go to
wind farms to switch off. It went to gas plant to switch on.

We did not take the post's word for it. We froze a method before looking
at a single September row, let a rule pick the day, and rebuilt the bill
from Elexon's published cashflows.

## What the rule picked

The rule: of 1–8 September, take the day with the highest total published
Balancing Mechanism cashflow. It picked 8 September, with 4 September
second, which is what the post implied. Both predictions were written
down before the data was fetched.

## Where the money went on 8 September

Money paid out to units in the Balancing Mechanism: **£33.6m**.

- **£3.8m (11 %)** to wind units, on bids, for reducing output.
- **£26.8m (80 %)** to gas units, on offers, for increasing output.
- **£3.0m (9 %)** to everything else, led by biomass units (£1.1m) and units
  the register gives no fuel type (£1.1m).

The post's "roughly 10 % and 90 %" is 11 % and 80 % in the published
cashflows. Its gas price of £231/MWh comes out at £229.53. Its 117 GWh of
gas turn-up comes out at 115–117 GWh depending on which Elexon volume
field you trust (more on that below).

## What the trackers do not see

The Balancing Mechanism is not the whole bill. NESO also buys adjustment
actions outside it, published later as Disaggregated BSAD. For 8
September those net to **£3.3m**, a tenth again on top of the
in-mechanism money. On 4 September they were £1.5m, under 5 %. So on the
record day the Balancing-Mechanism-only figure is a floor, and it is not
a small one; on the runner-up it is nearly the whole story.

## Why the post's totals are lower than ours

The post's total for 8 September is £29.65m. The Balancing Mechanism's
own net figure (money out minus money in) is £31.6m; gross money out is
£33.6m. Over the eight days the post's £130.2m and the Wasted Wind
tracker's £128.8m sit 8 % under the mechanism's net total and 18 % under
the gross. The post nets or excludes something it does not name. We
cannot say what from here. We can say its number is a cut of the
mechanism's spend, not a ceiling on it, and that it leaves out the £3.3m
outside.

## The thing we got wrong, on purpose left in

Our frozen method paired cashflows with Elexon's "Original" acceptance
volumes. That works for offers. For bids it does not: on 8 September the
"Original" rows carry 25 GWh of accepted bids against 144 GWh in the
settlement totals. The rows typed "Tagged" carry 144 GWh, and 119 GWh of
that is on wind units, beside the post's 114 GWh curtailed. We report
what the frozen rule produced, label it as not reconciling, and show the
"Tagged" figures as a sensitivity. The rule is not rewritten for this
window. The lesson goes into the next declaration.

## What this does not say

Nothing here attributes money to a transmission boundary; no public
mapping from units to boundaries exists. Nothing here is a saving or a
loss. Cashflows are indicative and pre-settlement. And whether 8
September is a record needs windows we did not open.

*Method, thresholds, falsifiers and every artefact digest are in the
investigation folder. The declaration was sealed before the fetch; its
hash is in the command that ran it.*
