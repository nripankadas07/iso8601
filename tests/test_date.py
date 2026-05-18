"""Tests for :func:`iso8601.parse_date` and :func:`iso8601.format_date`."""
from __future__ import annotations

import datetime as _dt

import pytest

import iso8601


class TestCalendarExtended:
    def test_basic_iso_date(self) -> None:
        assert iso8601.parse_date("2026-05-13") == _dt.date(2026, 5, 13)

    def test_first_of_january(self) -> None:
        assert iso8601.parse_date("2000-01-01") == _dt.date(2000, 1, 1)

    def test_last_of_december(self) -> None:
        assert iso8601.parse_date("1999-12-31") == _dt.date(1999, 12, 31)

    def test_leap_day(self) -> None:
        assert iso8601.parse_date("2024-02-29") == _dt.date(2024, 2, 29)

    def test_invalid_month_zero(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2026-00-10")

    def test_invalid_month_thirteen(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2026-13-10")

    def test_invalid_day_zero(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2026-05-00")

    def test_february_30_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2025-02-30")

    def test_non_leap_february_29_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2023-02-29")


class TestCalendarBasic:
    def test_basic_date(self) -> None:
        assert iso8601.parse_date("20260513") == _dt.date(2026, 5, 13)

    def test_basic_leap_day(self) -> None:
        assert iso8601.parse_date("20240229") == _dt.date(2024, 2, 29)

    def test_basic_invalid_month(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("20261301")

    def test_basic_short_rejected(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2026")


class TestOrdinal:
    def test_extended_ordinal(self) -> None:
        assert iso8601.parse_date("2026-001") == _dt.date(2026, 1, 1)

    def test_extended_ordinal_last_day(self) -> None:
        assert iso8601.parse_date("2025-365") == _dt.date(2025, 12, 31)

    def test_extended_ordinal_leap_year_366(self) -> None:
        assert iso8601.parse_date("2024-366") == _dt.date(2024, 12, 31)

    def test_extended_ordinal_366_in_non_leap_rejected(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2025-366")

    def test_extended_ordinal_zero_rejected(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2025-000")

    def test_basic_ordinal(self) -> None:
        assert iso8601.parse_date("2026001") == _dt.date(2026, 1, 1)

    def test_basic_ordinal_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2025366")


class TestWeekDate:
    def test_week_extended_first_week(self) -> None:
        assert iso8601.parse_date("2026-W01-1") == _dt.date(2025, 12, 29)

    def test_week_extended_mid_year(self) -> None:
        assert iso8601.parse_date("2026-W20-3") == _dt.date(2026, 5, 13)

    def test_week_extended_last_week_52(self) -> None:
        assert iso8601.parse_date("2025-W52-7") == _dt.date(2025, 12, 28)

    def test_week_extended_week_53_valid(self) -> None:
        # 2020 has 53 ISO weeks (Jan 1 is Wed and leap).
        assert iso8601.parse_date("2020-W53-1") == _dt.date(2020, 12, 28)

    def test_week_extended_week_53_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2025-W53-1")

    def test_week_extended_weekday_zero_invalid(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2026-W20-0")

    def test_week_basic(self) -> None:
        assert iso8601.parse_date("2026W203") == _dt.date(2026, 5, 13)

    def test_week_basic_bad_shape(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2026-W2-1")


class TestFormatAndErrors:
    def test_format_extended(self) -> None:
        assert iso8601.format_date(_dt.date(2026, 5, 13)) == "2026-05-13"

    def test_format_basic(self) -> None:
        assert iso8601.format_date(_dt.date(2026, 5, 13), basic=True) == "20260513"

    def test_format_zero_padded(self) -> None:
        assert iso8601.format_date(_dt.date(1, 1, 1)) == "0001-01-01"

    def test_format_rejects_non_date(self) -> None:
        with pytest.raises(TypeError):
            iso8601.format_date("not-a-date")  # type: ignore[arg-type]

    def test_parse_rejects_non_string(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.parse_date(20260513)  # type: ignore[arg-type]

    def test_parse_rejects_empty(self) -> None:
        with pytest.raises(iso8601.InvalidInputError):
            iso8601.parse_date("")

    def test_parse_rejects_random_garbage(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("hello world")

    def test_parse_rejects_unrecognised_extended_form(self) -> None:
        with pytest.raises(iso8601.ParseError):
            iso8601.parse_date("2026-05")

    def test_round_trip_extended(self) -> None:
        original = _dt.date(2026, 5, 13)
        assert iso8601.parse_date(iso8601.format_date(original)) == original

    def test_round_trip_basic(self) -> None:
        original = _dt.date(1999, 12, 31)
        assert iso8601.parse_date(
            iso8601.format_date(original, basic=True)
        ) == original
