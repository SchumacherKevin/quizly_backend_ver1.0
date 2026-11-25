"""Serializers for the auth_app API."""

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
        """Reject an email that is already used, ignoring case."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        """Ensure both passwords match and drop the confirmation."""
        confirmed_password = attrs.pop("confirmed_password")
        if attrs["password"] != confirmed_password:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create the user with a hashed password."""
        return User.objects.create_user(**validated_data)
