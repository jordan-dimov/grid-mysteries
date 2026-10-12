"""The engines' kept pack across a pack-format change (Morpholog v0.0.15,
#517): a verifier reads one format, its own, so a kept pack of an older
format is moved aside under its format, never overwritten, and the pack
is exported again in the binary's format."""

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from grid_mysteries import record
from morpholog_client import envelopes

ROLE_REBINDINGS = {"status": "not_evaluated"}


def report(verdict: dict[str, object]) -> object:
    passes = verdict["status"] == "intact"
    return envelopes.PackVerificationReport.from_json(
        {"passes": passes, "verdict": verdict, "role_rebindings": ROLE_REBINDINGS},
        envelopes.parse_tree_verification,
    )


INTACT = {"status": "intact", "checkpoints": 1, "tree_size": 7}
UNSUPPORTED = {
    "status": "unsupported_pack",
    "pack_format_version": 4,
    "reads": 17,
    "written_by": None,
    "detail": "unsupported pack format 4",
}


@dataclass
class Api:
    pack_dir: Path
    verdicts: list[dict[str, object]]

    def __post_init__(self) -> None:
        self.exports: list[str] = []

    def audit_verify_pack(self, path: str, **_: object) -> object:
        return report(self.verdicts.pop(0))

    def audit_export(self, path: str, tree_size: int) -> object:
        self.exports.append(Path(path).read_text() if Path(path).exists() else "")
        Path(path).write_text("format 17\n")
        return SimpleNamespace(tree_size=tree_size)


def fake_record(tmp_path: Path, api: Api) -> Any:
    return SimpleNamespace(packs=tmp_path, public_key=tmp_path / "key.pub", client=lambda *_: api)


def test_a_kept_pack_of_an_older_format_is_moved_aside_and_exported_again(tmp_path):
    kept = tmp_path / "tree-7.ndjson"
    kept.write_text("format 4\n")
    api = Api(tmp_path, [UNSUPPORTED, INTACT])

    pack = record.exported_pack(
        fake_record(tmp_path, api), "", tmp_path / "a.json", {"tree_size": 7}
    )

    assert pack == kept and kept.read_text() == "format 17\n"
    assert (tmp_path / "tree-7.format-4.ndjson").read_text() == "format 4\n"
    assert api.exports == [""]


def test_a_kept_pack_the_binary_reads_is_not_exported_again(tmp_path):
    kept = tmp_path / "tree-7.ndjson"
    kept.write_text("format 17\n")
    api = Api(tmp_path, [INTACT])

    record.exported_pack(fake_record(tmp_path, api), "", tmp_path / "a.json", {"tree_size": 7})

    assert api.exports == [] and sorted(p.name for p in tmp_path.iterdir()) == ["tree-7.ndjson"]
