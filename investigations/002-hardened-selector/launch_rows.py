"""Emit Investigation 002's governed opening rows, ready for scripts/record.

    uv run python investigations/002-hardened-selector/launch_rows.py

Prints one NDJSON row per line: open the inquiry, record v1 lineage,
assign the reserved corpus, declare the protocol (digest computed from
the committed declaration, never typed), and declare each Decimal
parameter. Generating them removes the hand-edited-JSON step that has
failed before, and guarantees the digest matches the bytes on disk.

Emitting is not proposing: these rows reach the record only through
`scripts/record`, and nothing here can seal anything.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from selection import INQUIRY, PARAM_MIN_ACCEPTED_MWH, PARAM_MIN_AVAILABLE_MW

from grid_mysteries.hashing import sha256_file

DECLARATION = Path(__file__).resolve().parent / "README.md"
CORPUS = "corpus-2026-08-w2"
LINEAGE_V1 = "inv-001-largest-apparent-inversion"
TITLE = "Mystery 002 - what survives a hardened selector on an untouched week"
MACHINE_ACTOR = "claude_fable_5"

#: Declared in README.md's candidate definition; the governed record holds
#: the authoritative copy and `selection.py` reads it back from there.
PARAMETERS = {
    PARAM_MIN_ACCEPTED_MWH: Decimal("0.01"),
    PARAM_MIN_AVAILABLE_MW: Decimal("1"),
}


def rows(now: str) -> list[dict]:
    digest = sha256_file(DECLARATION)
    return [
        {
            "transformation": "open_inquiry",
            "actor": MACHINE_ACTOR,
            "args_named": {
                "inquiry": INQUIRY,
                "kind": "prospective",
                "title": TITLE,
                "opened_at": now,
            },
        },
        {
            "transformation": "record_v1_lineage",
            "actor": MACHINE_ACTOR,
            "args_named": {"inquiry": INQUIRY, "v1_investigation": LINEAGE_V1},
        },
        {
            "transformation": "assign_corpus",
            "actor": MACHINE_ACTOR,
            "args_named": {"inquiry": INQUIRY, "corpus": CORPUS},
        },
        {
            "transformation": "declare_protocol",
            "actor": MACHINE_ACTOR,
            "args_named": {
                "inquiry": INQUIRY,
                "protocol_digest": digest,
                "declared_at": now,
            },
        },
        *[
            {
                "transformation": "declare_parameter",
                "actor": MACHINE_ACTOR,
                "args_named": {"inquiry": INQUIRY, "name": name, "parameter_value": str(value)},
            }
            for name, value in PARAMETERS.items()
        ],
    ]


if __name__ == "__main__":
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    for row in rows(stamp):
        print(json.dumps(row))
