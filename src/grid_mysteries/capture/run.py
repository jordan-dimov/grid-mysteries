"""The daily capture: fetch, content-address, write bytes and manifest, stop.

For each resource in the plan the strategy's artefacts are written to
`raw/<source>/<resource>/<day>/<sha256>` unless that key already exists
(the same bytes on a later day are the same object; the manifest line says
which day first held them). One manifest line per artefact goes to
`manifests/<day>.ndjson`; a status object to `status/<job>/<day>.json` and
`status/<job>/latest.json`; and the healthcheck is pinged, `/fail` when any
resource failed. Nothing is parsed, sealed or proposed.
"""

import contextlib
import hashlib
import json
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from typing import Any

from grid_mysteries.capture.fetch import Fetcher
from grid_mysteries.capture.plan import Resource
from grid_mysteries.capture.store import ObjectStore
from grid_mysteries.capture.strategies import STRATEGIES, Captured

JOB = "vintage-capture"


@dataclass
class ResourceStatus:
    name: str
    strategy: str
    artefacts: int = 0
    bytes: int = 0
    unchanged: int = 0
    error: str | None = None


@dataclass
class Status:
    job: str
    day: str
    started_at: str
    finished_at: str = ""
    ok: bool = False
    manifest_key: str = ""
    proof_keys: list[str] = field(default_factory=list)
    witness_error: str | None = None
    resources: list[ResourceStatus] = field(default_factory=list)
    #: "<resource>/<dataset>" -> {"sha256", "day", "key"}: the latest copy of each artefact.
    digests: dict[str, dict[str, str]] = field(default_factory=dict)
    #: "<resource>/<dataset>" -> the `extra` of its latest capture (e.g. CKAN last_modified).
    extras: dict[str, dict[str, str]] = field(default_factory=dict)


def raw_key(resource: Resource, day: date, sha256: str) -> str:
    return f"raw/{resource.source}/{resource.resource}/{day.isoformat()}/{sha256}"


def manifest_key(day: date) -> str:
    return f"manifests/{day.isoformat()}.ndjson"


def status_key(job: str, day: date | None) -> str:
    return f"status/{job}/{day.isoformat() if day else 'latest'}.json"


def previous_status(store: ObjectStore, job: str) -> dict[str, Any]:
    latest = store.get(status_key(job, None))
    return json.loads(latest) if latest is not None else {}


def manifest_line(
    resource: Resource,
    captured: Captured,
    day: date,
    sha256: str,
    key: str,
    fetched_at: str,
    unchanged_from: str | None,
) -> dict[str, Any]:
    return {
        "day": day.isoformat(),
        "source": resource.source,
        "resource": resource.resource,
        "dataset": captured.dataset,
        "url": captured.url,
        "key": key,
        "sha256": sha256,
        "bytes": len(captured.body),
        "fetched_at": fetched_at,
        "http": captured.headers,
        "extra": captured.extra,
        "unchanged_from": unchanged_from,
    }


def run_capture(
    plan: Iterable[Resource],
    fetcher: Fetcher,
    store: ObjectStore,
    *,
    day: date,
    job: str = JOB,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ping: Callable[[bool, str], None] | None = None,
    witness: Callable[[bytes, str], dict[str, bytes]] | None = None,
) -> Status:
    status = Status(job=job, day=day.isoformat(), started_at=now().isoformat(timespec="seconds"))
    before = previous_status(store, job)
    status.digests = before.get("digests", {})
    status.extras = before.get("extras", {})
    lines: list[dict[str, Any]] = []
    for resource in plan:
        rs = ResourceStatus(name=resource.name, strategy=resource.strategy)
        status.resources.append(rs)
        strategy = STRATEGIES.get(resource.strategy)
        if strategy is None:
            rs.error = f"unknown strategy {resource.strategy!r}"
            continue
        try:
            kwargs = {"previous": status.extras} if resource.strategy == "ckan" else {}
            for captured in strategy(resource, fetcher, day, **kwargs):
                sha256 = hashlib.sha256(captured.body).hexdigest()
                slot = f"{resource.resource}/{captured.dataset}"
                previous = status.digests.get(slot)
                unchanged_from = (
                    previous["day"] if previous and previous["sha256"] == sha256 else None
                )
                # The manifest line points at the object that holds the bytes:
                # the day they were first captured, not today.
                key = (
                    previous.get("key")
                    or raw_key(resource, date.fromisoformat(previous["day"]), sha256)
                    if unchanged_from is not None and previous
                    else raw_key(resource, day, sha256)
                )
                if unchanged_from is None and not store.exists(key):
                    store.put(
                        key,
                        captured.body,
                        content_type=captured.headers.get(
                            "content-type", "application/octet-stream"
                        ),
                    )
                if unchanged_from is not None:
                    rs.unchanged += 1
                fetched_at = now().isoformat(timespec="seconds")
                lines.append(
                    manifest_line(resource, captured, day, sha256, key, fetched_at, unchanged_from)
                )
                status.digests[slot] = {
                    "sha256": sha256,
                    "day": unchanged_from or day.isoformat(),
                    "key": key,
                }
                if captured.extra and "skipped" not in captured.extra:
                    status.extras[slot] = dict(captured.extra)
                rs.artefacts += 1
                rs.bytes += len(captured.body)
        except Exception as exc:  # noqa: BLE001 - one resource's failure never stops the others
            rs.error = f"{type(exc).__name__}: {exc}"[:500]
    existing = store.get(manifest_key(day))
    text = (existing.decode() if existing else "") + "".join(
        json.dumps(line) + "\n" for line in lines
    )
    store.put(manifest_key(day), text.encode(), content_type="application/x-ndjson")
    status.manifest_key = manifest_key(day)
    if witness is not None:
        try:
            proofs = witness(text.encode(), f"{day.isoformat()}.ndjson")
            for name, body in proofs.items():
                key = f"proofs/{name}"
                store.put(key, body, content_type="application/octet-stream")
                status.proof_keys.append(key)
        except Exception as exc:  # noqa: BLE001 - a missing proof is reported, never fatal
            status.witness_error = f"{type(exc).__name__}: {exc}"[:500]
    status.finished_at = now().isoformat(timespec="seconds")
    status.ok = all(r.error is None for r in status.resources)
    body = json.dumps(asdict(status), indent=1).encode()
    store.put(status_key(job, day), body, content_type="application/json")
    store.put(status_key(job, None), body, content_type="application/json")
    if ping is not None:
        summary = "; ".join(
            f"{r.name}: {r.artefacts} artefacts" + (f" ERROR {r.error}" if r.error else "")
            for r in status.resources
        )
        ping(status.ok, summary[:10000])
    return status


def healthcheck_pinger(fetcher: Fetcher, url: str | None) -> Callable[[bool, str], None] | None:
    """healthchecks.io: a hit on the URL is success, on `/fail` a failure;
    the body is kept as the check's log."""
    if not url:
        return None

    def ping(ok: bool, body: str) -> None:
        # A failed ping must not fail the run.
        with contextlib.suppress(Exception):
            fetcher.get(url if ok else url.rstrip("/") + "/fail", data=body.encode())

    return ping
