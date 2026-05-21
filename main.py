"""
LogSight: A streaming log analysis and processing tool.

This is the main entry point for the LogSight CLI application.
It orchestrates log parsing, normalization, and analysis.
"""

import argparse
import sys
from pathlib import Path
from app.parser import parse_line
from app.analyzer import LogAnalyzer
from app.dead_letter import DeadLetterWriter


def main() -> None:
    """
    Main entry point for LogSight CLI.

    Processes a log file line-by-line in streaming mode, parsing valid entries,
    recording malformed lines, and generating a comprehensive analysis report.
    Dead letter entries are written to dead_letter.log for later inspection.
    """
    parser = argparse.ArgumentParser(description="LogSight: Stream log analyzer")
    parser.add_argument("logfile", help="Path to log file to analyze")
    args = parser.parse_args()

    # Validate file exists
    logfile_path = Path(args.logfile)
    if not logfile_path.exists():
        print(f"Error: File not found: {args.logfile}", file=sys.stderr)
        sys.exit(1)

    if not logfile_path.is_file():
        print(f"Error: Not a file: {args.logfile}", file=sys.stderr)
        sys.exit(1)

    # Initialize components
    analyzer = LogAnalyzer()
    dead_letter_writer = DeadLetterWriter("dead_letter.log")

    # Process file in streaming mode
    try:
        with open(logfile_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                entry = parse_line(line)
                if entry:
                    analyzer.add(entry)
                else:
                    analyzer.record_malformed()
                    dead_letter_writer.write_entry(line_num, "parse_failed", line.strip())
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Print report
    print(analyzer.generate_report())


if __name__ == "__main__":
    main()
