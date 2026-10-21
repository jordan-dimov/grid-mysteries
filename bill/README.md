# The Balancing Bill record engine

Investigation 013's tracker as a governed record: every settlement day the
runner computed, under the rule version it computed it, so that a figure
once published cannot change without the change being a visible, refused
or new-versioned act. The kill test that justified it is `KILL-TEST.md`.

## Two layers

**The runner computes** (`investigations/013-the-cover-price-tracker/run.py`,
`src/grid_mysteries/investigations/cover_price.py`): from the pinned Elexon
and NESO bytes, under the sealed declaration and its frozen amendments, it
writes `evidence/tracker.json`, the tracker page and the public page. It
never proposes to any database, and on Render it only acquires.

**The record holds what was computed** (`bill-register.morph`, database
`grid_mysteries_bill`, never the research record's):

- `Day(day, rule, …)`: one settlement day under one rule version: the seven
  money figures every computed day carries, typed `Decimal[GBP]` and exact
  as the runner printed them, the sign verdict, the flag and the SHA-256
  over the digests of every artefact it was computed from. Beside it, one
  claim per block the declaration can leave blank, present only when
  computed: `DayGasOffer` (the DISPTAV type that reconciled, MWh and the
  three £/MWh figures), `DayBsad` (the first-kept populated L3 reading, its
  vintage, net £ and share) or `DayBsadPlaceholder` (a vintage read with no
  populated row: blank, never zero). A blank cell is the absence of a claim.
  Admitted once; no transformation alters or retracts any of them. A day
  recomputed under a new rule version is a second set beside the first.
- `DayRow(day, rule, …)`: the first shape, 26/09 to 21/10/2026, every figure
  as text with `-` for a blank; the twenty-two days computed before the
  amendment of 21/10/2026 hold it and are compared cell for cell. Closed:
  no act admits it (a claim keeps the shape it was admitted with; Morpholog
  migrates no claim to a new shape, and nothing here is backfilled).
- `RuleVersion`: `013-d20d5920-A1` (the declaration with Amendment 1 in
  force) for tracked days, `seed-012` for the eight days copied from 012.
- `Outcome` / `OutcomeRevision`: NESO's L1 and L4, first vintage kept, later
  differing vintages listed. `BsadRevision` / `BsadConfirmed`: Amendment 1's
  append-only L3 and the reading the next vintage reproduced, which decides
  T1.
- `Verdict(run, proposition, holds, detail)`: T1 to T4 as of each run.
- Each compute run imports as one `transact`: `open_run` (runs in date
  order, one open at a time), then only what is new, then `close_run`.
  `Run` names the tracker file by digest.

The importer (`src/grid_mysteries/bill/importer.py`) is pure in its plan:
a day the record holds identically, in either shape, costs nothing; a day
held under the same rule version with different figures is refused by name
before anything is proposed, and the kernel's `day_is_new` and
`day_not_held_in_the_first_shape` gates are the backstop. A row whose money
figures or sign verdict are blank is refused by name too: the second shape
has no placeholder for a figure every computed day carries. Each transact
is guarded by a recovery marker under `data/derived/bill/`, cleared only on
a positive non-commit.

## Running it (the laptop, by hand, after the runner has computed)

```bash
uv run python -m grid_mysteries.bill import                 # one transact; refuses an unprovisioned database first
uv run python -m grid_mysteries.bill checkpoint --witness   # signs; freetsa.org and DigiCert countersign
uv run python -m grid_mysteries.bill verify
```

`checkpoint` keeps the anchor under `bill/anchors/tree-<n>.json`, exports
the complete pack (NDJSON, Morpholog pack format 4) under
`data/derived/bill/packs/` and verifies it offline against the anchor with
the pinned key `trust/bill-2026.pub` and the TSA roots (`trust/tsa/roots.pem`). The private key
lives outside the repository (`~/.config/grid-mysteries/bill-signing-2026.pem`,
or `BILL_SIGNING_KEY`).

## Verify it yourself

```bash
morpholog audit verify-pack tree-<n>.ndjson --anchor-file bill/anchors/tree-<n>.json \
  --require-signing-key bill/trust/bill-2026.pub --trusted-tsa-file trust/tsa/roots.pem
```

## What it does not do

It does not recompute anything: Python measures the world, the record says
what was measured and refuses to let it be re-said. It does not hold the
pinned bytes, only their digests. It makes no claim beyond the declaration's.
