"""The deploy gate every engine import runs first (Morpholog v0.0.14,
`provision indexes --check`): a database missing an index or statistics
object the programme needs refuses the import before any plan is made."""

from dataclasses import dataclass

import pytest

from grid_mysteries import record


@dataclass
class Obj:
    name: str
    action: str


@dataclass
class Report:
    indexes: list[Obj]
    statistics: list[Obj]

    @property
    def is_current(self) -> bool:
        return all(o.action == "KEEP" for o in self.indexes + self.statistics)


class Api:
    def __init__(self, report: Report) -> None:
        self.report = report
        self.calls: list[dict[str, object]] = []

    def provision_indexes(self, **kwargs: object) -> Report:
        self.calls.append(kwargs)
        return self.report


def test_a_current_database_passes_and_the_check_changes_nothing():
    api = Api(Report([Obj("a", "KEEP")], [Obj("s", "KEEP")]))
    record.provisioned(api, "import")
    assert api.calls == [{"check": True}]


def test_anything_to_create_or_prune_refuses_the_import_and_names_it():
    api = Api(
        Report([Obj("ix_dayrow_0", "CREATE"), Obj("old", "STALE")], [Obj("st_run", "CREATE")])
    )
    with pytest.raises(record.ImportError_) as exc:
        record.provisioned(api, "import")
    message = str(exc.value)
    assert "3 index/statistics object(s)" in message
    assert "ix_dayrow_0 CREATE" in message and "old STALE" in message and "st_run CREATE" in message
    assert "provision indexes" in message
