# 05 – Models

## Ziel
Datenmodell für Quizze und Fragen. Als User-Modell dient Djangos Standard-`User`.

## Referenzen
- `docs/Endpoint Dokumentation.pdf` – Quiz-Objekt
- `docs/Quizly Checkliste.pdf` – US4 (10 Fragen à 4 Optionen), US6 (Titel und Beschreibung editierbar)

## Aufgaben
- [ ] `quiz_app/models.py`:

**Quiz**
| Feld | Typ |
|---|---|
| `owner` | `ForeignKey(User, on_delete=CASCADE, related_name="quizzes")` |
| `title` | `CharField(max_length=255)` |
| `description` | `TextField(blank=True)` |
| `video_url` | `URLField()` (normalisiert, `watch?v=`) |
| `created_at` | `DateTimeField(auto_now_add=True)` |
| `updated_at` | `DateTimeField(auto_now=True)` |

`Meta.ordering = ["-created_at"]`, `__str__` gibt den Titel zurück.

**Question**
| Feld | Typ |
|---|---|
| `quiz` | `ForeignKey(Quiz, on_delete=CASCADE, related_name="questions")` |
| `question_title` | `CharField(max_length=500)` |
| `question_options` | `JSONField()` (Liste mit 4 Strings) |
| `answer` | `CharField(max_length=255)` |
| `created_at` | `DateTimeField(auto_now_add=True)` |
| `updated_at` | `DateTimeField(auto_now=True)` |

`Meta.ordering = ["id"]`, `__str__` gibt `question_title` zurück.

- [ ] Optional: `Question.clean()` prüft, dass `question_options` genau 4 Strings enthält und `answer` darin vorkommt (greift auch im Admin)
- [ ] `makemigrations` und `migrate`

## Akzeptanzkriterien
- [ ] Wird ein Quiz gelöscht, werden alle seine Fragen mitgelöscht
- [ ] Wird ein User gelöscht, werden seine Quizze mitgelöscht

## Tests
- `quiz_app/tests/test_models.py`: Erstellen, `__str__`, Cascade-Delete, Sortierung, und dass `clean()` eine ungültige `answer` ablehnt

## Commit-Message
`feat(quiz): add Quiz and Question models`
