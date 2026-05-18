"""Input validation helpers for :mod:`iso8601`.

Centralised so every public entry point performs the same type checks with
identical error messages.
"""
from __future__ import annotations

from ._errors import InvalidInputError

__all__ = ["ensure_text", "split_sign"]


def ensure_text(value: object, what: str) -> str:
    """Return *value* if it is a non-empty ``str``; otherwise raise.

    :param value: object received from the caller.
    :param what: short description of the argument (e.g. ``"date string"``).
    :raises InvalidInputError: when *value* is not a :class:`str` or is empty.
    """
    if isinstance(value, str):
        if not value:
            raise InvalidInputError(value, f"non-empty {what}")
        return value
    raise InvalidInputError(value, f"non-empty {what}")


def split_sign(text: str) -> tuple[int, str]:
    """Strip a leading ``+``/``-`` and return ``(sign, remainder)``.

    Returns ``(1, text)`` if no sign is present, ``(-1, text[1:])`` for ``-``,
    ``(1, text[1:])`` for ``+``.
    """
    if text.startswith("-"):
        return -1, text[1:]
    if text.startswith("+"):
        return 1, text[1:]
    return 1, text
