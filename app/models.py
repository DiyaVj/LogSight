"""
Data models for LogSight.

This module contains dataclass definitions for log entries,
analysis results, and other core data structures.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

# TODO: Define LogEntry dataclass with fields:
#       - timestamp: datetime
#       - level: str (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#       - source: str (application/service name)
#       - message: str
#       - metadata: dict[str, Any]

# TODO: Define NormalizedLogEntry dataclass for standardized log format

# TODO: Define AnalysisResult dataclass for analysis outputs

# TODO: Define DeadLetterEntry dataclass for malformed logs

# TODO: Add type hints throughout
# TODO: Add docstrings for each dataclass
