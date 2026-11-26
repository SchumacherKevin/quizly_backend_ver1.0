"""Tests for the YouTube service (no network access)."""

import pytest

from quiz_app.services.youtube import extract_video_id

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
