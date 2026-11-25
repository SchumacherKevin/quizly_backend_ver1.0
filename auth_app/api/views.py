"""API views for auth_app."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer
from auth_app.utils import (
    REFRESH_COOKIE,
    authenticate_credentials,
    blacklist_refresh_token,
    build_login_response,
    delete_auth_cookies,
    refresh_access_token,
    set_access_cookie,
    unauthorized_response,
)

LOGOUT_DETAIL = (
    "Log-Out successfully! All Tokens will be deleted. "
    "Refresh token is now invalid."
)


class RegistrationView(APIView):
    """Register a new user without logging them in."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Create a user from the posted registration data."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Log a user in with username and password."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Return user data and cookies, or a generic 401.

        The 401 is returned explicitly: with ``authentication_classes = []``
        DRF would turn ``AuthenticationFailed`` into a 403.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_credentials(serializer.validated_data)
        if user is None:
            return unauthorized_response("Invalid username or password.")
        return build_login_response(user)


class LogoutView(APIView):
    """Log the current user out."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist the refresh token and delete the auth cookies."""
        blacklist_refresh_token(request.COOKIES.get(REFRESH_COOKIE))
        response = Response({"detail": LOGOUT_DETAIL})
        delete_auth_cookies(response)
        return response


class CookieTokenRefreshView(APIView):
    """Issue a new access cookie from the refresh cookie."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Set a fresh access cookie or answer 401 explicitly.

        Explicit 401 responses are needed because DRF would turn auth
        errors into 403 when ``authentication_classes`` is empty.
        """
        raw_token = request.COOKIES.get(REFRESH_COOKIE)
        if raw_token is None:
            return unauthorized_response("Refresh token not found.")
        try:
            access_token = refresh_access_token(raw_token)
        except TokenError:
            return unauthorized_response("Refresh token invalid.")
        response = Response({"detail": "Token refreshed"})
        set_access_cookie(response, access_token)
        return response
