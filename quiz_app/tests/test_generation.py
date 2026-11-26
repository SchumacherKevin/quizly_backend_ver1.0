"""Tests for the Gemini quiz generation service (no real API calls)."""

from quiz_app.services.generation import validate_quiz_data


def test_validate_quiz_data_accepts_valid_quiz(gemini_quiz_data):
    """A complete quiz with 10 valid questions passes validation."""
    validate_quiz_data(gemini_quiz_data)
