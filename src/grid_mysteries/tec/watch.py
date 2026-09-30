"""The named-project watch on the daily TEC capture.

A private instrument, not an investigation: for a short list of projects
it reads each new copy of NESO's TEC Register that the daily capture has
recorded, compares the rows it follows against the copy before, and writes
one line per change (a date, a status, a customer name, a Gate cell, a
capacity, a name, a site) with both copies' digests. It exists to tell one
person the day their project moves. It computes no figure and selects
nothing beyond the list it is given.

How a project is followed:

- **Seed.** A watch entry names a project as the register prints it, and
  records the customer name and MW it was seeded with. On the first copy
  in which a row's normalised project name (005's rule, `tec_register
  .normalise`) equals the entry's, the row is the entry's. If that row's
  customer or stage MW differ from what the entry recorded, a
  `seed-mismatch` line says so; the row is still followed, because the
  difference is the kind of change the watch is for.
- **Lock.** Once a row is the entry's, its `Project ID` (15-character
  form, 017's `project_id`) is remembered, and in every later copy any row
  with that id belongs to the entry whatever it is now called. A renamed
  project is therefore followed, and the rename is one of the lines.
- **Diff.** Rows are matched between consecutive copies by
  `overdue_queue.identity_key` (project id with the register's stage). A
  key in both copies produces one `change` line per watched column whose
  printed text differs; a key only in the earlier copy is `left`; a key
  only in the later copy is `arrived`. The first copy processed produces a
  `first-sight` line per followed row, so the log opens with what the
  register printed before anything moved. A cell whose printed text
  changes but whose value does not under the reading rules (a date
  respelled from `30/09/2027` to `2027-09-30`, an MW from `150` to
  `150.00`) is a `respelling`: kept in the log, never reported as movement.

Copies are read from the local mirror of the archive after their bytes are
checked against the committed daily manifest that recorded them, exactly as
017 version 3 reads them. A copy the mirror does not yet hold stops the run
before it, and the next run resumes there. Copies already processed are
never reprocessed: the state file names the last copy's digest.

Everything here is pure except `run`, which owns the files.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from grid_mysteries.hashing import sha256_file
from grid_mysteries.investigations.overdue_queue import identity_key, project_id, text
from grid_mysteries.sources import tec_register as tr

WATCHED_COLUMNS: Final = (
    "MW Effective From",
    "Project Status",
    "Customer Name",
    "Gate",
    "MW Increase / Decrease",
    "Cumulative Total Capacity (MW)",
    "Project Name",
    "Connection Site",
    "Stage",
)
DEFAULT_DIR: Final = Path("data/derived/tec-watch")


@dataclass(frozen=True)
class WatchEntry:
    """One project to follow, as seeded."""

    label: str
    project: str
    customer: str = ""
    mw: str = ""
    note: str = ""


@dataclass
class WatchState:
    last_sha256: str | None = None
    last_t_public: str | None = None
    copies_seen: list[str] = field(default_factory=list)
    locked: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> WatchState:
        return cls(
            last_sha256=data.get("last_sha256"),
            last_t_public=data.get("last_t_public"),
            copies_seen=list(data.get("copies_seen") or []),
            locked={k: list(v) for k, v in (data.get("locked") or {}).items()},
        )


def load_watchlist(path: Path) -> list[WatchEntry]:
    data = json.loads(path.read_text())
    entries = [WatchEntry(**item) for item in data["watch"]]
    labels = [e.label for e in entries]
    if len(set(labels)) != len(labels):
        raise ValueError("watch labels must be distinct")
    return entries


def copy_ref(entry: dict[str, Any]) -> dict[str, str]:
    """The four things that name a copy in a log line."""
    return {
        "t_public": str(entry["t_public"]),
        "sha256": str(entry["sha256"]),
        "filename": str(entry["filename"]),
        "manifest": str(entry["manifest"]),
    }


def belongs(entry: WatchEntry, row: dict[str, object], locked: set[str]) -> bool:
    pid = project_id(row)
    if pid and pid in locked:
        return True
    return tr.normalise(row.get("Project Name")) == tr.normalise(entry.project)


def followed_rows(
    entry: WatchEntry, rows: list[dict[str, object]], locked: set[str]
) -> dict[tuple[str, str], dict[str, object]]:
    """The entry's rows in one copy, keyed by `identity_key`.

    Two rows on one key in one copy cannot be told apart, so both are kept
    under a suffixed key and the log will show them as separate lines
    rather than pretend one of them is the other.
    """
    out: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        if not belongs(entry, row, locked):
            continue
        key = identity_key(row)
        n = 1
        while key in out:
            n += 1
            key = (key[0], f"{identity_key(row)[1]}#{n}")
        out[key] = row
    return out


def same_value(column: str, a: str, b: str) -> bool:
    """Whether two printed cells read as the same value under the register's
    reading rules: dates by `parse_date` (so `30/09/2027` and `2027-09-30`
    are one date), MW by `parse_decimal` (`150` and `150.00`), the stage by
    `normalise_stage`; every other column by its printed text. A cell that
    parses on one side and not the other is a change, never a respelling.
    """
    if column == "MW Effective From":
        da, db = tr.parse_date(a), tr.parse_date(b)
        return da is not None and da == db
    if column in ("MW Increase / Decrease", "Cumulative Total Capacity (MW)"):
        ma, mb = tr.parse_decimal(a), tr.parse_decimal(b)
        return ma is not None and ma == mb
    if column == "Stage":
        return tr.normalise_stage(a) == tr.normalise_stage(b)
    return a == b


MATERIAL_KINDS: Final = frozenset({"change", "left", "arrived", "seed-mismatch", "first-sight"})


def snapshot(row: dict[str, object]) -> dict[str, str]:
    return {column: text(row.get(column)) for column in WATCHED_COLUMNS}


def _line(kind: str, entry: WatchEntry, key: tuple[str, str], row: dict[str, object], **more):
    return {
        "kind": kind,
        "watch": entry.label,
        "key": f"{key[0]}|{key[1]}",
        "project_id": project_id(row),
        "project_name": text(row.get("Project Name")),
        **more,
    }


def seed_mismatches(entry: WatchEntry, row: dict[str, object]) -> list[tuple[str, str, str]]:
    """(what, seeded, printed) for each seeded fact the row does not print."""
    out = []
    printed_customer = text(row.get("Customer Name"))
    if entry.customer and tr.normalise(printed_customer) != tr.normalise(entry.customer):
        out.append(("Customer Name", entry.customer, printed_customer))
    if entry.mw:
        printed_mw = tr.parse_decimal(row.get("MW Increase / Decrease"))
        seeded_mw = tr.parse_decimal(entry.mw)
        if seeded_mw is not None and printed_mw != seeded_mw:
            out.append(
                ("MW Increase / Decrease", entry.mw, text(row.get("MW Increase / Decrease")))
            )
    return out


def first_sight(
    entry: WatchEntry, rows: list[dict[str, object]], locked: set[str], copy: dict[str, Any]
) -> tuple[list[dict[str, Any]], set[str]]:
    """Lines for the first copy an entry is read against, and the ids to lock."""
    lines: list[dict[str, Any]] = []
    new_locks: set[str] = set()
    for key, row in followed_rows(entry, rows, locked).items():
        lines.append(
            _line("first-sight", entry, key, row, copy=copy_ref(copy), state=snapshot(row))
        )
        for what, seeded, printed in seed_mismatches(entry, row):
            lines.append(
                _line(
                    "seed-mismatch",
                    entry,
                    key,
                    row,
                    copy=copy_ref(copy),
                    field=what,
                    seeded=seeded,
                    printed=printed,
                )
            )
        if pid := project_id(row):
            new_locks.add(pid)
    return lines, new_locks


def diff(
    entry: WatchEntry,
    before_rows: list[dict[str, object]],
    after_rows: list[dict[str, object]],
    locked: set[str],
    before: dict[str, Any],
    after: dict[str, Any],
) -> tuple[list[dict[str, Any]], set[str]]:
    """Change lines between two consecutive copies for one entry, and the
    ids newly seen (to lock)."""
    lines: list[dict[str, Any]] = []
    prev = followed_rows(entry, before_rows, locked)
    nxt = followed_rows(entry, after_rows, locked | {project_id(r) for r in prev.values()})
    refs = {"from_copy": copy_ref(before), "to_copy": copy_ref(after)}
    for key in sorted(prev.keys() | nxt.keys()):
        if key in prev and key in nxt:
            a, b = snapshot(prev[key]), snapshot(nxt[key])
            for column in WATCHED_COLUMNS:
                if a[column] != b[column]:
                    lines.append(
                        _line(
                            "respelling" if same_value(column, a[column], b[column]) else "change",
                            entry,
                            key,
                            nxt[key],
                            field=column,
                            before=a[column],
                            after=b[column],
                            **refs,
                        )
                    )
        elif key in prev:
            lines.append(_line("left", entry, key, prev[key], state=snapshot(prev[key]), **refs))
        else:
            lines.append(_line("arrived", entry, key, nxt[key], state=snapshot(nxt[key]), **refs))
    new_locks = {pid for r in nxt.values() if (pid := project_id(r))}
    return lines, new_locks


def human(line: dict[str, Any]) -> str:
    """One readable line, dates and digests included."""
    name = f"{line['watch']} [{line['project_name']}, {line['key']}]"
    if line["kind"] in ("change", "respelling"):
        what = "respelled " if line["kind"] == "respelling" else ""
        return (
            f"{line['to_copy']['t_public']} {name}: {what}{line['field']} "
            f"{line['before'] or '(blank)'} -> {line['after'] or '(blank)'} "
            f"(copies {line['from_copy']['sha256'][:8]} -> {line['to_copy']['sha256'][:8]})"
        )
    if line["kind"] in ("left", "arrived"):
        s = line["state"]
        return (
            f"{line['to_copy']['t_public']} {name}: row {line['kind']} "
            f"(status {s['Project Status']}, date {s['MW Effective From'] or '(blank)'}, "
            f"{s['MW Increase / Decrease']} MW, Gate {s['Gate'] or '(blank)'}; "
            f"copies {line['from_copy']['sha256'][:8]} -> {line['to_copy']['sha256'][:8]})"
        )
    if line["kind"] == "seed-mismatch":
        return (
            f"{line['copy']['t_public']} {name}: seeded {line['field']} "
            f"'{line['seeded']}' but the register prints '{line['printed']}'"
        )
    s = line["state"]
    return (
        f"{line['copy']['t_public']} {name}: first sight, status {s['Project Status']}, "
        f"date {s['MW Effective From'] or '(blank)'}, {s['MW Increase / Decrease']} MW, "
        f"Gate {s['Gate'] or '(blank)'}, customer {s['Customer Name']} "
        f"(copy {line['copy']['sha256'][:8]})"
    )


def pending_copies(entries: list[dict[str, Any]], state: WatchState) -> list[dict[str, Any]]:
    """The captured copies not yet processed, in publication order."""
    if state.last_sha256 is None:
        return entries
    digests = [e["sha256"] for e in entries]
    if state.last_sha256 not in digests:
        raise RuntimeError(
            f"the state's last copy {state.last_sha256[:8]} is not among the captured copies"
        )
    return entries[digests.index(state.last_sha256) + 1 :]


def read_copy(entry: dict[str, Any], mirror: Path) -> list[dict[str, object]] | None:
    """The copy's rows, or None when the mirror does not hold it yet; bytes
    that do not hash to the manifested digest stop the run."""
    path = mirror / entry["key"]
    if not path.exists():
        return None
    if sha256_file(path) != entry["sha256"]:
        raise RuntimeError(f"{entry['key']} does not match its manifested digest")
    return tr.read_vintage(path, "csv")


def run(
    *,
    watchlist: list[WatchEntry],
    manifests: list[Path],
    mirror: Path,
    state: WatchState,
    now: datetime | None = None,
) -> tuple[list[dict[str, Any]], WatchState, str | None]:
    """Process every pending copy. Returns the new log lines, the advanced
    state, and a note when the run stopped early (a copy not yet mirrored).

    The state is advanced only past copies fully processed; when a copy is
    not mirrored, the state still names the copy before it.
    """
    stamp = (now or datetime.now(UTC)).isoformat(timespec="seconds")
    entries = tr.capture_entries(manifests)
    pending = pending_copies(entries, state)
    lines: list[dict[str, Any]] = []
    stopped: str | None = None
    previous: tuple[dict[str, Any], list[dict[str, object]]] | None = None
    if state.last_sha256 is not None:
        last = next(e for e in entries if e["sha256"] == state.last_sha256)
        rows = read_copy(last, mirror)
        if rows is None:
            raise RuntimeError(f"the last processed copy {last['sha256'][:8]} is not mirrored")
        previous = (last, rows)
    for copy in pending:
        rows = read_copy(copy, mirror)
        if rows is None:
            stopped = (
                f"copy dated {copy['t_public']} ({copy['sha256'][:8]}, {copy['manifest']}) "
                f"is manifested but not yet mirrored; stopping before it"
            )
            break
        for entry in watchlist:
            locked = set(state.locked.get(entry.label, []))
            if previous is None:
                new, locks = first_sight(entry, rows, locked, copy)
            else:
                new, locks = diff(entry, previous[1], rows, locked, previous[0], copy)
            lines.extend(new)
            if locks - locked:
                state.locked[entry.label] = sorted(locked | locks)
        state.last_sha256 = copy["sha256"]
        state.last_t_public = copy["t_public"]
        state.copies_seen.append(copy["sha256"])
        previous = (copy, rows)
    for line in lines:
        line["logged_at"] = stamp
    return lines, state, stopped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--dir", type=Path, default=None, help=f"state dir (default {DEFAULT_DIR})")
    parser.add_argument("--watchlist", type=Path, default=None)
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    wdir = (args.dir or repo / DEFAULT_DIR).resolve()
    watch_path = args.watchlist or wdir / "watchlist.json"
    state_path = wdir / "state.json"
    log_path = wdir / "watch-log.ndjson"
    text_path = wdir / "watch-log.txt"
    watchlist = load_watchlist(watch_path)
    state = (
        WatchState.from_json(json.loads(state_path.read_text()))
        if state_path.exists()
        else WatchState()
    )
    manifests = sorted((repo / "data/manifests").glob("*.ndjson"))
    lines, state, stopped = run(
        watchlist=watchlist, manifests=manifests, mirror=repo / "data/raw/archive", state=state
    )
    wdir.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        for line in lines:
            f.write(json.dumps(line, sort_keys=False) + "\n")
    with text_path.open("a") as f:
        for line in lines:
            f.write(human(line) + "\n")
    state_path.write_text(json.dumps(state.__dict__, indent=1) + "\n")
    material = [line for line in lines if line["kind"] in MATERIAL_KINDS]
    for line in material:
        print(human(line))
    summary = (
        f"tec-watch: {len(material)} line(s) to report, "
        f"{len(lines) - len(material)} respelling(s) logged only; last copy {state.last_t_public} "
        f"({(state.last_sha256 or '')[:8]}); {len(watchlist)} entries watched"
    )
    if stopped:
        summary += f"; {stopped}"
    print(summary, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
