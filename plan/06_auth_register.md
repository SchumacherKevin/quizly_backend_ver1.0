# 06 – Registrierung `POST /api/register/`

## Ziel
Neue User können sich registrieren (User Story 1).

## Kontext (eigenständig)
- **Vorbedingungen:** 02–05 sind fertig. `api/`-Includes in `core/urls.py` existieren, die Fixtures `api_client` und `user` (`testuser` / `test@example.com` / `Test1234!`) auch.
- Betroffene Dateien: `auth_app/api/serializers.py`, `auth_app/api/views.py`, `auth_app/api/urls.py`, `auth_app/tests/test_register.py`
- URL-Name: `register`
- **Vertrag:**
  - Request: `{"username", "password", "confirmed_password", "email"}`
  - 201: `{"detail": "User created successfully!"}`
  - 400: Serializer-Fehler pro Feld
- **Frontend-Besonderheiten** (`quizly_frontend/shared/js/auth.js:101-125`):
  - liest **immer** `response.json()`, deshalb braucht jede Antwort einen JSON-Body
  - zeigt bei Fehlern `data.username` an
  - sendet kein `credentials: "include"`
  - Nach der Registrierung erfolgt **kein** Login, also werden keine Cookies gesetzt
- Die E-Mail muss eindeutig sein (Groß-/Kleinschreibung egal), ebenso der Username.
- Die View ist öffentlich: `permission_classes = [AllowAny]`, `authentication_classes = []`.

## Zyklen

### Zyklus 1: Erfolgreiche Registrierung
- **Test:** `auth_app/tests/test_register.py::test_register_creates_user`
  - Arrange: `payload = {"username": "newuser", "email": "new@example.com", "password": "Test1234!", "confirmed_password": "Test1234!"}`
  - Act: `api_client.post(reverse("register"), payload, format="json")`
  - Assert: `status_code == 201`, `response.json() == {"detail": "User created successfully!"}`, `User.objects.filter(username="newuser").exists()`, `user.check_password("Test1234!")`
- **Erwartetes Rot:** `NoReverseMatch: 'register'`
- **Green:**
  - `RegistrationSerializer(ModelSerializer)` mit `username`, `email`, `password` (write_only), `confirmed_password` (write_only); `create` nutzt `User.objects.create_user`
  - `RegistrationView(APIView).post` gibt die Response zurück
  - URL `register/`
- **Commit:** `feat(auth): add registration endpoint`
- [x] erledigt

### Zyklus 2: Kein Login nach der Registrierung
- **Test:** `test_register_sets_no_cookies`: Bei Erfolg enthält `response.cookies` weder `access_token` noch `refresh_token`
- **Erwartetes Rot:** keins, der Test ist von Anfang an grün (Absicherungs-Test). Trotzdem einzeln committen.
- **Commit:** `test(auth): ensure registration does not log user in`
- [x] erledigt

### Zyklus 3: Doppelter Username
- **Test:** `test_register_rejects_duplicate_username`: Mit der Fixture `user` und Username `testuser` ergibt sich 400, und `"username" in response.json()`
- **Erwartetes Rot:** möglicherweise schon grün durch den Model-Validator. Dann gilt Zyklus 2 entsprechend: als Absicherung committen.
- **Commit:** `test(auth): reject duplicate username on registration`
- [x] erledigt (war sofort grün durch den Unique-Validator des User-Models)

### Zyklus 4: Doppelte E-Mail (Groß-/Kleinschreibung egal)
- **Test:** `test_register_rejects_duplicate_email` (parametrisiert: `test@example.com`, `TEST@Example.com`)
  - Assert: 400 und `response.json()["email"] == ["Email already exists."]`
- **Erwartetes Rot:** 201, weil die E-Mail bisher nicht geprüft wird
- **Green:** `validate_email` mit `User.objects.filter(email__iexact=value).exists()`; die E-Mail ist Pflichtfeld (`required=True`)
- **Commit:** `feat(auth): enforce unique email on registration`
- [x] erledigt

### Zyklus 5: Passwörter stimmen nicht überein
- **Test:** `test_register_rejects_password_mismatch`: `confirmed_password="Other1234!"` ergibt 400 und `response.json()["password"] == ["Passwords do not match."]`; es wird kein User angelegt
- **Erwartetes Rot:** 201
- **Green:** `validate(self, attrs)` vergleicht beide Felder und entfernt `confirmed_password` vor `create`
- **Commit:** `feat(auth): validate password confirmation`
- [x] erledigt

### Zyklus 6: Passwortstärke und Pflichtfelder
- **Test:** `test_register_rejects_weak_password`: `"123"` als Passwort und Bestätigung ergibt 400 mit dem Key `"password"`
- **Test:** `test_register_requires_all_fields` (parametrisiert, jeweils ein Feld weglassen): 400, das fehlende Feld steht im Body, und die Antwort ist gültiges JSON
- **Erwartetes Rot:** schwaches Passwort ergibt 201
- **Green:** `django.contrib.auth.password_validation.validate_password` in `validate_password` des Serializers
- **Commit:** `feat(auth): validate password strength and required fields`
- [ ] erledigt

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Die View enthält nur die Response-Logik
- [ ] Status von Schritt 06 auf `[x]` gesetzt (Commit `docs: mark step 06 done`)
- [ ] Stopp → Review
