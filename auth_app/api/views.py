"""API views for auth_app."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer
from auth_app.utils import authenticate_credentials, build_login_response

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
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return build_login_response(user)


class LogoutView(APIView):
    """Log the current user out."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Confirm the logout."""
        return Response({"detail": LOGOUT_DETAIL})
