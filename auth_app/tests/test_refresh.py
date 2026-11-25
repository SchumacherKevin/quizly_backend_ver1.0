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
