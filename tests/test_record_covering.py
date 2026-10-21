"""A checkpoint after an import covers the import's close (Morpholog
v0.0.16, `audit checkpoint --covering`, #589): the close transition is
read from the record itself, the checkpoint is asked to contain it by
name, and the one refusal that records nothing (the transition is
committed but still outside the stable prefix) is retried, bounded."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from grid_mysteries import record

ENGINE = record.Record(
    name="unit", programme=Path("unit/unit.morph"), actor="unit", key_id="unit-2026"
)
CLOSE = "01a15f3a-272b-75cb-a86a-50a244ce5acd"
CHECKPOINT = {
    "status": "created",
    "tree_size": 16,
    "root_hash": "sha256:7f65",
    "prev_checkpoint_hash": None,
    "checkpoint_hash": "sha256:12af",
    "witnesses": [],
}
REFUSAL = {
    "code": "transition_not_covered",
    "error": "transition is committed but outside the stable prefix",
    "transition_id": CLOSE,
    "tree_size": 15,
}


@dataclass
class Claim:
    args: dict[str, object]
    asserted_in: str


class Api:
    def __init__(self, claims: dict[str, list[Claim]]) -> None:
        self.claims = claims

    def claims_named(self, predicate: str) -> list[Claim]:
        return self.claims.get(predicate, [])


def test_last_close_is_the_transition_that_asserted_the_current_imports_close():
    api = Api(
        {
            "CurrentRun": [Claim({"register": "bill", "run": "run-2"}, "t-open-2")],
            "Imported": [
                Claim({"run": "run-1"}, "t-close-1"),
                Claim({"run": "run-2"}, "t-close-2"),
            ],
        }
    )
    assert record.last_close(api, current="CurrentRun", key="run") == "t-close-2"


def test_last_close_is_none_before_any_import_and_while_the_first_is_open():
    assert record.last_close(Api({}), current="CurrentRun", key="run") is None
    open_only = Api({"CurrentRun": [Claim({"register": "bill", "run": "run-1"}, "t-open-1")]})
    assert record.last_close(open_only, current="CurrentRun", key="run") is None


def _binary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, outputs: list[dict[str, object]]):
    """A fake `morpholog` that answers each checkpoint call from `outputs`
    in order, exit 1 for a refusal, and records every argv."""
    calls: list[list[str]] = []
    paused: list[float] = []

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        calls.append(list(args))
        out = outputs.pop(0)
        code = 1 if out.get("code") == "transition_not_covered" else 0
        return subprocess.CompletedProcess(list(args), code, json.dumps(out) + "\n", "")

    monkeypatch.setattr(record, "run", run)
    monkeypatch.setattr(record, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(record, "exported_pack", lambda *a, **k: tmp_path / "pack.ndjson")
    return calls, paused


def test_the_checkpoint_names_the_close_and_is_retried_while_not_covered(monkeypatch, tmp_path):
    calls, paused = _binary(monkeypatch, tmp_path, [REFUSAL, REFUSAL, CHECKPOINT])
    path, anchor, _ = record.checkpoint_and_export(
        ENGINE, "postgres:///unit", witness=False, covering=CLOSE, pause=paused.append
    )
    assert len(calls) == 3 and all(c[-2:] == ["--covering", CLOSE] for c in calls)
    assert paused == list(record.COVERING_RETRY_PAUSES[:2])
    assert anchor["tree_size"] == 16 and path == tmp_path / "unit" / "anchors" / "tree-16.json"
    assert json.loads(path.read_text()) == CHECKPOINT


def test_a_refusal_that_outlasts_every_pause_is_an_exit_with_nothing_written(monkeypatch, tmp_path):
    pauses = len(record.COVERING_RETRY_PAUSES)
    calls, paused = _binary(monkeypatch, tmp_path, [REFUSAL] * (pauses + 1))
    with pytest.raises(SystemExit) as exc:
        record.checkpoint_and_export(
            ENGINE, "postgres:///unit", witness=False, covering=CLOSE, pause=paused.append
        )
    assert f"refused {pauses} times" in str(exc.value) and CLOSE in str(exc.value)
    assert len(calls) == pauses + 1 and paused == list(record.COVERING_RETRY_PAUSES)
    assert not (tmp_path / "unit").exists()


def test_without_a_close_the_checkpoint_is_asked_as_before(monkeypatch, tmp_path):
    calls, _ = _binary(monkeypatch, tmp_path, [CHECKPOINT])
    record.checkpoint_and_export(ENGINE, "postgres:///unit", witness=False, covering=None)
    assert len(calls) == 1 and "--covering" not in calls[0]
