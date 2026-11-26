"""Serializers for the quiz_app API."""

from rest_framework import serializers

from quiz_app.models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    """Question representation without timestamps (GET and PATCH)."""

    class Meta:
        """Expose the question fields from the API contract."""

        model = Question
        fields = ["id", "question_title", "question_options", "answer"]


class QuizSerializer(serializers.ModelSerializer):
    """Full quiz representation with its nested questions."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        """Expose the quiz fields from the API contract."""

        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]


class QuizUpdateSerializer(serializers.ModelSerializer):
    """Validate PATCH input; only title and description are editable."""

    class Meta:
        """Restrict writable fields to title and description."""

        model = Quiz
        fields = ["title", "description"]


class QuizCreateSerializer(serializers.Serializer):
    """Validate the POST input: the YouTube URL of the video."""

    url = serializers.CharField()


class QuestionDetailSerializer(QuestionSerializer):
    """Question representation with timestamps (POST response only)."""

    class Meta(QuestionSerializer.Meta):
        """Add the timestamps to the default question fields."""

        fields = QuestionSerializer.Meta.fields + ["created_at", "updated_at"]


class QuizCreateResponseSerializer(QuizSerializer):
    """Quiz representation returned after creation (with timestamps)."""

    questions = QuestionDetailSerializer(many=True, read_only=True)
