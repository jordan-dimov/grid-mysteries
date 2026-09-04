from pathlib import Path

import pytest

from grid_mysteries.corpus import RAW_ROOT
from grid_mysteries.sources import elexon

API = "https://data.elexon.co.uk/bmrs/api/v1"


def test_url_builders_produce_the_documented_endpoints() -> None:
    assert (
        elexon.bid_offer_url("2026-08-06", 9)
        == f"{API}/balancing/bid-offer/all?settlementDate=2026-08-06&settlementPeriod=9"
    )
    assert (
        elexon.acceptance_volumes_url("bid", "2026-08-06", 9)
        == f"{API}/balancing/settlement/indicative/volumes/all/bid/2026-08-06/9"
    )
    assert (
        elexon.acceptances_url("2026-08-06", 9)
        == f"{API}/balancing/acceptances/all?settlementDate=2026-08-06&settlementPeriod=9"
    )
    assert elexon.physical_url("MELS", "2026-08-06", 9) == (
        f"{API}/balancing/physical/all?dataset=MELS&settlementDate=2026-08-06&settlementPeriod=9"
    )
    assert (
        elexon.cashflows_url("offer", "2026-05-19")
        == f"{API}/balancing/settlement/indicative/cashflows/all/offer/2026-05-19"
    )


def test_day_stream_url_spans_exactly_one_day_and_filters_units() -> None:
    assert (
        elexon.day_stream_url("MDO", "2026-06-30")
        == f"{API}/datasets/MDO/stream?from=2026-06-30T00:00Z&to=2026-07-01T00:00Z"
    )
    # Month and year boundaries roll over; unit filters append in order.
    assert elexon.day_stream_url("PN", "2026-12-31", ["E_A-1", "E_B-1"]) == (
        f"{API}/datasets/PN/stream?from=2026-12-31T00:00Z&to=2027-01-01T00:00Z"
        "&bmUnit=E_A-1&bmUnit=E_B-1"
    )


def test_period_jobs_covers_the_full_per_period_pattern_in_order() -> None:
    jobs = elexon.period_jobs("2026-08-11", [1, 2])

    assert len(jobs) == 2 * 7
    first_period = jobs[:7]
    assert [dataset for dataset, _, _ in first_period] == [
        "BOD",
        "DISPTAV",
        "DISPTAV",
        "BOALF",
        "PN",
        "MELS",
        "MILS",
    ]
    day = RAW_ROOT / "2026-08-11"
    assert [path for _, _, path in first_period] == [
        day / "bod_p01.json",
        day / "disptav_offer_p01.json",
        day / "disptav_bid_p01.json",
        day / "boalf_p01.json",
        RAW_ROOT / "physical" / "2026-08-11" / "pn_p01.json",
        RAW_ROOT / "physical" / "2026-08-11" / "mels_p01.json",
        RAW_ROOT / "physical" / "2026-08-11" / "mils_p01.json",
    ]
    assert first_period[1][1] == elexon.acceptance_volumes_url("offer", "2026-08-11", 1)
    assert first_period[3][1] == elexon.acceptances_url("2026-08-11", 1)
    assert jobs[7][2] == day / "bod_p02.json"
    assert all(isinstance(path, Path) for _, _, path in jobs)


def test_period_jobs_honours_a_dataset_subset_and_its_order() -> None:
    jobs = elexon.period_jobs("2026-05-01", [48], datasets=("BOALF", "BOD", "DISPTAV"))

    assert [dataset for dataset, _, _ in jobs] == ["BOALF", "BOD", "DISPTAV", "DISPTAV"]
    assert elexon.period_jobs("2026-05-01", [], datasets=("BOD",)) == []
    with pytest.raises(ValueError, match="FUELINST"):
        elexon.period_jobs("2026-05-01", [1], datasets=("FUELINST",))


def test_bmunits_url_is_the_reference_endpoint() -> None:
    assert elexon.bmunits_url() == f"{API}/reference/bmunits/all"
