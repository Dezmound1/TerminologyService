from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class RefBookEntity:
    id: int
    code: str
    name: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class VersionEntity:
    id: int
    refbook_id: int
    version: str
    start_date: date


@dataclass(frozen=True, slots=True)
class ElementEntity:
    id: int
    version_id: int
    code: str
    value: str
