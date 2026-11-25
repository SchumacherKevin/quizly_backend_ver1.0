# 09 – Logout und Token-Refresh

## Ziel
Logout macht den Refresh-Token unbrauchbar und löscht die Cookies (US3). Der Refresh stellt einen neuen Access-Token als Cookie aus.

## Referenzen
- `docs/Endpoint Dokumentation.pdf` – Logout, Token Refresh
- `quizly_frontend/shared/js/auth.js:128-152` – Logout, Antwort wird ignoriert
- `quizly_frontend/shared/js/auth.js:263-274` – Refresh ohne Body und ohne Content-Type

## Logout – `POST /api/logout/`
- [ ] `LogoutView(APIView)` mit `IsAuthenticated`
- [ ] Refresh-Token aus dem Cookie lesen und `RefreshToken(raw).blacklist()` aufrufen; `TokenError` abfangen (der Token ist dann ohnehin ungültig)
- [ ] `delete_auth_cookies(response)`
- [ ] 200 mit `{"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}`
- [ ] Die Logik (Blacklisting) gehört nach `auth_app/utils.py`, nicht in die View

## Refresh – `POST /api/token/refresh/`
- [ ] `CookieTokenRefreshView(APIView)`: `AllowAny`, `authentication_classes = []`
- [ ] Refresh-Token aus dem Cookie lesen; fehlt er → 401 `{"detail": "Refresh token not found."}`
- [ ] `RefreshToken(raw)` validieren (prüft auch die Blacklist); bei ungültigem Token → 401 `{"detail": "Refresh token invalid."}`
- [ ] Neuen Access-Token mit `token.access_token` erzeugen und per `set_access_cookie` setzen
- [ ] 200 mit `{"detail": "Token refreshed"}`; der Token steht **nicht** im Body
- [ ] Keine Rotation (Entscheidung)

## Hinweis zur Access-Token-Gültigkeit
Access-Tokens sind zustandslos und bleiben nach dem Logout bis zu 5 Minuten gültig. Das ist bewusst akzeptiert, weil das Cookie gelöscht wird und die Lifetime kurz ist. Im README dokumentieren.

## Akzeptanzkriterien
- [ ] Logout → 200, beide Cookies gelöscht (`max-age=0`), Refresh-Token in `BlacklistedToken`
- [ ] Refresh mit einem geblacklisteten Token → 401
- [ ] Logout ohne Login → 401
- [ ] Refresh mit gültigem Cookie → 200, neues `access_token`-Cookie

## Tests
- `auth_app/tests/test_logout.py`, `auth_app/tests/test_refresh.py`: alle Akzeptanzkriterien, außerdem Refresh ohne Cookie und mit manipuliertem Cookie

## Commit-Message
`feat(auth): add logout with blacklist and cookie token refresh`
