"""Helper functions for the quiz_app."""

import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from quiz_app.services.exceptions import QuizGenerationError

logger = logging.getLogger(__name__)

OPTION_COUNT = 4


def validate_options(options):
    """Ensure the options are a list of four distinct strings.

    Args:
        options: The value of ``question_options``.

    Raises:
        ValidationError: Keyed by ``question_options`` if the value is not
            a list of exactly four unique strings.
    """
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
    """Ensure the answer exactly matches one of the options.

    Args:
        answer: The correct answer text.
        options: The four answer options.

    Raises:
        ValidationError: Keyed by ``answer`` if it is not an option.
    """
    if answer not in options:
        raise ValidationError({"answer": "Answer must be one of the options."})


def service_error_response(exc):
    """Map a pipeline error to a ``{"detail": ...}`` response.

    ``QuizGenerationError`` is logged with traceback; our messages never
    contain secrets. Must be called inside an ``except`` block.

    Args:
        exc: The caught ``QuizlyServiceError``.

    Returns:
        500 for a ``QuizGenerationError``, otherwise 400.
    """
    if isinstance(exc, QuizGenerationError):
        logger.exception("Quiz generation failed: %s", exc)
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        code = status.HTTP_400_BAD_REQUEST
    return Response({"detail": str(exc)}, status=code)
