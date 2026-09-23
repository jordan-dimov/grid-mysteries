"""The publications the TEC record imports, and where each came from.

Two places hold copies, and both are read, never written:

- the journalled archive (`data/raw/neso/tec-history/journal.ndjson`),
  one copy per publication date by 014's reading rule 1 (duplicates
  dropped; where two files claim a date, the one with more rows);
- the vintage-capture archive, as the laptop watchdog mirrors it
  (`data/manifests/<day>.ndjson` and `data/raw/archive/<key>`): each
  captured `NESO-TEC-REGISTER` file, dated by the CKAN `last_modified`
  in the metadata captured beside it the same day.

A copy whose bytes are already journalled is the journal's; a date both
places claim with different bytes stops the import. Every file is
checked against its recorded digest before it is read.
"""

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

from grid_mysteries.hashing import sha256_file
from grid_mysteries.sources import tec_register as tr

MANIFESTS: Final = Path("data/manifests")
ARCHIVE_MIRROR: Final = Path("data/raw/archive")
DATASET: Final = "NESO-TEC-REGISTER"
META_DATASET: Final = "NESO-TEC-REGISTER-META"


@dataclass(frozen=True)
class Copy:
    published_on: date
    sha256: str
    path: Path
    file_format: str
    #: The journal line, or the capture manifest line (plus the metadata
    #: line that dates it), exactly as held.
    provenance: dict[str, Any]


class SourceError(RuntimeError):
    pass


def _journal_copies(repo_root: Path) -> list[Copy]:
    out = []
    for entry in tr.one_per_date(tr.read_journal(repo_root / tr.JOURNAL_PATH)):
        path = repo_root / entry["path"]
        out.append(
            Copy(
                published_on=date.fromisoformat(entry["t_public"][:10]),
                sha256=entry["sha256"],
                path=path,
                file_format=entry.get("format") or path.suffix.lstrip(".").lower(),
                provenance={"journal": entry},
            )
        )
    return out


def _archive_copies(repo_root: Path) -> list[Copy]:
    out = []
    for manifest in sorted((repo_root / MANIFESTS).glob("*.ndjson")):
        lines = [json.loads(x) for x in manifest.read_text().splitlines() if x.strip()]
        data = [x for x in lines if x.get("dataset") == DATASET]
        meta = [x for x in lines if x.get("dataset") == META_DATASET]
        for line in data:
            if not meta:
                raise SourceError(f"{manifest.name}: a TEC copy with no metadata to date it")
            meta_path = repo_root / ARCHIVE_MIRROR / meta[-1]["key"]
            body = json.loads(meta_path.read_bytes())
            modified = (body.get("result") or body)["last_modified"]
            out.append(
                Copy(
                    published_on=date.fromisoformat(modified[:10]),
                    sha256=line["sha256"],
                    path=repo_root / ARCHIVE_MIRROR / line["key"],
                    file_format="csv",
                    provenance={"capture": line, "capture_meta": meta[-1]},
                )
            )
    return out


def copies(repo_root: Path) -> list[Copy]:
    """Every publication, one copy per date, in date order."""
    journal = _journal_copies(repo_root)
    held = {c.sha256 for c in journal}
    by_date = {c.published_on: c for c in journal}
    for copy in _archive_copies(repo_root):
        if copy.sha256 in held:
            continue
        other = by_date.get(copy.published_on)
        if other is not None and other.sha256 != copy.sha256:
            raise SourceError(
                f"{copy.published_on}: two different copies claim this publication date "
                f"({other.sha256[:12]} and {copy.sha256[:12]})"
            )
        held.add(copy.sha256)
        by_date[copy.published_on] = copy
    return [by_date[d] for d in sorted(by_date)]


def verify(copy: Copy) -> None:
    """Stop unless the copy's bytes still hash to its recorded digest."""
    if sha256_file(copy.path) != copy.sha256:
        raise SourceError(f"{copy.path} does not hash to its recorded digest")


def read(copy: Copy) -> list[dict[str, object]]:
    """The copy's rows by the declared reader. Call `verify` first."""
    return tr.read_vintage(copy.path, copy.file_format)
