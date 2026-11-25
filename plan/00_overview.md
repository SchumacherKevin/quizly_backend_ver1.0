# 00 – Übersicht Quizly Backend

## Projektziel
Quizly erzeugt aus einem YouTube-Video automatisch ein Quiz mit **10 Fragen à 4 Antwortmöglichkeiten**.
Pipeline: YouTube-URL → Audio (yt_dlp + FFmpeg) → Transkript (Whisper, lokal) → Quiz (Gemini Flash) → Speichern.
Das Frontend (`quizly_frontend`, Vanilla JS) ist vorgegeben; das Backend liefert eine REST-API unter `http://127.0.0.1:8000/api/`.

## Referenzen
- `D:\Github_Privat\Developer\Quizly\docs\Endpoint Dokumentation.pdf` – API-Vertrag
- `D:\Github_Privat\Developer\Quizly\docs\Quizly Checkliste.pdf` – Definition of Done, User Stories 1–10
- `D:\Github_Privat\Developer\Quizly\docs\Kurzanleitung Quizly.pdf` – FFmpeg, whisper, yt_dlp, Gemini-Key
- `D:\Github_Privat\Developer\Quizly\docs\ydl_opts.txt` – yt-dlp-Optionen
- `D:\Github_Privat\Developer\Quizly\quizly_frontend\shared\js\` – `config.js`, `auth.js`, `api.js`

## Entscheidungen (aus dem Interview)
| Thema | Entscheidung |
|---|---|
| Stack | Django + Django REST Framework, Python 3.12, SQLite |
| Apps | `core` (Settings/URLs) + `auth_app` + `quiz_app`, je mit `api/` (serializers, views, urls, permissions) und `utils.py` |
| Auth | simplejwt, Cookies `access_token` / `refresh_token` (HttpOnly, SameSite=Lax, secure=False in dev), eigene `CookieJWTAuthentication`, Access 5 min / Refresh 1 Tag, keine Rotation, Blacklist beim Logout, kein CSRF |
| Fremde Quizze | **403** laut Doku (Object-Permission, kein Queryset-Filter) |
| Pipeline | synchron im POST; yt_dlp → Whisper `base` → Gemini (Modell per `GEMINI_MODEL`, vorher in AI Studio prüfen; 1 Call pro Quiz) |
| URLs | watch?v=, youtu.be, shorts, m.youtube → normalisiert auf `https://www.youtube.com/watch?v=<ID>` |
| Videolänge | `MAX_VIDEO_MINUTES` (Default 15) → sonst 400 |
| Fehler | 400 (URL ungültig / nicht ladbar / zu lang), 500 `{"detail": ...}` (Whisper/Gemini), Temp-Dateien immer löschen, `transaction.atomic` |
| Config | python-dotenv + `.env.template` |
| Qualität | flake8 + black + isort, strikt PEP8, Funktionen ≤ 14 Zeilen, Docstrings, `views.py` nur Views |
| Tests | pytest + pytest-django + pytest-cov, KI gemockt, Ziel ≥ 90 % Coverage |
| Workflow | ein Commit je Plan-Schritt |

## Architekturskizze
```
quizly_backend_ver1.0/
├── core/                 # settings.py, urls.py (/admin/, /api/)
├── auth_app/
│   ├── api/              # serializers.py, views.py, urls.py
│   ├── authentication.py # CookieJWTAuthentication
│   ├── utils.py          # Cookie-Helper
│   └── tests/
├── quiz_app/
│   ├── api/              # serializers.py, views.py, urls.py, permissions.py
│   ├── services/         # youtube.py, transcription.py, generation.py, pipeline.py
│   ├── models.py, admin.py
│   └── tests/
├── plan/                 # diese Dateien
├── .env.template, requirements.txt, pyproject.toml, setup.cfg, README.md
└── manage.py
```

## Status
| # | Schritt | Datei | Status |
|---|---|---|---|
| 01 | API-Vertrag | [01_api_contract.md](01_api_contract.md) | [ ] |
| 02 | Projekt-Setup | [02_project_setup.md](02_project_setup.md) | [ ] |
| 03 | Settings, CORS, Config | [03_settings_cors_config.md](03_settings_cors_config.md) | [ ] |
| 04 | Tooling & Qualität | [04_tooling_quality.md](04_tooling_quality.md) | [ ] |
| 05 | Models | [05_models.md](05_models.md) | [ ] |
| 06 | Register | [06_auth_register.md](06_auth_register.md) | [ ] |
| 07 | Cookie-Authentifizierung | [07_auth_cookie_authentication.md](07_auth_cookie_authentication.md) | [ ] |
| 08 | Login | [08_auth_login.md](08_auth_login.md) | [ ] |
| 09 | Logout & Refresh | [09_auth_logout_refresh.md](09_auth_logout_refresh.md) | [ ] |
| 10 | Quiz lesen/ändern/löschen | [10_quiz_read_update_delete.md](10_quiz_read_update_delete.md) | [ ] |
| 11 | YouTube-Download | [11_youtube_download.md](11_youtube_download.md) | [ ] |
| 12 | Whisper-Transkription | [12_whisper_transcription.md](12_whisper_transcription.md) | [ ] |
| 13 | Gemini-Quizgenerierung | [13_gemini_quiz_generation.md](13_gemini_quiz_generation.md) | [ ] |
| 14 | Quiz-Create-Endpoint | [14_quiz_create_endpoint.md](14_quiz_create_endpoint.md) | [ ] |
| 15 | Admin | [15_admin.md](15_admin.md) | [ ] |
| 16 | Tests | [16_tests.md](16_tests.md) | [ ] |
| 17 | README & Abschluss | [17_readme_final_check.md](17_readme_final_check.md) | [ ] |

Tests werden **in jedem Schritt** mitgeschrieben; `16_tests.md` ist der Gesamt-Testplan und die Coverage-Abnahme.

## Aufbau jeder Schritt-Datei
**Ziel · Referenzen · Aufgaben (Checkboxen) · Akzeptanzkriterien · Tests · Commit-Message**
