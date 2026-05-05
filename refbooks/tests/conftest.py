import pytest
from django.test import Client


@pytest.fixture
def client():
    """Django test client"""
    return Client()
