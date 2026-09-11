from decimal import Decimal as D

from grid_mysteries.investigations import record_day as rd


def ebocf(period, unit, total):
    return {"settlementPeriod": period, "bmUnit": unit, "totalCashflow": total}


FUEL = {"W1": "WIND", "W2": "WIND", "G1": "CCGT", "G2": "OCGT", "PS": "PS"}


def test_fuel_class_never_guesses():
    assert rd.fuel_class("WIND") == "wind"
    assert rd.fuel_class("ccgt") == "gas"
    assert rd.fuel_class("OCGT") == "gas"
    assert rd.fuel_class("PS") == "other"
    assert rd.fuel_class(None) == "other"
    assert rd.fuel_class("") == "other"


def test_cashflow_rows_skip_absent_totals():
    rows = rd.cashflow_rows(
        [ebocf(1, "W1", "10.5"), {"settlementPeriod": 1, "bmUnit": "W2"}, ebocf(2, "G1", None)],
        "bid",
    )
    assert [(r.period, r.unit, r.gbp) for r in rows] == [(1, "W1", D("10.5"))]


def test_ledger_sums_and_sign_counts():
    bids = rd.cashflow_rows(
        [ebocf(1, "W1", "100"), ebocf(2, "W2", "-5"), ebocf(1, "PS", "-20")], "bid"
    )
    offers = rd.cashflow_rows(
        [ebocf(1, "G1", "900"), ebocf(3, "G2", "50"), ebocf(3, "X", "10")], "offer"
    )
    led = rd.ledger("2026-09-08", bids + offers, FUEL)
    assert led.available and led.periods_with_rows == 3 and led.units == 6
    assert led.total == D("1035")
    assert led.paid_out == D("1060") and led.paid_in == D("-25")
    assert led.by_class["wind"]["bid"] == D("95")
    assert led.paid_out_by_class["wind"]["bid"] == D("100")
    assert led.paid_out_by_class["gas"]["offer"] == D("950")
    assert led.paid_out_by_class["other"]["offer"] == D("10")  # unclassified unit stays other
    assert (led.wind_bid_positive_rows, led.wind_bid_negative_rows) == (1, 1)


def test_empty_day_is_unavailable():
    led = rd.ledger("2026-09-01", [], FUEL)
    assert not led.available and led.total == D(0)


def test_select_day_highest_total_ties_earlier_and_excludes_unavailable():
    a = rd.ledger("2026-09-04", rd.cashflow_rows([ebocf(1, "G1", "50")], "offer"), FUEL)
    b = rd.ledger("2026-09-08", rd.cashflow_rows([ebocf(1, "G1", "50")], "offer"), FUEL)
    c = rd.ledger("2026-09-02", rd.cashflow_rows([ebocf(1, "G1", "20")], "offer"), FUEL)
    empty = rd.ledger("2026-09-01", [], FUEL)
    assert rd.select_day({"a": a, "b": b, "c": c, "e": empty}) == ("2026-09-04", "2026-09-08")
    assert rd.select_day({"e": empty}) == (None, None)


def test_accepted_mwh_original_rows_only():
    records = [
        {
            "bmUnit": "G1",
            "dataType": "Original",
            "pairVolumes": {"p1": "10", "p2": None, "p3": "-2"},
        },
        {"bmUnit": "G1", "dataType": "Tagged", "pairVolumes": {"p1": "999"}},
        {"bmUnit": "W1", "dataType": "Original", "pairVolumes": {}},
    ]
    assert rd.accepted_mwh(records) == {"G1": D("12")}


def test_vwap_none_on_zero_volume():
    assert rd.vwap(D("100"), D(0)) is None
    assert rd.vwap(D("100"), D("4")) == D("25.00")


def test_mid_prices_one_provider_volume_weighted():
    records = [
        {"dataProvider": "APXMIDP", "settlementPeriod": 1, "price": "100", "volume": "1"},
        {"dataProvider": "APXMIDP", "settlementPeriod": 1, "price": "200", "volume": "3"},
        {"dataProvider": "N2EXMIDP", "settlementPeriod": 1, "price": "999", "volume": "3"},
        {"dataProvider": "APXMIDP", "settlementPeriod": 2, "price": "50", "volume": "0"},
    ]
    assert rd.mid_prices(records) == {1: D("175.00")}


def test_gas_offer_price_premium_excludes_periods_without_mid():
    out = rd.gas_offer_price({1: D("2310"), 2: D("2310")}, {1: D("10"), 2: D("10")}, {1: D("125")})
    assert out["gas_offer_vwap_gbp_per_mwh"] == "231.00"
    assert out["mid_vwap_same_periods_gbp_per_mwh"] == "125.00"
    assert out["premium_gbp_per_mwh"] == "106.00"
    assert out["periods_without_mid"] == 1


