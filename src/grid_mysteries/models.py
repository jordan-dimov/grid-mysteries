from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SourceArtifact:
    source: str
    dataset: str
    path: Path
    sha256: str
    fetched_at: datetime
    published_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.fetched_at.tzinfo is None:
            raise ValueError("fetched_at must be timezone-aware")
        if self.published_at is not None and self.published_at.tzinfo is None:
            raise ValueError("published_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class Mystery:
    mystery_id: str
    title: str
    opened_at: datetime
    observation: str
    interpretation: str | None = None

    @classmethod
    def open(cls, mystery_id: str, title: str, observation: str) -> Mystery:
        return cls(
            mystery_id=mystery_id,
            title=title,
            opened_at=datetime.now(UTC),
            observation=observation,
        )
