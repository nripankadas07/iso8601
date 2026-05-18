"""Tests for the validation helpers in :mod:`iso8601._validate`."""
from __future__ import annotations

import pytest

from iso8601._errors import InvalidInputError
from iso8601._validate import ensure_text, split_sign


class TestEnsureText:
    def test_non_empty_string_passes(self) -> None:
        assert ensure_text("hello", "thing") == "hello"

    def test_empty_string_rejected(self) -> None:
        with pytest.raises(InvalidInputError):
            ensure_text("", "thing")

    def test_int_rejected(self) -> None:
        with pytest.raises(InvalidInputError):
            ensure_text(1, "thing")

    def test_none_rejected(self) -> None:
        with pytest.raises(InvalidInputError):
            ensure_text(None, "thing")

    def test_bytes_rejected(self) -> None:
        with pytest.raises(InvalidInputError):
            ensure_text(b"hello", "thing")

    def test_error_carries_metadata(self) -> None:
        try:
            ensure_text(123, "date")
        except InvalidInputError as err:
            assert err.value == 123
            assert "date" in err.expected
        else:
            pytest.fail("expected InvalidInputError")


class TestSplitSign:
    def test_no_sign(self) -> None:
        assert split_sign("ABC") == (1, "ABC")

    def test_positive_sign(self) -> None:
        assert split_sign("+ABC") == (1, "ABC")

    def test_negative_sign(self) -> None:
        assert split_sign("-ABC") == (-1, "ABC")

    def test_empty_string(self) -> None:
        assert split_sign("") == (1, "")
