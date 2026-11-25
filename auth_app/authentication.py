"""DRF authentication that reads the JWT from an HttpOnly cookie."""

from rest_framework_simplejwt.authentication import JWTAuthentication

from auth_app.utils import ACCESS_COOKIE


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests with the ``access_token`` cookie."""

    def authenticate(self, request):
        """Return ``(user, token)`` or ``None`` without an access cookie."""
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
