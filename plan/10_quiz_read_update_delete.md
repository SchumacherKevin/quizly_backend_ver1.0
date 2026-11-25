# 10 – Quizze lesen, ändern und löschen

## Ziel
`GET /api/quizzes/`, `GET`, `PATCH` und `DELETE` auf `/api/quizzes/{id}/`, beschränkt auf den Owner (US5, US6, US7).

## Referenzen
- `docs/Endpoint Dokumentation.pdf` – Quiz-Endpoints
- `quizly_frontend/shared/js/api.js:26-63` – GET und PATCH
- `quizly_frontend/shared/js/quiz.js:111-118` – DELETE
- `quizly_frontend/shared/js/quizoverview.js:106-120` – PATCH, debounced

## Aufgaben
- [ ] `quiz_app/api/serializers.py`:
  - `QuestionSerializer`: `id`, `question_title`, `question_options`, `answer`
  - `QuestionDetailSerializer(QuestionSerializer)`: zusätzlich `created_at` und `updated_at` (nur für die POST-Response in 14)
  - `QuizSerializer`: `id`, `title`, `description`, `created_at`, `updated_at`, `video_url`, `questions` (read_only, nested)
  - `QuizUpdateSerializer`: nur `title` und `description`; `title` darf nicht leer sein
- [ ] `quiz_app/api/permissions.py` – `IsOwner.has_object_permission`: `obj.owner == request.user`
- [ ] `quiz_app/api/views.py`:
  - `QuizListCreateView(ListCreateAPIView)`: Queryset `Quiz.objects.filter(owner=request.user).prefetch_related("questions")`; `create` folgt in 14
  - `QuizDetailView(RetrieveUpdateDestroyAPIView)`:
    - Queryset `Quiz.objects.all()` (**nicht** nach Owner filtern, damit fremde Quizze 403 statt 404 liefern)
    - `permission_classes = [IsAuthenticated, IsOwner]`
    - `http_method_names = ["get", "patch", "delete"]` (kein PUT)
    - PATCH validiert mit `QuizUpdateSerializer` und antwortet mit `QuizSerializer`
- [ ] `quiz_app/api/urls.py`: `quizzes/` und `quizzes/<int:pk>/`

## Hinweise
- `quiz.js:241-262` ruft unter Umständen `GET quizzes/null/` auf. Mit `<int:pk>` ergibt das 404, und das Frontend kehrt zur Library zurück. Das ist gewollt.
- Für die Liste keine Pagination (Array).

## Akzeptanzkriterien
- [ ] Die Liste enthält nur eigene Quizze, neueste zuerst, als Array
- [ ] Detail eines fremden Quiz → 403; nicht vorhanden → 404; ohne Login → 401
- [ ] PATCH ändert nur `title` und `description`; `video_url` und Fragen bleiben unverändert; `updated_at` ändert sich
- [ ] DELETE → 204, Quiz und Fragen sind gelöscht
- [ ] Fragen in GET- und PATCH-Responses haben **keine** Timestamps

## Tests
- `quiz_app/tests/test_quiz_list.py`, `test_quiz_detail.py`, `test_quiz_update.py`, `test_quiz_delete.py`: Happy Path, 401, 403, 404 und 400 (leerer Titel)

## Commit-Message
`feat(quiz): add list, retrieve, update and delete endpoints`
