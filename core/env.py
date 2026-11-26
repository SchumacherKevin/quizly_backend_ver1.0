"""Helpers for reading typed values from environment variables."""

import os

from django.core.exceptions import ImproperlyConfigured

TRUTHY_VALUES = {"true", "1", "yes", "on"}


def get_bool(name: str, default: bool) -> bool:
    """Read an environment variable as a boolean.

    Args:
        name: Name of the environment variable.
        default: Value used if the variable is not set.

    Returns:
        True for "true", "1", "yes" or "on" (case-insensitive), False for
        any other value, or ``default`` if the variable is not set.
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUTHY_VALUES


def get_list(name: str, default: list[str]) -> list[str]:
    """Read an environment variable as a comma separated list.

    Args:
        name: Name of the environment variable.
        default: Value used if the variable is not set.

    Returns:
        The stripped, non-empty items, or ``default`` if the variable is
        not set.
    """
    value = os.getenv(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def get_int(name: str, default: int) -> int:
    """Read an environment variable as an integer.

    Args:
        name: Name of the environment variable.
        default: Value used if the variable is not set.

    Returns:
        The parsed integer, or ``default`` if the variable is not set.

    Raises:
        ImproperlyConfigured: If the value is not a valid integer.
    """
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        message = f"Environment variable {name} must be an integer."
        raise ImproperlyConfigured(message) from exc
