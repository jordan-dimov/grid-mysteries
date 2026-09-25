"""Every publication back out of the record, by folding its audit history.

Pure over an iterable of audit rows (the objects `morpholog inspect audit`
streams, or the `rows` of an exported pack; both carry tagged claims), in
commit order. Each `close_import` yields the publication as the record
then held it: its Vintage facts, the transition that closed it, and its
rows decoded to the reader's values, in the publication's line order.

This is how the analysis reads the record: never the source files.
"""

import json
import subprocess
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from grid_mysteries.tec import cells


@dataclass(frozen=True)
class Publication:
    vintage: str
    published_on: date
    sha256: str
    file_format: str
    columns: str
    close_transition: str
    #: Row keys in the publication's line order.
    keys: tuple[str, ...]
    #: The reader's rows, decoded from the record, in line order.
    rows: tuple[dict[str, object], ...]


def _value(tagged: dict[str, Any]) -> str:
    return str(tagged["value"])


class ReplayError(RuntimeError):
    pass


def fold(audit_rows: Iterable[dict[str, Any]]) -> Iterator[Publication]:
    held: dict[str, cells.Cells] = {}
    kinds: dict[str, str] = {}
    decoded: dict[tuple[str, str], dict[str, object]] = {}
    vintages: dict[str, tuple[str, ...]] = {}
    for row in audit_rows:
        for claim in row.get("retracted_claims") or []:
            if claim["predicate"] == "Row":
                held.pop(_value(claim["args"][0]), None)
            elif claim["predicate"] == "RowKinds":
                kinds.pop(_value(claim["args"][0]), None)
        order: str | None = None
        closed: str | None = None
        for claim in row.get("asserted_claims") or []:
            name, args = claim["predicate"], [_value(a) for a in claim["args"]]
            if name == "Row":
                held[args[0]] = tuple(args[1:])
            elif name == "RowKinds":
                kinds[args[0]] = args[1]
            elif name == "Vintage":
                vintages[args[0]] = tuple(args[1:])
            elif name == "RowOrder":
                order = args[1]
            elif name == "Imported":
                closed = args[0]
        if closed is None:
            continue
        if order is None:
            raise ReplayError(f"{closed}: closed with no line order")
        published_on, sha256, file_format, columns = vintages[closed]
        keys = tuple(cells.in_file_order(list(held), order))
        for k in keys:
            if (k, kinds[k]) not in decoded:
                decoded[(k, kinds[k])] = cells.decode(kinds[k], held[k])
        yield Publication(
            vintage=closed,
            published_on=date.fromisoformat(published_on),
            sha256=sha256,
            file_format=file_format,
            columns=columns,
            close_transition=str(row["transition_id"]),
            keys=keys,
            rows=tuple(decoded[(k, kinds[k])] for k in keys),
        )


def stream_audit(database_url: str, limit: int | None = None) -> Iterator[dict[str, Any]]:
    """The record's audit rows in commit order, `limit` rows at most."""
    proc = subprocess.Popen(
        ["morpholog", "inspect", "audit", "--database-url", database_url],
        stdout=subprocess.PIPE,
        text=True,
    )
    assert proc.stdout is not None
    count = 0
    try:
        for line in proc.stdout:
            if limit is not None and count >= limit:
                break
            if line.strip():
                count += 1
                yield json.loads(line)
    finally:
        proc.stdout.close()
        proc.terminate()
        proc.wait()
    if limit is not None and count != limit:
        raise ReplayError(f"audit stream held {count} rows, the checkpoint covers {limit}")


def pack_rows(pack_path: Path) -> list[dict[str, Any]]:
    """The audit rows of a complete-prefix pack, in log order, whichever
    form the pack takes: NDJSON (Morpholog pack format 4, from v0.0.12: a
    manifest line, `checkpoint_count` checkpoint lines, then one row per
    line) or the earlier single JSON document with a `rows` array."""
    with pack_path.open() as handle:
        first = handle.readline()
        try:
            head = json.loads(first)
        except json.JSONDecodeError:
            head = None
        streamed = isinstance(head, dict) and head.get("pack_kind") == "prefix"
        if streamed and "checkpoint_count" in head:
            to_skip = int(head["checkpoint_count"])
            rows: list[dict[str, Any]] = []
            for line in handle:
                if not line.strip():
                    continue
                if to_skip:
                    to_skip -= 1
                    continue
                rows.append(json.loads(line))
            if len(rows) != int(head["tree_size"]):
                raise ReplayError(
                    f"pack holds {len(rows)} rows, its manifest says {head['tree_size']}"
                )
            return rows
    return list(json.loads(pack_path.read_text())["rows"])
