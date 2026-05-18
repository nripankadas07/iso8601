"""Tests covering the public API surface exposed at the package root."""
from __future__ import annotations

import iso8601


def test_public_attributes_match_all() -> None:
    assert set(iso8601.__all__) == {
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
    }


def test_every_export_is_resolvable() -> None:
    for name in iso8601.__all__:
        assert getattr(iso8601, name) is not None


def test_version_is_semantic_string() -> None:
    assert isinstance(iso8601.__version__, str)
    pieces = iso8601.__version__.split(".")
    assert len(pieces) == 3
    for piece in pieces:
        assert piece.isdigit()


def test_error_hierarchy() -> None:
    assert issubclass(iso8601.ParseError, iso8601.Iso8601Error)
    assert issubclass(iso8601.InvalidInputError, iso8601.Iso8601Error)
    assert issubclass(iso8601.Iso8601Error, Exception)


def test_tz_utc_zero_offset() -> None:
    import datetime as _dt
    assert iso8601.TZ_UTC.utcoffset(None) == _dt.timedelta(0)
