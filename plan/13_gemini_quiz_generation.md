# 13 – Quizgenerierung mit Gemini

## Ziel
Aus dem Transkript erzeugt Gemini Flash mit **einem** API-Call ein Quiz (Titel, Beschreibung, 10 Fragen à 4 Optionen) als validiertes JSON.

## Referenzen
- `docs/Quizly Checkliste.pdf` – „KI Gemini Flash“, `google-genai`
- https://github.com/googleapis/python-genai

## Vorab: Modell verifizieren
- [ ] In Google AI Studio (https://aistudio.google.com) unter „Rate Limits“ prüfen, welches Flash-Modell im Free Tier verfügbar ist und wie hoch die Limits sind (laut Recherche vom 25.11.2026 vermutlich `gemini-3.8-flash` mit ca. 5 RPM / 20 RPD; die Angaben sind nicht offiziell)
- [ ] Den exakten Modellnamen in `.env` und `.env.template` (`GEMINI_MODEL`) eintragen
- [ ] Wegen der niedrigen Limits: genau 1 Call pro Quiz, keine automatischen Retries, in Tests immer mocken

## Aufgaben
- [ ] `quiz_app/services/generation.py`:
  - `build_prompt(transcript, video_title) -> str`: Anweisungen – ein Quiz in der Sprache des Transkripts, genau 10 Fragen, je 4 eindeutige Optionen, `answer` exakt gleich einer Option, ein kurzer Titel (≤ 255 Zeichen), eine Beschreibung (1–2 Sätze); das Transkript gegebenenfalls kürzen (Zeichenlimit als Konstante)
  - `request_quiz(prompt) -> str`: `genai.Client(api_key=settings.GEMINI_API_KEY).models.generate_content(model=settings.GEMINI_MODEL, contents=prompt, config={"response_mime_type": "application/json", "response_schema": ...})`
  - Das Response-Schema wird als Pydantic-Modell definiert (`QuizSchema` mit `title`, `description`, `questions: list[QuestionSchema]`); Pydantic wird von `google-genai` mitgebracht
  - `parse_quiz(raw) -> dict`: JSON parsen und validieren
  - `validate_quiz_data(data)`: genau 10 Fragen; jede mit 4 Optionen (Strings, nicht leer, eindeutig); `answer in question_options`; Titel nicht leer
  - `generate_quiz(transcript, video_title) -> dict`: verbindet die Schritte
- [ ] Fehler (API-Fehler, Quota erschöpft, ungültiges JSON, Validierung) → `QuizGenerationError` mit einer verständlichen Meldung
- [ ] Fehlt `GEMINI_API_KEY` → `QuizGenerationError("Gemini API key is not configured.")`

## Akzeptanzkriterien
- [ ] Eine gültige Gemini-Antwort ergibt ein Dict mit `title`, `description` und 10 Fragen
- [ ] Jede Abweichung (9 Fragen, 3 Optionen, `answer` nicht in den Optionen) → `QuizGenerationError`
- [ ] Der API-Key erscheint nie in Logs oder Responses

## Tests
- `quiz_app/tests/test_generation.py`: `genai.Client` wird gemockt; gültige Antwort, kaputtes JSON, falsche Anzahl an Fragen/Optionen, ungültige `answer`, API-Exception, fehlender Key; außerdem enthält `build_prompt` das Transkript und die Regeln

## Commit-Message
`feat(quiz): add Gemini quiz generation service`
