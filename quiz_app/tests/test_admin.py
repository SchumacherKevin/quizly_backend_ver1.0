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


def test_question_changelist_and_change_view_load(
    admin_client, user, quiz_factory
):
    """Single questions can be listed and opened in the admin."""
    question = quiz_factory(user, questions=1).questions.first()
    changelist = reverse("admin:quiz_app_question_changelist")
    change = reverse("admin:quiz_app_question_change", args=[question.pk])

    assert admin_client.get(changelist).status_code == 200
    assert admin_client.get(change).status_code == 200


def test_question_admin_rejects_answer_not_in_options(
    admin_client, user, quiz_factory
):
    """Saving an answer that is not an option re-shows the form."""
    quiz = quiz_factory(user, questions=1)
    question = quiz.questions.first()
    url = reverse("admin:quiz_app_question_change", args=[question.pk])
    payload = {
        "quiz": quiz.pk,
        "question_title": "Q",
        "question_options": '["A", "B", "C", "D"]',
        "answer": "Z",
    }

    response = admin_client.post(url, payload)

    assert response.status_code == 200
    assert "Answer must be one of the options." in response.content.decode()
    question.refresh_from_db()
    assert question.question_title == "Question 0"
    assert question.answer == "A"
