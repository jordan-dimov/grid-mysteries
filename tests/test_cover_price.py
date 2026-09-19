from datetime import date
from decimal import Decimal as D

from grid_mysteries.investigations import cover_price as cp
from grid_mysteries.investigations import record_day as rd

FUEL = {"W1": "WIND", "W2": "WIND", "G1": "CCGT", "G2": "OCGT", "PS": "PS"}


def ebocf(period, unit, total):
    return {"settlementPeriod": period, "bmUnit": unit, "totalCashflow": total}


def disptav(unit, kind, *volumes):
    return {
        "bmUnit": unit,
        "dataType": kind,
        "pairVolumes": {f"v{i}": v for i, v in enumerate(volumes)},
    }


# ------------------------------------------------------------------- batches


def test_batches_are_weekly_from_the_ninth_and_never_touch_the_seed_dates():
    assert cp.batch_dates(1) == [f"2026-09-{d:02d}" for d in range(9, 16)]
    assert cp.batch_dates(2)[0] == "2026-09-16" and cp.batch_dates(2)[-1] == "2026-09-22"
    assert cp.batch_index("2026-09-09") == 1
    assert cp.batch_index("2026-09-15") == 1
    assert cp.batch_index("2026-09-16") == 2
    assert tuple(f"2026-09-{d:02d}" for d in range(1, 9)) == cp.SEED_DATES
    for seed in cp.SEED_DATES:
        try:
            cp.batch_index(seed)
        except ValueError:
            continue
        raise AssertionError(f"{seed} must not belong to a batch")


def test_batch_needs_three_full_days_after_its_last_date():
    assert cp.earliest_fetch_date(1) == date(2026, 9, 19)
    assert cp.eligible_batches(date(2026, 9, 18)) == []
    assert cp.eligible_batches(date(2026, 9, 19)) == [1]
    assert cp.eligible_batches(date(2026, 9, 25)) == [1]
    assert cp.eligible_batches(date(2026, 9, 26)) == [1, 2]


# ------------------------------------------------------------ volume gate


def test_volumes_by_type_sums_absolute_pairs_per_unit_and_type():
    records = [
        disptav("G1", "Original", "10", None, "-2"),
        disptav("G1", "Tagged", "999"),
        disptav("W1", "Original"),
        disptav("W1", "Unknown", "5"),
    ]
    out = cp.volumes_by_type(records)
    assert out["Original"] == {"G1": D("12")}
    assert out["Tagged"] == {"G1": D("999")}
    assert out["Re-priced"] == {} and out["Original-Priced"] == {}


def test_settlement_totals_take_absolute_bid_volumes():
    rows: list[dict] = [
        {"totalAcceptedOfferVolume": "100.5", "totalAcceptedBidVolume": "-40"},
        {"totalAcceptedOfferVolume": None, "totalAcceptedBidVolume": "-10"},
    ]
    assert cp.settlement_totals(rows) == {"offer": D("100.5"), "bid": D("50")}


def test_reconcile_requires_both_directions_within_tolerance():
    settlement = {"offer": D("132101"), "bid": D("143704")}
    totals = {
        "Original": {"offer": D("130135"), "bid": D("24806")},  # offers 1.5 % off, bids far off
        "Original-Priced": {"offer": D("5236"), "bid": D("1936")},
        "Re-priced": {"offer": D("0"), "bid": D("1862")},
        "Tagged": {"offer": D("132083"), "bid": D("143685")},  # 0.014 % and 0.013 %
    }
    out = cp.reconcile(totals, settlement)
    assert out["chosen"] == "Tagged"
    assert out["by_type"]["Tagged"]["reconciles"] is True
    assert out["by_type"]["Original"]["reconciles"] is False
    assert out["by_type"]["Original"]["offer_deviation"] == "0.014883"


def test_reconcile_none_when_nothing_reconciles_and_boundary_at_tolerance():
    settlement = {"offer": D("1000"), "bid": D("1000")}
    off = {t: {"offer": D("1002"), "bid": D("1000")} for t in cp.DATA_TYPES}  # 0.2 %
    assert cp.reconcile(off, settlement)["chosen"] is None
    edge = {t: {"offer": D("999"), "bid": D("1001")} for t in cp.DATA_TYPES}  # exactly 0.1 %
    out = cp.reconcile(edge, settlement)
    assert out["chosen"] == "Original"  # all tie at the boundary; declared order breaks it
    assert all(v["reconciles"] for v in out["by_type"].values())


