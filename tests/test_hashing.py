from pathlib import Path

from grid_mysteries.hashing import sha256_file


def test_sha256_file(tmp_path: Path) -> None:
    path = tmp_path / "source.json"
    path.write_bytes(b"grid mysteries\n")

    assert sha256_file(path) == "86989080dd51fb6cc58bfe8e708e9056520ba02036308eb00cb45836f5f60ec0"
