"""Tests for the quiz_app models."""

import pytest

from quiz_app.models import Question, Quiz

VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
OPTIONS = ["Option A", "Option B", "Option C", "Option D"]


@pytest.fixture
def quiz(user):
    """Return a quiz owned by the default test user."""
    return Quiz.objects.create(owner=user, title="Quiz", video_url=VIDEO_URL)


@pytest.fixture
def question(quiz):
    """Return a valid question belonging to ``quiz``."""
    return Question.objects.create(
        quiz=quiz,
        question_title="What is Python?",
        question_options=OPTIONS,
        answer="Option A",
    )


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


@pytest.mark.django_db
def test_quizzes_ordered_newest_first(user):
    """Quizzes are returned with the newest one first."""
    created = [
        Quiz.objects.create(owner=user, title=f"Quiz {i}", video_url=VIDEO_URL)
        for i in range(3)
    ]

    assert list(Quiz.objects.all()) == list(reversed(created))


@pytest.mark.django_db
def test_question_str_returns_title(question):
    """A question is represented by its title."""
    assert str(question) == "What is Python?"
    assert question.question_options == OPTIONS


@pytest.mark.django_db
def test_deleting_quiz_deletes_questions(quiz, question):
    """Questions are removed together with their quiz."""
    quiz.delete()

    assert Question.objects.count() == 0


@pytest.mark.django_db
def test_deleting_user_deletes_quizzes(user, quiz):
    """Quizzes are removed together with their owner."""
    user.delete()

    assert Quiz.objects.count() == 0
