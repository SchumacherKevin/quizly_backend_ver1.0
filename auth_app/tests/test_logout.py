"""Tests for the logout endpoint POST /api/logout/."""

import pytest
from django.urls import reverse

LOGOUT_DETAIL = (
    "Log-Out successfully! All Tokens will be deleted. "
    "Refresh token is now invalid."
)


def test_logout_returns_success_message(auth_client):
    """An authenticated user is logged out with 200."""
    response = auth_client.post(reverse("logout"))

    assert response.status_code == 200
    assert response.json() == {"detail": LOGOUT_DETAIL}


@pytest.mark.parametrize("name", ["access_token", "refresh_token"])
def test_logout_deletes_auth_cookies(auth_client, name):
    """Logout expires both JWT cookies on the client."""
    response = auth_client.post(reverse("logout"))

    cookie = response.cookies[name]
    assert cookie.value == ""
    assert cookie["max-age"] == 0
