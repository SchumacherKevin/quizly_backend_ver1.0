"""Local speech-to-text with OpenAI Whisper."""

from functools import lru_cache
from pathlib import Path

import whisper
from django.conf import settings


@lru_cache(maxsize=1)
def get_whisper_model():
    """Load the configured Whisper model once per process."""
    return whisper.load_model(settings.WHISPER_MODEL)


def transcribe_audio(path: Path) -> str:
    """Transcribe the audio file at ``path`` and return the plain text."""
    result = get_whisper_model().transcribe(str(path), fp16=False)
    return result["text"].strip()
