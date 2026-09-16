# 015 — amendments and dated notes

`DECLARATION.md` is frozen (SHA-256 `77a192f1…`, witnessed 2026-09-16).

## Code correction, not amendment — 2026-09-16: import hours took the sign of MDB levels

The first compute divided MDB levels, which Elexon publishes as negative
numbers (import), by the import capacity's magnitude, so every import hour
in `storage.json` was negative. The declaration's rule is a magnitude
("the maximum MDB level divided by its import capacity"); the code now
takes both by magnitude and the energy bound by largest magnitude.
Recomputed from the same pinned bytes: only the import-hour columns
change sign; no export figure, link, scheme total or proposition moves.
Found by the sponsor's reconciliation, together with two wording changes
in `RESULTS.md` (hours quoted for the whole set and for the north; "ten
carried negative bid rows, five netted negative").
