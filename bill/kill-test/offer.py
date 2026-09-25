"""Offer a tracker.json to the record: rows whose DayRow already stands
identically are skipped (an honest re-run); everything else is proposed.

    python3 offer.py rows.py tracker.json postgres:///db > offered.ndjson
"""

import json
import subprocess
import sys

rows_script, tracker, database_url = sys.argv[1:4]
proposals = subprocess.run(
    ["python3", rows_script, tracker], capture_output=True, text=True, check=True
).stdout.splitlines()
rows = [json.loads(line) for line in proposals if line.strip()]
claims = json.loads(
    subprocess.run(
        ["morpholog", "inspect", "claims", "--database-url", database_url, "--predicate", "DayRow"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
)
standing = {tuple(a["value"] for a in c["args"]) for c in claims}
offer = [r for r in rows if tuple(r["args_named"].values()) not in standing]
print(
    f"{len(rows)} rows, {len(rows) - len(offer)} already stand identically, {len(offer)} offered",
    file=sys.stderr,
)
for r in offer:
    print(json.dumps(r))
