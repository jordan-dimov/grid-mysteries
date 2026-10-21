"""What every record engine shares.

A record engine (`tec/`, `bill/`) holds one governed record in its own
Morpholog database under its own signing key. This module is the part
of an engine that is the same for each: the client pinned to the
engine's programme, the transact guarded by a recovery marker, the
signed and witnessed checkpoint with its anchor file, the exported pack
verified offline against that anchor, and a streaming reader for the
pack. An engine keeps only what is its own: the pure plan over its
state, and the commands that read its record back.

The recovery marker is the safety of the whole thing. It is written
before a transact and cleared only on a positive non-commit: a
rejection, or an error whose stable `code` the runtime documents as
"nothing was recorded" (the generated client raises exactly those as
``MorphologRequestError``). An unknown outcome, including a binary
killed after COMMIT, keeps the marker, and the next run refuses until
someone has read the record and removed it by hand.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from grid_mysteries.capture.timestamp import TSAS
from grid_mysteries.corpus import REPO_ROOT

if TYPE_CHECKING:
    from morpholog_client.adapter import Morpholog
    from morpholog_client.envelopes import AtomicRejected

#: The timestamp authorities that countersign an engine's checkpoints, in
#: the order they are asked (the same two, in the same order, as the
#: research record and every freeze), and the one PEM file holding every
#: root their tokens are judged against (`trust/tsa/roots.pem`, the two
#: roots beside it concatenated; a test holds it to that). Until 08/10/2026
#: the engines asked DigiCert alone: freetsa.org's tokens could not be
#: verified before Morpholog v0.0.14, so an anchor of that time carries one
#: witness and still verifies against this file.
WITNESSES: Final = tuple("rfc3161:" + url for _, url in TSAS)
TSA_ROOTS: Final = REPO_ROOT / "trust" / "tsa" / "roots.pem"


@dataclass(frozen=True)
class Record:
    """One engine's identity. Every path and environment variable follows
    from the name and the key id, so a third engine is one line."""

    name: str
    programme: Path  # relative to the repository root
    actor: str
    key_id: str  # `<name>-<year>`

    def url(self) -> str:
        return os.environ.get(
            f"{self.name.upper()}_DATABASE_URL", f"postgres:///grid_mysteries_{self.name}"
        )

    @property
    def signing_key(self) -> Path:
        name, year = self.key_id.rsplit("-", 1)
        default = Path.home() / ".config" / "grid-mysteries" / f"{name}-signing-{year}.pem"
        return Path(os.environ.get(f"{self.name.upper()}_SIGNING_KEY", str(default)))

    @property
    def public_key(self) -> Path:
        return REPO_ROOT / self.name / "trust" / f"{self.key_id}.pub"

    @property
    def anchors(self) -> Path:
        return REPO_ROOT / self.name / "anchors"

    @property
    def packs(self) -> Path:
        return REPO_ROOT / "data" / "derived" / self.name / "packs"

    @property
    def marker_dir(self) -> Path:
        return Path("data") / "derived" / self.name

    def act(self, transformation: str, **args: object) -> dict[str, Any]:
        return {"transformation": transformation, "actor": self.actor, "args_named": args}

    def client(self, repo_root: Path, database_url: str) -> Morpholog:
        """A client that refuses, before its first call, a binary of another
        version than the vendored client was generated for, or a programme
        file whose hash is not the pinned one (`PROGRAMME_HASH.json` beside
        the programme). The pin that CI checks is then also the pin that
        holds when the laptop writes to the record."""
        from morpholog_client import MORPHOLOG_VERSION
        from morpholog_client.adapter import Morpholog

        pin = repo_root / self.programme.parent / "PROGRAMME_HASH.json"
        return Morpholog(
            str(repo_root / self.programme),
            database_url,
            expected_version=MORPHOLOG_VERSION,
            expected_model_hash=json.loads(pin.read_text())["hash"],
        )


def run(*args: str) -> subprocess.CompletedProcess[str]:
    """The `morpholog` binary (`MORPHOLOG_BIN`, else the one on PATH, as the
    generated client chooses), for the two commands whose exact stdout is
    the artefact (a checkpoint, a verify report)."""
    binary = os.environ.get("MORPHOLOG_BIN", "morpholog")
    return subprocess.run([binary, *args], capture_output=True, text=True)


# ------------------------------------------------------------ the transact


class ImportError_(RuntimeError):
    pass


@dataclass
class Outcome:
    status: str  # committed | not-committed | unknown
    detail: str = ""
    transition_ids: list[str] = field(default_factory=list)


def classify(result: object, error: BaseException | None) -> Outcome:
    """committed / not-committed / unknown, from a transact's result or error.

    The generated client raises ``MorphologRequestError`` only for the
    codes the runtime publishes as "nothing was recorded"
    (``envelopes.NOTHING_RECORDED_CODES``); that set is read from the
    client, never copied here. Anything else is unknown."""
    from morpholog_client import envelopes
    from morpholog_client.adapter import MorphologRequestError

    if error is None:
        if isinstance(result, envelopes.AtomicCommitted):
            return Outcome("committed", "", [a.outcome.transition_id for a in result.acts])
        if isinstance(result, envelopes.AtomicRejected):
            return Outcome("not-committed", refusal_detail(result))
        return Outcome("unknown", f"unrecognised result {result!r}"[:300])
    if isinstance(error, MorphologRequestError) and error.code in envelopes.NOTHING_RECORDED_CODES:
        return Outcome("not-committed", f"{error.code}: {error.error}"[:300])
    return Outcome("unknown", f"{type(error).__name__}: {error}"[:300])


def refusal_detail(rejected: AtomicRejected) -> str:
    """A refused act in one line, from what the refusal itself carries: the
    rule, the comparison it failed with both values (`compared`) and the
    bindings where it failed (`witness`), both from v0.0.15 (#531, #537),
    so nothing here re-derives a rule's arithmetic to explain it."""
    detail = f"act {rejected.act} refused [{rejected.rule}]"
    if rejected.compared is not None:
        c = rejected.compared
        detail += f": {c.left} {c.op} {c.right} does not hold"
    if rejected.witness:
        detail += " where " + ", ".join(f"{w.var}={w.value}" for w in rejected.witness)
    return detail


def marker_path(repo_root: Path, record: Record, database_url: str) -> Path:
    """One marker per database, so a test or rehearsal database can never
    block, or be unblocked by, the live record's imports. Credentials are
    left out of the hash, so a changed password does not orphan a marker."""
    name = database_url.rsplit("/", 1)[-1].split("?")[0] or "default"
    ident = hashlib.sha256(database_url.split("@")[-1].encode()).hexdigest()[:12]
    return repo_root / record.marker_dir / f".import-recovery.{name}.{ident}"


def refuse_if_marked(marker: Path, read_back: str) -> None:
    if marker.exists():
        raise ImportError_(
            f"recovery marker {marker} exists: a previous run's outcome is unknown. "
            f"Read the record ({read_back}) and remove the marker by hand."
        )


def guarded_transact(
    api: Any, marker: Path, label: str, acts: list[dict[str, Any]], note: dict[str, Any]
) -> Outcome:
    """One transact under the recovery marker. Returns the committed outcome;
    raises ``ImportError_`` otherwise, clearing the marker only when the
    record is known unchanged."""
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({**note, "acts": len(acts)}) + "\n")
    result: object = None
    error: BaseException | None = None
    try:
        result = api.transact(acts)
    except Exception as exc:  # noqa: BLE001 - classified below
        error = exc
    outcome = classify(result, error)
    if outcome.status == "not-committed":
        marker.unlink()
        raise ImportError_(f"{label} was not committed ({outcome.detail}); record unchanged")
    if outcome.status != "committed":
        raise ImportError_(
            f"{label}: commit outcome UNKNOWN ({outcome.detail}); marker left at {marker}"
        )
    marker.unlink()
    return outcome


