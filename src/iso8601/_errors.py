"""Exception tree for the :mod:`iso8601` package.

All errors raised by :mod:`iso8601` derive from :class:`Iso8601Error` so
callers can catch one class to handle every library-specific failure.
"""
from __future__ import annotations

__all__ = [
    "Iso8601Error",
    "ParseError",
    "InvalidInputError",
]


class Iso8601Error(Exception):
    """Base class for every error raised by :mod:`iso8601`."""


class ParseError(Iso8601Error):
    """Raised when a string cannot be parsed as a valid ISO-8601 production."""

    def __init__(self, text: object, kind: str, detail: str = "") -> None:
        self.text = text
        self.kind = kind
        self.detail = detail
        suffix = f" ({detail})" if detail else ""
        super().__init__(f"Invalid ISO-8601 {kind}: {text!r}{suffix}")


class InvalidInputError(Iso8601Error):
    """Raised when an argument has the wrong type."""

    def __init__(self, value: object, expected: str) -> None:
        self.value = value
        self.expected = expected
        super().__init__(
            f"Expected {expected}, got {type(value).__name__}: {value!r}"
        )