def test_reconcile_prefers_the_smallest_worst_deviation_over_declared_order():
    settlement = {"offer": D("1000"), "bid": D("1000")}
    totals = {
        "Original": {"offer": D("1000.9"), "bid": D("1000")},
        "Tagged": {"offer": D("1000.1"), "bid": D("1000")},
    }
    assert cp.reconcile(totals, settlement)["chosen"] == "Tagged"


def test_reconcile_zero_settlement_total_matches_only_zero():
    settlement = {"offer": D("500"), "bid": D("0")}
    totals = {
        "Original": {"offer": D("500"), "bid": D("3")},
        "Tagged": {"offer": D("500"), "bid": D("0")},
    }
    out = cp.reconcile(totals, settlement)
    assert out["chosen"] == "Tagged"
    assert out["by_type"]["Original"]["bid_deviation"] is None
    assert out["by_type"]["Original"]["reconciles"] is False


def test_pairing_and_volume_columns_follow_the_chosen_type():
    rows = rd.cashflow_rows([ebocf(1, "G1", "2000"), ebocf(2, "G2", "1000")], "offer")
    rows += rd.cashflow_rows([ebocf(1, "W1", "300")], "bid")
    cash = cp.cash_index(rows)
    pairing = cp.VolumePairing()
    pairing.add_period(
        1, "offer", [disptav("G1", "Tagged", "10"), disptav("G1", "Original", "1")], cash, FUEL
    )
    pairing.add_period(2, "offer", [disptav("G2", "Tagged", "10")], cash, FUEL)
    pairing.add_period(
        1, "bid", [disptav("W1", "Tagged", "-6"), disptav("W1", "Original", "-1")], cash, FUEL
    )
    assert pairing.totals["Tagged"] == {"offer": D("20"), "bid": D("6")}
    assert pairing.totals["Original"] == {"offer": D("1"), "bid": D("1")}
    mid = {1: D("100"), 2: D("50")}
    cols = cp.volume_columns(pairing, "Tagged", mid)
    assert cols["gas_offer_mwh"] == "20"
    assert cols["gas_offer_vwap_gbp_per_mwh"] == "150.00"
    assert cols["mid_vwap_same_periods_gbp_per_mwh"] == "75.00"
    assert cols["premium_gbp_per_mwh"] == "75.00"
    assert cols["wind_bid_mwh"] == "6" and cols["wind_bid_vwap_gbp_per_mwh"] == "50.00"
    blank = cp.volume_columns(pairing, None, mid)
    assert all(v is None for v in blank.values())


# ---------------------------------------------------------------------- rows


def test_money_columns_two_cuts_residual_and_sign_both_ways():
    bids = rd.cashflow_rows(
        [ebocf(1, "W1", "100"), ebocf(2, "W2", "-5"), ebocf(1, "PS", "-20")], "bid"
    )
    offers = rd.cashflow_rows(
        [ebocf(1, "G1", "900"), ebocf(3, "G2", "50"), ebocf(3, "X", "10"), ebocf(4, "W1", "2")],
        "offer",
    )
    cols = cp.money_columns(rd.ledger("2026-09-09", bids + offers, FUEL))
    assert cols["paid_out_gbp"] == "1062" and cols["net_gbp"] == "1037"
    assert cols["wind_bid_gbp"] == "100" and cols["gas_offer_gbp"] == "950"
    assert cols["other_gbp"] == "12"  # unclassified offer 10 + wind offer 2: the residual
    assert cols["two_cut_gbp"] == "1050"
    assert cols["sign_convention_holds"] is False  # one positive row, one negative: not a majority
    assert cols["wind_bid_inverted_gbp"] == "5"
    assert cols["wind_bid_inverted_share_of_paid_in"] == "0.2000"


def test_bsad_columns_blank_on_placeholder_and_absent_days():
    placeholder = rd.bsad_summary(
        [{"TradeFlag": "F", "DisaggregatedBSADCost": "0", "DisaggregatedBSADVolume": "0"}] * 48
    )
    cols = cp.bsad_columns(placeholder, D("1000"))
    assert cols["bsad_available"] is False and cols["bsad_placeholder_only"] is True
    assert cols["bsad_net_gbp"] is None and cols["bsad_share"] is None
    absent = cp.bsad_columns(None, D("1000"))
    assert absent["bsad_available"] is False and absent["bsad_rows"] is None
    live = cp.bsad_columns(
        rd.bsad_summary(
            [{"TradeFlag": "T", "DisaggregatedBSADCost": "60", "DisaggregatedBSADVolume": "1"}]
        ),
        D("1000"),
    )
    assert live["bsad_net_gbp"] == "60" and live["bsad_share"] == "0.0600"


