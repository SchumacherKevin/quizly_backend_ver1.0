"""Tests for the quiz creation pipeline (all external services mocked)."""

from pathlib import Path
from unittest.mock import patch

import pytest
from django.db import IntegrityError

from conftest import TEST_VIDEO_URL
from quiz_app.models import Quiz
from quiz_app.services.exceptions import QuizGenerationError
from quiz_app.services.pipeline import create_quiz_from_url, save_quiz

pytestmark = pytest.mark.django_db

BULK_CREATE_PATH = "quiz_app.services.pipeline.Question.objects.bulk_create"
SHORT_URL = "https://youtu.be/dQw4w9WgXcQ"


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


def _capture_target_dir(captured):
    """Return a fake ``download_audio`` that writes a file and records."""

    def fake_download(url, target_dir):
        """Create a dummy audio file in ``target_dir``."""
        captured["dir"] = Path(target_dir)
        audio_path = captured["dir"] / "audio.webm"
        audio_path.write_bytes(b"audio")
        return audio_path

    return fake_download


def test_pipeline_removes_temp_dir_on_success(user, services):
    """The temporary audio folder is gone after a successful run."""
    captured = {}
    services.download.side_effect = _capture_target_dir(captured)

    create_quiz_from_url(user, SHORT_URL)

    assert "dir" in captured
    assert not captured["dir"].exists()


def test_pipeline_removes_temp_dir_on_error(user, services):
    """The temporary audio folder is gone even if transcription fails."""
    captured = {}
    services.download.side_effect = _capture_target_dir(captured)
    services.transcribe.side_effect = QuizGenerationError("boom")

    with pytest.raises(QuizGenerationError):
        create_quiz_from_url(user, SHORT_URL)

    assert "dir" in captured
    assert not captured["dir"].exists()
    assert Quiz.objects.count() == 0
