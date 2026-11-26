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
    """Build the shared options for an auth cookie.

    Args:
        lifetime: Token lifetime as ``timedelta``; used as ``max_age``.

    Returns:
        Keyword arguments for ``HttpResponse.set_cookie``.
    """
    return {
        "httponly": True,
        "secure": settings.AUTH_COOKIE_SECURE,
        "samesite": settings.AUTH_COOKIE_SAMESITE,
        "path": "/",
        "max_age": int(lifetime.total_seconds()),
    }


def set_access_cookie(response, token):
    """Store the access token in an HttpOnly cookie.

    Args:
        response: The response that receives the cookie.
        token: The access token (object or string).
    """
    lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    response.set_cookie(ACCESS_COOKIE, str(token), **_cookie_options(lifetime))


def set_refresh_cookie(response, token):
    """Store the refresh token in an HttpOnly cookie.

    Args:
        response: The response that receives the cookie.
        token: The refresh token (object or string).
    """
    lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
    response.set_cookie(
        REFRESH_COOKIE, str(token), **_cookie_options(lifetime)
    )


def set_auth_cookies(response, refresh):
    """Store a refresh token and its access token as cookies.

    Args:
        response: The response that receives the cookies.
        refresh: The ``RefreshToken`` of the user.
    """
    set_access_cookie(response, refresh.access_token)
    set_refresh_cookie(response, refresh)


def authenticate_credentials(data):
    """Check username and password against Django's auth backends.

    Args:
        data: Validated data with ``username`` and ``password``.

    Returns:
        The matching user, or None if the credentials are invalid.
    """
    return authenticate(username=data["username"], password=data["password"])


def unauthorized_response(detail):
    """Build a 401 response.

    Args:
        detail: Message for the ``detail`` key.

    Returns:
        A DRF response with status 401.
    """
    return Response({"detail": detail}, status=status.HTTP_401_UNAUTHORIZED)


def build_login_response(user):
    """Build the login response with fresh JWT cookies.

    Args:
        user: The authenticated user.

    Returns:
        A 200 response with the user data and both auth cookies set.
    """
    response = Response(
        {"detail": "Login successfully!", "user": UserSerializer(user).data}
    )
    set_auth_cookies(response, RefreshToken.for_user(user))
    return response


def blacklist_refresh_token(raw_token):
    """Blacklist a refresh token; missing or invalid tokens are ignored.

    ``RefreshToken(None)`` would create a brand new token, so ``None``
    has to be handled explicitly.

    Args:
        raw_token: The refresh token string from the cookie, or None.
    """
    if raw_token is None:
        return
    try:
        RefreshToken(raw_token).blacklist()
    except TokenError:
        pass


def refresh_access_token(raw_token):
    """Create a new access token from a refresh token.

    Args:
        raw_token: The refresh token string from the cookie.

    Returns:
        The new access token as string.

    Raises:
        TokenError: If the refresh token is invalid, expired or
            blacklisted.
    """
    return str(RefreshToken(raw_token).access_token)


def delete_auth_cookies(response):
    """Expire both JWT cookies on the client.

    Args:
        response: The response that deletes the cookies.
    """
    for name in (ACCESS_COOKIE, REFRESH_COOKIE):
        response.delete_cookie(
            name, path="/", samesite=settings.AUTH_COOKIE_SAMESITE
        )
