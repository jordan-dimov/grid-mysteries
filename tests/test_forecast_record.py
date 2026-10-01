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
    realised = [r for r in REALISED if r.scope == "fleet"] + [
        fig("grid24", "realised", "GRID portfolio", "50000", 2024, published=date(2025, 4, 22))
    ]
    f = fig("f", "forecast", "4h", "90000", 2024, published=date(2023, 11, 1))
    row = fr.compare(f, fr.realised_index(realised), today=TODAY)
    assert row.status == "scope mismatch"
    assert row.realised == Decimal("55000")
    assert row.realised_scope == "fleet"  # the fleet outturn first, GRID's listed beside it
    assert row.signed_error is None and row.absolute_error_pct is None
    assert "never adjusted" in row.note and "GRID portfolio" in row.note


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


# ------------------------------------------------- the reading rules R-R


def page(
    figures: list[tuple[str, str]],
    *,
    url: str = "https://modoenergy.com/research/en/test-page",
    title: str = "A test page - Research | Modo Energy",
    published: str = "2025-06-09T10:00:00+0000",
    fmt: str = "html",
) -> dict:
    out = []
    offset = 0
    for printed, sentence in figures:
        out.append({"as_printed": printed, "sentence": sentence, "offset": offset, "shape": ""})
        offset += len(sentence) + 1
    return {
        "url": url,
        "sha256": "ab" * 32,
        "format": fmt,
        "title": title,
        "dates": {"meta:article:published_time": [published]} if published else {},
        "figures": out,
    }


def rules(p: dict, **kw) -> list[str]:
    return [r.rule for r in fr.read_page(p, publisher="Modo Energy", **kw)]


def test_rr0_json_title_pdf_and_duplicates_are_declined() -> None:
    p = page(
        [
            ("£60k/MW/year", '{"@type":"Article","description":"revenues £60k/MW/year"}'),
            ("£60k/MW/year", "A test page - Research | Modo Energy"),
            ("£60k/MW/year", "Batteries in Great Britain earned £60k/MW/year in May 2025."),
            ("£60k/MW/year", "Batteries in Great Britain earned £60k/MW/year in May 2025."),
        ],
        title="A test page - Research | Modo Energy",
    )
    assert rules(p) == [
        "R-R0 JSON payload",
        "R-R0 title or navigation duplicate",
        "R-R5 monthly figure",
        "R-R5 monthly figure",
    ]
    pdf = page([("£60k/MW/year", "anything")], fmt="pdf", published="")
    assert rules(pdf)[0].startswith("R-R0 PDF")


def test_rr1_and_rr6_publication_date_precedence_and_the_2023_cutoff() -> None:
    p = page([("£60k/MW/year", "In 2021, the index averaged £60k/MW/year.")], published="")
    p["dates"] = {"json:dateCreated": ["2022-12-31 07:00:00"], "json:datePublished": ["2023-01-02"]}
    assert fr.publication_date(p) == date(2023, 1, 2)
    p["dates"] = {"json:dateCreated": ["2022-12-31 07:00:00"]}
    assert rules(p) == ["R-R6 published before 2023"]
    p["dates"] = {"text:rns-header": ["23 May 2023"]}
    assert fr.publication_date(p) == date(2023, 5, 23)
    p["dates"] = {"pdf:CreationDate": ["Tue Apr 21 11:39:36 2026 BST"]}
    assert fr.publication_date(p) == date(2026, 4, 21)
    p["dates"] = {}
    assert rules(p) == ["R-R1 no publication date declared"]


def test_rr2_units_multipliers_ranges_hourly_and_no_period() -> None:
    s = "Batteries in Great Britain earned {} in May 2025."
    p = page(
        [
            ("£60k/MW/year", s.format("£60k/MW/year")),
            ("£60/kW/year", s.format("£60/kW/year")),
            ("£85/MWh", s.format("£85/MWh")),
            ("£6.85/MW/hr", s.format("£6.85/MW/hr")),
            ("£60-70k/MW/year", s.format("£60-70k/MW/year")),
            ("£60k/MW", s.format("£60k/MW")),
            ("£60k/MW", "In May 2025 batteries in Great Britain earned £60k/MW (annualised)."),
            ("£5k/MW/month", s.format("£5k/MW/month")),
        ]
    )
    got = fr.read_page(p, publisher="Modo Energy")
    assert [r.rule for r in got] == [
        "R-R5 monthly figure",
        "R-R5 monthly figure",
        "R-R2 a price per MWh, not a revenue per MW",
        "R-R2 an hourly rate",
        "R-R2 range, not a point figure",
        "R-R2 no period unit",
        "R-R5 monthly figure",
        "R-R2 a monthly rate",
    ]
    assert got[0].monthly is not None and got[0].monthly[2] == Decimal("60000")
    assert got[1].monthly is not None and got[1].monthly[2] == Decimal("60000")


