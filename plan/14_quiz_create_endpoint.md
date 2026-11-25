# 14 – Quiz-Create-Endpoint `POST /api/quizzes/` (Pipeline)

## Ziel
Aus einer YouTube-URL entsteht synchron ein gespeichertes Quiz; die Antwort ist 201 mit dem vollständigen Quiz (User Story 4).

## Kontext (eigenständig)
- **Vorbedingungen:** 02–13 sind fertig. Verfügbar:
  - `quiz_app/services/youtube.py`: `extract_video_id(url)`, `normalize_url(video_id)`, `fetch_video_info(url) -> dict` (`title`, `duration`), `check_duration(info)`, `download_audio(url, target_dir) -> Path`
  - `quiz_app/services/transcription.py`: `transcribe_audio(path) -> str`
  - `quiz_app/services/generation.py`: `generate_quiz(transcript, video_title) -> dict` (`title`, `description`, 10 × `question_title` / `question_options` / `answer`)
  - `quiz_app/services/exceptions.py`: `InvalidVideoError` (→ 400), `QuizGenerationError` (→ 500)
  - `quiz_app/api/views.py`: `QuizListCreateView(ListAPIView)` mit GET; `QuizSerializer` und `QuestionSerializer` (ohne Timestamps)
  - Fixtures: `api_client`, `auth_client` (als `user`), `user`, `gemini_quiz_data`
- Betroffene Dateien: `quiz_app/services/pipeline.py` (neu), `quiz_app/api/serializers.py` (`QuizCreateSerializer`, `QuestionDetailSerializer`, `QuizCreateResponseSerializer`), `quiz_app/api/views.py`, `quiz_app/tests/test_pipeline.py`, `quiz_app/tests/test_quiz_create.py`
- **Vertrag:**
  - Request `{"url": "..."}`
  - 201: vollständiges Quiz; **die Fragen hier mit `created_at` und `updated_at`**
  - 400 bei ungültiger URL, nicht ladbarem Video oder zu langem Video (`{"detail": ...}` bzw. Feldfehler `url`)
  - 401 ohne Login
  - 500 bei Whisper- oder Gemini-Fehlern (`{"detail": ...}`)
- Das Frontend braucht `id` in der Antwort (`library.js:49-59`) und zeigt währenddessen ein Loading-Overlay. Der Request darf lange dauern.
- **Ablauf:**
  1. URL normalisieren
  2. Info laden und Länge prüfen
  3. In einem `TemporaryDirectory` Audio laden und transkribieren
  4. Gemini aufrufen
  5. `save_quiz` atomar ausführen

  Das Temp-Verzeichnis wird durch den Context Manager **immer** gelöscht.
- **Patch-Ziele in Tests:** `quiz_app.services.pipeline.fetch_video_info`, `...pipeline.download_audio`, `...pipeline.transcribe_audio`, `...pipeline.generate_quiz` (dort patchen, wo die Namen benutzt werden)

## Zyklen

### Zyklus 1: `save_quiz` speichert Quiz und Fragen
- **Test:** `quiz_app/tests/test_pipeline.py::test_save_quiz_creates_quiz_with_questions`
  - Act: `quiz = save_quiz(user, "https://www.youtube.com/watch?v=dQw4w9WgXcQ", gemini_quiz_data)`
  - Assert: `quiz.owner == user`, Titel und Beschreibung aus den Daten, `quiz.questions.count() == 10`, die erste Frage entspricht den Daten
- **Erwartetes Rot:** `ModuleNotFoundError: quiz_app.services.pipeline`
- **Green:** `save_quiz(user, video_url, data) -> Quiz` mit `@transaction.atomic`; `Quiz.objects.create(...)`; `Question.objects.bulk_create([...])` über den Helper `_build_questions(quiz, items)`
- **Commit:** `feat(quiz): persist generated quiz atomically`
- [ ] erledigt

### Zyklus 2: Atomarität
- **Test:** `test_save_quiz_rolls_back_on_error`: Mit `patch("quiz_app.services.pipeline.Question.objects.bulk_create", side_effect=IntegrityError)` gilt nach `pytest.raises(IntegrityError)`: `Quiz.objects.count() == 0`
- **Erwartetes Rot:** `Quiz.objects.count() == 1`, falls `atomic` fehlt; sonst schon grün und als Absicherung committen
- **Commit:** `test(quiz): ensure quiz persistence is atomic`
- [ ] erledigt

### Zyklus 3: Orchestrierung `create_quiz_from_url`
- **Test:** `test_create_quiz_from_url_runs_pipeline`
  - Arrange: Die vier Service-Funktionen patchen: `fetch_video_info` liefert `{"title": "Video", "duration": 60}`; `download_audio` liefert `tmp/audio.webm`; `transcribe_audio` liefert `"text"`; `generate_quiz` liefert `gemini_quiz_data`
  - Act: `create_quiz_from_url(user, "https://youtu.be/dQw4w9WgXcQ")`
  - Assert: `fetch_video_info` wurde mit der **normalisierten** URL aufgerufen; `generate_quiz` mit `("text", "Video")`; das zurückgegebene Quiz ist gespeichert und hat `video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"`
