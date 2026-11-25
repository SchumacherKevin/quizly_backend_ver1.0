"""Tests for deleting quizzes via DELETE /api/quizzes/{id}/."""

from django.urls import reverse

from quiz_app.models import Question, Quiz


def _detail_url(pk):
    """Return the detail URL for the quiz with ``pk``."""
    return reverse("quiz-detail", kwargs={"pk": pk})


def test_delete_removes_quiz_and_questions(auth_client, user, quiz_factory):
    """The owner can delete a quiz; its questions are removed too."""
    quiz = quiz_factory(user, questions=2)

    response = auth_client.delete(_detail_url(quiz.id))

    assert response.status_code == 204
    assert response.content == b""
    assert Quiz.objects.count() == 0
    assert Question.objects.count() == 0


def test_delete_other_users_quiz_returns_403(
    auth_client, other_user, quiz_factory
):
    """Deleting someone else's quiz is forbidden and keeps the quiz."""
    quiz = quiz_factory(other_user)

    response = auth_client.delete(_detail_url(quiz.id))

    assert response.status_code == 403
    assert Quiz.objects.filter(id=quiz.id).exists()


def test_delete_missing_quiz_returns_404(auth_client):
    """Deleting a quiz that does not exist returns 404."""
    response = auth_client.delete(_detail_url(9999))

    assert response.status_code == 404


def test_delete_requires_auth(api_client, user, quiz_factory):
    """Anonymous users get 401 when deleting a quiz."""
    quiz = quiz_factory(user)

    response = api_client.delete(_detail_url(quiz.id))

    assert response.status_code == 401
    assert Quiz.objects.filter(id=quiz.id).exists()
