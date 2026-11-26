"""Quiz generation from a transcript with Google Gemini."""


def validate_quiz_data(data: dict) -> None:
    """Ensure the generated quiz matches the expected structure.

    Raises ``QuizGenerationError`` for invalid data (rules follow in the
    next cycle).
    """