def provisioned(api: Any, label: str) -> None:
    """The deploy gate: refuse to write until the database holds every
    index and statistics object the engine's programme needs (Morpholog
    v0.0.14, #467) and the programme still fits the claims the database
    holds (v0.0.16, #575: a stored claim with another arity, kind or unit
    than its declaration is an error no rule could ever match; a stored
    predicate the programme does not declare is a hint, and an engine's
    database serves one programme, so a hint here is read, not refused).
    Both read only. The Bill record ran unprovisioned from its launch on
    26/09/2026 to the 30/09 migration because nothing asked; this asks on
    every import."""
    report = api.provision_indexes(check=True)
    if not report.is_current:
        wanting = [f"{i.name} {i.action}" for i in report.indexes if i.action != "KEEP"] + [
            f"{st.name} {st.action}" for st in report.statistics if st.action != "KEEP"
        ]
        raise ImportError_(
            f"{label}: the database is not provisioned for the programme "
            f"({len(wanting)} index/statistics object(s) to act on: "
            + "; ".join(wanting[:6])
            + ("; …" if len(wanting) > 6 else "")
            + "). Run `morpholog provision indexes <programme> --prune` (every programme "
            "the database serves, one call) and retry."
        )
    fit = api.check(with_database=True)
    errors = [d.message for d in fit.diagnostics if d.severity == "error"]
    if errors:
        raise ImportError_(
            f"{label}: the programme does not fit the claims the database holds "
            f"({len(errors)} error(s)): "
            + "; ".join(errors[:6])
            + ("; …" if len(errors) > 6 else "")
            + ". Nothing was written; see `morpholog check --database-url`."
        )


