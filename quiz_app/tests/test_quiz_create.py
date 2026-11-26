"""Tests for creating quizzes via POST /api/quizzes/ (services mocked)."""

import pytest
from django.urls import reverse

from conftest import TEST_VIDEO_URL
from quiz_app.models import Quiz
from quiz_app.services.exceptions import (
    InvalidVideoError,
    QuizGenerationError,
)

pytestmark = pytest.mark.django_db

QUESTION_DETAIL_KEYS = {
    "id",
    "question_title",
    "question_options",
    "answer",
    "created_at",
    "updated_at",
}


def _post(client, payload):
    """POST ``payload`` as JSON to the quiz list endpoint."""
    return client.post(reverse("quiz-list"), payload, format="json")


def test_create_quiz_returns_201_with_full_quiz(auth_client, user, services):
    """A valid URL yields 201 with the saved quiz incl. timestamps."""
    response = _post(auth_client, {"url": "https://youtu.be/dQw4w9WgXcQ"})

    data = response.json()
    assert response.status_code == 201
    assert Quiz.objects.filter(id=data["id"], owner=user).exists()
    assert data["video_url"] == TEST_VIDEO_URL
    assert len(data["questions"]) == 10
    for question in data["questions"]:
        assert set(question) == QUESTION_DETAIL_KEYS


@pytest.mark.parametrize("url", ["https://vimeo.com/1", "abc"])
def test_create_quiz_rejects_invalid_url(auth_client, services, url):
    """Unsupported URLs give 400 before any service is called."""
    response = _post(auth_client, {"url": url})

    assert response.status_code == 400
    assert Quiz.objects.count() == 0
    services.fetch.assert_not_called()


def test_create_quiz_requires_url(auth_client, services):
    """A missing URL is a field error on ``url``."""
    response = _post(auth_client, {})

    assert response.status_code == 400
    assert "url" in response.json()


def test_create_quiz_rejects_too_long_video(auth_client, services):
    """Videos above the length limit give 400 with a detail message."""
    services.fetch.return_value = {"duration": 3600, "title": "x"}

    response = _post(auth_client, {"url": TEST_VIDEO_URL})

    assert response.status_code == 400
    assert "detail" in response.json()
    assert Quiz.objects.count() == 0


def test_create_quiz_rejects_unavailable_video(auth_client, services):
    """Videos yt-dlp cannot load give 400 with the error message."""
    services.fetch.side_effect = InvalidVideoError("Video not available.")

    response = _post(auth_client, {"url": TEST_VIDEO_URL})

    assert response.status_code == 400
    assert response.json() == {"detail": "Video not available."}


def test_create_quiz_returns_500_on_generation_error(
    auth_client, services, caplog
):
    """Gemini failures give 500, are logged and nothing is saved."""
    error = QuizGenerationError("Quiz generation failed.")
    services.generate.side_effect = error

    response = _post(auth_client, {"url": TEST_VIDEO_URL})

    assert response.status_code == 500
    assert response.json() == {"detail": "Quiz generation failed."}
    assert Quiz.objects.count() == 0
    assert "Quiz generation failed" in caplog.text


def test_create_quiz_returns_500_on_transcription_error(auth_client, services):
    """Whisper failures give 500 with the error message, nothing saved."""
    services.transcribe.side_effect = QuizGenerationError(
        "Transcription failed."
    )

    response = _post(auth_client, {"url": TEST_VIDEO_URL})

    assert response.status_code == 500
    assert response.json() == {"detail": "Transcription failed."}
    assert Quiz.objects.count() == 0


def test_create_quiz_requires_auth(api_client, services):
    """Anonymous users get 401 and no service is called."""
    response = _post(api_client, {"url": TEST_VIDEO_URL})

    assert response.status_code == 401
    services.fetch.assert_not_called()
    services.download.assert_not_called()
    services.transcribe.assert_not_called()
    services.generate.assert_not_called()
    assert Quiz.objects.count() == 0