def test_rr2_a_change_and_the_starting_point_of_a_change_are_not_levels() -> None:
    p = page(
        [
            ("£5k/MW/year", "Battery revenues reduced by £5k/MW/year in April 2025."),
            (
                "£59k/MW/year",
                "Battery revenues rise from around £59k/MW/year to £85k/MW/year by 2030, "
                "we forecast.",
            ),
            (
                "£85k/MW/year",
                "Battery revenues rise from around £59k/MW/year to £85k/MW/year by 2030, "
                "we forecast.",
            ),
            ("£60k/MW/year", "In April 2025, revenues in Great Britain fell to £60k/MW/year."),
        ]
    )
    assert rules(p) == [
        "R-R2 a change, not a level",
        "R-R2 the starting point of a stated change, not its level",
        "R-R5 endyear figure, basis forecast",
        "R-R5 monthly figure",
    ]


def test_rr3_components_subsets_fleet_fallback_durations_and_the_cm_qualifier() -> None:
    p = page(
        [
            ("£20k/MW/year", "Wholesale revenues averaged £20k/MW/year in May 2025."),
            (
                "£120k/MW/year",
                "Wishaw was the highest-earning battery, reaching £120k/MW/year in May 2025.",
            ),
            (
                "£60k/MW/year",
                "Revenues in Great Britain (GB) averaged £60k/MW/year in 2024, "
                "but the top systems earned more.",
            ),
            ("£70k/MW/year", "Two-hour systems earned £70k/MW/year in May 2025."),
            (
                "£55k/MW/year",
                "The index reported £55k/MW/year in May 2025 (excluding Capacity Market revenues).",
            ),
            ("£50k/MW/year", "Something earned £50k/MW/year in May 2025."),
        ],
        title="A page with no month in its title",
    )
    got = fr.read_page(p, publisher="Modo Energy")
    assert [r.rule for r in got] == [
        "R-R3 a revenue component, not the total",
        "R-R3 a named asset or subset, not the population",
        "R-R5 annual figure, basis realised",
        "R-R5 monthly figure",
        "R-R5 monthly figure",
        "R-R3 no population named in the clause",
    ]
    assert got[2].figure is not None and got[2].figure.scope == "fleet"
    assert got[3].monthly is not None and got[3].monthly[3] == "2h"
    assert got[4].monthly is not None and got[4].monthly[3] == "fleet-excl-cm"


def test_rr4_potential_contracted_and_forecast_words() -> None:
    p = page(
        [
            (
                "£60k/MW/year",
                "We estimate a toll of £60k/MW/year would make the project viable in 2027.",
            ),
            ("£90k/MW/year", "Revenues reach £90k/MW/year for a two-hour battery in 2030."),
            (
                "£90k/MW/year",
                "We forecast revenues of £90k/MW/year for a two-hour battery in 2030.",
            ),
        ]
    )
    assert rules(p) == [
        "R-R4 potential, required, contracted or assumed, not a forecast or an outturn",
        "R-R4 a future year with no forecast word",
        "R-R5 annual figure, basis forecast",
    ]


def test_rr5_the_period_nearest_the_figure_and_the_page_month() -> None:
    monthly = page(
        [
            (
                "£60k/MW/year",
                "Revenues in Great Britain fell to £60k/MW/year in May 2025, "
                "down from £70k/MW/year in April.",
            ),
            (
                "£70k/MW/year",
                "Revenues in Great Britain fell to £60k/MW/year in May 2025, "
                "down from £70k/MW/year in April.",
            ),
            (
                "£60.4k/MW/year",
                "Batteries earned £60.4k/MW/year in May, the lowest since July 2024.",
            ),
            ("£50k/MW/year", "The previous low was £50k/MW/year in July 2024."),
        ],
        title="ME BESS GB: revenues fall to £60k/MW/year in May 2025 - Research | Modo Energy",
    )
    got = fr.read_page(monthly, publisher="Modo Energy")
    assert [r.rule for r in got] == [
        "R-R7 the same month's figure, printed less precisely than another string on the page",
        "R-R2 the starting point of a stated change, not its level",
        "R-R5 monthly figure",
        "R-R5 another month than the page's own",
    ]
    assert got[2].monthly == (2025, 5, Decimal("60400"), "fleet")
    # a title month without a year is its most recent occurrence before publication
    assert fr.title_month("Revenues reach a yearly high in October", date(2024, 11, 6)) == (
        2024,
        10,
    )
    assert fr.title_month("Revenues in January", date(2024, 2, 5)) == (2024, 1)
    # without a page month, a month is read only within three months of publication
    older = page(
        [("£60k/MW/year", "Batteries in Great Britain earned £60k/MW/year in January.")],
        title="A page with no month",
        published="2025-06-09T10:00:00+0000",
    )
    assert rules(older) == ["R-R5 a month not current to the page"]


