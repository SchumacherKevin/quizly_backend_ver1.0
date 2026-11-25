# 01 – API-Vertrag

## Ziel
Eine verbindliche Referenz aller Endpoints, abgeleitet aus der Endpoint-Doku und den Frontend-Aufrufen. Bei Konflikten gilt die Doku; die Frontend-Besonderheiten sind zusätzlich einzuhalten.

## Referenzen
- `docs/Endpoint Dokumentation.pdf`
- `quizly_frontend/shared/js/config.js:1-8` – Base URL und Pfade
- `quizly_frontend/shared/js/auth.js:276-306` – `apiFetch` (401/403 → Refresh → Retry → Login)
- `quizly_frontend/shared/js/api.js` – Quiz-Aufrufe

## Allgemein
- Basis: `http://127.0.0.1:8000/api/`, **alle Pfade mit Trailing Slash**
- Requests: JSON, `Content-Type: application/json`, `credentials: "include"`
- Kein `Authorization`-Header, kein CSRF-Token → Auth nur über Cookies, CSRF nicht erzwingen
- Rate Limits: keine
- Wichtig: Das Frontend behandelt **401 und 403** gleich (Refresh, Retry, danach Login). 403 für fremde Quizze ist laut Doku gewollt (Entscheidung).

## Auth-Endpoints

### POST `/api/register/` – öffentlich
Request:
```json
{"username": "...", "password": "...", "confirmed_password": "...", "email": "user@example.com"}
```
| Status | Body |
|---|---|
| 201 | `{"detail": "User created successfully!"}` |
| 400 | Serializer-Fehler, z. B. `{"username": ["..."]}` |
| 500 | Interner Fehler |

Frontend: liest immer `response.json()` (auth.js:112) → **jede** Antwort braucht einen JSON-Body. Fehleranzeige nutzt `data.username` (auth.js:115). E-Mail muss eindeutig sein (US1). Registrierung setzt **keine** Cookies.

### POST `/api/login/` – öffentlich
Request: `{"username": "...", "password": "..."}`
| Status | Body |
|---|---|
| 200 | `{"detail": "Login successfully!", "user": {"id": 1, "username": "...", "email": "..."}}` + Cookies `access_token`, `refresh_token` |
| 401 | `{"detail": "..."}` (allgemein gehalten, US2) |
| 500 | Interner Fehler |

Frontend zeigt `responseData.detail` bei Fehlern (auth.js:79).

### POST `/api/logout/` – authentifiziert
Request: `{}` bzw. kein Body
| Status | Body |
|---|---|
| 200 | `{"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}` |
| 401 | Nicht authentifiziert |
| 500 | Interner Fehler |

Löscht beide Cookies, blacklistet den Refresh-Token.

### POST `/api/token/refresh/` – Refresh-Cookie nötig
Request: kein Body, **kein Content-Type-Header** (auth.js:263-274)
| Status | Body |
|---|---|
| 200 | `{"detail": "Token refreshed"}` + neues Cookie `access_token` |
| 401 | Refresh-Token ungültig oder fehlt |
| 500 | Interner Fehler |

Der Access-Token wird **nicht** im Body zurückgegeben (HttpOnly bleibt wirksam).

## Quiz-Endpoints (alle authentifiziert)

### Quiz-Objekt
```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```
- `created_at`/`updated_at` an Fragen **nur in der POST-Response**; GET/PATCH liefern Fragen ohne Timestamps.
- `video_url` immer im Format `watch?v=` (Frontend-Embed nutzt `/v=([^&]+)/`, quizoverview.js:85).
- `question_options`: genau 4 Strings; `answer` ist **exakt** einer davon (quiz.js vergleicht Text).
- `created_at` als ISO-Datum in UTC (Sidebar „heute / letzte 7 Tage“).

### POST `/api/quizzes/`
Request: `{"url": "https://www.youtube.com/watch?v=example"}`
| Status | Bedeutung |
|---|---|
| 201 | vollständiges Quiz (mit Fragen-Timestamps) |
| 400 | ungültige URL / nicht ladbar / zu lang |
| 401 | nicht authentifiziert |
| 500 | Pipeline-Fehler (Whisper/Gemini) |

Frontend braucht `id` in der Antwort (library.js:49-59).

### GET `/api/quizzes/`
200 → **unpaginiertes JSON-Array** der eigenen Quizze (Frontend nutzt `.length` / `.forEach`). 401 / 500.

### GET `/api/quizzes/{id}/`
200 Quiz · 401 · 403 fremdes Quiz · 404 nicht vorhanden · 500

### PATCH `/api/quizzes/{id}/`
Request: `{"title": "...", "description": "..."}` (Frontend sendet immer beide, 1 s debounced)
200 aktualisiertes Quiz · 400 · 401 · 403 · 404 · 500. Nur `title` und `description` sind änderbar.

### DELETE `/api/quizzes/{id}/`
204 ohne Body · 401 · 403 · 404 · 500. Löscht das Quiz samt Fragen (Cascade).

## Akzeptanzkriterien
- [ ] Jeder Endpoint ist in genau einem Umsetzungsschritt verortet (06, 08, 09, 10, 14)
- [ ] Response-Texte (`detail`) stimmen wortgleich mit der Doku überein

## Commit-Message
`docs: add API contract`
