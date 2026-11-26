"""Serializers for the auth_app API."""

from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a new user."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        """Expose the fields required for registration."""

        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True, "allow_blank": False},
        }

    def validate_email(self, value):
        """Reject an email that is already used, ignoring case.

        Args:
            value: The submitted email address.

        Returns:
            The unchanged email address.

        Raises:
            ValidationError: If a user with this email already exists.
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_password(self, value):
        """Run Django's configured password validators.

        Args:
            value: The submitted password.

        Returns:
            The unchanged password.

        Raises:
            django.core.exceptions.ValidationError: If a validator rejects
                the password (DRF turns it into a field error).
        """
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        """Ensure both passwords match and drop the confirmation.

        Args:
            attrs: The field values validated so far.

        Returns:
            The attributes without ``confirmed_password``.

        Raises:
            ValidationError: If the passwords do not match.
        """
        confirmed_password = attrs.pop("confirmed_password")
        if attrs["password"] != confirmed_password:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create the user with a hashed password.

        Args:
            validated_data: Username, email and password.

        Returns:
            The newly created user.
        """
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate that username and password are present."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Public user data returned after login."""

    class Meta:
        """Expose only non sensitive user fields."""

        model = User
        fields = ["id", "username", "email"]
