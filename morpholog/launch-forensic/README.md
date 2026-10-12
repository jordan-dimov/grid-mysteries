# Putting the forensic freezes into the record: v3 launch rows (12/10/2026)

Until today the forensic investigations from 012 onward were frozen by
`scripts/freeze` (git plus OpenTimestamps and RFC 3161) and nowhere else.
The v3 record held nine declarations, all from August's forward work. These
rows put every forensic declaration and amendment frozen since 012 into the
record. Generated from the files on disk: each `content_digest` is the
file's SHA-256 and each `declared_at` is the commit that froze it (the
proof sidecar's first commit; for 012 and 013, whose proofs sit elsewhere,
the file's first commit).

| step | actor | file | what it does |
|---|---|---|---|
| M1 | machine | `M1-declare.v3.ndjson.template` | 31 `declare` rows, kind `forensic_study`: 012, 013 (+ T4, amendment 1), 014 v1 to v4, 015 v1 and v2, 017 v1 to v3 (+ v3 amendment 1), 018 (+ amendment 1), 019 (+ amendments 1 and 2), 020 (+ amendments 1 to 4), 021, 022 (acquisition, amendment 1, declaration, amendments 2 and 3), 023 |
| H1 | **human** | `H1-seal.v3.ndjson.template` | 31 `seal_declaration` rows; `{SEALED_AT}` is the wall-clock time of sealing |
| M2 | machine | `M2-verdicts.v3.ndjson.template` | 8 falsifier verdicts from 12/10/2026, each a `#gate` verdict whose `about` names the falsifier: 023 F1, F2, F4 pass and F3 fail; 020 version 1 F4 fail under amendment 3, then F1, F2, F4 pass under amendment 4 |

The batch is `morpholog/batches/130-forensic-launch.v3.ndjson`. Run each
step with `scripts/launch-forward <step-file> 130-forensic-launch.v3.ndjson`:
M1 and M2 with `DATABASE_URL=postgres://gm_machine@localhost/grid_mysteries_morpholog`,
and H1 by Jordan:

```
! DATABASE_URL=postgres://gm_human@localhost/grid_mysteries_morpholog scripts/launch-forward morpholog/launch-forensic/H1-seal.v3.ndjson.template 130-forensic-launch.v3.ndjson
```

**What sealing after the fact means.** As with the August launch: these
files were frozen by git and external witnesses on the dates recorded, and
their computes ran afterwards. Sealing them now records their digests in the
Merkle-chained audit log, with a `sealed_at` later than the work. The record
will say, truthfully, that forensic seals were git and witnesses until
12/10/2026 and the record from then on. **From here, a freeze is complete
only when its declaration is sealed by the human login.** That is the
answer to today's question of whether another session's message counts as
the sponsor's word: in the record, a machine login cannot seal at all
(`seal_requires_declaration_authority`).

**Verdicts.** v3's stage vocabulary was written for forward work. A
forensic falsifier is recorded at stage `#gate` with `about` naming it
(`023/F3`), `#fail` when it fires and `#pass` when silent; the reason says
which. Earlier investigations' falsifier outcomes (011 to 022) are not
backfilled here: each needs its RESULTS read row by row, not recalled.

**Rehearsed** 12/10/2026 on a throwaway cluster (port 55439) after a fresh
`replay-research`: M1 31, H1 31 and M2 8 rows all commit, and the machine
login proposing a seal is refused by name. Every sealed digest resolves to a
file under `check-record`'s patterns, which now include `AMENDMENT-*.md` and
`ACQUISITION*.md`.

Not included: `identity/IDENTITY-DESIGN.md` (frozen 30/09) lives outside
`investigations/`, where `check-record` does not look; it goes in with the
identity register's build.
