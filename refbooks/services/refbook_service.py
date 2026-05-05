from datetime import date

from django.utils import timezone

from refbooks.domain.entities import ElementEntity, RefBookEntity
from refbooks.domain.exceptions import RefBookNotFound
from refbooks.repositories.refbook_repository import (
    ElementRepository,
    RefBookRepository,
    VersionRepository,
)


class RefBookService:
    def __init__(self) -> None:
        self.refbook_repo = RefBookRepository()

    def get_refbooks_list(self, on_date: date | None = None) -> list[RefBookEntity]:
        if on_date is None:
            return self.refbook_repo.list_all()
        return self.refbook_repo.list_with_version_on_date(on_date)


class ElementService:
    def __init__(self) -> None:
        self.refbook_repo = RefBookRepository()
        self.version_repo = VersionRepository()
        self.element_repo = ElementRepository()

    def _resolve_version_id(self, refbook_id: int, version_string: str | None) -> int | None:
        if not self.refbook_repo.exists(refbook_id):
            raise RefBookNotFound(f"RefBook with id {refbook_id} not found")

        if version_string is not None:
            version = self.version_repo.get_by_refbook_and_version(refbook_id, version_string)
            return version.id

        current = self.version_repo.get_current_version(refbook_id, timezone.localdate())
        return current.id if current else None

    def get_elements_for_version(
        self, refbook_id: int, version_string: str | None = None
    ) -> list[ElementEntity]:
        version_id = self._resolve_version_id(refbook_id, version_string)
        if version_id is None:
            return []
        return self.element_repo.list_by_version(version_id)

    def check_element_exists(
        self,
        refbook_id: int,
        code: str,
        value: str,
        version_string: str | None = None,
    ) -> bool:
        version_id = self._resolve_version_id(refbook_id, version_string)
        if version_id is None:
            return False
        return self.element_repo.exists(version_id, code, value)
