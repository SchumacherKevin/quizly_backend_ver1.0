# 04 – Settings, Env, CORS und JWT

## Ziel
Alle Secrets und Parameter kommen aus `.env`; CORS mit Credentials und simplejwt (inklusive Blacklist) sind passend zum Frontend konfiguriert.

## Kontext (eigenständig)
- **Vorbedingungen:** 02 und 03 sind fertig (pytest läuft, Fixtures `api_client`, `user`).
- Betroffene Dateien: `core/env.py` (neu), `core/settings.py`, `.env.template` (neu), `.env` (lokal, nicht committen), `core/tests/test_env.py`, `core/tests/test_settings.py`
- Das Frontend läuft auf `http://127.0.0.1:5500` (Live Server) und sendet **jeden** Request mit `credentials: "include"`. Deshalb muss `CORS_ALLOW_CREDENTIALS = True` sein, und Origins werden explizit angegeben (kein `*`).
- Die JWT-Cookies werden mit `SameSite=Lax` gesetzt, mit `Secure` nur wenn `DEBUG` aus ist.
- **Noch nicht** in diesem Schritt: `DEFAULT_AUTHENTICATION_CLASSES` mit `CookieJWTAuthentication`. Die Klasse existiert erst ab Schritt 07 und wird dort eingetragen.
- Entscheidungen: Access 5 min, Refresh 1 Tag, keine Rotation, Blacklist-App aktiv; `TIME_ZONE = "UTC"`, `USE_TZ = True`; keine Pagination.

## Referenzen
- `quizly_frontend/README.md` – JWT und HttpOnly-Cookies, CORS
- `quizly_frontend/shared/js/config.js:1` – `API_BASE_URL = "http://127.0.0.1:8000/api/"`

## `.env.template` (Zielinhalt)
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
`GEMINI_MODEL` wird in Schritt 13 verifiziert.

## Zyklen

### Zyklus 1: Env-Helper `get_bool`
- **Test:** `core/tests/test_env.py::test_get_bool` (parametrisiert)
  - Arrange: `monkeypatch.setenv("FLAG", value)`
  - Werte: `"True"`, `"true"`, `"1"`, `"yes"` → `True`; `"False"`, `"0"`, `"no"` → `False`
  - Assert: `get_bool("FLAG", default=False) == expected`
- **Test:** `test_get_bool_returns_default_when_missing`: Mit `monkeypatch.delenv("FLAG", raising=False)` ergibt `get_bool("FLAG", True)` den Wert `True`
- **Erwartetes Rot:** `ModuleNotFoundError: core.env`
- **Green:** `core/env.py` → `def get_bool(name: str, default: bool) -> bool`
- **Commit:** `feat(core): add boolean env helper`
- [ ] erledigt

### Zyklus 2: Env-Helper `get_list` und `get_int`
- **Test:** `test_get_list_splits_and_strips`: `"a, b ,c"` ergibt `["a", "b", "c"]`; ein leerer String ergibt `[]`; fehlt die Variable, gilt der Default
- **Test:** `test_get_int_parses_value`: `"15"` ergibt `15`; fehlt die Variable, gilt der Default
- **Test:** `test_get_int_raises_on_invalid`: `"abc"` löst `ImproperlyConfigured` aus
- **Erwartetes Rot:** `ImportError` für `get_list` / `get_int`
- **Green:** `get_list(name, default) -> list[str]`, `get_int(name, default) -> int`
- **Commit:** `feat(core): add list and int env helpers`
- [ ] erledigt

### Zyklus 3: Settings lesen `.env`
- **Test:** `core/tests/test_settings.py::test_quizly_settings_have_expected_types`
  - Assert: `settings.MAX_VIDEO_MINUTES` ist ein `int`, `settings.WHISPER_MODEL` ist ein `str`, `settings.GEMINI_MODEL` ist ein `str`, und `hasattr(settings, "GEMINI_API_KEY")`
- **Test:** `test_secret_key_not_hardcoded_default`: `settings.SECRET_KEY` beginnt nicht mit `"django-insecure-"`
- **Erwartetes Rot:** `AttributeError: 'Settings' object has no attribute 'MAX_VIDEO_MINUTES'`
- **Green:**
  - `load_dotenv(BASE_DIR / ".env")` oben in `settings.py`
  - `SECRET_KEY = os.environ["SECRET_KEY"]` (fehlt die Variable, gibt es einen klaren `KeyError`)
  - `DEBUG = get_bool("DEBUG", False)`, `ALLOWED_HOSTS = get_list(...)`
  - `GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")`, `GEMINI_MODEL`, `WHISPER_MODEL` (Default `"base"`), `MAX_VIDEO_MINUTES = get_int(..., 15)`
  - `TIME_ZONE = "UTC"`, `USE_TZ = True`
  - `.env.template` committen; `.env` lokal aus dem Template erzeugen (mit einem echten, zufälligen `SECRET_KEY`)
- **Hinweis:** Für pytest muss `.env` existieren. Im README (Schritt 17) vermerken.
- **Commit:** `feat(core): load settings from environment via dotenv`
- [ ] erledigt

### Zyklus 4: CORS mit Credentials
- **Test:** `test_cors_preflight_allows_frontend_origin`
  - Act: `client.options("/admin/login/", HTTP_ORIGIN="http://127.0.0.1:5500", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")`
  - Assert: `response["Access-Control-Allow-Origin"] == "http://127.0.0.1:5500"` und `response["Access-Control-Allow-Credentials"] == "true"`
- **Test:** `test_cors_rejects_unknown_origin`: mit Origin `http://evil.example` fehlt der Header `Access-Control-Allow-Origin`
- **Erwartetes Rot:** `KeyError: 'Access-Control-Allow-Origin'`
- **Green:** `corsheaders` in `INSTALLED_APPS`; `CorsMiddleware` **ganz oben** in `MIDDLEWARE`; `CORS_ALLOWED_ORIGINS = get_list("CORS_ORIGINS", [...])`; `CORS_ALLOW_CREDENTIALS = True`
- **Commit:** `feat(core): enable CORS with credentials for frontend origins`
- [ ] erledigt

### Zyklus 5: DRF- und simplejwt-Konfiguration
- **Test:** `test_simple_jwt_lifetimes`: `ACCESS_TOKEN_LIFETIME == timedelta(minutes=5)`, `REFRESH_TOKEN_LIFETIME == timedelta(days=1)`, `ROTATE_REFRESH_TOKENS is False`
- **Test:** `test_token_blacklist_installed`: `"rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS` und `"rest_framework" in settings.INSTALLED_APPS`
- **Test:** `test_default_permission_is_authenticated`: `settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] == ["rest_framework.permissions.IsAuthenticated"]`
- **Test:** `test_auth_cookie_settings`: `settings.AUTH_COOKIE_SAMESITE == "Lax"` und `settings.AUTH_COOKIE_SECURE == (not settings.DEBUG)`
- **Erwartetes Rot:** `AttributeError` bzw. `KeyError: 'SIMPLE_JWT'`
- **Green:** Werte in `settings.py` eintragen; danach `python manage.py migrate` (legt die Blacklist-Tabellen an)
- **Commit:** `feat(core): configure DRF defaults, simplejwt and blacklist`
- [ ] erledigt

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] `.env` ist nicht getrackt, `.env.template` ist getrackt
- [ ] Status von Schritt 04 auf `[x]` gesetzt (Commit `docs: mark step 04 done`)
- [ ] Stopp → Review → `git merge --ff-only step/04-settings`
