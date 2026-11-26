# 11 – YouTube-Service (URL, Metadaten, Audio-Download)

## Ziel
`quiz_app/services/youtube.py` validiert und normalisiert YouTube-URLs, prüft die Videolänge und lädt das Audio in ein übergebenes Verzeichnis.

## Kontext (eigenständig)
- **Vorbedingungen:** 02–10 sind fertig. `yt-dlp` ist installiert, `settings.MAX_VIDEO_MINUTES` existiert (int, Default 15).
- Betroffene Dateien: `quiz_app/services/exceptions.py` (neu), `quiz_app/services/youtube.py` (neu), `quiz_app/tests/test_youtube.py`
- **Exceptions** (`exceptions.py`):
  - `class QuizlyServiceError(Exception)` als Basis
  - `class InvalidVideoError(QuizlyServiceError)` → wird später zu 400
  - `class QuizGenerationError(QuizlyServiceError)` → wird später zu 500
- **Unterstützte URL-Formate** (Entscheidung): `https://www.youtube.com/watch?v=<ID>` (auch mit weiteren Parametern), `https://m.youtube.com/watch?v=<ID>`, `https://youtube.com/watch?v=<ID>`, `https://youtu.be/<ID>`, `https://www.youtube.com/shorts/<ID>`
- Eine gültige ID entspricht `^[A-Za-z0-9_-]{11}$`; zum Testen: `dQw4w9WgXcQ`
- Normalisierte Form: `https://www.youtube.com/watch?v=<ID>` (nur dieses Format kann das Frontend einbetten, `quizoverview.js:85`)
- **yt-dlp-Optionen** aus `docs/ydl_opts.txt`:
  ```python
  {"format": "bestaudio/best", "outtmpl": tmp_filename, "quiet": True, "noplaylist": True}
  ```
- **Tests ohne Netz:** `yt_dlp.YoutubeDL` wird gepatcht (`quiz_app.services.youtube.yt_dlp.YoutubeDL`). Weil `YoutubeDL` als Context Manager benutzt wird, gilt: `ydl = mock_cls.return_value.__enter__.return_value`.
- Das Temp-Verzeichnis selbst verwaltet die Pipeline (Schritt 14). Hier wird nur ein `target_dir` übergeben.

## Zyklen

### Zyklus 1: Video-ID aus gültigen URLs
- **Test:** `quiz_app/tests/test_youtube.py::test_extract_video_id_from_supported_urls` (parametrisiert, alle 5 Formate oben plus `watch?v=dQw4w9WgXcQ&t=42s`): Ergebnis ist immer `"dQw4w9WgXcQ"`
- **Erwartetes Rot:** `ModuleNotFoundError`
- **Green:**
  - `exceptions.py` anlegen
  - `extract_video_id(url: str) -> str` mit `urllib.parse.urlparse` und `parse_qs`
  - Host-Whitelist als Konstante
  - kleine Helper für „Query-ID“ und „Pfad-ID“
- **Commit:** `feat(quiz): extract video id from youtube urls`
- [x] erledigt (Fallback `return ""` für fremde Hosts ist noch ungetestet; ihn ersetzt Zyklus 2 durch `InvalidVideoError`)

### Zyklus 2: Ungültige URLs
- **Test:** `test_extract_video_id_rejects_invalid_urls` (parametrisiert), jeweils `pytest.raises(InvalidVideoError)`:
  - `"https://vimeo.com/123"`
  - `"https://www.youtube.com/watch"`
  - `"https://www.youtube.com/watch?v=short"`
  - `"https://www.youtube.com/playlist?list=PL123"`
  - `"not a url"`
  - `""`
  - `"https://evil.com/watch?v=dQw4w9WgXcQ"`
- **Erwartetes Rot:** falsche Rückgabe oder eine andere Exception
- **Green:** ID per Regex prüfen; sonst `raise InvalidVideoError("Invalid YouTube URL.")`
- **Commit:** `feat(quiz): reject non youtube or malformed urls`
- [x] erledigt (Abweichung: zusätzlicher Fall `https://evil.com/shorts/<ID>`, denn `/shorts/` wurde in Zyklus 1 auf jedem Host akzeptiert; die Shorts-Prüfung läuft jetzt erst nach der Host-Whitelist)

### Zyklus 3: URL normalisieren
- **Test:** `test_normalize_url`: `normalize_url("dQw4w9WgXcQ") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"`
- **Erwartetes Rot:** `ImportError`
- **Green:** `normalize_url(video_id: str) -> str`
- **Commit:** `feat(quiz): normalize youtube urls to watch format`
- [x] erledigt

### Zyklus 4: Metadaten laden
- **Test:** `test_fetch_video_info_returns_info_without_download`: Der Mock liefert `{"title": "T", "duration": 120}`; die Funktion gibt dieses Dict zurück, und `extract_info` wurde mit `(url, download=False)` aufgerufen
- **Test:** `test_fetch_video_info_raises_invalid_video_on_download_error`: `extract_info.side_effect = yt_dlp.utils.DownloadError("x")` führt zu `InvalidVideoError`
- **Erwartetes Rot:** `ImportError`
- **Green:** `fetch_video_info(url: str) -> dict` mit `YoutubeDL({"quiet": True, "noplaylist": True})`
- **Commit:** `feat(quiz): fetch youtube video metadata`
- [ ] erledigt

### Zyklus 5: Videolänge prüfen
- **Test:** `test_check_duration_accepts_short_video`: `settings.MAX_VIDEO_MINUTES = 15` (Fixture `settings`) und `{"duration": 900}` ergeben keinen Fehler
- **Test:** `test_check_duration_rejects_long_video`: `{"duration": 901}` führt zu `InvalidVideoError`, und die Meldung enthält `"15"`
- **Test:** `test_check_duration_rejects_missing_duration`: `{}` (z. B. Livestream) führt zu `InvalidVideoError`
- **Erwartetes Rot:** `ImportError`
- **Green:** `check_duration(info: dict) -> None`
- **Commit:** `feat(quiz): limit maximum video duration`
- [ ] erledigt

### Zyklus 6: Audio herunterladen
- **Test:** `test_download_audio_uses_expected_options` (mit `tmp_path`)
  - Arrange: `ydl.extract_info.return_value = {"id": "x"}`, `ydl.prepare_filename.return_value = str(tmp_path / "audio.webm")`
  - Act: `path = download_audio(url, tmp_path)`
  - Assert: Die an `YoutubeDL(...)` übergebenen Optionen enthalten `format == "bestaudio/best"`, `quiet is True` und `noplaylist is True`; `outtmpl` beginnt mit `str(tmp_path)`; `path == tmp_path / "audio.webm"`
- **Test:** `test_download_audio_raises_invalid_video_on_error`: `DownloadError` führt zu `InvalidVideoError`
- **Erwartetes Rot:** `ImportError`
- **Green:** `build_download_options(target_dir) -> dict` und `download_audio(url, target_dir) -> Path` mit `extract_info(url, download=True)` und `prepare_filename(info)`
- **Commit:** `feat(quiz): download youtube audio with yt-dlp`
- [ ] erledigt

## Abschluss-Check
- [ ] Kein Test greift auf das Netz zu (z. B. ohne Internet ausführen bzw. jeden Test auf den Patch prüfen)
- [ ] `black --check . ; isort --check-only . ; flake8 ; pytest` sind alle grün
- [ ] Status von Schritt 11 auf `[x]` gesetzt (Commit `docs: mark step 11 done`)
- [ ] Stopp → Review
