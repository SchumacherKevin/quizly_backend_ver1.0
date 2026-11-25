"""Tests for the shared auth fixtures in conftest.py."""

from rest_framework_simplejwt.tokens import AccessToken


def test_auth_client_fixture_has_cookies(auth_client, user):
    """The auth client carries JWT cookies for the default user."""
    assert "access_token" in auth_client.cookies
    assert "refresh_token" in auth_client.cookies
    access = AccessToken(auth_client.cookies["access_token"].value)
    assert access["user_id"] == str(user.id)
