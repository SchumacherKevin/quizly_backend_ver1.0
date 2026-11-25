# 02 – Projekt-Setup und `.venv`

## Ziel
Lauffähiges, leeres Django-Projekt mit `.venv`, Abhängigkeiten und den Apps `core`, `auth_app` und `quiz_app`. Ab diesem Stand kann in Schritt 03 per TDD gearbeitet werden.

## Kontext (eigenständig)
- **Vorbedingungen:** Repo `quizly_backend_ver1.0` existiert (Branch `main`), der Ordner `plan/` ist committet. Python 3.14 und FFmpeg sind installiert.
- In diesem Schritt gibt es **noch keine automatisierten Tests**, weil pytest erst in 03 eingerichtet wird. Die Verifikation erfolgt manuell über `manage.py check`.
- Shell: PowerShell (Windows).
- Die Struktur muss dem Zielbild in `00_overview.md` entsprechen.

## Referenzen
- `D:\Github_Privat\Developer\Quizly\docs\Kurzanleitung Quizly.pdf` – FFmpeg und Bibliotheken
- `D:\Github_Privat\Developer\Quizly\docs\Quizly Checkliste.pdf` – Tech-Vorgaben

## Zyklen

### Zyklus 1: Repo-Basis und `.venv`
- **Aufgaben:**
  - (Kevin) `git switch -c step/02-setup`
  - `.gitignore` anlegen:
    ```
    .venv/
    .env
    db.sqlite3
    __pycache__/
    *.pyc
    .pytest_cache/
    .coverage
    htmlcov/
    media/
    *.webm
    *.m4a
    *.mp3
    ```
  - `py -3.14 -m venv .venv`, danach `.\.venv\Scripts\Activate.ps1` und `python -m pip install --upgrade pip`
  - `python --version` muss 3.14.x ausgeben
- **Verifikation:** `git status` zeigt `.venv/` **nicht** an.
- **Commit:** `chore: add gitignore for python venv and local artifacts`
- [x] erledigt

### Zyklus 2: Abhängigkeiten
- **Aufgaben:**
  - Installieren: `pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv yt-dlp openai-whisper google-genai`
  - `requirements.txt` mit **gepinnten** Versionen schreiben (nur direkte Abhängigkeiten, die Versionen aus `pip freeze` übernehmen)
  - Dev: `pip install pytest pytest-django pytest-cov black isort flake8`, dann `requirements-dev.txt` mit `-r requirements.txt` als erster Zeile, darunter die gepinnten Dev-Pakete
  - `ffmpeg -version` muss funktionieren
- **Hinweis:** `openai-whisper` zieht `torch` mit (groß, das dauert). yt-dlp aktuell halten, weil YouTube alte Versionen blockiert.
- **Commit:** `chore: add pinned runtime and dev requirements`
- [ ] erledigt

### Zyklus 3: Django-Projekt und Apps
- **Aufgaben:**
  - `django-admin startproject core .`
  - `python manage.py startapp auth_app` und `python manage.py startapp quiz_app`
  - In beiden Apps die automatisch erzeugte `tests.py` löschen und stattdessen `tests/__init__.py` anlegen; ebenso `core/tests/__init__.py`
  - `auth_app/api/` mit `__init__.py`, `serializers.py`, `views.py`, `urls.py` (mit `urlpatterns = []`)
  - `quiz_app/api/` wie oben, zusätzlich `permissions.py`
  - `quiz_app/services/__init__.py`
  - `core/settings.py`: `auth_app` und `quiz_app` in `INSTALLED_APPS` (Rest folgt in 04)
  - `core/urls.py`:
    ```python
    urlpatterns = [
        path("admin/", admin.site.urls),
        path("api/", include("auth_app.api.urls")),
        path("api/", include("quiz_app.api.urls")),
    ]
    ```
- **Verifikation:** `python manage.py check` meldet keine Fehler; `python manage.py migrate` läuft durch; `python manage.py runserver` zeigt die Django-Seite auf `http://127.0.0.1:8000/admin/`.
- **Commit:** `chore: scaffold django project with core, auth_app and quiz_app`
- [ ] erledigt

## Abschluss-Check
- [ ] `python manage.py check` ist fehlerfrei
- [ ] `git status` ist sauber, und `.venv`, `db.sqlite3` sowie `.env` sind nicht getrackt
- [ ] Status von Schritt 02 in `00_overview.md` auf `[x]` gesetzt (Commit `docs: mark step 02 done`)
- [ ] Stopp → Review mit Kevin → `git switch main ; git merge --ff-only step/02-setup`
