import json
from datetime import UTC, datetime
from decimal import Decimal as D
from pathlib import Path

import pytest

from grid_mysteries.investigations.household_desk import LONDON, Rate
from grid_mysteries.sources import octopus

API = "https://api.octopus.energy/v1"


def test_url_builders_follow_the_documented_endpoints() -> None:
    assert octopus.tariff_code("AGILE-24-10-01", "C") == "E-1R-AGILE-24-10-01-C"
    with pytest.raises(ValueError):
        octopus.tariff_code("AGILE-24-10-01", "I")  # no region I
    assert octopus.products_url(2) == f"{API}/products/?page=2"
    assert octopus.product_url("GO-VAR-22-10-14") == f"{API}/products/GO-VAR-22-10-14/"
    url = octopus.unit_rates_url(
        "AGILE-24-10-01",
        "E-1R-AGILE-24-10-01-E",
        datetime(2026, 5, 31, 22, 0, tzinfo=LONDON),
        "2026-09-01T00:00Z",
        page=2,
    )
    assert url == (
        f"{API}/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-E/"
        "standard-unit-rates/?period_from=2026-05-31T21:00Z&period_to=2026-09-01T00:00Z"
        "&page_size=1500&page=2"
    )
    assert "/standing-charges/?" in octopus.standing_charges_url(
        "AGILE-24-10-01", "E-1R-AGILE-24-10-01-E", "2026-01-01T00:00Z", "2026-03-01T00:00Z"
    )


def test_agile_rates_are_known_at_16_00_on_the_day_their_agile_day_starts() -> None:
    midday = datetime(2026, 6, 24, 12, 0, tzinfo=LONDON)
    assert octopus.agile_published_at(midday) == datetime(2026, 6, 23, 16, 0, tzinfo=LONDON)
    late = datetime(2026, 6, 24, 23, 30, tzinfo=LONDON)  # already the next Agile day
    assert octopus.agile_published_at(late) == datetime(2026, 6, 24, 16, 0, tzinfo=LONDON)
    early = datetime(2026, 6, 24, 22, 30, tzinfo=LONDON)
    assert octopus.agile_published_at(early) == datetime(2026, 6, 23, 16, 0, tzinfo=LONDON)
    assert octopus.publication_rule("AGILE-24-10-01") is octopus.agile_published_at
    assert octopus.publication_rule("GO-VAR-22-10-14")(midday) is None


def page(rows, following=None):
    return {"count": len(rows), "next": following, "previous": None, "results": rows}


def row(valid_from, valid_to, exc, inc):
    return {
        "value_exc_vat": exc,
        "value_inc_vat": inc,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "payment_method": None,
    }


def test_import_reads_inc_vat_and_export_refuses_a_vat_bearing_row() -> None:
    rows = [row("2026-06-24T10:00:00Z", "2026-06-24T10:30:00Z", 20.0, 21.0)]
    (rate,) = octopus.parse_rates(
        page(rows), side="import", published_at=octopus.agile_published_at
    )
    assert rate == Rate(
        datetime(2026, 6, 24, 10, 0, tzinfo=UTC),
        datetime(2026, 6, 24, 10, 30, tzinfo=UTC),
        D("21.0"),
        datetime(2026, 6, 23, 16, 0, tzinfo=LONDON),
    )
    with pytest.raises(ValueError, match="carries VAT"):
        octopus.parse_rates(page(rows), side="export", published_at=octopus.known_indefinitely)
    export = [row("2026-06-24T10:00:00Z", None, 15.0, 15.0)]
    (rate,) = octopus.parse_rates(
        page(export), side="export", published_at=octopus.known_indefinitely
    )
    assert rate.pence_per_kwh == D("15.0") and rate.valid_to is None and rate.published_at is None
    with pytest.raises(ValueError, match="lacks"):
        octopus.parse_rates(
            page([{"valid_from": "x"}]), side="import", published_at=octopus.known_indefinitely
        )
    with pytest.raises(ValueError, match="results"):
        octopus.parse_rates({"data": []}, side="import", published_at=octopus.known_indefinitely)


def test_load_rates_merges_pages_dedupes_and_refuses_overlaps(tmp_path: Path) -> None:
    a = tmp_path / "page-1.json"
    b = tmp_path / "page-2.json"
    newer = [
        row("2026-06-24T10:30:00Z", "2026-06-24T11:00:00Z", 10.0, 10.5),
        row("2026-06-24T10:00:00Z", "2026-06-24T10:30:00Z", 20.0, 21.0),
    ]
    older = [
        row("2026-06-24T10:00:00Z", "2026-06-24T10:30:00Z", 20.0, 21.0),  # repeated across pages
        row("2026-06-24T09:30:00Z", "2026-06-24T10:00:00Z", 30.0, 31.5),
    ]
    a.write_text(json.dumps(page(newer, "next-url")))
    b.write_text(json.dumps(page(older)))
    rates = octopus.load_rates([a, b], side="import", published_at=octopus.known_indefinitely)
    assert [r.pence_per_kwh for r in rates] == [D("31.5"), D("21.0"), D("10.5")]
    assert octopus.next_page(json.loads(a.read_text())) == "next-url"
    assert octopus.next_page(json.loads(b.read_text())) is None
    b.write_text(json.dumps(page([row("2026-06-24T10:15:00Z", "2026-06-24T10:45:00Z", 1, 1)])))
    with pytest.raises(ValueError, match="overlapping"):
        octopus.load_rates([a, b], side="import", published_at=octopus.known_indefinitely)
    b.write_text(
        json.dumps(page([row("2026-06-24T10:00:00Z", "2026-06-24T10:30:00Z", 20.0, 99.0)]))
    )
    with pytest.raises(ValueError, match="conflicting"):
        octopus.load_rates([a, b], side="import", published_at=octopus.known_indefinitely)


def test_tariff_codes_are_read_from_the_product_document_not_guessed() -> None:
    document = {
        "code": "AGILE-24-10-01",
        "single_register_electricity_tariffs": {
            "_C": {"direct_debit_monthly": {"code": "E-1R-AGILE-24-10-01-C"}},
            "_E": {
                "direct_debit_monthly": {"code": "E-1R-AGILE-24-10-01-E"},
                "varying": {"code": "E-1R-AGILE-24-10-01-E"},
            },
        },
    }
    assert octopus.tariff_codes_in_product(document, "C") == ["E-1R-AGILE-24-10-01-C"]
    assert octopus.tariff_codes_in_product(document, "E") == ["E-1R-AGILE-24-10-01-E"]
    assert octopus.tariff_codes_in_product(document, "J") == []
    assert octopus.tariff_codes_in_product({}, "C") == []
