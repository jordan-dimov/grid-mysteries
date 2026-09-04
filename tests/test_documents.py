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


def test_suffix_follows_the_url_then_the_served_type_not_a_guess() -> None:
    assert documents.suffix_for("https://a/b/decision.PDF?download=1") == ".pdf"
    assert documents.suffix_for("https://a/b/decision") == ".html"
    assert documents.suffix_for("https://a/document/1/download", "application/pdf") == ".pdf"
    assert (
        documents.suffix_for("https://a/document/1/download", "text/html; charset=utf-8") == ".html"
    )
    assert documents.suffix_for("https://a/b/terms.docx", "application/octet-stream") == ".docx"
    assert documents.suffix_for("https://a/b/c", None) == ".html"


def test_probe_content_type_swallows_transport_errors(monkeypatch) -> None:
    class Boom:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def head(self, url):
            raise documents.httpx.ConnectError("no network in tests")

    monkeypatch.setattr(documents.httpx, "Client", Boom)
    assert documents.probe_content_type("https://a/b") is None
