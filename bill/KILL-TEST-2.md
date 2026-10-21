# The Balancing Bill as a record: kill test 2 (21/10/2026)

The first kill test (`KILL-TEST.md`, 25/09/2026) showed the kernel refusing,
by day, what the runner rewrote without a word. The amendment of 21/10/2026
gave the record a typed second shape (`Day`, `DayGasOffer`, `DayBsad`,
`DayBsadPlaceholder`: every figure with its unit, a blank cell no claim at
all). The question tonight: **can the record now say which figure moved,
rather than only that a day did?** And, a month on, does an honest
recompute still move anything?

## Method

A throwaway database, the live programme, the committed `evidence/tracker.json`
(run of 26/09/2026, 22 days) imported through the real importer, so every
day stands in the second shape. Then, in a scratch checkout of `8840d06`
with the pinned bytes linked in and the acquisition journals copied beside
them, the runner recomputed with `--run-date 2026-10-21`:

- **arm A**, the committed code;
- **arm B**, one constant changed: the volume gate's reconciliation tolerance
  from 0.1 % to 5 % (`RECONCILE_TOLERANCE`), the first test's alteration;
- **arm C**, synthetic: the committed file with one penny added to 22
  September's net, its BSAD share nudged by 0.0001, and 21 September's
  premium lowered by £1/MWh. Not a run of the runner; the shape of a refusal
  when a figure, not a block, moves.

Each arm was offered twice. Through the importer, which compares before it
proposes (`bill import --tracker`). And straight to the kernel, under a
scratch programme (`kill-test-2/bill-register-reaffirm.morph`: the live
programme plus three `reaffirm_*` acts whose gates each compare one offered
figure with the one the record holds; `kill-test-2/offer.py` turns a tracker
into those proposals in the tagged codec). A reaffirmation commits when the
block is identical, is refused by the gate that names the figure when it
moved, and fails its bind when the record holds no such block.

## Measured

| | the runner | the importer | the kernel, per block |
|---|---|---|---|
| committed file offered back (control) | n/a | every day unchanged | 52 blocks identical |
| **arm A**: same code, recomputed 25 days later | writes 43 rows, exit 0 | 21 new days (batches 3 to 5) added, **22 unchanged** | 52 identical; 63 binds fail, the 21 days the record does not yet hold |
| **arm B**: tolerance 5 % | writes 43 rows, exit 0: 13 and 22 September gain a DISPTAV type and a price | refused by name before anything is proposed: 13 and 22 September | 52 identical; `DayGasOffer` for 13 and 22 September **matched no candidates**: the record holds no gas-offer block for those days, so the offered one is a block gained, not a figure moved |
| **arm C**: three figures nudged | n/a | refused by name: 21 and 22 September | `premium_unchanged: record 73.87 GBP_per_MWh = offered 72.87 GBP_per_MWh`; `net_unchanged: record 2173461.081898841825635069 GBP = offered 2173461.091898841825635069 GBP`; `bsad_share_unchanged: record 0.2180 = offered 0.2181` |

The rejection log of the throwaway record held 100 refusals, each naming the
day, the block and the gate.

## Verdict

**The record now names the figure, with its unit and both values.** A
moved figure is refused by the gate that compares it; a block the runner
newly produces (arm B) is refused as a block the record does not hold, which
is the right answer, since the declaration's reconciliation gate, not a
figure, is what the altered tolerance changed. Nothing is written in any
case.

**An honest recompute moves nothing.** Arm A is the finding the first test
could not give: on 25/09 the same code recomputed six days later rewrote 8
of 15 rows (the floating L3 reading). With 013 Amendment 1 in force, the
same code recomputed 25 days later leaves all 22 committed days byte for
byte as the record holds them, and adds the 21 days of batches 3 to 5
cleanly in the second shape. The importer's "a day the record holds
identically costs nothing" is now exercised on real recomputed rows, not
only on the same file offered twice.

## What the test found about 013 itself, which matters before batches 3 to 5

**NESO renamed the columns of its daily balancing volume file in the vintage
of 16/10/2026**: `Energy Imbalance (MWh)`, `Constraint Offers (MWh)` and the
rest lost their parentheses (`Energy Imbalance MWh`, …). The 31 vintages from
15/09 to 15/10 carry the old header; the six from 16/10 to 21/10 the new. The
runner reads L1 and L4 from every pinned vintage in order, so on the laptop
today `--phase compute` fails with `KeyError: 'Constraint Offers (MWh)'`
before writing anything. Arms A and B were computed on the vintages to
15/10 only. This is the format check of the doctrine firing as a crash
rather than a named refusal: the declaration's reading rule names those
columns, and no frozen amendment reads the new spelling. Batches 3 to 5
cannot be computed until the sponsor amends the reading (a dated amendment
that maps the new header to the old names, applied from the vintage that
introduced it), and nothing here decides that.

## Not measured

Whether a reaffirmation act belongs in the live programme. It would make
"this figure still stands" a recorded act with a witness, which a receipt
for a published figure might want; tonight it was a scratch instrument, and
the live programme is unchanged.
