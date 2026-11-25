# 16 – Gesamt-Testplan und Coverage

## Ziel
Vollständige automatisierte Tests mit pytest und **≥ 90 % Coverage**, ohne echte Netzwerk- oder KI-Aufrufe.

## Werkzeuge
- `pytest`, `pytest-django`, `pytest-cov`
- `unittest.mock.patch` bzw. `monkeypatch` für yt_dlp, whisper und genai
- Fixtures in `conftest.py` (siehe 04): `api_client`, `user`, `other_user`, `auth_client`, `quiz_factory`, `gemini_quiz_data` (gültiges Dict mit 10 Fragen)

## Testmatrix Endpoints
| Endpoint | 2xx | 400 | 401 | 403 | 404 |
|---|---|---|---|---|---|
| POST register/ | ✓ | ✓ (Duplikate, Mismatch, fehlende Felder) | – | – | – |
| POST login/ | ✓ (Cookies) | ✓ (fehlende Felder) | ✓ | – | – |
| POST logout/ | ✓ (Blacklist, Cookies weg) | – | ✓ | – | – |
| POST token/refresh/ | ✓ (neues Cookie) | – | ✓ (fehlt, ungültig, geblacklistet) | – | – |
| POST quizzes/ | ✓ (gemockt) | ✓ (URL, Länge) | ✓ | – | – |
| GET quizzes/ | ✓ (nur eigene) | – | ✓ | – | – |
| GET quizzes/{id}/ | ✓ | – | ✓ | ✓ | ✓ |
| PATCH quizzes/{id}/ | ✓ | ✓ (leerer Titel) | ✓ | ✓ | ✓ |
| DELETE quizzes/{id}/ | ✓ (204) | – | ✓ | ✓ | ✓ |
| POST quizzes/ bei Pipeline-Fehler | – | – | – | – | 500 ✓ |

## Unit-Tests Services
- `youtube.py`: URL-Formate (parametrisiert), Dauer, `DownloadError`
- `transcription.py`: Text, leer, Exception, Cache
- `generation.py`: Prompt, Schema-Validierung, Fehlerfälle, fehlender Key
- `pipeline.py`: Ablauf, Atomarität, Cleanup des Temp-Verzeichnisses

## Weitere Tests
- Response-Format: Fragen-Timestamps nur in der POST-Response
- Format von `video_url` (`watch?v=`)
- Models und Admin (siehe 05, 15)
- CORS-Preflight (siehe 03)

## Ausführen
```bash
pytest
pytest --cov-report=html   # Report in htmlcov/
```

## Akzeptanzkriterien
- [ ] Alle Tests grün
- [ ] Coverage ≥ 90 % (Migrationen und Tests ausgenommen)
- [ ] Kein Test macht echte Netzwerk- oder Gemini-Aufrufe
- [ ] Die Tests sind ebenfalls PEP8-konform (flake8)

## Commit-Message
`test: complete test suite and reach coverage goal`
