from decimal import Decimal

from grid_mysteries import corpus


def test_window_is_the_declared_seven_days() -> None:
    dates = corpus.window_dates()
    assert dates[0] == "2026-08-04"
    assert dates[-1] == "2026-08-10"
    assert len(dates) == corpus.WINDOW_DAYS == 7
    assert corpus.TOTAL_PERIODS == 336


def test_load_records_parses_floats_as_decimal(tmp_path) -> None:
    path = tmp_path / "artefact.json"
    path.write_text('{"data": [{"price": 71.25, "volume": 18}]}')

    [record] = corpus.load_records(path)

    assert record["price"] == Decimal("71.25")
    assert isinstance(record["price"], Decimal)
    assert record["volume"] == 18


def test_artefact_paths_follow_the_pinned_layout() -> None:
    assert str(corpus.window_path("bod", "2026-08-06", 9)).endswith(
        "data/raw/elexon/2026-08-06/bod_p09.json"
    )
    assert str(corpus.physical_path("MELS", "2026-08-06", 29)).endswith(
        "data/raw/elexon/physical/2026-08-06/mels_p29.json"
    )