def test_rr5_annual_horizon_end_year_in_year_partial_and_fund_title() -> None:
    p = page(
        [
            ("£60k/MW/year", "In 2024, the index averaged £60k/MW/year."),
            (
                "£90k/MW/year",
                "Revenues increase to £90k/MW/year for a two-hour battery out to 2030.",
            ),
            (
                "£85k/MW/year",
                "A 2-hour battery is projected to earn £85k/MW/year at the end of 2025.",
            ),
            (
                "£70k/MW/year",
                "So far in 2025, batteries in Great Britain have averaged £70k/MW/year.",
            ),
            ("£65k/MW/year", "In H1 2025, batteries in Great Britain earned £65k/MW/year."),
            ("£75k/MW/year", "The index averaged £75k/MW/year in 2025."),
        ]
    )
    got = fr.read_page(p, publisher="Modo Energy")
    assert [r.rule for r in got] == [
        "R-R5 annual figure, basis realised",
        "R-R5 horizon figure, basis forecast",
        "R-R5 endyear figure, basis forecast",
        "R-R5 a partial period (half, quarter, season or to date)",
        "R-R5 a partial period (half, quarter, season or to date)",
        "R-R5 the year of publication, not complete",
    ]
    assert (got[1].figure.period_start, got[1].figure.period_end) == (2026, 2030)  # type: ignore[union-attr]
    assert (got[2].figure.period_start, got[2].figure.period_end) == (2025, 2025)  # type: ignore[union-attr]
    fund = page(
        [
            (
                "£67.3k/MW/year",
                "The portfolio generated £67.3k/MW/year, up 29 % from £52.1k/MW/year in FY2024.",
            ),
            (
                "£52.1k/MW/year",
                "The portfolio generated £67.3k/MW/year, up 29 % from £52.1k/MW/year in FY2024.",
            ),
            (
                "£40,000 per MW/yr",
                "Average revenue of £40,000 per MW/yr (31 March 2024: £45,000 per MW/yr).",
            ),
        ],
        url="https://www.investegate.co.uk/announcement/rns/x--grid/full-year-results/1",
        title="Full-Year Results to 31 December 2025 | Company Announcement | Investegate",
        published="2026-04-21T07:00:00",
    )
    got = fr.read_page(fund, publisher="GRID (fund RNS)", portfolio_scope="GRID portfolio")
    assert [r.rule for r in got] == [
        "R-R5 annual figure, basis realised",
        "R-R2 the starting point of a stated change, not its level",
        "R-R5 period not stated",
    ]
    assert got[0].figure.period_start == 2025 and got[0].figure.scope == "GRID portfolio"  # type: ignore[union-attr]


def test_rr7_a_page_whose_strings_disagree_beyond_rounding_reads_none() -> None:
    p = page(
        [
            ("£60k/MW/year", "Batteries in Great Britain earned £60k/MW/year in May 2025."),
            ("£60/MW/year", "Battery energy storage systems earned £60/MW/year in May 2025."),
        ],
        title="ME BESS GB: revenues in May 2025",
    )
    assert all(
        r.rule.startswith("R-R7 the page prints figures")
        for r in fr.read_page(p, publisher="Modo Energy")
    )


