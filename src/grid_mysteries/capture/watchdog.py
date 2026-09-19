"""The laptop watchdog: five checks on the archive, then one sync.

Runs from a systemd user timer (ops/systemd/) against the bucket with the
watchdog credential, which can read and check settings but never write.
The checks are the design's (ops/VINTAGE-CAPTURE.md, section 7): every
job's status is fresh; artefact counts and bytes per resource sit inside
a band learned from recent runs; a sample of yesterday's artefacts still
hashes as its manifest line says; a proof exists for each recent manifest;
the bucket's protective settings are unchanged. Then manifests, proofs and
instrument state are synced into the repository so the laptop remains a
full second copy. Pure over an `ObjectStore`, so it is tested locally.
"""

import hashlib
import json
import random
import statistics
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from grid_mysteries.capture.run import manifest_key, status_key
from grid_mysteries.capture.store import ObjectStore

#: job -> hours its latest status may be old before the check fails. The
#: 013 job writes no status object (its state is the pinned artefacts and
#: journals under state/013/ and healthchecks.io watches its ping), so only
#: the capture job is checked for freshness here.
DEFAULT_JOBS: dict[str, float] = {"vintage-capture": 26.0}
BAND_RUNS = 30
BAND_LOW = 0.5
BAND_HIGH = 3.0
SAMPLE_SIZE = 5
PROOF_DAYS = 7


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


@dataclass
class Report:
    checks: list[Check] = field(default_factory=list)
    synced: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


def _load(store: ObjectStore, key: str) -> dict[str, Any] | None:
    body = store.get(key)
    return json.loads(body) if body else None


def check_freshness(store: ObjectStore, jobs: dict[str, float], now: datetime) -> list[Check]:
    out = []
    for job, hours in jobs.items():
        latest = _load(store, status_key(job, None))
        if latest is None:
            out.append(Check(f"fresh:{job}", False, "no status object yet"))
            continue
        finished = datetime.fromisoformat(latest["finished_at"])
        age = (now - finished).total_seconds() / 3600
        ok = age <= hours and bool(latest.get("ok"))
        out.append(
            Check(
                f"fresh:{job}",
                ok,
                f"finished {latest['finished_at']} ({age:.1f} h ago; allowed {hours:.0f} h); "
                f"run {'ok' if latest.get('ok') else 'FAILED'}",
            )
        )
    return out


def check_bands(store: ObjectStore, job: str) -> list[Check]:
    """The latest run's artefact count and bytes per resource against the
    median of the BAND_RUNS days before it that have a status: a source that
    shrinks to a login page fails BAND_LOW, one that explodes fails BAND_HIGH.
    The anchor is `status/latest.json`, not today's date: the watchdog fires
    twice a day and the 04:12 run precedes the 06:30 capture, so "today's
    status" does not exist yet and is not a fault (2026-09-18, the first
    pre-capture run after the timer was re-enabled, failed on exactly that).
    Staleness is check_freshness's question, not this one's."""
    latest = _load(store, status_key(job, None))
    if latest is None:
        return [Check(f"band:{job}", False, "no status object yet")]
    day = date.fromisoformat(latest["day"])
    history: dict[str, list[tuple[int, int]]] = {}
    for back in range(1, BAND_RUNS + 1):
        past = _load(store, status_key(job, day - timedelta(days=back)))
        if past is None:
            continue
        for r in past.get("resources", []):
            if r.get("error") is None:
                history.setdefault(r["name"], []).append((r["artefacts"], r["bytes"]))
    out = []
    for r in latest.get("resources", []):
        runs = history.get(r["name"], [])
        if len(runs) < 3:
            out.append(
                Check(f"band:{job}:{r['name']}", True, f"{len(runs)} prior runs; no band yet")
            )
            continue
        med_count = statistics.median(c for c, _ in runs)
        med_bytes = statistics.median(b for _, b in runs)
        ok = (
            r.get("error") is None
            and BAND_LOW * med_count <= r["artefacts"] <= BAND_HIGH * max(med_count, 1)
            and BAND_LOW * med_bytes <= r["bytes"] <= BAND_HIGH * max(med_bytes, 1)
        )
        out.append(
            Check(
                f"band:{job}:{r['name']}",
                ok,
                f"{r['artefacts']} artefacts / {r['bytes']:,} bytes against medians "
                f"{med_count:.0f} / {med_bytes:,.0f} over {len(runs)} runs"
                + (f"; ERROR {r['error']}" if r.get("error") else ""),
            )
        )
    return out


def check_sample(
    store: ObjectStore, day: date, *, rng: random.Random | None = None, size: int = SAMPLE_SIZE
) -> Check:
    body = store.get(manifest_key(day))
    if body is None:
        return Check(f"sample:{day}", False, "no manifest")
    lines = [json.loads(line) for line in body.decode().splitlines() if line.strip()]
    if not lines:
        return Check(f"sample:{day}", True, "empty manifest")
    chosen = (rng or random.Random()).sample(lines, min(size, len(lines)))
    bad = []
    for line in chosen:
        data = store.get(line["key"])
        if data is None or hashlib.sha256(data).hexdigest() != line["sha256"]:
            bad.append(line["key"])
    return Check(
        f"sample:{day}",
        not bad,
        f"{len(chosen)} of {len(lines)} entries re-read; "
        + (f"MISMATCH {bad}" if bad else "all match"),
    )


