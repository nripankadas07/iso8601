# iso8601

Strict ISO-8601 date, time, datetime and duration parser for Python.
Zero dependencies, fully type-annotated, round-trips between strings and
the standard-library `datetime` types.

## Features

- Calendar dates: `YYYY-MM-DD` and `YYYYMMDD`
- Ordinal dates: `YYYY-DDD` and `YYYYDDD`
- Week dates: `YYYY-Www-D` and `YYYYWwwD`
- Times with optional fractional seconds and timezone designators
  (`Z`, `±HH`, `±HHMM`, `±HH:MM`)
- Combined `<date>T<time>` datetimes; mixing basic and extended forms is
  rejected
- Durations: `P3Y6M4DT12H30M5S`, `P1W`, `-PT0.5S`, with fractional seconds
- Fully type-annotated, ships `py.typed`
- 100% line + branch coverage, `mypy --strict` clean

## Install

```bash
pip install iso8601
```

## Usage

```python
import iso8601

# Dates
iso8601.parse_date("2026-05-13")          # date(2026, 5, 13)
iso8601.parse_date("20260513")            # date(2026, 5, 13)
iso8601.parse_date("2026-W20-3")          # date(2026, 5, 13)
iso8601.parse_date("2026-133")            # date(2026, 5, 13) ordinal

# Times — Z, ±HH:MM, ±HHMM, ±HH all accepted
iso8601.parse_time("09:30:45.250Z")
iso8601.parse_time("093045+0530")

# Combined datetimes
iso8601.parse_datetime("2026-05-13T09:30:00Z")
iso8601.parse_datetime("2026-05-13 09:30:00")   # space separator too

# Durations
iso8601.parse_duration("P3Y6M4DT12H30M5S")
iso8601.parse_duration("PT1H30M").to_timedelta()  # ↔ datetime.timedelta
iso8601.parse_duration("-PT30M")                  # negative

# Round-trip
iso8601.format_datetime(iso8601.parse_datetime("2026-05-13T09:30:00Z"))
# '2026-05-13T09:30:00Z'
```

## API reference

### Dates

- `parse_date(text: str) -> datetime.date` — parse any ISO-8601 date.
- `format_date(value: datetime.date, *, basic: bool = False) -> str`

### Times

- `parse_time(text: str) -> datetime.time` — fractional seconds and
  timezone designators are honoured.
- `format_time(value: datetime.time, *, basic: bool = False) -> str`

### Datetimes

- `parse_datetime(text: str) -> datetime.datetime`
- `format_datetime(value: datetime.datetime, *, basic: bool = False) -> str`

### Durations

- `parse_duration(text: str) -> Duration`
- `format_duration(duration: Duration) -> str`
- `Duration(years=0, months=0, weeks=0, days=0, hours=0, minutes=0,
   seconds=0, microseconds=0, negative=False)` — immutable dataclass.
  Methods: `.to_timedelta()`, `.is_zero()`.

### Errors

- `Iso8601Error` — base class.
- `ParseError` — string is not valid ISO-8601 (carries `.text`, `.kind`).
- `InvalidInputError` — argument is the wrong type or empty.

## Running tests

```bash
pip install pytest pytest-cov mypy
pytest --cov=iso8601 --cov-branch --cov-fail-under=100
mypy --strict src/iso8601
```

## License

MIT — see [LICENSE](LICENSE).
