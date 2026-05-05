from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from refbooks.models import Element, RefBook, Version


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def refbook1(db: None) -> RefBook:
    rb = RefBook.objects.create(code="RB1", name="RefBook 1")
    v_old = Version.objects.create(refbook=rb, version="1.0", start_date=date(2023, 1, 1))
    v_new = Version.objects.create(refbook=rb, version="2.0", start_date=date(2024, 1, 1))
    Element.objects.create(version=v_new, code="C1", value="Value 1")
    Element.objects.create(version=v_new, code="C2", value="Value 2")
    Element.objects.create(version=v_old, code="OLD", value="Old Value")
    return rb


@pytest.fixture
def refbook_future(db: None) -> RefBook:
    """Справочник, у которого все версии в будущем — нет текущей версии."""
    rb = RefBook.objects.create(code="FUTURE", name="Future RefBook")
    Version.objects.create(refbook=rb, version="1.0", start_date=date(2099, 1, 1))
    return rb


@pytest.mark.django_db
class TestRefBooksList:
    def test_no_date_returns_all(self, api_client: APIClient, refbook1: RefBook) -> None:
        RefBook.objects.create(code="RB2", name="RefBook 2")

        response = api_client.get("/api/refbooks/")

        assert response.status_code == status.HTTP_200_OK
        codes = {rb["code"] for rb in response.json()["refbooks"]}
        assert codes == {"RB1", "RB2"}

    def test_filtered_by_date(self, api_client: APIClient, refbook1: RefBook) -> None:
        RefBook.objects.create(code="RB2", name="RefBook 2")

        response = api_client.get("/api/refbooks/?date=2023-06-01")

        assert response.status_code == status.HTTP_200_OK
        codes = {rb["code"] for rb in response.json()["refbooks"]}
        assert codes == {"RB1"}

    def test_invalid_date(self, api_client: APIClient) -> None:
        response = api_client.get("/api/refbooks/?date=not-a-date")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()


@pytest.mark.django_db
class TestRefBookElements:
    def test_current_version_returns_latest(self, api_client: APIClient, refbook1: RefBook) -> None:
        response = api_client.get(f"/api/refbooks/{refbook1.pk}/elements/")

        assert response.status_code == status.HTTP_200_OK
        codes = {e["code"] for e in response.json()["elements"]}
        assert codes == {"C1", "C2"}

    def test_specific_version(self, api_client: APIClient, refbook1: RefBook) -> None:
        response = api_client.get(f"/api/refbooks/{refbook1.pk}/elements/?version=1.0")

        assert response.status_code == status.HTTP_200_OK
        codes = {e["code"] for e in response.json()["elements"]}
        assert codes == {"OLD"}

    def test_refbook_not_found(self, api_client: APIClient) -> None:
        response = api_client.get("/api/refbooks/999/elements/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Справочник не найден"

    def test_version_not_found(self, api_client: APIClient, refbook1: RefBook) -> None:
        response = api_client.get(f"/api/refbooks/{refbook1.pk}/elements/?version=9.9")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Версия не найдена"

    def test_no_current_version_returns_empty(
        self, api_client: APIClient, refbook_future: RefBook
    ) -> None:
        response = api_client.get(f"/api/refbooks/{refbook_future.pk}/elements/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"elements": []}


@pytest.mark.django_db
class TestCheckElement:
    def test_existing_element(self, api_client: APIClient, refbook1: RefBook) -> None:
        response = api_client.get(
            f"/api/refbooks/{refbook1.pk}/check_element/",
            {"code": "C1", "value": "Value 1"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"exists": True}

    def test_wrong_value(self, api_client: APIClient, refbook1: RefBook) -> None:
        response = api_client.get(
            f"/api/refbooks/{refbook1.pk}/check_element/",
            {"code": "C1", "value": "Wrong"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"exists": False}

    def test_missing_params(self, api_client: APIClient, refbook1: RefBook) -> None:
        response = api_client.get(
            f"/api/refbooks/{refbook1.pk}/check_element/",
            {"code": "C1"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refbook_not_found(self, api_client: APIClient) -> None:
        response = api_client.get(
            "/api/refbooks/999/check_element/",
            {"code": "C1", "value": "Value 1"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_version_not_found(self, api_client: APIClient, refbook1: RefBook) -> None:
        response = api_client.get(
            f"/api/refbooks/{refbook1.pk}/check_element/",
            {"code": "C1", "value": "Value 1", "version": "9.9"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_no_current_version_returns_false(
        self, api_client: APIClient, refbook_future: RefBook
    ) -> None:
        response = api_client.get(
            f"/api/refbooks/{refbook_future.pk}/check_element/",
            {"code": "C1", "value": "Value 1"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"exists": False}
