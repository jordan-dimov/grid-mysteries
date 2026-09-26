import re
from html import escape
from typing import Any

from grid_mysteries.rendering import balancing_bill as bb

ROW = {
    "settlement_date": "2026-09-08",
    "seed": False,
    "available": True,
    "record": False,
    "paid_out_gbp": "33610462.712976159288981078",
    "net_gbp": "31561031.82",
    "wind_bid_gbp": "3768601.305298115938623229",
    "wind_bid_share": "0.1121",
    "gas_offer_gbp": "26820639.172920768961194702",
    "gas_offer_share": "0.7980",
    "other_gbp": "3021222.234757274389163147",
    "other_share": "0.0899",
    "two_cut_gbp": "30589240.48",
    "disptav_type": "Tagged",
    "gas_offer_vwap_gbp_per_mwh": "229.53",
    "premium_gbp_per_mwh": "82.64",
    "bsad_net_gbp": "3333989.85",
    "bsad_share": "0.0992",
    "bsad_placeholder_only": False,
    "outcome": None,
}


def tracker(rows, **extra):
    return {
        "declaration_sha256": "d20d59203e7b7fda174c2c6deb2807159687bd9ddea39fe760961af884416473",
        "computed_at": "2026-09-11T20:00:00+00:00",
        "run_date": "2026-09-11",
        "rows": rows,
        **extra,
    }


def test_fixture_row_renders_to_the_expected_cells():
    assert bb.row_cells(ROW, "2026-09-11") == [
        "8 Sep 2026",
        "£33.61m",
        "£3.77m (11.2%)",
        "£26.82m (79.8%)",
        "£3.02m (9.0%)",
        "£229.53",
        "£82.64",
        "£3.33m (9.9%)",
        "not yet published (as of 11 Sep 2026)",
        "—",
    ]


def test_blank_neso_column_says_not_yet_published_as_of_the_run_date():
    cells = bb.row_cells(ROW, "2026-10-02")
    assert cells[8] == "not yet published (as of 2 Oct 2026)"
    assert cells[9] == "—"
    published = dict(
        ROW,
        outcome={
            "vintage": "2026-10-02",
            "l1_constraints_gbp": "40000000",
            "ratio_l1_to_two_cut": "1.3076",
        },
    )
    cells = bb.row_cells(published, "2026-10-02")
    assert cells[8] == "£40.00m (published 2 Oct 2026)"
    assert cells[9] == "1.31× the headline number"


def test_record_flag_renders_the_badge_and_seed_rows_the_dagger_and_label():
    html = bb.render_table_row(dict(ROW, record=True), "2026-09-11")
    assert '<span class="tag record">record</span>' in html
    assert 'class="record"' in html
    seed = bb.render_table_row(dict(ROW, seed=True), "2026-09-11")
    assert '<span class="tag seed"' in seed
    assert "£229.53 †" in seed
    assert "record</span>" not in seed
    plain = bb.render_table_row(ROW, "2026-09-11")
    assert "tag" not in plain


def test_unavailable_and_placeholder_rows():
    cells = bb.row_cells({"settlement_date": "2026-09-12", "available": False}, "2026-09-11")
    assert cells[:2] == ["12 Sep 2026", "no published data"] and set(cells[2:]) == {"—"}
    cells = bb.row_cells(
        dict(ROW, bsad_net_gbp=None, bsad_share=None, bsad_placeholder_only=True), "2026-09-11"
    )
    assert cells[7] == "not yet populated"
    cells = bb.row_cells(
        dict(ROW, gas_offer_vwap_gbp_per_mwh=None, premium_gbp_per_mwh=None), "2026-09-11"
    )
    assert cells[5] == "—" and cells[6] == "—"


def test_table_is_newest_first():
    rows = [dict(ROW, settlement_date=d) for d in ("2026-09-01", "2026-09-08", "2026-09-04")]
    html = bb.render_table(rows, "2026-09-11")
    assert re.findall(r'datetime="([^"]+)"', html) == ["2026-09-08", "2026-09-04", "2026-09-01"]


def test_corrections_section_renders_its_empty_state():
    assert "None so far" in bb.render_corrections(None)
    assert "None so far" in bb.render_corrections([])
    listed = bb.render_corrections([{"date": "2026-10-01", "text": "Fixed <x>"}])
    assert "<ol>" in listed and "Fixed &lt;x&gt;" in listed and "1 Oct 2026" in listed


