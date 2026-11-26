"""Tests for the Gemini quiz generation service (no real API calls)."""

import copy
import json
from unittest.mock import patch

import pytest

from quiz_app.services.exceptions import QuizGenerationError
from quiz_app.services.generation import (
    MAX_TRANSCRIPT_CHARS,
    build_prompt,
    generate_quiz,
    parse_quiz,
    request_quiz,
    validate_quiz_data,
)


def test_validate_quiz_data_accepts_valid_quiz(gemini_quiz_data):
    """A complete quiz with 10 valid questions passes validation."""
    validate_quiz_data(gemini_quiz_data)


def _first(data):
    """Return the first question of ``data`` for in-place changes."""
    return data["questions"][0]


def _drop_question(data):
    """Leave only 9 questions."""
    data["questions"].pop()


def _add_question(data):
    """Add an 11th question."""
    data["questions"].append(copy.deepcopy(_first(data)))


def _drop_option(data):
    """Leave the first question with only 3 options."""
    _first(data)["question_options"].pop()


def _empty_option(data):
    """Replace one option of the first question with an empty string."""
    _first(data)["question_options"][1] = ""


def _duplicate_option(data):
    """Repeat the answer as a second option."""
    _first(data)["question_options"][1] = _first(data)["answer"]


def _foreign_answer(data):
    """Use an answer that is not one of the options."""
    _first(data)["answer"] = "Nope"


def _empty_title(data):
    """Clear the quiz title."""
    data["title"] = ""


def _long_title(data):
    """Use a title with 256 characters."""
    data["title"] = "x" * 256


def _empty_question_title(data):
    """Clear the title of the first question."""
    _first(data)["question_title"] = ""


INVALID_CHANGES = [
    _drop_question,
    _add_question,
    _drop_option,
    _empty_option,
    _duplicate_option,
    _foreign_answer,
    _empty_title,
    _long_title,
    _empty_question_title,
]


@pytest.mark.parametrize(
    "change", INVALID_CHANGES, ids=lambda f: f.__name__.strip("_")
)
def test_validate_quiz_data_rejects_invalid(gemini_quiz_data, change):
    """Each broken rule raises ``QuizGenerationError``."""
    data = copy.deepcopy(gemini_quiz_data)
    change(data)

    with pytest.raises(QuizGenerationError):
        validate_quiz_data(data)


def test_build_prompt_contains_transcript_and_rules():
    """The prompt carries transcript, video title and the quiz rules."""
    prompt = build_prompt("Python ist eine Sprache.", "Python Intro")

    assert "Python ist eine Sprache." in prompt
    assert "Python Intro" in prompt
    assert "10" in prompt
    assert "4" in prompt
    assert "exactly match one of the options" in prompt


def test_build_prompt_truncates_long_transcript():
    """Overly long transcripts are cut to ``MAX_TRANSCRIPT_CHARS``."""
    head = "a" * MAX_TRANSCRIPT_CHARS
    transcript = head + "#TAIL#" * 100

    prompt = build_prompt(transcript, "Title")

    assert head in prompt
    assert "#TAIL#" not in prompt


def test_parse_quiz_returns_dict(gemini_quiz_data):
    """A JSON object string is parsed into the equivalent dict."""
    assert parse_quiz(json.dumps(gemini_quiz_data)) == gemini_quiz_data


def test_parse_quiz_rejects_invalid_json():
    """Malformed JSON raises ``QuizGenerationError``."""
    with pytest.raises(QuizGenerationError):
        parse_quiz("not json")


def test_parse_quiz_rejects_non_object():
    """Valid JSON that is not an object raises ``QuizGenerationError``."""
    with pytest.raises(QuizGenerationError):
        parse_quiz("[]")


CLIENT_PATH = "quiz_app.services.generation.genai.Client"
FAKE_KEY = "test-secret-key"


@pytest.fixture
def client_cls(settings):
    """Patch ``genai.Client`` and configure a fake key and model."""
    settings.AI_PROVIDER = "gemini"
    settings.GEMINI_API_KEY = FAKE_KEY
    settings.GEMINI_MODEL = "gemini-test"
    with patch(CLIENT_PATH) as mock_cls:
        yield mock_cls


def _generate(client_cls):
    """Return the mocked ``client.models.generate_content``."""
    return client_cls.return_value.models.generate_content


def test_request_quiz_calls_configured_model(client_cls):
    """Gemini is called with key, model and JSON response config."""
    _generate(client_cls).return_value.text = '{"a": 1}'

    raw = request_quiz("prompt")

    assert raw == '{"a": 1}'
    client_cls.assert_called_once_with(api_key=FAKE_KEY)
    kwargs = _generate(client_cls).call_args.kwargs
    assert kwargs["model"] == "gemini-test"
    assert kwargs["contents"] == "prompt"
    assert kwargs["config"]["response_mime_type"] == "application/json"


