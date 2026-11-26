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


def test_quiz_change_view_shows_question_inline(
    admin_client, user, quiz_factory
):
    """The quiz edit page contains the questions as inline forms."""
    quiz = quiz_factory(user, questions=2)
    url = reverse("admin:quiz_app_quiz_change", args=[quiz.pk])

    response = admin_client.get(url)

    content = response.content.decode()
    assert response.status_code == 200
    assert "questions-TOTAL_FORMS" in content
    assert quiz.questions.first().question_title in content
