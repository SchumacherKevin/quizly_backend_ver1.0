# 17 – README und Endabnahme

## Ziel
Eine aussagekräftige `README.md`, ein manueller End-to-End-Test mit dem echten Frontend und der Postman CLI sowie die Abnahme aller Punkte der Checkliste.

## Kontext (eigenständig)
- **Vorbedingungen:** 02–16 sind fertig; alle Tests grün; Coverage ≥ 90 %.
- Betroffene Dateien: `README.md`, optional `postman/quizly.postman_collection.json`
- Die Checkliste verlangt: eine aussagekräftige `README.MD`, **und darin muss stehen, dass FFmpeg global installiert sein muss**.
- Frontend: `D:\Github_Privat\Developer\Quizly\quizly_frontend`, mit Live Server über `http://127.0.0.1:5500` öffnen. Nicht `localhost` verwenden: Sonst ist der Request cross-site, und die Lax-Cookies werden nicht gesendet.
- Die Postman CLI ist auf dem Rechner installiert.

## Zyklen

### Zyklus 1: README schreiben
Inhalt:
- [x] Projektbeschreibung und Features (YouTube → Quiz mit 10 Fragen)
- [x] Tech-Stack: Python 3.14, Django, DRF, simplejwt, django-cors-headers, yt-dlp, openai-whisper, google-genai
- [x] **Voraussetzungen:** Python 3.14, **FFmpeg global installiert** (Windows: `winget install ffmpeg` bzw. Download und `PATH` setzen; macOS: `brew install ffmpeg`); Prüfung mit `ffmpeg -version`
- [x] Installation (PowerShell):
  ```powershell
  git clone <repo>
  cd quizly_backend_ver1.0
  py -3.14 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  Copy-Item .env.template .env   # Werte eintragen (SECRET_KEY, GEMINI_API_KEY ...)
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver
  ```
- [x] Erklärung der Env-Variablen (Tabelle); Gemini-Key unter https://ai.google.dev/
- [x] Hinweise:
  - Whisper lädt beim ersten Lauf das Modell herunter
  - Das Gemini-Free-Tier ist begrenzt
  - yt-dlp aktuell halten (`pip install -U yt-dlp`)
  - Maximale Videolänge per `MAX_VIDEO_MINUTES`
  - Der Access-Token bleibt nach dem Logout bis zu 5 Minuten technisch gültig, das Cookie wird aber gelöscht
- [x] Frontend-Hinweis: über `http://127.0.0.1:5500` öffnen
- [x] API-Übersicht: Tabelle mit allen 9 Endpoints (Methode, Pfad, Auth, Beschreibung)
- [x] Entwicklung: `pip install -r requirements-dev.txt`, `pytest`, `black . ; isort . ; flake8`, TDD-Workflow mit Verweis auf `plan/00_overview.md`
- [x] Projektstruktur
- **Commit:** `docs: add README with setup and ffmpeg requirement`
- [x] erledigt (README auf Englisch wie der Code. Zusätzlich: Hinweis, dass `DEBUG=True` für lokales HTTP nötig ist, weil die Cookies sonst `Secure` sind; Linux-Befehl für FFmpeg; PyTorch-Download; SECRET_KEY-Generator; Beispiel-Quiz; 503-Hinweis zu Gemini)

### Zyklus 2: Frisches Setup prüfen
- [x] Repo in einen temporären Ordner klonen und die README Schritt für Schritt befolgen, bis `runserver` läuft und `pytest` grün ist (26.11.2026, Klon aus dem lokalen Repo, weil der Stand noch nicht gepusht war: venv, `pip install` in 1,8 min, `.env` mit generiertem `SECRET_KEY`, `migrate` und `check` sauber; `runserver` antwortet mit 401 auf `GET quizzes/` und 201 auf `POST register/`; Dev-Requirements: 170 passed, 100 %, black/isort/flake8 sauber. Klon danach gelöscht)
- [x] Gefundene Lücken in der README korrigieren (eine Lücke: `Activate.ps1` scheitert an der Standard-ExecutionPolicy; Hinweis auf `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` ergänzt). **Commit:** `docs: fix setup instructions`

