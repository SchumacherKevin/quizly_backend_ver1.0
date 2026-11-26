"""Quiz generation from a transcript with Google Gemini."""

import json

from django.conf import settings
from django.core.exceptions import ValidationError
from google import genai
from openai import OpenAI
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

Answer with a single JSON object and nothing else, in this format:
{{"title": "...", "description": "...", "questions": [
  {{"question_title": "...",
    "question_options": ["...", "...", "...", "..."],
    "answer": "..."}}
]}}

Video title: {video_title}

Transcript:
{transcript}
"""


def _require_text(value, field: str) -> None:
    """Ensure a value is a non-blank string.

    Args:
        value: The value to check.
        field: Field name used in the error message.

    Raises:
        QuizGenerationError: If ``value`` is not a non-blank string.
    """
    if not isinstance(value, str) or not value.strip():
        raise QuizGenerationError(f"Generated quiz has an empty {field}.")


def _validate_title(data: dict) -> None:
    """Ensure the quiz title is present and fits the model field.

    Args:
        data: The generated quiz dict.

    Raises:
        QuizGenerationError: If the title is empty or too long.
    """
    title = data.get("title")
    _require_text(title, "title")
    if len(title) > MAX_TITLE_LENGTH:
        raise QuizGenerationError("Generated quiz title is too long.")


def _validate_question_count(data: dict) -> None:
    """Ensure the quiz contains exactly ``QUESTION_COUNT`` questions.

    Args:
        data: The generated quiz dict.

    Raises:
        QuizGenerationError: If ``questions`` is no list of that length.
    """
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != QUESTION_COUNT:
        raise QuizGenerationError(
            f"Generated quiz must have {QUESTION_COUNT} questions."
        )


def _validate_question(question: dict) -> None:
    """Ensure title, four distinct non-empty options and a valid answer.

    Args:
        question: One generated question dict.

    Raises:
        QuizGenerationError: If any of these rules is violated.
    """
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

    Args:
        data: The parsed quiz dict from Gemini.

    Raises:
        QuizGenerationError: For any violated rule.
    """
    _validate_title(data)
    _validate_question_count(data)
    for question in data["questions"]:
        _validate_question(question)


def build_prompt(transcript: str, video_title: str) -> str:
    """Build the Gemini prompt; long transcripts are truncated.

    Args:
        transcript: The Whisper transcript.
        video_title: The YouTube video title as extra context.

    Returns:
        The prompt with the quiz rules and at most
        ``MAX_TRANSCRIPT_CHARS`` characters of the transcript.
    """
    return PROMPT_TEMPLATE.format(
        question_count=QUESTION_COUNT,
        option_count=OPTION_COUNT,
        max_title=MAX_TITLE_LENGTH,
        video_title=video_title,
        transcript=transcript[:MAX_TRANSCRIPT_CHARS],
    )


def parse_quiz(raw: str) -> dict:
    """Parse the Gemini JSON answer into a dict.

    Args:
        raw: The JSON text returned by Gemini (may be None).

    Returns:
        The parsed quiz dict.

    Raises:
        QuizGenerationError: For malformed JSON or a non-object.
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
    """Fail early if no Gemini API key is configured.

    Raises:
        QuizGenerationError: If ``settings.GEMINI_API_KEY`` is empty.
    """
    if not settings.GEMINI_API_KEY:
        raise QuizGenerationError("Gemini API key is not configured.")


def _request_gemini(prompt: str) -> str:
    """Send the prompt to Gemini once (no retries).

    Args:
        prompt: The complete prompt from ``build_prompt``.

    Returns:
        The raw JSON text of the response.

    Raises:
        QuizGenerationError: If the key is missing or the API call fails;
            the message never contains the API key.
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


LOCAL_API_KEY = "not-needed"
JSON_MODE = {"type": "json_object"}


def _ensure_openai_model() -> None:
    """Fail early if no model is configured for the OpenAI provider.

    Raises:
        QuizGenerationError: If ``settings.OPENAI_MODEL`` is empty.
    """
    if not settings.OPENAI_MODEL:
        raise QuizGenerationError("OPENAI_MODEL is not configured.")


def _openai_client() -> OpenAI:
    """Create a client for the configured OpenAI-compatible API.

    Returns:
        An ``OpenAI`` client for ``OPENAI_BASE_URL``; local servers get a
        placeholder key because they need none.
    """
    return OpenAI(
        api_key=settings.OPENAI_API_KEY or LOCAL_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )


def _request_openai(prompt: str) -> str:
    """Send the prompt once to an OpenAI-compatible chat API.

    Args:
        prompt: The complete prompt from ``build_prompt``.

    Returns:
        The raw JSON text of the response.

    Raises:
        QuizGenerationError: If the model is missing or the API call
            fails; the message never contains the API key.
    """
    _ensure_openai_model()
    try:
        response = _openai_client().chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format=JSON_MODE,
        )
    except Exception as exc:
        raise QuizGenerationError("AI request failed.") from exc
    return response.choices[0].message.content


PROVIDERS = {"gemini": _request_gemini, "openai": _request_openai}


def request_quiz(prompt: str) -> str:
    """Send the prompt to the AI provider set in ``AI_PROVIDER``.

    Args:
        prompt: The complete prompt from ``build_prompt``.

    Returns:
        The raw JSON text of the response.

    Raises:
        QuizGenerationError: If the provider is unknown or its request
            fails.
    """
    provider = settings.AI_PROVIDER
    send = PROVIDERS.get(provider)
    if send is None:
        raise QuizGenerationError(f"Unknown AI provider: {provider}.")
    return send(prompt)


def generate_quiz(transcript: str, video_title: str) -> dict:
    """Create a validated quiz from a transcript with one Gemini call.

    Args:
        transcript: The Whisper transcript.
        video_title: The YouTube video title.

    Returns:
        Quiz dict with ``title``, ``description`` and 10 questions.

    Raises:
        QuizGenerationError: If any stage fails.
    """
    raw = request_quiz(build_prompt(transcript, video_title))
    data = parse_quiz(raw)
    validate_quiz_data(data)
    return data
