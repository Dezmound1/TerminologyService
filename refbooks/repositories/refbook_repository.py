from datetime import date

from django.utils import timezone

from refbooks.domain.entities import ElementEntity, RefBookEntity, VersionEntity
from refbooks.domain.exceptions import RefBookNotFound, VersionNotFound
from refbooks.models import Element, RefBook, Version


class RefBookRepository:
    def get_by_id(self, refbook_id: int) -> RefBookEntity:
        try:
            refbook = RefBook.objects.get(pk=refbook_id)
            return RefBookEntity(
                id=refbook.id,
                code=refbook.code,
                name=refbook.name,
                description=refbook.description,
            )
        except RefBook.DoesNotExist:
            raise RefBookNotFound(f"RefBook with id {refbook_id} not found")

    def get_by_code(self, code: str) -> RefBookEntity:
        try:
            refbook = RefBook.objects.get(code=code)
            return RefBookEntity(
                id=refbook.id,
                code=refbook.code,
                name=refbook.name,
                description=refbook.description,
            )
        except RefBook.DoesNotExist:
            raise RefBookNotFound(f"RefBook with code {code} not found")

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
        """Get refbooks that have a version with start_date <= target_date"""
        refbooks = RefBook.objects.filter(versions__start_date__lte=target_date).distinct().order_by("code")
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
    def get_by_id(self, version_id: int) -> VersionEntity:
        try:
            version = Version.objects.get(pk=version_id)
            return VersionEntity(
                id=version.id,
                refbook_id=version.refbook_id,
                version=version.version,
                start_date=version.start_date,
            )
        except Version.DoesNotExist:
            raise VersionNotFound(f"Version with id {version_id} not found")

    def get_current_version(self, refbook_id: int, on_date: date | None = None) -> VersionEntity | None:
        """Get current (latest) version of refbook for given date"""
        if on_date is None:
            on_date = timezone.now().date()

        try:
            version = Version.objects.filter(
                refbook_id=refbook_id,
                start_date__lte=on_date,
            ).latest("start_date")
            return VersionEntity(
                id=version.id,
                refbook_id=version.refbook_id,
                version=version.version,
                start_date=version.start_date,
            )
        except Version.DoesNotExist:
            return None

    def get_by_refbook_and_version(self, refbook_id: int, version_string: str) -> VersionEntity:
        try:
            version = Version.objects.get(
                refbook_id=refbook_id,
                version=version_string,
            )
            return VersionEntity(
                id=version.id,
                refbook_id=version.refbook_id,
                version=version.version,
                start_date=version.start_date,
            )
        except Version.DoesNotExist:
            raise VersionNotFound(f"Version {version_string} for refbook {refbook_id} not found")

    def list_by_refbook(self, refbook_id: int) -> list[VersionEntity]:
        versions = Version.objects.filter(refbook_id=refbook_id).order_by("start_date")
        return [
            VersionEntity(
                id=v.id,
                refbook_id=v.refbook_id,
                version=v.version,
                start_date=v.start_date,
            )
            for v in versions
        ]


class ElementRepository:
    def get_by_version_and_code(self, version_id: int, code: str) -> ElementEntity | None:
        """Get element by version_id and code"""
        try:
            element = Element.objects.get(version_id=version_id, code=code)
            return ElementEntity(
                id=element.id,
                version_id=element.version_id,
                code=element.code,
                value=element.value,
            )
        except Element.DoesNotExist:
            return None

    def list_by_version(self, version_id: int) -> list[ElementEntity]:
        """Get all elements for a version"""
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