- **Erwartetes Rot:** `ImportError: create_quiz_from_url`
- **Green:** `create_quiz_from_url(user, url) -> Quiz` und `_transcribe_video(url) -> str` (mit `TemporaryDirectory`), jeweils ≤ 14 Zeilen
- **Commit:** `feat(quiz): orchestrate quiz generation pipeline`
- [ ] erledigt

### Zyklus 4: Temp-Verzeichnis wird immer gelöscht
- **Test:** `test_pipeline_removes_temp_dir_on_success` und `test_pipeline_removes_temp_dir_on_error`
  - Arrange: `download_audio` als `side_effect` merkt sich `target_dir` und legt dort eine Datei an; im Fehlerfall wirft `transcribe_audio` einen `QuizGenerationError`
  - Assert: `not Path(captured_dir).exists()`; im Fehlerfall zusätzlich `Quiz.objects.count() == 0`
- **Erwartetes Rot:** vermutlich grün durch `TemporaryDirectory`; als Absicherung committen
- **Commit:** `test(quiz): ensure temporary audio files are cleaned up`
- [ ] erledigt

### Zyklus 5: Endpoint 201 mit Fragen-Timestamps
- **Test:** `quiz_app/tests/test_quiz_create.py::test_create_quiz_returns_201_with_full_quiz`
  - Arrange: die vier Service-Funktionen wie in Zyklus 3 patchen
  - Act: `auth_client.post(reverse("quiz-list"), {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}, format="json")`
  - Assert: 201; `data["id"]` existiert in der DB; `len(data["questions"]) == 10`; die Keys jeder Frage sind genau `{"id", "question_title", "question_options", "answer", "created_at", "updated_at"}`; `data["video_url"]` ist normalisiert
- **Erwartetes Rot:** 405 (POST nicht erlaubt)
- **Green:**
  - `QuizListCreateView` wird zu `ListCreateAPIView`
  - `QuizCreateSerializer` (Feld `url`)
  - `QuestionDetailSerializer` erbt von `QuestionSerializer` und ergänzt die Timestamps
  - `QuizCreateResponseSerializer` erbt von `QuizSerializer` und nutzt `questions = QuestionDetailSerializer(many=True)`
  - `create()` validiert, ruft `create_quiz_from_url` auf und antwortet mit 201
- **Commit:** `feat(quiz): add quiz creation endpoint`
- [ ] erledigt

### Zyklus 6: Ungültige Eingaben ergeben 400
- **Test:** `test_create_quiz_rejects_invalid_url` (parametrisiert: `"https://vimeo.com/1"`, `"abc"`): 400, kein Quiz in der DB, und `fetch_video_info` wurde **nicht** aufgerufen
- **Test:** `test_create_quiz_requires_url`: `{}` ergibt 400 mit dem Key `"url"`
- **Test:** `test_create_quiz_rejects_too_long_video`: `fetch_video_info` liefert `{"duration": 3600, "title": "x"}`; Ergebnis 400 mit `"detail"`
- **Test:** `test_create_quiz_rejects_unavailable_video`: `fetch_video_info` wirft `InvalidVideoError("Video not available.")`; Ergebnis 400 mit `{"detail": "Video not available."}`
- **Erwartetes Rot:** 500 oder eine unbehandelte Exception
- **Green:** `validate_url` im Serializer ruft `extract_video_id` auf; die View fängt `InvalidVideoError` ab und gibt 400 `{"detail": str(exc)}` zurück
- **Commit:** `feat(quiz): return 400 for invalid or unsupported videos`
- [ ] erledigt

### Zyklus 7: Pipeline-Fehler ergeben 500
- **Test:** `test_create_quiz_returns_500_on_generation_error`: `generate_quiz` wirft `QuizGenerationError("Quiz generation failed.")`; Ergebnis 500 mit `{"detail": "Quiz generation failed."}`, kein Quiz in der DB
- **Test:** `test_create_quiz_returns_500_on_transcription_error`: analog mit `transcribe_audio`
- **Erwartetes Rot:** unbehandelte Exception
- **Green:** `except QuizGenerationError` gibt 500 zurück; Logging mit `logger.exception(...)` ohne Secrets
- **Commit:** `feat(quiz): return 500 on quiz generation failures`
- [ ] erledigt

### Zyklus 8: Authentifizierung
- **Test:** `test_create_quiz_requires_auth`: `api_client.post(...)` ergibt 401, und keine Service-Funktion wurde aufgerufen
- **Erwartetes Rot:** vermutlich grün; als Absicherung committen
- **Commit:** `test(quiz): require authentication for quiz creation`
- [ ] erledigt

## Manueller Test (nach dem Abschluss-Check, zählt gegen das Gemini-Kontingent)
- [ ] `python manage.py runserver`; Frontend auf `http://127.0.0.1:5500`; Login; ein kurzes Video (1–3 min) eingeben; das Quiz erscheint in der Übersicht

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Status von Schritt 14 auf `[x]` gesetzt (Commit `docs: mark step 14 done`)
- [ ] Stopp → Review
