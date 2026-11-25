"""URL routes for the quiz_app API."""

from django.urls import path

from quiz_app.api.views import QuizListCreateView

urlpatterns = [
    path("quizzes/", QuizListCreateView.as_view(), name="quiz-list"),
]
