"""Tests for the project settings loaded from the environment."""

from django.conf import settings


def test_quizly_settings_have_expected_types():
    """Quizly specific settings exist with the expected types."""
    assert isinstance(settings.MAX_VIDEO_MINUTES, int)
    assert isinstance(settings.WHISPER_MODEL, str)
    assert isinstance(settings.GEMINI_MODEL, str)
    assert hasattr(settings, "GEMINI_API_KEY")


def test_secret_key_not_hardcoded_default():
    """The secret key is not the generated insecure default."""
    assert not settings.SECRET_KEY.startswith("django-insecure-")
