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


def test_login_sets_httponly_cookies(api_client, user):
    """A successful login stores both JWTs in HttpOnly cookies."""
    response = _login(api_client, username="testuser", password=TEST_PASSWORD)

    for name in ("access_token", "refresh_token"):
        cookie = response.cookies[name]
        assert cookie["httponly"] is True
        assert cookie.value


def test_login_does_not_expose_tokens_in_body(api_client, user):
    """Tokens are only sent as cookies, never in the response body."""
    response = _login(api_client, username="testuser", password=TEST_PASSWORD)

    body = response.content.decode()
    assert "access" not in body
    assert "refresh" not in body
    assert response.cookies["access_token"].value not in body
    assert response.cookies["refresh_token"].value not in body
