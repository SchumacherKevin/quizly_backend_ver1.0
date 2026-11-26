"""Quiz generation from a transcript with Google Gemini."""

from django.core.exceptions import ValidationError

from quiz_app.services.exceptions import QuizGenerationError
from quiz_app.utils import validate_answer, validate_options

QUESTION_COUNT = 10
MAX_TITLE_LENGTH = 255


def _require_text(value, field: str) -> None:
    """Raise if ``value`` is not a non-blank string."""
    if not isinstance(value, str) or not value.strip():
        raise QuizGenerationError(f"Generated quiz has an empty {field}.")


def _validate_title(data: dict) -> None:
    """Ensure the quiz title is present and fits the model field."""
    title = data.get("title")
    _require_text(title, "title")
    if len(title) > MAX_TITLE_LENGTH:
        raise QuizGenerationError("Generated quiz title is too long.")


def _validate_question_count(data: dict) -> None:
    """Ensure the quiz contains exactly ``QUESTION_COUNT`` questions."""
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != QUESTION_COUNT:
        raise QuizGenerationError(
            f"Generated quiz must have {QUESTION_COUNT} questions."
        )


def _validate_question(question: dict) -> None:
    """Ensure title, four distinct non-empty options and a valid answer."""
    _require_text(question.get("question_title"), "question title")
    options = question.get("question_options")
    try:
        validate_options(options)
        validate_answer(question.get("answer"), options)
    except ValidationError as exc:
        raise QuizGenerationError("Generated question is invalid.") from exc
    for option in options:
        _require_text(option, "option")


def validate_quiz_data(data: dict) -> None:
    """Ensure the generated quiz matches the expected structure.

    Raises ``QuizGenerationError`` for any violated rule.
    """
    _validate_title(data)
    _validate_question_count(data)
    for question in data["questions"]:
        _validate_question(question)
