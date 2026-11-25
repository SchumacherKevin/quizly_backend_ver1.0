"""Tests for the registration endpoint POST /api/register/."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

PASSWORD = "Test1234!"


def _payload(**overrides):
    """Return a valid registration payload with optional overrides."""
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "password": PASSWORD,
        "confirmed_password": PASSWORD,
    }
    payload.update(overrides)
    return payload


def _register(api_client, payload):
    """Post ``payload`` to the registration endpoint."""
    return api_client.post(reverse("register"), payload, format="json")


@pytest.mark.django_db
def test_register_creates_user(api_client):
    """A valid registration creates the user and returns 201."""
    response = _register(api_client, _payload())

    assert response.status_code == 201
    assert response.json() == {"detail": "User created successfully!"}
    user = User.objects.get(username="newuser")
    assert user.email == "new@example.com"
    assert user.check_password(PASSWORD)


@pytest.mark.django_db
def test_register_sets_no_cookies(api_client):
    """Registration does not log the user in, so no JWT cookies are set."""
    response = _register(api_client, _payload())

    assert response.status_code == 201
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies


def test_register_rejects_duplicate_username(api_client, user):
    """A username that is already taken is rejected with 400."""
    payload = _payload(username=user.username)

    response = _register(api_client, payload)

    assert response.status_code == 400
    assert "username" in response.json()
    assert User.objects.filter(username=user.username).count() == 1
