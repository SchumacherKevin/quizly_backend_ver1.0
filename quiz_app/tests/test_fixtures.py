"""Tests for the shared quiz fixtures in conftest.py."""

import pytest


@pytest.mark.django_db
def test_quiz_factory_creates_quiz_with_questions(quiz_factory, user):
    """The factory creates an owned quiz with valid questions."""
    quiz = quiz_factory(user, questions=3)

    assert quiz.owner == user
    assert quiz.questions.count() == 3
    for question in quiz.questions.all():
        question.full_clean()
