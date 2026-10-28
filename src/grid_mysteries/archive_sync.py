"""What an archive sync may commit, decided from the working tree alone.

The watchdog (`scripts/check-vintages`) writes into the repository and leaves
the commit to a person: each day's capture manifest with its five proof files,
OpenTimestamps proofs it upgraded in place, and the 013 tracker's grown state.
`scripts/archive-sync` commits exactly that, after checking it, and refuses
anything else in the working tree by name. This module is the pure part:
which changed path is which, and whether a grown file only grew.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Final

#: The proof files `scripts/timestamp` writes beside every stamped file.
PROOF_SUFFIXES: Final = (".ots", ".tsq", ".freetsa.tsr", ".digicert.tsr", ".timestamps.json")
_MANIFEST: Final = re.compile(r"^data/manifests/(\d{4}-\d{2}-\d{2})\.ndjson(.*)$")
#: State files the 013 tracker appends to; a sync commits them only if they grew.
GROWN: Final = (
    "investigations/013-the-cover-price-tracker/evidence/acquisition-log.json",
    "investigations/013-the-cover-price-tracker/evidence/neso-manifest.json",
)
_BATCH: Final = re.compile(
    r"^investigations/013-the-cover-price-tracker/evidence/batch-\d{2}-manifest\.json$"
)


@dataclass
class Plan:
    #: day -> the files of that day's manifest found new (manifest and proofs).
    days: dict[str, set[str]] = field(default_factory=dict)
    upgraded_proofs: list[str] = field(default_factory=list)
    grown: list[str] = field(default_factory=list)
    batches: list[str] = field(default_factory=list)
    #: (path, why) for everything a sync must not commit.
    refused: list[tuple[str, str]] = field(default_factory=list)

    def incomplete_days(self) -> dict[str, list[str]]:
        """Days missing the manifest or any of its five proof files."""
        out = {}
        for day, files in self.days.items():
            want = {f"data/manifests/{day}.ndjson"} | {
                f"data/manifests/{day}.ndjson{s}" for s in PROOF_SUFFIXES
            }
            if missing := sorted(want - files):
                out[day] = missing
        return out

    def paths(self) -> list[str]:
        return sorted(
            {p for files in self.days.values() for p in files}
            | set(self.upgraded_proofs)
            | set(self.grown)
            | set(self.batches)
        )


def classify(changes: list[tuple[str, str]]) -> Plan:
    """Sort `git status --porcelain` entries, as (status, path), into a plan.
    Status `??` is untracked, `M` modified; anything else is refused."""
    plan = Plan()
    for status, path in changes:
        manifest = _MANIFEST.match(path)
        if status == "??" and manifest and manifest[2] in ("", *PROOF_SUFFIXES):
            plan.days.setdefault(manifest[1], set()).add(path)
        elif status == "M" and path.endswith(".ots"):
            plan.upgraded_proofs.append(path)
        elif status == "M" and path in GROWN:
            plan.grown.append(path)
        elif status == "??" and _BATCH.match(path):
            plan.batches.append(path)
        else:
            plan.refused.append((path, f"{status}: not something an archive sync commits"))
    return plan


def only_grew(before: bytes, after: bytes) -> bool:
    """True if `after` keeps everything `before` held: see `grew`."""
    return grew(json.loads(before), json.loads(after))


def grew(old: object, new: object) -> bool:
    """An object keeps every key and each value only grows; a list keeps its
    old entries unchanged, in order, at its start (records are appended, never
    edited); anything else is unchanged."""
    if isinstance(old, dict) and isinstance(new, dict):
        return all(k in new and grew(v, new[k]) for k, v in old.items())
    if isinstance(old, list) and isinstance(new, list):
        return new[: len(old)] == old
    return bool(old == new)
