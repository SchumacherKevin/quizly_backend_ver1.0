"""Shared pytest fixtures for the Quizly backend."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

TEST_PASSWORD = "Test1234!"


@pytest.fixture
def api_client():
    """Return an unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Return the default test user."""
    return User.objects.create_user(
        "testuser", "test@example.com", TEST_PASSWORD
    )


@pytest.fixture
def other_user(db):
    """Return a second user who does not own the default user's data."""
    return User.objects.create_user(
        "otheruser", "other@example.com", TEST_PASSWORD
    )
