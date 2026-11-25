"""Custom permissions for the quiz_app API."""

from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Allow access only to the owner of the object (403 otherwise)."""

    def has_object_permission(self, request, view, obj):
        """Return ``True`` if the requesting user owns ``obj``."""
        return obj.owner == request.user
