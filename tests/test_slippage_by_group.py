"""Investigation 021: 014's series cut by plant type and host TO."""

from datetime import date

from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import slippage_by_group as sbg


def row(name, stage, mw, eff, plant="Wind Onshore", host="NGET", customer="C", site="S"):
    return {
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "MW Effective From": date.fromisoformat(eff) if eff else None,
        "Plant Type": plant,
        "HOST TO": host,
    }


# ----------------------------------------------------------- schema pass


def test_unit_keys_align_row_by_row_with_entries():
    rows = [
        row("A", "1", 10, "2025-01-01"),
        row("A", "2", 20, "2026-01-01"),
        row("B", "", 5, "2025-06-01"),
        row("C", "", 5, "2025-06-01"),
        row("C", "", 7, "2025-07-01"),  # two rows, no distinct stage: numbered by date
    ]
    keys = cs.unit_keys(rows)
    assert len(keys) == len(rows)
    assert set(keys) == set(cs.entries(rows))
    assert keys[2].endswith("#1") and keys[3].endswith("#1") and keys[4].endswith("#2")


def test_tags_read_the_grouping_keys_as_printed_with_whitespace_collapsed():
    rows = [row("A", "1", 10, "2025-01-01", plant=" Energy  Storage System ", host=None)]
    tagged = sbg.tags(rows)
    (value,) = tagged.values()
    assert value == {"plant_type": "Energy Storage System", "host_to": ""}


def test_key_stability_counts_changes_of_a_unit_between_consecutive_copies():
    first = [row("A", "1", 10, "2025-01-01", plant="Wind Onshore", host="SPT")]
    second = [
        row("A", "1", 10, "2025-01-01", plant="Wind Onshore;Energy Storage System", host="SPT")
    ]
    third = [
        row("A", "1", 10, "2025-01-01", plant="Wind Onshore;Energy Storage System", host="SPT")
    ]
    out = sbg.key_stability(
        [(date(2024, 1, 1), first), (date(2024, 2, 1), second), (date(2024, 3, 1), third)]
    )
    assert out["matched_units_over_consecutive_copies"] == 2
    assert out["plant_type"]["units_changed"] == 1
    assert out["plant_type"]["transitions"] == [
        {"from": "Wind Onshore", "to": "Wind Onshore;Energy Storage System", "units": 1}
    ]
    assert out["host_to"]["units_changed"] == 0
    assert [c["t_public"] for c in out["copies_with_a_change"]] == ["2024-02-01"]


# ---------------------------------------------------------------- the cut

from decimal import Decimal  # noqa: E402

import pytest  # noqa: E402

from grid_mysteries.investigations import connection_slippage_v3 as v3  # noqa: E402
from grid_mysteries.rendering import slippage_by_group as page  # noqa: E402
from grid_mysteries.tec import identity as content_rule  # noqa: E402

D = Decimal


def copies(*rows_per_copy):
    """v2 entries, v2 keys, content entries and content keys for consecutive copies."""
    carrier = content_rule.ContentIdentity()
    out = []
    for rows in rows_per_copy:
        c_entries = carrier.step(rows)
        out.append(
            (
                cs.entries(rows),
                sbg.keys_from_rows(rows),
                c_entries,
                sbg.keys_from_units(carrier.units),
            )
        )
    return out


def cut_of(*ends, dimension="plant_type", undetermined=frozenset(), figures=None):
    (vb, kb, cb, ckb), (vc, kc, cc, ckc) = ends
    pair = cs.compare(vb, vc, baseline_date=date(2024, 1, 1), current_date=date(2025, 1, 1))
    split = v3.split(
        (vb, vc), (cb, cc), set(undetermined), baseline=date(2024, 1, 1), current=date(2025, 1, 1)
    )
    figures = figures or {
        "mw_years_net": pair.mw_years_net,
        "determined": split["determined"],
        "weighted_mw": pair.weighted_mw,
    }
    return sbg.cut(
        dimension=dimension,
        v2=(vb, vc),
        content=(cb, cc),
        keys_v2=(kb, kc),
        keys_content=(ckb, ckc),
        undetermined=set(undetermined),
        comparison=figures,
    )


def by_name(result, name):
    return next(g for g in result["groups"] if g["group"] == name)


