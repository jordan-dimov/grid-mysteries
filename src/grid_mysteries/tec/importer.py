"""Import TEC publications into the governed record, one transact each.

The plan for a publication (`plan`) is pure: given the rows the record
holds now and the rows the publication prints, it names the publication,
drops the rows that are gone, adds the rows that are new, and closes the
import. Rows that are unchanged cost nothing.

The run (`run`) reads the record's own state first (current publication,
current rows), so it resumes from wherever the record is and never trusts
a local log. Each transact is guarded by a recovery marker kept per
database. The marker is cleared only on a positive non-commit: a
rejection, or an error whose stable `code` the runtime documents as
"nothing was recorded". An unknown outcome, an unknown code, or any other
failure (including the client's by-elimination `MorphologError`, which a
binary killed after COMMIT also produces) keeps the marker, and the next
run refuses until someone has read the record and removed it.
"""

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Final

from grid_mysteries.tec import cells, sources

PROGRAMME: Final = Path("tec/tec-register.morph")
REGISTER: Final = "tec"
ACTOR: Final = "tec_importer"
MARKER_DIR: Final = Path("data/derived/tec")
#: Error codes the runtime documents as "nothing was recorded" (v0.0.11,
#: docs/embedder-integration.md). `commit_outcome_unknown` is deliberately
#: absent; a code not listed here keeps the marker.
NOT_COMMITTED_CODES: Final = frozenset(
    {
        "actor_assertion_unauthorised",
        "duplicate_intent",
        "invalid_arguments",
        "invalid_request",
        "kernel_error",
        "not_committed",
        "serialization_failure",
        "unknown_transformation",
    }
)

RowState = dict[str, tuple[str, cells.Cells]]


def vintage_id(published_on: date) -> str:
    return f"tec-{published_on.isoformat()}"


def act(transformation: str, **args: object) -> dict[str, Any]:
    return {"transformation": transformation, "actor": ACTOR, "args_named": args}


@dataclass(frozen=True)
class Plan:
    vintage: str
    acts: list[dict[str, Any]]
    added: int
    dropped: int
    rekinded: int
    rows: int
    #: What the record holds once this plan commits.
    state: RowState


def plan(
    prior: tuple[str, date] | None,
    held: RowState,
    copy: sources.Copy,
    rows: list[dict[str, object]],
) -> Plan:
    """The acts that bring the record from `held` to this publication."""
    vid = vintage_id(copy.published_on)
    head = dict(
        vintage=vid,
        published_on=copy.published_on.isoformat(),
        sha256=copy.sha256,
        file_format=copy.file_format,
        columns=cells.columns_carried(rows),
    )
    if prior is None:
        acts = [act("open_register", **head)]
    else:
        acts = [
            act("publish", **head, prior=prior[0], prior_on=prior[1].isoformat()),
        ]
    now = cells.keyed(rows)
    dropped = [key for key in held if key not in now]
    added = [key for key in now if key not in held]
    acts += [act("drop_row", row=key, vintage=vid) for key in dropped]
    acts += [
        act("rekind", row=key, vintage=vid, kinds=now[key][0])
        for key in now
        if key in held and held[key][0] != now[key][0]
    ]
    for key in added:
        kinds, values = now[key]
        acts.append(
            act(
                "add_row",
                row=key,
                vintage=vid,
                kinds=kinds,
                **dict(zip(cells.FIELDS, values, strict=True)),
            )
        )
    acts.append(act("close_import", vintage=vid, order=cells.line_order(list(now))))
    rekinded = sum(1 for a in acts if a["transformation"] == "rekind")
    return Plan(vid, acts, len(added), len(dropped), rekinded, len(now), now)


# ------------------------------------------------------------------ marker


def marker_path(repo_root: Path, database_url: str) -> Path:
    """One marker per database, so a test or rehearsal database can never
    block, or be unblocked by, the live record's imports."""
    name = database_url.rsplit("/", 1)[-1].split("?")[0] or "default"
    ident = hashlib.sha256(database_url.split("@")[-1].encode()).hexdigest()[:12]
    return repo_root / MARKER_DIR / f".import-recovery.{name}.{ident}"


class ImportError_(RuntimeError):
    pass


@dataclass
class Outcome:
    vintage: str
    status: str  # committed | not-committed | unknown
    detail: str = ""
    transition_ids: list[str] = field(default_factory=list)


def classify(result: object, error: BaseException | None) -> Outcome:
    """committed / not-committed / unknown, from a transact's result or error."""
    from morpholog_client import envelopes
    from morpholog_client.adapter import MorphologRequestError

    if error is None:
        if isinstance(result, envelopes.AtomicCommitted):
            return Outcome("", "committed", "", [a.outcome.transition_id for a in result.acts])
        if isinstance(result, envelopes.AtomicRejected):
            return Outcome("", "not-committed", f"act {result.act} refused [{result.rule}]")
        return Outcome("", "unknown", f"unrecognised result {result!r}"[:300])
    if isinstance(error, MorphologRequestError) and error.code in NOT_COMMITTED_CODES:
        return Outcome("", "not-committed", f"{error.code}: {error.error}"[:300])
    return Outcome("", "unknown", f"{type(error).__name__}: {error}"[:300])


# --------------------------------------------------------------------- run


