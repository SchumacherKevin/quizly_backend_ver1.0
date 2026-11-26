# 00 – Übersicht, Arbeitsweise und Konventionen

> Diese Datei und `01_api_contract.md` sind der **gemeinsame Kontext** für jeden Schritt.
> Für einen Schritt reichen: `00` + `01` + die Schritt-Datei.

## Projektziel
Quizly erzeugt aus einem YouTube-Video automatisch ein Quiz mit **10 Fragen à 4 Antwortmöglichkeiten**.
Pipeline: YouTube-URL → Audio (yt_dlp, FFmpeg) → Transkript (Whisper, lokal) → Quiz (Gemini Flash) → Speichern.
Das Frontend (`D:\Github_Privat\Developer\Quizly\quizly_frontend`, Vanilla JS, Live Server `127.0.0.1:5500`) ist vorgegeben.
Das Backend liefert eine REST-API unter `http://127.0.0.1:8000/api/`.

## Entscheidungen
| Thema | Entscheidung |
|---|---|
| Stack | Django + Django REST Framework, **Python 3.14**, SQLite |
| Umgebung | `.venv` im Projektroot (nicht committen) |
| Apps | `core` (Settings/URLs), `auth_app`, `quiz_app` |
| Auth | simplejwt; HttpOnly-Cookies `access_token` / `refresh_token`; `CookieJWTAuthentication`; Access 5 min, Refresh 1 Tag; keine Rotation; Blacklist beim Logout; kein CSRF |
| Fremde Quizze | **403** (Object-Permission `IsOwner`, Queryset **nicht** nach Owner filtern) |
| Pipeline | synchron im POST; yt_dlp → Whisper `base` → Gemini (Modell aus `GEMINI_MODEL`, vorher in AI Studio prüfen); genau 1 Gemini-Call pro Quiz |
| URLs | `watch?v=`, `youtu.be/`, `shorts/`, `m.youtube.com` → normalisiert auf `https://www.youtube.com/watch?v=<ID>` |
| Videolänge | `MAX_VIDEO_MINUTES` (Default 15), darüber 400 |
| Fehler | 400 (URL ungültig / nicht ladbar / zu lang); 500 `{"detail": ...}` (Whisper/Gemini); Temp-Dateien immer löschen; atomar speichern |
| Config | python-dotenv, `.env` (ignoriert) + `.env.template` (committet) |
| Qualität | black + isort + flake8 (PEP8, Zeilenlänge 79); Funktionen ≤ 14 Zeilen (**Docstring zählt nicht mit**); Docstrings im **Google-Format** (`Args:`, `Returns:`, `Raises:`, sobald es Parameter, Rückgabewert bzw. Exceptions gibt); `views.py` nur Views |
| Tests | **TDD**; pytest + pytest-django + pytest-cov; Netz und KI immer gemockt; Ziel ≥ 90 % Coverage |
| Commits | **1 Commit pro abgeschlossenem Red-Green-Refactor-Zyklus** |

## Projektstruktur (Zielbild)
```
quizly_backend_ver1.0/
├── .venv/                      # nicht im Git
├── core/
│   ├── settings.py, urls.py
│   ├── env.py                  # get_bool / get_int / get_list
│   └── tests/
├── auth_app/
│   ├── api/  serializers.py, views.py, urls.py
│   ├── authentication.py       # CookieJWTAuthentication
│   ├── utils.py                # Cookie- und Token-Helper
│   └── tests/
├── quiz_app/
│   ├── api/  serializers.py, views.py, urls.py, permissions.py
│   ├── services/ exceptions.py, youtube.py, transcription.py, generation.py, pipeline.py
│   ├── models.py, admin.py
│   └── tests/
├── conftest.py                 # gemeinsame Fixtures
├── plan/
├── .env.template, .gitignore, requirements.txt, requirements-dev.txt
├── pyproject.toml, setup.cfg, README.md, manage.py
```

## Zentrale Konventionen
- **URL-Namen:** `register`, `login`, `logout`, `token-refresh`, `quiz-list`, `quiz-detail`. In Tests immer `reverse("<name>")` verwenden.
- **Cookie-Namen:** `access_token`, `refresh_token` (Konstanten in `auth_app/utils.py`: `ACCESS_COOKIE`, `REFRESH_COOKIE`).
- **Exceptions:** `quiz_app/services/exceptions.py` → `InvalidVideoError` (wird zu 400), `QuizGenerationError` (wird zu 500).
- **Fixtures** (`conftest.py` im Root, wachsen mit den Schritten):
  | Fixture | ab Schritt | Inhalt |
  |---|---|---|
  | `api_client` | 03 | `rest_framework.test.APIClient()` |
  | `user` | 03 | `testuser` / `test@example.com` / Passwort `Test1234!` |
  | `other_user` | 03 | `otheruser` / `other@example.com` / `Test1234!` |
  | `auth_client` | 07 | `APIClient` mit gültigem `access_token`- und `refresh_token`-Cookie für `user` |
  | `quiz_factory` | 05 | `quiz_factory(owner, questions=2)` → Quiz mit n gültigen Fragen |
  | `gemini_quiz_data` | 13 | gültiges Dict: `title`, `description`, 10 Fragen à 4 Optionen |
