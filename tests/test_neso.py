from datetime import UTC, datetime
from pathlib import Path

from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources import neso


def test_fetch_pinned_delegates_with_the_portal_source_and_long_timeout(
    monkeypatch, tmp_path: Path
) -> None:
    seen: dict = {}

    def fake_fetch_artifact(**kwargs) -> SourceArtifact:
        seen.update(kwargs)
        return SourceArtifact(
            source=kwargs["source"],
            dataset=kwargs["dataset"],
            path=kwargs["destination"],
            sha256="0" * 64,
            fetched_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    monkeypatch.setattr(neso, "fetch_artifact", fake_fetch_artifact)
    artefact = neso.fetch_pinned(
        url=neso.dump_url("rid"), destination=tmp_path / "x.csv", dataset="NESO-X"
    )

    assert artefact.source == neso.SOURCE == "neso-data-portal"
    assert seen["url"] == "https://api.neso.energy/datastore/dump/rid"
    assert seen["timeout_seconds"] == 300.0


def test_ckan_url_builders_target_the_action_api_and_quote_queries() -> None:
    assert neso.resource_show_url("abc") == f"{neso.CKAN_ACTION}/resource_show?id=abc"
    assert neso.package_show_url("eac-results") == f"{neso.CKAN_ACTION}/package_show?id=eac-results"
    assert (
        neso.package_search_url("dynamic containment performance", rows=5)
        == f"{neso.CKAN_ACTION}/package_search?q=dynamic%20containment%20performance&rows=5"
    )
    assert (
        neso.datastore_fields_url("r1")
        == f"{neso.CKAN_ACTION}/datastore_search?resource_id=r1&limit=0"
    )


def test_read_csv_path_keeps_values_as_strings(tmp_path: Path) -> None:
    path = tmp_path / "eac.csv"
    path.write_text("auctionUnit,executedQuantity\nKILSB-1,12.5\n")
    assert neso.read_csv_path(path) == [{"auctionUnit": "KILSB-1", "executedQuantity": "12.5"}]