def test_rs4_twelve_months_mean_published_figure_precedence_and_restatements() -> None:
    readings = []
    for m in range(1, 13):
        readings += fr.read_page(
            page(
                [
                    (
                        f"£{50 + m}k/MW/year",
                        f"Batteries in Great Britain earned £{50 + m}k/MW/year in "
                        f"{list(fr.MONTHS)[m - 1].title()} 2025.",
                    )
                ],
                title=f"ME BESS GB: revenues in {list(fr.MONTHS)[m - 1].title()} 2025",
                published=f"2025-{m:02d}-28T10:00:00+0000"
                if m < 12
                else "2026-01-08T10:00:00+0000",
                url=f"https://modoenergy.com/research/en/m{m}",
            ),
            publisher="Modo Energy",
        )
    # a later page restates June beyond rounding, and another restates July within rounding
    readings += fr.read_page(
        page(
            [("£70k/MW/year", "Batteries in Great Britain earned £70k/MW/year in June 2025.")],
            title="June 2025 revisited",
            published="2025-08-01T10:00:00+0000",
            url="https://modoenergy.com/research/en/june-again",
        ),
        publisher="Modo Energy",
    )
    readings += fr.read_page(
        page(
            [("£57.4k/MW/year", "Batteries in Great Britain earned £57.4k/MW/year in July 2025.")],
            title="July 2025 revisited",
            published="2025-09-01T10:00:00+0000",
            url="https://modoenergy.com/research/en/july-again",
        ),
        publisher="Modo Energy",
    )
    means, detail, restated = fr.annual_from_months(readings, publisher="Modo Energy")
    assert len(means) == 1 and means[0].period_start == 2025 and means[0].basis == "realised"
    assert means[0].figure_id == "mean-12m:fleet:2025"
    # June: the later 70,000 (beyond rounding, latest published); July: the more precise 57,400
    assert [x["month"] for x in restated] == [6]
    values = detail[0]["values"]
    assert values[5] == "70000" and values[6] == "57400"
    expected = (
        sum(Decimal(50 + m) * 1000 for m in range(1, 13))
        - Decimal(56000)
        + Decimal(70000)
        - Decimal(57000)
        + Decimal(57400)
    ) / 12
    assert means[0].value == expected.quantize(Decimal("1"))
    # a figure published for the year outranks the mean, whatever its date
    published = fig("annual-2025", "realised", "fleet", "61000", 2025, published=date(2025, 2, 1))
    index = fr.realised_index(means + [published])
    assert fr.realised_for("fleet", 2025, index) is published


def test_pipeline_runs_end_to_end_on_synthetic_pages_and_f1_fires_without_a_scorable_vintage() -> (
    None
):
    modo = [
        page(
            [
                (
                    "£90k/MW/year",
                    "Revenues increase to £90k/MW/year for a two-hour battery out to 2030.",
                )
            ],
            published="2025-01-13T10:00:00+0000",
            url="https://modoenergy.com/research/en/f1",
        ),
        page(
            [("£60k/MW/year", "In 2024, the index averaged £60k/MW/year.")],
            published="2025-02-18T10:00:00+0000",
            url="https://modoenergy.com/research/en/a1",
        ),
        page(
            [("£99k/MW/Jahr", "irrelevant")],
            published="2025-02-18T10:00:00+0000",
            url="https://modoenergy.com/research/de/a1",
        ),
    ]
    result = fr.pipeline(modo, [], today=date(2026, 10, 1))
    assert [f.basis for f in result["figures"]] == ["forecast", "realised"]
    assert result["comparisons"][0].status == "not yet scorable"
    assert result["comparisons"][0].scorable_after == date(2031, 1, 1)
    assert result["falsifiers"]["F1"] is True
    assert result["propositions"]["P-A"]["verdict"] == "undecided"
    assert (
        result["falsifiers"]["F2"]["per_year_strings"] == 2
        and result["falsifiers"]["F2"]["fires"] is False
    )


def test_rr4f_a_fund_citing_a_curve_for_a_future_year_is_the_funds_forecast_with_its_source() -> (
    None
):
    fund = page(
        [
            (
                "£75k/MW/year",
                "The valuation assumes merchant revenues of £75k/MW/year for two-hour assets "
                "in 2024, based on the Aurora central case.",
            ),
            (
                "£60k/MW/year",
                "The valuation assumed revenues of £60k/MW/year for the portfolio in 2021.",
            ),
            (
                "£52k/MW/year",
                "Third-party forecasters anticipate £52k/MW/year for the portfolio in 2024.",
            ),
            (
                "£58k/MW/year",
                "Third-party forecasters are anticipating 2026 merchant revenue levels for 2-hour "
                "assets of c.£58k/MW/year.",
            ),
        ],
        url="https://www.investegate.co.uk/announcement/rns/x--grid/nav/1",
        title="Net Asset Value | Company Announcement | Investegate",
        published="2022-03-01T07:00:00",
    )
    got = fr.read_page(fund, publisher="GRID (fund RNS)", portfolio_scope="GRID portfolio")
    assert [r.rule for r in got] == [
        "R-R5 annual figure, basis forecast, cited by the fund (aurora)",
        "R-R4 an assumption for a past period, not an outturn",
        "R-R5 annual figure, basis forecast, cited by the fund (third-party)",
        "R-R5 annual figure, basis forecast, cited by the fund (third-party)",
    ]
    assert got[3].figure.scope == "2h" and got[3].figure.period_start == 2026  # type: ignore[union-attr]
    assert got[0].figure.scope == "2h" and got[0].figure.cited_source == "aurora"  # type: ignore[union-attr]
    assert got[2].figure.scope == "GRID portfolio"  # type: ignore[union-attr]
    assert got[0].figure.publisher == "GRID (fund RNS)"  # type: ignore[union-attr]