# R1


def test_r1_whitespace_and_separator_are_one_spelling_and_compounds_are_kept_whole():
    a = sbg.read_key("plant_type", "Energy Storage System; PV Array (Photo Voltaic/solar)")
    b = sbg.read_key("plant_type", "Energy  Storage System;PV Array (Photo Voltaic/solar) ")
    assert a == b == ("Energy Storage System;PV Array (Photo Voltaic/solar)",) * 2
    assert sbg.group_name(a[1]).count(";") == 1  # one group, never split


def test_r1_the_spelling_table_unifies_expansions_per_component_and_nothing_else():
    printed, unified = sbg.read_key("plant_type", "CCGT; Battery Storage")
    assert printed == "CCGT;Battery Storage"
    assert unified == "CCGT (Combined Cycle Gas Turbine);Battery Storage"
    assert sbg.read_key("plant_type", "Battery Storage")[1] == "Battery Storage"
    assert sbg.read_key("plant_type", "Hybrid")[1] == "Hybrid"
    assert sbg.read_key("plant_type", "HYBRID")[1] == "Hybrid"
    assert sbg.read_key("host_to", "SHE")[1] == "SHET"
    assert sbg.read_key("host_to", "OFFSHORE")[1] == "OFTO"
    assert sbg.read_key("host_to", "NGET") == ("NGET", "NGET")


# R2, R3


def test_r2_a_unit_whose_key_changes_is_a_bucket_never_reassigned_and_unified_ones_are_counted():
    b = [
        row("A", "1", 100, "2025-01-01", plant="Wind Onshore"),
        row("B", "1", 100, "2025-01-01", plant="CCGT"),
    ]
    c = [
        row("A", "1", 100, "2026-01-01", plant="Wind Offshore"),  # a real change
        row("B", "1", 100, "2026-01-01", plant="CCGT (Combined Cycle Gas Turbine)"),  # spelling
    ]
    result = cut_of(*copies(b, c))
    names = {g["group"] for g in result["groups"]}
    assert sbg.KEY_CHANGED in names and "Wind Offshore" not in names
    # The baseline group keeps its baseline count and no matched unit: it is
    # listed, with nothing to move, and is thin under R7.
    left = by_name(result, "Wind Onshore")
    assert (left["units_baseline"], left["matched"], left["dated_both"]) == (1, 0, 0)
    assert left["thin"] is True
    changed = by_name(result, sbg.KEY_CHANGED)
    assert changed["dated_both"] == 1 and changed["capacity_baseline_mw"] == D("100.00")
    assert result["key_changed"]["units"] == 1
    assert by_name(result, "CCGT (Combined Cycle Gas Turbine)")["dated_both"] == 1
    assert result["unified_by_spelling_table"] == 1
    assert changed["thin"] is None  # R7 is not applied to the bucket


def test_r3_a_blank_key_is_the_blank_group():
    b = [row("A", "1", 100, "2025-01-01", host=None)]
    c = [row("A", "1", 100, "2026-01-01", host="")]
    result = cut_of(*copies(b, c), dimension="host_to")
    assert [g["group"] for g in result["groups"]] == [sbg.BLANK_GROUP]
    assert by_name(result, sbg.BLANK_GROUP)["bucket"] is True


# R5, R6, C4


