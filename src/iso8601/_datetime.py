"""ISO-8601 combined datetime parsing and formatting.

The combined production is ``<date>T<time>``. A literal space is also
accepted as the date/time separator (RFC 3339 §5.6). Mixing basic and
extended forms within a single string is rejected.
"""
from __future__ import annotations

import datetime as _dt

from ._date import format_date, parse_date
from ._errors import ParseError
from ._time import format_time, parse_time
from ._validate import ensure_text

__all__ = ["parse_datetime", "format_datetime"]


def parse_datetime(text: object) -> _dt.datetime:
    """Parse an ISO-8601 combined datetime and return a :class:`datetime.datetime`.

    A timezone designator (``Z`` or ``±HH[:?MM]``) produces a tz-aware result.

    :raises InvalidInputError: when *text* is not a non-empty string.
    :raises ParseError: when *text* is not a valid ISO-8601 datetime.
    """
    raw = ensure_text(text, "datetime string")
    date_part, time_part = _split_datetime(raw)
    if _is_basic_date(date_part) != _is_basic_time(time_part):
        raise ParseError(raw, "datetime", "mixed basic and extended forms")
    date = parse_date(date_part)
    time = parse_time(time_part)
    return _dt.datetime.combine(date, time, tzinfo=time.tzinfo)


def format_datetime(value: _dt.datetime, *, basic: bool = False) -> str:
    """Return *value* as an ISO-8601 combined datetime string.

    :param value: a :class:`datetime.datetime` instance.
    :param basic: emit the basic form (no separators) when ``True``.
    :raises TypeError: when *value* is not a :class:`datetime.datetime`.
    """
    if not isinstance(value, _dt.datetime):
        raise TypeError(
            "format_datetime() requires datetime.datetime, "
            f"got {type(value).__name__}"
        )
    return (
        format_date(value.date(), basic=basic)
        + "T"
        + format_time(value.timetz(), basic=basic)
    )


def _split_datetime(text: str) -> tuple[str, str]:
    if "T" in text:
        date_part, _, time_part = text.partition("T")
    elif " " in text:
        date_part, _, time_part = text.partition(" ")
    else:
        raise ParseError(text, "datetime", "missing 'T' separator")
    if not date_part or not time_part:
        raise ParseError(text, "datetime", "empty date or time component")
    return date_part, time_part


def _is_basic_date(text: str) -> bool:
    return "-" not in text


def _is_basic_time(text: str) -> bool:
    body = _strip_tz(text)
    return ":" not in body


def _strip_tz(text: str) -> str:
    if text.endswith("Z"):
        return text[:-1]
    for index in range(len(text) - 1, 0, -1):
        char = text[index]
        if char in "+-":
            return text[:index]
    return text
