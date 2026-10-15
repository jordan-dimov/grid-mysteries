# ruff: noqa: E501
"""024 — the day rule, clock-change days, the leg arithmetic, the two ratio
definitions, the readers' forms and the falsifiers."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from grid_mysteries.investigations import gas_in_the_spread as g
from grid_mysteries.sources import n2ex_day_ahead, ons_sap, ukets_monthly

D = Decimal


def prices(*xs: str) -> list[Decimal]:
    return [D(x) for x in xs]


def test_day_rule_measures_23_to_25_prices_and_excludes_the_rest():
    assert g.day_spread(prices(*["10"] * 22 + ["50"])) == D(40)  # 23 prices
    assert g.day_spread(prices(*["10"] * 23 + ["50"])) == D(40)  # 24
    assert g.day_spread(prices(*["10"] * 24 + ["50"])) == D(40)  # 25
    assert g.day_spread(prices(*["10"] * 21 + ["50"])) is None  # 22
    assert g.day_spread(prices(*["10"] * 25 + ["50"])) is None  # 26
    assert g.day_spread([]) is None


def test_spread_is_highest_minus_lowest_including_negative_prices():
    day = prices(*["5"] * 22, "-12.5", "87.25")
    assert g.day_spread(day) == D("99.75")


def test_local_day_reads_a_printed_utc_hour_into_the_london_calendar_day():
    assert g.local_day(date(2026, 7, 1), 23) == date(2026, 7, 2)  # BST: 23:00 UTC is 00:00 next day
    assert g.local_day(date(2026, 7, 1), 22) == date(2026, 7, 1)
    assert g.local_day(date(2026, 1, 1), 23) == date(2026, 1, 1)  # GMT: no shift


def test_clock_change_days_have_23_and_25_hours_when_reconstructed_from_utc():
    def local_counts(first: date, last: date) -> dict[date, int]:
        counts: dict[date, int] = {}
        for o in range(first.toordinal(), last.toordinal() + 1):
            for h in range(24):
                ld = g.local_day(date.fromordinal(o), h)
                counts[ld] = counts.get(ld, 0) + 1
        return counts

    spring = local_counts(date(2026, 3, 27), date(2026, 3, 31))
    assert spring[date(2026, 3, 29)] == 23
    assert spring[date(2026, 3, 30)] == 24
    autumn = local_counts(date(2026, 10, 23), date(2026, 10, 28))
    assert autumn[date(2026, 10, 25)] == 25
    assert autumn[date(2026, 10, 26)] == 24


def test_ccgt_cost_is_twice_gas_plus_point_four_carbon():
    assert g.ccgt_cost(D(30), D(60)) == D(84)
    assert g.ccgt_cost(D("64.5"), D("50.25")) == D("149.1")


@pytest.mark.parametrize(
    "day, cost, expected",
    [
        # wholly negative day: the whole spread is the negative leg
        (prices("-30", "-20", "-5", "-1"), D(80), (D(29), D(0), D(0))),
        # no scarcity: nothing above the CCGT cost
        (prices("0", "20", "50", "79"), D(80), (D(0), D(79), D(0))),
        # all three legs
        (prices("-10", "5", "80", "130"), D(80), (D(10), D(80), D(50))),
        # flat day: every leg zero
        (prices("40", "40", "40"), D(80), (D(0), D(0), D(0))),
        # crossing zero only (max below cost)
        (prices("-7.5", "12.25"), D(80), (D("7.5"), D("12.25"), D(0))),
        # above cost only (min above cost)
        (prices("90", "150"), D(80), (D(0), D(0), D(60))),
    ],
)
def test_the_three_legs_sum_exactly_to_the_spread(day, cost, expected):
    lg = g.legs(day, cost)
    assert (lg.negative, lg.merit_order, lg.scarcity) == expected
    assert lg.total == max(day) - min(day)
    assert min(lg.negative, lg.merit_order, lg.scarcity) >= 0


def test_ratio_of_means_and_mean_of_ratios_differ_and_are_both_defined():
    spreads, gases = prices("100", "50"), prices("50", "10")
    assert g.ratio_of_means(spreads, gases) == D(75) / D(30)
    assert g.mean_of_ratios(zip(spreads, gases, strict=True)) == D("3.5")
    assert g.ratio_of_means([], []) is None
    assert g.mean_of_ratios([]) is None


def test_build_rows_joins_gas_and_the_months_carbon_and_counts_unmeasured_days():
    days = {
        date(2026, 9, 1): prices(*["20"] * 23, "-5"),
        date(2026, 9, 2): prices("1", "2"),  # two prices: not measured
        date(2026, 10, 1): prices(*["20"] * 24),  # no allowance for October
    }
    gas = {date(2026, 9, 1): D(60), date(2026, 9, 2): D(60)}
    rows = g.build_rows(days, gas, {(2026, 9): D(50)})
    r1, r2, r3 = rows
    assert (r1.spread, r1.gas, r1.carbon, r1.ccgt) == (D(25), D(60), D(68), D("147.2"))
    assert (r1.negative, r1.merit_order, r1.scarcity) == (D(5), D(20), D(0))
    assert r2.spread is None and r2.negative is None
    assert r3.spread == D(0) and r3.gas is None and r3.carbon is None and r3.negative is None


def test_periods_are_the_years_the_two_to_date_windows_and_the_months():
    ps = g.periods(date(2026, 10, 15), (2026, 10))
    labels = [p[0] for p in ps]
    assert labels[:6] == ["2022", "2023", "2024", "2025", "2026 to date", "2025 same dates"]
    assert dict((p[0], (p[1], p[2])) for p in ps)["2026 to date"] == (
        date(2026, 1, 1),
        date(2026, 10, 15),
    )
    assert dict((p[0], (p[1], p[2])) for p in ps)["2025 same dates"] == (
        date(2025, 1, 1),
        date(2025, 10, 15),
    )
    assert labels[6] == "2022-01" and labels[-1] == "2026-10" and len(labels) == 6 + 58
    assert dict((p[0], (p[1], p[2])) for p in ps)["2024-02"] == (
        date(2024, 2, 1),
        date(2024, 2, 29),
    )


def test_summarise_counts_days_and_computes_both_ratios_and_the_shares():
    days = {date(2026, 9, d): prices(*["20"] * 23, "-5") for d in (1, 2)}
    days[date(2026, 9, 3)] = prices("1")
    gas = {date(2026, 9, 1): D(60), date(2026, 9, 2): D(40), date(2026, 9, 3): D(40)}
    s = g.summarise(
        g.build_rows(days, gas, {(2026, 9): D(50)}), date(2026, 9, 1), date(2026, 9, 30)
    )
    assert (s["days_printed"], s["days_measured"], s["days_excluded_by_price_count"]) == (3, 2, 1)
    assert (s["days_with_gas"], s["days_with_both"], s["days_with_legs"]) == (3, 2, 2)
    assert (
        s["spread_mean"] == D(25)
        and s["gas_mean"] == D("46.666667")
        and s["gas_mean_both"] == D(50)
    )
    assert s["ratio_of_means"] == D("0.5") and s["mean_of_ratios"] == D("0.520833")
    assert s["legs_mean"] == {"negative": D(5), "merit_order": D(20), "scarcity": D(0)}
    assert s["legs_share"] == {"negative": D("0.2"), "merit_order": D("0.8"), "scarcity": D(0)}


def test_falsifiers():
    assert g.f1_fires(D("1.79"), D("2.25")) is False
    assert g.f1_fires(D("2.15"), D("2.25")) is True  # within 5 %
    assert g.f1_fires(D("2.30"), D("2.25")) is True
    assert g.f1_fires(None, D(2)) is None
    assert g.f2_fires(D("121.7")) is False
    assert g.f2_fires(D("124.5")) is True
    assert g.f2_fires(D("119.9")) is True


def test_n2ex_reader_reads_the_declared_forms_and_profiles_a_byte_order_mark(tmp_path: Path):
    good = tmp_path / "good.csv"
    good.write_text(
        "Date,Delivery Period,Price\n2026-09-01,22:00 - 23:00,129.950000\n2026-09-01,23:00 - 00:00,-1.500000\n"
    )
    rows = list(n2ex_day_ahead.read(good))
    assert [(r.day, r.start_hour, r.price) for r in rows] == [
        (date(2026, 9, 1), 22, D("129.950000")),
        (date(2026, 9, 1), 23, D("-1.500000")),
    ]
    profile = n2ex_day_ahead.format_profile(good)
    assert profile["header"] == ["Date", "Delivery Period", "Price"]
    assert profile["field_counts"] == {"3": 2} and profile["leading_byte_order_mark"] is False
    assert profile["forms"]["price"] == {"decimal-6": 2, "other": 0}
    bom = tmp_path / "bom.csv"
    bom.write_bytes(b"\xef\xbb\xbf" + good.read_bytes())
    assert n2ex_day_ahead.format_profile(bom)["leading_byte_order_mark"] is True
    bad = tmp_path / "bad.csv"
    bad.write_text("Date,Delivery Period,Price\n01/09/2026,22:00 - 23:00,129.95\n")
    with pytest.raises(ValueError):
        list(n2ex_day_ahead.read(bad))


def test_ons_sap_cells_convert_to_pounds_per_megawatt_hour_exactly():
    assert ons_sap.as_decimal(1.7083) * ons_sap.PENCE_PER_KWH_TO_GBP_PER_MWH == D("17.0830")
    assert ons_sap.as_decimal(2) * ons_sap.PENCE_PER_KWH_TO_GBP_PER_MWH == D(20)
    with pytest.raises(ValueError):
        ons_sap.as_decimal("[x]")


def test_ons_sap_reader_reads_the_daily_sheet(tmp_path: Path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = ons_sap.SHEET
    ws.append(["Table 1: Daily System Average Price (SAP) of Gas"])
    ws.append(["This worksheet contains one table."])
    ws.append(["Back to Notes"])
    ws.append(["Back to Contents"])
    ws.append(list(ons_sap.HEADER))
    ws.append([date(2026, 9, 1), 6.4512, "[x]"])
    ws.append([date(2026, 9, 2), 6, 6.2])
    path = tmp_path / "sap.xlsx"
    wb.save(path)
    assert ons_sap.read(path) == {date(2026, 9, 1): D("64.5120"), date(2026, 9, 2): D(60)}
    profile = ons_sap.format_profile(path)
    assert profile["header"] == list(ons_sap.HEADER) and profile["rows"] == 2
    assert profile["forms"]["sap"] == {"number": 2, "blank": 0, "other": 0}


CCM_HTML = """<html><body><main><div class="govspeak">
<table><tr><th>Month</th><th>2-year reference period</th><th>Trigger price</th><th>3-month monitoring period</th>
<th>Month 1 average price</th><th>Month 2 average price</th><th>Month 3 average price</th><th>CCM triggered? Yes or No</th></tr>
<tr><td>Aug-21</td><td>n/a</td><td>£44.74</td><td>May, June, July</td><td>£45.10</td><td>£47.20</td><td>£46.30</td><td>No</td></tr>
<tr><td>Sep-21</td><td>n/a</td><td>£44.74</td><td>June, July, Aug</td><td>£47.20</td><td>£46.30</td><td>£52.00</td><td>No</td></tr>
</table>
<table><tr><th>Month</th><th>2-year reference period</th><th>Trigger price</th><th>6-month monitoring period</th>
<th>Month 1 average price</th><th>Month 2 average price</th><th>Month 3 average price</th><th>Month 4 average price</th><th>Month 5 average price</th><th>Month 6 average price</th><th>CCM triggered? Yes or No</th></tr>
<tr><td>Feb-23</td><td>x</td><td>£60.00</td><td>Aug, Sep, Oct, Nov, Dec, Jan</td><td>£80.1</td><td>£75.2</td><td>£70.3</td><td>£65.4</td><td>£60.5</td><td>-</td><td>No</td></tr>
</table></div></main></body></html>"""


def test_ukets_monthly_reading_rule_maps_each_rows_months_back_from_the_row(tmp_path: Path):
    path = tmp_path / "ccm.html"
    path.write_text(CCM_HTML)
    got = ukets_monthly.read(path)
    assert (
        got[(2021, 5)] == D("45.10")
        and got[(2021, 7)] == D("46.30")
        and got[(2021, 8)] == D("52.00")
    )
    assert got[(2022, 8)] == D("80.1") and got[(2022, 12)] == D("60.5")
    assert (2023, 1) not in got  # a cell that is not a price is skipped
    profile = ukets_monthly.format_profile(path)
    assert [t["rows"] for t in profile["tables"]] == [2, 1]
    assert profile["tables"][1]["average_price_forms"] == {"pounds": 5, "other": 1}


def test_ukets_monthly_stops_on_a_disagreement_or_a_misprinted_period(tmp_path: Path):
    path = tmp_path / "ccm.html"
    path.write_text(
        CCM_HTML.replace(
            "<td>£47.20</td><td>£46.30</td><td>£52.00</td>",
            "<td>£47.21</td><td>£46.30</td><td>£52.00</td>",
        )
    )
    with pytest.raises(ValueError, match="prints"):
        ukets_monthly.read(path)
    path.write_text(CCM_HTML.replace("May, June, July", "Apr, May, June"))
    with pytest.raises(ValueError, match="period"):
        ukets_monthly.read(path)
    assert ukets_monthly.months_before(2023, 2, 6) == [
        (2022, 8),
        (2022, 9),
        (2022, 10),
        (2022, 11),
        (2022, 12),
        (2023, 1),
    ]
