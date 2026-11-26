# 15 – Admin-Panel

## Ziel
Im Django-Admin lassen sich Quizze (mit Fragen inline) und einzelne Fragen bearbeiten (Checkliste: „Das Admin-Panel wird gepflegt und lässt das Bearbeiten von Quizzes und einzelnen Quizfragen zu“).

## Kontext (eigenständig)
- **Vorbedingungen:** 02–14 sind fertig.
  - Die Models `Quiz` (`owner`, `title`, `description`, `video_url`, Timestamps) und `Question` (`quiz`, `question_title`, `question_options` als JSON, `answer`, Timestamps) existieren.
  - `Question.clean()` prüft 4 Optionen und dass `answer` eine davon ist.
  - Fixtures: `user`, `quiz_factory`; von pytest-django `admin_client` (eingeloggter Superuser).
- Betroffene Dateien: `quiz_app/admin.py`, `quiz_app/tests/test_admin.py`
- Admin-URLs: `reverse("admin:quiz_app_quiz_changelist")`, `reverse("admin:quiz_app_quiz_change", args=[pk])`, analog `quiz_app_question_...`
- Das Feld `question_options` (JSONField) wird im Admin-Formular als JSON-String übergeben, z. B. `'["A", "B", "C", "D"]'`.

## Zyklen

### Zyklus 1: Quiz im Admin registriert
- **Test:** `test_quiz_changelist_loads`: `admin_client.get(changelist)` ergibt 200, und der Quiz-Titel steht im Inhalt
- **Erwartetes Rot:** `NoReverseMatch: admin:quiz_app_quiz_changelist`
- **Green:** `@admin.register(Quiz) class QuizAdmin` mit `list_display = ("id", "title", "owner", "created_at")`, `list_filter`, `search_fields = ("title", "description")`, `readonly_fields = ("created_at", "updated_at")`
- **Commit:** `feat(quiz): register Quiz in admin`
- [x] erledigt

### Zyklus 2: Fragen inline im Quiz
- **Test:** `test_quiz_change_view_shows_question_inline`: Die Change-View ergibt 200, `"questions-TOTAL_FORMS"` steht im Inhalt, ebenso der Titel der ersten Frage
- **Erwartetes Rot:** Das Inline fehlt
- **Green:** `QuestionInline(admin.TabularInline)` mit `model = Question`, `extra = 0`, `readonly_fields` für die Timestamps; `inlines = [QuestionInline]`
- **Commit:** `feat(quiz): edit questions inline in quiz admin`
- [x] erledigt

### Zyklus 3: Fragen einzeln bearbeiten
- **Test:** `test_question_changelist_and_change_view_load`: beide ergeben 200
- **Erwartetes Rot:** `NoReverseMatch`
- **Green:** `@admin.register(Question) class QuestionAdmin` mit `list_display = ("id", "question_title", "quiz")`, `search_fields`, `list_filter = ("quiz",)`
- **Commit:** `feat(quiz): register Question in admin`
- [x] erledigt (zusätzlich `readonly_fields` für die Timestamps, wie bei `QuizAdmin`)

### Zyklus 4: Admin lehnt ungültige Antworten ab
- **Test:** `test_question_admin_rejects_answer_not_in_options`
  - Act: `admin_client.post(question_change_url, {"quiz": quiz.pk, "question_title": "Q", "question_options": '["A", "B", "C", "D"]', "answer": "Z"})`
  - Assert: 200 (das Formular wird erneut angezeigt, kein Redirect), eine Fehlermeldung steht im Inhalt, und die DB ist unverändert
- **Erwartetes Rot:** 302, falls `clean()` nicht greift; sonst grün und als Absicherung committen
- **Commit:** `test(quiz): ensure admin validates question answers`
- [ ] erledigt

## Abschluss-Check
- [ ] Manuell: `python manage.py createsuperuser`; unter `/admin/` ein Quiz und eine Frage bearbeiten
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Status von Schritt 15 auf `[x]` gesetzt (Commit `docs: mark step 15 done`)
- [ ] Stopp → Review
