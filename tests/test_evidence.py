import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from grid_mysteries.evidence import evidence_dir, jsonable, write_json


@dataclass(frozen=True)
class Row:
    unit: str
    price: Decimal
    seen: date


def test_evidence_dir_sits_beside_the_script() -> None:
    assert evidence_dir("/repo/investigations/007-x/run.py") == Path(
        "/repo/investigations/007-x/evidence"
    )


def test_write_json_uses_the_committed_layout(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "out.json"
    write_json(path, {"b": Decimal("1.50"), "a": [Decimal("2"), (1, 2)]})

    text = path.read_text()
    # indent=1, insertion order kept, Decimal as string, trailing newline.
    assert text == '{\n "b": "1.50",\n "a": [\n  "2",\n  [\n   1,\n   2\n  ]\n ]\n}\n'
    assert text == json.dumps(json.loads(text), indent=1) + "\n"


def test_write_json_can_omit_the_trailing_newline_for_legacy_files(tmp_path: Path) -> None:
    path = tmp_path / "legacy.json"
    write_json(path, [1], trailing_newline=False)
    assert path.read_bytes() == b"[\n 1\n]"


def test_jsonable_handles_the_evidence_value_types() -> None:
    row = Row("E_A-1", Decimal("71.25"), date(2026, 8, 6))
    text = json.dumps(
        {"row": row, "when": datetime(2026, 8, 6, 12, 30, tzinfo=UTC), "keys": {1, 2}},
        default=jsonable,
    )
    assert json.loads(text) == {
        "row": {"unit": "E_A-1", "price": "71.25", "seen": "2026-08-06"},
        "when": "2026-08-06T12:30:00+00:00",
        "keys": [1, 2],
    }
    # str(Decimal) semantics, never float: exponent forms survive verbatim.
    assert jsonable(Decimal("1E+2")) == "1E+2"
    with pytest.raises(TypeError, match="object"):
        jsonable(object())
