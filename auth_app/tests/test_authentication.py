"""Tests for the cookie based JWT authentication class."""

from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken

from auth_app.authentication import CookieJWTAuthentication


def _request_with_cookie(value=None):
    """Return a GET request with an optional ``access_token`` cookie."""
    request = APIRequestFactory().get("/")
    if value is not None:
        request.COOKIES["access_token"] = value
    return request


def test_authenticate_without_cookie_returns_none():
    """A request without an access cookie stays anonymous."""
    request = _request_with_cookie()

    assert CookieJWTAuthentication().authenticate(request) is None


def test_authenticate_with_valid_cookie_returns_user(user):
    """A valid access cookie authenticates its user."""
    token = AccessToken.for_user(user)
    request = _request_with_cookie(str(token))

    result = CookieJWTAuthentication().authenticate(request)

    assert result[0] == user
    assert str(result[1]) == str(token)
