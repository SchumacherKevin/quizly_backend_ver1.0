"""API views for quiz_app."""

from rest_framework.generics import ListAPIView

from quiz_app.api.serializers import QuizSerializer
from quiz_app.models import Quiz


class QuizListCreateView(ListAPIView):
    """List the quizzes of the current user (create follows in step 14)."""

    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
