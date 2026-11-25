"""Tests for the token refresh endpoint POST /api/token/refresh/."""

from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


def _refresh(api_client):
    """Post to the refresh endpoint without a body, like the frontend."""
    return api_client.post(reverse("token-refresh"))


def test_refresh_sets_new_access_cookie(api_client, user):
    """A valid refresh cookie yields a new HttpOnly access cookie."""
    api_client.cookies["refresh_token"] = str(RefreshToken.for_user(user))

    response = _refresh(api_client)

    assert response.status_code == 200
    assert response.json() == {"detail": "Token refreshed"}
    cookie = response.cookies["access_token"]
    assert cookie["httponly"] is True
    assert AccessToken(cookie.value)["user_id"] == str(user.id)


def test_refresh_does_not_return_tokens(api_client, user):
    """No token is sent in the body and the refresh token is not rotated."""
    api_client.cookies["refresh_token"] = str(RefreshToken.for_user(user))

    response = _refresh(api_client)

    assert response.json() == {"detail": "Token refreshed"}
    assert "refresh_token" not in response.cookies


def test_refresh_without_cookie_returns_401(api_client):
    """A missing refresh cookie is rejected with 401."""
    response = _refresh(api_client)

    assert response.status_code == 401
    assert response.json() == {"detail": "Refresh token not found."}


def test_refresh_with_invalid_cookie_returns_401(api_client):
    """A malformed refresh cookie is rejected with 401."""
    api_client.cookies["refresh_token"] = "garbage"

    response = _refresh(api_client)

    assert response.status_code == 401
    assert response.json() == {"detail": "Refresh token invalid."}


def test_refresh_with_blacklisted_token_returns_401(api_client, user):
    """A blacklisted refresh token is rejected with 401."""
    refresh = RefreshToken.for_user(user)
    refresh.blacklist()
    api_client.cookies["refresh_token"] = str(refresh)

    response = _refresh(api_client)

    assert response.status_code == 401
    assert response.json() == {"detail": "Refresh token invalid."}


def test_refresh_after_logout_fails(auth_client):
    """The old refresh token cannot be used after logging out."""
    old_refresh = auth_client.cookies["refresh_token"].value
    auth_client.post(reverse("logout"))
    auth_client.cookies["refresh_token"] = old_refresh

    response = _refresh(auth_client)

    assert response.status_code == 401
