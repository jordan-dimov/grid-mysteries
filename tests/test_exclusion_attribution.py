from decimal import Decimal

from grid_mysteries.investigations.exclusion_attribution import (
    categorise,
    excluded_volume_by_category,
    primary_category,
    split_reasons,
)


def row(reason: str, volume: str) -> dict:
    return {"exclusion_reason": reason, "excluded_volume_MWh": volume}


def test_atomic_reason_maps_to_its_category() -> None:
    assert categorise("Wind offer") == ["wind_offer"]
    assert categorise("Inaccessible pumped storage through zero") == ["long_notice_or_access"]


def test_compound_reason_splits_into_all_categories() -> None:
    assert categorise("Behind constraint, Unit ramping between 0 and SEL or 0 and SIL") == [
        "behind_constraint",
        "ramping",
    ]
    assert categorise(
        "Long notice 0 to SIL or 0 to SEL, Cannot take a long notice unit offline"
    ) == ["long_notice_or_access", "long_notice_or_access"]


def test_unknown_fragment_is_preserved_as_unrecognised() -> None:
    assert split_reasons("Some future reason") == ["Some future reason"]
    assert categorise("Some future reason") == ["unrecognised"]
    assert categorise("Wind offer, Some future reason") == ["wind_offer", "unrecognised"]


def test_volume_attribution_sums_absolute_volumes_per_category() -> None:
    volumes = excluded_volume_by_category(
        [
            row("Wind offer", "5"),
            row("Wind offer", "-3"),
            row("Behind constraint, Wind offer", "2"),
        ]
    )
    assert volumes == {"wind_offer": Decimal("10"), "behind_constraint": Decimal("2")}


def test_primary_category_is_largest_volume_with_declared_tie_break() -> None:
    assert primary_category([row("Behind constraint", "4"), row("Wind offer", "6")]) == "wind_offer"
    # Equal volumes: the declared layer order prefers wind_offer.
    assert primary_category([row("Behind constraint", "4"), row("Wind offer", "4")]) == "wind_offer"
    assert primary_category([]) is None
