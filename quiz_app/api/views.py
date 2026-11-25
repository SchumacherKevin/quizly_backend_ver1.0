"""API views for quiz_app."""

from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.api.permissions import IsOwner
from quiz_app.api.serializers import QuizSerializer, QuizUpdateSerializer
from quiz_app.models import Quiz


class QuizListCreateView(ListAPIView):
    """List the quizzes of the current user (create follows in step 14)."""

    serializer_class = QuizSerializer

    def get_queryset(self):
        """Return only the quizzes owned by the current user."""
        return Quiz.objects.filter(owner=self.request.user).prefetch_related(
            "questions"
        )


class QuizDetailView(RetrieveUpdateAPIView):
    """Retrieve or patch a single quiz (delete follows in a later cycle).

    The queryset is not filtered by owner on purpose: foreign quizzes
    must return 403 via ``IsOwner`` instead of 404.
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = QuizSerializer
    queryset = Quiz.objects.prefetch_related("questions")
    http_method_names = ["get", "patch"]

    def update(self, request, *args, **kwargs):
        """Patch title and description, then return the full quiz."""
        quiz = self.get_object()
        serializer = QuizUpdateSerializer(
            quiz, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(QuizSerializer(quiz).data)
