# LogSight

A streaming log analysis and processing tool built with Python 3.12.

## Features

- Streaming log processing
- Log parsing and normalization
- Log analysis and pattern detection
- Dead letter handling for malformed logs
- CLI-based interface

## Requirements

- Python 3.12+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py [options] <log_file>
```

## Project Structure

- `app/` - Core application modules
  - `models.py` - Data models and dataclasses
  - `parser.py` - Log parsing logic
  - `analyzer.py` - Log analysis logic
  - `normalizer.py` - Log normalization logic
  - `dead_letter.py` - Dead letter queue handling

- `scripts/` - Utility scripts
  - `generate_logs.py` - Sample log generation

- `tests/` - Test suite
  - `test_parser.py` - Parser tests

- `sample_logs/` - Sample log files for testing

## TODO

- [ ] Implement core functionality
- [ ] Add comprehensive tests
- [ ] Add documentation
