import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from grid_mysteries.tec import watch as w

HEADER = (
    "Project Name,Customer Name,Connection Site,Stage,MW Connected,MW Increase / Decrease,"
    "Cumulative Total Capacity (MW),MW Effective From,Project Status,Agreement Type,HOST TO,"
    "Plant Type,Project ID,Project Number,Gate\n"
)
NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def row(
    name="Zenobe Stalybridge Project",
    customer="ZENOBE STALYBRIDGE LIMITED",
    site="Stalybridge 275kV Substation",
    mw="150.00",
    date="30/09/2027",
    status="Scoping",
    pid="a0l4L0000005iuVQAQ",
    gate="",
    stage="",
):
    return (
        f"{name},{customer},{site},{stage},0.00,{mw},{mw},{date},{status},Direct Connection,"
        f"NGET,Energy Storage System,{pid},PRO-001940,{gate}\n"
    )


def copy(tmp_path: Path, day: str, t_public: str, body: str, filename="tec.csv"):
    """A manifested and mirrored copy; returns the manifest path."""
    data = (HEADER + body).encode()
    digest = hashlib.sha256(data).hexdigest()
    key = f"raw/neso/tec-register/{day}/{digest}"
    target = tmp_path / "mirror" / key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    record = {
        "day": day,
        "dataset": "NESO-TEC-REGISTER",
        "url": f"https://x/{filename}?sig=1",
        "key": key,
        "sha256": digest,
        "bytes": len(data),
        "fetched_at": f"{day}T06:31:00+00:00",
        "extra": {"ckan_last_modified": f"{t_public}T09:00:00"},
    }
    manifest = tmp_path / "manifests" / f"{day}.ndjson"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(record) + "\n")
    return manifest


ENTRY = w.WatchEntry(
    label="stalybridge",
    project="Zenobe Stalybridge Project",
    customer="ZENOBE STALYBRIDGE LIMITED",
    mw="150",
)


def run(tmp_path, manifests, state=None, watchlist=(ENTRY,)):
    return w.run(
        watchlist=list(watchlist),
        manifests=manifests,
        mirror=tmp_path / "mirror",
        state=state or w.WatchState(),
        now=NOW,
    )


def test_first_copy_gives_first_sight_and_locks_the_id(tmp_path):
    m = copy(
        tmp_path, "2026-09-15", "2026-09-15", row() + row(name="Other", pid="a0l4L0000005other")
    )
    lines, state, stopped = run(tmp_path, [m])
    assert stopped is None
    assert [ln["kind"] for ln in lines] == ["first-sight"]
    assert lines[0]["state"]["MW Effective From"] == "30/09/2027"
    assert lines[0]["copy"]["t_public"] == "2026-09-15"
    assert state.locked == {"stalybridge": ["a0l4L0000005iuV"]}
    assert state.last_t_public == "2026-09-15"
    assert "first sight" in w.human(lines[0])