def readable(copy: sources.Copy) -> bool:
    """Does the declared reader get rows out of this copy? (Digest checked first.)"""
    sources.verify(copy)
    try:
        return bool(sources.read(copy))
    except Exception:  # noqa: BLE001 - an unreadable copy is a fact, not an error
        return False


def stranded(
    held: list[sources.Copy],
    in_record: set[str],
    current: date,
    can_read: Callable[[sources.Copy], bool],
) -> list[sources.Copy]:
    """Readable copies dated at or before the record's current publication
    that the record does not hold: they can only enter a rebuilt record."""
    return [
        c for c in held if c.published_on <= current and c.sha256 not in in_record and can_read(c)
    ]


def recorded_copies(api: Any) -> set[str]:
    """The SHA-256 of every publication the record holds."""
    return {str(c.args["sha256"]) for c in api.claims_named("Vintage")}


def read_state(api: Any) -> tuple[tuple[str, date] | None, RowState, bool]:
    """(current publication, current rows, an import left open)."""
    current = api.claims_named("CurrentVintage")
    prior = None
    if current:
        args = current[0].args
        prior = (str(args["vintage"]), date.fromisoformat(str(args["published_on"])))
    kinds = {str(c.args["row"]): str(c.args["kinds"]) for c in api.claims_named("RowKinds")}
    held: RowState = {}
    for claim in api.claims_named("Row"):
        a = claim.args
        held[str(a["row"])] = (kinds[str(a["row"])], tuple(str(a[f]) for f in cells.FIELDS))
    return prior, held, bool(api.claims_named("Importing"))


def run(
    repo_root: Path,
    database_url: str,
    *,
    until: date | None = None,
    limit: int | None = None,
    accept_stranded: bool = False,
    log: Callable[[str], None] = print,
) -> list[dict[str, Any]]:
    """Import every held publication newer than the record's current one.

    Refuses, unless `accept_stranded`, when a readable copy dated at or
    before the record's current publication is missing from it (an EIR
    reply filling a gap, say): such a copy can only enter a rebuilt record,
    and importing past it silently would hide the gap."""
    from morpholog_client.adapter import Morpholog

    marker = marker_path(repo_root, database_url)
    if marker.exists():
        raise ImportError_(
            f"recovery marker {marker} exists: a previous import's outcome is unknown. "
            "Read the record (CurrentVintage, Importing) and remove the marker by hand."
        )
    api = Morpholog(str(repo_root / PROGRAMME), database_url)
    prior, held, open_import = read_state(api)
    if open_import:
        raise ImportError_("the record has an import open (Importing): refusing to continue")
    held_copies = sources.copies(repo_root)
    if prior is not None:
        behind = stranded(held_copies, recorded_copies(api), prior[1], readable)
        if behind and not accept_stranded:
            raise ImportError_(
                f"{len(behind)} readable cop{'y' if len(behind) == 1 else 'ies'} dated at or "
                f"before the record's current publication ({prior[1]}) are not in the record: "
                + ", ".join(str(c.published_on) for c in behind[:10])
                + ". The record imports in publication order only; rebuild it into a fresh "
                "database to include them, or pass --accept-stranded to import newer copies anyway."
            )
        for c in behind:
            log(f"stranded (accepted): {c.published_on} {c.sha256[:12]} is not in the record")
    todo = [
        c
        for c in held_copies
        if (prior is None or c.published_on > prior[1])
        and (until is None or c.published_on <= until)
    ]
    if limit is not None:
        todo = todo[:limit]
    done: list[dict[str, Any]] = []
    marker.parent.mkdir(parents=True, exist_ok=True)
    for copy in todo:
        sources.verify(copy)
        try:
            rows = sources.read(copy)
        except Exception as exc:  # noqa: BLE001 - listed, not guessed
            log(f"skip {copy.published_on}: {type(exc).__name__}: {str(exc)[:120]}")
            continue
        if not rows:
            log(f"skip {copy.published_on}: no header/rows parsed")
            continue
        p = plan(prior, held, copy, rows)
        marker.write_text(json.dumps({"vintage": p.vintage, "acts": len(p.acts)}) + "\n")
        started = time.monotonic()
        result: object = None
        error: BaseException | None = None
        try:
            result = api.transact(p.acts)
        except Exception as exc:  # noqa: BLE001 - classified below
            error = exc
        outcome = classify(result, error)
        seconds = round(time.monotonic() - started, 3)
        if outcome.status == "not-committed":
            marker.unlink()
            raise ImportError_(
                f"{p.vintage} was not committed ({outcome.detail}); record unchanged"
            )
        if outcome.status != "committed":
            raise ImportError_(
                f"{p.vintage}: commit outcome UNKNOWN ({outcome.detail}); marker left at {marker}"
            )
        marker.unlink()
        line = {
            "vintage": p.vintage,
            "sha256": copy.sha256,
            "rows": p.rows,
            "added": p.added,
            "dropped": p.dropped,
            "rekinded": p.rekinded,
            "acts": len(p.acts),
            "seconds": seconds,
            "close_transition": outcome.transition_ids[-1],
        }
        done.append(line)
        log(json.dumps(line))
        prior = (p.vintage, copy.published_on)
        held = p.state
    return done
