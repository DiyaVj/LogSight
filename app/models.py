"""
Data models for LogSight.

This module contains dataclass definitions for log entries,
analysis results, and other core data structures.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass(frozen=True)
class LogEntry:
    """
    Represents a parsed log entry with HTTP request details.

    An immutable dataclass storing log information extracted from raw log lines.
    Immutability ensures data integrity throughout processing pipelines and
    prevents accidental modifications. All fields are required and validated
    at creation time.

    Attributes:
        timestamp: The timestamp of the log entry as a string (multiple formats supported).
        ip: The client IP address in dotted decimal notation.
        method: The HTTP method (GET, POST, PUT, DELETE, PATCH, etc.).
        path: The request path/URL endpoint.
        status: The HTTP response status code (200, 404, 500, etc.) or None if missing.
        response_time_ms: The response time in milliseconds as a float.
        source: The source/origin of the log entry (service name, application, format).
    """
    timestamp: str
    ip: str
    method: str
    path: str
    status: Optional[int]
    response_time_ms: float
    source: str


# TODO: Define NormalizedLogEntry dataclass for standardized log format

# TODO: Define AnalysisResult dataclass for analysis outputs

# TODO: Define DeadLetterEntry dataclass for malformed logs
