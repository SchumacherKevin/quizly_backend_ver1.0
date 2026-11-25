# 08 – Login `POST /api/login/`

## Ziel
Login mit Username und Passwort setzt `access_token` und `refresh_token` als HttpOnly-Cookies (User Story 2).

## Kontext (eigenständig)
- **Vorbedingungen:** 02–07 sind fertig. In `auth_app/utils.py` gibt es `set_auth_cookies(response, refresh)`, in `conftest.py` die Fixtures `api_client` und `user` (`testuser` / `Test1234!`).
- Betroffene Dateien: `auth_app/api/serializers.py` (`LoginSerializer`), `auth_app/api/views.py` (`LoginView`), `auth_app/api/urls.py`, `auth_app/utils.py` (`authenticate_credentials`), `auth_app/tests/test_login.py`
- URL-Name: `login`
- **Vertrag:**
  - Request `{"username", "password"}`
  - 200: `{"detail": "Login successfully!", "user": {"id", "username", "email"}}` plus Cookies
  - 401 bei falschen Daten, mit **allgemein gehaltener** Meldung (US2)
  - 400 bei fehlenden Feldern
- **Frontend** (`quizly_frontend/shared/js/auth.js:65-89`): zeigt bei Fehlern `responseData.detail` an.
- **Wichtige Falle:** Wenn eine View `authentication_classes = []` hat, wandelt DRF ein `AuthenticationFailed` (401) in **403** um, weil ohne Authenticator kein `WWW-Authenticate`-Header gesetzt werden kann. Deshalb gibt die View die 401-Response **explizit** zurück: `Response({"detail": ...}, status=401)`.
- Die Tokens gehören **nie** in den Response-Body.

## Zyklen

### Zyklus 1: Erfolgreicher Login
- **Test:** `auth_app/tests/test_login.py::test_login_returns_user_data`
  - Act: `api_client.post(reverse("login"), {"username": "testuser", "password": "Test1234!"}, format="json")`
  - Assert: `status_code == 200`; `response.json() == {"detail": "Login successfully!", "user": {"id": user.id, "username": "testuser", "email": "test@example.com"}}`
- **Erwartetes Rot:** `NoReverseMatch: 'login'`
- **Green:**
  - `LoginSerializer` mit den Feldern `username` und `password`
  - `authenticate_credentials(data)` in `auth_app/utils.py` ruft `django.contrib.auth.authenticate` auf
  - `LoginView` (`AllowAny`, `authentication_classes = []`)
  - URL `login/`
- **Hinweis:** Die User-Daten liefert ein `UserSerializer` (`id`, `username`, `email`) in `auth_app/api/serializers.py`
- **Commit:** `feat(auth): add login endpoint returning user data`
- [x] erledigt

### Zyklus 2: Cookies werden gesetzt
- **Test:** `test_login_sets_httponly_cookies`: `response.cookies["access_token"]["httponly"]` und `response.cookies["refresh_token"]["httponly"]` sind `True`, die Werte sind nicht leer
- **Test:** `test_login_does_not_expose_tokens_in_body`: Weder `"access"` noch `"refresh"` noch der Cookie-Wert kommen in `response.content` vor
- **Erwartetes Rot:** `KeyError: 'access_token'`
- **Green:** `refresh = RefreshToken.for_user(user)` und `set_auth_cookies(response, refresh)` in der View bzw. in einem Helper `build_login_response(user)` in `utils.py`
- **Commit:** `feat(auth): set JWT cookies on login`
- [x] erledigt (umgesetzt als `build_login_response(user)` in `auth_app/utils.py`)

### Zyklus 3: Falsche Zugangsdaten ergeben 401 mit allgemeiner Meldung
- **Test:** `test_login_rejects_invalid_credentials` (parametrisiert: falsches Passwort für `testuser`; unbekannter User `ghost`)
  - Assert: `status_code == 401`, `response.json() == {"detail": "Invalid username or password."}`, keine Auth-Cookies gesetzt
- **Erwartetes Rot:** 200 oder ein Fehler, weil `authenticate` `None` liefert
- **Green:** Liefert `authenticate_credentials` `None`, gibt die View `Response({"detail": "Invalid username or password."}, status=401)` zurück
- **Commit:** `feat(auth): return generic 401 on invalid login`
- [x] erledigt

### Zyklus 4: Fehlende Felder ergeben 400
- **Test:** `test_login_requires_username_and_password` (parametrisiert: `{}`, nur Username, nur Passwort) ergibt 400 mit dem jeweiligen Feld-Key
- **Erwartetes Rot:** vermutlich schon grün durch `serializer.is_valid(raise_exception=True)`; dann als Absicherung committen
- **Commit:** `test(auth): require username and password on login`
- [x] erledigt (wie erwartet sofort grün, Absicherungstest)

### Zyklus 5: Inaktive User
- **Test:** `test_login_rejects_inactive_user`: `user.is_active = False` ergibt 401 mit derselben allgemeinen Meldung
- **Erwartetes Rot:** vermutlich grün (`ModelBackend` lehnt inaktive User ab); als Absicherung committen
- **Commit:** `test(auth): reject inactive users on login`
- [x] erledigt (wie erwartet sofort grün durch `ModelBackend`)

## Abschluss-Check
- [x] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [x] Status von Schritt 08 auf `[x]` gesetzt (Commit `docs: mark step 08 done`)
- [x] Stopp → Review
