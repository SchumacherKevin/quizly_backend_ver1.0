"""Serializers for the quiz_app API."""

from rest_framework import serializers

from quiz_app.models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    """Full quiz representation returned by the API."""

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
        ]
