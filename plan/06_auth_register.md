# 06 – Registrierung

## Ziel
`POST /api/register/` legt einen User an (US1).

## Referenzen
- `docs/Endpoint Dokumentation.pdf` – Register
- `quizly_frontend/shared/js/auth.js:40-53` – Formulardaten
- `quizly_frontend/shared/js/auth.js:101-125` – Aufruf und Fehleranzeige (`data.username`)

## Aufgaben
- [ ] `auth_app/api/serializers.py` – `RegistrationSerializer`:
  - Felder `username`, `email`, `password` (write_only), `confirmed_password` (write_only)
  - `validate_email`: eindeutig (case-insensitive) → `"Email already exists."`
  - Username-Eindeutigkeit über den Model-Validator
  - `validate`: `password == confirmed_password` → sonst ein Fehler unter `password`
  - Passwort zusätzlich mit `django.contrib.auth.password_validation.validate_password` prüfen
  - `create`: `User.objects.create_user(...)`
- [ ] `auth_app/api/views.py` – `RegistrationView(APIView)`:
  - `permission_classes = [AllowAny]`, `authentication_classes = []`
  - Bei Erfolg 201 mit `{"detail": "User created successfully!"}`, bei Fehlern 400 mit den Serializer-Fehlern
- [ ] `auth_app/api/urls.py`: `path("register/", RegistrationView.as_view())`

## Hinweise
- Das Frontend zeigt nur `data.username` an. Fehler bei Passwort oder E-Mail erscheinen dort als „undefined“. Das ist ein Frontend-Thema; das Backend bleibt doku-konform (400 mit Feldfehlern).
- Das Frontend validiert schon clientseitig (Username ≥ 3 Zeichen, Passwort ≥ 6 Zeichen mit Groß- und Kleinbuchstabe sowie Ziffer).

## Akzeptanzkriterien
- [ ] Gültige Daten → 201 mit dem exakten `detail`-Text, User in der DB, Passwort gehasht
- [ ] Doppelter Username oder doppelte E-Mail → 400
- [ ] Passwörter stimmen nicht überein → 400
- [ ] Es werden keine Cookies gesetzt

## Tests
- `auth_app/tests/test_register.py`: Erfolg, doppelter Username, doppelte E-Mail (auch in anderer Groß-/Kleinschreibung), Passwort-Mismatch, fehlende Felder

## Commit-Message
`feat(auth): add registration endpoint`
