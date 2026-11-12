"""Run diagnostics from stdin or a local traceback file."""
import argparse
import json
import sys
from pathlib import Path

from .diagnostics import MAX_INPUT, diagnose


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline debugging guidance, no API keys or network requests")
    parser.add_argument("path", nargs="?", help="Plain-text traceback file (default: stdin)")
    parser.add_argument("--json", action="store_true", help="Machine-readable diagnostic")
    args = parser.parse_args()
    try:
        if args.path:
            file = Path(args.path).expanduser()
            if file.stat().st_size > MAX_INPUT * 4:
                raise ValueError("Input file too large")
            text = file.read_text(encoding="utf-8")
        else:
            text = sys.stdin.read(MAX_INPUT + 1)
        result = diagnose(text)
    except (ValueError, OSError, UnicodeError) as error:
        print(f"Unable to analyze input: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"{result.title} ({result.category})")
        if result.line_number is not None:
            print(f"Likely line: {result.line_number}")
        print(result.explanation)
        print(f"Evidence: {result.matched_line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
