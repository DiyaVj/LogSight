"""
Log analysis module for LogSight.

Performs analysis on log entries including pattern detection,
anomaly identification, and statistical insights.
"""

from collections import Counter
from dataclasses import dataclass, field
from app.models import LogEntry


def _calculate_slow_endpoints(
    endpoint_times: dict[str, list[float]],
) -> list[tuple[str, float]]:
    """
    Calculate average response time per endpoint.

    Args:
        endpoint_times: Dict mapping endpoint paths to lists of response times.

    Returns:
        List of (endpoint, avg_time) tuples sorted by avg time descending.
    """
    slow = []
    for endpoint, times in endpoint_times.items():
        if times:
            avg = sum(times) / len(times)
            slow.append((endpoint, avg))
    return sorted(slow, key=lambda x: x[1], reverse=True)


def _detect_anomalies(
    status_counts: Counter, missing_count: int, total_valid: int
) -> list[str]:
    """
    Detect anomalies in log data.

    Args:
        status_counts: Counter of HTTP status codes.
        missing_count: Count of entries with missing status.
        total_valid: Total valid log entries.

    Returns:
        List of anomaly descriptions.
    """
    anomalies = []
    if total_valid == 0:
        return anomalies

    # Check for high error rate (4xx, 5xx)
    error_count = sum(c for status, c in status_counts.items() if status >= 400)
    total_with_status = sum(status_counts.values())
    if total_with_status > 0:
        error_rate = error_count / total_with_status * 100
        if error_rate > 10:
            anomalies.append(f"High error rate: {error_rate:.1f}%")

    # Check for high missing status rate
    if missing_count > 0:
        missing_rate = missing_count / total_valid * 100
        if missing_rate > 5:
            anomalies.append(f"High missing status rate: {missing_rate:.1f}%")

    return anomalies


@dataclass
class LogAnalyzer:
    """
    Analyzes log entries in streaming fashion.

    Maintains stateful counters and collections for frequency analysis,
    status code distribution, and response time tracking. Detects anomalies
    based on configurable thresholds. Designed for memory-efficient
    processing of logs one entry at a time.
    """

    total_lines: int = 0
    valid_lines: int = 0
    malformed_lines: int = 0
    json_lines: int = 0
    missing_status_count: int = 0

    endpoint_freq: Counter = field(default_factory=Counter)
    status_counts: Counter = field(default_factory=Counter)
    endpoint_times: dict[str, list[float]] = field(default_factory=dict)

    def add(self, entry: LogEntry) -> None:
        """
        Record a successfully parsed log entry.

        Tracks endpoint frequency, status codes, and response times.

        Args:
            entry: Parsed LogEntry to analyze.
        """
        self.total_lines += 1
        self.valid_lines += 1

        # Track endpoint frequency
        self.endpoint_freq[entry.path] += 1

        # Track status codes
        if entry.status is None:
            self.missing_status_count += 1
        else:
            self.status_counts[entry.status] += 1

        # Track response times per endpoint
        if entry.path not in self.endpoint_times:
            self.endpoint_times[entry.path] = []
        self.endpoint_times[entry.path].append(entry.response_time_ms)

    def record_malformed(self) -> None:
        """Record a malformed log line that failed parsing."""
        self.total_lines += 1
        self.malformed_lines += 1

    def generate_report(self) -> str:
        """
        Generate a formatted analysis report.

        Produces a multi-section report including summary statistics,
        top endpoints, status code distribution, slow endpoints,
        and detected anomalies.

        Returns:
            Multi-line report string with statistics and anomalies.
        """
        lines = []

        # Summary
        lines.append("Processed: " + str(self.total_lines))
        lines.append("Valid: " + str(self.valid_lines))
        lines.append("Malformed: " + str(self.malformed_lines))
        lines.append("")

        # Top endpoints
        lines.append("Top Endpoints:")
        for endpoint, count in self.endpoint_freq.most_common(5):
            lines.append(f"  {endpoint}: {count}")
        lines.append("")

        # Status summary
        lines.append("Status Summary:")
        for status in sorted(self.status_counts.keys()):
            count = self.status_counts[status]
            lines.append(f"  {status}: {count}")
        if self.missing_status_count > 0:
            lines.append(f"  Missing: {self.missing_status_count}")
        lines.append("")

        # Slow endpoints
        slow_endpoints = _calculate_slow_endpoints(self.endpoint_times)
        if slow_endpoints:
            lines.append("Slow Endpoints (avg response time):")
            for endpoint, avg_time in slow_endpoints[:5]:
                lines.append(f"  {endpoint}: {avg_time:.2f}ms")
            lines.append("")

        # Anomalies
        anomalies = _detect_anomalies(
            self.status_counts, self.missing_status_count, self.valid_lines
        )
        lines.append("Anomalies:")
        if anomalies:
            for anomaly in anomalies:
                lines.append(f"  {anomaly}")
        else:
            lines.append("  None detected")

        return "\n".join(lines)
