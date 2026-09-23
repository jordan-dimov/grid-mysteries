from datetime import date
from decimal import Decimal as D

import pytest

from grid_mysteries.investigations import p415_compensation as p4
from grid_mysteries.sources import elexon_portal as portal


def bp7(unit, *, s_vol="", vtp="", cash=""):
    """A 26-field BP7 line with only the P415 tail positions set."""
    f = ["BP7", unit] + ["0"] * 16 + [""] * 8
    f[p4.BP7_SUPPLIER_COMPENSATION_VOLUME] = s_vol
    f[p4.BP7_SECONDARY_COMPENSATION_VOLUME] = vtp
    f[p4.BP7_SUPPLIER_COMPENSATION_CASHFLOW] = cash
    assert len(f) == 26
    return "|".join(f) + "|\n"


def bph(party):
    return f"BPH|20260828|SF|2|2|20260828|2|166710|{party}|\n"


HEAD = [
    "AAA|S0142013|D|20260922223519|SA|UKDC|PB|PORTAL|41694|OPER|\n",
    "SRH|20260828|SF|2|2|20260828|2|166710|NGC|\n",
]
SPI = ["SPI|1|121.68|121.68|N|\n", "SPI|2|122.01|122.01|N|\n"]


def day(*body):
    return HEAD + SPI + list(body) + ["ZZZ|1|2|\n"]


def test_the_party_is_the_bph_above_the_bp7_never_the_unit_code():
    lines = day(
        bph("ALMAPERJ"),
        "SP7|1|\n",
        bp7("V__KALMA002", vtp="10"),
        bph("GMTR"),
        "SP7|1|\n",
        bp7("2__HGMTR000", s_vol="9", cash="900"),
        # a unit whose letters name another party still counts for its BPH
        bph("AXLEENER"),
        "SP7|2|\n",
        bp7("V__AALMA001", vtp="1"),
    )
    s = p4.summarise(lines)
    assert s.settlement_date == date(2026, 8, 28) and s.run == "SF"
    assert dict(s.vtp_volume) == {"ALMAPERJ": D("10"), "AXLEENER": D("1")}
    assert dict(s.supplier_cash) == {"GMTR": D("900")}
    assert dict(s.supplier_volume) == {"GMTR": D("9")}
    assert s.periods == {1, 2} and s.bp7_lines == 3


def test_blank_is_absent_and_zero_is_a_value():
    s = p4.summarise(
        day(bph("X"), "SP7|1|\n", bp7("2__AXXXX001", s_vol="0", cash="0"), bp7("2__AXXXX002"))
    )
    assert dict(s.supplier_cash) == {"X": D("0")}
    assert s.supplier_cash_total == 0


def test_negative_cash_is_kept_with_its_sign():
    s = p4.summarise(
        day(bph("A"), "SP7|1|\n", bp7("2__AAAAA001", cash="100"), bp7("2__AAAAA002", cash="-30"))
    )
    assert s.supplier_cash_total == D("70")


def test_a_p415_value_off_its_prefix_is_counted_and_never_summed():
    s = p4.summarise(
        day(
            bph("A"),
            "SP7|1|\n",
            bp7("C__AAAAA001", cash="5"),
            bp7("2__AAAAA001", vtp="3"),
            bp7("T_ABC-1", s_vol="1"),
        )
    )
    assert s.supplier_cash_total == 0 and s.vtp_volume_total == 0 and s.supplier_volume_total == 0
    assert dict(s.off_prefix) == {"25:C__": 1, "23:2__": 1, "22:T_A": 1}


def test_a_bp7_without_a_bph_and_sp7_above_it_is_an_orphan():
    s = p4.summarise(day(bp7("V__AAAAA001", vtp="4"), bph("A"), bp7("V__AAAAA001", vtp="4")))
    assert s.orphan_bp7 == 2 and s.vtp_volume_total == 0


def test_the_trailing_pipe_is_not_a_field():
    assert p4._fields("BP7|a|b|\n") == ["BP7", "a", "b"]
    assert p4._fields("BP7|a||\n") == ["BP7", "a", ""]


def test_file_names_parse_and_foreign_names_are_refused():
    f = p4.parse_name("S0142_20260217_R3_20260922224432.gz")
    assert (f.settlement_date, f.run, f.published.hour) == (date(2026, 2, 17), "R3", 22)
    with pytest.raises(ValueError):
        p4.parse_name("S0142_20260217_R3.gz")


