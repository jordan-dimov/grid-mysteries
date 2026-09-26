"""The Balancing Bill record: the plan is pure and a computed row never changes."""

from datetime import date

import pytest

from grid_mysteries.bill import importer


def row(day: str, paid_out: str = "1000", **extra):
    base = {
        "settlement_date": day,
        "seed": False,
        "batch": 1,
        "source": "013 batch 01",
        "available": True,
        "artefacts": [{"sha256": "a" * 64}, {"sha256": "b" * 64}],
        "paid_out_gbp": paid_out,
        "net_gbp": "900",
        "paid_in_gbp": "-100",
        "wind_bid_gbp": "100",
        "gas_offer_gbp": "700",
        "other_gbp": "200",
        "two_cut_gbp": "800",
        "sign_convention_holds": True,
        "disptav_type": "Tagged",
        "gas_offer_mwh": "10",
        "gas_offer_vwap_gbp_per_mwh": "70",
        "mid_vwap_same_periods_gbp_per_mwh": "50",
        "premium_gbp_per_mwh": "20",
        "bsad_vintage": "2026-09-15",
        "bsad_net_gbp": "50",
        "bsad_share": "0.0500",
        "bsad_revisions": [],
        "bsad_confirmed_vintage": "2026-09-15",
        "bsad_deciding_net_gbp": "50",
        "bsad_deciding_share": "0.0500",
        "outcome": None,
        "outcome_revisions": [],
        "record": False,
    }
    return dict(base, **extra)


def tracker(rows, run_date="2026-09-19", propositions=None):
    return {
        "run_date": run_date,
        "rows": rows,
        "propositions": propositions
        or {
            "T1": {"holds": None, "instances": []},
            "T2": {"holds": False, "instances": [{"seed": True}, {"seed": False}]},
            "T3": {"holds": None, "instances": []},
            "T4": {"holds": None, "n": 3, "min_days": 20, "decided": False, "rho": None},
        },
    }


def names(acts):
    return [a["transformation"] for a in acts]


def test_first_run_declares_rules_opens_adds_days_verdicts_and_closes():
    p = importer.plan(importer.State(), tracker([row("2026-09-09"), row("2026-09-10")]), "f" * 64)
    assert p.run == "run-2026-09-19-ffffffffffff"
    assert names(p.acts) == [
        "declare_rule",
        "open_first_run",
        "add_day",
        "confirm_bsad",
        "add_day",
        "confirm_bsad",
        "record_verdict",
        "record_verdict",
        "record_verdict",
        "record_verdict",
        "close_run",
    ]
    assert p.added == ["2026-09-09", "2026-09-10"] and p.confirmed == 2 and p.verdicts == 4
    day = p.acts[2]["args_named"]
    assert day["rule"] == importer.RULE and day["flag"] == "none" and day["sign"] == "holds"
    assert day["artefacts_sha256"] == importer.artefacts_digest(row("2026-09-09"))
    verdicts = {
        a["args_named"]["proposition"]: a["args_named"]
        for a in p.acts
        if a["transformation"] == "record_verdict"
    }
    assert (
        verdicts["T2"]["holds"] == "false" and verdicts["T2"]["detail"] == "2 instances, 1 deciding"
    )
    assert verdicts["T4"]["holds"] == "undecided" and verdicts["T4"]["detail"].startswith("3 of 20")


def test_seed_rows_carry_their_own_rule_and_flag():
    seed = row("2026-09-08", seed=True, source="seed (012)", batch=0)
    p = importer.plan(importer.State(), tracker([seed]), "f" * 64)
    declared = [a["args_named"]["rule"] for a in p.acts if a["transformation"] == "declare_rule"]
    assert declared == ["seed-012"]
    day = next(a["args_named"] for a in p.acts if a["transformation"] == "add_day")
    assert day["rule"] == "seed-012" and day["flag"] == "seed" and day["batch"] == "0"


def held_after(p: importer.Plan) -> importer.State:
    """The state the record would hold after this plan committed."""
    s = importer.State(rules=set(importer.RULES), current=(p.run, p.run_date), runs={p.run})
    for a in p.acts:
        args = a["args_named"]
        if a["transformation"] == "add_day":
            s.rows[(args["day"], args["rule"])] = tuple(args[f] for f in importer.DAY_FIELDS)
        elif a["transformation"] == "append_outcome":
            s.outcomes.add(args["day"])
        elif a["transformation"] == "revise_outcome":
            s.outcome_revisions.add((args["day"], args["vintage"]))
        elif a["transformation"] == "revise_bsad":
            s.bsad_revisions.add((args["day"], args["vintage"]))
        elif a["transformation"] == "confirm_bsad":
            s.bsad_confirmed.add(args["day"])
    return s


