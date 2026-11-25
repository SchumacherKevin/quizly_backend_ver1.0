"""Tests for the DRF and simplejwt configuration."""

from datetime import timedelta

from django.conf import settings

from core.env import get_bool


def test_simple_jwt_lifetimes():
    """Tokens use the agreed lifetimes and refresh tokens do not rotate."""
    jwt = settings.SIMPLE_JWT

    assert jwt["ACCESS_TOKEN_LIFETIME"] == timedelta(minutes=5)
    assert jwt["REFRESH_TOKEN_LIFETIME"] == timedelta(days=1)
    assert jwt["ROTATE_REFRESH_TOKENS"] is False


def test_token_blacklist_installed():
    """DRF and the simplejwt blacklist app are installed."""
    blacklist = "rest_framework_simplejwt.token_blacklist"

    assert blacklist in settings.INSTALLED_APPS
    assert "rest_framework" in settings.INSTALLED_APPS


def test_default_permission_is_authenticated():
    """API views require authentication unless they opt out."""
    permissions = settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]

    assert permissions == ["rest_framework.permissions.IsAuthenticated"]


def test_auth_cookie_settings():
    """Auth cookies are Lax and only secure outside of debug mode.

    The test runner forces ``settings.DEBUG`` to False, so the expected
    value is derived from the ``DEBUG`` environment variable instead.
    """
    debug = get_bool("DEBUG", False)

    assert settings.AUTH_COOKIE_SAMESITE == "Lax"
    assert settings.AUTH_COOKIE_SECURE is (not debug)
