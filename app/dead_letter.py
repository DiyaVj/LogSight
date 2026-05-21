"""
Dead letter queue handling for LogSight.

Manages logs that cannot be processed or parsed correctly.
Provides tracking and reporting of malformed/problematic logs.
"""

import json


class DeadLetterWriter:
    """
    Writes unparseable log entries to a dead letter file.

    Stores entries as JSON lines with line number, failure reason, and
    original content. All file I/O operations are exception-safe to ensure
    parsing failures never crash the main processing pipeline.
    """

    def __init__(self, filepath: str = "dead_letter.log") -> None:
        """
        Initialize DeadLetterWriter.

        Args:
            filepath: Path to dead letter log file (default: dead_letter.log).
        """
        self.filepath = filepath

    def write_entry(self, line_num: int, reason: str, content: str) -> None:
        """
        Write a failed log entry to dead letter file.

        Appends entry as JSON line. Silently handles all exceptions
        to prevent parser crashes.

        Args:
            line_num: Line number in original log file.
            reason: Failure reason (e.g., "parse_failed", "validation_error").
            content: Raw log line content.
        """
        try:
            entry = {"line": line_num, "reason": reason, "content": content}
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            # Silently ignore all exceptions to prevent parser disruption
            pass

    def write_batch(self, entries: list[dict[str, int | str]]) -> None:
        """
        Write multiple dead letter entries efficiently.

        Batch writes are more efficient for processing large sets
        of dead letter entries at once. Silently handles exceptions
        to prevent parser disruption.

        Args:
            entries: List of dicts with keys: line (int), reason (str), content (str).
        """
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")
        except Exception:
            # Silently ignore all exceptions
            pass
