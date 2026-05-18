"""ISO-8601 duration parsing, formatting and the :class:`Duration` type.

Grammar (informally):

    duration := sign? "P" ( weeks | composite )
    weeks    := number "W"
    composite := datepart? ("T" timepart)?
    datepart  := number ("Y" | "M" | "D") (datepart)?
    timepart  := number ("H" | "M" | "S") (timepart)?

Numbers may carry a fractional component using ``.`` or ``,`` (e.g.
``PT0.5S``). Per the standard, weeks cannot coexist with other components.
Fractional fields are accepted only on the seconds field; all other fields
must be integers.
"""
from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field

from ._errors import InvalidInputError, ParseError
from ._validate import ensure_text, split_sign

__all__ = ["Duration", "parse_duration", "format_duration"]

_WEEK_RE = re.compile(r"^(\d+)W$")
_DATE_TOKEN_RE = re.compile(r"(\d+)([YMD])")
_TIME_TOKEN_RE = re.compile(r"(\d+(?:[.,]\d+)?)([HMS])")
_DATE_TOKEN_FULL = re.compile(r"^(?:\d+[YMD])*$")
_TIME_TOKEN_FULL = re.compile(r"^(?:\d+(?:[.,]\d+)?[HMS])+$")

_DATE_LETTERS = ("Y", "M", "D")
_TIME_LETTERS = ("H", "M", "S")


@dataclass(frozen=True)
class Duration:
    """An ISO-8601 calendar duration.

    All component fields are non-negative integers. ``negative=True`` flips
    the sign of the whole duration. ``weeks`` is mutually exclusive with the
    other date/time components per the standard.
    """

    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    microseconds: int = 0
    negative: bool = field(default=False)

    def __post_init__(self) -> None:
        for name, value in self._components().items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise InvalidInputError(value, f"non-negative int ({name})")
            if value < 0:
                raise InvalidInputError(value, f"non-negative int ({name})")
        if self.microseconds >= 1_000_000:
            raise InvalidInputError(
                self.microseconds, "microseconds < 1_000_000"
            )
        if self.weeks and self._has_non_week_components():
            raise InvalidInputError(
                self.weeks,
                "weeks cannot be combined with other components",
            )

    def _components(self) -> dict[str, int]:
        return {
            "years": self.years,
            "months": self.months,
            "weeks": self.weeks,
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "microseconds": self.microseconds,
        }

    def _has_non_week_components(self) -> bool:
        return any(
            value
            for name, value in self._components().items()
            if name != "weeks"
        )

    def is_zero(self) -> bool:
        """Return ``True`` if every component is zero."""
        return all(value == 0 for value in self._components().values())

    def to_timedelta(self) -> _dt.timedelta:
        """Return an equivalent :class:`datetime.timedelta`.

        :raises InvalidInputError: when ``years`` or ``months`` is non-zero.
            Months and years have ambiguous lengths so no fixed conversion
            exists.
        """
        if self.years or self.months:
            raise InvalidInputError(
                self, "duration without years or months for timedelta()"
            )
        total = _dt.timedelta(
            weeks=self.weeks,
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
            microseconds=self.microseconds,
        )
        return -total if self.negative else total


def parse_duration(text: object) -> Duration:
    """Parse an ISO-8601 duration string and return a :class:`Duration`."""
    raw = ensure_text(text, "duration string")
    sign, body = split_sign(raw)
    if not body.startswith("P"):
        raise ParseError(raw, "duration", "missing 'P' prefix")
    body = body[1:]
    if not body:
        raise ParseError(raw, "duration", "empty after 'P'")
    week_match = _WEEK_RE.match(body)
    if week_match is not None:
        return Duration(weeks=int(week_match[1]), negative=(sign == -1))
    return _parse_composite(raw, body, negative=(sign == -1))


def format_duration(duration: Duration) -> str:
    """Format a :class:`Duration` as a canonical ISO-8601 string."""
    if not isinstance(duration, Duration):
        raise TypeError(
            f"format_duration() requires Duration, got {type(duration).__name__}"
        )
    body = _format_body(duration)
    sign = "-" if duration.negative and not duration.is_zero() else ""
    return f"{sign}P{body}"


