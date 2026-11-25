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
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create the user with a hashed password."""
        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)
