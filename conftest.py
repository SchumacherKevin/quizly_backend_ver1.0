"""Shared pytest fixtures for the Quizly backend."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from quiz_app.models import Question, Quiz

TEST_PASSWORD = "Test1234!"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


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
