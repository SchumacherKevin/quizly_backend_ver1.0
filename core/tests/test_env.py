"""Tests for the environment variable helpers in core.env."""

import pytest

from core.env import get_bool


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("True", True),
        ("true", True),
        ("1", True),
        ("yes", True),
        ("False", False),
        ("0", False),
        ("no", False),
    ],
)
def test_get_bool(monkeypatch, value, expected):
    """Common truthy and falsy strings are parsed to booleans."""
    monkeypatch.setenv("FLAG", value)

    assert get_bool("FLAG", default=False) is expected


def test_get_bool_returns_default_when_missing(monkeypatch):
    """A missing variable falls back to the default."""
    monkeypatch.delenv("FLAG", raising=False)

    assert get_bool("FLAG", True) is True
