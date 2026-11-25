"""Tests for the environment variable helpers in core.env."""

import pytest
from django.core.exceptions import ImproperlyConfigured

from core.env import get_bool, get_int, get_list


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


@pytest.mark.parametrize(
    ("value", "expected"),
    [("a, b ,c", ["a", "b", "c"]), ("", []), ("single", ["single"])],
)
def test_get_list_splits_and_strips(monkeypatch, value, expected):
    """Comma separated values are split and stripped."""
    monkeypatch.setenv("ITEMS", value)

    assert get_list("ITEMS", ["default"]) == expected


def test_get_list_returns_default_when_missing(monkeypatch):
    """A missing variable falls back to the default list."""
    monkeypatch.delenv("ITEMS", raising=False)

    assert get_list("ITEMS", ["default"]) == ["default"]


def test_get_int_parses_value(monkeypatch):
    """A numeric string is parsed to an integer."""
    monkeypatch.setenv("NUMBER", "15")

    assert get_int("NUMBER", 1) == 15


def test_get_int_returns_default_when_missing(monkeypatch):
    """A missing variable falls back to the default integer."""
    monkeypatch.delenv("NUMBER", raising=False)

    assert get_int("NUMBER", 7) == 7


def test_get_int_raises_on_invalid(monkeypatch):
    """A non numeric value raises a configuration error."""
    monkeypatch.setenv("NUMBER", "abc")

    with pytest.raises(ImproperlyConfigured):
        get_int("NUMBER", 1)
