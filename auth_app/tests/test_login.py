"""Tests for the login endpoint POST /api/login/."""

from django.urls import reverse

from conftest import TEST_PASSWORD


def _login(api_client, **payload):
    """Post ``payload`` to the login endpoint."""
    return api_client.post(reverse("login"), payload, format="json")


def test_login_returns_user_data(api_client, user):
    """Valid credentials return a success message and the user data."""
    response = _login(api_client, username="testuser", password=TEST_PASSWORD)

    assert response.status_code == 200
    assert response.json() == {
        "detail": "Login successfully!",
        "user": {
            "id": user.id,
            "username": "testuser",
            "email": "test@example.com",
        },
    }
