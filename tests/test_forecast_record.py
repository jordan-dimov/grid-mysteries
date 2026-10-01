"""022's scoring rules: scorability, the comparison, scope mismatch, the
revision direction and the three propositions, on synthetic figures."""

from datetime import date
from decimal import Decimal

import pytest

from grid_mysteries.investigations import forecast_record as fr

TODAY = date(2026, 10, 1)


def fig(
    fid: str,
    basis: str,
    scope: str,
    value: str,
    start: int,
    end: int | None = None,
    *,
    published: date,
    publisher: str = "Modo Energy",
    url: str | None = None,
) -> fr.Figure:
    return fr.Figure(
        figure_id=fid,
        publisher=publisher,
        published_on=published,
        source_url=url or f"https://example.invalid/{published.isoformat()}",
        source_sha256="0" * 64,
        basis=basis,  # type: ignore[arg-type]
        scope=scope,
        value=Decimal(value),
        period_start=start,
        period_end=end if end is not None else start,
        as_printed=f"£{value}/MW/year",
    )


REALISED = [
    fig("r24-2h", "realised", "2h", "61500", 2024, published=date(2025, 1, 20)),
    fig("r25-2h", "realised", "2h", "80000", 2025, published=date(2026, 1, 15)),
    fig("r24-fleet", "realised", "fleet", "55000", 2024, published=date(2025, 1, 20)),
    fig("r25-fleet", "realised", "fleet", "70000", 2025, published=date(2026, 1, 15)),
]


def test_rs1_a_year_counts_only_if_the_forecast_was_published_before_it_began() -> None:
    f = fig("f", "forecast", "2h", "70000", 2024, 2026, published=date(2024, 6, 1))
    assert fr.eligible_years(f) == [2025, 2026]
    f_before = fig("f2", "forecast", "2h", "70000", 2024, published=date(2023, 12, 31))
    assert fr.eligible_years(f_before) == [2024]


def test_an_in_year_figure_is_never_scored_and_says_so() -> None:
    f = fig("f", "forecast", "2h", "70000", 2024, published=date(2024, 6, 1))
    row = fr.compare(f, fr.realised_index(REALISED), today=TODAY)
    assert row.status == "in-year, never scored"
    assert row.signed_error is None and row.realised is None


def test_rc_signed_error_is_forecast_minus_realised_in_pounds_and_percent() -> None:
    f = fig("f", "forecast", "2h", "73800", 2024, published=date(2023, 11, 1))
    row = fr.compare(f, fr.realised_index(REALISED), today=TODAY)
    assert row.status == "scored"
    assert row.realised == Decimal("61500")
    assert row.signed_error == Decimal("12300")
    assert row.absolute_error == Decimal("12300")
    assert row.signed_error_pct == Decimal("20.0")
    assert row.absolute_error_pct == Decimal("20.0")
    assert row.realised_ids == ("r24-2h",)
    under = fig("g", "forecast", "2h", "50000", 2024, published=date(2023, 11, 1))
    row2 = fr.compare(under, fr.realised_index(REALISED), today=TODAY)
    assert row2.signed_error == Decimal("-11500")
    assert row2.signed_error_pct == Decimal("-18.7")
    assert row2.absolute_error_pct == Decimal("18.7")


def test_rs2_a_multi_year_figure_scores_against_the_mean_once_every_year_is_realised() -> None:
    f = fig("f", "forecast", "2h", "75000", 2024, 2025, published=date(2023, 11, 1))
    row = fr.compare(f, fr.realised_index(REALISED), today=TODAY)
    assert row.status == "scored"
    assert row.realised == Decimal("70750")
    assert row.signed_error == Decimal("4250")
    assert row.note == "mean of the realised years"
    later = fig("g", "forecast", "2h", "75000", 2024, 2026, published=date(2023, 11, 1))
    row2 = fr.compare(later, fr.realised_index(REALISED), today=TODAY)
    assert row2.status == "not yet scorable"
    assert row2.scorable_after == date(2027, 1, 1)
    assert "2026" in row2.note


