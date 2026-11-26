"""Tests for the YouTube service (no network access)."""

import pytest

from quiz_app.services.exceptions import InvalidVideoError
from quiz_app.services.youtube import extract_video_id, normalize_url

VIDEO_ID = "dQw4w9WgXcQ"


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
