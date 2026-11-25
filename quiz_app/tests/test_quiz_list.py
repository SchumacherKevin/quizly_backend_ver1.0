"""Tests for the quiz list endpoint GET /api/quizzes/."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_quiz_list_requires_auth(api_client):
    """Anonymous users get 401 for the quiz list."""
    response = api_client.get(reverse("quiz-list"))

    assert response.status_code == 401


def test_quiz_list_returns_only_own_quizzes(
    auth_client, user, other_user, quiz_factory
):
    """Only the user's quizzes are listed as an array, newest first."""
    first = quiz_factory(user, title="First")
    second = quiz_factory(user, title="Second")
    quiz_factory(other_user, title="Foreign")

    response = auth_client.get(reverse("quiz-list"))

    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert [item["id"] for item in data] == [second.id, first.id]
