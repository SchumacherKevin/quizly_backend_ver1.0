# 03 – Tooling, pytest und Code-Qualität

## Ziel
pytest mit Coverage läuft, black/isort/flake8 sichern PEP8 automatisch, und die Basis-Fixtures stehen bereit. Ab hier wird jeder Schritt per TDD umgesetzt.

## Kontext (eigenständig)
- **Vorbedingungen:** Schritt 02 ist fertig (Django-Projekt `core`, Apps `auth_app` und `quiz_app` mit `tests/`-Paketen, `.venv` mit Dev-Abhängigkeiten).
- Betroffene Dateien: `pyproject.toml`, `setup.cfg`, `conftest.py`, `core/tests/test_smoke.py`
- **Definition of Done aus der Checkliste** (gilt ab jetzt in jedem Zyklus):
  - Funktionen und Methoden haben **höchstens 14 Zeilen** und genau eine Aufgabe
  - `snake_case` für Funktionen und Variablen, `PascalCase` für Klassen, sprechende Namen
  - keine ungenutzten Variablen, Funktionen oder Imports und kein auskommentierter Code
  - Docstrings für Module, Klassen und Funktionen
  - `views.py` enthält nur Views, die eine Response zurückgeben; Logik liegt in `utils.py` oder `services/`
  - PEP8-konform

## Zyklen

### Zyklus 1: pytest läuft gegen Django
- **Test:** `core/tests/test_smoke.py::test_settings_module_is_core`
  - Arrange: –
  - Act: `from django.conf import settings`
  - Assert: `settings.ROOT_URLCONF == "core.urls"`
- **Test:** `core/tests/test_smoke.py::test_admin_login_page_is_reachable`
  - Act: `client.get("/admin/login/")` (pytest-django-Fixture `client`, mit `django_db`)
  - Assert: `status_code == 200`
- **Erwartetes Rot:** `ImproperlyConfigured` bzw. „settings are not configured“, weil die pytest-Konfiguration fehlt.
- **Green:** `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  DJANGO_SETTINGS_MODULE = "core.settings"
  python_files = ["test_*.py"]
  addopts = "--cov --cov-report=term-missing"

  [tool.coverage.run]
  source = ["core", "auth_app", "quiz_app"]
  omit = ["*/migrations/*", "*/tests/*", "manage.py", "core/asgi.py", "core/wsgi.py"]
  ```
- **Commit:** `test(core): configure pytest-django with coverage and add smoke tests`
- [ ] erledigt

### Zyklus 2: Formatter und Linter
- **Aufgaben:**
  - `pyproject.toml` ergänzen:
    ```toml
    [tool.black]
    line-length = 79
    extend-exclude = "migrations"

    [tool.isort]
    profile = "black"
    line_length = 79
    skip = [".venv", "migrations"]
    ```
  - `setup.cfg`:
    ```ini
    [flake8]
    max-line-length = 79
    extend-ignore = E203, W503
    exclude = .venv, */migrations/*, __pycache__
    ```
  - Einmal `black . ; isort .` ausführen (formatiert den Django-Startcode)
- **Verifikation:** `black --check . ; isort --check-only . ; flake8` liefern 0 Meldungen, und `pytest` ist grün.
- **Hinweis:** Die Regel „Funktionen ≤ 14 Zeilen“ prüft flake8 nicht. Sie wird im Refactor-Schritt jedes Zyklus manuell geprüft und in Schritt 16 noch einmal geprüft.
- **Commit:** `chore: configure black, isort and flake8 for pep8`
- [ ] erledigt

### Zyklus 3: Basis-Fixtures
- **Test:** `core/tests/test_fixtures.py::test_user_fixture_has_hashed_password`
  - Arrange: Fixture `user`
  - Assert: `user.username == "testuser"`, `user.email == "test@example.com"`, `user.check_password("Test1234!") is True`, `user.password != "Test1234!"`
- **Test:** `core/tests/test_fixtures.py::test_other_user_differs_from_user`
  - Assert: `other_user.pk != user.pk` und `other_user.username == "otheruser"`
- **Test:** `core/tests/test_fixtures.py::test_api_client_is_drf_client`
  - Assert: `isinstance(api_client, APIClient)`
- **Erwartetes Rot:** `fixture 'user' not found`
- **Green:** `conftest.py` im Projektroot:
  - `api_client()` gibt `APIClient()` zurück
  - `user(db)` gibt `User.objects.create_user("testuser", "test@example.com", "Test1234!")` zurück
  - `other_user(db)` analog mit `otheruser` / `other@example.com`
  - Docstrings für jede Fixture
- **Commit:** `test: add shared api_client and user fixtures`
- [ ] erledigt

## Abschluss-Check
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Status von Schritt 03 in `00_overview.md` auf `[x]` gesetzt (Commit `docs: mark step 03 done`)
- [ ] Stopp → Review → `git merge --ff-only step/03-tooling`
