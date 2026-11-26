"""Tests for the Gemini quiz generation service (no real API calls)."""

import copy

import pytest

from quiz_app.services.exceptions import QuizGenerationError
from quiz_app.services.generation import validate_quiz_data


def test_validate_quiz_data_accepts_valid_quiz(gemini_quiz_data):
    """A complete quiz with 10 valid questions passes validation."""
    validate_quiz_data(gemini_quiz_data)


def _first(data):
    """Return the first question of ``data`` for in-place changes."""
    return data["questions"][0]


def _drop_question(data):
    """Leave only 9 questions."""
    data["questions"].pop()


def _add_question(data):
    """Add an 11th question."""
    data["questions"].append(copy.deepcopy(_first(data)))


def _drop_option(data):
    """Leave the first question with only 3 options."""
    _first(data)["question_options"].pop()


def _empty_option(data):
    """Replace one option of the first question with an empty string."""
    _first(data)["question_options"][1] = ""


def _duplicate_option(data):
    """Repeat the answer as a second option."""
    _first(data)["question_options"][1] = _first(data)["answer"]


def _foreign_answer(data):
    """Use an answer that is not one of the options."""
    _first(data)["answer"] = "Nope"


def _empty_title(data):
    """Clear the quiz title."""
    data["title"] = ""


def _long_title(data):
    """Use a title with 256 characters."""
    data["title"] = "x" * 256


def _empty_question_title(data):
    """Clear the title of the first question."""
    _first(data)["question_title"] = ""


INVALID_CHANGES = [
    _drop_question,
    _add_question,
    _drop_option,
    _empty_option,
    _duplicate_option,
    _foreign_answer,
    _empty_title,
    _long_title,
    _empty_question_title,
]


@pytest.mark.parametrize(
    "change", INVALID_CHANGES, ids=lambda f: f.__name__.strip("_")
)
def test_validate_quiz_data_rejects_invalid(gemini_quiz_data, change):
    """Each broken rule raises ``QuizGenerationError``."""
    data = copy.deepcopy(gemini_quiz_data)
    change(data)

    with pytest.raises(QuizGenerationError):
        validate_quiz_data(data)
