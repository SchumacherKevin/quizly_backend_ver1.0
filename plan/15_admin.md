# 15 – Admin-Panel

## Ziel
Im Admin lassen sich Quizze und einzelne Quizfragen bearbeiten (Checkliste, Django-Regeln).

## Referenzen
- `docs/Quizly Checkliste.pdf` – „Das Admin-Panel wird gepflegt und lässt das Bearbeiten von Quizzes und einzelnen Quizfragen zu“

## Aufgaben
- [ ] `quiz_app/admin.py`:
  - `QuestionInline(admin.TabularInline)`: `model = Question`, `extra = 0`, `readonly_fields = ("created_at", "updated_at")`
  - `QuizAdmin`: `list_display = ("id", "title", "owner", "created_at")`, `list_filter = ("owner", "created_at")`, `search_fields = ("title", "description")`, `inlines = [QuestionInline]`, `readonly_fields = ("created_at", "updated_at")`
  - `QuestionAdmin`: `list_display = ("id", "question_title", "quiz")`, `search_fields = ("question_title",)`, `list_filter = ("quiz",)`
- [ ] Die Validierung aus `Question.clean()` (05) greift auch im Admin
- [ ] `createsuperuser` im README dokumentieren

## Akzeptanzkriterien
- [ ] Quiz mit Fragen inline bearbeitbar
- [ ] Einzelne Fragen separat bearbeitbar
- [ ] Ungültige `answer` wird im Admin abgelehnt

## Tests
- `quiz_app/tests/test_admin.py`: Changelist und Change-View für Quiz und Question geben als Superuser 200 zurück

## Commit-Message
`feat(quiz): register Quiz and Question in admin`
