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
    """Build unsaved questions for the generated items.

    Args:
        quiz: The quiz the questions belong to.
        items: Generated question dicts.

    Returns:
        Unsaved ``Question`` instances for ``bulk_create``.
    """
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
    """Store the generated quiz and its questions in one transaction.

    Args:
        user: Owner of the new quiz.
        video_url: Normalized YouTube watch URL.
        data: Validated quiz dict from Gemini.

    Returns:
        The saved quiz.
    """
    quiz = Quiz.objects.create(
        owner=user,
        title=data["title"],
        description=data["description"],
        video_url=video_url,
    )
    Question.objects.bulk_create(_build_questions(quiz, data["questions"]))
    return quiz


def _transcribe_video(url: str) -> str:
    """Download the audio into a temp dir and transcribe it.

    The temporary directory is always removed, even on errors.

    Args:
        url: Normalized YouTube watch URL.

    Returns:
        The transcript text.
    """
    with TemporaryDirectory(prefix="quizly_") as target_dir:
        audio_path = download_audio(url, target_dir)
        return transcribe_audio(audio_path)


def create_quiz_from_url(user, url: str) -> Quiz:
    """Run the full pipeline and save the resulting quiz.

    Args:
        user: Owner of the new quiz.
        url: YouTube URL in any supported format.

    Returns:
        The saved quiz with its questions.

    Raises:
        InvalidVideoError: If the URL or video is invalid (HTTP 400).
        QuizGenerationError: If transcription or generation fails
            (HTTP 500).
    """
    video_url = normalize_url(extract_video_id(url))
    info = fetch_video_info(video_url)
    check_duration(info)
    transcript = _transcribe_video(video_url)
    data = generate_quiz(transcript, info.get("title", ""))
    return save_quiz(user, video_url, data)
