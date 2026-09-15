from pathlib import Path

from grid_mysteries.capture import state
from grid_mysteries.capture.store import LocalStore


def test_push_uploads_new_and_changed_files_only(tmp_path: Path):
    store = LocalStore(tmp_path / "bucket")
    repo = tmp_path / "repo"
    (repo / "data/raw/elexon/013/2026-09-09").mkdir(parents=True)
    (repo / "data/raw/elexon/013/2026-09-09/ebocf_offer.json").write_bytes(b"[]")
    (repo / "investigations/013/evidence").mkdir(parents=True)
    (repo / "investigations/013/evidence/batch-01-journal.ndjson").write_bytes(b"{}\n")
    paths = [Path("data/raw/elexon/013"), Path("investigations/013/evidence"), Path("missing")]
    first = state.push(store, repo, "013", paths)
    assert first == [
        "state/013/data/raw/elexon/013/2026-09-09/ebocf_offer.json",
        "state/013/investigations/013/evidence/batch-01-journal.ndjson",
    ]
    assert state.push(store, repo, "013", paths) == []
    (repo / "investigations/013/evidence/batch-01-journal.ndjson").write_bytes(b"{}\n{}\n")
    assert state.push(store, repo, "013", paths) == [
        "state/013/investigations/013/evidence/batch-01-journal.ndjson"
    ]


def test_pull_downloads_grows_journals_and_reports_conflicts(tmp_path: Path):
    store = LocalStore(tmp_path / "bucket")
    store.put("state/013/investigations/013/evidence/j.ndjson", b"{}\n{}\n")
    store.put("state/013/data/raw/elexon/013/a.json", b"[]")
    repo = tmp_path / "repo"
    (repo / "investigations/013/evidence").mkdir(parents=True)
    (repo / "investigations/013/evidence/j.ndjson").write_bytes(b"{}\n")
    report = state.pull(store, repo, "013")
    assert report == [
        f"state/013/data/raw/elexon/013/a.json -> {repo / 'data/raw/elexon/013/a.json'}",
        f"grew state/013/investigations/013/evidence/j.ndjson -> "
        f"{repo / 'investigations/013/evidence/j.ndjson'}",
    ]
    assert (repo / "investigations/013/evidence/j.ndjson").read_bytes() == b"{}\n{}\n"
    assert state.pull(store, repo, "013") == []
    (repo / "data/raw/elexon/013/a.json").write_bytes(b"tampered")
    report = state.pull(store, repo, "013")
    assert report[0].startswith("MISMATCH state/013/data/raw/elexon/013/a.json")
    assert (repo / "data/raw/elexon/013/a.json").read_bytes() == b"tampered"
