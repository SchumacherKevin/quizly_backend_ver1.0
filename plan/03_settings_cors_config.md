# 03 – Settings, CORS und Konfiguration

## Ziel
`core/settings.py` liest alle Secrets und Parameter aus `.env`, und CORS, DRF und simplejwt sind passend zum Frontend konfiguriert.

## Referenzen
- `quizly_frontend/README.md` – JWT in HttpOnly-Cookies, CORS für das lokale Frontend
- `quizly_frontend/shared/js/auth.js` – `credentials: "include"` überall

## `.env.template`
```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.8-flash
WHISPER_MODEL=base
MAX_VIDEO_MINUTES=15
```
`GEMINI_MODEL` wird in Schritt 13 in AI Studio verifiziert und hier gegebenenfalls angepasst.

## Aufgaben
- [ ] `load_dotenv(BASE_DIR / ".env")` am Anfang der Settings
- [ ] `SECRET_KEY`, `DEBUG` (String → bool), `ALLOWED_HOSTS` (kommasepariert) aus der Umgebung
- [ ] `INSTALLED_APPS`: `rest_framework`, `rest_framework_simplejwt.token_blacklist`, `corsheaders`, `auth_app`, `quiz_app`
- [ ] `MIDDLEWARE`: `corsheaders.middleware.CorsMiddleware` **ganz oben**
- [ ] CORS:
  - `CORS_ALLOWED_ORIGINS` aus `CORS_ORIGINS`
  - `CORS_ALLOW_CREDENTIALS = True` (kein `*`)
- [ ] `REST_FRAMEWORK`:
  - `DEFAULT_AUTHENTICATION_CLASSES = ["auth_app.authentication.CookieJWTAuthentication"]`
  - `DEFAULT_PERMISSION_CLASSES = ["rest_framework.permissions.IsAuthenticated"]`
  - keine Pagination (das Frontend erwartet ein Array)
- [ ] `SIMPLE_JWT`:
  - `ACCESS_TOKEN_LIFETIME = timedelta(minutes=5)`
  - `REFRESH_TOKEN_LIFETIME = timedelta(days=1)`
  - `ROTATE_REFRESH_TOKENS = False`
  - `BLACKLIST_AFTER_ROTATION = False`
- [ ] Eigene Settings: `AUTH_COOKIE_SECURE = not DEBUG`, `AUTH_COOKIE_SAMESITE = "Lax"`
- [ ] Quizly-Settings: `GEMINI_API_KEY`, `GEMINI_MODEL`, `WHISPER_MODEL`, `MAX_VIDEO_MINUTES` (int)
- [ ] `LANGUAGE_CODE`, `TIME_ZONE = "UTC"`, `USE_TZ = True` (ISO-Zeitstempel in UTC)

## Hinweise
- Das Frontend muss über `127.0.0.1:5500` geöffnet werden (nicht `localhost`), sonst ist der Request cross-site und Lax-Cookies werden nicht gesendet. Das gehört in die README.
- Da `SessionAuthentication` nicht verwendet wird, greift die DRF-CSRF-Prüfung nicht.

## Akzeptanzkriterien
- [ ] Ohne `.env` gibt es eine klare Fehlermeldung oder einen sicheren Default (kein Secret im Code)
- [ ] Ein Preflight-`OPTIONS`-Request von `http://127.0.0.1:5500` liefert `Access-Control-Allow-Credentials: true`
- [ ] `python manage.py migrate` legt die Blacklist-Tabellen an

## Tests
- `test_settings.py`: Die CORS-Origin-Liste wird korrekt aus der Env gelesen.
- Preflight-Test mit dem Django-Test-Client (Header `Origin`, `Access-Control-Request-Method`).

## Commit-Message
`feat(core): configure settings, CORS and JWT via environment`