def test_r5_group_figures_shares_and_concentration_sum_over_every_bucket():
    b = [
        row("A", "1", 300, "2025-01-01", host="NGET"),
        row("B", "1", 100, "2025-01-01", host="SPT"),
        row("C", "1", 100, "2025-01-01", host="SPT"),  # will change key
    ]
    c = [
        row("A", "1", 300, "2026-01-01", host="NGET"),  # +300 MW-years
        row("B", "1", 100, "2025-01-01", host="SPT"),  # unchanged
        row("C", "1", 100, "2026-01-01", host="SHET"),  # key changed, +100
    ]
    result = cut_of(*copies(b, c), dimension="host_to")
    nget, spt, changed = (by_name(result, n) for n in ("NGET", "SPT", sbg.KEY_CHANGED))
    # 300 MW moved 365 days: 300 x 365/365.25 = 299.795 MW-years.
    assert nget["total"][sbg.RULE_V2] == D("299.795") == nget["determined"]
    assert nget["undetermined"] == {r: D("0.000") for r in sbg.RULES}
    assert nget["later"] == 1 and spt["unchanged"] == 1
    assert nget["share_of_capacity_percent"] == D("60.0")
    assert nget["share_of_net_percent"] == D("75.0")
    assert nget["concentration_points"] == D("15.0")
    assert changed["share_of_net_percent"] == D("25.0")
    total_share = sum(g["share_of_net_percent"] for g in result["groups"])
    assert total_share == D("100.0")
    assert result["sums"]["dated_both"] == 3
    assert result["sums"]["capacity_baseline_mw"] == D("500.00")
    assert result["sums"]["within_rounding"]
    assert abs(result["rounding_residual"]) <= D("0.001") * len(result["groups"])
    assert result["groups"][0]["group"] == "NGET"  # named groups first, by capacity


def test_r6_each_groups_gross_sides_are_quantised_and_the_residual_is_reported():
    # 10 MW moved 1 day: 10/365.25 = 0.027378... MW-years, quantised per group.
    b = [row("A", "1", 10, "2025-01-01", host="NGET"), row("B", "1", 10, "2025-01-01", host="SPT")]
    c = [row("A", "1", 10, "2025-01-02", host="NGET"), row("B", "1", 10, "2025-01-02", host="SPT")]
    result = cut_of(*copies(b, c), dimension="host_to")
    assert by_name(result, "NGET")["mw_years_later"] == D("0.027")
    assert abs(result["rounding_residual"]) <= D("0.001") * 2


# R7


def test_r7_a_group_whose_matched_units_are_under_half_its_baseline_units_is_thin():
    b = [row(f"P{i}", "1", 10, "2025-01-01", host="SHET") for i in range(5)]
    c = [
        row("P0", "1", 10, "2026-01-01", host="SHET"),
        row("P1", "1", 10, "2026-01-01", host="SHET"),
    ]
    result = cut_of(*copies(b, c), dimension="host_to")
    g = by_name(result, "SHET")
    assert g["units_baseline"] == 5 and g["matched"] == 2 and g["thin"] is True
    assert result["thin_groups"] == ["SHET"]


# R8


def test_r8_storage_alone_excludes_compounds_and_including_counts_them():
    b = [
        row("A", "1", 100, "2025-01-01", plant="Energy Storage System"),
        row(
            "B",
            "1",
            100,
            "2025-01-01",
            plant="Energy Storage System;PV Array (Photo Voltaic/solar)",
        ),
        row("C", "1", 100, "2025-01-01", plant="Pump Storage"),
        row("D", "1", 100, "2025-01-01", plant="Battery Storage"),
    ]
    c = [dict(r, **{"MW Effective From": date(2026, 1, 1)}) for r in b]
    result = cut_of(*copies(b, c))
    alone, including = result["storage"]["alone"], result["storage"]["including"]
    assert alone["groups"] == ["Battery Storage", "Energy Storage System"]
    assert including["groups"] == [
        "Battery Storage",
        "Energy Storage System",
        "Energy Storage System;PV Array (Photo Voltaic/solar)",
    ]
    assert alone["share_of_capacity_percent"] == D("50.0")
    assert including["share_of_capacity_percent"] == D("75.0")
    assert not sbg.is_storage("Pump Storage", including_compounds=True)
    assert not sbg.is_storage(sbg.KEY_CHANGED, including_compounds=True)


# R9, F-G4


def test_r9_shares_of_a_small_net_are_marked_not_read():
    b = [row("A", "1", 10, "2025-01-01")]
    c = [row("A", "1", 10, "2025-01-02")]
    assert cut_of(*copies(b, c))["not_read"] is True
    b2 = [row("A", "1", 100000, "2025-01-01")]
    c2 = [row("A", "1", 100000, "2026-01-01")]
    assert cut_of(*copies(b2, c2))["not_read"] is False


