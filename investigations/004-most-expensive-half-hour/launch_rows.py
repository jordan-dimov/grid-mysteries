"""Emit Investigation 004's governed opening rows, ready for scripts/record.

    uv run python investigations/004-most-expensive-half-hour/launch_rows.py

Generated rather than hand-typed so the protocol digest always matches
the bytes of the committed declaration on disk. Emitting is not
proposing: these rows reach the record only through `scripts/record`,
and nothing here can seal anything.

Two deliberate differences from 002's opening:

- **kind is `descriptive`.** The declaration's own framing is "the
  question is an event, not a methodology": 004 reconstructs a half-hour
  rather than testing a selector out of sample. Verified before choosing
  that this is an honest label and not a way past
  `prospective_corpus_unexposed` — `morpholog explain` confirms
  corpus-2026-06 is assignable to a *prospective* inquiry too, because
  June overlaps no consumed window.
- **no DeclaredParameter rows.** The frozen rule is "highest published
  Constraints value", which has no tunable threshold. Declaring a
  parameter that does not exist would be governance theatre.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from grid_mysteries.hashing import sha256_file

DECLARATION = Path(__file__).resolve().parent / "README.md"
INQUIRY = "inq-004"
CORPUS = "corpus-2026-06"
TITLE = "Mystery 004 - Britain's most expensive half-hour"
ACTOR = "claude_fable_5"


def rows(now: str) -> list[dict]:
    return [
        {
            "transformation": "open_inquiry",
            "actor": ACTOR,
            "args_named": {
                "inquiry": INQUIRY,
                "kind": "descriptive",
                "title": TITLE,
                "opened_at": now,
            },
        },
        {
            "transformation": "assign_corpus",
            "actor": ACTOR,
            "args_named": {"inquiry": INQUIRY, "corpus": CORPUS},
        },
        {
            "transformation": "declare_protocol",
            "actor": ACTOR,
            "args_named": {
                "inquiry": INQUIRY,
                "protocol_digest": sha256_file(DECLARATION),
                "declared_at": now,
            },
        },
    ]


if __name__ == "__main__":
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    for row in rows(stamp):
        print(json.dumps(row))