def test_rs3_the_latest_published_realised_figure_is_read() -> None:
    index = fr.realised_index(
        REALISED
        + [fig("r24-2h-revised", "realised", "2h", "62000", 2024, published=date(2025, 6, 1))]
    )
    assert fr.realised_for("2h", 2024, index) is not None
    assert fr.realised_for("2h", 2024, index).figure_id == "r24-2h-revised"  # type: ignore[union-attr]
    assert fr.realised_for("8h", 2024, index) is None


def test_rm_a_fleet_realised_figure_against_a_duration_forecast_is_a_mismatch_never_adjusted() -> (
    None
):
    realised = [r for r in REALISED if r.scope == "fleet"]
    f = fig("f", "forecast", "4h", "90000", 2024, published=date(2023, 11, 1))
    row = fr.compare(f, fr.realised_index(realised), today=TODAY)
    assert row.status == "scope mismatch"
    assert row.realised == Decimal("55000")
    assert row.realised_scope == "fleet"
    assert row.signed_error is None and row.absolute_error_pct is None
    assert "never adjusted" in row.note


def test_not_yet_scorable_dates_the_day_the_period_ends() -> None:
    f = fig("f", "forecast", "2h", "90000", 2026, published=date(2025, 11, 1))
    row = fr.compare(f, fr.realised_index(REALISED), today=TODAY)
    assert row.status == "not yet scorable"
    assert row.scorable_after == date(2027, 1, 1)
    table = fr.not_yet_scorable_table([row])
    assert table[0]["period"] == "2026" and table[0]["scorable_after"] == "2027-01-01"
    past = fig("g", "forecast", "2h", "90000", 2024, published=date(2023, 11, 1))
    row2 = fr.compare(past, fr.realised_index([]), today=TODAY)
    assert row2.status == "not yet scorable" and row2.scorable_after == TODAY


def test_comparisons_make_one_row_per_forecast_in_publication_order() -> None:
    figures = REALISED + [
        fig("b", "forecast", "2h", "70000", 2025, published=date(2024, 11, 1)),
        fig("a", "forecast", "2h", "73800", 2024, published=date(2023, 11, 1)),
        fig("c", "forecast", "2h", "90000", 2026, published=date(2025, 11, 1)),
    ]
    rows = fr.comparisons(figures, today=TODAY)
    assert [r.forecast_id for r in rows] == ["a", "b", "c"]
    assert [r.status for r in rows] == ["scored", "scored", "not yet scorable"]


def test_pa_holds_only_when_every_scorable_vintage_overstated_its_first_year() -> None:
    over = [
        fig("a", "forecast", "2h", "73800", 2024, published=date(2023, 11, 1)),
        fig("b", "forecast", "2h", "85000", 2025, published=date(2024, 11, 1)),
    ]
    rows = fr.comparisons(REALISED + over, today=TODAY)
    pa = fr.proposition_a(rows)
    assert pa["verdict"] == "holds" and pa["scorable_vintages"] == 2
    under = fig("c", "forecast", "2h", "60000", 2025, published=date(2024, 12, 1))
    pa2 = fr.proposition_a(fr.comparisons(REALISED + over + [under], today=TODAY))
    assert pa2["verdict"] == "fails"
    assert pa2["falsified_by"] == ["Modo Energy 2024-12-01 https://example.invalid/2024-12-01"]
    assert fr.proposition_a([])["verdict"] == "undecided"


def test_pa_a_vintage_mixed_across_scopes_in_its_first_year_falsifies() -> None:
    url = "https://example.invalid/one-page"
    mixed = [
        fig("a", "forecast", "2h", "73800", 2024, published=date(2023, 11, 1), url=url),
        fig("b", "forecast", "fleet", "50000", 2024, published=date(2023, 11, 1), url=url),
    ]
    pa = fr.proposition_a(fr.comparisons(REALISED + mixed, today=TODAY))
    assert pa["verdict"] == "fails"
    assert list(pa["per_vintage"].values())[0]["reading"] == "mixed"


