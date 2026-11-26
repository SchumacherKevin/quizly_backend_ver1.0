"""Quiz generation from a transcript with Google Gemini."""

import json

from django.conf import settings
from django.core.exceptions import ValidationError
from google import genai
from pydantic import BaseModel

from quiz_app.services.exceptions import QuizGenerationError
from quiz_app.utils import OPTION_COUNT, validate_answer, validate_options

QUESTION_COUNT = 10
MAX_TITLE_LENGTH = 255
MAX_TRANSCRIPT_CHARS = 30000
PROMPT_TEMPLATE = """You create a quiz from the transcript of a YouTube video.

Rules:
- Write exactly {question_count} questions.
- Every question has exactly {option_count} distinct, non-empty options.
- The "answer" must exactly match one of the options, character by character.
- "title" is a short quiz title (at most {max_title} characters).
- "description" summarizes the quiz in 1-2 sentences.
- Use the language of the transcript.
- Only ask about content of the transcript.

Video title: {video_title}

Transcript:
{transcript}
"""


def _require_text(value, field: str) -> None:
    """Raise if ``value`` is not a non-blank string."""
    if not isinstance(value, str) or not value.strip():
        raise QuizGenerationError(f"Generated quiz has an empty {field}.")


def _validate_title(data: dict) -> None:
    """Ensure the quiz title is present and fits the model field."""
    title = data.get("title")
    _require_text(title, "title")
    if len(title) > MAX_TITLE_LENGTH:
        raise QuizGenerationError("Generated quiz title is too long.")


def _validate_question_count(data: dict) -> None:
    """Ensure the quiz contains exactly ``QUESTION_COUNT`` questions."""
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != QUESTION_COUNT:
        raise QuizGenerationError(
            f"Generated quiz must have {QUESTION_COUNT} questions."
        )


def _validate_question(question: dict) -> None:
    """Ensure title, four distinct non-empty options and a valid answer."""
    _require_text(question.get("question_title"), "question title")
    options = question.get("question_options")
    try:
        validate_options(options)
        validate_answer(question.get("answer"), options)
    except ValidationError as exc:
        raise QuizGenerationError("Generated question is invalid.") from exc
    for option in options:
        _require_text(option, "option")


def validate_quiz_data(data: dict) -> None:
    """Ensure the generated quiz matches the expected structure.

    Raises ``QuizGenerationError`` for any violated rule.
    """
    _validate_title(data)
    _validate_question_count(data)
    for question in data["questions"]:
        _validate_question(question)


def build_prompt(transcript: str, video_title: str) -> str:
    """Return the Gemini prompt; long transcripts are truncated."""
    return PROMPT_TEMPLATE.format(
        question_count=QUESTION_COUNT,
        option_count=OPTION_COUNT,
        max_title=MAX_TITLE_LENGTH,
        video_title=video_title,
        transcript=transcript[:MAX_TRANSCRIPT_CHARS],
    )


def parse_quiz(raw: str) -> dict:
    """Parse the Gemini JSON answer into a dict.

    Raises ``QuizGenerationError`` for malformed JSON or a non-object.
    """
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise QuizGenerationError("Gemini returned invalid JSON.") from exc
    if not isinstance(data, dict):
        raise QuizGenerationError("Gemini returned no quiz object.")
    return data


class QuestionSchema(BaseModel):
    """Response schema of a single generated question."""

    question_title: str
    question_options: list[str]
    answer: str


class QuizSchema(BaseModel):
    """Response schema Gemini must follow for the whole quiz."""

    title: str
    description: str
    questions: list[QuestionSchema]


GENERATION_CONFIG = {
    "response_mime_type": "application/json",
    "response_schema": QuizSchema,
}


def _ensure_api_key() -> None:
    """Fail early if no Gemini API key is configured."""
    if not settings.GEMINI_API_KEY:
        raise QuizGenerationError("Gemini API key is not configured.")


def request_quiz(prompt: str) -> str:
    """Send ``prompt`` to Gemini once and return the raw JSON text.

    Any API error becomes a ``QuizGenerationError`` without the key.
    """
    _ensure_api_key()
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=GENERATION_CONFIG,
        )
    except Exception as exc:
        raise QuizGenerationError("Gemini request failed.") from exc
    return response.text


def generate_quiz(transcript: str, video_title: str) -> dict:
    """Create a validated quiz dict from a transcript with one Gemini call.

    Raises ``QuizGenerationError`` if any stage fails.
    """
    raw = request_quiz(build_prompt(transcript, video_title))
    data = parse_quiz(raw)
    validate_quiz_data(data)
    return data
