# 08 – Login

## Ziel
`POST /api/login/` prüft die Zugangsdaten und setzt `access_token` und `refresh_token` als HttpOnly-Cookies (US2).

## Referenzen
- `docs/Endpoint Dokumentation.pdf` – Login
- `quizly_frontend/shared/js/auth.js:65-89` – zeigt bei Fehlern `responseData.detail`

## Aufgaben
- [ ] `auth_app/api/serializers.py` – `LoginSerializer`:
  - Felder `username`, `password`
  - `validate`: `authenticate(username=..., password=...)`; bei Fehlschlag `AuthenticationFailed("Invalid username or password.")` (allgemein formuliert)
- [ ] `auth_app/api/views.py` – `LoginView(APIView)`:
  - `permission_classes = [AllowAny]`, `authentication_classes = []`
  - `RefreshToken.for_user(user)` erzeugt die Tokens; Cookies über die Helper aus 07 setzen
  - Response 200:
    ```json
    {"detail": "Login successfully!", "user": {"id": 1, "username": "...", "email": "..."}}
    ```
- [ ] URL `login/`

## Akzeptanzkriterien
- [ ] Richtige Zugangsdaten → 200, beide Cookies HttpOnly, Body wie in der Doku
- [ ] Falsche Zugangsdaten oder unbekannter User → **401** mit `{"detail": ...}`, dieselbe Meldung in beiden Fällen
- [ ] Fehlende Felder → 400
- [ ] Die Tokens stehen nicht im Body

## Tests
- `auth_app/tests/test_login.py`: Erfolg (Cookies und Flags prüfen), falsches Passwort, unbekannter User, fehlende Felder

## Commit-Message
`feat(auth): add login endpoint setting JWT cookies`
