# 05 – Models `Quiz` und `Question`

## Ziel
Datenmodell für Quizze und Fragen inklusive Validierung und der Fixture `quiz_factory`.

## Kontext (eigenständig)
- **Vorbedingungen:** 02–04 sind fertig (pytest, Fixtures `user` und `other_user`).
- Betroffene Dateien: `quiz_app/models.py`, Migration, `conftest.py` (`quiz_factory`), `quiz_app/tests/test_models.py`
- Es wird das Standard-User-Modell `django.contrib.auth.models.User` verwendet (über `settings.AUTH_USER_MODEL` referenzieren).
- Fachlich: Ein Quiz hat genau 10 Fragen mit je 4 Optionen. Das Model erzwingt die Anzahl **10 nicht** (das prüft Schritt 13), aber jede Frage muss 4 Optionen haben, und `answer` muss eine davon sein.
- `video_url` wird normalisiert gespeichert (`https://www.youtube.com/watch?v=<ID>`), weil das Frontend nur dieses Format einbetten kann.
- Titel und Beschreibung sind später per PATCH editierbar.

## Zielmodell
**Quiz:** `owner` (FK User, CASCADE, `related_name="quizzes"`), `title` (Char 255), `description` (Text, blank), `video_url` (URLField), `created_at` (auto_now_add), `updated_at` (auto_now); `ordering = ["-created_at"]`

**Question:** `quiz` (FK Quiz, CASCADE, `related_name="questions"`), `question_title` (Char 500), `question_options` (JSONField), `answer` (Char 255), `created_at`, `updated_at`; `ordering = ["id"]`

## Zyklen

### Zyklus 1: Quiz anlegen
- **Test:** `quiz_app/tests/test_models.py::test_quiz_str_returns_title`
  - Arrange: `Quiz.objects.create(owner=user, title="Python Basics", description="d", video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")`
  - Assert: `str(quiz) == "Python Basics"`, `quiz.created_at` und `quiz.updated_at` sind gesetzt
- **Erwartetes Rot:** `ImportError: cannot import name 'Quiz'`
- **Green:** Model `Quiz`, `makemigrations quiz_app`, `__str__`, Docstring
- **Commit:** `feat(quiz): add Quiz model`
- [x] erledigt

### Zyklus 2: Sortierung, neueste zuerst
- **Test:** `test_quizzes_ordered_newest_first`: drei Quizze anlegen, danach liefert `list(Quiz.objects.all())` die umgekehrte Anlage-Reihenfolge
- **Erwartetes Rot:** Die Reihenfolge stimmt nicht
- **Green:** `Meta.ordering = ["-created_at", "-id"]` und eine Migration (`-id` als Tie-Breaker, weil schnell hintereinander angelegte Quizze den gleichen Zeitstempel haben können). Außerdem `verbose_name_plural = "quizzes"` für den Admin.
- **Commit:** `feat(quiz): order quizzes by newest first`
- [x] erledigt

### Zyklus 3: Question anlegen und Cascade
- **Test:** `test_question_str_returns_title`: Frage mit 4 Optionen anlegen, `str(question) == question_title`
- **Test:** `test_deleting_quiz_deletes_questions`: `quiz.delete()` ergibt `Question.objects.count() == 0`
- **Test:** `test_deleting_user_deletes_quizzes`: `user.delete()` ergibt `Quiz.objects.count() == 0`
- **Erwartetes Rot:** `ImportError: Question`
- **Green:** Model `Question` und eine Migration
- **Commit:** `feat(quiz): add Question model with cascade delete`
- [x] erledigt

### Zyklus 4: Validierung von Optionen und Antwort
- **Test:** `test_question_clean_accepts_valid_data`: `question.full_clean()` mit 4 Strings und `answer` in den Optionen wirft keinen Fehler
- **Test:** `test_question_clean_rejects_invalid` (parametrisiert), jeweils mit `pytest.raises(ValidationError)`:
  - 3 Optionen
  - 5 Optionen
  - Optionen kein Array (`"A,B,C,D"`)
  - `answer` nicht in den Optionen
  - doppelte Optionen
  - Option ist kein String (`["A", "B", "C", 4]`), zusätzlich ergänzt
- **Erwartetes Rot:** Es wird kein `ValidationError` geworfen
- **Green:** `Question.clean()` delegiert an kleine Helper in `quiz_app/utils.py` (z. B. `validate_options(options)`, `validate_answer(answer, options)`), jeweils ≤ 14 Zeilen
- **Commit:** `feat(quiz): validate question options and answer`
- [x] erledigt

### Zyklus 5: Fixture `quiz_factory`
- **Test:** `test_quiz_factory_creates_quiz_with_questions`: `quiz_factory(user, questions=3)` ergibt `quiz.owner == user` und `quiz.questions.count() == 3`; jede Frage besteht `full_clean()`
- **Erwartetes Rot:** `fixture 'quiz_factory' not found`
- **Green:** In `conftest.py` eine Fixture, die eine Funktion `make(owner, questions=2, title="Test Quiz")` zurückgibt. Fragen: `question_title=f"Question {i}"`, Optionen `["A", "B", "C", "D"]`, `answer="A"`.
- **Refactor:** Das Anlegen der Fragen ist in `_create_questions(quiz, count)` ausgelagert (≤ 14 Zeilen); die lokale `quiz`-Fixture in `test_models.py` nutzt `quiz_factory(user, questions=0)`
- **Commit:** `test(quiz): add quiz_factory fixture`
- [x] erledigt

## Abschluss-Check
- [x] `python manage.py makemigrations --check` meldet keine fehlenden Migrationen
- [x] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [x] Status von Schritt 05 auf `[x]` gesetzt (Commit `docs: mark step 05 done`)
- [x] Stopp → Review
