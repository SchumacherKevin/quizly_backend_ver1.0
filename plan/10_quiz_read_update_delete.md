# 10 – Quizze lesen, ändern und löschen

## Ziel
- `GET /api/quizzes/`
- `GET`, `PATCH` und `DELETE` auf `/api/quizzes/{id}/`
Nur für den Owner (User Stories 5–7).

## Kontext (eigenständig)
- **Vorbedingungen:** 02–09 sind fertig.
  - Models `Quiz` und `Question` existieren (`related_name="questions"`, `ordering ["-created_at"]`).
  - Fixtures: `api_client`, `auth_client` (eingeloggt als `user`), `user`, `other_user`, `quiz_factory(owner, questions=2)`.
- Betroffene Dateien: `quiz_app/api/serializers.py`, `quiz_app/api/permissions.py`, `quiz_app/api/views.py`, `quiz_app/api/urls.py`, `quiz_app/tests/test_quiz_list.py`, `test_quiz_detail.py`, `test_quiz_update.py`, `test_quiz_delete.py`
- URL-Namen: `quiz-list` (`quizzes/`), `quiz-detail` (`quizzes/<int:pk>/`)
- **Vertrag:**
  - Quiz-Objekt: `id`, `title`, `description`, `created_at`, `updated_at`, `video_url`, `questions[]`
  - Jede Frage hat `id`, `question_title`, `question_options`, `answer`; in GET und PATCH **ohne** Timestamps. Die Variante mit Timestamps braucht nur POST (Schritt 14).
  - Die Liste ist ein **unpaginiertes Array**, nur eigene Quizze, neueste zuerst.
  - Fremdes Quiz → **403**, nicht vorhanden → 404, ohne Login → 401.
  - PATCH ändert nur `title` und `description`; ein leerer Titel ergibt 400. DELETE ergibt 204 ohne Body.
- **Entscheidung 403:** Im Detail-View ist das Queryset `Quiz.objects.all()`, und die Ownership prüft `IsOwner.has_object_permission`. Bei einem Queryset-Filter käme 404 statt 403.
- Frontend: PATCH sendet immer beide Felder, mit 1 s Debounce (`quizoverview.js:106-120`). `GET quizzes/null/` kommt vor und muss 404 ergeben; das ist durch `<int:pk>` gegeben.
- Den POST (Quiz erstellen) baut Schritt 14. Hier ist die Listen-View deshalb zunächst eine `ListAPIView` namens `QuizListCreateView` (wird in 14 erweitert).

## Zyklen – Liste

### Zyklus 1: Liste erfordert Login
- **Test:** `test_quiz_list_requires_auth`: `api_client.get(reverse("quiz-list"))` ergibt 401
- **Erwartetes Rot:** `NoReverseMatch: 'quiz-list'`
- **Green:** `QuizListCreateView(ListAPIView)`, `QuizSerializer`, URL
- **Commit:** `feat(quiz): add quiz list endpoint`
- [x] erledigt

### Zyklus 2: Liste enthält nur eigene Quizze als Array
- **Test:** `test_quiz_list_returns_only_own_quizzes`: 2 Quizze für `user` und 1 für `other_user` ergeben 200, `isinstance(data, list)`, `len == 2`, und die IDs sind die eigenen in der Reihenfolge neueste zuerst
- **Erwartetes Rot:** `len == 3`
- **Green:** `get_queryset` filtert `owner=self.request.user` mit `.prefetch_related("questions")`
- **Commit:** `feat(quiz): restrict quiz list to owner`
- [x] erledigt

### Zyklus 3: Struktur des Quiz-Objekts
- **Test:** `test_quiz_list_item_shape`
  - Die Keys des Quiz sind genau `{"id", "title", "description", "created_at", "updated_at", "video_url", "questions"}`
  - Die Keys jeder Frage sind genau `{"id", "question_title", "question_options", "answer"}`
  - `question_options` ist eine Liste mit 4 Einträgen
- **Erwartetes Rot:** abweichende Keys
- **Green:** `QuestionSerializer` (ohne Timestamps) und nested `questions` (read_only) im `QuizSerializer`
- **Commit:** `feat(quiz): serialize quizzes with nested questions`
- [x] erledigt

## Zyklen – Detail

