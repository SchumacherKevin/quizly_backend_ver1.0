"""Tests for the YouTube service (no network access)."""

from unittest.mock import patch

import pytest
import yt_dlp

from quiz_app.services.exceptions import InvalidVideoError
from quiz_app.services.youtube import (
    extract_video_id,
    fetch_video_info,
    normalize_url,
)

VIDEO_ID = "dQw4w9WgXcQ"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"
YDL_PATH = "quiz_app.services.youtube.yt_dlp.YoutubeDL"


@pytest.mark.parametrize(
    "url",
    [
        f"https://www.youtube.com/watch?v={VIDEO_ID}",
        f"https://www.youtube.com/watch?v={VIDEO_ID}&t=42s",
        f"https://m.youtube.com/watch?v={VIDEO_ID}",
        f"https://youtube.com/watch?v={VIDEO_ID}",
        f"https://youtu.be/{VIDEO_ID}",
        f"https://www.youtube.com/shorts/{VIDEO_ID}",
    ],
)
def test_extract_video_id_from_supported_urls(url):
    """All supported URL formats yield the plain video id."""
    assert extract_video_id(url) == VIDEO_ID


@pytest.mark.parametrize(
    "url",
    [
        "https://vimeo.com/123",
        "https://www.youtube.com/watch",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/playlist?list=PL123",
        "not a url",
        "",
        f"https://evil.com/watch?v={VIDEO_ID}",
        f"https://evil.com/shorts/{VIDEO_ID}",
    ],
)
def test_extract_video_id_rejects_invalid_urls(url):
    """Foreign hosts and malformed ids raise ``InvalidVideoError``."""
    with pytest.raises(InvalidVideoError):
        extract_video_id(url)


def test_normalize_url():
    """A video id is turned into the embeddable watch URL."""
    assert normalize_url(VIDEO_ID) == (
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )


@pytest.fixture
def ydl_cls():
    """Patch ``YoutubeDL`` so no test ever touches the network."""
    with patch(YDL_PATH) as mock_cls:
        yield mock_cls


def _ydl(ydl_cls):
    """Return the instance yielded by ``with YoutubeDL(...) as ydl``."""
    return ydl_cls.return_value.__enter__.return_value


def test_fetch_video_info_returns_info_without_download(ydl_cls):
    """Metadata is fetched via ``extract_info`` without downloading."""
    _ydl(ydl_cls).extract_info.return_value = {"title": "T", "duration": 120}

    info = fetch_video_info(VIDEO_URL)

    assert info == {"title": "T", "duration": 120}
    _ydl(ydl_cls).extract_info.assert_called_once_with(
        VIDEO_URL, download=False
    )


def test_fetch_video_info_raises_invalid_video_on_download_error(ydl_cls):
    """A yt-dlp ``DownloadError`` becomes ``InvalidVideoError``."""
    error = yt_dlp.utils.DownloadError("x")
    _ydl(ydl_cls).extract_info.side_effect = error

    with pytest.raises(InvalidVideoError):
        fetch_video_info(VIDEO_URL)