def test_pb_counts_vintages_whose_every_first_year_error_exceeds_twenty_percent() -> None:
    big = [
        fig("a", "forecast", "2h", "80000", 2024, published=date(2023, 11, 1)),  # +30.1 %
        fig("b", "forecast", "2h", "100000", 2025, published=date(2024, 11, 1)),  # +25.0 %
        fig("c", "forecast", "2h", "84000", 2025, published=date(2024, 12, 1)),  # +5.0 %
    ]
    pb = fr.proposition_b(fr.comparisons(REALISED + big, today=TODAY))
    assert pb["verdict"] == "holds" and pb["exceeding"] == 2 and pb["scorable_vintages"] == 3
    exactly_twenty = [fig("d", "forecast", "2h", "73800", 2024, published=date(2023, 10, 1))]
    pb2 = fr.proposition_b(fr.comparisons(REALISED + big[2:] + exactly_twenty, today=TODAY))
    assert pb2["verdict"] == "fails" and pb2["exceeding"] == 0  # 20.0 is not above 20
    assert fr.proposition_b([])["verdict"] == "undecided"


def test_pc_counts_direction_between_consecutive_vintages_of_the_same_scope_and_period() -> None:
    forecasts = [
        fig("a", "forecast", "2h", "80000", 2025, published=date(2023, 11, 1)),
        fig("b", "forecast", "2h", "70000", 2025, published=date(2024, 5, 1)),
        fig("c", "forecast", "2h", "72000", 2025, published=date(2024, 11, 1)),
        fig("d", "forecast", "2h", "65000", 2025, published=date(2025, 3, 1)),
        fig("e", "forecast", "fleet", "60000", 2025, published=date(2024, 11, 1)),  # alone
        fig("f", "forecast", "2h", "90000", 2026, published=date(2025, 3, 1)),  # another period
    ]
    pc = fr.proposition_c(forecasts)
    assert (pc["pairs"], pc["down"], pc["up"], pc["unchanged"]) == (3, 2, 1, 0)
    assert pc["verdict"] == "holds"
    assert [p["direction"] for p in pc["revisions"]] == ["down", "up", "down"]
    assert pc["revisions"][0]["change"] == "-10000"
    tie = fr.proposition_c(forecasts[:3])
    assert tie["verdict"] == "fails"  # one down, one up: not more often
    assert fr.proposition_c(forecasts[4:5])["verdict"] == "undecided"


def test_pc_reads_one_figure_per_vintage_and_lists_the_duplicates() -> None:
    url = "https://example.invalid/page"
    figures = [
        fig("a1", "forecast", "2h", "80000", 2025, published=date(2023, 11, 1), url=url),
        fig("a2", "forecast", "2h", "81000", 2025, published=date(2023, 11, 1), url=url),
        fig("b", "forecast", "2h", "70000", 2025, published=date(2024, 5, 1)),
    ]
    pc = fr.proposition_c(figures)
    assert pc["pairs"] == 1 and pc["revisions"][0]["duplicates_on_page"] == ["a2"]


def test_f3_require_unchanged_names_committed_rows_that_would_differ() -> None:
    committed = {"k1": "a", "k2": "b"}
    assert fr.require_unchanged(committed, {"k1": "a", "k2": "c", "k3": "d"}) == ["k2"]
    assert fr.require_unchanged(committed, {"k1": "a"}) == []


def test_a_figure_refuses_a_negative_value_or_a_backwards_period() -> None:
    with pytest.raises(ValueError):
        fig("x", "forecast", "2h", "-1", 2025, published=date(2024, 1, 1))
    with pytest.raises(ValueError):
        fig("y", "forecast", "2h", "1", 2026, 2025, published=date(2024, 1, 1))
