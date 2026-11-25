"""Helpers for reading typed values from environment variables."""

import os

from django.core.exceptions import ImproperlyConfigured

TRUTHY_VALUES = {"true", "1", "yes", "on"}


def get_bool(name: str, default: bool) -> bool:
    """Return the environment variable ``name`` parsed as a boolean."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUTHY_VALUES


def get_list(name: str, default: list[str]) -> list[str]:
    """Return the environment variable ``name`` as a comma separated list."""
    value = os.getenv(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def get_int(name: str, default: int) -> int:
    """Return the environment variable ``name`` parsed as an integer."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        message = f"Environment variable {name} must be an integer."
        raise ImproperlyConfigured(message) from exc
