"""Tests for the Whisper transcription service (no real model)."""

from unittest.mock import patch

import pytest

from quiz_app.services.transcription import get_whisper_model

WHISPER_PATH = "quiz_app.services.transcription.whisper"


@pytest.fixture(autouse=True)
def clear_model_cache():
    """Reset the cached model so every test loads it freshly."""
    get_whisper_model.cache_clear()
    yield
    get_whisper_model.cache_clear()


@pytest.fixture
def whisper_mock():
    """Patch the ``whisper`` module so no real model is loaded."""
    with patch(WHISPER_PATH) as mock_whisper:
        yield mock_whisper


def test_get_whisper_model_loads_configured_model(settings, whisper_mock):
    """The model name comes from ``settings.WHISPER_MODEL``."""
    settings.WHISPER_MODEL = "tiny"

    model = get_whisper_model()

    whisper_mock.load_model.assert_called_once_with("tiny")
    assert model is whisper_mock.load_model.return_value


def test_get_whisper_model_is_cached(whisper_mock):
    """The model is loaded only once per process."""
    first = get_whisper_model()
    second = get_whisper_model()

    assert first is second
    whisper_mock.load_model.assert_called_once()
