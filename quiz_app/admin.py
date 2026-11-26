"""Admin configuration for quiz_app."""

from django.contrib import admin

from quiz_app.models import Question, Quiz


class QuestionInline(admin.TabularInline):
    """Edit the questions of a quiz directly on the quiz page."""

    model = Question
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin list and edit view for quizzes."""

    list_display = ("id", "title", "owner", "created_at")
    list_filter = ("created_at", "owner")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuestionInline]