def test_latest_run_is_by_run_order_then_publication_and_never_below_the_floor():
    names = [
        "S0142_20260101_II_20260110000000.gz",
        "S0142_20260101_R1_20260301000000.gz",
        "S0142_20260101_SF_20260125000000.gz",
        "S0142_20260101_ZZ_20270101000000.gz",  # unknown run: never selected
    ]
    files = [p4.parse_name(n) for n in names]
    latest = p4.latest_run(files)
    assert latest is not None and latest.run == "R1"
    assert p4.latest_run(files[:1]) is None  # II alone does not reach SF
    ii = p4.latest_run(files[:1], minimum="II")
    assert ii is not None and ii.run == "II"
    again = p4.parse_name("S0142_20260101_R1_20260302000000.gz")
    assert p4.latest_run([*files, again]) is again


def summary(cash=None, vtp=None, run="SF"):
    s = p4.DaySummary(settlement_date=date(2026, 1, 1), run=run)
    for k, v in (cash or {}).items():
        s.supplier_cash[k] = D(v)
    for k, v in (vtp or {}).items():
        s.vtp_volume[k] = D(v)
    return s


def test_h1_is_a_ratio_of_mean_daily_cash_killed_below_the_threshold():
    base = [summary({"A": "100"}), summary({"A": "300"})]
    assert p4.h1_ratio([summary({"B": "150"})], base, kill_below=D("0.5"))["verdict"] == "holds"
    out = p4.h1_ratio([summary({"B": "99"})], base, kill_below=D("0.5"))
    assert out["ratio"] == D("0.495") and out["verdict"] == "killed"
    # exactly at the threshold is not below it
    assert p4.h1_ratio([summary({"B": "100"})], base, kill_below=D("0.5"))["verdict"] == "holds"


def test_h1_decides_nothing_against_an_empty_or_non_positive_baseline():
    assert (
        p4.h1_ratio([summary({"A": "1"})], [summary({"A": "0"})], kill_below=D("0.5"))["verdict"]
        == "not decided"
    )
    with pytest.raises(ValueError):
        p4.h1_ratio([], [summary({"A": "1"})], kill_below=D("0.5"))


def test_h2_chooses_the_party_on_the_baseline_and_only_reads_it_after():
    base = [summary(vtp={"ALMA": "80", "AXLE": "20"})]
    post = [summary(vtp={"AXLE": "90", "ALMA": "5", "EDF": "5"})]
    out = p4.h2_handover(base, post, "vtp_volume", baseline_above=D("0.5"), post_below=D("0.1"))
    assert (
        out["party"] == "ALMA"
        and out["baseline_share"] == D("0.8")
        and out["post_share"] == D("0.05")
    )
    assert out["verdict"] == "holds"
    # the post window's own leader is never substituted
    stays = [summary(vtp={"ALMA": "50", "AXLE": "50"})]
    assert (
        p4.h2_handover(base, stays, "vtp_volume", baseline_above=D("0.5"), post_below=D("0.1"))[
            "verdict"
        ]
        == "fails"
    )


def test_h2_needs_a_concentrated_baseline():
    base = [summary(cash={"A": "50", "B": "50"})]
    post = [summary(cash={"C": "1"})]
    out = p4.h2_handover(base, post, "supplier_cash", baseline_above=D("0.5"), post_below=D("0.25"))
    assert out["verdict"] == "fails"  # 50 % is not more than half


def test_restatement_is_measured_against_the_latest_run():
    runs = [
        summary({"A": "110"}, run="R2"),
        summary({"A": "100"}, run="SF"),
        summary({"A": "80"}, run="II"),
    ]
    out = p4.restatement(runs, "supplier_cash_total")
    assert [r["run"] for r in out] == ["II", "SF", "R2"]
    assert [r["movement"] for r in out] == [D("30") / D("110"), D("10") / D("110"), D("0")]


def test_the_portal_key_never_enters_an_identity_url_or_an_error():
    ident = portal.download_url("S0142_20260217_R3_20260922224432.gz")
    assert "key" not in ident
    redacted = portal.redact(f"failed to fetch {portal.with_key(ident, 's3cret')}", "s3cret")
    assert "s3cret" not in redacted and redacted.endswith("key=<ELEXON_PORTAL_KEY>")
    assert (
        portal.list_url("2026-09-22")
        == "https://downloads.elexonportal.co.uk/p114/list?date=2026-09-22&filter=s0142"
    )


