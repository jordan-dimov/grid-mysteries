import json
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from grid_mysteries.capture import timestamp as ts
from grid_mysteries.capture.fetch import CannedFetcher, Response
from grid_mysteries.capture.store import LocalStore
from grid_mysteries.sources.archive import Archive, ArchiveError


def fake_runner(calls, *, fail_ots=False):
    def run(command):
        calls.append(command)
        if command[:3] == ["openssl", "ts", "-query"]:
            Path(command[command.index("-out") + 1]).write_bytes(b"TSQ")
        elif command[:2] == ["ots", "stamp"]:
            if fail_ots:
                raise subprocess.CalledProcessError(1, command)
            Path(command[2] + ".ots").write_bytes(b"OTS")
        return subprocess.CompletedProcess(command, 0, b"", b"")

    return run


def test_witness_produces_query_two_tokens_ots_and_a_sidecar(tmp_path: Path):
    calls: list[list[str]] = []
    fetcher = CannedFetcher(
        {
            "https://freetsa.org/tsr": Response("https://freetsa.org/tsr", 200, b"TSR1"),
            "http://timestamp.digicert.com": Response(
                "http://timestamp.digicert.com", 200, b"TSR2"
            ),
        }
    )
    proofs = ts.witness(
        b"{}\n",
        "2026-09-15.ndjson",
        tmp_path,
        fetcher=fetcher,
        run=fake_runner(calls),
        now=lambda: datetime(2026, 9, 15, 6, 40, tzinfo=UTC),
    )
    assert set(proofs) == {
        "2026-09-15.ndjson.tsq",
        "2026-09-15.ndjson.freetsa.tsr",
        "2026-09-15.ndjson.digicert.tsr",
        "2026-09-15.ndjson.ots",
        "2026-09-15.ndjson.timestamps.json",
    }
    assert proofs["2026-09-15.ndjson.freetsa.tsr"] == b"TSR1"
    assert fetcher.calls[0] == ("https://freetsa.org/tsr", b"TSQ")
    sidecar = json.loads(proofs["2026-09-15.ndjson.timestamps.json"])
    assert sidecar["failures"] == []
    assert [p["kind"] for p in sidecar["proofs"]] == ["rfc3161", "rfc3161", "opentimestamps"]
    assert calls[0][:3] == ["openssl", "ts", "-query"] and calls[-1][:2] == ["ots", "stamp"]


def test_a_failed_authority_or_ots_is_recorded_not_hidden(tmp_path: Path):
    fetcher = CannedFetcher(
        {"https://freetsa.org/tsr": Response("https://freetsa.org/tsr", 200, b"TSR1")}
    )
    proofs = ts.witness(
        b"x", "d.ndjson", tmp_path, fetcher=fetcher, run=fake_runner([], fail_ots=True)
    )
    assert "d.ndjson.freetsa.tsr" in proofs
    assert "d.ndjson.digicert.tsr" not in proofs and "d.ndjson.ots" not in proofs
    sidecar = json.loads(proofs["d.ndjson.timestamps.json"])
    assert any(f.startswith("digicert:") for f in sidecar["failures"])
    assert any(f.startswith("ots stamp:") for f in sidecar["failures"])


def test_upload_proofs_lands_under_the_proofs_prefix(tmp_path: Path):
    store = LocalStore(tmp_path)
    keys = ts.upload_proofs(store, {"2026-09-15.ndjson.ots": b"OTS"})
    assert keys == ["proofs/2026-09-15.ndjson.ots"]
    assert store.get("proofs/2026-09-15.ndjson.ots") == b"OTS"


def line(
    store: LocalStore, day="2026-09-15", body=b"Project Name\nA\n", dataset="NESO-TEC-REGISTER"
):
    import hashlib

    sha = hashlib.sha256(body).hexdigest()
    key = f"raw/neso/tec-register/{day}/{sha}"
    store.put(key, body)
    entry = {
        "day": day,
        "source": "neso",
        "resource": "tec-register",
        "dataset": dataset,
        "url": "https://api.neso.energy/dl/tec.csv",
        "key": key,
        "sha256": sha,
        "bytes": len(body),
        "fetched_at": f"{day}T06:31:00+00:00",
        "http": {"etag": '"e"'},
        "extra": {"ckan_last_modified": f"{day}T05:00:00"},
        "unchanged_from": None,
    }
    store.put(f"manifests/{day}.ndjson", (json.dumps(entry) + "\n").encode())
    return entry


def test_archive_finds_reads_verifies_and_pins_with_a_journal(tmp_path: Path):
    store = LocalStore(tmp_path / "bucket")
    entry = line(store)
    archive = Archive(store)
    assert archive.find(date(2026, 9, 15), "NESO-TEC-REGISTER") == entry
    assert archive.find(date(2026, 9, 15), "OTHER") is None
    assert archive.manifest(date(2026, 9, 14)) == []
    assert archive.read(entry) == b"Project Name\nA\n"
    repo = tmp_path / "repo"
    dest = repo / "data/raw/neso/tec-history/2026-09-15_archive.csv"
    journal = repo / "data/raw/neso/tec-history/journal.ndjson"
    pinned = archive.pin(entry, dest, journal_path=journal, repo_root=repo)
    assert dest.read_bytes() == b"Project Name\nA\n"
    assert pinned["source"] == "archive" and pinned["archive_key"] == entry["key"]
    assert pinned["path"] == "data/raw/neso/tec-history/2026-09-15_archive.csv"
    assert json.loads(journal.read_text().splitlines()[0]) == pinned
    # pinning again over identical bytes is fine; different bytes are refused
    archive.pin(entry, dest, journal_path=journal, repo_root=repo)
    dest.write_bytes(b"tampered")
    with pytest.raises(ArchiveError):
        archive.pin(entry, dest, journal_path=journal, repo_root=repo)


def test_archive_refuses_bytes_that_do_not_hash_as_the_manifest_says(tmp_path: Path):
    store = LocalStore(tmp_path)
    entry = line(store)
    store.put(entry["key"], b"corrupted")
    with pytest.raises(ArchiveError):
        Archive(store).read(entry)
    with pytest.raises(ArchiveError):
        Archive(store).read({**entry, "key": "raw/missing"})
