"""Tests for the quiz list endpoint GET /api/quizzes/."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_quiz_list_requires_auth(api_client):
    """Anonymous users get 401 for the quiz list."""
    response = api_client.get(reverse("quiz-list"))

    assert response.status_code == 401
