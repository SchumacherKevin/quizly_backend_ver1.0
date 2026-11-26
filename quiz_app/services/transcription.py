"""Local speech-to-text with OpenAI Whisper."""

from functools import lru_cache

import whisper
from django.conf import settings


@lru_cache(maxsize=1)
def get_whisper_model():
    """Load the configured Whisper model once per process."""
    return whisper.load_model(settings.WHISPER_MODEL)
