"""The vintage archive as a source: read a captured copy by manifest line
and pin it like any other artefact.

Given a day and a dataset, find the manifest line the capture job wrote,
read the bytes (from S3 with the analysis reader, or from the local
mirror), verify them against the line's digest, and write them under
`data/raw/` with a journal entry that names the archive key and the day
the copy was held. A copy the archive holds is then a legitimate source
for a declaration frozen after that day.
"""

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from grid_mysteries.capture.run import manifest_key
from grid_mysteries.capture.store import ObjectStore


class ArchiveError(RuntimeError):
    pass


class Archive:
    def __init__(self, store: ObjectStore) -> None:
        self.store = store

    def manifest(self, day: date) -> list[dict[str, Any]]:
        body = self.store.get(manifest_key(day))
        if body is None:
            return []
        return [json.loads(line) for line in body.decode().splitlines() if line.strip()]

    def find(self, day: date, dataset: str) -> dict[str, Any] | None:
        for line in self.manifest(day):
            if line["dataset"] == dataset:
                return line
        return None

    def read(self, line: dict[str, Any]) -> bytes:
        body = self.store.get(line["key"])
        if body is None:
            raise ArchiveError(f"archive has no object at {line['key']}")
        if hashlib.sha256(body).hexdigest() != line["sha256"]:
            raise ArchiveError(f"{line['key']} does not hash as its manifest line says")
        return body

    def pin(
        self, line: dict[str, Any], destination: Path, *, journal_path: Path, repo_root: Path
    ) -> dict[str, Any]:
        """Write the copy under data/raw and journal it; refuse to overwrite."""
        if destination.exists():
            existing = hashlib.sha256(destination.read_bytes()).hexdigest()
            if existing != line["sha256"]:
                raise ArchiveError(f"{destination} exists with different bytes; refusing")
            body = destination.read_bytes()
        else:
            body = self.read(line)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
        entry = {
            "source": "archive",
            "dataset": line["dataset"],
            "url": line["url"],
            "path": str(destination.relative_to(repo_root)),
            "sha256": line["sha256"],
            "bytes": len(body),
            "fetched_at": line["fetched_at"],
            "archive_key": line["key"],
            "archive_day": line["day"],
            "unchanged_from": line.get("unchanged_from"),
            "http": line.get("http", {}),
            "extra": line.get("extra", {}),
        }
        journal_path.parent.mkdir(parents=True, exist_ok=True)
        with journal_path.open("a") as out:
            out.write(json.dumps(entry) + "\n")
        return entry
