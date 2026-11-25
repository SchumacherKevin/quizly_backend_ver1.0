"""API views for quiz_app."""

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from quiz_app.api.permissions import IsOwner
from quiz_app.api.serializers import QuizSerializer
from quiz_app.models import Quiz


class QuizListCreateView(ListAPIView):
    """List the quizzes of the current user (create follows in step 14)."""

    serializer_class = QuizSerializer

    def get_queryset(self):
        """Return only the quizzes owned by the current user."""
        return Quiz.objects.filter(owner=self.request.user).prefetch_related(
            "questions"
        )


class QuizDetailView(RetrieveAPIView):
    """Retrieve a single quiz (update and delete follow in later cycles).

    The queryset is not filtered by owner on purpose: foreign quizzes
    must return 403 via ``IsOwner`` instead of 404.
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = QuizSerializer
    queryset = Quiz.objects.prefetch_related("questions")
