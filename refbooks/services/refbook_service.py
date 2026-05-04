from datetime import date

from django.utils import timezone

from refbooks.domain.entities import ElementEntity, RefBookEntity, VersionEntity
from refbooks.repositories.refbook_repository import (
    ElementRepository,
    RefBookRepository,
    VersionRepository,
)


class RefBookService:
    def __init__(self) -> None:
        self.refbook_repo = RefBookRepository()
        self.version_repo = VersionRepository()

    def get_refbooks_list(self, on_date: date | None = None) -> list[RefBookEntity]:
        """Get all refbooks that have a version for given date"""
        if on_date is None:
            on_date = timezone.now().date()

        return self.refbook_repo.list_with_version_on_date(on_date)


class VersionService:
    def __init__(self) -> None:
        self.version_repo = VersionRepository()

    def get_current_version(self, refbook_id: int, on_date: date | None = None) -> VersionEntity | None:
        """Get current version of refbook for given date"""
        if on_date is None:
            on_date = timezone.now().date()

        return self.version_repo.get_current_version(refbook_id, on_date)

    def get_version_by_string(self, refbook_id: int, version_string: str) -> VersionEntity:
        """Get specific version of refbook"""
        return self.version_repo.get_by_refbook_and_version(refbook_id, version_string)


class ElementService:
    def __init__(self) -> None:
        self.element_repo = ElementRepository()
        self.version_repo = VersionRepository()

    def get_elements_for_version(self, refbook_id: int, version_string: str | None = None) -> list[ElementEntity]:
        """Get elements for specific or current version of refbook"""
        if version_string is None:

            current_version = self.version_repo.get_current_version(refbook_id)
            if current_version is None:
                return []
            version_id = current_version.id
        else:

            version = self.version_repo.get_by_refbook_and_version(refbook_id, version_string)
            version_id = version.id

        return self.element_repo.list_by_version(version_id)

    def check_element_exists(
        self,
        refbook_id: int,
        code: str,
        value: str,
        version_string: str | None = None,
    ) -> bool:
        """Check if element with code and value exists in version"""
        if version_string is None:

            current_version = self.version_repo.get_current_version(refbook_id)
            if current_version is None:
                return False
            version_id = current_version.id
        else:
            
            version = self.version_repo.get_by_refbook_and_version(refbook_id, version_string)
            version_id = version.id

        element = self.element_repo.get_by_version_and_code(version_id, code)
        if element is None:
            return False

        return element.value == value
