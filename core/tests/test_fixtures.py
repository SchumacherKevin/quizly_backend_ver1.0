"""Tests for the shared pytest fixtures defined in conftest.py."""

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_user_fixture_has_hashed_password(user):
    """The user fixture has known credentials and a hashed password."""
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("Test1234!") is True
    assert user.password != "Test1234!"


def test_other_user_differs_from_user(user, other_user):
    """The other_user fixture is a separate account."""
    assert other_user.pk != user.pk
    assert other_user.username == "otheruser"


def test_api_client_is_drf_client(api_client):
    """The api_client fixture is a DRF test client."""
    assert isinstance(api_client, APIClient)
