"""URL routes for the auth_app API."""

from django.urls import path

from auth_app.api.views import LoginView, LogoutView, RegistrationView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
