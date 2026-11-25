"""Helpers for reading typed values from environment variables."""

import os

TRUTHY_VALUES = {"true", "1", "yes", "on"}


def get_bool(name: str, default: bool) -> bool:
    """Return the environment variable ``name`` parsed as a boolean."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUTHY_VALUES
