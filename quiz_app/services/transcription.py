"""Local speech-to-text with OpenAI Whisper."""

from functools import lru_cache
from pathlib import Path

import whisper
from django.conf import settings

from quiz_app.services.exceptions import QuizGenerationError


@lru_cache(maxsize=1)
def get_whisper_model():
    """Load the configured Whisper model once per process.

    Returns:
        The Whisper model named in ``settings.WHISPER_MODEL``.
    """
    return whisper.load_model(settings.WHISPER_MODEL)


def _run_whisper(path: Path) -> str:
    """Run Whisper on the audio file.

    Args:
        path: Path to the audio file.

    Returns:
        The raw transcript text.

    Raises:
        QuizGenerationError: If loading the model or transcribing fails.
    """
    try:
        result = get_whisper_model().transcribe(str(path), fp16=False)
    except Exception as exc:
        raise QuizGenerationError("Transcription failed.") from exc
    return result["text"]


def transcribe_audio(path: Path) -> str:
    """Transcribe an audio file to plain text.

    Args:
        path: Path to the audio file.

    Returns:
        The transcript without surrounding whitespace.

    Raises:
        QuizGenerationError: If Whisper fails or returns no text.
    """
    text = _run_whisper(path).strip()
    if not text:
        raise QuizGenerationError("Transcript is empty.")
    return text
