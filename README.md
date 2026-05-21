# LogSight

A streaming log analysis and processing tool built with Python 3.12. Analyzes HTTP logs efficiently with minimal memory overhead, perfect for processing large log files.

## Features

- **Streaming Processing** - Processes logs line-by-line, not loading entire files into memory
- **Multi-Format Support** - Parses JSON, space-separated, and various timestamp formats
- **Resilient Parsing** - Gracefully handles malformed logs without crashing
- **Real-Time Analytics** - Generates statistics on endpoints, status codes, and response times
- **Anomaly Detection** - Identifies high error rates and missing status patterns
- **Dead Letter Tracking** - Records malformed logs for later inspection
- **CLI Interface** - Simple command-line usage with no external dependencies
- **Type-Safe** - Full type hints for code quality and IDE support
- **Comprehensive Tests** - 23+ unit tests covering all parsing scenarios

## Supported Log Formats

1. **Standard Format** - Space-separated with ISO timestamps
   ```
   2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms
   ```

2. **Alternate Timestamps** - Slash-date or dash-date formats
   ```
   2024/03/15 14:23:01 192.168.1.42 GET /users 200 142ms
   15-Mar-2024 14:23:01 192.168.1.42 POST /login 401 0.089s
   ```

3. **JSON Format** - Structured JSON logs
   ```json
   {"timestamp":"2024-03-15T14:23:01Z","ip":"1.1.1.1","method":"GET","path":"/users","status":200,"time":"142ms"}
   ```

4. **Flexible Response Times** - Milliseconds, seconds, or raw integers
   - `142ms` → 142 ms
   - `0.089s` → 89 ms
   - `142` → 142 ms

5. **Missing Status Codes** - Handles `-` as missing status

## Requirements

- Python 3.12+
- No external dependencies for core functionality
- pytest (optional, for testing)

## Installation

```bash
# Clone and install
git clone https://github.com/DiyaVj/LogSight.git
cd LogSight

# Install dependencies (testing)
pip install -r requirements.txt
```

## Quick Start

### 1. Generate Sample Logs
```bash
# Generate 1000 sample logs
python scripts/generate_logs.py

# Custom amount and location
python scripts/generate_logs.py --lines 10000 --output my_logs.log
```

### 2. Analyze Logs
```bash
# Analyze generated logs
python main.py sample_logs/generated.log
```

### Sample Output
```
Processed: 1000
Valid: 890
Malformed: 110

Top Endpoints:
  /api/users: 245
  /health: 189
  /logout: 156
  /api/search: 145
  /download: 155

Status Summary:
  200: 450
  201: 89
  204: 102
  400: 54
  401: 78
  404: 89
  500: 28

Slow Endpoints (avg response time):
  /api/search: 2145.32ms
  /api/users: 1856.74ms
  /download: 1542.19ms

Anomalies:
  High error rate: 15.2%
```

## Project Structure

```
logsight/
├── main.py                      # CLI entry point
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── ANSWERS.md                   # Architecture & design decisions
│
├── app/                         # Core application
│   ├── __init__.py
│   ├── models.py               # LogEntry dataclass
│   ├── parser.py               # Multi-format log parsing
│   ├── analyzer.py             # Streaming statistics & analysis
│   ├── dead_letter.py          # Malformed log tracking
│   └── normalizer.py           # (Future: log normalization)
│
├── scripts/                     # Utilities
│   └── generate_logs.py        # Sample log generation
│
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_parser.py          # Parser unit tests (23 tests)
│
└── sample_logs/                # Generated logs directory
```

## Architecture Highlights

### Separation of Concerns
- **Parser** (`parser.py`) - Only parsing, no analysis
- **Analyzer** (`analyzer.py`) - Only analysis, no I/O
- **DeadLetterWriter** (`dead_letter.py`) - Single responsibility
- **Main** (`main.py`) - Pure orchestration, no business logic

### Streaming Design
```python
# Process logs without loading entire file into memory
with open(logfile) as f:
    for line_num, line in enumerate(f, start=1):
        entry = parse_line(line)  # Returns LogEntry or None
        if entry:
            analyzer.add(entry)    # Accumulate statistics
        else:
            dead_letter_writer.write_entry(line_num, "parse_failed", line)
```

### Error Resilience
- Dead letter writer catches all exceptions silently
- Parser never crashes on malformed input
- Main application continues even with file I/O issues

## Testing

Run the comprehensive test suite:

```bash
# All tests
pytest tests/ -v

# Specific test class
pytest tests/test_parser.py::TestParseStandardLog -v

# With coverage
pytest tests/ --cov=app
```

**Test Coverage:**
- Response time format conversions (4 tests)
- Standard log parsing (6 tests)
- JSON log parsing (4 tests)
- Error handling & edge cases (7 tests)
- LogEntry immutability (2 tests)

All 23 tests pass ✓

## Performance

- **Memory**: O(unique endpoints + unique status codes) - constant space regardless of log size
- **Time**: O(n) single pass through logs
- **Typical Load**: 100,000+ logs per second on modern hardware

## Usage Examples

### Analyze a Large Log File
```bash
python main.py /var/log/nginx/access.log
```

### Generate and Analyze Test Data
```bash
python scripts/generate_logs.py --lines 50000 --output large_test.log
python main.py large_test.log
```

### Inspect Failed Logs
```bash
cat dead_letter.log | python -m json.tool
```

## Configuration

Configuration options in generator:

```python
# scripts/generate_logs.py
ENDPOINTS = ["/api/users", "/api/posts", ...]  # Modify to add/remove endpoints
METHODS = ["GET", "POST", "PUT", "DELETE"]     # Modify HTTP methods
STATUS_CODES = [200, 404, 500, ...]            # Modify status codes
STACK_TRACES = [...]                           # Modify malformed traces
```

Anomaly thresholds in analyzer:

```python
# app/analyzer.py - _detect_anomalies()
error_rate > 10     # High error rate threshold (4xx, 5xx)
missing_rate > 5    # High missing status rate threshold
```

## Design Philosophy

LogSight prioritizes:
1. **Simplicity** - Pure Python, no frameworks
2. **Type Safety** - Complete type hints
3. **Resilience** - Handles edge cases gracefully
4. **Efficiency** - Streaming processing for large files
5. **Clarity** - Well-documented code and clear architecture

See [ANSWERS.md](ANSWERS.md) for detailed architecture documentation.

## Development

### Adding New Log Formats
1. Create parser function in `app/parser.py`
2. Add test cases in `tests/test_parser.py`
3. Update `parse_line()` dispatcher to call new parser

### Adding New Analytics
1. Add tracking fields to `LogAnalyzer` dataclass
2. Implement analysis logic in instance methods
3. Update `generate_report()` to include new metrics

## License

MIT

## Author

Built for interview demonstration of clean code principles and software engineering best practices.
