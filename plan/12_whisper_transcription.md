# 12 – Whisper-Transkription

## Ziel
Die Audiodatei wird lokal mit Whisper in Text umgewandelt.

## Referenzen
- `docs/Quizly Checkliste.pdf` – Whisper AI lokal; FFmpeg ist Pflicht
- `docs/Kurzanleitung Quizly.pdf` – FFmpeg-Installation

## Aufgaben
- [ ] `quiz_app/services/transcription.py`:
  - `get_whisper_model()`: lädt `whisper.load_model(settings.WHISPER_MODEL)` **lazy** und cacht es mit `functools.lru_cache(maxsize=1)`, damit das Modell nicht bei jedem Request neu geladen wird und auch nicht beim Django-Start
  - `transcribe_audio(path) -> str`: `model.transcribe(str(path), fp16=False)["text"].strip()`
  - Ist der Text leer → `QuizGenerationError("Transcript is empty.")`
  - Andere Exceptions (z. B. FFmpeg fehlt) → `QuizGenerationError`
- [ ] `fp16=False` vermeidet die CPU-Warnung
- [ ] Der Import von `whisper` erfolgt innerhalb der Funktion bzw. ist im Test leicht mockbar

## Hinweise
- Beim ersten Aufruf lädt Whisper das Modell `base` herunter (~140 MB). Im README erwähnen.
- Die Sprache erkennt Whisper automatisch; das Quiz wird in der Sprache des Transkripts erzeugt (siehe 13).

## Akzeptanzkriterien
- [ ] Ein Modell wird pro Prozess nur einmal geladen
- [ ] Fehler werden als `QuizGenerationError` weitergereicht

## Tests
- `quiz_app/tests/test_transcription.py`: `whisper.load_model` wird gemockt; geprüft werden der zurückgegebene Text, ein leeres Transkript (Fehler), eine Exception (Fehler) und das Caching

## Commit-Message
`feat(quiz): add Whisper transcription service`
