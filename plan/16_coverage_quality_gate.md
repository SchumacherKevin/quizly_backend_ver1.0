# 16 – Coverage- und Quality-Gate

## Ziel
Gesamtabnahme der Codequalität: Coverage ≥ 90 %, alle DoD-Regeln der Checkliste erfüllt, keine Lücken im API-Vertrag.
Die Tests sind durch TDD schon entstanden. Hier werden nur **Lücken gefunden und geschlossen**.

## Kontext (eigenständig)
- **Vorbedingungen:** 02–15 sind fertig; alle Endpoints und Services sind implementiert und getestet.
- Werkzeuge: `pytest --cov` (Konfiguration in `pyproject.toml`), `black`, `isort`, `flake8`
- **DoD-Regeln (Checkliste):**
  - Funktionen ≤ 14 Zeilen (ohne Docstring) und eine Aufgabe
  - `snake_case`, sprechende Namen
  - keine ungenutzten Variablen, Funktionen oder Imports und kein auskommentierter Code
  - Docstrings im Google-Format (`Args:`, `Returns:`, `Raises:`), Vorgabe von Kevin am 26.11.2026
  - `views.py` nur Views mit Response
  - Helper in `utils.py` bzw. `services/`
  - PEP8
- **Endpoints und erwartete Statuscodes** (aus `01_api_contract.md`):
  | Endpoint | Codes |
  |---|---|
  | POST register/ | 201, 400 |
  | POST login/ | 200, 400, 401 |
  | POST logout/ | 200, 401 |
  | POST token/refresh/ | 200, 401 |
  | POST quizzes/ | 201, 400, 401, 500 |
  | GET quizzes/ | 200, 401 |
  | GET quizzes/{id}/ | 200, 401, 403, 404 |
  | PATCH quizzes/{id}/ | 200, 400, 401, 403, 404 |
  | DELETE quizzes/{id}/ | 204, 401, 403, 404 |

## Zyklen

### Zyklus 1: Coverage-Analyse
- **Aufgabe:** `pytest --cov-report=term-missing --cov-report=html` ausführen und die fehlenden Zeilen pro Datei notieren
- **Für jede Lücke** einen Mini-Zyklus durchführen: Test schreiben, der die Lücke abdeckt → grün → Commit `test(<scope>): cover <verhalten>`
- Nicht testbarer oder toter Code wird **entfernt** statt ausgenommen (`refactor: remove unused ...`)
- [x] Coverage ≥ 90 % (Ergebnis 26.11.2026: 502 Statements, 0 fehlend, **100 %**; zusätzlich mit `--cov-branch`: 58 Branches, 0 teilweise, ebenfalls 100 %. Keine Lücken, deshalb keine Mini-Zyklen. Ausgenommen sind nur `migrations`, `tests`, `manage.py`, `asgi.py` und `wsgi.py`, also generierter Einstiegscode ohne Logik)

### Zyklus 2: Abgleich mit dem API-Vertrag
- **Aufgabe:** Für jede Zeile der Tabelle oben per `grep` den passenden Test suchen (z. B. `status_code == 403` in `quiz_app/tests/`)
- Fehlt ein Code, gibt es einen Mini-Zyklus mit Test und Commit
- [x] Jeder Statuscode ist durch mindestens einen Test abgedeckt (26.11.2026: alle 9 Endpoints vollständig, zusätzlich 405 für PUT. Auch die vier `detail`-Texte aus dem Vertrag werden wortgleich geprüft; der über zwei Zeilen umbrochene Logout-Text wurde per Vergleich verifiziert. Keine Mini-Zyklen nötig)

### Zyklus 3: Funktionslänge und Docstrings
- **Aufgabe:** Ein Skript im Scratchpad (**nicht** ins Repo) mit `ast` zählt die Zeilen jeder Funktion **ohne Docstring** in `core`, `auth_app` und `quiz_app` (ohne `migrations` und `tests`). Es listet alle Funktionen mit mehr als 14 Zeilen und alle ohne Google-Docstring: Fehlt `Args:` bei Parametern (außer `self`/`cls`), `Returns:` bei Rückgabewert oder `Raises:` bei eigenem `raise`? Außerdem prüft es Modul- und Klassen-Docstrings.
- Jeden Fund refaktorieren; die Tests müssen grün bleiben. Commit: `refactor(<scope>): split <funktion>` bzw. `docs(<scope>): add missing docstrings`
- [x] 0 Funde (Erstlauf: 0 Funde bei der Länge, 126 beim Format, verteilt auf ca. 60 Funktionen, 6 leere `__init__.py` und 2 `apps.py`. Alle auf das Google-Format umgestellt; per AST-Vergleich gegen HEAD verifiziert, dass sich nur Docstrings geändert haben. Tests bleiben ein einzeiliger Docstring, weil Fixtures als Parameter kein `Args:` brauchen)

### Zyklus 4: Struktur-Review
- [x] `views.py` enthält nur Views (keine Helper-Funktionen): in beiden `views.py` nur Klassen, keine Funktionen auf Modulebene
- [x] Kein auskommentierter Code (`grep -rn "^\s*# .*(" --include=*.py` stichprobenartig prüfen): alle `#`-Zeilen geprüft, nur Abschnittsüberschriften und Doku-Links in `core/settings.py`
- [x] Keine Secrets im Repo (`git grep -i "api_key\s*="` liefert nur Settings und Env): Treffer nur in Settings (`os.getenv`), `.env.template` (Platzhalter) und Tests (Fake-Key). Zusätzlich die gesamte Git-History geprüft: weder der echte Gemini-Key noch der `SECRET_KEY` sind enthalten, `.env` und die DB sind nicht getrackt
- [x] `python manage.py makemigrations --check` ist sauber („No changes detected“)
- Commit je Korrektur (keine Korrektur nötig)

## Abschluss-Check
- [x] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün, Coverage ≥ 90 % (170 passed, 100 %)
- [x] Status von Schritt 16 auf `[x]` gesetzt (Commit `docs: mark step 16 done`)
- [x] Stopp → Review
