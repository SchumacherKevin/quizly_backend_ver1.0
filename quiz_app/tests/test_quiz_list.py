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


QUIZ_KEYS = {
    "id",
    "title",
    "description",
    "created_at",
    "updated_at",
    "video_url",
    "questions",
}
QUESTION_KEYS = {"id", "question_title", "question_options", "answer"}


def test_quiz_list_item_shape(auth_client, user, quiz_factory):
    """Quizzes contain nested questions without timestamps."""
    quiz_factory(user, questions=2)

    item = auth_client.get(reverse("quiz-list")).json()[0]

    assert set(item) == QUIZ_KEYS
    assert len(item["questions"]) == 2
    for question in item["questions"]:
        assert set(question) == QUESTION_KEYS
        assert len(question["question_options"]) == 4
