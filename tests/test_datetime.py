"""Tests for :func:`iso8601.parse_datetime` / :func:`iso8601.format_datetime`."""
from __future__ import annotations

import datetime as _dt

import pytest

import iso8601


class TestParseExtended:
    def test_t_separator(self) -> None:
        result = iso8601.parse_datetime("2026-05-13T09:30:00")
        assert result == _dt.datetime(2026, 5, 13, 9, 30, 0)

    def test_space_separator(self) -> None:
        result = iso8601.parse_datetime("2026-05-13 09:30:00")
        assert result == _dt.datetime(2026, 5, 13, 9, 30, 0)

    def test_with_z(self) -> None:
        result = iso8601.parse_datetime("2026-05-13T09:30:00Z")
        assert result == _dt.datetime(
            2026, 5, 13, 9, 30, 0, tzinfo=iso8601.TZ_UTC
        )

    def test_with_offset(self) -> None:
        result = iso8601.parse_datetime("2026-05-13T09:30:00+05:30")
        assert result.utcoffset() == _dt.timedelta(hours=5, minutes=30)

    def test_with_fraction(self) -> None:
        result = iso8601.parse_datetime("2026-05-13T09:30:00.250")
        assert result.microsecond == 250_000


class TestParseBasic:
    def test_basic_datetime(self) -> None:
        result = iso8601.parse_datetime("20260513T093045")
        assert result == _dt.datetime(2026, 5, 13, 9, 30, 45)

    def test_basic_with_z(self) -> None:
        result = iso8601.parse_datetime("20260513T093045Z")
        assert result == _dt.datetime(
            2026, 5, 13, 9, 30, 45, tzinfo=iso8601.TZ_UTC
        )


class TestRejections:
    def test_mixed_basic_date_extended_time(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_datetime("20260513T09:30:00")

    def test_mixed_extended_date_basic_time(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_datetime("2026-05-13T093000")

    def test_missing_separator(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_datetime("2026-05-1309:30:00")

    def test_empty_date_portion(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_datetime("T09:30:00")

    def test_empty_time_portion(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_datetime("2026-05-13T")

    def test_invalid_date(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_datetime("2026-13-01T09:30:00")

    def test_invalid_time(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_datetime("2026-05-13T25:00:00")

    def test_non_string_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.parse_datetime(20260513)  # type: ignore[arg-type]

    def test_empty_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.parse_datetime("")


class TestFormat:
    def test_format_naive(self) -> None:
        dt = _dt.datetime(2026, 5, 13, 9, 30, 0)
        assert iso8601.format_datetime(dt) == "2026-05-13T09:30:00"

    def test_format_with_utc(self) -> None:
        dt = _dt.datetime(2026, 5, 13, 9, 30, 0, tzinfo=iso8601.TZ_UTC)
        assert iso8601.format_datetime(dt) == "2026-05-13T09:30:00Z"

    def test_format_with_microseconds(self) -> None:
        dt = _dt.datetime(2026, 5, 13, 9, 30, 0, 123_456)
        assert iso8601.format_datetime(dt) == "2026-05-13T09:30:00.123456"

    def test_format_basic(self) -> None:
        dt = _dt.datetime(2026, 5, 13, 9, 30, 0, tzinfo=iso8601.TZ_UTC)
        assert iso8601.format_datetime(dt, basic=True) == "20260513T093000Z"

    def test_format_rejects_non_datetime(self) -> None:
        with pytest.raises(TypeError):
            iso8601.format_datetime(_dt.date(2026, 5, 13))  # type: ignore[arg-type]


class TestRoundTrip:
    def test_round_trip_extended(self) -> None:
        original = _dt.datetime(
            2026, 5, 13, 9, 30, 0, 123_456, tzinfo=iso8601.TZ_UTC
        )
        rendered = iso8601.format_datetime(original)
        assert iso8601.parse_datetime(rendered) == original

    def test_round_trip_basic(self) -> None:
        tz = _dt.timezone(_dt.timedelta(hours=-3))
        original = _dt.datetime(2026, 5, 13, 9, 30, 0, tzinfo=tz)
        rendered = iso8601.format_datetime(original, basic=True)
        assert iso8601.parse_datetime(rendered) == original