### Zyklus 3: API-Test mit der Postman CLI
- [x] Collection mit den 9 Endpoints anlegen; der Cookie-Jar überträgt die Cookies vom Login in die folgenden Requests (`postman/quizly.postman_collection.json`, 12 Requests: zusätzlich GET nach DELETE → 404 und GET nach Logout → 401; prüft u. a. HttpOnly-Cookies, keine Tokens im Body, 10 × 4 Optionen, Antwort in den Optionen)
- [ ] Ablauf: register → login → list → create (echtes kurzes Video) → detail → patch → refresh → delete → logout → refresh (erwartet 401)
- [ ] `postman collection run postman/quizly.postman_collection.json` ist grün
- **Commit:** `test: add postman collection for end-to-end api checks`
- **Befund 1 (behoben, eigener TDD-Zyklus):** Norton Web/Mail Shield signiert HTTPS mit eigener Root-CA neu. yt-dlp prüft mit `certifi`, das diese Root nicht kennt → `CERTIFICATE_VERIFY_FAILED` → 400. Fix: `compat_opts: {"no-certifi"}` in den yt-dlp-Optionen (Prüfung gegen den Windows-Zertifikatsspeicher, weiterhin verifiziert). Tests `test_fetch_video_info_prefers_system_certificates` und `test_download_options_prefer_system_certificates`. Commit: `fix(quiz): verify youtube tls against os certificate store`
- **Befund 2:** yt-dlp warnt, dass keine JS-Runtime (Deno) gefunden wurde; der Download funktioniert trotzdem. In der README dokumentiert
- **Befund 3 (offen):** Gemini `gemini-3.8-flash` antwortet am 26.11.2026 wiederholt mit 503 „high demand“, obwohl das SDK intern selbst wiederholt. Download und Whisper liefen echt durch (Whisper-Modell geladen, ca. 30 s), danach korrekt 500 `{"detail": "Gemini request failed."}`. Ein Lauf mit 201 steht noch aus
- Stand der Läufe: alle Requests außer Create und den davon abhängigen (Detail, Patch, Delete) sind grün

### Zyklus 4: E2E mit dem Frontend
- [ ] Registrieren → Login → Quiz aus einem kurzen Video erstellen → Übersicht (Video-Embed sichtbar) → Titel und Beschreibung bearbeiten (bleibt nach dem Reload erhalten) → Quiz spielen und auswerten → „See all“ → Quiz löschen → Logout
- [ ] Nach mehr als 5 Minuten Inaktivität funktioniert der automatische Refresh (keine Weiterleitung zum Login)
- [ ] Nach dem Logout leitet der Aufruf von `library.html` zum Login weiter
- Gefundene Bugs: je ein TDD-Zyklus (zuerst ein Test, der den Bug reproduziert) und Commit `fix(<scope>): ...`

## Abnahme Checkliste (DoD)
| Regel | Umgesetzt in | ✓ |
|---|---|---|
| Funktionen ≤ 14 Zeilen, eine Aufgabe | alle, geprüft in 16 | [ ] |
| snake_case, sprechende Namen | alle, 16 | [ ] |
| keine ungenutzten Variablen, kein auskommentierter Code | flake8, 16 | [ ] |
| Docstrings | alle, 16 | [ ] |
| README mit FFmpeg-Hinweis | 17 | [ ] |
| `views.py` nur Views, Helper in `utils.py`/`services/` | 06–14, 16 | [ ] |
| Admin: Quizze und Fragen bearbeitbar | 15 | [ ] |
| PEP8 | 03 (black, isort, flake8) | [ ] |
| Django-Backend, REST-API, Frontend getrennt | 02–14 | [ ] |
| JWT mit HttpOnly-Cookies | 07–09 | [ ] |
| FFmpeg global | 02, 17 | [ ] |
| nur YouTube, yt_dlp | 11 | [ ] |
| Whisper lokal | 12 | [ ] |
| Gemini Flash | 13 | [ ] |
| US1 Registrierung | 06 | [ ] |
| US2 Login | 08 | [ ] |
| US3 Logout + Blacklist | 09 | [ ] |
| US4 Quiz erstellen (10 × 4) | 11–14 | [ ] |
| US5–US7 Quizze anzeigen, bearbeiten, löschen | 10 | [ ] |
| US8/US9 Quiz spielen, Auswertung | Frontend (E2E in 17) | [ ] |
| US10 Datenschutz/Impressum | Frontend | [ ] |

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Alle DoD-Zeilen abgehakt
- [ ] Status von Schritt 17 auf `[x]` gesetzt (Commit `docs: mark step 17 done`)
- [ ] Stopp → finales Review mit Kevin
