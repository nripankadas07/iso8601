"""Cross-module integration tests for :mod:`iso8601`."""
from __future__ import annotations

import datetime as _dt

import pytest

import iso8601


def test_datetime_round_trip_with_fraction_and_offset() -> None:
    tz = _dt.timezone(_dt.timedelta(hours=-5))
    original = _dt.datetime(2026, 1, 2, 3, 4, 5, 678_000, tzinfo=tz)
    rendered = iso8601.format_datetime(original)
    assert iso8601.parse_datetime(rendered) == original


def test_date_components_match() -> None:
    parsed = iso8601.parse_date("2026-05-13")
    assert parsed.year == 2026
    assert parsed.month == 5
    assert parsed.day == 13


def test_week_date_consistency_with_calendar() -> None:
    # The week-date and calendar forms must produce the same date.
    cal = iso8601.parse_date("2026-05-13")
    week = iso8601.parse_date("2026-W20-3")
    assert cal == week


def test_basic_and_extended_calendar_agree() -> None:
    assert iso8601.parse_date("2026-05-13") == iso8601.parse_date("20260513")


def test_ordinal_and_calendar_agree() -> None:
    # 2026-05-13 is the 133rd day of 2026.
    ordinal = iso8601.parse_date("2026-133")
    cal = iso8601.parse_date("2026-05-13")
    assert ordinal == cal


def test_duration_arithmetic_via_timedelta() -> None:
    base = iso8601.parse_datetime("2026-05-13T09:30:00Z")
    delta = iso8601.parse_duration("PT1H30M").to_timedelta()
    later = base + delta
    assert iso8601.format_datetime(later) == "2026-05-13T11:00:00Z"


def test_negative_duration_subtracts() -> None:
    base = iso8601.parse_datetime("2026-05-13T09:30:00Z")
    delta = iso8601.parse_duration("-PT30M").to_timedelta()
    earlier = base + delta
    assert iso8601.format_datetime(earlier) == "2026-05-13T09:00:00Z"


def test_full_combined_round_trip_basic() -> None:
    tz = _dt.timezone(_dt.timedelta(hours=2))
    original = _dt.datetime(1999, 12, 31, 23, 59, 59, tzinfo=tz)
    rendered = iso8601.format_datetime(original, basic=True)
    assert rendered == "19991231T235959+0200"
    assert iso8601.parse_datetime(rendered) == original


def test_every_error_inherits_from_iso8601_error() -> None:
    with pytest.raises(iso8601.Iso8601Error):
        iso8601.parse_date("nope")
    with pytest.raises(iso8601.Iso8601Error):
        iso8601.parse_time("nope")
    with pytest.raises(iso8601.Iso8601Error):
        iso8601.parse_duration("nope")
    with pytest.raises(iso8601.Iso8601Error):
        iso8601.parse_datetime("nope")


def test_format_parse_duration_keeps_fraction_precision() -> None:
    original = iso8601.Duration(seconds=2, microseconds=345_678)
    text = iso8601.format_duration(original)
    assert iso8601.parse_duration(text) == original