def last_close(api: Any, *, current: str, key: str) -> str | None:
    """The transition that closed the latest import, read from the record
    itself: the `Imported` claim of the subject the engine's current
    pointer names (`CurrentRun(#bill, run, ..)`, `CurrentVintage(#tec,
    vintage, ..)`), and the transition that asserted it (`asserted_in`,
    v0.0.15). None on a record nothing has been imported into. The
    checkpoint after an import covers this transition by name, so "the
    anchor contains the close" is refused rather than assumed."""
    pointers = api.claims_named(current)
    if not pointers:
        return None
    subject = str(pointers[-1].args[key])
    closes = [c for c in api.claims_named("Imported") if str(c.args[key]) == subject]
    return closes[-1].asserted_in if closes else None


# ------------------------------------------------------ checkpoint and pack


#: How a checkpoint asked to cover a transition is retried when that
#: transition is committed but not yet in the stable prefix (`audit
#: checkpoint --covering`, v0.0.16, #589): nothing is recorded by the
#: refusal, so the same call is repeated after each pause, in seconds.
COVERING_RETRY_PAUSES: Final = (1, 2, 4, 8, 16)


def checkpoint_and_export(
    record: Record,
    database_url: str,
    *,
    witness: bool,
    covering: str | None = None,
    pause: Callable[[float], None] = time.sleep,
) -> tuple[Path, dict[str, Any], Path]:
    """Sign a checkpoint over the record's head (both timestamp authorities
    countersign it with `witness`), keep the anchor under the engine's
    anchors directory, then export the complete pack at that tree size and
    verify it against the anchor. Returns (anchor path, anchor, pack).

    With `covering`, the checkpoint succeeds only with a head that contains
    that transition (the import's close, from `last_close`), so the anchor
    provably covers the import rather than whatever prefix was stable. A
    transition committed moments ago can sit outside that prefix on the
    first try: the refusal records nothing and is retried after each of
    `COVERING_RETRY_PAUSES`; a refusal that outlasts them is an exit.

    The checkpoint call is raw on purpose: the anchor file is the binary's
    exact bytes, and a failed witness is a nonzero exit with the recorded
    checkpoint still on stdout. The pack is exported either way, so the
    retry only has to witness."""
    argv = ["audit", "checkpoint", "--database-url", database_url]
    argv += ["--signing-key", str(record.signing_key), "--key-id", record.key_id]
    if witness:
        for authority in WITNESSES:
            argv += ["--witness", authority]
    if covering is not None:
        argv += ["--covering", covering]
    for attempt, wait in enumerate((*COVERING_RETRY_PAUSES, None)):
        proc = run(*argv)
        if not proc.stdout.strip():
            raise SystemExit(f"checkpoint failed:\n{proc.stderr}")
        anchor = json.loads(proc.stdout)
        if anchor.get("code") != "transition_not_covered":
            break
        if wait is None:
            raise SystemExit(
                f"checkpoint refused {attempt} times: transition {covering} is committed but "
                f"still outside the stable prefix at tree size {anchor.get('tree_size')}; "
                "nothing recorded. Retry `checkpoint` once the prefix advances."
            )
        print(f"checkpoint: {covering} not yet in the stable prefix; retrying in {wait} s")
        pause(wait)
    path = record.anchors / f"tree-{anchor['tree_size']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    # An unwitnessed head never overwrites a witnessed anchor of the same size.
    if not path.exists() or "witnesses" in anchor:
        path.write_text(proc.stdout if proc.stdout.endswith("\n") else proc.stdout + "\n")
    print(f"anchor {path.relative_to(REPO_ROOT)} ({anchor.get('status', 'witnessed')})")
    anchor = json.loads(path.read_text())
    pack = exported_pack(record, database_url, path, anchor)
    if proc.returncode != 0:
        witnesses = " ".join(f"--witness {authority}" for authority in WITNESSES)
        raise SystemExit(
            "a timestamp authority failed; the checkpoint is recorded. Retry with\n"
            f"  morpholog audit witness --database-url {database_url} "
            f"--tree-size {anchor['tree_size']} {witnesses} "
            f"> {path.relative_to(REPO_ROOT)}"
        )
    return path, anchor, pack


