"""
Log parsing module for LogSight.

Handles parsing of raw log lines into structured log entries.
Supports streaming processing for efficient memory usage.
"""

import json
from typing import Optional
from app.models import LogEntry


def parse_response_time(time_str: str) -> float:
    """
    Convert response time to milliseconds.

    Handles three formats:
    - "142ms": milliseconds with suffix
    - "0.089s": seconds with suffix (converted to ms)
    - "142": raw integer or float (assumed milliseconds)

    Args:
        time_str: Response time in various formats.

    Returns:
        Response time in milliseconds as float.

    Raises:
        ValueError: If the time string cannot be converted to float.
    """
    time_str = time_str.strip()
    if time_str.endswith("ms"):
        return float(time_str[:-2])
    elif time_str.endswith("s"):
        return float(time_str[:-1]) * 1000
    else:
        return float(time_str)


def parse_standard(line: str) -> Optional[LogEntry]:
    """
    Parse space-separated log formats.

    Intelligently handles variable-length timestamps (1-2 tokens based on
    colon presence) and supports missing status codes ("-"). Extra trailing
    fields are safely ignored.

    Args:
        line: Raw log line in space-separated format.

    Returns:
        LogEntry if successful, None otherwise.

    Raises:
        ValueError: Internally caught for invalid status codes or response times.
    """
    parts = line.split()
    if len(parts) < 6:
        return None

    try:
        # Determine if timestamp spans 1 or 2 tokens
        ts_end = 2 if (len(parts) > 1 and ":" in parts[1]) else 1
        timestamp = " ".join(parts[:ts_end])

        # Extract remaining fields
        rest = parts[ts_end:]
        if len(rest) < 5:
            return None

        ip = rest[0]
        method = rest[1]
        path = rest[2]
        status_str = rest[3]
        time_str = rest[4]

        status = None if status_str == "-" else int(status_str)
        response_time_ms = parse_response_time(time_str)

        return LogEntry(timestamp, ip, method, path, status, response_time_ms, "web-server")
    except (ValueError, IndexError):
        return None


def parse_json(line: str) -> Optional[LogEntry]:
    """
    Parse JSON-formatted log line.

    Validates required fields (timestamp, ip, method, path) and gracefully
    handles optional fields (status, time). Missing or non-integer status
    codes are treated as None.

    Args:
        line: Raw JSON log line.

    Returns:
        LogEntry if successful, None otherwise.

    Raises:
        json.JSONDecodeError: Internally caught for invalid JSON.
    """
    try:
        data = json.loads(line)
        timestamp = data.get("timestamp", "")
        ip = data.get("ip", "")
        method = data.get("method", "")
        path = data.get("path", "")

        if not all([timestamp, ip, method, path]):
            return None

        status = data.get("status")
        if not isinstance(status, int):
            status = None
        response_time_ms = parse_response_time(str(data.get("time", "0")))

        return LogEntry(timestamp, ip, method, path, status, response_time_ms, "json")
    except (json.JSONDecodeError, ValueError):
        return None


def parse_line(line: str) -> Optional[LogEntry]:
    """
    Parse a log line in any supported format.

    Intelligently filters out empty lines and stack traces (lines starting
    with whitespace or "at "). Attempts JSON parsing first, falling back
    to standard text formats if JSON fails.

    Args:
        line: Raw log line.

    Returns:
        LogEntry if successful, None otherwise.
    """
    line = line.strip()

    # Skip blank lines and stack traces
    if not line or line.startswith(" ") or line.startswith("at "):
        return None

    # Try JSON format first
    if line.startswith("{"):
        result = parse_json(line)
        if result:
            return result

    # Try standard text formats
    return parse_standard(line)
