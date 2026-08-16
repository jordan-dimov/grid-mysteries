import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from grid_mysteries.hashing import sha256_file
from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.pinning import fetch_journalled, load_journal


def fake_fetch_factory(payloads: dict[str, bytes], calls: list[str]):
    def fake_fetch(*, url: str, destination: Path, dataset: str) -> SourceArtifact:
        calls.append(url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payloads[url])
        return SourceArtifact(
            source="test",
            dataset=dataset,
            path=destination,
            sha256=sha256_file(destination),
            fetched_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    return fake_fetch


def test_fetch_journalled_pins_and_resumes_without_refetching(tmp_path: Path) -> None:
    root = tmp_path
    jobs = [
        ("D1", "https://example.invalid/a", root / "raw" / "a.json"),
        ("D2", "https://example.invalid/b", root / "raw" / "b.json"),
    ]
    payloads = {job[1]: job[1].encode() for job in jobs}
    journal_path = root / "journal.ndjson"
    manifest_path = root / "manifest.json"

    calls: list[str] = []
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=journal_path,
        manifest_path=manifest_path,
        repo_root=root,
        fetch=fake_fetch_factory(payloads, calls),
        sleep_seconds=0,
    )
    assert (fetched, skipped) == (2, 0)
    assert len(calls) == 2

    # Resume: everything verified and skipped, nothing refetched.
    fetched, skipped = fetch_journalled(
        jobs,
        journal_path=journal_path,
        manifest_path=manifest_path,
        repo_root=root,
        fetch=fake_fetch_factory(payloads, calls),
        sleep_seconds=0,
    )
    assert (fetched, skipped) == (0, 2)
    assert len(calls) == 2

    manifest = json.loads(manifest_path.read_text())
    assert [entry["path"] for entry in manifest] == ["raw/a.json", "raw/b.json"]
    assert load_journal(journal_path).keys() == {"raw/a.json", "raw/b.json"}


def test_fetch_journalled_refuses_unjournalled_and_corrupted_artefacts(tmp_path: Path) -> None:
    root = tmp_path
    job = [("D1", "https://example.invalid/a", root / "raw" / "a.json")]
    payloads = {job[0][1]: b"original"}
    journal_path = root / "journal.ndjson"
    manifest_path = root / "manifest.json"

    orphan = root / "raw" / "a.json"
    orphan.parent.mkdir(parents=True)
    orphan.write_bytes(b"unjournalled")
    with pytest.raises(RuntimeError, match="not journalled"):
        fetch_journalled(
            job,
            journal_path=journal_path,
            manifest_path=manifest_path,
            repo_root=root,
            fetch=fake_fetch_factory(payloads, []),
            sleep_seconds=0,
        )

    orphan.unlink()
    fetch_journalled(
        job,
        journal_path=journal_path,
        manifest_path=manifest_path,
        repo_root=root,
        fetch=fake_fetch_factory(payloads, []),
        sleep_seconds=0,
    )
    orphan.write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="digest"):
        fetch_journalled(
            job,
            journal_path=journal_path,
            manifest_path=manifest_path,
            repo_root=root,
            fetch=fake_fetch_factory(payloads, []),
            sleep_seconds=0,
        )
