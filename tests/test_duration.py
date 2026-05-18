"""Tests for :class:`iso8601.Duration` and the duration parser/formatter."""
from __future__ import annotations

import datetime as _dt

import pytest

import iso8601


class TestDurationConstruction:
    def test_default_is_zero(self) -> None:
        assert iso8601.Duration().is_zero()

    def test_negative_int_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.Duration(years=-1)

    def test_non_int_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.Duration(days=1.5)  # type: ignore[arg-type]

    def test_bool_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.Duration(days=True)  # type: ignore[arg-type]

    def test_microseconds_overflow_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.Duration(microseconds=1_000_000)

    def test_weeks_with_other_components_rejected(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.Duration(weeks=1, days=1)

    def test_weeks_alone_allowed(self) -> None:
        d = iso8601.Duration(weeks=3)
        assert not d.is_zero()


class TestDurationParse:
    def test_simple_p1d(self) -> None:
        assert iso8601.parse_duration("P1D") == iso8601.Duration(days=1)

    def test_full_form(self) -> None:
        result = iso8601.parse_duration("P3Y6M4DT12H30M5S")
        assert result == iso8601.Duration(
            years=3, months=6, days=4, hours=12, minutes=30, seconds=5
        )

    def test_time_only(self) -> None:
        assert iso8601.parse_duration("PT1H") == iso8601.Duration(hours=1)

    def test_weeks_only(self) -> None:
        assert iso8601.parse_duration("P3W") == iso8601.Duration(weeks=3)

    def test_negative_prefix(self) -> None:
        assert iso8601.parse_duration("-P1D") == iso8601.Duration(
            days=1, negative=True
        )

    def test_positive_prefix(self) -> None:
        assert iso8601.parse_duration("+P1D") == iso8601.Duration(days=1)

    def test_fractional_seconds_dot(self) -> None:
        result = iso8601.parse_duration("PT0.5S")
        assert result.seconds == 0
        assert result.microseconds == 500_000

    def test_fractional_seconds_comma(self) -> None:
        result = iso8601.parse_duration("PT0,250S")
        assert result.microseconds == 250_000

    def test_fractional_truncated_to_six(self) -> None:
        result = iso8601.parse_duration("PT0.123456789S")
        assert result.microseconds == 123_456

    def test_pt0s_zero(self) -> None:
        assert iso8601.parse_duration("PT0S") == iso8601.Duration()

    def test_p0d_zero(self) -> None:
        assert iso8601.parse_duration("P0D") == iso8601.Duration(days=0)


class TestDurationParseErrors:
    def test_missing_p(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("1Y")

    def test_empty_after_p(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P")

    def test_lowercase_letters(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P1y")

    def test_garbage(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("hello")

    def test_non_string(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.parse_duration(123)  # type: ignore[arg-type]

    def test_empty_time_after_t(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P1DT")

    def test_duplicate_designator(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P1Y2Y")

    def test_out_of_order_designator(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P1D2Y")

    def test_time_out_of_order(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("PT1S2H")

    def test_fractional_minutes_rejected(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("PT0.5M")

    def test_fractional_hours_rejected(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("PT0.5H")

    def test_bad_date_portion(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P1X")

    def test_bad_time_portion(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P1DT0X")

    def test_weeks_with_decimal_rejected(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_duration("P1.5W")


class TestDurationFormat:
    def test_format_zero(self) -> None:
        assert iso8601.format_duration(iso8601.Duration()) == "PT0S"

    def test_format_full(self) -> None:
        d = iso8601.Duration(
            years=3, months=6, days=4, hours=12, minutes=30, seconds=5
        )
        assert iso8601.format_duration(d) == "P3Y6M4DT12H30M5S"

    def test_format_time_only(self) -> None:
        assert iso8601.format_duration(iso8601.Duration(hours=2)) == "PT2H"

    def test_format_weeks(self) -> None:
        assert iso8601.format_duration(iso8601.Duration(weeks=3)) == "P3W"

    def test_format_negative(self) -> None:
        d = iso8601.Duration(days=1, negative=True)
        assert iso8601.format_duration(d) == "-P1D"

    def test_format_negative_zero_no_sign(self) -> None:
        # A zero duration with negative=True still formats without sign.
        assert iso8601.format_duration(
            iso8601.Duration(negative=True)
        ) == "PT0S"

    def test_format_fractional_seconds(self) -> None:
        d = iso8601.Duration(seconds=1, microseconds=500_000)
        assert iso8601.format_duration(d) == "PT1.5S"

    def test_format_fractional_only_micros(self) -> None:
        d = iso8601.Duration(microseconds=250_000)
        assert iso8601.format_duration(d) == "PT0.25S"

    def test_format_rejects_non_duration(self) -> None:
        with pytest.raises(TypeError):
            iso8601.format_duration("not a duration")  # type: ignore[arg-type]


class TestToTimedelta:
    def test_simple_conversion(self) -> None:
        d = iso8601.Duration(days=1, hours=2)
        assert d.to_timedelta() == _dt.timedelta(days=1, hours=2)

    def test_weeks_conversion(self) -> None:
        d = iso8601.Duration(weeks=2)
        assert d.to_timedelta() == _dt.timedelta(weeks=2)

    def test_negative_flips_sign(self) -> None:
        d = iso8601.Duration(days=1, negative=True)
        assert d.to_timedelta() == _dt.timedelta(days=-1)

    def test_years_rejected(self) -> None:
        d = iso8601.Duration(years=1)
        with pytest.raises(iso8601.InvalidInputError):
            d.to_timedelta()

    def test_months_rejected(self) -> None:
        d = iso8601.Duration(months=1)
        with pytest.raises(iso8601.InvalidInputError):
            d.to_timedelta()

    def test_fractional_seconds_preserved(self) -> None:
        d = iso8601.Duration(seconds=1, microseconds=500_000)
        assert d.to_timedelta() == _dt.timedelta(seconds=1, microseconds=500_000)


class TestRoundTrip:
    def test_round_trip_full(self) -> None:
        original = iso8601.Duration(
            years=3, months=6, days=4, hours=12, minutes=30, seconds=5
        )
        assert iso8601.parse_duration(iso8601.format_duration(original)) == original

    def test_round_trip_negative_weeks(self) -> None:
        original = iso8601.Duration(weeks=2, negative=True)
        assert iso8601.parse_duration(iso8601.format_duration(original)) == original

    def test_round_trip_fractional(self) -> None:
        original = iso8601.Duration(seconds=1, microseconds=125_000)
        assert iso8601.parse_duration(iso8601.format_duration(original)) == original
