"""API views for auth_app."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
)
from auth_app.utils import authenticate_credentials


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
        """Return the user data for valid credentials."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_credentials(serializer.validated_data)
        return Response(
            {
                "detail": "Login successfully!",
                "user": UserSerializer(user).data,
            }
        )
