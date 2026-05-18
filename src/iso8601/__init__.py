"""iso8601 — strict ISO-8601 date, time, datetime and duration parser.

A small, zero-dependency library that recognises every common ISO-8601
production and round-trips between strings and Python's :mod:`datetime`
types.

Supported productions:

* Calendar dates: ``YYYY-MM-DD`` / ``YYYYMMDD``
* Ordinal dates: ``YYYY-DDD`` / ``YYYYDDD``
* Week dates: ``YYYY-Www-D`` / ``YYYYWwwD``
* Times of day with optional fractional seconds and timezone designator
* Combined ``<date>T<time>`` datetimes
* Durations: ``P3Y6M4DT12H30M5S``, ``P1W``, with optional fractional seconds

Example::

    >>> import iso8601
    >>> iso8601.parse_datetime("2026-05-13T09:30:00Z")
    datetime.datetime(2026, 5, 13, 9, 30, tzinfo=datetime.timezone.utc)
    >>> iso8601.format_duration(iso8601.Duration(hours=1, minutes=30))
    'PT1H30M'
"""
from __future__ import annotations

from ._date import format_date, parse_date
from ._datetime import format_datetime, parse_datetime
from ._duration import Duration, format_duration, parse_duration
from ._errors import InvalidInputError, Iso8601Error, ParseError
from ._time import TZ_UTC, format_time, parse_time

__all__ = [
    "Duration",
    "InvalidInputError",
    "Iso8601Error",
    "ParseError",
    "TZ_UTC",
    "format_date",
    "format_datetime",
    "format_duration",
    "format_time",
    "parse_date",
    "parse_datetime",
    "parse_duration",
    "parse_time",
]

__version__ = "0.1.0"
