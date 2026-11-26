"""Exceptions raised by the quiz generation services."""


class QuizlyServiceError(Exception):
    """Base class for all service errors."""


class InvalidVideoError(QuizlyServiceError):
    """The video URL is invalid, not loadable or too long (HTTP 400)."""


class QuizGenerationError(QuizlyServiceError):
    """Transcription or quiz generation failed (HTTP 500)."""
