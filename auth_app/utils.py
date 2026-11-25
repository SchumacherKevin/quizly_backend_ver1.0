"""Helpers for the JWT auth cookies."""

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.api.serializers import UserSerializer

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


def authenticate_credentials(data):
    """Return the user for ``username`` and ``password`` or ``None``."""
    return authenticate(username=data["username"], password=data["password"])


def unauthorized_response(detail):
    """Return a 401 response with the message ``detail``."""
    return Response({"detail": detail}, status=status.HTTP_401_UNAUTHORIZED)


def build_login_response(user):
    """Return the login response for ``user`` with fresh JWT cookies."""
    response = Response(
        {"detail": "Login successfully!", "user": UserSerializer(user).data}
    )
    set_auth_cookies(response, RefreshToken.for_user(user))
    return response


def blacklist_refresh_token(raw_token):
    """Blacklist ``raw_token``; missing or invalid tokens are ignored.

    ``RefreshToken(None)`` would create a brand new token, so ``None``
    has to be handled explicitly.
    """
    if raw_token is None:
        return
    try:
        RefreshToken(raw_token).blacklist()
    except TokenError:
        pass


def refresh_access_token(raw_token):
    """Return a new access token string for the refresh ``raw_token``."""
    return str(RefreshToken(raw_token).access_token)


def delete_auth_cookies(response):
    """Expire both JWT cookies on the client."""
    for name in (ACCESS_COOKIE, REFRESH_COOKIE):
        response.delete_cookie(
            name, path="/", samesite=settings.AUTH_COOKIE_SAMESITE
        )
