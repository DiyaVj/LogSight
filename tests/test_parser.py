"""
Unit tests for the parser module.

Tests parsing of various log formats and error handling.
"""

import pytest
from app.parser import parse_line, parse_response_time
from app.models import LogEntry


class TestParseResponseTime:
    """Tests for response time parsing."""

    def test_milliseconds(self) -> None:
        """Test parsing milliseconds format."""
        assert parse_response_time("142ms") == 142.0

    def test_seconds_conversion(self) -> None:
        """Test parsing seconds and converting to milliseconds."""
        assert parse_response_time("0.089s") == 89.0
        assert parse_response_time("1.5s") == 1500.0

    def test_raw_integer(self) -> None:
        """Test parsing raw integer as milliseconds."""
        assert parse_response_time("142") == 142.0

    def test_raw_float(self) -> None:
        """Test parsing raw float."""
        assert parse_response_time("142.5") == 142.5


class TestParseStandardLog:
    """Tests for standard format log parsing."""

    def test_valid_standard_log(self) -> None:
        """Test parsing valid standard format log."""
        line = "2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms"
        entry = parse_line(line)
        assert entry is not None
        assert entry.timestamp == "2024-03-15T14:23:01Z"
        assert entry.ip == "192.168.1.42"
        assert entry.method == "GET"
        assert entry.path == "/api/users"
        assert entry.status == 200
        assert entry.response_time_ms == 142.0

    def test_slash_date_format(self) -> None:
        """Test parsing slash-date timestamp format."""
        line = "2024/03/15 14:23:01 192.168.1.42 GET /users 200 142ms"
        entry = parse_line(line)
        assert entry is not None
        assert entry.timestamp == "2024/03/15 14:23:01"
        assert entry.status == 200

    def test_dash_date_format(self) -> None:
        """Test parsing dash-date timestamp format."""
        line = "15-Mar-2024 14:23:01 192.168.1.42 POST /login 401 0.089s"
        entry = parse_line(line)
        assert entry is not None
        assert entry.timestamp == "15-Mar-2024 14:23:01"
        assert entry.method == "POST"
        assert entry.status == 401
        assert entry.response_time_ms == 89.0

    def test_missing_status_code(self) -> None:
        """Test parsing log with missing status code (-)."""
        line = "2024-03-15T14:23:01Z 192.168.1.42 GET /health - 142ms"
        entry = parse_line(line)
        assert entry is not None
        assert entry.status is None
        assert entry.response_time_ms == 142.0

    def test_extra_trailing_fields(self) -> None:
        """Test parsing log with extra trailing fields."""
        line = "2024-03-15T14:23:01Z 192.168.1.42 GET /api 200 142ms extra=value foo=bar"
        entry = parse_line(line)
        assert entry is not None
        assert entry.status == 200

    def test_raw_integer_time(self) -> None:
        """Test parsing response time as raw integer."""
        line = "1710512581 192.168.1.42 GET /health 200 142"
        entry = parse_line(line)
        assert entry is not None
        assert entry.timestamp == "1710512581"
        assert entry.response_time_ms == 142.0


class TestParseJsonLog:
    """Tests for JSON format log parsing."""

    def test_valid_json_log(self) -> None:
        """Test parsing valid JSON format log."""
        line = '{"timestamp":"2024-03-15T14:23:01Z","ip":"1.1.1.1","method":"GET","path":"/users","status":200,"time":"142ms"}'
        entry = parse_line(line)
        assert entry is not None
        assert entry.timestamp == "2024-03-15T14:23:01Z"
        assert entry.ip == "1.1.1.1"
        assert entry.method == "GET"
        assert entry.path == "/users"
        assert entry.status == 200
        assert entry.response_time_ms == 142.0

    def test_json_missing_status(self) -> None:
        """Test parsing JSON with missing status field."""
        line = '{"timestamp":"2024-03-15T14:23:01Z","ip":"1.1.1.1","method":"GET","path":"/users","time":"142ms"}'
        entry = parse_line(line)
        assert entry is not None
        assert entry.status is None

    def test_json_null_status(self) -> None:
        """Test parsing JSON with null status."""
        line = '{"timestamp":"2024-03-15T14:23:01Z","ip":"1.1.1.1","method":"GET","path":"/users","status":null,"time":"142ms"}'
        entry = parse_line(line)
        assert entry is not None
        assert entry.status is None

    def test_json_with_seconds(self) -> None:
        """Test parsing JSON with response time in seconds."""
        line = '{"timestamp":"2024-03-15T14:23:01Z","ip":"1.1.1.1","method":"POST","path":"/login","status":401,"time":"0.089s"}'
        entry = parse_line(line)
        assert entry is not None
        assert entry.response_time_ms == 89.0


class TestParseErrorHandling:
    """Tests for error handling and edge cases."""

    def test_blank_line(self) -> None:
        """Test parsing blank line returns None."""
        assert parse_line("") is None
        assert parse_line("   ") is None

    def test_malformed_line(self) -> None:
        """Test parsing completely malformed line."""
        assert parse_line("garbage data here") is None
        assert parse_line("just two fields") is None

    def test_stack_trace_line(self) -> None:
        """Test parsing stack trace line returns None."""
        assert parse_line("  at Object.<anonymous> (/app/index.js:42:10)") is None
        assert parse_line("    at Module._load (internal/modules/cjs/loader.js:936:1)") is None

    def test_malformed_json(self) -> None:
        """Test parsing malformed JSON returns None."""
        assert parse_line('{"invalid json}') is None
        assert parse_line('{"timestamp":"2024"}') is None  # Missing required fields

    def test_incomplete_standard_log(self) -> None:
        """Test parsing incomplete standard format."""
        assert parse_line("2024-03-15T14:23:01Z 192.168.1.42") is None
        assert parse_line("192.168.1.42 GET /users") is None

    def test_invalid_status_code(self) -> None:
        """Test parsing invalid status code format."""
        line = "2024-03-15T14:23:01Z 192.168.1.42 GET /api invalid_status 142ms"
        assert parse_line(line) is None

    def test_invalid_response_time(self) -> None:
        """Test parsing invalid response time format."""
        line = "2024-03-15T14:23:01Z 192.168.1.42 GET /api 200 invalid_time"
        assert parse_line(line) is None


class TestParseLogEntry:
    """Tests for LogEntry dataclass creation."""

    def test_log_entry_immutable(self) -> None:
        """Test that LogEntry is immutable."""
        line = "2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms"
        entry = parse_line(line)
        assert entry is not None

        with pytest.raises(AttributeError):
            entry.status = 404  # type: ignore

    def test_log_entry_all_fields(self) -> None:
        """Test LogEntry contains all required fields."""
        line = "2024-03-15T14:23:01Z 192.168.1.42 POST /api/login 401 0.5s"
        entry = parse_line(line)
        assert entry is not None

        # Verify all fields are present and correct
        assert isinstance(entry.timestamp, str)
        assert isinstance(entry.ip, str)
        assert isinstance(entry.method, str)
        assert isinstance(entry.path, str)
        assert entry.status is not None
        assert isinstance(entry.response_time_ms, float)
        assert isinstance(entry.source, str)
