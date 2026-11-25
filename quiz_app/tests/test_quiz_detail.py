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


def test_quiz_detail_of_other_user_returns_403(
    auth_client, other_user, quiz_factory
):
    """A quiz owned by someone else is forbidden."""
    quiz = quiz_factory(other_user)

    response = auth_client.get(_detail_url(quiz.id))

    assert response.status_code == 403


def test_quiz_detail_not_found_returns_404(auth_client):
    """A quiz id that does not exist returns 404."""
    response = auth_client.get(_detail_url(9999))

    assert response.status_code == 404


def test_quiz_detail_requires_auth(api_client, user, quiz_factory):
    """Anonymous users get 401 for a quiz detail."""
    quiz = quiz_factory(user)

    response = api_client.get(_detail_url(quiz.id))

    assert response.status_code == 401
