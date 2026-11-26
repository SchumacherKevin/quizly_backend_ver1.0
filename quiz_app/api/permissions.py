"""Custom permissions for the quiz_app API."""

from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Allow access only to the owner of the object (403 otherwise)."""

    def has_object_permission(self, request, view, obj):
        """Check whether the requesting user owns the object.

        Args:
            request: The incoming DRF request.
            view: The view handling the request.
            obj: The quiz being accessed.

        Returns:
            True if ``obj.owner`` is the requesting user.
        """
        return obj.owner == request.user
