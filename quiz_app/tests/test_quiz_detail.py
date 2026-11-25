"""Tests for the quiz detail endpoint GET /api/quizzes/{id}/."""

from django.urls import reverse


def _detail_url(pk):
    """Return the detail URL for the quiz with ``pk``."""
    return reverse("quiz-detail", kwargs={"pk": pk})


def test_quiz_detail_returns_own_quiz(auth_client, user, quiz_factory):
    """The owner can fetch a single quiz with its questions."""
    quiz = quiz_factory(user, questions=2)

    response = auth_client.get(_detail_url(quiz.id))

    data = response.json()
    assert response.status_code == 200
    assert data["id"] == quiz.id
    assert len(data["questions"]) == 2
