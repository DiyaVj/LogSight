"""
Sample log generation utility for LogSight.

Generates sample log files in various formats for testing and development.
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


# Configuration
ENDPOINTS = ["/api/users", "/api/posts", "/api/comments", "/health", "/login", "/logout", "/api/search", "/download"]
METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
STATUS_CODES = [200, 201, 204, 400, 401, 403, 404, 500, 502, 503]
STACK_TRACES = [
    "  at Object.<anonymous> (/app/index.js:42:10)",
    "  at Module._load (internal/modules/cjs/loader.js:936:1)",
    "  at Function.Module._load (internal/modules/cjs/loader.js:936:1)",
]


def random_ip() -> str:
    """Generate random IPv4 address."""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"


def _random_past_datetime() -> datetime:
    """Generate a random datetime in the past 72 hours."""
    return datetime.now() - timedelta(hours=random.randint(0, 72))


def random_timestamp_iso() -> str:
    """Generate ISO 8601 timestamp."""
    return _random_past_datetime().isoformat(timespec="seconds") + "Z"


def random_timestamp_slash() -> str:
    """Generate slash-date timestamp format (YYYY/MM/DD HH:MM:SS)."""
    return _random_past_datetime().strftime("%Y/%m/%d %H:%M:%S")


def random_timestamp_dash() -> str:
    """Generate dash-date timestamp format (DD-Mon-YYYY HH:MM:SS)."""
    return _random_past_datetime().strftime("%d-%b-%Y %H:%M:%S")


def random_response_time() -> str:
    """
    Generate random response time in various formats.

    Randomly selects between milliseconds ("142ms"), seconds ("1.5s"),
    or raw integer ("142") formats to simulate real-world variation.

    Returns:
        Response time string in one of three formats.
    """
    value = random.randint(10, 5000)
    choice = random.choice(["ms", "s", "raw"])
    if choice == "ms":
        return f"{value}ms"
    elif choice == "s":
        return f"{value / 1000:.3f}s"
    else:
        return str(value)


def generate_standard_log() -> str:
    """
    Generate standard format log line.

    Produces space-separated format with ISO timestamp, IP, method, endpoint,
    status, and response time. Includes 5% chance of missing status and
    10% chance of extra trailing fields.

    Returns:
        Standard format log line.
    """
    timestamp = random_timestamp_iso()
    ip = random_ip()
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status = random.choice(STATUS_CODES) if random.random() > 0.05 else "-"
    response_time = random_response_time()

    # 10% chance of extra trailing fields
    extra = " extra_field=value" if random.random() < 0.1 else ""
    return f"{timestamp} {ip} {method} {endpoint} {status} {response_time}{extra}"


def generate_json_log() -> str:
    """
    Generate JSON format log line.

    Produces a JSON log entry with all standard fields including optional
    status (which may be null). Includes 5% chance of null status.

    Returns:
        JSON-formatted log line.
    """
    entry = {
        "timestamp": random_timestamp_iso(),
        "ip": random_ip(),
        "method": random.choice(METHODS),
        "path": random.choice(ENDPOINTS),
        "status": random.choice(STATUS_CODES) if random.random() > 0.05 else None,
        "time": random_response_time(),
    }
    return json.dumps(entry)


def generate_alternate_timestamp_log() -> str:
    """
    Generate log with alternate timestamp format.

    Uses either slash-date or dash-date formats instead of ISO 8601,
    simulating logs from different sources or legacy systems.

    Returns:
        Standard format log line with alternate timestamp.
    """
    choice = random.choice([random_timestamp_slash, random_timestamp_dash])
    timestamp = choice()
    ip = random_ip()
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status = random.choice(STATUS_CODES) if random.random() > 0.05 else "-"
    response_time = random_response_time()
    return f"{timestamp} {ip} {method} {endpoint} {status} {response_time}"


def generate_malformed_log() -> str:
    """
    Generate intentionally malformed log entry.

    Produces one of four malformed types: incomplete line, stack trace,
    garbage text, or blank line. Used to test parser resilience and
    error handling.

    Returns:
        Malformed log line or blank string.
    """
    choice = random.randint(1, 4)
    if choice == 1:
        # Incomplete line
        return f"{random_ip()} {random.choice(METHODS)}"
    elif choice == 2:
        # Stack trace
        return random.choice(STACK_TRACES)
    elif choice == 3:
        # Garbage text
        return "ERROR: corrupted data @@## $%^& invalid format"
    else:
        # Blank line
        return ""


def generate_log_line() -> str:
    """
    Generate a single log line with realistic distribution.

    Distribution (by format):
    - 70% standard format
    - 10% JSON format
    - 10% alternate timestamp format
    - 10% malformed (invalid/problematic)

    Returns:
        Randomly selected log line from available formats.
    """
    rand = random.random()
    if rand < 0.7:
        return generate_standard_log()
    elif rand < 0.8:
        return generate_json_log()
    elif rand < 0.9:
        return generate_alternate_timestamp_log()
    else:
        return generate_malformed_log()


def generate_logs(count: int, output_file: str) -> None:
    """
    Generate log file with specified number of lines.

    Creates parent directories as needed and writes log lines to the
    specified file. Each line is generated independently.

    Args:
        count: Number of log lines to generate.
        output_file: Path to write logs to.

    Raises:
        OSError: If unable to create directories or write to file.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for _ in range(count):
            line = generate_log_line()
            f.write(line + "\n")


def main() -> None:
    """
    Main entry point for log generator CLI.

    Parses command-line arguments and generates a log file with the
    specified number of lines in various formats for testing LogSight.
    """
    parser = argparse.ArgumentParser(description="Generate sample logs for LogSight")
    parser.add_argument("--lines", type=int, default=1000, help="Number of log lines to generate (default: 1000)")
    parser.add_argument("--output", type=str, default="sample_logs/generated.log", help="Output file path")
    args = parser.parse_args()

    if args.lines < 1:
        print("Error: --lines must be at least 1")
        return

    generate_logs(args.lines, args.output)
    print(f"Generated {args.lines} log lines to {args.output}")


if __name__ == "__main__":
    main()
