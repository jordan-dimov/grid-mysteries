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


def test_pull_overwrite_lets_the_archive_win_for_the_unattended_job(tmp_path: Path):
    """The Docker image carries the repository's acquisition log as of the
    build; after the job's own previous run pushed a newer one, the next
    pull must take the archive's, or the job fails before acquiring anything
    (tracker-013, 2026-09-18). JSON rewritten by write_json is not a byte
    prefix of its earlier self, so growth-only replacement does not apply."""
    store = LocalStore(tmp_path / "bucket")
    key = "state/013/investigations/013/evidence/acquisition-log.json"
    store.put(key, b'{\n "runs": [1, 2]\n}')
    repo = tmp_path / "repo"
    (repo / "investigations/013/evidence").mkdir(parents=True)
    local = repo / "investigations/013/evidence/acquisition-log.json"
    local.write_bytes(b'{\n "runs": [1]\n}')
    assert state.pull(store, repo, "013")[0].startswith("MISMATCH")
    assert local.read_bytes() == b'{\n "runs": [1]\n}'
    report = state.pull(store, repo, "013", overwrite=True)
    assert report == [f"replaced {key} -> {local}"]
    assert local.read_bytes() == b'{\n "runs": [1, 2]\n}'
    assert state.pull(store, repo, "013", overwrite=True) == []


def test_push_include_globs_keep_computed_files_out(tmp_path: Path):
    store = LocalStore(tmp_path / "bucket")
    repo = tmp_path / "repo"
    ev = repo / "investigations/013/evidence"
    ev.mkdir(parents=True)
    (ev / "batch-01-journal.ndjson").write_bytes(b"{}\n")
    (ev / "batch-01-manifest.json").write_bytes(b"[]")
    (ev / "acquisition-log.json").write_bytes(b"{}")
    (ev / "tracker.json").write_bytes(b"{}")
    pushed = state.push(
        store,
        repo,
        "013",
        [Path("investigations/013/evidence")],
        include=["*-journal.ndjson", "*-manifest.json", "acquisition-log.json"],
    )
    assert pushed == [
        "state/013/investigations/013/evidence/acquisition-log.json",
        "state/013/investigations/013/evidence/batch-01-journal.ndjson",
        "state/013/investigations/013/evidence/batch-01-manifest.json",
    ]
