# 18 – Wählbarer KI-Anbieter (Gemini Standard, OpenAI-kompatibel optional)

## Ziel
Gemini bleibt der Standard. Wer eine andere KI-API nutzt, stellt sie per `.env` um, ohne Code zu ändern (Wunsch von Kevin, 26.11.2026).

## Kontext (eigenständig)
- **Vorbedingungen:** 02–16 sind fertig. `quiz_app/services/generation.py` enthält `build_prompt`, `request_quiz` (Gemini über `genai.Client`), `parse_quiz`, `validate_quiz_data` und `generate_quiz`.
- **Entscheidung:** Zweiter Weg über die **OpenAI-kompatible Chat-Completions-API**. Sie wird von OpenAI, Mistral, Groq, OpenRouter und lokal von Ollama und LM Studio angeboten.
- **Neue Settings** (alle optional):

  | Variable | Default | Bedeutung |
  |---|---|---|
  | `AI_PROVIDER` | `gemini` | `gemini` oder `openai` |
  | `OPENAI_API_KEY` | `""` | API-Key des OpenAI-kompatiblen Anbieters |
  | `OPENAI_MODEL` | `""` | Modellname beim Anbieter, z. B. `gpt-…` oder `llama3.1` |
  | `OPENAI_BASE_URL` | `https://api.openai.com/v1` | z. B. `http://localhost:11434/v1` für Ollama |

  `GEMINI_API_KEY` und `GEMINI_MODEL` bleiben unverändert.
- **Ablauf:** `request_quiz` entscheidet nach `AI_PROVIDER`: `_request_gemini` (bisheriger Code) bzw. `_request_openai`. Prompt, Parsing und Prüfung bleiben gemeinsam. Weiterhin gilt genau 1 Request pro Quiz ohne eigene Retries, und der Key erscheint nie in Fehlermeldungen.
- OpenAI-kompatibel: `OpenAI(api_key=..., base_url=...).chat.completions.create(model=..., messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})`, Antwort in `choices[0].message.content`. Der JSON-Modus verlangt, dass der Prompt „JSON“ erwähnt.
- Tests patchen `quiz_app.services.generation.OpenAI`; es gibt nie echte Netzaufrufe.

## Zyklen

### Zyklus 1: Anbieter-Auswahl, Gemini als Standard
- **Test:** `test_request_quiz_uses_gemini_by_default`: Ohne `AI_PROVIDER` in den Settings wird `genai.Client` aufgerufen
- **Test:** `test_request_quiz_rejects_unknown_provider`: `AI_PROVIDER = "foo"` führt zu `QuizGenerationError("Unknown AI provider: foo.")`, und `genai.Client` wird nicht aufgerufen
- **Erwartetes Rot:** Bei unbekanntem Anbieter wird trotzdem Gemini aufgerufen
- **Green:** `AI_PROVIDER` in `settings.py`; der bisherige Code wird zu `_request_gemini`; `request_quiz` verteilt über ein Dict `PROVIDERS`
- **Commit:** `feat(quiz): select ai provider via settings`
- [x] erledigt (Abweichung: statt „ohne `AI_PROVIDER`“ setzt der Test `AI_PROVIDER = "gemini"` explizit, damit er nicht von der lokalen `.env` abhängt; die Fixture `client_cls` setzt ebenfalls `"gemini"`. `AI_PROVIDER` wird per `strip().lower()` normalisiert)

### Zyklus 2: OpenAI-kompatibler Anbieter
- **Test:** `test_request_quiz_calls_openai_compatible_api`: `AI_PROVIDER = "openai"`, Key, Modell und Base-URL gesetzt; `OpenAI` wird mit `api_key` und `base_url` erzeugt, `create` mit `model`, der Prompt steht als User-Nachricht, `response_format` ist `json_object`, und die Rückgabe ist der Content
- **Test:** `test_request_quiz_openai_without_model_raises`: Fehlt das Modell, kommt `QuizGenerationError`, und `OpenAI` wird nicht erzeugt
- **Test:** `test_request_quiz_openai_wraps_api_errors`: Ein API-Fehler führt zu `QuizGenerationError` ohne Key in der Meldung
- **Green:** Paket `openai` in `requirements.txt`, Settings, `_request_openai`
- **Commit:** `feat(quiz): support openai compatible ai providers`
- [x] erledigt (zusätzlicher Test `test_request_quiz_openai_allows_missing_key`: Ohne Key wird der Platzhalter `"not-needed"` gesendet, weil Ollama und LM Studio keinen brauchen. Refactor: Helper `_openai_client`, sonst hätte `_request_openai` 15 Zeilen. `openai==3.60.0` installiert und in `requirements.txt`)

### Zyklus 3: Prompt beschreibt das JSON-Format
- **Test:** `test_build_prompt_describes_json_format`: Der Prompt enthält `"JSON"` und die Keys `title`, `description`, `questions`, `question_title`, `question_options`, `answer`
- **Grund:** Andere Anbieter bekommen kein Schema wie Gemini (`response_schema`), und der JSON-Modus von OpenAI verlangt das Wort „JSON“ im Prompt
- **Commit:** `feat(quiz): describe json response format in prompt`
- [x] erledigt (Beispiel-Objekt im Template mit verdoppelten `{{ }}` wegen `.format()`; geprüft, dass das Beispiel gültiges JSON ist)

### Zyklus 4: Dokumentation
- [x] `.env.template` um die neuen Variablen ergänzen (auskommentiert bzw. leer, Gemini aktiv)
- [x] README: Abschnitt „Using another AI provider“ mit Beispielen (OpenAI, Ollama), Tabelle der Env-Variablen (zusätzlich: Hinweis zum Wechsel nur des Gemini-Modells, Fehlerverhalten bei Formatverstößen, Erweiterung um native SDKs über `PROVIDERS`; Features, Tech-Stack und Requirements angepasst)
- **Commit:** `docs: explain how to switch the ai provider`

## Abschluss-Check
- [x] Kein Test ruft eine echte KI-API auf (gesamte Suite mit gesperrtem Netz: 179 passed)
- [x] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün, Coverage ≥ 90 %, das DoD-Skript aus 16 findet 0 Funde (100 %, 0 Funde)
- [x] Status von Schritt 18 auf `[x]` gesetzt (Commit `docs: mark step 18 done`)
- [x] Stopp → Review