def test_page_is_self_contained_and_a_pure_function_of_the_tracker():
    page = bb.render_page(tracker([ROW]))
    assert page == bb.render_page(tracker([ROW]))
    assert "<script" not in page and "http" not in page.split("<body>")[0].split("<style>")[
        0
    ].replace('lang="en-GB"', "")
    assert page.count("<link") == 0 and 'src="' not in page
    assert "The Balancing Bill" in page and "Who got paid to keep Britain" in page
    assert "None so far" in page
    assert "jdimov@a115.co.uk" in page and "Shell, Centrica and Limejump" in page
    assert "investigations/013-the-cover-price-tracker/DECLARATION.md" in page
    assert "d20d59203e7b7fda" in page
    for heading in bb.COLUMNS:
        assert f'<th scope="col">{escape(heading)}</th>' in page
    assert "No day has yet exceeded" in page
    assert "which is what the daily trackers add up" in page
    assert "Official figure vs the headline number" in page
    with_record = bb.render_page(
        tracker([ROW, dict(ROW, settlement_date="2026-09-09", record=True)])
    )
    assert "Record days so far: 9 Sep 2026." in with_record


PROPOSITIONS: dict[str, Any] = {
    "as_of": "2026-09-19",
    "falsifier_date": "2027-03-31",
    "record_days": [],
    "T1": {"claim": "c1", "instances": [], "holds": None},
    "T2": {
        "claim": "c2",
        "instances": [
            {"settlement_date": "2026-09-02", "seed": True, "holds": False},
            {"settlement_date": "2026-09-09", "seed": False, "holds": False},
        ],
        "deciding_instances": 1,
        "holds": False,
    },
    "T3": {"claim": "c3", "instances": [], "holds": None},
}


def test_the_t2_note_renders_only_beside_the_failure_it_describes():
    page = bb.render_page(tracker([ROW], propositions=PROPOSITIONS))
    assert "<li><strong>T2</strong> — c2: <strong>fails</strong> (2 instances, 1 deciding)." in page
    assert "<p><strong>T2 failed on 9 September 2026.</strong></p>" in page
    assert page.index("<h2>Propositions</h2>") < page.index("T2 failed on 9 September")
    assert escape(bb.T2_FAILURE_NOTE[1]) in page
    undecided = dict(PROPOSITIONS, T2=dict(PROPOSITIONS["T2"], holds=None))
    assert "T2 failed on" not in bb.render_page(tracker([ROW], propositions=undecided))
    other_day = dict(
        PROPOSITIONS,
        T2=dict(
            PROPOSITIONS["T2"],
            instances=[{"settlement_date": "2026-09-23", "seed": False, "holds": False}],
        ),
    )
    try:
        bb.render_page(tracker([ROW], propositions=other_day))
    except ValueError as exc:
        assert "2026-09-23" in str(exc)
    else:
        raise AssertionError("a note about 9 September rendered beside another failure")


def test_page_cautions_mark_cells_and_add_one_line_each():
    ambiguous = dict(
        ROW, settlement_date="2026-09-12", sign_convention_holds=False, bsad_provisional=True
    )
    cells = bb.row_cells(ambiguous, "2026-09-19")
    assert cells[2] == "£3.77m (11.2%) ‡" and cells[7] == "£3.33m (9.9%) §"
    page = bb.render_page(tracker([ambiguous]))
    assert page.count('<p class="notes">‡ Wind figure ambiguous') == 1
    assert (
        "not yet been repeated by a later file. A reading counts once the next pinned NESO "
        "vintage reproduces it unchanged (013 Amendment 1)" in page
    )
    assert "‡ Wind" not in bb.render_page(tracker([ROW])) and "§ Prov" not in bb.render_page(
        tracker([ROW])
    )


def test_page_cites_the_record_anchor_only_when_given_one():
    plain = bb.render_page(tracker([ROW]))
    assert "governed record" not in plain
    record = {
        "tree_size": 84,
        "root_hash": "sha256:7a8db97df0d566c45a635670ea3997bcd1ef4cef9bea8e6e03ca777c363e147d",
        "anchor_path": "bill/anchors/tree-84.json",
    }
    cited = bb.render_page(tracker([ROW]), record=record)
    assert "checkpoint at tree size 84, root <code>sha256:7a8db97df0d566c4…</code>" in cited
    assert (
        'href="https://github.com/jordan-dimov/grid-mysteries/blob/main/bill/anchors/tree-84.json"'
        in cited
    )
    assert cited == bb.render_page(tracker([ROW]), record=record)