- **DB-Zugriff in Tests:** `pytestmark = pytest.mark.django_db` am Dateianfang.
- **Gültige Test-Video-ID:** `dQw4w9WgXcQ`
- **Patch-Ziele:** immer dort patchen, wo der Name **benutzt** wird, z. B. `quiz_app.services.pipeline.fetch_video_info`.

## Arbeitsweise TDD (pro Zyklus)
1. `.venv` aktivieren: `.\.venv\Scripts\Activate.ps1`
2. **Red:** Test laut Zyklus schreiben → `pytest <testdatei> -x`. Der Test muss **aus dem erwarteten Grund** fehlschlagen (siehe „Erwartetes Rot“).
3. **Green:** Nur so viel implementieren, dass der Test grün wird.
4. **Refactor:** Funktionen ≤ 14 Zeilen, Docstrings, sprechende Namen. Dann `black . ; isort . ; flake8 ; pytest`; **alles grün**.
5. Checkbox des Zyklus in der Schritt-Datei abhaken.
6. **Commit durch Kevin** mit der Commit-Message aus dem Zyklus.

Ein Zyklus wird nie mit roten Tests committet.

## Git-Workflow (alles macht Kevin)
- **Claude führt keine verändernden Git-Befehle aus** (kein `add`, `commit`, `switch -c`, `merge`, `push`). Nur lesende Befehle wie `git status`, `git log` und `git diff` sind erlaubt.
- Es wird direkt auf `main` gearbeitet (keine Feature-Branches)
- Nach jedem Zyklus ein Commit auf `main`
- Commit-Präfixe: `feat`, `test`, `fix`, `refactor`, `chore`, `docs` mit Scope (`auth`, `quiz`, `core`)
- Wo in den Schritt-Dateien „Commit:“ oder Git-Befehle stehen, sind das **Vorschläge bzw. Aufgaben für Kevin**.

## So arbeitet Claude einen Schritt ab
1. Nur `00`, `01` und die Schritt-Datei lesen und keine anderen Plan-Dateien voraussetzen
2. Vorbedingungen der Schritt-Datei prüfen: `git status`, `git log --oneline`, `pytest` grün, Status-Tabelle, und der letzte Zyklus ist committet.
3. **Einen Zyklus** durchführen: Red → Green → Refactor → alle Checks grün → Checkbox abhaken
4. **Stoppen** und Kevin geben:
   - die geänderten Dateien
   - die Testergebnisse
   - die fertige Commit-Message
5. Kevin committet und sagt „weiter“ → nächster Zyklus
6. Nach dem letzten Zyklus: Abschluss-Check, Status unten auf `[x]` setzen, kurze Zusammenfassung des Schritts (Abweichungen vom Plan) → Kevin reviewt

## Status
| # | Schritt | Datei | Status |
|---|---|---|---|
| 01 | API-Vertrag (Referenz) | [01_api_contract.md](01_api_contract.md) | [x] |
| 02 | Projekt-Setup und `.venv` | [02_project_setup.md](02_project_setup.md) | [x] |
| 03 | Tooling, pytest, Qualität | [03_tooling_quality.md](03_tooling_quality.md) | [x] |
| 04 | Settings, Env, CORS, JWT | [04_settings_cors_config.md](04_settings_cors_config.md) | [x] |
| 05 | Models | [05_models.md](05_models.md) | [x] |
| 06 | Register | [06_auth_register.md](06_auth_register.md) | [x] |
| 07 | Cookie-Authentifizierung | [07_auth_cookie_authentication.md](07_auth_cookie_authentication.md) | [x] |
| 08 | Login | [08_auth_login.md](08_auth_login.md) | [x] |
| 09 | Logout und Refresh | [09_auth_logout_refresh.md](09_auth_logout_refresh.md) | [x] |
| 10 | Quiz lesen, ändern, löschen | [10_quiz_read_update_delete.md](10_quiz_read_update_delete.md) | [x] |
| 11 | YouTube-Service | [11_youtube_download.md](11_youtube_download.md) | [x] |
| 12 | Whisper-Service | [12_whisper_transcription.md](12_whisper_transcription.md) | [x] |
| 13 | Gemini-Service | [13_gemini_quiz_generation.md](13_gemini_quiz_generation.md) | [x] |
| 14 | Quiz-Create-Endpoint (Pipeline) | [14_quiz_create_endpoint.md](14_quiz_create_endpoint.md) | [x] |
| 15 | Admin | [15_admin.md](15_admin.md) | [x] |
| 16 | Coverage- und Quality-Gate | [16_coverage_quality_gate.md](16_coverage_quality_gate.md) | [ ] |
| 17 | README und Endabnahme | [17_readme_final_check.md](17_readme_final_check.md) | [ ] |
