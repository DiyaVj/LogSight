# LogSight - Design Decisions and Implementation Notes

## Architecture Overview

LogSight is a streaming log analyzer built with Python 3.12, designed for interview-quality code that emphasizes:
- **Separation of concerns** - Each module has a single, clear responsibility
- **Streaming efficiency** - Processes logs one at a time, minimal memory overhead
- **Type safety** - Full type hints throughout for clarity and IDE support
- **Resilience** - Graceful handling of malformed logs without pipeline disruption

## Architecture Decisions

### Modular Structure
- **models.py** - Immutable data structures (LogEntry)
- **parser.py** - Format-agnostic parsing with multi-format support
- **analyzer.py** - Stateful analysis and anomaly detection
- **dead_letter.py** - Resilient error tracking without disrupting main flow

### Streaming Processing
All core modules support streaming via generators or stateful objects:
- `parse_line()` processes one line at a time
- `LogAnalyzer` maintains state, accumulating statistics as entries arrive
- `DeadLetterWriter` appends failures without loading entire dataset

### Response Time Handling
Consolidated `parse_response_time()` function supports three formats:
- Milliseconds: "142ms"
- Seconds: "0.089s" (converted to ms)
- Raw integer/float: "142"

### Timestamp Flexibility
Parser intelligently detects variable-length timestamps (1-2 tokens) by checking for colons, supporting:
- ISO 8601: "2024-03-15T14:23:01Z"
- Slash-date: "2024/03/15 14:23:01"
- Dash-date: "15-Mar-2024 14:23:01"
- Unix epoch: "1710512581"

### Error Handling
- **Parser**: Returns None for any malformed line, never raises
- **Dead Letter Writer**: All I/O exceptions silently ignored to prevent parser crashes
- **Main**: File validation and error reporting to stderr with proper exit codes

### Separation of Concerns
- No business logic in CLI (main.py) - purely orchestration
- No data validation/transformation in models - LogEntry is pure data
- No file I/O in parsing - parse_line() takes string input
- No analysis in parsing - clear pipeline: parse → analyze → report

## Code Quality

### Type Hints
- Complete type hints on all public functions and methods
- Specific return types (list[tuple[str, float]] vs list[tuple])
- Union types for optional status codes (int | None)

### Naming Conventions
- Private functions prefixed with underscore (_calculate_slow_endpoints)
- Consistent naming: `parse_*` for parsing, `generate_*` for generation
- Descriptive variable names: endpoint_times, status_counts, response_time_ms

### Function Size
- All functions kept under 30 lines for readability
- Single responsibility per function
- Helper functions extracted to avoid duplication

### Docstrings
- Google-style docstrings with Args, Returns, Raises sections
- Clear description of behavior and edge cases
- Examples of supported formats documented

## Testing Strategy

Unit tests cover:
- Valid parsing in all formats (standard, JSON, alternate timestamps)
- Edge cases (blank lines, malformed JSON, invalid status codes)
- Response time conversion (ms, seconds, raw integers)
- Immutability verification of LogEntry
- Dead letter writing resilience

## Performance Characteristics

- **Memory**: O(unique endpoints + unique status codes) = constant space per log regardless of file size
- **Time**: O(n) single pass through logs
- **I/O**: Single file read, optional dead letter write
- **Scaling**: Efficient up to millions of logs per file

## Future Extensibility

Without redesign, can easily add:
- Additional timestamp formats (parse_standard handles flexible detection)
- New log sources via parse_* functions
- Additional anomaly thresholds (configurable constants in _detect_anomalies)
- Batch processing via new generator-based parse_stream() function