def test_rr0_and_rr6_for_fund_pdfs_in_reading_order_and_the_2021_window() -> None:
    pdf = page(
        [
            (
                "£60k/MW/year",
                "Revenues of £60k/MW/year were assumed for 2024 GRID Annual Report 2022 "
                "Strategic report",
            ),
            ("£60k/MW/year", "Revenues of £60k/MW/year were assumed for 2024."),
        ],
        fmt="pdf (pdftotext reading order (no -layout))",
        published="",
    )
    pdf["dates"] = {"json:dateCreated": ["2022-04-20"]}
    got = fr.read_page(pdf, publisher="GRID (fund RNS)", portfolio_scope="GRID portfolio")
    assert [r.rule for r in got] == [
        "R-R0 PDF sentence glued to page furniture",
        "R-R5 annual figure, basis forecast, cited by the fund (source unnamed)",
    ]
    layout = dict(pdf, format="pdf")
    first = fr.read_page(layout, publisher="GRID (fund RNS)", portfolio_scope="GRID portfolio")[0]
    assert first.rule.startswith("R-R0 PDF: layout")
    early = dict(pdf, dates={"json:dateCreated": ["2020-12-31"]})
    first = fr.read_page(early, publisher="GRID (fund RNS)", portfolio_scope="GRID portfolio")[0]
    assert first.rule == "R-R6 published before 2021"


def test_propositions_are_reported_per_publisher_beside_the_whole() -> None:
    figures = REALISED + [
        fig("a", "forecast", "2h", "73800", 2024, published=date(2023, 11, 1)),
        fig("b", "forecast", "2h", "60000", 2024, published=date(2023, 10, 1), publisher="GRID"),
    ]
    rows = fr.comparisons(figures, today=TODAY)
    props = fr.propositions(figures, rows)
    assert props["P-A"]["verdict"] == "fails"
    assert props["per_publisher"]["Modo Energy"]["P-A"]["verdict"] == "holds"
    assert props["per_publisher"]["GRID"]["P-A"]["verdict"] == "fails"


def test_rr2_a_string_repeated_verbatim_in_one_sentence_is_read_at_its_own_place() -> None:
    sentence = (
        "The adviser revised its assumptions for 2024 from £60,000 per MW/yr to £50,000 per MW/yr "
        "and for 2025 from £50,000 per MW/yr to £45,000 per MW/yr."
    )
    fund = page(
        [
            ("£60,000 per MW/yr", sentence),
            ("£50,000 per MW/yr", sentence),
            ("£50,000 per MW/yr", sentence),
            ("£45,000 per MW/yr", sentence),
        ],
        url="https://www.investegate.co.uk/announcement/rns/x--heit/nav/1",
        title="Trading Update | Company Announcement | Investegate",
        published="2023-05-23T07:00:00",
    )
    got = fr.read_page(fund, publisher="HEIT", portfolio_scope="HEIT portfolio")
    assert [r.rule for r in got] == [
        "R-R2 the starting point of a stated change, not its level",
        "R-R5 annual figure, basis forecast, cited by the fund (source unnamed)",
        "R-R2 the starting point of a stated change, not its level",
        "R-R5 annual figure, basis forecast, cited by the fund (source unnamed)",
    ]
    assert [r.figure.period_start for r in got if r.figure] == [2024, 2025]


def test_rr0_the_same_figure_in_an_rns_and_its_report_of_one_day_is_one_publication() -> None:
    a = fig("a", "forecast", "2h", "70000", 2028, published=date(2025, 9, 24), url="https://x/rns")
    b = fig("b", "forecast", "2h", "70000", 2028, published=date(2025, 9, 24), url="https://x/pdf")
    c = fig("c", "forecast", "2h", "71000", 2028, published=date(2025, 9, 24), url="https://x/pdf")
    kept, duplicates = fr.dedupe_same_day([b, a, c])
    assert sorted(f.figure_id for f in kept) == ["b", "c"]  # the first by URL is kept
    assert duplicates == [{"figure_id": "a", "same_as": "b", "url": "https://x/rns"}]
