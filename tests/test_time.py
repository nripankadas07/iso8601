"""Tests for :func:`iso8601.parse_time` and :func:`iso8601.format_time`."""
from __future__ import annotations

import datetime as _dt

import pytest

import iso8601


class TestExtendedTime:
    def test_full_seconds(self) -> None:
        assert iso8601.parse_time("09:30:45") == _dt.time(9, 30, 45)

    def test_hour_minute_only(self) -> None:
        assert iso8601.parse_time("09:30") == _dt.time(9, 30, 0)

    def test_hour_only(self) -> None:
        assert iso8601.parse_time("09") == _dt.time(9, 0, 0)

    def test_midnight(self) -> None:
        assert iso8601.parse_time("00:00:00") == _dt.time(0, 0, 0)

    def test_one_second_before_midnight(self) -> None:
        assert iso8601.parse_time("23:59:59") == _dt.time(23, 59, 59)


class TestBasicTime:
    def test_basic_full(self) -> None:
        assert iso8601.parse_time("093045") == _dt.time(9, 30, 45)

    def test_basic_hh_mm(self) -> None:
        assert iso8601.parse_time("0930") == _dt.time(9, 30, 0)

    def test_basic_hh(self) -> None:
        assert iso8601.parse_time("09") == _dt.time(9, 0, 0)


class TestFractionalSeconds:
    def test_dot_fraction_millis(self) -> None:
        assert iso8601.parse_time("09:30:45.123") == _dt.time(9, 30, 45, 123_000)

    def test_dot_fraction_micros(self) -> None:
        assert iso8601.parse_time("09:30:45.123456") == _dt.time(
            9, 30, 45, 123_456
        )

    def test_comma_fraction(self) -> None:
        assert iso8601.parse_time("09:30:45,500") == _dt.time(9, 30, 45, 500_000)

    def test_basic_fraction(self) -> None:
        assert iso8601.parse_time("093045.001") == _dt.time(9, 30, 45, 1_000)

    def test_fraction_truncated_to_six(self) -> None:
        assert iso8601.parse_time("09:30:45.123456789") == _dt.time(
            9, 30, 45, 123_456
        )


class TestTimezones:
    def test_z_suffix_is_utc(self) -> None:
        result = iso8601.parse_time("09:30:00Z")
        assert result.tzinfo == iso8601.TZ_UTC

    def test_positive_offset_extended(self) -> None:
        result = iso8601.parse_time("09:30:00+05:30")
        assert result.utcoffset() == _dt.timedelta(hours=5, minutes=30)

    def test_negative_offset_extended(self) -> None:
        result = iso8601.parse_time("09:30:00-08:00")
        assert result.utcoffset() == _dt.timedelta(hours=-8)

    def test_offset_basic(self) -> None:
        result = iso8601.parse_time("093000+0530")
        assert result.utcoffset() == _dt.timedelta(hours=5, minutes=30)

    def test_offset_hour_only(self) -> None:
        result = iso8601.parse_time("09:30:00+05")
        assert result.utcoffset() == _dt.timedelta(hours=5)

    def test_offset_out_of_range(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_time("09:30:00+24:00")

    def test_bad_offset_shape(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_time("09:30:00+xx")

    def test_offset_minute_out_of_range(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_time("09:30:00+10:60")


class TestRangeErrors:
    def test_hour_24_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_time("24:00:00")

    def test_minute_60_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_time("09:60:00")

    def test_second_60_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_time("09:30:60")

    def test_bad_shape_raises(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_time("9:30")

    def test_non_string_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.parse_time(930)  # type: ignore[arg-type]

    def test_empty_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.parse_time("")


class TestFormat:
    def test_format_naive(self) -> None:
        assert iso8601.format_time(_dt.time(9, 30, 45)) == "09:30:45"

    def test_format_basic(self) -> None:
        assert iso8601.format_time(
            _dt.time(9, 30, 45), basic=True
        ) == "093045"

    def test_format_with_fraction(self) -> None:
        assert iso8601.format_time(
            _dt.time(9, 30, 45, 123_000)
        ) == "09:30:45.123"

    def test_format_with_utc(self) -> None:
        assert iso8601.format_time(
            _dt.time(9, 30, 45, tzinfo=iso8601.TZ_UTC)
        ) == "09:30:45Z"

    def test_format_with_positive_offset(self) -> None:
        tz = _dt.timezone(_dt.timedelta(hours=5, minutes=30))
        assert iso8601.format_time(
            _dt.time(9, 30, 45, tzinfo=tz)
        ) == "09:30:45+05:30"

    def test_format_with_negative_offset(self) -> None:
        tz = _dt.timezone(_dt.timedelta(hours=-8))
        assert iso8601.format_time(
            _dt.time(9, 30, 45, tzinfo=tz)
        ) == "09:30:45-08:00"

    def test_format_basic_offset_no_colon(self) -> None:
        tz = _dt.timezone(_dt.timedelta(hours=5, minutes=30))
        assert iso8601.format_time(
            _dt.time(9, 30, 45, tzinfo=tz), basic=True
        ) == "093045+0530"

    def test_format_rejects_non_time(self) -> None:
        with pytest.raises(TypeError):
            iso8601.format_time("nope")  # type: ignore[arg-type]

    def test_format_with_tzinfo_returning_none(self) -> None:
        class NullTz(_dt.tzinfo):
            def utcoffset(self, dt):  # type: ignore[override]
                return None

            def tzname(self, dt):  # type: ignore[override]
                return None

            def dst(self, dt):  # type: ignore[override]
                return None

        assert iso8601.format_time(
            _dt.time(9, 30, 45, tzinfo=NullTz())
        ) == "09:30:45"


class TestRoundTrip:
    def test_round_trip_with_offset(self) -> None:
        tz = _dt.timezone(_dt.timedelta(hours=-4))
        original = _dt.time(12, 30, 0, tzinfo=tz)
        rendered = iso8601.format_time(original)
        assert iso8601.parse_time(rendered) == original

    def test_round_trip_basic(self) -> None:
        original = _dt.time(23, 59, 59, 999_999)
        rendered = iso8601.format_time(original, basic=True)
        assert iso8601.parse_time(rendered) == original

    def test_round_trip_z(self) -> None:
        original = _dt.time(0, 0, 0, tzinfo=iso8601.TZ_UTC)
        rendered = iso8601.format_time(original)
        assert rendered.endswith("Z")
        assert iso8601.parse_time(rendered) == original
