import pytest
from unittest.mock import Mock

from refbooks.domain.entities import RefBookEntity, VersionEntity
from refbooks.repositories.refbook_repository import RefBookRepository, VersionRepository
from refbooks.services.refbook_service import RefBookService


class TestRefBookService:
    def test_get_refbooks_list_with_date(self):
        # Arrange
        mock_repo = Mock(spec=RefBookRepository)
        service = RefBookService()
        service.refbook_repo = mock_repo

        expected_refbooks = [
            RefBookEntity(id=1, code="RB1", name="RefBook 1", description=""),
            RefBookEntity(id=2, code="RB2", name="RefBook 2", description=""),
        ]
        mock_repo.list_with_version_on_date.return_value = expected_refbooks

        # Act
        result = service.get_refbooks_list(date(2023, 1, 1))

        # Assert
        assert result == expected_refbooks
        mock_repo.list_with_version_on_date.assert_called_once_with(date(2023, 1, 1))

    def test_get_refbooks_list_without_date_uses_today(self):
        # Arrange
        mock_repo = Mock(spec=RefBookRepository)
        service = RefBookService()
        service.refbook_repo = mock_repo

        expected_refbooks = []
        mock_repo.list_with_version_on_date.return_value = expected_refbooks

        # Act
        result = service.get_refbooks_list()

        # Assert
        assert result == expected_refbooks
        # Should be called with today's date, but we can't mock timezone.now easily
        mock_repo.list_with_version_on_date.assert_called_once()


class TestVersionService:
    def test_get_current_version_exists(self):
        # Arrange
        mock_repo = Mock(spec=VersionRepository)
        from refbooks.services.refbook_service import VersionService

        service = VersionService()
        service.version_repo = mock_repo

        expected_version = VersionEntity(id=1, refbook_id=1, version="1.0", start_date=date(2023, 1, 1))
        mock_repo.get_current_version.return_value = expected_version

        # Act
        result = service.get_current_version(1, date(2023, 6, 1))

        # Assert
        assert result == expected_version
        mock_repo.get_current_version.assert_called_once_with(1, date(2023, 6, 1))

    def test_get_current_version_none(self):
        # Arrange
        mock_repo = Mock(spec=VersionRepository)
        from refbooks.services.refbook_service import VersionService

        service = VersionService()
        service.version_repo = mock_repo

        mock_repo.get_current_version.return_value = None

        # Act
        result = service.get_current_version(1)

        # Assert
        assert result is None

    def test_get_version_by_string(self):
        # Arrange
        mock_repo = Mock(spec=VersionRepository)
        from refbooks.services.refbook_service import VersionService

        service = VersionService()
        service.version_repo = mock_repo

        expected_version = VersionEntity(id=1, refbook_id=1, version="1.0", start_date=date(2023, 1, 1))
        mock_repo.get_by_refbook_and_version.return_value = expected_version

        # Act
        result = service.get_version_by_string(1, "1.0")

        # Assert
        assert result == expected_version
        mock_repo.get_by_refbook_and_version.assert_called_once_with(1, "1.0")


class TestElementService:
    def test_get_elements_for_version_with_version_string(self):
        # Arrange
        from refbooks.services.refbook_service import ElementService

        service = ElementService()

        # Mock repositories
        service.refbook_repo = Mock()
        service.version_repo = Mock()
        service.element_repo = Mock()

        # Mock refbook exists
        service.refbook_repo.get_by_id.return_value = RefBookEntity(id=1, code="RB1", name="RefBook 1", description="")

        # Mock version exists
        version_entity = VersionEntity(id=10, refbook_id=1, version="1.0", start_date=date(2023, 1, 1))
        service.version_repo.get_by_refbook_and_version.return_value = version_entity

        # Mock elements
        from refbooks.domain.entities import ElementEntity

        expected_elements = [
            ElementEntity(id=1, version_id=10, code="C1", value="Value 1"),
        ]
        service.element_repo.list_by_version.return_value = expected_elements

        # Act
        result = service.get_elements_for_version(1, "1.0")

        # Assert
        assert result == expected_elements
        service.refbook_repo.get_by_id.assert_called_once_with(1)
        service.version_repo.get_by_refbook_and_version.assert_called_once_with(1, "1.0")
        service.element_repo.list_by_version.assert_called_once_with(10)

    def test_get_elements_for_version_current_version(self):
        # Arrange
        from refbooks.services.refbook_service import ElementService

        service = ElementService()

        # Mock repositories
        service.refbook_repo = Mock()
        service.version_repo = Mock()
        service.element_repo = Mock()

        # Mock refbook exists
        service.refbook_repo.get_by_id.return_value = RefBookEntity(id=1, code="RB1", name="RefBook 1", description="")

        # Mock current version
        version_entity = VersionEntity(id=10, refbook_id=1, version="1.0", start_date=date(2023, 1, 1))
        service.version_repo.get_current_version.return_value = version_entity

        # Mock elements
        from refbooks.domain.entities import ElementEntity

        expected_elements = [
            ElementEntity(id=1, version_id=10, code="C1", value="Value 1"),
        ]
        service.element_repo.list_by_version.return_value = expected_elements

        # Act
        result = service.get_elements_for_version(1, None)

        # Assert
        assert result == expected_elements
        service.version_repo.get_current_version.assert_called_once()

    def test_get_elements_for_version_no_current_version(self):
        # Arrange
        from refbooks.services.refbook_service import ElementService

        service = ElementService()

        # Mock repositories
        service.refbook_repo = Mock()
        service.version_repo = Mock()

        # Mock refbook exists
        service.refbook_repo.get_by_id.return_value = RefBookEntity(id=1, code="RB1", name="RefBook 1", description="")

        # Mock no current version
        service.version_repo.get_current_version.return_value = None

        # Act
        result = service.get_elements_for_version(1, None)

        # Assert
        assert result == []

    def test_check_element_exists_true(self):
        # Arrange
        from refbooks.services.refbook_service import ElementService

        service = ElementService()

        # Mock get_elements_for_version
        from refbooks.domain.entities import ElementEntity

        elements = [
            ElementEntity(id=1, version_id=10, code="C1", value="Value 1"),
            ElementEntity(id=2, version_id=10, code="C2", value="Value 2"),
        ]
        service.get_elements_for_version = Mock(return_value=elements)

        # Act
        result = service.check_element_exists(1, "C1", "Value 1", "1.0")

        # Assert
        assert result is True
        service.get_elements_for_version.assert_called_once_with(1, "1.0")

    def test_check_element_exists_false(self):
        # Arrange
        from refbooks.services.refbook_service import ElementService

        service = ElementService()

        # Mock get_elements_for_version
        from refbooks.domain.entities import ElementEntity

        elements = [
            ElementEntity(id=1, version_id=10, code="C1", value="Value 1"),
        ]
        service.get_elements_for_version = Mock(return_value=elements)

        # Act
        result = service.check_element_exists(1, "C2", "Value 2", "1.0")

        # Assert
        assert result is False