def test_fg4_a_key_changed_bucket_above_a_fifth_of_dated_capacity_is_unfit():
    b = [row("A", "1", 30, "2025-01-01", plant="HYBRID"), row("B", "1", 70, "2025-01-01")]
    c = [
        row("A", "1", 30, "2026-01-01", plant="Energy Storage System"),
        row("B", "1", 70, "2026-01-01"),
    ]
    assert cut_of(*copies(b, c))["unfit"] is True
    b2 = [row("A", "1", 10, "2025-01-01", plant="HYBRID"), row("B", "1", 90, "2025-01-01")]
    c2 = [
        row("A", "1", 10, "2026-01-01", plant="Energy Storage System"),
        row("B", "1", 90, "2026-01-01"),
    ]
    assert cut_of(*copies(b2, c2))["unfit"] is False


# C3 / F-G2: the determined part must not depend on the rule


def test_c3_the_determined_part_of_a_group_is_the_same_under_both_rules():
    b = [row("A", "1", 10, "2025-01-01"), row("A", "2", 20, "2026-01-01")]
    c = [row("A", "1", 10, "2025-06-01"), row("A", "2", 20, "2026-01-01")]
    result = cut_of(*copies(b, c))
    g = by_name(result, "Wind Onshore")
    assert g["determined"] == g["total"][sbg.RULE_V2] == g["total"][v3.RULE_CONTENT]


def test_fg2_a_planted_disagreement_on_a_determined_group_refuses():
    b = [row("A", "1", 10, "2025-01-01"), row("A", "2", 20, "2026-01-01")]
    c = [row("A", "1", 10, "2025-06-01"), row("A", "2", 20, "2026-01-01")]
    (vb, kb, cb, ckb), (vc, kc, cc, ckc) = copies(b, c)
    # The content rule's current copy with the two stages' dates exchanged: a
    # different pairing of a group the labels determine.
    u1, u2 = sorted(cc)
    swapped = {
        u1: cs.Entry(u1, cc[u1].identity, cc[u1].stage, cc[u1].mw, cc[u2].effective, ""),
        u2: cs.Entry(u2, cc[u2].identity, cc[u2].stage, cc[u2].mw, cc[u1].effective, ""),
    }
    with pytest.raises(sbg.RuleDisagreement, match="F-G2"):
        sbg.cut(
            dimension="plant_type",
            v2=(vb, vc),
            content=(cb, swapped),
            keys_v2=(kb, kc),
            keys_content=(ckb, ckc),
            undetermined=set(),
            comparison={"mw_years_net": D(1), "determined": D(1), "weighted_mw": D(1)},
        )


def test_an_undetermined_groups_movement_is_in_the_undetermined_part_under_each_rule():
    b = [row("A", "1", 100, "2025-01-01"), row("B", "1", 100, "2025-01-01")]
    c = [row("A", "1", 100, "2026-01-01"), row("B", "1", 100, "2026-01-01")]
    ident = cs.identity(b[0])
    result = cut_of(*copies(b, c), undetermined={ident})
    g = by_name(result, "Wind Onshore")
    # Each unit moves 99.9315... MW-years; the determined side quantises to
    # 99.932, the whole to 199.863, and the undetermined part is their
    # difference (R6), so the two always add up to the printed total.
    assert g["determined"] == D("99.932")
    assert g["total"][sbg.RULE_V2] == D("199.863")
    assert g["undetermined"][sbg.RULE_V2] == D("99.931")


# F-G3


def test_fg3_a_committed_line_that_would_change_is_named_and_new_lines_are_not():
    committed = {"k1": "a", "k2": "b"}
    assert sbg.require_unchanged(committed, {"k1": "a", "k2": "changed", "k3": "new"}) == ["k2"]
    assert sbg.require_unchanged(committed, {"k1": "a", "k3": "new"}) == []


# Propositions


def host_cut(groups, *, not_read=False):
    return {"not_read": not_read, "groups": groups}


def host(name, net, det, cap, dated=40, thin=False, bucket=False):
    return {
        "group": name,
        "bucket": bucket,
        "share_of_net_percent": net,
        "share_of_determined_percent": det,
        "share_of_capacity_percent": cap,
        "dated_both": dated,
        "total": {sbg.RULE_V2: D(net), v3.RULE_CONTENT: D(net)},
        "determined": D(det),
        "thin": thin,
    }