def test_request_quiz_without_api_key_raises(client_cls, settings):
    """A missing API key fails early without creating a client."""
    settings.GEMINI_API_KEY = ""

    with pytest.raises(
        QuizGenerationError, match="Gemini API key is not configured."
    ):
        request_quiz("prompt")
    client_cls.assert_not_called()


def test_request_quiz_wraps_api_errors(client_cls):
    """API errors are wrapped and never leak the API key."""
    _generate(client_cls).side_effect = Exception(
        f"quota exceeded for {FAKE_KEY}"
    )

    with pytest.raises(QuizGenerationError) as exc_info:
        request_quiz("prompt")
    assert FAKE_KEY not in str(exc_info.value)


def test_generate_quiz_returns_validated_data(client_cls, gemini_quiz_data):
    """A valid Gemini answer is returned as the parsed quiz dict."""
    _generate(client_cls).return_value.text = json.dumps(gemini_quiz_data)

    assert generate_quiz("transcript", "title") == gemini_quiz_data


def test_generate_quiz_raises_on_invalid_answer(client_cls, gemini_quiz_data):
    """An answer that is not one of the options is rejected."""
    _foreign_answer(gemini_quiz_data)
    _generate(client_cls).return_value.text = json.dumps(gemini_quiz_data)

    with pytest.raises(QuizGenerationError):
        generate_quiz("transcript", "title")


def test_generate_quiz_calls_gemini_once(client_cls, gemini_quiz_data):
    """Exactly one Gemini request is made per quiz."""
    _generate(client_cls).return_value.text = json.dumps(gemini_quiz_data)

    generate_quiz("transcript", "title")

    assert _generate(client_cls).call_count == 1


def test_request_quiz_uses_gemini_provider(client_cls, settings):
    """With ``AI_PROVIDER = "gemini"`` the Gemini client is used."""
    settings.AI_PROVIDER = "gemini"
    _generate(client_cls).return_value.text = "{}"

    assert request_quiz("prompt") == "{}"
    client_cls.assert_called_once()


def test_request_quiz_rejects_unknown_provider(client_cls, settings):
    """An unknown provider fails clearly without calling any API."""
    settings.AI_PROVIDER = "foo"

    with pytest.raises(QuizGenerationError, match="Unknown AI provider: foo."):
        request_quiz("prompt")
    client_cls.assert_not_called()


OPENAI_PATH = "quiz_app.services.generation.OpenAI"
LOCAL_BASE_URL = "http://localhost:11434/v1"


@pytest.fixture
def openai_cls(settings):
    """Patch ``OpenAI`` and configure an OpenAI-compatible provider."""
    settings.AI_PROVIDER = "openai"
    settings.OPENAI_API_KEY = FAKE_KEY
    settings.OPENAI_MODEL = "model-test"
    settings.OPENAI_BASE_URL = LOCAL_BASE_URL
    with patch(OPENAI_PATH) as mock_cls:
        yield mock_cls


def _completions(openai_cls):
    """Return the mocked ``client.chat.completions.create``."""
    return openai_cls.return_value.chat.completions.create


def test_request_quiz_calls_openai_compatible_api(openai_cls):
    """Key, base URL, model, prompt and JSON mode are passed on."""
    response = _completions(openai_cls).return_value
    response.choices[0].message.content = '{"a": 1}'

    raw = request_quiz("prompt")

    assert raw == '{"a": 1}'
    openai_cls.assert_called_once_with(
        api_key=FAKE_KEY, base_url=LOCAL_BASE_URL
    )
    kwargs = _completions(openai_cls).call_args.kwargs
    assert kwargs["model"] == "model-test"
    assert kwargs["messages"] == [{"role": "user", "content": "prompt"}]
    assert kwargs["response_format"] == {"type": "json_object"}


def test_request_quiz_openai_allows_missing_key(openai_cls, settings):
    """Local servers (e.g. Ollama) need no key; a placeholder is sent."""
    settings.OPENAI_API_KEY = ""

    request_quiz("prompt")

    assert openai_cls.call_args.kwargs["api_key"]


def test_request_quiz_openai_without_model_raises(openai_cls, settings):
    """Without ``OPENAI_MODEL`` the request fails before any API call."""
    settings.OPENAI_MODEL = ""

    with pytest.raises(
        QuizGenerationError, match="OPENAI_MODEL is not configured."
    ):
        request_quiz("prompt")
    openai_cls.assert_not_called()


def test_request_quiz_openai_wraps_api_errors(openai_cls):
    """API errors are wrapped and never leak the API key."""
    error = Exception(f"invalid key {FAKE_KEY}")
    _completions(openai_cls).side_effect = error

    with pytest.raises(QuizGenerationError) as exc_info:
        request_quiz("prompt")
    assert FAKE_KEY not in str(exc_info.value)
