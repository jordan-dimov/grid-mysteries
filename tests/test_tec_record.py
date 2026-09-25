"""The TEC record engine: cells, plans, markers, replay, identity, flapping,
certificates. No database; the record is simulated by audit rows."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.tec import analysis, cells, certificate, identity, importer, replay, sources


def row(name="Alpha", customer="Cust", site="Site", mw=100, eff="2025-01-01", **extra):
    out: dict[str, object] = {
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "MW Increase / Decrease": mw,
        "MW Effective From": date.fromisoformat(eff) if eff else None,
    }
    out.update(extra)
    return out


# ------------------------------------------------------------------ cells


@pytest.mark.parametrize(
    "value",
    ["text", " spaced ", "", 340, 340.0, -5, 1e20, 43000.5, date(2019, 8, 1), None, "43000"],
)
def test_cells_round_trip_exactly_type_included(value):
    kind, text = cells.encode_cell(value)
    back = cells.decode_cell(kind, text)
    assert back == value and type(back) is type(value) or (value is None and back is None)


def test_cells_keep_int_and_float_apart_and_text_dates_apart_from_date_cells():
    assert cells.encode_cell(340) != cells.encode_cell(340.0)
    assert cells.encode_cell("2019-08-01") != cells.encode_cell(date(2019, 8, 1))


def test_the_same_printed_number_in_three_formats_is_one_row_with_other_kinds():
    csv, xlsx, xls = row(mw="900"), row(mw=900), row(mw=900.0)
    keys = {next(iter(cells.keyed([r]))) for r in (csv, xlsx, xls)}
    assert len(keys) == 1
    assert len({cells.encode(r)[0] for r in (csv, xlsx, xls)}) == 3


def test_a_format_switch_is_a_rekind_and_replays_to_the_new_types():
    first = importer.plan(None, {}, copy("2020-01-01"), [row(mw="900")])
    second = importer.plan(
        ("tec-2020-01-01", date(2020, 1, 1)), first.state, copy("2020-02-01"), [row(mw=900.0)]
    )
    assert [a["transformation"] for a in second.acts] == ["publish", "rekind", "close_import"]
    pubs = list(replay.fold(audit_rows_for([first, second])))
    assert pubs[0].rows[0]["MW Increase / Decrease"] == "900"
    back = pubs[1].rows[0]["MW Increase / Decrease"]
    assert back == 900.0 and type(back) is float


def test_boolean_cells_are_refused_not_coerced():
    with pytest.raises(cells.CellError):
        cells.encode_cell(True)


def test_identical_rows_get_occurrence_keys_and_order_round_trips():
    rows = [row(), row(name="Beta"), row()]
    keyed = cells.keyed(rows)
    keys = list(keyed)
    assert keys[0].endswith("#1") and keys[2].endswith("#2")
    assert keys[0].split("#")[0] == keys[2].split("#")[0]
    order = cells.line_order(keys)
    assert cells.in_file_order(list(reversed(keys)), order) == keys


def test_a_line_order_that_is_not_a_permutation_is_refused():
    with pytest.raises(cells.CellError):
        cells.in_file_order(["a#1", "b#1"], "0,0")


# ------------------------------------------------------------------ plans


def copy(day: str) -> sources.Copy:
    return sources.Copy(date.fromisoformat(day), "f" * 64, Path("x.csv"), "csv", {})


def test_first_plan_opens_the_register_and_later_plans_change_only_what_changed():
    first = importer.plan(None, {}, copy("2020-01-01"), [row(), row(name="Beta")])
    assert [a["transformation"] for a in first.acts] == [
        "open_register",
        "add_row",
        "add_row",
        "close_import",
    ]
    second = importer.plan(
        ("tec-2020-01-01", date(2020, 1, 1)),
        first.state,
        copy("2020-02-01"),
        [row(name="Beta"), row(eff="2026-01-01")],
    )
    kinds = [a["transformation"] for a in second.acts]
    assert kinds == ["publish", "drop_row", "add_row", "close_import"]
    assert (second.added, second.dropped, second.rows) == (1, 1, 2)
    assert second.acts[0]["args_named"]["prior_on"] == "2020-01-01"


def test_a_reordered_publication_changes_no_row_only_the_line_order():
    first = importer.plan(None, {}, copy("2020-01-01"), [row(), row(name="Beta")])
    second = importer.plan(
        ("tec-2020-01-01", date(2020, 1, 1)),
        first.state,
        copy("2020-02-01"),
        [row(name="Beta"), row()],
    )
    assert [a["transformation"] for a in second.acts] == ["publish", "close_import"]
    assert second.acts[-1]["args_named"]["order"] != first.acts[-1]["args_named"]["order"]


# ----------------------------------------------------------------- marker


class FakeRequestError(Exception):
    def __init__(self, code):
        self.code, self.error = code, "boom"


def test_marker_classification_trusts_only_positive_non_commits(monkeypatch):
    import morpholog_client.adapter as adapter

    monkeypatch.setattr(adapter, "MorphologRequestError", FakeRequestError)
    assert importer.classify(None, FakeRequestError("not_committed")).status == "not-committed"
    assert importer.classify(None, FakeRequestError("commit_outcome_unknown")).status == "unknown"
    assert importer.classify(None, FakeRequestError("a_code_from_the_future")).status == "unknown"
    assert importer.classify(None, adapter.MorphologError("killed")).status == "unknown"
    assert importer.classify(object(), None).status == "unknown"


def test_markers_are_per_database(tmp_path):
    live = importer.marker_path(tmp_path, "postgres:///grid_mysteries_tec")
    test = importer.marker_path(tmp_path, "postgres:///grid_mysteries_tec_test")
    other_host = importer.marker_path(tmp_path, "postgres://u:p@elsewhere/grid_mysteries_tec")
    assert len({live, test, other_host}) == 3


# ----------------------------------------------------------------- replay


def tagged(*values):
    return [{"type": "subject", "value": v} for v in values]


def audit_rows_for(plans: list[importer.Plan]) -> list[dict]:
    """Audit rows as the runtime would write them for these plans."""
    out, n = [], 0
    for p in plans:
        for a in p.acts:
            n += 1
            args = a["args_named"]
            asserted, retracted = [], []
            t = a["transformation"]
            if t in ("open_register", "publish"):
                asserted.append(
                    {
                        "predicate": "Vintage",
                        "args": tagged(
                            args["vintage"],
                            args["published_on"],
                            args["sha256"],
                            args["file_format"],
                            args["columns"],
                        ),
                    }
                )
            elif t == "add_row":
                asserted += [
                    {
                        "predicate": "Row",
                        "args": tagged(args["row"], *(args[f] for f in cells.FIELDS)),
                    },
                    {"predicate": "RowKinds", "args": tagged(args["row"], args["kinds"])},
                ]
            elif t == "drop_row":
                retracted += [
                    {"predicate": "Row", "args": tagged(args["row"])},
                    {"predicate": "RowKinds", "args": tagged(args["row"])},
                ]
            elif t == "rekind":
                retracted.append({"predicate": "RowKinds", "args": tagged(args["row"])})
                asserted.append(
                    {"predicate": "RowKinds", "args": tagged(args["row"], args["kinds"])}
                )
            elif t == "close_import":
                asserted += [
                    {"predicate": "Imported", "args": tagged(args["vintage"])},
                    {"predicate": "RowOrder", "args": tagged(args["vintage"], args["order"])},
                ]
            out.append(
                {
                    "transition_id": f"t{n}",
                    "asserted_claims": asserted,
                    "retracted_claims": retracted,
                }
            )
    return out


def test_replay_gives_back_each_publication_rows_and_line_order():
    a = [row(mw=100), row(name="Beta", mw=20.0), row(mw=100)]
    b = [row(name="Beta", mw=20.0), row(mw=100, eff="2026-06-01")]
    p1 = importer.plan(None, {}, copy("2020-01-01"), a)
    p2 = importer.plan(("tec-2020-01-01", date(2020, 1, 1)), p1.state, copy("2020-02-01"), b)
    pubs = list(replay.fold(audit_rows_for([p1, p2])))
    assert [p.vintage for p in pubs] == ["tec-2020-01-01", "tec-2020-02-01"]
    for pub, rows in zip(pubs, (a, b), strict=True):
        assert [{k: r.get(k) for k in cells.COLUMNS} for r in pub.rows] == [
            {k: r.get(k) for k in cells.COLUMNS} for r in rows
        ]
    assert pubs[1].close_transition == f"t{len(p1.acts) + len(p2.acts)}"


# --------------------------------------------------------------- identity


def test_content_identity_ignores_row_order_where_014_ordinals_would_move():
    # Two rows of one group, same date and cumulative MW, different stage MW.
    first = [row(mw=10, eff="2025-01-01"), row(mw=20, eff="2026-01-01")]
    reordered = list(reversed(first))
    carrier = identity.ContentIdentity()
    a = carrier.step(first)
    b = carrier.step(reordered)
    assert {k: (e.mw, e.effective) for k, e in a.items()} == {
        k: (e.mw, e.effective) for k, e in b.items()
    }


def test_content_identity_follows_the_row_whose_date_moved():
    carrier = identity.ContentIdentity()
    a = carrier.step([row(mw=10, eff="2025-01-01"), row(mw=20, eff="2025-06-01")])
    # The 10 MW stage moves past the 20 MW one: 014's ordinals would swap.
    b = carrier.step([row(mw=10, eff="2027-01-01"), row(mw=20, eff="2025-06-01")])
    moved = [k for k in b if a[k].effective != b[k].effective]
    assert len(moved) == 1 and b[moved[0]].mw == 10
    by_014_a = cs.entries([row(mw=10, eff="2025-01-01"), row(mw=20, eff="2025-06-01")])
    by_014_b = cs.entries([row(mw=10, eff="2027-01-01"), row(mw=20, eff="2025-06-01")])
    assert sum(1 for k in by_014_b if by_014_a[k].effective != by_014_b[k].effective) == 2


def test_best_assignment_is_exact():
    matrix = [[(0, 0, 1, 0, 5), (0, 0, 0, 0, 0)], [(0, 0, 0, 0, 0), (0, 1, 0, 0, 0)]]
    assert identity.best_assignment(matrix) == [1, 0]


def test_each_regime_segment_numbers_its_own_units():
    old = cs.VintageInput(date(2025, 7, 1), (row(),), "a", "")
    new = cs.VintageInput(date(2026, 5, 19), (row(),), "b", "")
    seq = [analysis.Kept("old", old, False), analysis.Kept("new", new, False)]
    units = [set(e) for _, e in analysis.entries_content(seq)]
    assert units[0] == units[1]  # same name, but each segment numbers its own units


# --------------------------------------------------------------- flapping


def entry(key, group, eff, mw=Decimal(10)):
    return cs.Entry(key, group, "", mw, date.fromisoformat(eff), eff)


def test_a_reversal_the_files_do_not_show_is_counted_as_not_in_the_files():
    # One group of two rows whose printed dates never change; the keys swap.
    d = [date(2020, 1, 1), date(2020, 2, 1), date(2020, 3, 1)]
    seq = [
        (d[0], {"g#1": entry("g#1", "g", "2025-01-01"), "g#2": entry("g#2", "g", "2026-01-01")}),
        (d[1], {"g#1": entry("g#1", "g", "2026-01-01"), "g#2": entry("g#2", "g", "2025-01-01")}),
        (d[2], {"g#1": entry("g#1", "g", "2025-01-01"), "g#2": entry("g#2", "g", "2026-01-01")}),
    ]
    f = analysis.flapping([seq], "test")
    assert f["reversed_by_next"] == 2 and f["reversed_not_in_files_on_repeated_keys"] == 2


def test_a_reversal_the_files_really_print_is_file_backed():
    d = [date(2020, 1, 1), date(2020, 2, 1), date(2020, 3, 1)]
    seq = [
        (d[0], {"g#1": entry("g#1", "g", "2025-01-01")}),
        (d[1], {"g#1": entry("g#1", "g", "2026-01-01")}),
        (d[2], {"g#1": entry("g#1", "g", "2025-01-01")}),
    ]
    f = analysis.flapping([seq], "test")
    assert (f["reversed_by_next"], f["reversed_file_backed"]) == (1, 1)


# ------------------------------------------------------------ certificate


def test_certificate_matches_by_normalised_name_and_stage():
    assert certificate.matches(row(name="East  Anglia-ONE", Stage="1.0"), "east anglia one", "1")
    assert not certificate.matches(row(name="East Anglia One", Stage="2"), "east anglia one", "1")


def test_certificate_changes_list_publications_where_lines_changed():
    a, b = [row()], [row(eff="2026-01-01")]
    p1 = importer.plan(None, {}, copy("2020-01-01"), a)
    p2 = importer.plan(("tec-2020-01-01", date(2020, 1, 1)), p1.state, copy("2020-02-01"), b)
    p3 = importer.plan(("tec-2020-02-01", date(2020, 2, 1)), p2.state, copy("2020-03-01"), b)
    pubs = list(replay.fold(audit_rows_for([p1, p2, p3])))
    out = certificate.record(pubs, "alpha", None, [date(2020, 1, 15), date(2020, 3, 15)], {})
    assert [c["published_on"] for c in out["changes"]] == [date(2020, 2, 1)]
    assert out["as_of"][1]["lines"][0]["cells"]["MW Effective From"] == "2026-01-01"


# ------------------------------------------------------ gaps and strandings


def held_copy(day: str, sha: str) -> sources.Copy:
    return sources.Copy(date.fromisoformat(day), sha, Path("x.csv"), "csv", {})


def test_a_readable_copy_behind_the_record_is_stranded_and_an_unreadable_one_is_not():
    held = [
        held_copy("2025-07-22", "a"),
        held_copy("2025-10-01", "b"),
        held_copy("2025-11-01", "c"),
    ]
    out = importer.stranded(held, {"a"}, date(2026, 5, 19), lambda c: c.sha256 != "c")
    assert [c.sha256 for c in out] == ["b"]
    assert importer.stranded(held, {"a"}, date(2025, 7, 22), lambda c: True) == []


def test_a_certificate_states_the_gap_and_copies_held_but_not_in_the_record():
    p1 = importer.plan(None, {}, copy("2025-07-22"), [row()])
    pubs = list(replay.fold(audit_rows_for([p1])))
    out = certificate.record(
        pubs,
        "alpha",
        None,
        [date(2025, 8, 1), date(2026, 1, 1)],
        {},
        [(date(2025, 10, 1), "b" * 64)],
    )
    near, far = out["as_of"]
    assert (near["days_before"], near["gap"], near["held_but_not_in_record"]) == (10, False, [])
    assert far["gap"] is True
    assert far["held_but_not_in_record"] == [
        {"published_on": date(2025, 10, 1), "sha256": "b" * 64}
    ]


def test_the_bundled_script_checks_each_date_even_when_two_share_a_publication(tmp_path):
    import json
    import subprocess
    import sys

    p1 = importer.plan(None, {}, copy("2025-07-22"), [row(), row(mw=5, eff="2027-01-01")])
    pack = {"rows": audit_rows_for([p1])}
    pubs = list(replay.fold(pack["rows"]))
    cert = certificate.record(pubs, "alpha", None, [date(2025, 8, 1), date(2026, 1, 1)], {})
    (tmp_path / "pack.json").write_text(json.dumps(pack))
    (tmp_path / "certificate.json").write_text(json.dumps(cert, default=str))
    (tmp_path / "lines_from_pack.py").write_text(certificate.LINES_FROM_PACK)
    run = subprocess.run(
        [sys.executable, "lines_from_pack.py", "pack.json", "certificate.json"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout
    assert run.stdout.count("2 line(s) in the pack, as the certificate states") == 2


def test_pack_rows_and_the_bundled_script_read_the_ndjson_pack_form(tmp_path):
    """Morpholog v0.0.12 exports a prefix pack as NDJSON (format 4): a
    manifest line, `checkpoint_count` checkpoint lines, then one audit row
    per line. Both readers must give the same rows as the earlier
    single-document form, and the manifest's row count is checked."""
    import json
    import subprocess
    import sys

    p1 = importer.plan(None, {}, copy("2025-07-22"), [row(), row(mw=5, eff="2027-01-01")])
    rows = audit_rows_for([p1])
    manifest = {
        "pack_format_version": 4,
        "pack_kind": "prefix",
        "tree_size": len(rows),
        "root_hash": "sha256:" + "0" * 64,
        "checkpoint_hash": "sha256:" + "1" * 64,
        "checkpoint_count": 2,
    }
    checkpoints = [{"tree_size": 1, "root_hash": "x"}, {"tree_size": len(rows), "root_hash": "y"}]
    ndjson = "".join(json.dumps(x) + "\n" for x in [manifest, *checkpoints, *rows])
    (tmp_path / "pack.ndjson").write_text(ndjson)
    (tmp_path / "pack.json").write_text(json.dumps({"rows": rows}))

    assert replay.pack_rows(tmp_path / "pack.ndjson") == rows
    assert replay.pack_rows(tmp_path / "pack.json") == rows

    short = dict(manifest, tree_size=len(rows) + 1)
    (tmp_path / "short.ndjson").write_text(
        "".join(json.dumps(x) + "\n" for x in [short, *checkpoints, *rows])
    )
    with pytest.raises(replay.ReplayError):
        replay.pack_rows(tmp_path / "short.ndjson")

    pubs = list(replay.fold(rows))
    cert = certificate.record(pubs, "alpha", None, [date(2025, 8, 1), date(2026, 1, 1)], {})
    (tmp_path / "certificate.json").write_text(json.dumps(cert, default=str))
    (tmp_path / "lines_from_pack.py").write_text(certificate.LINES_FROM_PACK)
    outputs = []
    for pack in ("pack.ndjson", "pack.json"):
        run = subprocess.run(
            [sys.executable, "lines_from_pack.py", pack, "certificate.json"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert run.returncode == 0, run.stdout
        outputs.append(run.stdout)
    assert outputs[0] == outputs[1]
    assert outputs[0].count("2 line(s) in the pack, as the certificate states") == 2


def test_pairing_is_undetermined_on_a_split_or_on_repeated_labels_only():
    split_before = [row(name="S", Stage=None)]
    split_after = [row(name="S", Stage="1"), row(name="S", Stage="2")]
    repeated = [row(name="R", mw=1), row(name="R", mw=2)]
    distinct = [row(name="D", Stage="1"), row(name="D", Stage="2", mw=5)]
    single = [row(name="O")]
    before = split_before + repeated + distinct + single
    after = split_after + repeated + distinct + single
    found = analysis.undetermined(before, after)
    assert {g.split("|")[0] for g in found} == {"name:s", "name:r"}
