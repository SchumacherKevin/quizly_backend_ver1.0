# 12 – Whisper-Service (Transkription)

## Ziel
`quiz_app/services/transcription.py` wandelt eine Audiodatei lokal mit Whisper in Text um. Das Modell wird nur einmal pro Prozess geladen.

## Kontext (eigenständig)
- **Vorbedingungen:** 02–11 sind fertig. `openai-whisper` ist installiert, FFmpeg global im `PATH`, `settings.WHISPER_MODEL` existiert (Default `"base"`). In `quiz_app/services/exceptions.py` gibt es `QuizGenerationError`.
- Betroffene Dateien: `quiz_app/services/transcription.py` (neu), `quiz_app/tests/test_transcription.py`
- Whisper braucht FFmpeg zum Dekodieren. Fehlt FFmpeg, wirft Whisper eine Exception; die wird als `QuizGenerationError` weitergegeben (→ 500).
- Auf der CPU wird `fp16=False` gesetzt, das vermeidet eine Warnung.
- **Tests ohne echtes Modell:** `quiz_app.services.transcription.whisper` wird gepatcht. Der Cache (`functools.lru_cache`) wird vor jedem Test geleert, z. B. per autouse-Fixture `get_whisper_model.cache_clear()`.
- Der erste echte Lauf lädt das Modell herunter (~140 MB für `base`). Das kommt ins README (Schritt 17).

## Zyklen

### Zyklus 1: Modell laden und cachen
- **Test:** `test_get_whisper_model_loads_configured_model`: `settings.WHISPER_MODEL = "tiny"` führt zu `whisper.load_model` mit dem Aufruf `("tiny")`
- **Test:** `test_get_whisper_model_is_cached`: Zwei Aufrufe ergeben genau einen `load_model`-Aufruf, und es kommt dasselbe Objekt zurück
- **Erwartetes Rot:** `ModuleNotFoundError: quiz_app.services.transcription`
- **Green:** `@lru_cache(maxsize=1) def get_whisper_model()`
- **Commit:** `feat(quiz): load and cache whisper model`
- [x] erledigt (`import whisper` auf Modulebene zieht torch mit; der Testlauf wird dadurch um ein paar Sekunden langsamer, ein Modell wird aber nicht geladen)

### Zyklus 2: Audio transkribieren
- **Test:** `test_transcribe_audio_returns_stripped_text` (mit `tmp_path`)
  - Arrange: `model.transcribe.return_value = {"text": "  Hallo Welt  "}`
  - Assert: Ergebnis `"Hallo Welt"`; `transcribe` wurde mit `(str(path), fp16=False)` aufgerufen
- **Erwartetes Rot:** `ImportError: transcribe_audio`
- **Green:** `transcribe_audio(path: Path) -> str`
- **Commit:** `feat(quiz): transcribe audio with whisper`
- [ ] erledigt

### Zyklus 3: Fehlerfälle
- **Test:** `test_transcribe_audio_rejects_empty_transcript`: `{"text": "   "}` führt zu `QuizGenerationError` mit der Meldung `"Transcript is empty."`
- **Test:** `test_transcribe_audio_wraps_errors`: `transcribe.side_effect = RuntimeError("ffmpeg not found")` führt zu `QuizGenerationError`
- **Test:** `test_get_whisper_model_wraps_load_errors`: `load_model.side_effect = RuntimeError` führt beim Transkribieren zu `QuizGenerationError`
- **Erwartetes Rot:** `RuntimeError` statt `QuizGenerationError`
- **Green:** `try/except Exception` mit `raise QuizGenerationError("Transcription failed.") from exc`; zusätzlich Prüfung auf leeren Text
- **Commit:** `feat(quiz): handle whisper transcription errors`
- [ ] erledigt

## Abschluss-Check
- [ ] Kein Test lädt ein echtes Whisper-Modell
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Status von Schritt 12 auf `[x]` gesetzt (Commit `docs: mark step 12 done`)
- [ ] Stopp → Review
