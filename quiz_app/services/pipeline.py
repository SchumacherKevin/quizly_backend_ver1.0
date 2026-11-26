"""Pipeline: YouTube URL -> audio -> transcript -> quiz -> database."""

from django.db import transaction

from quiz_app.models import Question, Quiz


def _build_questions(quiz: Quiz, items: list) -> list:
    """Return unsaved ``Question`` objects for the generated items."""
    return [
        Question(
            quiz=quiz,
            question_title=item["question_title"],
            question_options=item["question_options"],
            answer=item["answer"],
        )
        for item in items
    ]


@transaction.atomic
def save_quiz(user, video_url: str, data: dict) -> Quiz:
    """Store the generated quiz and its questions in one transaction."""
    quiz = Quiz.objects.create(
        owner=user,
        title=data["title"],
        description=data["description"],
        video_url=video_url,
    )
    Question.objects.bulk_create(_build_questions(quiz, data["questions"]))
    return quiz
