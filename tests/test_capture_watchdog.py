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
    store.put("status/vintage-capture/latest.json", status(date(2026, 9, 16), resources=tiny))
    checks = wd.check_bands(store, "vintage-capture")
    assert checks[0].ok is False and "1,200 bytes" in checks[0].detail
    fresh = LocalStore(tmp_path / "new")
    fresh.put("status/vintage-capture/latest.json", status(date(2026, 9, 16)))
    assert wd.check_bands(fresh, "vintage-capture")[0].detail.endswith("no band yet")
    assert wd.check_bands(LocalStore(tmp_path / "empty"), "vintage-capture")[0].ok is False


def test_a_run_before_the_day_s_capture_bands_the_latest_status_not_today_s(tmp_path: Path):
    """The 04:12 watchdog run precedes the 06:30 capture; the band is anchored
    on latest.json (yesterday's run), and the absence of today's dated
    status is not a failure. Regression for the 2026-09-18 04:12 alert."""
    store = LocalStore(tmp_path)
    seed(store, today=date(2026, 9, 17))  # latest is the 17th; "today" is the 18th
    report = wd.run_watchdog(
        store,
        repo_root=tmp_path / "repo",
        now=lambda: datetime(2026, 9, 18, 3, 12, tzinfo=UTC),
        jobs={"vintage-capture": 26},
        rng=random.Random(1),
    )
    bands = [c for c in report.checks if c.name.startswith("band:")]
    assert bands and all(c.ok for c in bands)
    assert "no status for" not in " ".join(c.detail for c in report.checks)


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


LOG = {"seal": "d20d5920", "runs": [{"run_date": "2026-09-18", "batches": []}]}


def test_extends_accepts_appended_lines_and_appended_json_entries():
    assert wd.extends(b'{"a":1}\n', b'{"a":1}\n{"a":2}\n')
    grown = {**LOG, "runs": [*LOG["runs"], {"run_date": "2026-09-19", "batches": [1]}]}
    assert wd.extends(json.dumps(LOG).encode(), json.dumps(grown, indent=1).encode())
    assert wd.extends(json.dumps([{"p": 1}]).encode(), json.dumps([{"p": 1}, {"p": 2}]).encode())


def test_extends_rejects_edits_reorders_truncation_and_reformatting():
    local = json.dumps([{"p": 1}, {"p": 2}]).encode()
    assert not wd.extends(local, local)
    assert not wd.extends(local, json.dumps([{"p": 1}, {"p": 2}], indent=2).encode())
    assert not wd.extends(local, json.dumps([{"p": 1}, {"p": 3}, {"p": 4}]).encode())
    assert not wd.extends(local, json.dumps([{"p": 2}, {"p": 1}, {"p": 3}]).encode())
    assert not wd.extends(local, json.dumps([{"p": 1}]).encode())
    assert not wd.extends(b'{"a":1}\n{"a":2}\n', b'{"a":1}\n')
    assert not wd.extends(b'{"a":1}\n', b'{"a":9}\n{"a":2}\n')
    edited_seal = {**LOG, "seal": "00000000", "runs": [*LOG["runs"], {"run_date": "x"}]}
    assert not wd.extends(json.dumps(LOG).encode(), json.dumps(edited_seal).encode())
    extra_key = {**LOG, "runs": [*LOG["runs"], {"run_date": "x"}], "note": "?"}
    assert not wd.extends(json.dumps(LOG).encode(), json.dumps(extra_key).encode())
    assert not wd.extends(b"not json", b"also not json")


def test_sync_adopts_grown_state_but_never_grows_raw_manifests_or_proofs(tmp_path: Path):
    store = LocalStore(tmp_path / "bucket")
    repo = tmp_path / "repo"
    evidence = "investigations/013-x/evidence"
    local = {
        f"{evidence}/acquisition-log.json": json.dumps(LOG).encode(),
        f"{evidence}/neso-journal.ndjson": b'{"n":1}\n',
        f"{evidence}/neso-manifest.json": json.dumps([{"n": 1}]).encode(),
        "data/raw/elexon/013/a.json": b'{"n":1}\n',
        "data/manifests/2026-09-15.ndjson": b'{"n":1}\n',
    }
    for path, body in local.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_bytes(body)
    grown_log = {**LOG, "runs": [*LOG["runs"], {"run_date": "2026-09-19", "batches": [1]}]}
    store.put(f"state/013/{evidence}/acquisition-log.json", json.dumps(grown_log).encode())
    store.put(f"state/013/{evidence}/neso-journal.ndjson", b'{"n":1}\n{"n":2}\n')
    store.put(f"state/013/{evidence}/neso-manifest.json", json.dumps([{"n": 9}]).encode())
    store.put("state/013/data/raw/elexon/013/a.json", b'{"n":1}\n{"n":2}\n')
    store.put("manifests/2026-09-15.ndjson", b'{"n":1}\n{"n":2}\n')
    synced = wd.sync(store, repo)
    grew = sorted(s for s in synced if s.startswith("grew"))
    mismatched = sorted(s for s in synced if s.startswith("MISMATCH"))
    assert [s.split()[1] for s in grew] == [
        f"state/013/{evidence}/acquisition-log.json",
        f"state/013/{evidence}/neso-journal.ndjson",
    ]
    assert [s.split()[1] for s in mismatched] == [
        "manifests/2026-09-15.ndjson",
        "state/013/data/raw/elexon/013/a.json",
        f"state/013/{evidence}/neso-manifest.json",
    ]
    assert json.loads((repo / evidence / "acquisition-log.json").read_bytes()) == grown_log
    for path in ("data/raw/elexon/013/a.json", f"{evidence}/neso-manifest.json"):
        assert (repo / path).read_bytes() == local[path]