def test_a_later_run_adds_only_what_is_new_and_skips_identical_days():
    first = importer.plan(importer.State(), tracker([row("2026-09-09")]), "1" * 64)
    state = held_after(first)
    later = importer.plan(
        state, tracker([row("2026-09-09"), row("2026-09-10")], "2026-09-26"), "2" * 64
    )
    assert names(later.acts)[:2] == ["open_run", "add_day"]
    assert later.acts[0]["args_named"]["prior"] == first.run
    assert later.added == ["2026-09-10"] and later.unchanged == ["2026-09-09"]


def test_a_day_held_with_different_figures_is_refused_by_name_before_anything_is_proposed():
    state = held_after(importer.plan(importer.State(), tracker([row("2026-09-09")]), "1" * 64))
    with pytest.raises(importer.PlanError, match="2026-09-09 under 013-d20d5920-A1"):
        importer.plan(state, tracker([row("2026-09-09", paid_out="1001")], "2026-09-26"), "2" * 64)


def test_a_recompute_under_a_new_rule_version_is_a_second_row_not_a_replacement(monkeypatch):
    state = held_after(importer.plan(importer.State(), tracker([row("2026-09-09")]), "1" * 64))
    monkeypatch.setattr(importer, "RULE", "013-d20d5920-A2")
    monkeypatch.setitem(importer.RULES, "013-d20d5920-A2", ("d20d5920", "A2"))
    p = importer.plan(state, tracker([row("2026-09-09", paid_out="1001")], "2026-10-03"), "3" * 64)
    assert p.added == ["2026-09-09"]
    assert [a["args_named"]["rule"] for a in p.acts if a["transformation"] == "declare_rule"] == [
        "013-d20d5920-A2"
    ]


def test_outcomes_and_bsad_are_append_only_first_kept_then_revisions_then_confirmation():
    outcome = {
        "vintage": "2026-09-15",
        "l1_constraints_gbp": "500",
        "l4_constraint_offers_mwh": "5",
        "l4_constraint_bids_mwh": "1",
        "ratio_l1_to_two_cut": "0.6250",
    }
    revision = dict(
        outcome, vintage="2026-09-26", l4_constraint_offers_mwh=None, l4_constraint_bids_mwh=None
    )
    r = row(
        "2026-09-09",
        outcome=outcome,
        outcome_revisions=[revision],
        bsad_revisions=[{"vintage": "2026-09-17", "bsad_net_gbp": "60", "bsad_share": "0.0600"}],
        bsad_confirmed_vintage="2026-09-17",
        bsad_deciding_net_gbp="60",
        bsad_deciding_share="0.0600",
    )
    p = importer.plan(importer.State(), tracker([r]), "1" * 64)
    assert names(p.acts)[2:7] == [
        "add_day",
        "append_outcome",
        "revise_outcome",
        "revise_bsad",
        "confirm_bsad",
    ]
    assert p.acts[4]["args_named"]["l4_offers_mwh"] == "-"
    assert p.acts[6]["args_named"] == {
        "run": p.run,
        "day": "2026-09-09",
        "vintage": "2026-09-17",
        "bsad_net_gbp": "60",
        "bsad_share": "0.0600",
    }
    # the same file offered again: nothing but the run and the verdicts
    again = importer.plan(held_after(p), tracker([r], "2026-09-26"), "2" * 64)
    assert names(again.acts) == ["open_run"] + ["record_verdict"] * 4 + ["close_run"]


def test_runs_go_in_date_order_and_never_twice():
    p = importer.plan(importer.State(), tracker([row("2026-09-09")], "2026-09-26"), "1" * 64)
    state = held_after(p)
    with pytest.raises(importer.PlanError, match="before the record's current run"):
        importer.plan(state, tracker([row("2026-09-09")], "2026-09-19"), "2" * 64)
    with pytest.raises(importer.PlanError, match="already in the record"):
        importer.plan(state, tracker([row("2026-09-09")], "2026-09-26"), "1" * 64)
    assert p.run_date == date(2026, 9, 26)


def test_unavailable_days_are_not_recorded():
    p = importer.plan(
        importer.State(),
        tracker([row("2026-09-09", available=False, status="not pinned")]),
        "1" * 64,
    )
    assert "add_day" not in names(p.acts) and p.added == []


class FakeRequestError(Exception):
    def __init__(self, code):
        self.code, self.error = code, "boom"


def test_marker_classification_trusts_only_positive_non_commits(monkeypatch):
    import morpholog_client.adapter as adapter

    monkeypatch.setattr(adapter, "MorphologRequestError", FakeRequestError)
    assert importer.classify(None, FakeRequestError("not_committed")).status == "not-committed"
    assert importer.classify(None, FakeRequestError("commit_outcome_unknown")).status == "unknown"
    assert importer.classify(None, adapter.MorphologError("killed")).status == "unknown"
    assert importer.classify(object(), None).status == "unknown"


def test_markers_are_per_database(tmp_path):
    a = importer.marker_path(tmp_path, "postgres:///grid_mysteries_bill")
    b = importer.marker_path(tmp_path, "postgres:///grid_mysteries_bill_test")
    assert a != b and a.parent == b.parent
