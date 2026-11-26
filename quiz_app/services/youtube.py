"""YouTube helpers: URL parsing, metadata and audio download."""

import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yt_dlp
from django.conf import settings

from quiz_app.services.exceptions import InvalidVideoError

WATCH_HOSTS = {"www.youtube.com", "youtube.com", "m.youtube.com"}
SHORT_HOSTS = {"youtu.be"}
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
WATCH_URL = "https://www.youtube.com/watch?v={video_id}"
INFO_OPTIONS = {"quiet": True, "noplaylist": True}
AUDIO_TEMPLATE = "audio.%(ext)s"
LOAD_ERROR = "Video could not be loaded."


def _query_id(parsed):
    """Read the id from the ``v`` query parameter of a watch URL.

    Args:
        parsed: Result of ``urlparse`` for the URL.

    Returns:
        The value of ``v``, or an empty string if it is missing.
    """
    return parse_qs(parsed.query).get("v", [""])[0]


def _path_id(parsed):
    """Read the id from the last path segment (youtu.be or shorts).

    Args:
        parsed: Result of ``urlparse`` for the URL.

    Returns:
        The last path segment.
    """
    return parsed.path.rstrip("/").split("/")[-1]


def _raw_id(parsed):
    """Find the id candidate depending on host and path.

    Args:
        parsed: Result of ``urlparse`` for the URL.

    Returns:
        The unvalidated id candidate, or an empty string for hosts that
        are not YouTube.
    """
    if parsed.hostname in SHORT_HOSTS:
        return _path_id(parsed)
    if parsed.hostname not in WATCH_HOSTS:
        return ""
    if parsed.path.startswith("/shorts/"):
        return _path_id(parsed)
    return _query_id(parsed)


def extract_video_id(url: str) -> str:
    """Extract the video id from a supported YouTube URL.

    Args:
        url: URL in ``watch?v=``, ``youtu.be/``, ``shorts/`` or mobile
            format.

    Returns:
        The 11 character video id.

    Raises:
        InvalidVideoError: For foreign hosts or malformed ids.
    """
    video_id = _raw_id(urlparse(url))
    if not VIDEO_ID_PATTERN.match(video_id):
        raise InvalidVideoError("Invalid YouTube URL.")
    return video_id


def normalize_url(video_id: str) -> str:
    """Build the canonical watch URL the frontend can embed.

    Args:
        video_id: The 11 character video id.

    Returns:
        ``https://www.youtube.com/watch?v=<video_id>``.
    """
    return WATCH_URL.format(video_id=video_id)


def fetch_video_info(url: str) -> dict:
    """Load the video metadata without downloading anything.

    Args:
        url: Normalized YouTube watch URL.

    Returns:
        The yt-dlp info dict (e.g. ``title`` and ``duration``).

    Raises:
        InvalidVideoError: If yt-dlp cannot load the video.
    """
    try:
        with yt_dlp.YoutubeDL(INFO_OPTIONS) as ydl:
            return ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as error:
        raise InvalidVideoError(LOAD_ERROR) from error


def check_duration(info: dict) -> None:
    """Ensure the video is not longer than ``MAX_VIDEO_MINUTES``.

    Args:
        info: The yt-dlp info dict of the video.

    Raises:
        InvalidVideoError: If the duration is missing (e.g. livestreams)
            or above the limit.
    """
    duration = info.get("duration")
    if not duration:
        raise InvalidVideoError("Video duration is unknown.")
    limit = settings.MAX_VIDEO_MINUTES
    if duration > limit * 60:
        raise InvalidVideoError(f"Video is longer than {limit} minutes.")


def build_download_options(target_dir) -> dict:
    """Build the yt-dlp options for an audio download.

    Args:
        target_dir: Folder the audio file is written to.

    Returns:
        The options dict for ``yt_dlp.YoutubeDL``.
    """
    return {
        "format": "bestaudio/best",
        "outtmpl": str(Path(target_dir) / AUDIO_TEMPLATE),
        "quiet": True,
        "noplaylist": True,
    }


def download_audio(url: str, target_dir) -> Path:
    """Download the audio track of a video.

    Args:
        url: Normalized YouTube watch URL.
        target_dir: Folder the audio file is written to.

    Returns:
        Path of the downloaded audio file.

    Raises:
        InvalidVideoError: If yt-dlp cannot load the video.
    """
    try:
        with yt_dlp.YoutubeDL(build_download_options(target_dir)) as ydl:
            info = ydl.extract_info(url, download=True)
            return Path(ydl.prepare_filename(info))
    except yt_dlp.utils.DownloadError as error:
        raise InvalidVideoError(LOAD_ERROR) from error
