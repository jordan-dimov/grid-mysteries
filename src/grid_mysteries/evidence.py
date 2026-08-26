"""Where an investigation writes its evidence, and how it serialises it.

Evidence JSON is committed and digest-pinned, so its byte layout is a
contract: `indent=1`, insertion key order, Decimals as strings (never
floats), dates in ISO form, dataclasses as their field dicts, and a
trailing newline. One writer keeps every investigation on that layout.
"""

import dataclasses
import json
from datetime import date
from decimal import Decimal
from pathlib import Path


def evidence_dir(script_file: str | Path) -> Path:
    """The `evidence/` directory beside an investigation script (`__file__`)."""
    return Path(script_file).resolve().parent / "evidence"


def jsonable(obj: object) -> object:
    """`json.dumps` default hook for the value types evidence carries."""
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, date):  # datetime is a date; both serialise as isoformat
        return obj.isoformat()
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, tuple | set | frozenset):
        return list(obj)
    raise TypeError(f"{type(obj).__name__} is not evidence-serialisable")


def dumps(obj: object) -> str:
    """The evidence JSON layout, without the trailing newline."""
    return json.dumps(obj, indent=1, default=jsonable)


def write_json(path: Path, obj: object, *, trailing_newline: bool = True) -> None:
    """Write `obj` as evidence JSON, creating parent directories.

    `trailing_newline=False` exists only for files whose committed bytes
    predate the convention; new evidence never passes it.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    text = dumps(obj)
    path.write_text(text + "\n" if trailing_newline else text)
