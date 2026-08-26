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
