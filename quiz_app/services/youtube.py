"""YouTube helpers: URL parsing, metadata and audio download."""

import re
from urllib.parse import parse_qs, urlparse

import yt_dlp

from quiz_app.services.exceptions import InvalidVideoError

WATCH_HOSTS = {"www.youtube.com", "youtube.com", "m.youtube.com"}
SHORT_HOSTS = {"youtu.be"}
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
WATCH_URL = "https://www.youtube.com/watch?v={video_id}"
INFO_OPTIONS = {"quiet": True, "noplaylist": True}


def _query_id(parsed):
    """Return the ``v`` query parameter of a watch URL."""
    return parse_qs(parsed.query).get("v", [""])[0]


def _path_id(parsed):
    """Return the last path segment of a short or shorts URL."""
    return parsed.path.rstrip("/").split("/")[-1]


def _raw_id(parsed):
    """Return the unvalidated id candidate, or '' for foreign hosts."""
    if parsed.hostname in SHORT_HOSTS:
        return _path_id(parsed)
    if parsed.hostname not in WATCH_HOSTS:
        return ""
    if parsed.path.startswith("/shorts/"):
        return _path_id(parsed)
    return _query_id(parsed)


def extract_video_id(url: str) -> str:
    """Return the video id of a supported YouTube URL.

    Raises ``InvalidVideoError`` for foreign hosts or malformed ids.
    """
    video_id = _raw_id(urlparse(url))
    if not VIDEO_ID_PATTERN.match(video_id):
        raise InvalidVideoError("Invalid YouTube URL.")
    return video_id


def normalize_url(video_id: str) -> str:
    """Return the canonical watch URL the frontend can embed."""
    return WATCH_URL.format(video_id=video_id)


def fetch_video_info(url: str) -> dict:
    """Return the video metadata without downloading anything.

    Raises ``InvalidVideoError`` if yt-dlp cannot load the video.
    """
    try:
        with yt_dlp.YoutubeDL(INFO_OPTIONS) as ydl:
            return ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as error:
        raise InvalidVideoError("Video could not be loaded.") from error