def test_evaluate_thresholds_and_none_inputs():
    bids = rd.cashflow_rows([ebocf(1, "W1", "100")], "bid")
    offers = rd.cashflow_rows([ebocf(1, "G1", "900")], "offer")
    led = rd.ledger("2026-09-08", bids + offers, FUEL)
    out = rd.evaluate(led, D("50"), D("231"))
    assert out["sign_convention_holds"] is True
    assert out["P1"]["holds"] is True and out["P1"]["wind_bid_share_of_paid_out"] == "0.1000"
    assert out["P2"]["holds"] is True and out["P2"]["bsad_share_of_paid_out"] == "0.0500"
    assert out["P3"]["holds"] is True
    boundary = rd.evaluate(led, D("49.99"), D("196.35"))  # 15% below 231 is 196.35
    assert boundary["P2"]["holds"] is False and boundary["P3"]["holds"] is True
    assert rd.evaluate(led, None, None)["P2"]["holds"] is None
    assert rd.evaluate(led, None, None)["P3"]["holds"] is None
    wind_heavy = rd.ledger("d", rd.cashflow_rows([ebocf(1, "W1", "600")], "bid") + offers, FUEL)
    assert rd.evaluate(wind_heavy, D(0), None)["P1"]["holds"] is False


def test_evaluate_with_no_paid_out_gives_none_for_p1():
    led = rd.ledger("d", rd.cashflow_rows([ebocf(1, "W1", "-5")], "bid"), FUEL)
    assert rd.evaluate(led, None, None)["P1"]["holds"] is None


def test_mid_prices_filters_to_the_settlement_day():
    records = [
        {
            "dataProvider": "APXMIDP",
            "settlementDate": "2026-09-08",
            "settlementPeriod": 3,
            "price": "100",
            "volume": "1",
        },
        {
            "dataProvider": "APXMIDP",
            "settlementDate": "2026-09-09",
            "settlementPeriod": 1,
            "price": "999",
            "volume": "1",
        },
    ]
    assert rd.mid_prices(records, settlement_date="2026-09-08") == {3: D("100.00")}
    assert rd.mid_prices(records) == {3: D("100.00"), 1: D("999.00")}  # unfiltered, for contrast


def bsad(cost, volume, flag="T"):
    return {"DisaggregatedBSADCost": cost, "DisaggregatedBSADVolume": volume, "TradeFlag": flag}


def test_bsad_summary_splits_by_trade_flag():
    out = rd.bsad_summary([bsad("100", "10"), bsad("-20", "-2", "F"), bsad("0", "0")])
    assert out["system_cost_gbp"] == "100" and out["energy_cost_gbp"] == "-20"
    assert out["system_volume_mwh"] == "10" and out["energy_volume_mwh"] == "-2"
    assert out["net_cost_gbp"] == "80"
    assert out["rows"] == 3 and out["nonzero_rows"] == 2
    assert out["available"] is True and out["placeholder_only"] is False


def test_bsad_summary_all_zero_placeholder_day_is_not_populated():
    out = rd.bsad_summary([bsad("0", "0")] * 48)
    assert out["rows"] == 48 and out["nonzero_rows"] == 0
    assert out["available"] is False and out["placeholder_only"] is True
    empty = rd.bsad_summary([])
    assert empty["available"] is False and empty["placeholder_only"] is False


def test_sign_convention_needs_rows_and_signed_sum_to_agree():
    offers = rd.cashflow_rows([ebocf(1, "G1", "900")], "offer")
    # two small positive rows, one large negative: rows say yes, pounds say no -> F2
    bids = rd.cashflow_rows(
        [ebocf(1, "W1", "1"), ebocf(2, "W1", "1"), ebocf(3, "W2", "-50")], "bid"
    )
    out = rd.evaluate(rd.ledger("d", bids + offers, FUEL), None, None)
    assert out["sign_convention_holds"] is False
    assert out["wind_bid_rows"] == {"positive": 2, "negative": 1}
    assert out["wind_bid_signed_sum_gbp"] == "-48"
    # one large positive row, two small negatives: pounds say yes, rows say no -> F2
    bids = rd.cashflow_rows(
        [ebocf(1, "W1", "500"), ebocf(2, "W1", "-1"), ebocf(3, "W2", "-1")], "bid"
    )
    assert (
        rd.evaluate(rd.ledger("d", bids + offers, FUEL), None, None)["sign_convention_holds"]
        is False
    )
