from datetime import date
from unittest.mock import Mock

import pytest

from refbooks.domain.entities import ElementEntity, RefBookEntity, VersionEntity
from refbooks.domain.exceptions import RefBookNotFound, VersionNotFound
from refbooks.services.refbook_service import ElementService, RefBookService


def _make_element_service(refbook_exists: bool = True) -> ElementService:
    service = ElementService()
    service.refbook_repo = Mock()
    service.refbook_repo.exists.return_value = refbook_exists
    service.version_repo = Mock()
    service.element_repo = Mock()
    return service


class TestRefBookService:
    def test_without_date_returns_all(self) -> None:
        service = RefBookService()
        service.refbook_repo = Mock()
        service.refbook_repo.list_all.return_value = [RefBookEntity(id=1, code="RB1", name="N")]

        result = service.get_refbooks_list()

        assert len(result) == 1
        service.refbook_repo.list_all.assert_called_once_with()
        service.refbook_repo.list_with_version_on_date.assert_not_called()

    def test_with_date_filters(self) -> None:
        service = RefBookService()
        service.refbook_repo = Mock()
        service.refbook_repo.list_with_version_on_date.return_value = []

        service.get_refbooks_list(date(2023, 6, 1))

        service.refbook_repo.list_with_version_on_date.assert_called_once_with(date(2023, 6, 1))


class TestElementServiceGetElements:
    def test_uses_explicit_version(self) -> None:
        service = _make_element_service()
        service.version_repo.get_by_refbook_and_version.return_value = VersionEntity(
            id=10, refbook_id=1, version="1.0", start_date=date(2023, 1, 1)
        )
        service.element_repo.list_by_version.return_value = [
            ElementEntity(id=1, version_id=10, code="C1", value="V1")
        ]

        result = service.get_elements_for_version(1, "1.0")

        assert len(result) == 1
        service.element_repo.list_by_version.assert_called_once_with(10)

    def test_uses_current_version_when_not_specified(self) -> None:
        service = _make_element_service()
        service.version_repo.get_current_version.return_value = VersionEntity(
            id=10, refbook_id=1, version="2.0", start_date=date(2024, 1, 1)
        )
        service.element_repo.list_by_version.return_value = []

        service.get_elements_for_version(1, None)

        service.version_repo.get_current_version.assert_called_once()
        service.element_repo.list_by_version.assert_called_once_with(10)

    def test_returns_empty_when_no_current_version(self) -> None:
        service = _make_element_service()
        service.version_repo.get_current_version.return_value = None

        assert service.get_elements_for_version(1, None) == []
        service.element_repo.list_by_version.assert_not_called()

    def test_raises_when_refbook_missing(self) -> None:
        service = _make_element_service(refbook_exists=False)

        with pytest.raises(RefBookNotFound):
            service.get_elements_for_version(999, None)

    def test_propagates_version_not_found(self) -> None:
        service = _make_element_service()
        service.version_repo.get_by_refbook_and_version.side_effect = VersionNotFound("nope")

        with pytest.raises(VersionNotFound):
            service.get_elements_for_version(1, "9.9")


class TestElementServiceCheckElement:
    def test_returns_true_when_element_exists(self) -> None:
        service = _make_element_service()
        service.version_repo.get_by_refbook_and_version.return_value = VersionEntity(
            id=10, refbook_id=1, version="1.0", start_date=date(2023, 1, 1)
        )
        service.element_repo.exists.return_value = True

        assert service.check_element_exists(1, "C1", "V1", "1.0") is True
        service.element_repo.exists.assert_called_once_with(10, "C1", "V1")

    def test_returns_false_when_element_missing(self) -> None:
        service = _make_element_service()
        service.version_repo.get_by_refbook_and_version.return_value = VersionEntity(
            id=10, refbook_id=1, version="1.0", start_date=date(2023, 1, 1)
        )
        service.element_repo.exists.return_value = False

        assert service.check_element_exists(1, "C1", "V1", "1.0") is False

    def test_returns_false_when_no_current_version(self) -> None:
        service = _make_element_service()
        service.version_repo.get_current_version.return_value = None

        assert service.check_element_exists(1, "C1", "V1") is False
        service.element_repo.exists.assert_not_called()

    def test_raises_when_refbook_missing(self) -> None:
        service = _make_element_service(refbook_exists=False)

        with pytest.raises(RefBookNotFound):
            service.check_element_exists(999, "C1", "V1")
