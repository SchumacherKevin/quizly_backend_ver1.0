# 09 – Logout und Token-Refresh

## Ziel
- `POST /api/logout/` blacklistet den Refresh-Token und löscht beide Cookies (User Story 3).
- `POST /api/token/refresh/` stellt aus dem Refresh-Cookie einen neuen Access-Token als Cookie aus.

## Kontext (eigenständig)
- **Vorbedingungen:** 02–08 sind fertig.
  - `CookieJWTAuthentication` ist Standard; ohne Cookie gibt es 401.
  - `auth_app/utils.py` enthält `ACCESS_COOKIE`, `REFRESH_COOKIE`, `set_access_cookie`, `set_auth_cookies` und `delete_auth_cookies`.
  - Die Fixture `auth_client` hat beide Cookies für `user`.
  - Die Blacklist-App ist installiert und migriert.
- Betroffene Dateien: `auth_app/api/views.py` (`LogoutView`, `CookieTokenRefreshView`), `auth_app/api/urls.py`, `auth_app/utils.py` (`blacklist_refresh_token`, `refresh_access_token`), `auth_app/tests/test_logout.py`, `auth_app/tests/test_refresh.py`
- URL-Namen: `logout` (`logout/`), `token-refresh` (`token/refresh/`)
- **Vertrag Logout:** authentifiziert; 200 mit `{"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}`; ohne Login 401
- **Vertrag Refresh:** Refresh-Cookie nötig; 200 mit `{"detail": "Token refreshed"}` und neuem `access_token`-Cookie; 401, wenn der Token fehlt oder ungültig ist. Das Frontend sendet **keinen Body und keinen Content-Type** (`quizly_frontend/shared/js/auth.js:263-274`).
- Keine Rotation; der Access-Token kommt nicht in den Body.
- **Falle:** Die Refresh-View hat `authentication_classes = []`. Deshalb gibt sie die 401-Antworten **explizit** zurück (`Response(..., status=401)`), sonst macht DRF daraus 403.
- Der Access-Token bleibt nach dem Logout bis zu 5 Minuten technisch gültig (zustandslos). Das ist akzeptiert, weil das Cookie gelöscht wird. Wird im README dokumentiert.

## Zyklen – Logout

### Zyklus 1: Logout antwortet mit 200
- **Test:** `auth_app/tests/test_logout.py::test_logout_returns_success_message`
  - Act: `auth_client.post(reverse("logout"))`
  - Assert: 200 und der exakte `detail`-Text
- **Erwartetes Rot:** `NoReverseMatch: 'logout'`
- **Green:** `LogoutView(APIView)` mit `IsAuthenticated`, URL `logout/`
- **Commit:** `feat(auth): add logout endpoint`
- [ ] erledigt

### Zyklus 2: Logout löscht die Cookies
- **Test:** `test_logout_deletes_auth_cookies`: Für `access_token` und `refresh_token` gilt in `response.cookies` `max-age == 0` und `value == ""`
- **Erwartetes Rot:** `KeyError: 'access_token'`
- **Green:** `delete_auth_cookies(response)` in der View
- **Commit:** `feat(auth): delete auth cookies on logout`
- [ ] erledigt

### Zyklus 3: Logout blacklistet den Refresh-Token
- **Test:** `test_logout_blacklists_refresh_token`
  - Arrange: `jti = RefreshToken(auth_client.cookies["refresh_token"].value)["jti"]`
  - Assert nach dem Logout: `BlacklistedToken.objects.filter(token__jti=jti).exists()`
- **Erwartetes Rot:** `False`
- **Green:** `blacklist_refresh_token(raw)` in `utils.py` mit `RefreshToken(raw).blacklist()`; `TokenError` wird abgefangen und ignoriert
- **Commit:** `feat(auth): blacklist refresh token on logout`
- [ ] erledigt

### Zyklus 4: Randfälle beim Logout
- **Test:** `test_logout_requires_authentication`: `api_client.post(reverse("logout"))` ohne Cookies ergibt **401**
- **Test:** `test_logout_succeeds_with_invalid_refresh_cookie`: Mit `auth_client.cookies["refresh_token"] = "garbage"` ergibt sich trotzdem 200, und die Cookies sind gelöscht
- **Test:** `test_logout_succeeds_without_refresh_cookie`: Das Refresh-Cookie wird entfernt, das Ergebnis ist trotzdem 200
- **Erwartetes Rot:** möglicherweise eine Exception bei fehlendem Cookie
- **Green:** `blacklist_refresh_token(None)` macht nichts
- **Commit:** `feat(auth): handle missing or invalid refresh token on logout`
- [ ] erledigt

## Zyklen – Refresh

### Zyklus 5: Refresh mit gültigem Cookie
- **Test:** `auth_app/tests/test_refresh.py::test_refresh_sets_new_access_cookie`
  - Arrange: `api_client.cookies["refresh_token"] = str(RefreshToken.for_user(user))`
  - Act: `api_client.post(reverse("token-refresh"))` (ohne Body)
  - Assert: 200, `response.json() == {"detail": "Token refreshed"}`, `response.cookies["access_token"]["httponly"] is True`; der neue Wert ist ein gültiger `AccessToken` für `user`
- **Erwartetes Rot:** `NoReverseMatch: 'token-refresh'`
- **Green:**
  - `CookieTokenRefreshView` (`AllowAny`, `authentication_classes = []`)
  - `refresh_access_token(raw) -> str` in `utils.py` gibt `str(RefreshToken(raw).access_token)` zurück
  - `set_access_cookie` setzt das Cookie
- **Commit:** `feat(auth): add cookie based token refresh endpoint`
- [ ] erledigt

### Zyklus 6: Kein Token im Body und keine Rotation
- **Test:** `test_refresh_does_not_return_tokens`: Body ist genau `{"detail": "Token refreshed"}`, und `"refresh_token"` steht nicht in `response.cookies`
- **Erwartetes Rot:** vermutlich grün; als Absicherung committen
- **Commit:** `test(auth): ensure refresh does not expose or rotate tokens`
- [ ] erledigt

### Zyklus 7: Ungültige, fehlende oder geblacklistete Tokens
- **Test:** `test_refresh_without_cookie_returns_401`: 401 mit `{"detail": "Refresh token not found."}`
- **Test:** `test_refresh_with_invalid_cookie_returns_401`: `"garbage"` ergibt 401 mit `{"detail": "Refresh token invalid."}`
- **Test:** `test_refresh_with_blacklisted_token_returns_401`: Den Token vorher mit `.blacklist()` sperren, dann ergibt sich 401
- **Test:** `test_refresh_after_logout_fails`: Logout mit `auth_client`, danach den Refresh mit dem **alten** Refresh-Wert erneut setzen; Ergebnis 401
- **Erwartetes Rot:** Exception (`TokenError`) oder 403
- **Green:** `TokenError` abfangen und explizit 401 zurückgeben
- **Commit:** `feat(auth): reject missing, invalid and blacklisted refresh tokens`
- [ ] erledigt

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Status von Schritt 09 auf `[x]` gesetzt (Commit `docs: mark step 09 done`)
- [ ] Stopp → Review → `git merge --ff-only step/09-logout-refresh`
