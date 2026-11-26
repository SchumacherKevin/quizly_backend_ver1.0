"""Local speech-to-text with OpenAI Whisper."""

from functools import lru_cache
from pathlib import Path

import whisper
from django.conf import settings

from quiz_app.services.exceptions import QuizGenerationError


@lru_cache(maxsize=1)
def get_whisper_model():
    """Load the configured Whisper model once per process."""
    return whisper.load_model(settings.WHISPER_MODEL)


def _run_whisper(path: Path) -> str:
    """Return the raw Whisper text; any failure becomes a service error."""
    try:
        result = get_whisper_model().transcribe(str(path), fp16=False)
    except Exception as exc:
        raise QuizGenerationError("Transcription failed.") from exc
    return result["text"]


def transcribe_audio(path: Path) -> str:
    """Transcribe the audio file at ``path`` and return the plain text.

    Raises ``QuizGenerationError`` if Whisper fails or returns no text.
    """
    text = _run_whisper(path).strip()
    if not text:
        raise QuizGenerationError("Transcript is empty.")
    return text
