"""The deploy gate every engine import runs first: a database missing an
index or statistics object the programme needs (Morpholog v0.0.14,
`provision indexes --check`), or holding a claim the programme's
declaration no longer fits (v0.0.16, `check --database-url`), refuses the
import before any plan is made. Hints pass: an engine's database serves
one programme, so an undeclared stored predicate is read, not refused."""

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


@dataclass
class Diagnostic:
    severity: str
    message: str


@dataclass
class Fit:
    diagnostics: list[Diagnostic]


CURRENT = Report([Obj("a", "KEEP")], [Obj("s", "KEEP")])


class Api:
    def __init__(self, report: Report, fit: Fit | None = None) -> None:
        self.report = report
        self.fit = fit or Fit([])
        self.calls: list[tuple[str, dict[str, object]]] = []

    def provision_indexes(self, **kwargs: object) -> Report:
        self.calls.append(("provision_indexes", kwargs))
        return self.report

    def check(self, **kwargs: object) -> Fit:
        self.calls.append(("check", kwargs))
        return self.fit


def test_a_current_database_passes_and_the_check_changes_nothing():
    api = Api(CURRENT)
    record.provisioned(api, "import")
    assert api.calls == [("provision_indexes", {"check": True}), ("check", {"with_database": True})]


def test_a_hint_from_the_database_check_passes():
    api = Api(CURRENT, Fit([Diagnostic("hint", "stored predicate `Old` is not declared")]))
    record.provisioned(api, "import")


def test_a_stored_claim_the_declaration_no_longer_fits_refuses_the_import():
    api = Api(
        CURRENT,
        Fit(
            [
                Diagnostic("hint", "stored predicate `Old` is not declared"),
                Diagnostic("error", "stored claim `DayRow` has arity 21, declared 22"),
            ]
        ),
    )
    with pytest.raises(record.ImportError_) as exc:
        record.provisioned(api, "import")
    message = str(exc.value)
    assert "does not fit" in message and "1 error(s)" in message
    assert "arity 21" in message and "Old" not in message


def test_provisioning_is_asked_before_fit_and_refuses_first():
    api = Api(Report([Obj("ix", "CREATE")], []), Fit([Diagnostic("error", "unfit")]))
    with pytest.raises(record.ImportError_) as exc:
        record.provisioned(api, "import")
    assert "provision indexes" in str(exc.value)
    assert [c[0] for c in api.calls] == ["provision_indexes"]


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
