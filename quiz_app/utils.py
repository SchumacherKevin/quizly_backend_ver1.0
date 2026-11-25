"""Helper functions for the quiz_app."""

from django.core.exceptions import ValidationError

OPTION_COUNT = 4


def validate_options(options):
    """Ensure ``options`` is a list of four distinct strings."""
    if not isinstance(options, list) or len(options) != OPTION_COUNT:
        raise ValidationError(
            {"question_options": "Exactly 4 options are required."}
        )
    if not all(isinstance(option, str) for option in options):
        raise ValidationError(
            {"question_options": "All options must be strings."}
        )
    if len(set(options)) != OPTION_COUNT:
        raise ValidationError({"question_options": "Options must be unique."})


def validate_answer(answer, options):
    """Ensure ``answer`` exactly matches one of the ``options``."""
    if answer not in options:
        raise ValidationError({"answer": "Answer must be one of the options."})
