"""API views for quiz_app."""

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.api.permissions import IsOwner
from quiz_app.api.serializers import (
    QuizCreateResponseSerializer,
    QuizCreateSerializer,
    QuizSerializer,
    QuizUpdateSerializer,
)
from quiz_app.models import Quiz
from quiz_app.services.exceptions import QuizlyServiceError
from quiz_app.services.pipeline import create_quiz_from_url
from quiz_app.utils import service_error_response


class QuizListCreateView(ListCreateAPIView):
    """List the quizzes of the current user or create one from a video."""

    serializer_class = QuizSerializer

    def get_queryset(self):
        """Return only the quizzes owned by the current user."""
        return Quiz.objects.filter(owner=self.request.user).prefetch_related(
            "questions"
        )

    def create(self, request, *args, **kwargs):
        """Generate a quiz from the posted YouTube URL (synchronous)."""
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quiz = create_quiz_from_url(
                request.user, serializer.validated_data["url"]
            )
        except QuizlyServiceError as exc:
            return service_error_response(exc)
        return Response(
            QuizCreateResponseSerializer(quiz).data,
            status=status.HTTP_201_CREATED,
        )


class QuizDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, patch or delete a single quiz of the current user.

    The queryset is not filtered by owner on purpose: foreign quizzes
    must return 403 via ``IsOwner`` instead of 404.
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = QuizSerializer
    queryset = Quiz.objects.prefetch_related("questions")
    http_method_names = ["get", "patch", "delete"]

    def update(self, request, *args, **kwargs):
        """Patch title and description, then return the full quiz."""
        quiz = self.get_object()
        serializer = QuizUpdateSerializer(
            quiz, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(QuizSerializer(quiz).data)
