"""Database models for quizzes generated from YouTube videos."""

from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """A quiz generated from a YouTube video and owned by a user."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the quiz title."""
        return self.title
