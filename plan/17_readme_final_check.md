# 17 – README und Endabnahme

## Ziel
Eine aussagekräftige `README.md`, ein manueller End-to-End-Test mit dem echten Frontend und der Abgleich aller Punkte der Checkliste.

## README.md – Inhalt
- [ ] Projektbeschreibung und Features
- [ ] Tech-Stack (Django, DRF, simplejwt, yt-dlp, Whisper, Gemini Flash)
- [ ] **Voraussetzungen: FFmpeg global installiert** (Pflicht laut Checkliste), mit Anleitung für Windows und macOS aus der Kurzanleitung; Python 3.12
- [ ] Installation: Repo klonen, venv, `pip install -r requirements.txt`, `.env.template` nach `.env` kopieren und ausfüllen (Gemini-Key von https://ai.google.dev/), `migrate`, `createsuperuser`, `runserver`
- [ ] Hinweise: Whisper lädt beim ersten Lauf das Modell herunter; das Gemini-Free-Tier ist begrenzt; yt-dlp aktuell halten
- [ ] Frontend über `http://127.0.0.1:5500` öffnen (nicht `localhost`, wegen der Cookies)
- [ ] API-Übersicht (Tabelle mit den 9 Endpoints)
- [ ] Tests und Linting ausführen
- [ ] Projektstruktur

## Manueller E2E-Test (Frontend + Postman CLI)
- [ ] Postman-Collection für alle Endpoints anlegen und mit der Postman CLI ausführen (Cookie-Handling prüfen)
- [ ] Frontend: Registrieren → Login → Quiz aus einem kurzen Video erstellen → Übersicht → Titel und Beschreibung bearbeiten → Quiz spielen → Quiz löschen → Logout
- [ ] Nach 5 Minuten: automatischer Refresh funktioniert
- [ ] Nach dem Logout: Zugriff auf die Library leitet zum Login weiter

## Abgleich Checkliste (DoD)
| Regel | Wo umgesetzt |
|---|---|
| Funktionen ≤ 14 Zeilen, eine Aufgabe | alle Schritte, 04 |
| snake_case, sprechende Namen | 04 |
| keine ungenutzten Variablen und kein auskommentierter Code | 04, flake8 |
| Docstrings | alle Schritte |
| README mit FFmpeg | 17 |
| `views.py` nur Views, Helper in `utils.py`/`services/` | 07–14 |
| Admin: Quizze und Fragen bearbeitbar | 15 |
| PEP8 | 04 (black, isort, flake8) |
| REST-API, Django | 02–14 |
| JWT + HttpOnly-Cookies | 07–09 |
| FFmpeg global | 02, 17 |
| nur YouTube, yt_dlp | 11 |
| Whisper lokal | 12 |
| Gemini Flash | 13 |
| US1 Registrierung | 06 |
| US2 Login | 08 |
| US3 Logout + Blacklist | 09 |
| US4 Quiz erstellen (10 × 4) | 11–14 |
| US5–US7 Quizze verwalten | 10 |
| US8/US9 Quiz spielen und Auswertung | Frontend (kein Backend nötig) |
| US10 Datenschutz/Impressum | Frontend |

## Akzeptanzkriterien
- [ ] Ein frisches Setup nach README funktioniert
- [ ] Alle Zeilen der Tabelle sind abgehakt
- [ ] `black --check .`, `isort --check .`, `flake8` und `pytest` laufen grün

## Commit-Message
`docs: add README and final checklist`