def plant_cut(points, groups=("Energy Storage System",), *, not_read=False):
    g = [host(n, D("10.0"), D("10.0"), D("10.0")) for n in groups]
    return {
        "not_read": not_read,
        "groups": g,
        "storage": {
            "including": {"groups": list(groups), "concentration_points": points},
            "alone": {"groups": list(groups), "concentration_points": points},
        },
    }


def test_propositions_are_decided_by_their_instances_or_stay_undecided():
    hosts = [
        host("NGET", D("70.0"), D("70.0"), D("60.0")),
        host("SPT", D("20.0"), D("20.0"), D("25.0")),
        host("SHET", D("10.0"), D("10.0"), D("15.0"), dated=20),
        host(sbg.KEY_CHANGED, D("90.0"), D("90.0"), D("1.0"), bucket=True),  # never judged
    ]
    props = sbg.propositions(host_cut(hosts), plant_cut(D("3.0")))
    assert props["P-A"]["verdict"] == "holds" and props["P-A"]["failing"] == []
    assert props["P-B"]["verdict"] == "holds"
    assert [g["group"] for g in props["P-B"]["groups"]] == ["NGET", "SPT"]  # SHET has 20 dated
    assert props["P-C"]["verdict"] == "holds"

    failing = [
        host("NGET", D("70.0"), D("60.0"), D("40.0")),
        host("SPT", D("-5.0"), D("1.0"), D("60.0")),
    ]
    props = sbg.propositions(host_cut(failing), plant_cut(D("-16.0")))
    assert props["P-A"]["verdict"] == "fails" and props["P-A"]["failing"] == ["NGET"]
    assert props["P-A"]["failing_on_determined"] == []  # the determined reading disagrees
    assert props["P-B"]["verdict"] == "fails" and props["P-B"]["failing"] == ["SPT"]
    assert props["P-B"]["failing_on_determined"] == []
    assert props["P-C"]["verdict"] == "fails"

    props = sbg.propositions(host_cut(hosts, not_read=True), plant_cut(D("3.0"), not_read=True))
    assert {p["verdict"] for p in props.values()} == {"undecided"}
    props = sbg.propositions(
        host_cut([host("NGET", D("70.0"), D("70.0"), D("60.0"), thin=True)]), plant_cut(None)
    )
    assert props["P-A"]["verdict"] == "undecided" and props["P-C"]["verdict"] == "undecided"


# The page


