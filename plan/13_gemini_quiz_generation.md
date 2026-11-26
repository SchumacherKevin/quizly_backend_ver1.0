# 13 – Gemini-Service (Quizgenerierung)

## Ziel
`quiz_app/services/generation.py` erzeugt aus Transkript und Videotitel mit **einem** Gemini-Call ein validiertes Quiz-Dict:
`{"title": str, "description": str, "questions": [{"question_title": str, "question_options": [4 × str], "answer": str}, × 10]}`

## Kontext (eigenständig)
- **Vorbedingungen:** 02–12 sind fertig. `google-genai` ist installiert (bringt `pydantic` mit). In den Settings gibt es `GEMINI_API_KEY` und `GEMINI_MODEL`, in `quiz_app/services/exceptions.py` `QuizGenerationError`.
- Betroffene Dateien: `quiz_app/services/generation.py` (neu), `conftest.py` (`gemini_quiz_data`), `quiz_app/tests/test_generation.py`
- Fachlich (US4): genau 10 Fragen, je 4 eindeutige, nicht leere Optionen; `answer` ist **exakt** eine der Optionen (das Frontend vergleicht den Text); Titel ≤ 255 Zeichen; Beschreibung in 1–2 Sätzen; die Sprache folgt dem Transkript.
- Das Free Tier ist sehr knapp (vermutlich ca. 5 RPM / 20 RPD). Deshalb: 1 Call pro Quiz, keine Retries, in Tests **immer** mocken (`quiz_app.services.generation.genai.Client`).
- Der API-Key erscheint nie in Logs, Exceptions oder Responses.
- SDK-Aufruf (google-genai):
  ```python
  client = genai.Client(api_key=settings.GEMINI_API_KEY)
  response = client.models.generate_content(
      model=settings.GEMINI_MODEL,
      contents=prompt,
      config={"response_mime_type": "application/json", "response_schema": QuizSchema},
  )
  response.text  # JSON-String
  ```

