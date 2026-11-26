"""Tests for the quiz creation pipeline (all external services mocked)."""

from unittest.mock import patch

import pytest
from django.db import IntegrityError

from conftest import TEST_VIDEO_URL
from quiz_app.models import Quiz
from quiz_app.services.pipeline import save_quiz

pytestmark = pytest.mark.django_db

BULK_CREATE_PATH = "quiz_app.services.pipeline.Question.objects.bulk_create"


def test_save_quiz_creates_quiz_with_questions(user, gemini_quiz_data):
    """Quiz and all ten questions are stored for the owner."""
    quiz = save_quiz(user, TEST_VIDEO_URL, gemini_quiz_data)

    quiz.refresh_from_db()
    assert quiz.owner == user
    assert quiz.title == gemini_quiz_data["title"]
    assert quiz.description == gemini_quiz_data["description"]
    assert quiz.video_url == TEST_VIDEO_URL
    assert quiz.questions.count() == 10
    first = quiz.questions.first()
    expected = gemini_quiz_data["questions"][0]
    assert first.question_title == expected["question_title"]
    assert first.question_options == expected["question_options"]
    assert first.answer == expected["answer"]


def test_save_quiz_rolls_back_on_error(user, gemini_quiz_data):
    """If saving the questions fails, the quiz is not kept either."""
    with patch(BULK_CREATE_PATH, side_effect=IntegrityError):
        with pytest.raises(IntegrityError):
            save_quiz(user, TEST_VIDEO_URL, gemini_quiz_data)

    assert Quiz.objects.count() == 0