def _parse_composite(raw: str, body: str, *, negative: bool) -> Duration:
    date_body, _, time_body = body.partition("T")
    _validate_date_body(raw, date_body)
    _validate_time_body(raw, body, time_body)
    # The validators guarantee at least one of date_body or time_body is
    # non-empty here: an empty body was rejected before we were called, and
    # the "T with nothing after" case raises "empty time portion after T".
    date_counts = _parse_tokens(
        raw, date_body, _DATE_TOKEN_RE, _DATE_LETTERS
    )
    time_counts, seconds_pair = _parse_time_tokens(raw, time_body)
    return Duration(
        years=date_counts.get("Y", 0),
        months=date_counts.get("M", 0),
        days=date_counts.get("D", 0),
        hours=time_counts.get("H", 0),
        minutes=time_counts.get("M", 0),
        seconds=seconds_pair[0],
        microseconds=seconds_pair[1],
        negative=negative,
    )


def _validate_date_body(raw: str, date_body: str) -> None:
    if date_body and _DATE_TOKEN_FULL.match(date_body) is None:
        raise ParseError(raw, "duration", "bad date portion")


def _validate_time_body(raw: str, body: str, time_body: str) -> None:
    if "T" in body and not time_body:
        raise ParseError(raw, "duration", "empty time portion after 'T'")
    if time_body and _TIME_TOKEN_FULL.match(time_body) is None:
        raise ParseError(raw, "duration", "bad time portion")


def _parse_tokens(
    raw: str,
    body: str,
    pattern: re.Pattern[str],
    order: tuple[str, ...],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    seen: list[str] = []
    for value_str, letter in pattern.findall(body):
        _check_order(raw, letter, seen, order)
        seen.append(letter)
        counts[letter] = int(value_str)
    return counts


def _parse_time_tokens(
    raw: str, time_body: str
) -> tuple[dict[str, int], tuple[int, int]]:
    counts: dict[str, int] = {}
    seconds_pair = (0, 0)
    seen: list[str] = []
    for value_str, letter in _TIME_TOKEN_RE.findall(time_body):
        _check_order(raw, letter, seen, _TIME_LETTERS)
        seen.append(letter)
        if letter == "S":
            seconds_pair = _split_seconds_token(value_str)
        else:
            if "." in value_str or "," in value_str:
                raise ParseError(
                    raw, "duration", f"fractional {letter} not allowed"
                )
            counts[letter] = int(value_str)
    return counts, seconds_pair


def _check_order(
    raw: str, letter: str, seen: list[str], order: tuple[str, ...]
) -> None:
    if letter in seen:
        raise ParseError(raw, "duration", f"duplicate {letter}")
    if seen and order.index(letter) <= order.index(seen[-1]):
        raise ParseError(raw, "duration", f"out-of-order {letter}")


def _split_seconds_token(value_str: str) -> tuple[int, int]:
    normalised = value_str.replace(",", ".")
    if "." in normalised:
        whole_str, frac_str = normalised.split(".")
        whole = int(whole_str) if whole_str else 0
        micros = int((frac_str + "000000")[:6])
        return whole, micros
    return int(normalised), 0


def _format_body(duration: Duration) -> str:
    if duration.is_zero():
        return "T0S"
    if duration.weeks:
        return f"{duration.weeks}W"
    date_part = _format_date_part(duration)
    time_part = _format_time_part(duration)
    return date_part + time_part


def _format_date_part(duration: Duration) -> str:
    pieces: list[str] = []
    if duration.years:
        pieces.append(f"{duration.years}Y")
    if duration.months:
        pieces.append(f"{duration.months}M")
    if duration.days:
        pieces.append(f"{duration.days}D")
    return "".join(pieces)


def _format_time_part(duration: Duration) -> str:
    pieces: list[str] = []
    if duration.hours:
        pieces.append(f"{duration.hours}H")
    if duration.minutes:
        pieces.append(f"{duration.minutes}M")
    seconds_text = _format_seconds(duration)
    if seconds_text:
        pieces.append(seconds_text)
    return "T" + "".join(pieces) if pieces else ""


def _format_seconds(duration: Duration) -> str:
    if not duration.seconds and not duration.microseconds:
        return ""
    if duration.microseconds:
        fraction = f"{duration.microseconds:06d}".rstrip("0")
        return f"{duration.seconds}.{fraction}S"
    return f"{duration.seconds}S"
