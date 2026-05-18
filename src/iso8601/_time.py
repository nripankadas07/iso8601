"""ISO-8601 time-of-day parsing and formatting.

Supports:

* Extended – ``HH``, ``HH:MM``, ``HH:MM:SS``, ``HH:MM:SS.ffffff``
* Basic    – ``HH``, ``HHMM``, ``HHMMSS``, ``HHMMSS.ffffff``
* Comma decimal mark – ``HH:MM:SS,fff`` (per ISO-8601)
* Time-zone designators – ``Z``, ``±HH``, ``±HHMM``, ``±HH:MM``

Fractional precision is preserved up to six digits (microseconds). Excess
digits beyond six are truncated, matching :func:`datetime.time` behaviour.
"""
from __future__ import annotations

import datetime as _dt
import re

from ._errors import ParseError
from ._validate import ensure_text

__all__ = ["parse_time", "format_time", "TZ_UTC"]

TZ_UTC = _dt.timezone.utc

_OFFSET_RE = re.compile(r"^([+-])(\d{2})(?::?(\d{2}))?$")
_TIME_EXTENDED = re.compile(
    r"^(\d{2})(?::(\d{2})(?::(\d{2})(?:[.,](\d{1,9}))?)?)?$"
)
_TIME_BASIC = re.compile(
    r"^(\d{2})(?:(\d{2})(?:(\d{2})(?:[.,](\d{1,9}))?)?)?$"
)


def parse_time(text: object) -> _dt.time:
    """Parse an ISO-8601 time and return a :class:`datetime.time`.

    A time-zone designator (``Z`` or ``±HH[:?MM]``) produces a tz-aware result
    whose ``tzinfo`` is :class:`datetime.timezone`.

    :raises InvalidInputError: when *text* is not a non-empty string.
    :raises ParseError: when *text* is not a valid ISO-8601 time.
    """
    raw = ensure_text(text, "time string")
    body, tz = _split_tz(raw)
    h, m, s, micro = _parse_time_components(raw, body)
    return _dt.time(h, m, s, micro, tzinfo=tz)


def format_time(value: _dt.time, *, basic: bool = False) -> str:
    """Return *value* as an ISO-8601 time string.

    Always emits seconds (``HH:MM:SS``); fractional seconds appear only when
    *value* has a non-zero microsecond component. The timezone designator is
    emitted when *value* is tz-aware.
    """
    if not isinstance(value, _dt.time):
        raise TypeError(
            f"format_time() requires datetime.time, got {type(value).__name__}"
        )
    body = _format_time_body(value, basic=basic)
    return body + _format_offset(value, basic=basic)


def _split_tz(text: str) -> tuple[str, _dt.timezone | None]:
    if text.endswith("Z"):
        return text[:-1], TZ_UTC
    for index in range(len(text) - 1, 0, -1):
        if text[index] in "+-":
            return text[:index], _parse_offset_token(text[index:], text)
    return text, None


def _parse_offset_token(token: str, raw: str) -> _dt.timezone:
    match = _OFFSET_RE.match(token)
    if match is None:
        raise ParseError(raw, "time", f"bad offset {token!r}")
    sign = 1 if match[1] == "+" else -1
    hours = int(match[2])
    minutes = int(match[3]) if match[3] is not None else 0
    if hours > 23 or minutes > 59:
        raise ParseError(raw, "time", f"offset {token!r} out of range")
    delta = _dt.timedelta(hours=hours, minutes=minutes) * sign
    return _dt.timezone(delta)


def _parse_time_components(raw: str, body: str) -> tuple[int, int, int, int]:
    extended_match = _TIME_EXTENDED.match(body)
    basic_match = _TIME_BASIC.match(body)
    if ":" in body:
        match = extended_match
    else:
        match = basic_match
    if match is None:
        raise ParseError(raw, "time", f"unrecognised body {body!r}")
    h = int(match[1])
    m = int(match[2]) if match[2] is not None else 0
    s = int(match[3]) if match[3] is not None else 0
    micro = _fraction_to_microseconds(match[4]) if match[4] else 0
    _check_time_ranges(raw, h, m, s)
    return h, m, s, micro


def _check_time_ranges(raw: str, hours: int, minutes: int, seconds: int) -> None:
    if hours > 23:
        raise ParseError(raw, "time", f"hour {hours} out of range")
    if minutes > 59:
        raise ParseError(raw, "time", f"minute {minutes} out of range")
    if seconds > 59:
        raise ParseError(raw, "time", f"second {seconds} out of range")


def _fraction_to_microseconds(fraction: str) -> int:
    padded = (fraction + "000000")[:6]
    return int(padded)


def _format_time_body(value: _dt.time, *, basic: bool) -> str:
    sep = "" if basic else ":"
    body = f"{value.hour:02d}{sep}{value.minute:02d}{sep}{value.second:02d}"
    if value.microsecond:
        fraction = f"{value.microsecond:06d}".rstrip("0")
        body += f".{fraction}"
    return body


def _format_offset(value: _dt.time, *, basic: bool) -> str:
    tz = value.tzinfo
    if tz is None:
        return ""
    offset = tz.utcoffset(None)
    if offset is None:
        return ""
    return _format_offset_delta(offset, basic=basic)


def _format_offset_delta(offset: _dt.timedelta, *, basic: bool) -> str:
    total = int(offset.total_seconds())
    if total == 0:
        return "Z"
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, remainder = divmod(total, 3600)
    minutes = remainder // 60
    sep = "" if basic else ":"
    return f"{sign}{hours:02d}{sep}{minutes:02d}"
