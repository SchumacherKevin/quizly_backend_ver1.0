# 11 – YouTube-URL und Audio-Download

## Ziel
Eine YouTube-URL wird validiert und normalisiert, die Videolänge geprüft und das Audio in ein temporäres Verzeichnis geladen.

## Referenzen
- `docs/ydl_opts.txt` – Optionen
- `docs/Quizly Checkliste.pdf` – „nur YouTube Videos“, yt_dlp
- `quizly_frontend/shared/js/quizoverview.js:85` – Embed braucht `v=<ID>`

## Aufgaben
- [ ] `quiz_app/services/exceptions.py`:
  - `InvalidVideoError` → wird zu 400
  - `QuizGenerationError` → wird zu 500
- [ ] `quiz_app/services/youtube.py`:
  - `extract_video_id(url) -> str`: unterstützt `youtube.com/watch?v=`, `m.youtube.com/watch?v=`, `youtu.be/<id>`, `youtube.com/shorts/<id>`; Parsing mit `urllib.parse` und einer Host-Whitelist; die ID muss `^[A-Za-z0-9_-]{11}$` entsprechen; sonst `InvalidVideoError`
  - `normalize_url(video_id) -> str`: gibt `https://www.youtube.com/watch?v=<id>` zurück
  - `fetch_video_info(url) -> dict`: `extract_info(url, download=False)`; bei `DownloadError` → `InvalidVideoError`
  - `check_duration(info)`: `duration > MAX_VIDEO_MINUTES * 60` → `InvalidVideoError("Video is longer than X minutes.")`
  - `download_audio(url, target_dir) -> Path`: Optionen wie in `ydl_opts.txt`:
    ```python
    {"format": "bestaudio/best", "outtmpl": tmp_filename, "quiet": True, "noplaylist": True}
    ```
    `outtmpl` liegt im `tempfile.TemporaryDirectory()`, der Rückgabewert ist der tatsächliche Dateipfad
- [ ] Jede Funktion hat höchstens 14 Zeilen und einen Docstring

## Hinweise
- Den Titel des Videos aus `info["title"]` kann man Gemini als Kontext mitgeben.
- Cleanup: Das `TemporaryDirectory` wird im Pipeline-Orchestrator (14) als Context Manager verwendet, damit Dateien auch bei Fehlern gelöscht werden.
- yt-dlp muss aktuell gehalten werden; im README vermerken.

## Akzeptanzkriterien
- [ ] Alle vier URL-Formate ergeben dieselbe normalisierte URL
- [ ] Fremde Domains, fehlende oder ungültige IDs und Playlist-only-URLs → `InvalidVideoError`
- [ ] Zu lange Videos → `InvalidVideoError`, bevor heruntergeladen wird

## Tests
- `quiz_app/tests/test_youtube.py`: parametrisierte URL-Tests; `yt_dlp.YoutubeDL` wird gemockt (Info, `DownloadError`, Dauer) – **kein echter Netzwerkzugriff**

## Commit-Message
`feat(quiz): add YouTube URL validation and audio download service`
