from datetime import UTC, datetime
from pathlib import Path

from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources import documents


def test_fetch_pinned_uses_the_public_document_source(monkeypatch, tmp_path: Path) -> None:
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

    monkeypatch.setattr(documents, "fetch_artifact", fake_fetch_artifact)
    artefact = documents.fetch_pinned(
        url="https://www.ofgem.gov.uk/x.pdf", destination=tmp_path / "x.pdf", dataset="ofgem"
    )
    assert artefact.source == "public-document"
    assert seen["dataset"] == "ofgem"


def test_suffix_follows_the_url_not_a_guess() -> None:
    assert documents.suffix_for("https://a/b/decision.PDF?download=1") == ".pdf"
    assert documents.suffix_for("https://a/b/decision") == ".html"
