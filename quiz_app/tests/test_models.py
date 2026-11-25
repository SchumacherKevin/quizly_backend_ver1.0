"""Tests for the quiz_app models."""

import pytest

from quiz_app.models import Quiz

VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.mark.django_db
def test_quiz_str_returns_title(user):
    """A quiz is represented by its title and gets timestamps."""
    quiz = Quiz.objects.create(
        owner=user,
        title="Python Basics",
        description="d",
        video_url=VIDEO_URL,
    )

    assert str(quiz) == "Python Basics"
    assert quiz.created_at is not None
    assert quiz.updated_at is not None
