from datetime import UTC, datetime, timedelta
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations.duration_envelope import (
    EnvelopeRecord,
    coverage_fraction,
    energy_bound_mwh,
    resolve_segments,
)

PERIOD_START = datetime(2026, 7, 5, 12, 0, tzinfo=UTC)
PERIOD_END = datetime(2026, 7, 5, 12, 30, tzinfo=UTC)


def record(
    from_min: int,
    to_min: int,
    level: str,
    published_min: int = -120,
    serial: str = "1",
    level_to: str | None = None,
) -> EnvelopeRecord:
    return EnvelopeRecord(
        time_from=PERIOD_START + timedelta(minutes=from_min),
        time_to=PERIOD_START + timedelta(minutes=to_min),
        level_from=Decimal(level),
        level_to=Decimal(level_to if level_to is not None else level),
        publish_time=PERIOD_START + timedelta(minutes=published_min),
        serial_number=serial,
    )


def test_single_full_cover_record_gives_level_times_half_hour() -> None:
    assert energy_bound_mwh([record(-10, 40, "50")], PERIOD_START, PERIOD_END, None) == Decimal(
        "25"
    )


def test_coverage_gap_means_unknown_never_partial_credit() -> None:
    records = [record(0, 20, "50")]
    assert energy_bound_mwh(records, PERIOD_START, PERIOD_END, None) is None
    assert coverage_fraction(records, PERIOD_START, PERIOD_END, None) == Decimal(1200) / Decimal(
        1800
    )


def test_later_publication_wins_on_overlap_and_cutoff_restores_the_earlier() -> None:
    early = record(-10, 40, "50", published_min=-120, serial="1")
    revision = record(-10, 40, "10", published_min=-30, serial="2")

    hindsight = energy_bound_mwh([early, revision], PERIOD_START, PERIOD_END, None)
    assert hindsight == Decimal("5")

    cutoff = PERIOD_START - timedelta(minutes=60)  # the declared decision cutoff
    public_as_of = energy_bound_mwh([early, revision], PERIOD_START, PERIOD_END, cutoff)
    assert public_as_of == Decimal("25")


def test_serial_number_breaks_publish_time_ties() -> None:
    a = record(-10, 40, "50", published_min=-120, serial="10")
    b = record(-10, 40, "30", published_min=-120, serial="20")
    [(_, _, winner)] = resolve_segments([a, b], PERIOD_START, PERIOD_END, None)
    assert winner is b


def test_generous_bound_uses_the_larger_absolute_endpoint_and_mdb_negatives() -> None:
    sloped = [record(-10, 40, "-28.399", level_to="-10")]
    assert energy_bound_mwh(sloped, PERIOD_START, PERIOD_END, None) == Decimal("28.399") / 2


def test_piecewise_records_stitch_and_clip() -> None:
    records = [record(-10, 15, "40"), record(15, 45, "20")]
    # 15 min at 40 MW + 15 min at 20 MW = 10 + 5 MWh
    assert energy_bound_mwh(records, PERIOD_START, PERIOD_END, None) == Decimal("15")


@st.composite
def envelope_records(draw):
    from_min = draw(st.integers(-30, 40))
    return record(
        from_min,
        from_min + draw(st.integers(1, 60)),
        str(draw(st.integers(-500, 500))),
        published_min=draw(st.integers(-300, 30)),
        serial=str(draw(st.integers(1, 99))),
    )


@given(records=st.lists(envelope_records(), max_size=8), seed=st.randoms())
def test_resolution_is_order_invariant_and_coverage_is_cutoff_monotone(records, seed):
    shuffled = list(records)
    seed.shuffle(shuffled)
    assert resolve_segments(shuffled, PERIOD_START, PERIOD_END, None) == resolve_segments(
        records, PERIOD_START, PERIOD_END, None
    )

    early_cutoff = PERIOD_START - timedelta(minutes=60)
    fraction_early = coverage_fraction(records, PERIOD_START, PERIOD_END, early_cutoff)
    fraction_late = coverage_fraction(records, PERIOD_START, PERIOD_END, None)
    assert Decimal(0) <= fraction_early <= fraction_late <= Decimal(1)

    bound = energy_bound_mwh(records, PERIOD_START, PERIOD_END, None)
    if bound is not None:
        assert bound >= 0
        assert fraction_late == 1
