"""Tests for the cookie based JWT authentication class."""

from datetime import timedelta

import pytest
from django.conf import settings
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.exceptions import InvalidToken
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


def _expired_token(user):
    """Return an access token for ``user`` that has already expired."""
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=-timedelta(seconds=1))
    return str(token)


@pytest.mark.parametrize(
    "make_token",
    [lambda user: "garbage", _expired_token],
    ids=["garbage", "expired"],
)
def test_authenticate_with_invalid_cookie_raises(user, make_token):
    """Malformed or expired access cookies are rejected."""
    request = _request_with_cookie(make_token(user))

    with pytest.raises(InvalidToken):
        CookieJWTAuthentication().authenticate(request)


def test_authenticate_header_is_set():
    """A WWW-Authenticate header makes DRF answer 401 instead of 403."""
    request = _request_with_cookie()

    assert CookieJWTAuthentication().authenticate_header(request)


def test_default_authentication_class_is_cookie_jwt():
    """DRF uses the cookie JWT authentication for every view by default."""
    classes = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]

    assert classes == ["auth_app.authentication.CookieJWTAuthentication"]
