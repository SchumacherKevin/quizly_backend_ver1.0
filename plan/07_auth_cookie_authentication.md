# 07 – Cookie-basierte JWT-Authentifizierung

## Ziel
DRF authentifiziert Requests über das HttpOnly-Cookie `access_token`. Cookie-Helper und die Fixture `auth_client` stehen für die folgenden Schritte bereit.

## Kontext (eigenständig)
- **Vorbedingungen:** 02–06 sind fertig. In `settings.py` sind `SIMPLE_JWT` (Access 5 min, Refresh 1 Tag), `AUTH_COOKIE_SECURE` und `AUTH_COOKIE_SAMESITE = "Lax"` gesetzt; die App `token_blacklist` ist installiert.
- Betroffene Dateien: `auth_app/authentication.py` (neu), `auth_app/utils.py` (neu), `core/settings.py` (`DEFAULT_AUTHENTICATION_CLASSES`), `conftest.py` (`auth_client`), `auth_app/tests/test_authentication.py`, `auth_app/tests/test_cookie_utils.py`
- Das Frontend sendet **keinen** `Authorization`-Header, nur Cookies (`credentials: "include"`). Bei 401 oder 403 versucht es einen Refresh (`quizly_frontend/shared/js/auth.js:276-306`).
- Wichtig: Fehlende Authentifizierung muss **401** ergeben, nicht 403. DRF liefert nur dann 401, wenn die Auth-Klasse `authenticate_header` implementiert; `JWTAuthentication` tut das bereits (`Bearer realm="api"`).
- Cookie-Namen als Konstanten: `ACCESS_COOKIE = "access_token"`, `REFRESH_COOKIE = "refresh_token"`

## Zyklen

### Zyklus 1: Kein Cookie bedeutet anonym
- **Test:** `auth_app/tests/test_authentication.py::test_authenticate_without_cookie_returns_none`
  - Arrange: `request = APIRequestFactory().get("/")`
  - Act: `CookieJWTAuthentication().authenticate(request)`
  - Assert: `is None`
- **Erwartetes Rot:** `ModuleNotFoundError: auth_app.authentication`
- **Green:** `class CookieJWTAuthentication(JWTAuthentication)` mit `authenticate(self, request)`, das `request.COOKIES.get(ACCESS_COOKIE)` liest; ohne Cookie gibt es `None` zurück
- **Hinweis:** Cookie-Konstanten `ACCESS_COOKIE` und `REFRESH_COOKIE` liegen schon ab hier in `auth_app/utils.py`
- **Commit:** `feat(auth): add cookie based JWT authentication class`
- [x] erledigt

### Zyklus 2: Gültiges Cookie liefert den User
- **Test:** `test_authenticate_with_valid_cookie_returns_user`
  - Arrange: `token = AccessToken.for_user(user)`; `request.COOKIES["access_token"] = str(token)`
  - Assert: `result[0] == user`
- **Erwartetes Rot:** `None` statt eines Tupels
- **Green:** `validated = self.get_validated_token(raw)`; Rückgabe `(self.get_user(validated), validated)`
- **Commit:** `feat(auth): authenticate user from access_token cookie`
- [x] erledigt

### Zyklus 3: Ungültiges oder abgelaufenes Token
- **Test:** `test_authenticate_with_invalid_cookie_raises` (parametrisiert):
  - `"garbage"`
  - ein abgelaufenes Token (`token = AccessToken.for_user(user)`, dann `token.set_exp(lifetime=-timedelta(seconds=1))`)
  - Assert: `pytest.raises(InvalidToken)`
- **Test:** `test_authenticate_header_is_set`: `CookieJWTAuthentication().authenticate_header(request)` ist nicht leer (das sichert 401 statt 403)
- **Erwartetes Rot:** Bei korrekt umgesetztem Zyklus 2 vermutlich schon grün; dann als Absicherung committen
- **Commit:** `test(auth): cover invalid and expired access tokens`
- [x] erledigt (wie erwartet sofort grün, Absicherungstests)

### Zyklus 4: Cookie-Helper setzen
- **Test:** `auth_app/tests/test_cookie_utils.py::test_set_auth_cookies_sets_httponly_cookies`
  - Arrange: `response = Response()`, `refresh = RefreshToken.for_user(user)`
  - Act: `set_auth_cookies(response, refresh)`
  - Assert für beide Cookies: `cookie["httponly"] is True`, `cookie["samesite"] == "Lax"`, `cookie["path"] == "/"`
  - Access: `cookie["max-age"] == 300`; Refresh: `cookie["max-age"] == 86400`
  - `AccessToken(response.cookies["access_token"].value)["user_id"] == str(user.id)`. Achtung: `refresh.access_token` erzeugt bei **jedem** Zugriff ein neues Token mit neuer `jti`, deshalb ist ein direkter String-Vergleich nicht möglich.
- **Test:** `test_set_access_cookie_only_sets_access`: `set_access_cookie(response, "abc")` setzt nur `access_token`
- **Erwartetes Rot:** `ImportError` aus `auth_app.utils`
- **Green:** In `auth_app/utils.py`:
  - `_cookie_options(lifetime)` liefert ein Dict (`httponly`, `secure=settings.AUTH_COOKIE_SECURE`, `samesite`, `path`, `max_age=int(lifetime.total_seconds())`)
  - `set_access_cookie(response, token)`
  - `set_refresh_cookie(response, token)`
  - `set_auth_cookies(response, refresh)` setzt beide
- **Commit:** `feat(auth): add helpers to set auth cookies`
- [x] erledigt

### Zyklus 5: Cookies löschen
- **Test:** `test_delete_auth_cookies_expires_both`: Nach `delete_auth_cookies(response)` gilt für beide Cookies `value == ""` und `max-age == 0`
- **Erwartetes Rot:** `ImportError`
- **Green:** `delete_auth_cookies(response)` mit `response.delete_cookie(name, path="/", samesite=...)` für beide Cookies
- **Commit:** `feat(auth): add helper to delete auth cookies`
- [x] erledigt

### Zyklus 6: Als Standard aktivieren, Fixture `auth_client`
- **Test:** `test_default_authentication_class_is_cookie_jwt`: `settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] == ["auth_app.authentication.CookieJWTAuthentication"]`
- **Test:** `test_auth_client_fixture_has_cookies`: `"access_token" in auth_client.cookies` und `"refresh_token" in auth_client.cookies`
- **Erwartetes Rot:** `KeyError` bzw. `fixture 'auth_client' not found`
- **Green:**
  - In `settings.py` `DEFAULT_AUTHENTICATION_CLASSES` eintragen
  - `conftest.py`: `auth_client(api_client, user)` erzeugt `refresh = RefreshToken.for_user(user)` und setzt `api_client.cookies["access_token"] = str(refresh.access_token)` sowie `api_client.cookies["refresh_token"] = str(refresh)`
- **Commit:** `feat(auth): use cookie JWT authentication by default and add auth_client fixture`
- [ ] erledigt

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün (auch die Tests aus Schritt 06: Register bleibt öffentlich)
- [ ] Status von Schritt 07 auf `[x]` gesetzt (Commit `docs: mark step 07 done`)
- [ ] Stopp → Review