def test_outcome_columns_none_until_neso_reaches_the_day():
    assert cp.outcome_columns(None, None, None, "2026-10-01", D("10"), D("12")) is None
    out = cp.outcome_columns(D("15"), D("100"), D("200"), "2026-10-01", D("10"), D("12"))
    assert out is not None
    assert out["vintage"] == "2026-10-01"
    assert out["ratio_l1_to_two_cut"] == "1.5000"
    assert out["ratio_l1_to_paid_out"] == "1.2500"
    l4_only = cp.outcome_columns(None, D("1"), D("2"), "2026-10-01", D("10"), D("12"))
    assert l4_only is not None and l4_only["l1_constraints_gbp"] is None
    assert l4_only["ratio_l1_to_two_cut"] is None


def row(day, paid_out, *, seed=False, available=True, **extra):
    return {
        "settlement_date": day,
        "seed": seed,
        "available": available,
        "paid_out_gbp": str(paid_out),
        "two_cut_gbp": str(D(paid_out) * D("0.9")),
        **extra,
    }


def test_flag_records_seeds_set_the_bar_but_are_never_flagged():
    rows = [
        row("2026-09-08", "33610463", seed=True),
        row("2026-09-04", "30049726", seed=True),
        row("2026-09-10", "35000000"),
        row("2026-09-09", "20000000"),
        row("2026-09-11", "35000000"),  # equal to the running max: not a record
        row("2026-09-12", "1", available=False),
        row("2026-09-13", "36000000"),
    ]
    ordered = cp.flag_records(rows)
    assert [r["settlement_date"] for r in ordered] == sorted(r["settlement_date"] for r in rows)
    flags = {r["settlement_date"]: r["record"] for r in ordered}
    assert flags == {
        "2026-09-04": False,
        "2026-09-08": False,
        "2026-09-09": False,
        "2026-09-10": True,
        "2026-09-11": False,
        "2026-09-12": False,
        "2026-09-13": True,
    }
    by_day = {r["settlement_date"]: r for r in ordered}
    assert by_day["2026-09-10"]["prior_max_paid_out_gbp"] == "33610463"
    assert by_day["2026-09-13"]["prior_max_paid_out_gbp"] == "35000000"


def test_flag_records_is_idempotent_and_order_independent():
    rows = [row("2026-09-10", "40"), row("2026-09-09", "50"), row("2026-09-08", "45", seed=True)]
    first = cp.flag_records(rows)
    again = cp.flag_records(list(reversed(first)))
    assert [(r["settlement_date"], r["record"]) for r in again] == [
        ("2026-09-08", False),
        ("2026-09-09", True),
        ("2026-09-10", False),
    ]


# -------------------------------------------------------------- propositions


def test_evaluate_none_without_instances_and_counterexample_fails():
    rows = cp.flag_records(
        [
            row("2026-09-08", "100", seed=True, bsad_share="0.0992", premium_gbp_per_mwh="82.64"),
            row("2026-09-09", "50", bsad_share="0.01", premium_gbp_per_mwh="10"),
        ]
    )
    verdicts = cp.evaluate(rows, date(2026, 9, 20))
    assert verdicts["record_days"] == []
    assert verdicts["T1"]["holds"] is None and verdicts["T3"]["holds"] is None
    assert verdicts["T2"]["holds"] is None and verdicts["falsifier_date_reached"] is False

    rows = cp.flag_records(
        [
            row("2026-09-08", "100", seed=True),
            row("2026-09-09", "120", bsad_share="0.0600", premium_gbp_per_mwh="51"),
            row("2026-09-10", "130", bsad_share="0.0500", premium_gbp_per_mwh="49.99"),
            row("2026-09-11", "140", bsad_share=None, premium_gbp_per_mwh=None),
        ]
    )
    verdicts = cp.evaluate(rows, date(2027, 3, 31))
    assert verdicts["record_days"] == ["2026-09-09", "2026-09-10", "2026-09-11"]
    assert verdicts["T1"]["holds"] is False  # exactly 5 % does not exceed 5 %
    assert verdicts["T3"]["holds"] is False
    assert [i["holds"] for i in verdicts["T1"]["instances"]] == [True, False, None]
    assert verdicts["falsifier_date_reached"] is True


