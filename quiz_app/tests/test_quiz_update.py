"""Tests for updating quizzes via PATCH /api/quizzes/{id}/."""

from django.urls import reverse


def _detail_url(pk):
    """Return the detail URL for the quiz with ``pk``."""
    return reverse("quiz-detail", kwargs={"pk": pk})


def _patch(client, quiz_id, payload):
    """Send ``payload`` as JSON PATCH to the quiz detail URL."""
    return client.patch(_detail_url(quiz_id), payload, format="json")


def test_patch_updates_title_and_description(auth_client, user, quiz_factory):
    """Title and description are updated and the full quiz is returned."""
    quiz = quiz_factory(user, questions=2)
    old_updated_at = quiz.updated_at

    response = _patch(
        auth_client, quiz.id, {"title": "New", "description": "Desc"}
    )

    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "New"
    assert data["description"] == "Desc"
    assert len(data["questions"]) == 2
    quiz.refresh_from_db()
    assert quiz.title == "New"
    assert quiz.description == "Desc"
    assert quiz.updated_at > old_updated_at
