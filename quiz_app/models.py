"""Database models for quizzes generated from YouTube videos."""

from django.conf import settings
from django.db import models

from quiz_app.utils import validate_answer, validate_options


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

    class Meta:
        """Show the newest quiz first; the id breaks timestamp ties."""

        ordering = ["-created_at", "-id"]
        verbose_name_plural = "quizzes"

    def __str__(self):
        """Represent the quiz in the admin and shell.

        Returns:
            The quiz title.
        """
        return self.title


class Question(models.Model):
    """A multiple choice question with four options belonging to a quiz."""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_title = models.CharField(max_length=500)
    question_options = models.JSONField()
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Keep questions in the order they were generated."""

        ordering = ["id"]

    def __str__(self):
        """Represent the question in the admin and shell.

        Returns:
            The question title.
        """
        return self.question_title

    def clean(self):
        """Validate the options and that the answer is one of them."""
        validate_options(self.question_options)
        validate_answer(self.answer, self.question_options)
