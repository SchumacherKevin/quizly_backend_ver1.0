# Quizly Backend

Quizly turns a YouTube video into a quiz. Paste a link and the backend downloads the
audio, transcribes it locally with Whisper and lets Google Gemini write a quiz with
**10 questions and 4 answer options each**. Users can list, rename, play and delete
their quizzes in the [Quizly frontend](#frontend).

This repository contains the Django REST API. The frontend is a separate Vanilla JS
project.

## Features

- Registration, login and logout with JWT stored in **HttpOnly cookies**
  (refresh token is blacklisted on logout, automatic access token refresh)
- Create a quiz from a YouTube URL (`watch?v=`, `youtu.be/`, `shorts/`, mobile links)
- Pipeline: **yt-dlp** (audio) → **Whisper** (local transcription) → **Gemini Flash**
  (one request per quiz) → database (atomic)
- Gemini is the default; any OpenAI-compatible AI API (OpenAI, Mistral, Groq,
  OpenRouter, local Ollama/LM Studio) can be used instead via `.env`
  ([details](#using-another-ai-provider))
- List, view, edit (title/description) and delete your own quizzes;
  other users' quizzes are protected (403)
- Django admin to edit quizzes and single questions
- 100 % test coverage, all external services mocked in tests

## Tech stack

| Area | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | Django 6.1, Django REST Framework 3.18 |
| Auth | djangorestframework-simplejwt (cookie based), token blacklist |
| CORS | django-cors-headers |
| Video / audio | yt-dlp, FFmpeg |
| Transcription | openai-whisper (runs locally, CPU is fine) |
| Quiz generation | google-genai (Gemini Flash, default), openai (any OpenAI-compatible API) |
| Database | SQLite |
| Quality | pytest, pytest-django, pytest-cov, black, isort, flake8 |

## Requirements

- **Python 3.14**
- **FFmpeg must be installed globally** and available on the `PATH`.
  yt-dlp and Whisper both need it to read audio.
  - Windows: `winget install ffmpeg` (or download a build from
    <https://www.gyan.dev/ffmpeg/builds/> and add its `bin` folder to `PATH`)
  - macOS: `brew install ffmpeg`
  - Linux (Debian/Ubuntu): `sudo apt install ffmpeg`
  - Check: `ffmpeg -version` must print a version in a **new** terminal
- A Google Gemini API key: <https://ai.google.dev/> (Google AI Studio), or access
  to another AI API, see [Using another AI provider](#using-another-ai-provider)

## Installation (Windows PowerShell)

```powershell
git clone https://github.com/SchumacherKevin/quizly_backend_ver1.0.git
cd quizly_backend_ver1.0
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.template .env      # then fill in the values, see below
python manage.py migrate
python manage.py createsuperuser  # optional, for /admin/
python manage.py runserver
```

If `Activate.ps1` fails with "running scripts is disabled on this system", allow
scripts for the current terminal session only and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux use `python3.14 -m venv .venv`, `source .venv/bin/activate` and
`cp .env.template .env`.

The API now runs at <http://127.0.0.1:8000/api/>, the admin at
<http://127.0.0.1:8000/admin/>.

`openai-whisper` installs PyTorch, so the first `pip install` downloads a few hundred
MB.

## Environment variables

All settings are read from `.env` (never commit it). `.env.template` lists every key.

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | yes | – | Django secret key, any long random string |
| `DEBUG` | no | `False` | **Keep `True` for local development over HTTP.** With `False` the auth cookies are `Secure` and the browser only sends them over HTTPS |
| `ALLOWED_HOSTS` | no | `127.0.0.1,localhost` | Comma separated hosts |
| `CORS_ORIGINS` | no | `http://127.0.0.1:5500,http://localhost:5500` | Comma separated frontend origins |
| `AI_PROVIDER` | no | `gemini` | `gemini` or `openai` (any OpenAI-compatible API) |
| `GEMINI_API_KEY` | with `gemini` | – | API key from Google AI Studio |
| `GEMINI_MODEL` | no | `gemini-3.8-flash` | Gemini model used for quiz generation |
| `OPENAI_API_KEY` | with `openai`* | – | Key of the OpenAI-compatible provider (*not needed for local servers) |
| `OPENAI_MODEL` | with `openai` | – | Model name at that provider |
| `OPENAI_BASE_URL` | no | `https://api.openai.com/v1` | API endpoint of that provider |
| `WHISPER_MODEL` | no | `base` | Whisper model size (`tiny`, `base`, `small`, ...) |
| `MAX_VIDEO_MINUTES` | no | `15` | Longer videos are rejected with 400 |

Generate a secret key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Using another AI provider

Gemini is the default and needs no extra configuration. To change only the
**Gemini model**, set `GEMINI_MODEL` (e.g. `gemini-3.7-flash`).

To use **another AI API**, set `AI_PROVIDER=openai`. This works with every provider
that offers the OpenAI-compatible *Chat Completions* API with JSON mode. Then
restart the server. Examples for `.env`:

```dotenv
# OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=<model name, e.g. a current GPT mini model>

# Local model with Ollama (no key needed, runs on your machine)
AI_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1

# Any other OpenAI-compatible provider (Mistral, Groq, OpenRouter, ...)
AI_PROVIDER=openai
OPENAI_BASE_URL=<the provider's OpenAI-compatible endpoint>
OPENAI_API_KEY=<your key>
OPENAI_MODEL=<model name at that provider>
```

Notes:

- The prompt, the JSON parsing and the validation (10 questions, 4 unique options,
  answer must be one of the options) are the same for every provider. If a model
  breaks the format, the API answers 500 with the reason, e.g.
  `{"detail": "Generated question is invalid."}`, and nothing is saved.
- Smaller local models often break these rules; use a capable model.
- Providers other than Gemini/OpenAI-compatible (e.g. a native SDK) need a new
  request function in `quiz_app/services/generation.py`, registered in `PROVIDERS`.

## Frontend

Open the frontend (`quizly_frontend`) with VS Code **Live Server** at
**<http://127.0.0.1:5500>**, not `localhost:5500`. The backend runs on `127.0.0.1`;
with `localhost` the requests become cross-site and the browser does not send the
`SameSite=Lax` auth cookies, so every request would be 401.

## Good to know

- **Whisper** downloads the model on the first quiz (about 140 MB for `base`) into
  your user cache. The first quiz therefore takes longer.
- Quiz creation is **synchronous**: depending on the video length the request takes
  from several seconds to a few minutes. The frontend shows a loading overlay.
- The **Gemini free tier** has tight rate limits. Every quiz uses exactly one request
  and failed requests are not retried. If Gemini is overloaded (HTTP 503) the API
  answers 500, so try again later.
- Keep **yt-dlp** up to date, YouTube changes often:
  `pip install -U yt-dlp`
- yt-dlp may warn *"No supported JavaScript runtime could be found"*. Downloads
  still work, but YouTube increasingly needs a JS runtime. If videos stop loading,
  install [Deno](https://deno.com/) (`winget install DenoLand.Deno`) and restart the
  server.
- yt-dlp verifies HTTPS certificates against the **operating system's certificate
  store** (`compat_opts: no-certifi`). This keeps quiz creation working behind
  antivirus HTTPS scanners (e.g. Norton Web/Mail Shield) that re-sign traffic with
  their own root certificate.
- Videos may be at most **15 minutes** long (`MAX_VIDEO_MINUTES`). Longer videos,
  livestreams and invalid links are rejected with 400.
- The frontend shows the same message ("Error generating quiz") for every failed
  quiz creation. The actual reason is in the response body and in the server log:

  | Status | Body | Meaning |
  |---|---|---|
  | 400 | `{"url": ["This field may not be blank."]}` | URL field was empty |
  | 400 | `{"url": ["Invalid YouTube URL."]}` | Not a supported YouTube link |
  | 400 | `{"detail": "Video is longer than 15 minutes."}` | Above `MAX_VIDEO_MINUTES` |
  | 400 | `{"detail": "Video duration is unknown."}` | e.g. livestreams |
  | 400 | `{"detail": "Video could not be loaded."}` | Private, removed or blocked video |
  | 500 | `{"detail": "Transcription failed."}` | Whisper/FFmpeg problem |
  | 500 | `{"detail": "Gemini request failed."}` | Gemini error, e.g. overloaded (503) |
  | 500 | `{"detail": "Generated question is invalid."}` (or similar) | AI answer broke the quiz rules |
- After logout the cookies are deleted and the refresh token is blacklisted. An
  already issued access token stays technically valid until it expires (max.
  5 minutes), but the browser no longer has it.

## API overview

Base URL: `http://127.0.0.1:8000/api/`. Authentication uses the `access_token` and
`refresh_token` HttpOnly cookies set by the login.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `register/` | no | Create a user (`username`, `email`, `password`, `confirmed_password`) → 201 |
| POST | `login/` | no | Log in, sets both cookies, returns user data → 200 / 401 |
| POST | `logout/` | yes | Blacklist refresh token, delete cookies → 200 |
| POST | `token/refresh/` | refresh cookie | New `access_token` cookie → 200 / 401 |
| POST | `quizzes/` | yes | Create a quiz from `{"url": "<YouTube URL>"}` → 201 / 400 / 500 |
| GET | `quizzes/` | yes | List your quizzes (newest first, unpaginated array) |
| GET | `quizzes/{id}/` | yes | Get one quiz with its questions → 200 / 403 / 404 |
| PATCH | `quizzes/{id}/` | yes | Update `title` and/or `description` → 200 / 400 / 403 / 404 |
| DELETE | `quizzes/{id}/` | yes | Delete a quiz and its questions → 204 / 403 / 404 |

Error responses use `{"detail": "..."}` or DRF field errors such as
`{"url": ["Invalid YouTube URL."]}`. Without valid cookies every protected endpoint
returns 401.

Example quiz:

```json
{
  "id": 1,
  "title": "Python Basics",
  "description": "A short quiz about Python.",
  "created_at": "2026-11-26T12:34:56.789Z",
  "updated_at": "2026-11-26T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "questions": [
    {
      "id": 1,
      "question_title": "Who created Python?",
      "question_options": ["Guido van Rossum", "Linus Torvalds", "James Gosling", "Dennis Ritchie"],
      "answer": "Guido van Rossum"
    }
  ]
}
```

Questions include `created_at` and `updated_at` only in the response of
`POST quizzes/`.

## Development

```powershell
pip install -r requirements-dev.txt
pytest                      # runs all tests with coverage report
black . ; isort . ; flake8  # format and lint (line length 79)
```

- Tests never touch the network: yt-dlp, Whisper and the AI providers are always
  mocked.
- The project was built test-first (Red → Green → Refactor, one commit per cycle).
  The step-by-step plan and conventions live in [`plan/00_overview.md`](plan/00_overview.md).
- Conventions: functions max. 14 lines (docstring not counted), Google style
  docstrings, `views.py` contains only views, helpers live in `utils.py` or
  `quiz_app/services/`.

## Project structure

```
quizly_backend_ver1.0/
├── core/                  # settings, root URLs, env helpers (env.py)
├── auth_app/
│   ├── api/               # serializers, views, urls
│   ├── authentication.py  # CookieJWTAuthentication
│   ├── utils.py           # cookie and token helpers
│   └── tests/
├── quiz_app/
│   ├── api/               # serializers, views, urls, permissions
│   ├── services/          # youtube, transcription, generation, pipeline, exceptions
│   ├── models.py, admin.py, utils.py
│   └── tests/
├── plan/                  # TDD implementation plan (00–17)
├── conftest.py            # shared pytest fixtures
├── .env.template
├── requirements.txt, requirements-dev.txt
├── pyproject.toml         # pytest, coverage, black, isort
└── setup.cfg              # flake8
```