def test_the_windows_are_the_declarations_and_the_seen_days_are_in_none_of_the_tests():
    w = p4.WINDOWS
    assert (len(w["FEB"]), len(w["PRE"]), len(w["POST"]), len(w["SERIES"]), len(w["C4"])) == (
        27,
        14,
        13,
        51,
        28,
    )
    for seen in p4.SCHEMA_PASS_DAYS:
        assert all(seen not in w[k] for k in ("FEB", "PRE", "POST", "SERIES"))
    assert date(2026, 2, 17) in w["C4"]
    assert all(d.weekday() == 2 for d in w["SERIES"])
    assert set(p4.RESTATE) <= set(w["SERIES"])
    assert w["POST"][0] == date(2026, 8, 24) and w["PRE"][-1] == date(2026, 8, 23)


def test_selection_takes_sf_or_later_lists_missing_days_and_keeps_every_restate_run():
    names = [
        "S0142_20260824_II_20260831000000.gz",  # POST day with only II: missing
        "S0142_20260825_SF_20260918000000.gz",
        "S0142_20250903_II_20250910000000.gz",
        "S0142_20250903_SF_20250925000000.gz",
        "S0142_20250903_R1_20251105000000.gz",
        "S0142_20250903_XX_20251106000000.gz",  # unknown: reported, never chosen
        "not-an-s0142.txt",
    ]
    out = p4.select(p4.build_index(names))
    assert date(2026, 8, 24) in out["missing"]["POST"]
    assert out["chosen"]["POST"][date(2026, 8, 25)].run == "SF"
    assert out["chosen"]["SERIES"][date(2025, 9, 3)].run == "R1"
    assert [f.run for f in out["restate"][date(2025, 9, 3)]] == ["II", "SF", "R1"]
    assert out["unknown_runs"] == ["XX"]


def test_restatement_matters_only_on_two_of_four_days_above_five_percent():
    five = D("0.05")
    assert (
        p4.restate_verdict([D("0.06"), D("0.051"), D("0"), D("0")], above=five, days=2) == "holds"
    )
    assert p4.restate_verdict([D("0.06"), D("0.05"), D("0"), D("0")], above=five, days=2) == "fails"
    assert (
        p4.restate_verdict([D("0.06"), None, D("0"), D("0")], above=five, days=2) == "not decided"
    )


def test_checks_pass_on_a_consistent_file_and_fail_on_a_foreign_layout():
    ssc = [f"SPI|{i}|" + "|".join(["0"] * 51) + "|10.00|\n" for i in range(1, 49)]
    lines = (
        HEAD
        + ssc
        + [
            bph("A"),
            "APC|" + "|".join(["0"] * 10) + "|20.00|20.00|\n",
            "SP7|1|\n",
            bp7("2__AAAAA001", s_vol="2", cash="20.00"),
            bph("V"),
            "SP7|1|\n",
            bp7("V__AVVVV001", vtp="2"),
            "ZZZ|1|2|\n",
        ]
    )
    s = p4.summarise(lines)
    assert s.charged_total == D("20.00") and s.apc_paid_total == D("20.00")
    assert s.paid_at_ssc == D("20.00") and s.vtp_at_ssc == D("20.00")
    expect = p4.parse_name("S0142_20260828_SF_20260922223519.gz")
    assert all(p4.checks(s, expect=expect).values())
    wrong_run = p4.parse_name("S0142_20260828_R1_20260922223519.gz")
    assert not p4.checks(s, expect=wrong_run)["C1 header matches name and layout"]
    short = p4.summarise(lines[:2] + lines[3:])  # one SPI period missing
    assert not p4.checks(short, expect=expect)["C3 48 settlement periods"]
    off = p4.summarise([*lines[:-1], bph("B"), "SP7|1|\n", bp7("2__BBBBB001", cash="5"), "ZZZ|\n"])
    assert not p4.checks(off, expect=expect)["C6 paid cash is volume x Supplier Sourcing Cost"]
    assert not p4.checks(off, expect=expect)["C7 BP7 cash equals the APC day total, party by party"]
