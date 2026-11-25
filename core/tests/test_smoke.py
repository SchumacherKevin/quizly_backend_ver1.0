"""Smoke tests ensuring pytest runs against the Django project."""

import pytest
from django.conf import settings


def test_settings_module_is_core():
    """The project settings from the core package are loaded."""
    assert settings.ROOT_URLCONF == "core.urls"


@pytest.mark.django_db
def test_admin_login_page_is_reachable(client):
    """The admin login page responds successfully."""
    response = client.get("/admin/login/")

    assert response.status_code == 200