def test_t2_decided_on_tracked_days_only_seeds_shown_as_context():
    rows = cp.flag_records(
        [
            row("2026-09-08", "100", seed=True, outcome={"l1_constraints_gbp": "10"}),  # < 90
            row("2026-09-09", "100", outcome={"l1_constraints_gbp": "95"}),  # > 90
            row("2026-09-10", "100", outcome=None),
        ]
    )
    t2 = cp.evaluate(rows, date(2026, 10, 1))["T2"]
    assert len(t2["instances"]) == 2 and t2["deciding_instances"] == 1
    assert t2["holds"] is True
    assert [i["seed"] for i in t2["instances"]] == [True, False]


# ---------------------------------------------------------------- rendering


def test_render_row_blank_columns_and_seed_marker():
    seed = {
        "settlement_date": "2026-09-08",
        "seed": True,
        "available": True,
        "record": False,
        "paid_out_gbp": "33610463.12",
        "net_gbp": "31560000",
        "wind_bid_gbp": "3768601",
        "wind_bid_share": "0.1121",
        "gas_offer_gbp": "26820639",
        "gas_offer_share": "0.7980",
        "other_gbp": "3021223",
        "other_share": "0.0899",
        "gas_offer_vwap_gbp_per_mwh": "229.53",
        "premium_gbp_per_mwh": "82.64",
        "disptav_type": "Original",
        "bsad_net_gbp": "3333989.85",
        "bsad_share": "0.0992",
        "sign_convention_holds": True,
        "outcome": None,
    }
    line = cp.render_row(seed)
    assert "| seed (012) | 33.61 | 31.56 | 3.77 (11.2 %) |" in line
    assert "| 229.53 | 82.64 | Original † | 3.33 (9.9 %) | holds |  |  |" in line
    tracked = dict(
        seed, seed=False, record=True, disptav_type=None, reconciliation={"chosen": None}
    )
    tracked.update(
        gas_offer_vwap_gbp_per_mwh=None,
        premium_gbp_per_mwh=None,
        bsad_net_gbp=None,
        bsad_share=None,
        bsad_placeholder_only=True,
        outcome={
            "l1_constraints_gbp": "40000000",
            "vintage": "2026-10-02",
            "ratio_l1_to_two_cut": "1.3075",
        },
    )
    line = cp.render_row(tracked)
    assert "| **record** |" in line
    assert "|  |  | none reconciles | unpopulated | holds | 40.00 (2026-10-02) | 130.8 % |" in line
    unavailable = {"settlement_date": "2026-09-12", "seed": False, "available": False}
    assert cp.render_row(unavailable).startswith("| 2026-09-12 | unavailable |")
    assert cp.render_table([unavailable]).startswith(cp.TABLE_HEADER)


def test_display_cautions_mark_values_without_changing_them():
    base = {
        "settlement_date": "2026-09-12",
        "seed": False,
        "available": True,
        "paid_out_gbp": "23540000",
        "net_gbp": "22400000",
        "wind_bid_gbp": "2800000",
        "wind_bid_share": "0.119",
        "gas_offer_gbp": "17680000",
        "gas_offer_share": "0.751",
        "other_gbp": "3070000",
        "other_share": "0.130",
        "bsad_net_gbp": "72.86",
        "bsad_share": "0.0000",
        "sign_convention_holds": True,
        "outcome": None,
    }
    quiet = dict(base, settlement_date="2026-09-16")
    assert cp.render_table([quiet]) == "\n".join([cp.TABLE_HEADER, cp.render_row(quiet)])
    assert "‡" not in cp.render_row(quiet) and "§" not in cp.render_row(quiet)
    line = cp.render_row(dict(base, sign_convention_holds=False))
    assert "| 2.80 (11.9 %) ‡ |" in line and "| 0.00 (0.0 %) § |" in line
    table = cp.render_table([dict(base, sign_convention_holds=False)])
    assert table.endswith(
        "§ BSAD provisional: NESO may not have finished filling the marked days. The declared "
        "rule treats a day with rows as populated, so this is a caution, not a reclassification."
    )
    assert "\n\n‡ The sign check on wind-unit bids failed" in table
    unpopulated = dict(base, bsad_net_gbp=None, bsad_share=None, bsad_placeholder_only=True)
    assert "§" not in cp.render_row(unpopulated)  # nothing to caution on a blank
    assert "‡" not in cp.render_row(dict(base, sign_convention_holds=None))
