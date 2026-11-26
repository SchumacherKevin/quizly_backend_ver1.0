"""Tests for creating quizzes via POST /api/quizzes/ (services mocked)."""

import pytest
from django.urls import reverse

from conftest import TEST_VIDEO_URL
from quiz_app.models import Quiz

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