### Zyklus 4: Eigenes Quiz abrufen
- **Test:** `test_quiz_detail_returns_own_quiz`: 200 und `data["id"] == quiz.id`, `len(data["questions"]) == 2`
- **Erwartetes Rot:** `NoReverseMatch: 'quiz-detail'`
- **Green:** `QuizDetailView(RetrieveAPIView)`, Queryset `Quiz.objects.prefetch_related("questions")`. Bewusst noch nicht `RetrieveUpdateDestroyAPIView`, damit PATCH (Zyklus 6) und DELETE (Zyklus 9) nicht ungetestet freigeschaltet werden; die Klasse wird dort erweitert.
- **Commit:** `feat(quiz): add quiz detail endpoint`
- [x] erledigt

### Zyklus 5: Fremdes Quiz, nicht vorhanden, ohne Login
- **Test:** `test_quiz_detail_of_other_user_returns_403`: Quiz von `other_user` ergibt **403**
- **Test:** `test_quiz_detail_not_found_returns_404`: `pk=9999` ergibt 404
- **Test:** `test_quiz_detail_requires_auth`: ohne Login 401
- **Erwartetes Rot:** 200 statt 403
- **Green:** `IsOwner(BasePermission).has_object_permission` gibt `obj.owner == request.user` zurück; `permission_classes = [IsAuthenticated, IsOwner]`
- **Commit:** `feat(quiz): restrict quiz detail to owner with 403`
- [x] erledigt (404 und 401 waren schon vorher grün)

## Zyklen – Update

### Zyklus 6: Titel und Beschreibung patchen
- **Test:** `test_patch_updates_title_and_description`
  - Act: `auth_client.patch(url, {"title": "New", "description": "Desc"}, format="json")`
  - Assert: 200, die Response enthält die neuen Werte und **das vollständige Quiz** (inklusive `questions`); in der DB ist der Wert aktualisiert, und `updated_at` ist größer als vorher
- **Erwartetes Rot:** 405 bzw. kein Update
- **Green:** `QuizUpdateSerializer` (Felder `title`, `description`); in `update` validieren, speichern und mit `QuizSerializer` antworten; `http_method_names = ["get", "patch", "delete"]`
- **Hinweis:** `QuizDetailView` erbt jetzt von `RetrieveUpdateAPIView` mit `http_method_names = ["get", "patch"]`; `"delete"` kommt in Zyklus 9 dazu.
- **Commit:** `feat(quiz): allow patching quiz title and description`
- [x] erledigt

### Zyklus 7: Nur erlaubte Felder, leerer Titel, PUT
- **Test:** `test_patch_ignores_read_only_fields`: Mit `{"video_url": "https://example.com", "questions": []}` bleiben `video_url` und die Fragen unverändert
- **Test:** `test_patch_rejects_empty_title`: `{"title": ""}` ergibt 400 mit dem Key `"title"`
- **Test:** `test_put_not_allowed`: PUT ergibt 405
- **Erwartetes Rot:** einzeln prüfen, was rot ist
- **Ergebnis:** alle drei sofort grün (`QuizUpdateSerializer` kennt nur `title`/`description`, `CharField` verbietet leere Werte, `http_method_names` schließt PUT aus). Deshalb als Absicherung mit `test(...)` committet.
- **Commit:** `test(quiz): cover quiz patch input validation`
- [x] erledigt

### Zyklus 8: PATCH auf fremde oder fehlende Quizze
- **Test:** `test_patch_other_users_quiz_returns_403`, `test_patch_missing_quiz_returns_404`, `test_patch_requires_auth` (401); beim 403-Fall bleibt die DB unverändert
- **Erwartetes Rot:** vermutlich grün durch Zyklus 5; als Absicherung committen
- **Commit:** `test(quiz): cover patch permissions`
- [x] erledigt (wie erwartet sofort grün, Absicherungstests)

## Zyklen – Delete

### Zyklus 9: Quiz löschen
- **Test:** `test_delete_removes_quiz_and_questions`: 204, `response.content == b""`, `Quiz.objects.count() == 0` und `Question.objects.count() == 0`
- **Test:** `test_delete_other_users_quiz_returns_403` (das Quiz existiert danach noch), `test_delete_missing_quiz_returns_404`, `test_delete_requires_auth` (401)
- **Erwartetes Rot:** vermutlich nur der Happy Path, falls DELETE nicht erlaubt ist
- **Commit:** `feat(quiz): allow owners to delete quizzes`
- [ ] erledigt

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Status von Schritt 10 auf `[x]` gesetzt (Commit `docs: mark step 10 done`)
- [ ] Stopp → Review
