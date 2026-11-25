# 04 – Tooling und Code-Qualität

## Ziel
PEP8-Konformität wird automatisch gesichert, die Testinfrastruktur steht, und die Regeln aus der Checkliste sind dokumentiert.

## Referenzen
- `docs/Quizly Checkliste.pdf` – Clean Code, Dokumentation, Django-Regeln, PEP8

## Aufgaben
- [ ] `pyproject.toml`:
  - `[tool.black]` `line-length = 79` (PEP8-konform), Ausschluss `migrations`, `.venv`
  - `[tool.isort]` `profile = "black"`, `line_length = 79`
  - `[tool.pytest.ini_options]` `DJANGO_SETTINGS_MODULE = "core.settings"`, `python_files = ["test_*.py"]`, `addopts = "--cov --cov-report=term-missing"`
  - `[tool.coverage.run]` `source = ["auth_app", "quiz_app", "core"]`, `omit = ["*/migrations/*", "*/tests/*", "manage.py", "core/asgi.py", "core/wsgi.py"]`
- [ ] `setup.cfg` mit `[flake8]`: `max-line-length = 79`, `extend-ignore = E203, W503`, `exclude = .venv, migrations, __pycache__`
- [ ] `conftest.py` im Root mit gemeinsamen Fixtures: `api_client`, `user`, `other_user`, `auth_client` (eingeloggt über Cookies)
- [ ] Optional: `.pre-commit-config.yaml` mit black, isort und flake8

## Definition of Done (gilt für jeden Schritt)
- [ ] Funktionen und Methoden haben **höchstens 14 Zeilen** und genau eine Aufgabe
- [ ] Namen in `snake_case`, Klassen in `PascalCase`, Variablennamen sprechend
- [ ] Keine ungenutzten Variablen, Funktionen oder Imports und kein auskommentierter Code
- [ ] Jede Klasse und Funktion hat einen Docstring
- [ ] `views.py` enthält **nur Views, die eine Response zurückgeben**; Logik liegt in `utils.py` oder `services/`
- [ ] `black --check .`, `isort --check .` und `flake8` sind fehlerfrei
- [ ] Die Tests laufen grün

## Akzeptanzkriterien
- [ ] `pytest` läuft (auch ohne Tests) und gibt einen Coverage-Report aus
- [ ] `flake8` liefert für das Startprojekt 0 Meldungen

## Commit-Message
`chore: add black, isort, flake8 and pytest configuration`
