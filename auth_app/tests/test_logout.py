"""Tests for the logout endpoint POST /api/logout/."""

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