def test_no_change_between_copies_writes_nothing(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    # Identical bytes would be one copy (capture_entries keys by digest), so
    # the second copy differs only in a row the watch does not follow.
    b = copy(
        tmp_path, "2026-09-19", "2026-09-18", row() + row(name="Unwatched", pid="a0l4L0000005un")
    )
    lines, state, _ = run(tmp_path, [a, b])
    assert [ln["kind"] for ln in lines] == ["first-sight"]
    assert state.copies_seen == [
        json.loads(a.read_text())["sha256"],
        json.loads(b.read_text())["sha256"],
    ]


def test_a_date_and_a_status_change_give_one_line_each_with_both_digests(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    b = copy(
        tmp_path, "2026-09-19", "2026-09-18", row(date="2029-03-31", status="Awaiting Consents")
    )
    lines, _, _ = run(tmp_path, [a, b])
    changes = [ln for ln in lines if ln["kind"] == "change"]
    assert [(c["field"], c["before"], c["after"]) for c in changes] == [
        ("MW Effective From", "30/09/2027", "2029-03-31"),
        ("Project Status", "Scoping", "Awaiting Consents"),
    ]
    assert changes[0]["from_copy"]["sha256"] == json.loads(a.read_text())["sha256"]
    assert changes[0]["to_copy"]["sha256"] == json.loads(b.read_text())["sha256"]
    assert "30/09/2027 -> 2029-03-31" in w.human(changes[0])


def test_a_renamed_project_is_followed_by_its_id_and_the_rename_is_a_line(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    b = copy(
        tmp_path,
        "2026-09-19",
        "2026-09-18",
        row(name="Stalybridge BESS Phase 1", customer="ZENOBE ENERGY LIMITED"),
    )
    lines, state, _ = run(tmp_path, [a, b])
    changes = {ln["field"]: (ln["before"], ln["after"]) for ln in lines if ln["kind"] == "change"}
    assert changes == {
        "Customer Name": ("ZENOBE STALYBRIDGE LIMITED", "ZENOBE ENERGY LIMITED"),
        "Project Name": ("Zenobe Stalybridge Project", "Stalybridge BESS Phase 1"),
    }
    # A third copy with the new name only is still followed: no left/arrived.
    c = copy(
        tmp_path,
        "2026-09-23",
        "2026-09-22",
        row(name="Stalybridge BESS Phase 1", customer="ZENOBE ENERGY LIMITED", gate="2"),
    )
    lines2, _, _ = run(tmp_path, [a, b, c], state=state)
    assert [(ln["kind"], ln["field"]) for ln in lines2] == [("change", "Gate")]


def test_rows_leaving_and_arriving_are_lines(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    b = copy(
        tmp_path,
        "2026-09-19",
        "2026-09-18",
        row(stage="2", pid="a0l4L0000005iuVQAQ") + row(name="Nothing here", pid="a0l4L0000005zzzz"),
    )
    lines, _, _ = run(tmp_path, [a, b])
    kinds = [(ln["kind"], ln["key"]) for ln in lines if ln["kind"] != "first-sight"]
    assert kinds == [("left", "id:a0l4L0000005iuV|"), ("arrived", "id:a0l4L0000005iuV|2")]
    assert "row left" in w.human(lines[1]) and "row arrived" in w.human(lines[2])


def test_seed_mismatch_is_reported_and_the_row_still_followed(tmp_path):
    a = copy(
        tmp_path, "2026-09-15", "2026-09-15", row(customer="ZENOBE ENERGY LIMITED", mw="100.00")
    )
    lines, state, _ = run(tmp_path, [a])
    assert [ln["kind"] for ln in lines] == ["first-sight", "seed-mismatch", "seed-mismatch"]
    assert lines[1]["field"] == "Customer Name" and lines[1]["printed"] == "ZENOBE ENERGY LIMITED"
    assert lines[2]["field"] == "MW Increase / Decrease" and lines[2]["seeded"] == "150"
    assert state.locked["stalybridge"] == ["a0l4L0000005iuV"]
    assert "seeded Customer Name" in w.human(lines[1])


def test_state_advances_and_a_rerun_writes_nothing(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    b = copy(tmp_path, "2026-09-19", "2026-09-18", row(date="2029-03-31"))
    lines, state, _ = run(tmp_path, [a, b])
    assert len(lines) == 2
    again, state2, _ = run(tmp_path, [a, b], state=state)
    assert again == [] and state2.last_sha256 == state.last_sha256


def test_an_unmirrored_copy_stops_before_it_and_keeps_the_state(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    b = copy(tmp_path, "2026-09-19", "2026-09-18", row(date="2029-03-31"))
    key = json.loads(b.read_text())["key"]
    (tmp_path / "mirror" / key).unlink()
    lines, state, stopped = run(tmp_path, [a, b])
    assert [ln["kind"] for ln in lines] == ["first-sight"]
    assert state.last_t_public == "2026-09-15"
    assert stopped and "not yet mirrored" in stopped


def test_altered_mirror_bytes_stop_the_run(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    key = json.loads(a.read_text())["key"]
    (tmp_path / "mirror" / key).write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="manifested digest"):
        run(tmp_path, [a])


def test_a_state_naming_an_unknown_copy_refuses(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    with pytest.raises(RuntimeError, match="not among the captured copies"):
        run(tmp_path, [a], state=w.WatchState(last_sha256="f" * 64))


def test_watchlist_labels_must_be_distinct(tmp_path):
    p = tmp_path / "w.json"
    p.write_text(
        json.dumps({"watch": [{"label": "a", "project": "X"}, {"label": "a", "project": "Y"}]})
    )
    with pytest.raises(ValueError):
        w.load_watchlist(p)
    p.write_text(
        json.dumps({"watch": [{"label": "a", "project": "X", "customer": "C", "mw": "1"}]})
    )
    assert w.load_watchlist(p) == [w.WatchEntry("a", "X", "C", "1")]


def test_main_writes_log_state_and_prints_lines(tmp_path, capsys):
    repo = tmp_path
    (repo / "data").mkdir()
    (repo / "data/manifests").symlink_to(tmp_path / "manifests")
    (repo / "data/raw").mkdir()
    (repo / "data/raw/archive").symlink_to(tmp_path / "mirror")
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    b = copy(tmp_path, "2026-09-19", "2026-09-18", row(status="Consents Approved"))
    assert a.parent == repo / "data/manifests" or True
    wdir = repo / "data/derived/tec-watch"
    wdir.mkdir(parents=True)
    (wdir / "watchlist.json").write_text(json.dumps({"watch": [ENTRY.__dict__]}))
    assert w.main(["--repo", str(repo)]) == 0
    out = capsys.readouterr()
    assert "first sight" in out.out and "Scoping -> Consents Approved" in out.out
    assert "2 line(s)" in out.err
    assert len((wdir / "watch-log.ndjson").read_text().splitlines()) == 2
    assert json.loads((wdir / "state.json").read_text())["last_t_public"] == "2026-09-18"
    assert w.main(["--repo", str(repo)]) == 0
    assert capsys.readouterr().out == ""
    assert b.exists()


def test_a_respelled_date_or_mw_is_logged_not_reported(tmp_path):
    a = copy(tmp_path, "2026-09-15", "2026-09-15", row())
    b = copy(tmp_path, "2026-09-19", "2026-09-18", row(date="2027-09-30", mw="150.00"))
    lines, _, _ = run(tmp_path, [a, b])
    kinds = {(ln["kind"], ln["field"]) for ln in lines if ln["kind"] != "first-sight"}
    assert kinds == {("respelling", "MW Effective From")}
    b2 = copy(tmp_path, "2026-09-20", "2026-09-19", row(date="2027-09-30", mw="150"))
    lines_mw, _, _ = run(tmp_path, [a, b, b2])
    assert {(ln["kind"], ln["field"]) for ln in lines_mw[-2:]} == {
        ("respelling", "MW Increase / Decrease"),
        ("respelling", "Cumulative Total Capacity (MW)"),
    }
    assert "respelled MW Effective From 30/09/2027 -> 2027-09-30" in w.human(lines[1])
    # A date that stops parsing is a change, not a respelling.
    c = copy(tmp_path, "2026-09-23", "2026-09-22", row(date="TBC", mw="150.00"))
    lines2, _, _ = run(tmp_path, [a, b, c])
    changes = [(ln["kind"], ln["field"]) for ln in lines2 if ln["kind"] in ("change", "respelling")]
    assert changes[-1] == ("change", "MW Effective From")
    assert w.same_value("Stage", "1", "1.0") and not w.same_value("Gate", "1", "2")
