import hashlib
import json
import random
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from grid_mysteries.capture import watchdog as wd
from grid_mysteries.capture.store import LocalStore

NOW = datetime(2026, 9, 16, 9, 0, tzinfo=UTC)


def status(day: date, *, ok=True, finished=None, resources=None):
    return json.dumps(
        {
            "job": "vintage-capture",
            "day": day.isoformat(),
            "finished_at": (
                finished
                or datetime.combine(day, datetime.min.time(), UTC).replace(hour=6, minute=45)
            ).isoformat(),
            "ok": ok,
            "resources": resources
            or [
                {
                    "name": "NESO-TEC-REGISTER",
                    "strategy": "ckan",
                    "artefacts": 2,
                    "bytes": 400_000,
                    "unchanged": 0,
                    "error": None,
                }
            ],
        }
    ).encode()


def seed(store: LocalStore, days: int = 10, *, today: date = date(2026, 9, 16)):
    for back in range(days, -1, -1):
        day = today - timedelta(days=back)
        store.put(f"status/vintage-capture/{day}.json", status(day))
    store.put("status/vintage-capture/latest.json", status(today))
    body = b"Project Name\nA\n"
    key = f"raw/neso/tec-register/{today - timedelta(days=1)}/{hashlib.sha256(body).hexdigest()}"
    store.put(key, body)
    line = {
        "day": str(today - timedelta(days=1)),
        "dataset": "NESO-TEC-REGISTER",
        "key": key,
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    store.put(f"manifests/{today - timedelta(days=1)}.ndjson", (json.dumps(line) + "\n").encode())
    store.put(f"manifests/{today}.ndjson", b"")
    for day in (today, today - timedelta(days=1)):
        store.put(
            f"proofs/{day}.ndjson.timestamps.json",
            json.dumps(
                {"proofs": [{"kind": "rfc3161"}, {"kind": "opentimestamps"}], "failures": []}
            ).encode(),
        )
    return key


def test_a_healthy_archive_passes_every_check_and_syncs(tmp_path: Path):
    store = LocalStore(tmp_path / "bucket")
    seed(store)
    store.put(
        "state/013/investigations/013-the-cover-price-tracker/evidence/x-manifest.json", b"[]"
    )
    repo = tmp_path / "repo"
    report = wd.run_watchdog(
        store, repo_root=repo, now=lambda: NOW, jobs={"vintage-capture": 26}, rng=random.Random(1)
    )
    assert report.ok, [c for c in report.checks if not c.ok]
    names = [c.name for c in report.checks]
    assert (
        "fresh:vintage-capture" in names
        and "sample:2026-09-15" in names
        and "bucket-settings" in names
    )
    assert (repo / "data/manifests/2026-09-15.ndjson").exists()
    assert (repo / "data/manifests/2026-09-15.ndjson.timestamps.json").exists()
    assert (
        repo / "investigations/013-the-cover-price-tracker/evidence/x-manifest.json"
    ).read_bytes() == b"[]"
    assert not (repo / "data/raw/archive").exists()
    again = wd.run_watchdog(
        store, repo_root=repo, now=lambda: NOW, jobs={"vintage-capture": 26}, rng=random.Random(1)
    )
    assert again.synced == []  # nothing new, nothing overwritten


def test_stale_or_failed_status_fails_freshness(tmp_path: Path):
    store = LocalStore(tmp_path)
    seed(store)
    stale = status(date(2026, 9, 16), finished=NOW - timedelta(hours=30))
    store.put("status/vintage-capture/latest.json", stale)
    checks = wd.check_freshness(store, {"vintage-capture": 26}, NOW)
    assert checks[0].ok is False and "30.0 h ago" in checks[0].detail
    store.put("status/vintage-capture/latest.json", status(date(2026, 9, 16), ok=False))
    assert wd.check_freshness(store, {"vintage-capture": 26}, NOW)[0].ok is False
    assert wd.check_freshness(store, {"tracker-013": 26}, NOW)[0].detail == "no status object yet"


def test_a_source_that_shrinks_to_a_login_page_fails_the_band(tmp_path: Path):
    store = LocalStore(tmp_path)
    seed(store)
    tiny = [
        {
            "name": "NESO-TEC-REGISTER",
            "strategy": "ckan",
            "artefacts": 2,
            "bytes": 1_200,
            "unchanged": 0,
            "error": None,
        }
    ]
    store.put("status/vintage-capture/2026-09-16.json", status(date(2026, 9, 16), resources=tiny))
    checks = wd.check_bands(store, "vintage-capture", date(2026, 9, 16))
    assert checks[0].ok is False and "1,200 bytes" in checks[0].detail
    fresh = LocalStore(tmp_path / "new")
    fresh.put("status/vintage-capture/2026-09-16.json", status(date(2026, 9, 16)))
    assert wd.check_bands(fresh, "vintage-capture", date(2026, 9, 16))[0].detail.endswith(
        "no band yet"
    )


def test_sample_detects_a_corrupted_object_and_proofs_detect_a_missing_sidecar(tmp_path: Path):
    store = LocalStore(tmp_path)
    key = seed(store)
    assert wd.check_sample(store, date(2026, 9, 15), rng=random.Random(0)).ok is True
    store.put(key, b"corrupted")
    check = wd.check_sample(store, date(2026, 9, 15), rng=random.Random(0))
    assert check.ok is False and "MISMATCH" in check.detail
    assert wd.check_sample(store, date(2026, 9, 1)).ok is False
    proofs = wd.check_proofs(store, date(2026, 9, 16))
    assert all(c.ok for c in proofs) and len(proofs) == 2
    store.put(
        "proofs/2026-09-16.ndjson.timestamps.json",
        json.dumps({"proofs": [{"kind": "rfc3161"}], "failures": ["ots stamp: x"]}).encode(),
    )
    assert wd.check_proofs(store, date(2026, 9, 16))[0].ok is False


def test_bucket_settings_drift_is_named():
    assert (
        wd.check_bucket_settings(None, wd.EXPECTED_SETTINGS).detail == "local store; not applicable"
    )
    good = dict(wd.EXPECTED_SETTINGS)
    assert wd.check_bucket_settings(lambda: good, wd.EXPECTED_SETTINGS).ok is True
    bad = dict(good, object_lock=None)
    check = wd.check_bucket_settings(lambda: bad, wd.EXPECTED_SETTINGS)
    assert check.ok is False and "object_lock" in check.detail

    def boom():
        raise RuntimeError("denied")

    assert wd.check_bucket_settings(boom, wd.EXPECTED_SETTINGS).ok is False


def test_sync_never_overwrites_different_local_bytes(tmp_path: Path):
    store = LocalStore(tmp_path / "bucket")
    store.put("manifests/2026-09-15.ndjson", b"new")
    repo = tmp_path / "repo"
    (repo / "data/manifests").mkdir(parents=True)
    (repo / "data/manifests/2026-09-15.ndjson").write_bytes(b"old")
    synced = wd.sync(store, repo)
    assert synced == [
        f"MISMATCH manifests/2026-09-15.ndjson -> {repo / 'data/manifests/2026-09-15.ndjson'}"
    ]
    assert (repo / "data/manifests/2026-09-15.ndjson").read_bytes() == b"old"
    store.put("raw/neso/x/2026-09-15/abc", b"bytes")
    wd.sync(store, repo, include_bytes=True)
    assert (repo / "data/raw/archive/raw/neso/x/2026-09-15/abc").read_bytes() == b"bytes"
