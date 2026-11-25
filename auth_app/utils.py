"""Helpers for the JWT auth cookies."""

from django.conf import settings

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"


def _cookie_options(lifetime):
    """Return the shared cookie options for a token ``lifetime``."""
    return {
        "httponly": True,
        "secure": settings.AUTH_COOKIE_SECURE,
        "samesite": settings.AUTH_COOKIE_SAMESITE,
        "path": "/",
        "max_age": int(lifetime.total_seconds()),
    }


def set_access_cookie(response, token):
    """Store the access ``token`` in an HttpOnly cookie."""
    lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    response.set_cookie(ACCESS_COOKIE, str(token), **_cookie_options(lifetime))


def set_refresh_cookie(response, token):
    """Store the refresh ``token`` in an HttpOnly cookie."""
    lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
    response.set_cookie(
        REFRESH_COOKIE, str(token), **_cookie_options(lifetime)
    )


def set_auth_cookies(response, refresh):
    """Store the ``refresh`` token and its access token as cookies."""
    set_access_cookie(response, refresh.access_token)
    set_refresh_cookie(response, refresh)


def delete_auth_cookies(response):
    """Expire both JWT cookies on the client."""
    for name in (ACCESS_COOKIE, REFRESH_COOKIE):
        response.delete_cookie(
            name, path="/", samesite=settings.AUTH_COOKIE_SAMESITE
        )