## Zyklus 0 (manuell, Kevin): Modell verifizieren
- [x] In Google AI Studio (https://aistudio.google.com) den API-Key anlegen bzw. prüfen
- [x] Unter „Rate Limits“ prüfen, welches Flash-Modell im Free Tier verfügbar ist. Die Recherche vom 25.11.2026 ergab vermutlich `gemini-3.8-flash`, das ist aber nicht offiziell bestätigt.
- [x] `GEMINI_MODEL` in `.env` und `.env.template` eintragen und `GEMINI_API_KEY` in `.env` (Kevin hat am 26.11.2026 bestätigt, dass `gemini-3.8-flash` korrekt ist; das Template war schon richtig, deshalb kein `chore`-Commit nötig)
- **Commit (falls sich das Template ändert):** `chore: set verified gemini model in env template`

## Zyklen

### Zyklus 1: Fixture `gemini_quiz_data` und Validierung des Happy Path
- **Test:** `test_validate_quiz_data_accepts_valid_quiz`: `validate_quiz_data(gemini_quiz_data)` wirft keinen Fehler
- **Erwartetes Rot:** `fixture 'gemini_quiz_data' not found` bzw. `ModuleNotFoundError`
- **Green:**
  - `conftest.py`: `gemini_quiz_data()` liefert `{"title": "Python Basics", "description": "Ein Quiz über Python.", "questions": [...]}` mit 10 Fragen, jeweils `question_options = [f"Option {i}A", ..., f"Option {i}D"]` und `answer = f"Option {i}A"`
  - `validate_quiz_data(data: dict) -> None`
- **Commit:** `feat(quiz): validate generated quiz data`
- [x] erledigt (Fake-it: `validate_quiz_data` ist noch ein No-op; Zyklus 2 ergänzt die Regeln. Fixture mit Helper `_gemini_question(i)`, Fragen 1–10)

### Zyklus 2: Ungültige Quizdaten
- **Test:** `test_validate_quiz_data_rejects_invalid` (parametrisiert; die Fixture wird jeweils kopiert und verändert), jeweils `pytest.raises(QuizGenerationError)`:
  - 9 Fragen
  - 11 Fragen
  - eine Frage mit 3 Optionen
  - eine leere Option
  - doppelte Optionen
  - `answer` nicht in den Optionen
  - leerer Titel
  - Titel mit mehr als 255 Zeichen
  - leerer Fragetitel
- **Erwartetes Rot:** keine Exception
- **Green:** kleine Prüf-Helper wie `_validate_title`, `_validate_question_count` und `_validate_question` (jeweils ≤ 14 Zeilen)
- **Commit:** `feat(quiz): reject invalid generated quizzes`
- [x] erledigt (nutzt `validate_options`/`validate_answer` aus `quiz_app/utils.py` wieder und übersetzt deren `ValidationError`; die Testfälle sind benannte Mutator-Funktionen statt Lambdas)

### Zyklus 3: Prompt bauen
- **Test:** `test_build_prompt_contains_transcript_and_rules`: Der Prompt enthält das Transkript, den Videotitel, `"10"`, `"4"` und den Hinweis, dass `answer` exakt einer Option entsprechen muss
- **Test:** `test_build_prompt_truncates_long_transcript`: Ein Transkript mit `MAX_TRANSCRIPT_CHARS + 500` Zeichen erscheint im Prompt höchstens mit `MAX_TRANSCRIPT_CHARS` Zeichen
- **Erwartetes Rot:** `ImportError`
- **Green:** Konstante `MAX_TRANSCRIPT_CHARS = 30000`, `PROMPT_TEMPLATE` als Modulkonstante, `build_prompt(transcript, video_title) -> str`
- **Commit:** `feat(quiz): build gemini prompt from transcript`
- [x] erledigt (Prompt auf Englisch mit der Regel „Use the language of the transcript“; Zahlen kommen aus `QUESTION_COUNT`, `OPTION_COUNT` und `MAX_TITLE_LENGTH`; geschweifte Klammern im Transkript sind unkritisch, weil nur das Template formatiert wird)

### Zyklus 4: JSON parsen
- **Test:** `test_parse_quiz_returns_dict`: `json.dumps(gemini_quiz_data)` ergibt nach dem Parsen ein Dict gleich der Fixture
- **Test:** `test_parse_quiz_rejects_invalid_json`: `"not json"` führt zu `QuizGenerationError`
- **Test:** `test_parse_quiz_rejects_non_object`: `"[]"` führt zu `QuizGenerationError`
- **Erwartetes Rot:** `ImportError`
- **Green:** `parse_quiz(raw: str) -> dict`
- **Commit:** `feat(quiz): parse gemini json response`
- [x] erledigt (fängt zusätzlich `TypeError` ab, weil `response.text` bei blockierten Antworten `None` sein kann)

### Zyklus 5: Gemini aufrufen
- **Test:** `test_request_quiz_calls_configured_model` (`settings.GEMINI_API_KEY = "key"`, `settings.GEMINI_MODEL = "gemini-test"`)
  - Arrange: `client = mock_client_cls.return_value`; `client.models.generate_content.return_value.text = '{"a": 1}'`
  - Assert: Rückgabe `'{"a": 1}'`; `Client` wurde mit `api_key="key"` aufgerufen; `generate_content` mit `model="gemini-test"` und `config["response_mime_type"] == "application/json"`
- **Test:** `test_request_quiz_without_api_key_raises`: `GEMINI_API_KEY = ""` führt zu `QuizGenerationError("Gemini API key is not configured.")`, und `Client` wird nicht aufgerufen
- **Test:** `test_request_quiz_wraps_api_errors`: `generate_content.side_effect = Exception("quota")` führt zu `QuizGenerationError`, und `"key"` steht nicht in `str(exc)`
- **Erwartetes Rot:** `ImportError`
- **Green:** Pydantic-Schemas `QuestionSchema` und `QuizSchema`; `request_quiz(prompt: str) -> str`
- **Commit:** `feat(quiz): request quiz from gemini`
- [x] erledigt (Abweichung: Test-Key `"test-secret-key"` statt `"key"`, damit die Leak-Prüfung aussagekräftig ist, und die simulierte API-Fehlermeldung enthält den Key absichtlich; zusätzlich wird `contents == prompt` geprüft. Config-Dict offline gegen `types.GenerateContentConfig` geprüft)

### Zyklus 6: Orchestrierung `generate_quiz`
- **Test:** `test_generate_quiz_returns_validated_data`: Der Mock liefert `json.dumps(gemini_quiz_data)`; `generate_quiz("transcript", "title")` ergibt die Fixture
- **Test:** `test_generate_quiz_raises_on_invalid_answer`: Der Mock liefert ein Quiz mit ungültiger `answer`; Ergebnis `QuizGenerationError`
- **Test:** `test_generate_quiz_calls_gemini_once`: `generate_content.call_count == 1`
- **Erwartetes Rot:** `ImportError`
- **Green:** `generate_quiz(transcript, video_title) -> dict` mit build → request → parse → validate
- **Commit:** `feat(quiz): generate validated quiz from transcript`
- [x] erledigt

## Abschluss-Check
- [x] Kein Test ruft die echte Gemini-API auf (geprüft: `test_generation.py` mit gesperrtem `socket.connect`/`getaddrinfo` → 21 passed)
- [x] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Optional manuell (zählt gegen das Kontingent): `python manage.py shell` und dort `generate_quiz("<kurzer Text>", "Test")`
- [x] Status von Schritt 13 auf `[x]` gesetzt (Commit `docs: mark step 13 done`)
- [x] Stopp → Review
