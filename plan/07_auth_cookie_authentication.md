# 07 – Cookie-basierte JWT-Authentifizierung

## Ziel
DRF authentifiziert Requests über das HttpOnly-Cookie `access_token` statt über den `Authorization`-Header.

## Referenzen
- `docs/Quizly Checkliste.pdf` – „JWT und HTTP-ONLY-COOKIES“
- `quizly_frontend/shared/js/auth.js:276-306` – kein Auth-Header, 401 löst den Refresh aus

## Aufgaben
- [ ] `auth_app/authentication.py` – `CookieJWTAuthentication(JWTAuthentication)`:
  - `authenticate(request)`: liest `request.COOKIES.get("access_token")`; ohne Cookie gibt sie `None` zurück
  - Token mit `self.get_validated_token(raw)` prüfen und mit `self.get_user(token)` den User holen
  - Ungültiger oder abgelaufener Token → `InvalidToken` (DRF antwortet mit 401)
  - `authenticate_header` liefert einen Wert, damit DRF 401 statt 403 zurückgibt
- [ ] `auth_app/utils.py` – Cookie-Helper:
  - `set_access_cookie(response, token)`
  - `set_refresh_cookie(response, token)`
  - `delete_auth_cookies(response)`
  - Gemeinsame Optionen: `httponly=True`, `secure=settings.AUTH_COOKIE_SECURE`, `samesite=settings.AUTH_COOKIE_SAMESITE`, `max_age` aus der jeweiligen `SIMPLE_JWT`-Lifetime, `path="/"`

## Akzeptanzkriterien
- [ ] Request ohne Cookie auf eine geschützte Route → **401** (nicht 403)
- [ ] Gültiges Cookie → `request.user` ist gesetzt
- [ ] Abgelaufenes oder manipuliertes Token → 401

## Tests
- `auth_app/tests/test_authentication.py`: kein Cookie, gültiges Cookie, ungültiges Token, abgelaufenes Token (mit gepatchter Lifetime)
- Cookie-Helper setzen die Flags `httponly`, `samesite` und `max-age`

## Commit-Message
`feat(auth): authenticate via access_token cookie`
