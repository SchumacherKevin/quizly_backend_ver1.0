# 02 – Projekt-Setup

## Ziel
Lauffähiges, leeres Django-Projekt mit den Apps `core`, `auth_app` und `quiz_app`, virtueller Umgebung und Abhängigkeiten.

## Referenzen
- `docs/Kurzanleitung Quizly.pdf` – FFmpeg-Installation, Bibliotheken
- `docs/Quizly Checkliste.pdf` – Tech-Vorgaben (Django, yt_dlp, Whisper, Gemini Flash)

## Voraussetzungen
- Python 3.12
- FFmpeg global installiert und im `PATH` (`ffmpeg -version`) – Pflicht für Whisper

## Aufgaben
- [ ] `py -3.12 -m venv .venv` und aktivieren
- [ ] `requirements.txt` anlegen (Versionen beim Installieren pinnen):
  - `Django`
  - `djangorestframework`
  - `djangorestframework-simplejwt`
  - `django-cors-headers`
  - `python-dotenv`
  - `yt-dlp` (Doku verweist auf Tag 2025.07.21; aktuelle Version verwenden, weil YouTube ältere Versionen oft blockiert)
  - `openai-whisper`
  - `google-genai`
- [ ] `requirements-dev.txt`: `pytest`, `pytest-django`, `pytest-cov`, `flake8`, `black`, `isort`
- [ ] `django-admin startproject core .`
- [ ] `python manage.py startapp auth_app` und `startapp quiz_app`
- [ ] In beiden Apps einen `api/`-Ordner anlegen (`__init__.py`, `serializers.py`, `views.py`, `urls.py`); `quiz_app/api/permissions.py`
- [ ] `quiz_app/services/` anlegen (`__init__.py`)
- [ ] `tests/`-Pakete in beiden Apps (die Standard-`tests.py` entfernen)
- [ ] `.gitignore`: `.venv/`, `.env`, `db.sqlite3`, `__pycache__/`, `.pytest_cache/`, `.coverage`, `htmlcov/`, `media/`, `*.webm`, `*.m4a`
- [ ] `.env.template` (Inhalt siehe 03)
- [ ] `core/urls.py`: `admin/`, `api/` → `include('auth_app.api.urls')` und `include('quiz_app.api.urls')`

## Akzeptanzkriterien
- [ ] `python manage.py check` läuft ohne Fehler
- [ ] `python manage.py runserver` startet auf Port 8000
- [ ] `ffmpeg -version` funktioniert
- [ ] `.env` ist nicht im Git

## Tests
- Noch keine Tests; Testinfrastruktur folgt in 04.

## Commit-Message
`chore: set up Django project with auth_app and quiz_app`
