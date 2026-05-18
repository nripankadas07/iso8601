"""ISO-8601 calendar / ordinal / week-date parsing and formatting.

Supports the four canonical date productions:

* Extended calendar  – ``YYYY-MM-DD``
* Basic calendar     – ``YYYYMMDD``
* Extended ordinal   – ``YYYY-DDD``
* Basic ordinal      – ``YYYYDDD``
* Extended week date – ``YYYY-Www-D``
* Basic week date    – ``YYYYWwwD``

Mixing basic and extended forms is rejected per the standard.
"""
from __future__ import annotations

import datetime as _dt
import re
from typing import Callable

from ._errors import ParseError
from ._validate import ensure_text

_DateParser = Callable[[str], _dt.date]

__all__ = ["parse_date", "format_date"]

_CAL_EXTENDED = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_CAL_BASIC = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
_ORD_EXTENDED = re.compile(r"^(\d{4})-(\d{3})$")
_ORD_BASIC = re.compile(r"^(\d{4})(\d{3})$")
_WEEK_EXTENDED = re.compile(r"^(\d{4})-W(\d{2})-(\d)$")
_WEEK_BASIC = re.compile(r"^(\d{4})W(\d{2})(\d)$")


def parse_date(text: object) -> _dt.date:
    """Parse an ISO-8601 date string and return a :class:`datetime.date`.

    Accepts every common ISO-8601 date production: calendar, ordinal and
    week-date forms, in both extended (with separators) and basic (no
    separators) shapes.

    :raises InvalidInputError: when *text* is not a non-empty string.
    :raises ParseError: when *text* is not a valid ISO-8601 date.
    """
    raw = ensure_text(text, "date string")
    parser = _select_date_parser(raw)
    return parser(raw)


def format_date(value: _dt.date, *, basic: bool = False) -> str:
    """Return *value* as an ISO-8601 calendar date.

    :param value: a :class:`datetime.date` (or :class:`datetime.datetime`).
    :param basic: emit ``YYYYMMDD`` instead of ``YYYY-MM-DD`` when ``True``.
    :raises TypeError: when *value* is not a date.
    """
    if not isinstance(value, _dt.date):
        raise TypeError(
            f"format_date() requires datetime.date, got {type(value).__name__}"
        )
    if basic:
        return f"{value.year:04d}{value.month:02d}{value.day:02d}"
    return f"{value.year:04d}-{value.month:02d}-{value.day:02d}"


def _select_date_parser(text: str) -> _DateParser:
    """Return the parser appropriate to *text* based on shape heuristics."""
    if "W" in text:
        return _parse_week
    if "-" in text:
        return _parse_extended
    return _parse_basic


def _parse_extended(text: str) -> _dt.date:
    if (m := _CAL_EXTENDED.match(text)) is not None:
        return _build_calendar(text, int(m[1]), int(m[2]), int(m[3]))
    if (m := _ORD_EXTENDED.match(text)) is not None:
        return _build_ordinal(text, int(m[1]), int(m[2]))
    raise ParseError(text, "date", "unrecognised extended form")


def _parse_basic(text: str) -> _dt.date:
    if (m := _CAL_BASIC.match(text)) is not None:
        return _build_calendar(text, int(m[1]), int(m[2]), int(m[3]))
    if (m := _ORD_BASIC.match(text)) is not None:
        return _build_ordinal(text, int(m[1]), int(m[2]))
    raise ParseError(text, "date", "unrecognised basic form")


def _parse_week(text: str) -> _dt.date:
    if (m := _WEEK_EXTENDED.match(text)) is not None:
        return _build_week(text, int(m[1]), int(m[2]), int(m[3]))
    if (m := _WEEK_BASIC.match(text)) is not None:
        return _build_week(text, int(m[1]), int(m[2]), int(m[3]))
    raise ParseError(text, "date", "unrecognised week form")


def _build_calendar(raw: str, year: int, month: int, day: int) -> _dt.date:
    try:
        return _dt.date(year, month, day)
    except ValueError as exc:
        raise ParseError(raw, "date", str(exc)) from None


def _build_ordinal(raw: str, year: int, ordinal: int) -> _dt.date:
    days_in_year = 366 if _is_leap(year) else 365
    if not 1 <= ordinal <= days_in_year:
        raise ParseError(raw, "date", f"ordinal day {ordinal} out of range")
    return _dt.date(year, 1, 1) + _dt.timedelta(days=ordinal - 1)


def _build_week(raw: str, year: int, week: int, weekday: int) -> _dt.date:
    if not 1 <= week <= _weeks_in_iso_year(year):
        raise ParseError(raw, "date", f"week {week} out of range")
    if not 1 <= weekday <= 7:
        raise ParseError(raw, "date", f"weekday {weekday} out of range")
    return _dt.date.fromisocalendar(year, week, weekday)


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _weeks_in_iso_year(year: int) -> int:
    """Return 52 or 53 — the number of ISO weeks in *year*."""
    return 53 if _has_53_weeks(year) else 52


def _has_53_weeks(year: int) -> bool:
    """ISO-8601 year has 53 weeks if Jan 1 is Thursday or (leap & Wednesday)."""
    jan1 = _dt.date(year, 1, 1).isoweekday()
    return jan1 == 4 or (jan1 == 3 and _is_leap(year))