def exported_pack(
    record: Record, database_url: str, anchor_path: Path, anchor: dict[str, Any]
) -> Path:
    """The complete pack at the anchor's tree size, exported once and kept,
    verified offline against the anchor with the pinned key and the TSA
    roots every time it is asked for.

    A verifier reads one pack format, its own (v0.0.15, #517). A kept pack
    of an older format is reported `unsupported_pack`; it is moved aside as
    `tree-<n>.format-<f>.ndjson`, never overwritten (only the release that
    wrote it verifies it, and the record may not always be there to export
    it again), and the pack is exported afresh in the binary's format."""
    from morpholog_client import envelopes

    tree = int(anchor["tree_size"])
    pack = record.packs / f"tree-{tree}.ndjson"
    api = record.client(REPO_ROOT, database_url)

    def verify() -> envelopes.PackVerificationReport[envelopes.TreeVerification]:
        return api.audit_verify_pack(
            str(pack),
            anchor_file=str(anchor_path),
            require_signing_key=str(record.public_key),
            trusted_tsa_file=str(TSA_ROOTS),
        )

    report = verify() if pack.exists() else None
    if report is not None and isinstance(report.verdict, envelopes.TreeUnsupportedPack):
        pack.rename(
            pack.with_name(f"tree-{tree}.format-{report.verdict.pack_format_version}.ndjson")
        )
        report = None
    if report is None:
        pack.parent.mkdir(parents=True, exist_ok=True)
        manifest = api.audit_export(str(pack), tree_size=tree)
        if manifest.tree_size != tree:
            raise SystemExit(
                f"exported a pack of {manifest.tree_size} rows, the anchor says {tree}"
            )
        report = verify()
    # `passes` is the binary's own verdict (Morpholog v0.0.14, #468): the
    # verdict intact and no witness `invalid`; `unsupported` and `unverified`
    # say what could not be established and do not fail it.
    if not report.passes:
        invalid = [
            w.submitted_to
            for c in (report.witnesses.checkpoints if report.witnesses else [])
            for w in c.witnesses
            if w.status == "invalid"
        ]
        raise SystemExit(
            f"the pack does not verify against {anchor_path.name}: {report.verdict!r}"
            + (f"; invalid witness from {', '.join(invalid)}" if invalid else "")
        )
    return pack


class PackError(RuntimeError):
    pass


def pack_rows(pack_path: Path) -> Iterator[dict[str, Any]]:
    """The audit rows of a complete-prefix pack (a manifest line,
    `checkpoint_count` checkpoint lines, then one row per line), streamed in
    log order. The row count is checked against the manifest once the
    stream is exhausted.

    Formats 4 and 13 (v0.0.12 to v0.0.14) and 17 (v0.0.15) lay the body out
    alike and differ in the manifest: 17 adds `morpholog_version`, which the
    generated client's `PrefixPackManifest` requires. Packs of every format
    stay on disk (TEC's under `data/derived/tec/packs/`), so only the two
    counts the stream needs are read here; whether a pack verifies is the
    binary's question, asked before its rows are trusted."""
    with pack_path.open() as handle:
        manifest = json.loads(handle.readline())
        if manifest.get("pack_kind") != "prefix":
            raise PackError(f"not a complete-prefix pack: {manifest.get('pack_kind')!r}")
        checkpoint_count, tree_size = manifest["checkpoint_count"], manifest["tree_size"]
        lines = (line for line in handle if line.strip())
        for _ in range(checkpoint_count):
            next(lines)
        count = 0
        for line in lines:
            count += 1
            yield json.loads(line)
    if count != tree_size:
        raise PackError(f"pack holds {count} rows, its manifest says {tree_size}")
