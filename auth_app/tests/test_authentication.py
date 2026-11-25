"""Tests for the cookie based JWT authentication class."""

from rest_framework.test import APIRequestFactory

from auth_app.authentication import CookieJWTAuthentication


def test_authenticate_without_cookie_returns_none():
    """A request without an access cookie stays anonymous."""
    request = APIRequestFactory().get("/")

    assert CookieJWTAuthentication().authenticate(request) is None
