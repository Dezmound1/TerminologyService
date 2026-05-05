from datetime import date

from refbooks.domain.entities import ElementEntity, RefBookEntity, VersionEntity
from refbooks.domain.exceptions import VersionNotFound
from refbooks.models import Element, RefBook, Version


class RefBookRepository:
    def exists(self, refbook_id: int) -> bool:
        return RefBook.objects.filter(pk=refbook_id).exists()

    def list_all(self) -> list[RefBookEntity]:
        refbooks = RefBook.objects.all().order_by("code")
        return [
            RefBookEntity(
                id=rb.id,
                code=rb.code,
                name=rb.name,
                description=rb.description,
            )
            for rb in refbooks
        ]

    def list_with_version_on_date(self, target_date: date) -> list[RefBookEntity]:
        refbooks = (
            RefBook.objects.filter(versions__start_date__lte=target_date)
            .distinct()
            .order_by("code")
        )
        return [
            RefBookEntity(
                id=rb.id,
                code=rb.code,
                name=rb.name,
                description=rb.description,
            )
            for rb in refbooks
        ]


class VersionRepository:
    def get_current_version(self, refbook_id: int, on_date: date) -> VersionEntity | None:
        try:
            version = Version.objects.filter(
                refbook_id=refbook_id,
                start_date__lte=on_date,
            ).latest("start_date")
        except Version.DoesNotExist:
            return None
        return VersionEntity(
            id=version.id,
            refbook_id=version.refbook_id,
            version=version.version,
            start_date=version.start_date,
        )

    def get_by_refbook_and_version(self, refbook_id: int, version_string: str) -> VersionEntity:
        try:
            version = Version.objects.get(
                refbook_id=refbook_id,
                version=version_string,
            )
        except Version.DoesNotExist:
            raise VersionNotFound(f"Version {version_string} for refbook {refbook_id} not found")
        return VersionEntity(
            id=version.id,
            refbook_id=version.refbook_id,
            version=version.version,
            start_date=version.start_date,
        )


class ElementRepository:
    def exists(self, version_id: int, code: str, value: str) -> bool:
        return Element.objects.filter(
            version_id=version_id, code=code, value=value
        ).exists()

    def list_by_version(self, version_id: int) -> list[ElementEntity]:
        elements = Element.objects.filter(version_id=version_id).order_by("code")
        return [
            ElementEntity(
                id=e.id,
                version_id=e.version_id,
                code=e.code,
                value=e.value,
            )
            for e in elements
        ]
