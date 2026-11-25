# 14 – Quiz-Create-Endpoint (Pipeline)

## Ziel
`POST /api/quizzes/` verbindet die Pipeline (11 → 12 → 13), speichert das Quiz atomar und antwortet mit 201 und dem vollständigen Quiz (US4).

## Referenzen
- `docs/Endpoint Dokumentation.pdf` – POST /api/quizzes/
- `quizly_frontend/shared/js/api.js:1-24`, `library.js:49-59` – braucht `id`, Loading-Overlay vorhanden

## Aufgaben
- [ ] `quiz_app/api/serializers.py` – `QuizCreateSerializer`: Feld `url` (`URLField`); `validate_url` ruft `extract_video_id` auf und gibt bei `InvalidVideoError` 400 zurück
- [ ] `quiz_app/services/pipeline.py`:
  - `create_quiz_from_url(user, url) -> Quiz`:
    1. `video_url = normalize_url(extract_video_id(url))`
    2. `info = fetch_video_info(video_url)`, dann `check_duration(info)`
    3. `with TemporaryDirectory() as tmp:` → `download_audio`, `transcribe_audio`
    4. `data = generate_quiz(transcript, info["title"])`
    5. `save_quiz(user, video_url, data)`
  - `save_quiz(...)` mit `@transaction.atomic`: `Quiz.objects.create(...)` und `Question.objects.bulk_create(...)`
  - Jede Funktion hat höchstens 14 Zeilen, gegebenenfalls in Teilfunktionen aufteilen
- [ ] `QuizListCreateView.create` (nur die Response-Logik):
  - Serializer validieren → `create_quiz_from_url`
  - `InvalidVideoError` → 400 `{"detail": str(e)}`
  - `QuizGenerationError` → 500 `{"detail": str(e)}`
  - Erfolg → 201 mit `QuizSerializer`, dessen Fragen über `QuestionDetailSerializer` (mit Timestamps) serialisiert werden, z. B. per Serializer-Kontext oder eigener `QuizCreateResponseSerializer`
- [ ] Logging (`logging.getLogger(__name__)`) für Pipeline-Fehler, ohne den API-Key

## Hinweise
- Der Request ist synchron und kann je nach Videolänge 30 s bis mehrere Minuten dauern. Der Dev-Server und das Frontend vertragen das.
- Bei Fehlern wird nichts gespeichert, weil das Speichern erst ganz am Ende atomar passiert.

## Akzeptanzkriterien
- [ ] Gültige URL (Pipeline gemockt) → 201, Quiz und 10 Fragen in der DB, `owner` gesetzt, `video_url` normalisiert
- [ ] Die Response enthält Fragen **mit** `created_at` und `updated_at`
- [ ] Ungültige URL / zu langes Video → 400, kein Quiz in der DB
- [ ] Whisper- oder Gemini-Fehler → 500 mit `detail`, kein Quiz in der DB, Temp-Verzeichnis gelöscht
- [ ] Ohne Login → 401

## Tests
- `quiz_app/tests/test_quiz_create.py`: Services gemockt (`fetch_video_info`, `download_audio`, `transcribe_audio`, `generate_quiz`); alle Akzeptanzkriterien
- `quiz_app/tests/test_pipeline.py`: Reihenfolge der Aufrufe, Atomarität (Fehler in `bulk_create` → kein Quiz)

## Manueller Test
- Ein echtes kurzes Video (1–3 min) über das Frontend erstellen; dabei zählt der Call gegen das Gemini-Kontingent

## Commit-Message
`feat(quiz): add quiz creation pipeline endpoint`
