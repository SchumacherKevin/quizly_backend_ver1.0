"""Tests for the quiz creation pipeline (all external services mocked)."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db import IntegrityError

from conftest import TEST_VIDEO_URL
from quiz_app.models import Quiz
from quiz_app.services.pipeline import create_quiz_from_url, save_quiz

pytestmark = pytest.mark.django_db

BULK_CREATE_PATH = "quiz_app.services.pipeline.Question.objects.bulk_create"
PIPELINE = "quiz_app.services.pipeline"
SHORT_URL = "https://youtu.be/dQw4w9WgXcQ"


@pytest.fixture
def services(tmp_path, gemini_quiz_data):
    """Patch all external pipeline services with happy-path results."""
    with (
        patch(f"{PIPELINE}.fetch_video_info") as fetch,
        patch(f"{PIPELINE}.download_audio") as download,
        patch(f"{PIPELINE}.transcribe_audio") as transcribe,
        patch(f"{PIPELINE}.generate_quiz") as generate,
    ):
        fetch.return_value = {"title": "Video", "duration": 60}
        download.return_value = tmp_path / "audio.webm"
        transcribe.return_value = "text"
        generate.return_value = gemini_quiz_data
        yield SimpleNamespace(
            fetch=fetch,
            download=download,
            transcribe=transcribe,
            generate=generate,
        )


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


def test_create_quiz_from_url_runs_pipeline(user, services):
    """The pipeline normalizes the URL, chains the services and saves."""
    quiz = create_quiz_from_url(user, SHORT_URL)

    services.fetch.assert_called_once_with(TEST_VIDEO_URL)
    services.generate.assert_called_once_with("text", "Video")
    assert Quiz.objects.filter(id=quiz.id, owner=user).exists()
    assert quiz.video_url == TEST_VIDEO_URL
    assert quiz.questions.count() == 10
