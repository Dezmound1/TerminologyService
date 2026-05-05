import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from refbooks.models import Element, RefBook, Version


class RefBooksAPITestCase(APITestCase):
    def setUp(self):
        self.refbook1 = RefBook.objects.create(code="RB1", name="RefBook 1", description="Test refbook 1")
        self.refbook2 = RefBook.objects.create(code="RB2", name="RefBook 2", description="Test refbook 2")

        self.version1_1 = Version.objects.create(refbook=self.refbook1, version="1.0", start_date="2023-01-01")
        self.version1_2 = Version.objects.create(refbook=self.refbook1, version="2.0", start_date="2024-01-01")
        self.version2_1 = Version.objects.create(refbook=self.refbook2, version="1.0", start_date="2025-01-01")

        Element.objects.create(version=self.version1_2, code="C1", value="Value 1")
        Element.objects.create(version=self.version1_2, code="C2", value="Value 2")

    def test_get_refbooks_no_date(self):
        """Test GET /refbooks/ without date parameter"""
        url = reverse("refbooks-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("refbooks", data)
        refbook_codes = [rb["code"] for rb in data["refbooks"]]
        self.assertIn("RB1", refbook_codes)

    def test_get_refbooks_with_date(self):
        """Test GET /refbooks/?date=2023-06-01"""
        url = reverse("refbooks-list")
        response = self.client.get(url, {"date": "2023-06-01"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        refbook_codes = [rb["code"] for rb in data["refbooks"]]
        self.assertIn("RB1", refbook_codes)

    def test_get_refbooks_invalid_date(self):
        """Test GET /refbooks/?date=invalid"""
        url = reverse("refbooks-list")
        response = self.client.get(url, {"date": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.json())

    def test_get_refbook_elements_current_version(self):
        """Test GET /refbooks/1/elements/ (current version)"""
        url = reverse("refbook-elements", kwargs={"id": self.refbook1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("elements", data)
        self.assertEqual(len(data["elements"]), 2)
        codes = [e["code"] for e in data["elements"]]
        self.assertIn("C1", codes)
        self.assertIn("C2", codes)

    def test_get_refbook_elements_specific_version(self):
        """Test GET /refbooks/1/elements/?version=1.0"""
        url = reverse("refbook-elements", kwargs={"id": self.refbook1.id})
        response = self.client.get(url, {"version": "1.0"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["elements"]), 0)

    def test_get_refbook_elements_not_found(self):
        """Test GET /refbooks/999/elements/"""
        url = reverse("refbook-elements", kwargs={"id": 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.json())

    def test_get_refbook_elements_version_not_found(self):
        """Test GET /refbooks/1/elements/?version=3.0"""
        url = reverse("refbook-elements", kwargs={"id": self.refbook1.id})
        response = self.client.get(url, {"version": "3.0"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.json())

    def test_check_element_exists_true(self):
        """Test GET /refbooks/1/check_element?code=C1&value=Value 1"""
        url = reverse("check-element", kwargs={"id": self.refbook1.id})
        response = self.client.get(url, {"code": "C1", "value": "Value 1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["exists"], True)

    def test_check_element_exists_false(self):
        """Test GET /refbooks/1/check_element?code=C3&value=Value 3"""
        url = reverse("check-element", kwargs={"id": self.refbook1.id})
        response = self.client.get(url, {"code": "C3", "value": "Value 3"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["exists"], False)

    def test_check_element_missing_params(self):
        """Test GET /refbooks/1/check_element without code/value"""
        url = reverse("check-element", kwargs={"id": self.refbook1.id})
        response = self.client.get(url, {"code": "C1"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.json())

    def test_check_element_refbook_not_found(self):
        """Test GET /refbooks/999/check_element"""
        url = reverse("check-element", kwargs={"id": 999})
        response = self.client.get(url, {"code": "C1", "value": "Value 1"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.json())
