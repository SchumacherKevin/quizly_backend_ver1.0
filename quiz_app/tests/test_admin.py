"""Tests for the Django admin of quiz_app."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_quiz_changelist_loads(admin_client, user, quiz_factory):
    """The quiz list in the admin shows existing quizzes."""
    quiz_factory(user, title="Admin Quiz")

    response = admin_client.get(reverse("admin:quiz_app_quiz_changelist"))

    assert response.status_code == 200
    assert "Admin Quiz" in response.content.decode()
