"""YouTube helpers: URL parsing, metadata and audio download."""

from urllib.parse import parse_qs, urlparse

WATCH_HOSTS = {"www.youtube.com", "youtube.com", "m.youtube.com"}
SHORT_HOSTS = {"youtu.be"}


def _query_id(parsed):
    """Return the ``v`` query parameter of a watch URL."""
    return parse_qs(parsed.query).get("v", [""])[0]


def _path_id(parsed):
    """Return the last path segment of a short or shorts URL."""
    return parsed.path.rstrip("/").split("/")[-1]


def extract_video_id(url: str) -> str:
    """Return the video id of a supported YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in SHORT_HOSTS or parsed.path.startswith("/shorts/"):
        return _path_id(parsed)
    if parsed.hostname in WATCH_HOSTS:
        return _query_id(parsed)
    return ""
