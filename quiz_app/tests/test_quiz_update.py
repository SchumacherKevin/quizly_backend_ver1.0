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


def test_patch_ignores_read_only_fields(auth_client, user, quiz_factory):
    """Video URL and questions cannot be changed via PATCH."""
    quiz = quiz_factory(user, questions=2)
    old_video_url = quiz.video_url

    response = _patch(
        auth_client,
        quiz.id,
        {"video_url": "https://example.com", "questions": []},
    )

    assert response.status_code == 200
    quiz.refresh_from_db()
    assert quiz.video_url == old_video_url
    assert quiz.questions.count() == 2


def test_patch_rejects_empty_title(auth_client, user, quiz_factory):
    """An empty title is rejected with 400."""
    quiz = quiz_factory(user)

    response = _patch(auth_client, quiz.id, {"title": ""})

    assert response.status_code == 400
    assert "title" in response.json()


def test_put_not_allowed(auth_client, user, quiz_factory):
    """PUT is not supported on the quiz detail endpoint."""
    quiz = quiz_factory(user)

    response = auth_client.put(
        _detail_url(quiz.id), {"title": "New"}, format="json"
    )

    assert response.status_code == 405


def test_patch_other_users_quiz_returns_403(
    auth_client, other_user, quiz_factory
):
    """Patching someone else's quiz is forbidden and changes nothing."""
    quiz = quiz_factory(other_user, title="Foreign")

    response = _patch(auth_client, quiz.id, {"title": "Hacked"})

    assert response.status_code == 403
    quiz.refresh_from_db()
    assert quiz.title == "Foreign"


def test_patch_missing_quiz_returns_404(auth_client):
    """Patching a quiz that does not exist returns 404."""
    response = _patch(auth_client, 9999, {"title": "New"})

    assert response.status_code == 404


def test_patch_requires_auth(api_client, user, quiz_factory):
    """Anonymous users get 401 when patching a quiz."""
    quiz = quiz_factory(user)

    response = _patch(api_client, quiz.id, {"title": "New"})

    assert response.status_code == 401
