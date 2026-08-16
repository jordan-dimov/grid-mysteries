from pathlib import Path

import pytest

from grid_mysteries.sources.http import fetch_artifact


def test_fetch_artifact_refuses_to_overwrite_a_pinned_artefact(tmp_path: Path) -> None:
    destination = tmp_path / "artefact.json"
    destination.write_bytes(b"{}")

    # The immutability check must fire before any network activity.
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        fetch_artifact(
            url="https://unreachable.invalid/artefact",
            destination=destination,
            source="test",
            dataset="TEST",
        )

    assert destination.read_bytes() == b"{}"