def evidence_fixture():
    def comparison(window, dimension, regime="old", baseline="2024-07-19", current="2025-07-22"):
        key = f"76ad7dc3|{regime}|{window}|{baseline}|{current}|{dimension}"
        return {
            "key": key,
            "rule_version": "76ad7dc3",
            "regime": regime,
            "window": window,
            "baseline": baseline,
            "current": current,
            "dimension": dimension,
            "figures_014_v4": {
                "mw_years_net": "57823.493",
                "dated_both": 889,
                "weighted_mw": "292763.70",
                "determined": "53221.271",
                "undetermined_groups": 88,
                "total": {sbg.RULE_V2: "57823.493", v3.RULE_CONTENT: "61542.867"},
            },
            "key_changed": {
                "units": 1,
                "dated_both": 1,
                "capacity_baseline_mw": "10.00",
                "mw_years_net": "1.000",
            },
            "unified_by_spelling_table": 2,
            "rounding_residual": "0.000",
            "not_read": False,
            "unfit": False,
            "thin_groups": ["OFTO"] if dimension == "host_to" else [],
            "storage": (
                {
                    "alone": {
                        "groups": ["Energy Storage System"],
                        "dated_both": 10,
                        "capacity_baseline_mw": "100.00",
                        "mw_years_net": "10.000",
                        "determined": "9.000",
                        "share_of_net_percent": "10.0",
                        "share_of_capacity_percent": "12.0",
                        "concentration_points": "-2.0",
                    },
                    "including": {
                        "groups": [
                            "Energy Storage System",
                            "Energy Storage System;PV Array (Photo Voltaic/solar)",
                        ],
                        "dated_both": 20,
                        "capacity_baseline_mw": "200.00",
                        "mw_years_net": "20.000",
                        "determined": "18.000",
                        "share_of_net_percent": "20.0",
                        "share_of_capacity_percent": "24.0",
                        "concentration_points": "-4.0",
                    },
                }
                if dimension == "plant_type"
                else None
            ),
        }

    def group(c, name, bucket=False, thin=False):
        return {
            "key": f"{c['key']}|{name}",
            "rule_version": "76ad7dc3",
            "group": name,
            "bucket": bucket,
            "units_baseline": 10,
            "matched": 8,
            "dated_both": 6,
            "later": 2,
            "earlier": 1,
            "unchanged": 3,
            "capacity_baseline_mw": "1000.00",
            "capacity_current_mw": "1000.00",
            "mw_years_later": "12.000",
            "mw_years_earlier": "-2.000",
            "determined": "9.000",
            "undetermined": {sbg.RULE_V2: "1.000", v3.RULE_CONTENT: "2.000"},
            "total": {sbg.RULE_V2: "10.000", v3.RULE_CONTENT: "11.000"},
            "share_of_net_percent": "50.0",
            "share_of_determined_percent": "49.0",
            "share_of_capacity_percent": "40.0",
            "concentration_points": "10.0",
            "thin": None if name == sbg.KEY_CHANGED else thin,
        }

    comparisons, groups = [], []
    for window, regime, b, cur in (
        ("headline", "old", "2024-07-19", "2025-07-22"),
        ("2024", "old", "2024-01-05", "2025-01-03"),
        ("copy-to-copy", "new", "2026-05-19", "2026-08-22"),
    ):
        for dimension in ("host_to", "plant_type"):
            c = comparison(window, dimension, regime, b, cur)
            comparisons.append(c)
            names = (
                ("NGET", "OFTO", sbg.KEY_CHANGED)
                if dimension == "host_to"
                else (
                    "Energy Storage System",
                    "Energy Storage System;PV Array (Photo Voltaic/solar)",
                    sbg.KEY_CHANGED,
                )
            )
            groups += [
                group(c, n, bucket=(n == sbg.KEY_CHANGED), thin=(n == "OFTO")) for n in names
            ]
    summary = {
        "rule_version": "76ad7dc3",
        "declaration_sha256": "76ad7dc3" + "0" * 56,
        "declaration_timestamps": {
            "proofs": [{"kind": "rfc3161", "tsa": "digicert", "status": "ok"}]
        },
        "seal": "76ad7dc3",
        "run_date": "2026-10-01",
        "schema_report_sha256": "9e" * 32,
        "v4_manifest_sha256": "4b" * 32,
        "content_rule_sha256": "a0" * 32,
        "copies": {"usable": 700, "first": "2014-01-31", "last": "2026-09-15"},
        "rows": {"comparisons_appended": 6, "groups_appended": 18},
        "unfit": [],
        "not_read": [],
        "propositions": sbg.propositions(
            {
                "not_read": False,
                "groups": [g for g in groups if g["key"].startswith(comparisons[0]["key"])],
            },
            {
                "not_read": False,
                "groups": [g for g in groups if g["key"].startswith(comparisons[1]["key"])],
                "storage": comparisons[1]["storage"],
            },
        ),
    }
    return summary, comparisons, groups


def test_the_page_is_a_pure_function_of_the_evidence_and_keeps_the_framing_rules():
    summary, comparisons, groups = evidence_fixture()
    text = page.render_findings(summary, comparisons, groups)
    assert text == page.render_findings(summary, comparisons, groups)
    assert "promise" not in text.replace("never a promise", "")
    # The cause split appears beside every figure section: the headline, both
    # year tables and the storage table.
    assert text.count(page.CAUSE_SPLIT) >= 6
    assert "+57,823" in text and "+53,221" in text  # the headline with its split
    assert "| NGET |" in text and "OFTO" in text and "thin" in text
    assert "**P-A**" in text and "**P-B**" in text and "**P-C**" in text
    assert "Thin groups under R7" in text and "OFTO" in text.split("Thin groups under R7")[1]
    assert "76ad7dc3" in text


def test_the_page_renders_only_the_summarys_rule_version():
    summary, comparisons, groups = evidence_fixture()
    stale = dict(comparisons[0], rule_version="deadbeef", key="deadbeef|x")
    text = page.render_findings(summary, [*comparisons, stale], groups)
    assert "deadbeef" not in text