def check_proofs(store: ObjectStore, today: date, days: int = PROOF_DAYS) -> list[Check]:
    out = []
    for back in range(0, days):
        day = today - timedelta(days=back)
        if store.get(manifest_key(day)) is None:
            continue
        sidecar = _load(store, f"proofs/{day.isoformat()}.ndjson.timestamps.json")
        if sidecar is None:
            out.append(Check(f"proof:{day}", False, "manifest without a proof sidecar"))
            continue
        kinds = sorted(p["kind"] for p in sidecar.get("proofs", []))
        ok = "rfc3161" in kinds and "opentimestamps" in kinds
        out.append(
            Check(
                f"proof:{day}",
                ok,
                f"proofs {kinds}"
                + (f"; failures {sidecar['failures']}" if sidecar.get("failures") else ""),
            )
        )
    return out


def check_bucket_settings(
    settings: Callable[[], dict[str, Any]] | None, expected: dict[str, Any]
) -> Check:
    """`settings` returns the bucket's live protective settings (see
    `s3_settings`); None means a local store, where the check does not apply."""
    if settings is None:
        return Check("bucket-settings", True, "local store; not applicable")
    try:
        live = settings()
    except Exception as exc:  # noqa: BLE001
        return Check("bucket-settings", False, f"could not read settings: {exc}")
    drift = {k: (expected[k], live.get(k)) for k in expected if live.get(k) != expected[k]}
    return Check("bucket-settings", not drift, f"drift {drift}" if drift else "as expected")


EXPECTED_SETTINGS: dict[str, Any] = {
    "versioning": "Enabled",
    "object_lock": "Enabled",
    "logging": True,
    "block_public_acls": True,
}


def s3_settings(bucket: str, client: Any) -> Callable[[], dict[str, Any]]:
    def read() -> dict[str, Any]:
        versioning = client.get_bucket_versioning(Bucket=bucket).get("Status")
        lock = client.get_object_lock_configuration(Bucket=bucket)["ObjectLockConfiguration"]
        logging = client.get_bucket_logging(Bucket=bucket).get("LoggingEnabled") is not None
        pab = client.get_public_access_block(Bucket=bucket)["PublicAccessBlockConfiguration"]
        return {
            "versioning": versioning,
            "object_lock": lock.get("ObjectLockEnabled"),
            "logging": logging,
            "block_public_acls": pab.get("BlockPublicAcls"),
        }

    return read


def extends(local: bytes, remote: bytes) -> bool:
    """Whether `remote` is `local` with entries appended and nothing else
    changed: a byte prefix (journals, NDJSON), or JSON whose lists each keep
    every local entry, unchanged and in order, with the same keys around them
    (manifests, the acquisition log). Byte-identical or merely reformatted
    content is not growth, and neither is an edit, reorder or truncation."""
    if remote == local:
        return False
    if remote.startswith(local):
        return True
    try:
        old, new = json.loads(local), json.loads(remote)
    except ValueError:
        return False
    return old != new and _json_extends(old, new)


def _json_extends(old: Any, new: Any) -> bool:
    if isinstance(old, list) and isinstance(new, list):
        return len(new) >= len(old) and new[: len(old)] == old
    if isinstance(old, dict) and isinstance(new, dict):
        return old.keys() == new.keys() and all(_json_extends(old[k], new[k]) for k in old)
    return old == new


def sync(store: ObjectStore, repo_root: Path, *, include_bytes: bool = False) -> list[str]:
    """Copy manifests and proofs into data/manifests/, instrument state
    (`state/<instrument>/<repo-relative path>`) into the repository, and
    optionally the raw bytes into data/raw/archive/. Never overwrites a
    local file with different bytes, with one exception: instrument state
    outside data/raw/ that only grew (see `extends`) is replaced and reported
    as `grew`, because every tracker run appends to its log, manifests and
    journals (2026-09-19). Anything else that differs is reported as
    MISMATCH. Witnessed manifests, proofs and raw artefacts never grow."""
    synced: list[str] = []
    targets = [
        ("manifests/", repo_root / "data/manifests"),
        ("proofs/", repo_root / "data/manifests"),
    ]
    if include_bytes:
        targets.append(("raw/", repo_root / "data/raw/archive"))
    for prefix, base in targets:
        for key in store.keys(prefix):
            rel = key[len(prefix) :] if prefix != "raw/" else key
            _place(store, key, base / rel, synced)
    for key in store.keys("state/"):
        parts = key.split("/", 2)
        if len(parts) < 3:
            continue
        _place(
            store, key, repo_root / parts[2], synced, may_grow=not parts[2].startswith("data/raw/")
        )
    return synced


def _place(
    store: ObjectStore, key: str, target: Path, synced: list[str], *, may_grow: bool = False
) -> None:
    body = store.get(key)
    if body is None:
        return
    if target.exists():
        local = target.read_bytes()
        if local == body:
            return
        if may_grow and extends(local, body):
            target.write_bytes(body)
            synced.append(f"grew {key} -> {target}")
            return
        synced.append(f"MISMATCH {key} -> {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    synced.append(f"{key} -> {target}")


def run_watchdog(
    store: ObjectStore,
    *,
    repo_root: Path,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    jobs: dict[str, float] | None = None,
    settings: Callable[[], dict[str, Any]] | None = None,
    include_bytes: bool = False,
    rng: random.Random | None = None,
) -> Report:
    moment = now()
    today = moment.date()
    report = Report()
    report.checks += check_freshness(store, jobs or DEFAULT_JOBS, moment)
    for job in jobs or DEFAULT_JOBS:
        if store.get(status_key(job, None)) is not None:
            report.checks += check_bands(store, job)
    report.checks.append(check_sample(store, today - timedelta(days=1), rng=rng))
    report.checks += check_proofs(store, today)
    report.checks.append(check_bucket_settings(settings, EXPECTED_SETTINGS))
    report.synced = sync(store, repo_root, include_bytes=include_bytes)
    return report
