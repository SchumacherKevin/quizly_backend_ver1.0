"""Shared pytest fixtures for the Quizly backend."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from quiz_app.models import Question, Quiz

TEST_PASSWORD = "Test1234!"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
PIPELINE = "quiz_app.services.pipeline"


@pytest.fixture
def api_client():
    """Return an unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Return the default test user."""
    return User.objects.create_user(
        "testuser", "test@example.com", TEST_PASSWORD
    )


@pytest.fixture
def other_user(db):
    """Return a second user who does not own the default user's data."""
    return User.objects.create_user(
        "otheruser", "other@example.com", TEST_PASSWORD
    )


@pytest.fixture
def auth_client(api_client, user):
    """Return an API client logged in as ``user`` via JWT cookies."""
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    api_client.cookies["refresh_token"] = str(refresh)
    return api_client


def _create_questions(quiz, count):
    """Create ``count`` valid questions for ``quiz``."""
    for i in range(count):
        Question.objects.create(
            quiz=quiz,
            question_title=f"Question {i}",
            question_options=["A", "B", "C", "D"],
            answer="A",
        )


@pytest.fixture
def quiz_factory(db):
    """Return a function that creates a quiz with simple questions."""

    def make(owner, questions=2, title="Test Quiz"):
        """Create a quiz for ``owner`` with ``questions`` questions."""
        quiz = Quiz.objects.create(
            owner=owner,
            title=title,
            description="Test description",
            video_url=TEST_VIDEO_URL,
        )
        _create_questions(quiz, questions)
        return quiz

    return make


def _gemini_question(i):
    """Return one valid generated question with four distinct options."""
    options = [f"Option {i}{letter}" for letter in "ABCD"]
    return {
        "question_title": f"Question {i}?",
        "question_options": options,
        "answer": options[0],
    }


@pytest.fixture
def gemini_quiz_data():
    """Return a valid quiz dict as Gemini would generate it."""
    return {
        "title": "Python Basics",
        "description": "Ein Quiz über Python.",
        "questions": [_gemini_question(i) for i in range(1, 11)],
    }


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
