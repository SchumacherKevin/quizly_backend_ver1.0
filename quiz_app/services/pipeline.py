"""Pipeline: YouTube URL -> audio -> transcript -> quiz -> database."""

from tempfile import TemporaryDirectory

from django.db import transaction

from quiz_app.models import Question, Quiz
from quiz_app.services.generation import generate_quiz
from quiz_app.services.transcription import transcribe_audio
from quiz_app.services.youtube import (
    check_duration,
    download_audio,
    extract_video_id,
    fetch_video_info,
    normalize_url,
)


def _build_questions(quiz: Quiz, items: list) -> list:
    """Return unsaved ``Question`` objects for the generated items."""
    return [
        Question(
            quiz=quiz,
            question_title=item["question_title"],
            question_options=item["question_options"],
            answer=item["answer"],
        )
        for item in items
    ]


@transaction.atomic
def save_quiz(user, video_url: str, data: dict) -> Quiz:
    """Store the generated quiz and its questions in one transaction."""
    quiz = Quiz.objects.create(
        owner=user,
        title=data["title"],
        description=data["description"],
        video_url=video_url,
    )
    Question.objects.bulk_create(_build_questions(quiz, data["questions"]))
    return quiz


def _transcribe_video(url: str) -> str:
    """Download the audio into a temp dir and return its transcript.

    The temporary directory is always removed, even on errors.
    """
    with TemporaryDirectory(prefix="quizly_") as target_dir:
        audio_path = download_audio(url, target_dir)
        return transcribe_audio(audio_path)


def create_quiz_from_url(user, url: str) -> Quiz:
    """Run the full pipeline for ``url`` and return the saved quiz.

    Raises ``InvalidVideoError`` (400) or ``QuizGenerationError`` (500).
    """
    video_url = normalize_url(extract_video_id(url))
    info = fetch_video_info(video_url)
    check_duration(info)
    transcript = _transcribe_video(video_url)
    data = generate_quiz(transcript, info.get("title", ""))
    return save_quiz(user, video_url, data)
