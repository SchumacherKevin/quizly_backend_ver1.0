"""Tests for the auth cookie helpers in auth_app.utils."""

import pytest
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from auth_app.utils import (
    delete_auth_cookies,
    set_access_cookie,
    set_auth_cookies,
)


def _assert_secure_flags(cookie):
    """Assert the shared flags of an auth cookie."""
    assert cookie["httponly"] is True
    assert cookie["samesite"] == "Lax"
    assert cookie["path"] == "/"


@pytest.mark.django_db
def test_set_auth_cookies_sets_httponly_cookies(user):
    """Both JWT cookies are HttpOnly with the token lifetimes."""
    response = Response()
    refresh = RefreshToken.for_user(user)

    set_auth_cookies(response, refresh)

    access = response.cookies["access_token"]
    refresh_cookie = response.cookies["refresh_token"]
    _assert_secure_flags(access)
    _assert_secure_flags(refresh_cookie)
    assert access["max-age"] == 300
    assert refresh_cookie["max-age"] == 86400
    assert AccessToken(access.value)["user_id"] == str(user.id)
    assert refresh_cookie.value == str(refresh)


def test_set_access_cookie_only_sets_access():
    """Setting the access cookie leaves the refresh cookie untouched."""
    response = Response()

    set_access_cookie(response, "abc")

    assert response.cookies["access_token"].value == "abc"
    assert "refresh_token" not in response.cookies


@pytest.mark.parametrize("name", ["access_token", "refresh_token"])
def test_delete_auth_cookies_expires_both(name):
    """Deleting the auth cookies empties and expires both of them."""
    response = Response()

    delete_auth_cookies(response)

    cookie = response.cookies[name]
    assert cookie.value == ""
    assert cookie["max-age"] == 0
    assert cookie["path"] == "/"
