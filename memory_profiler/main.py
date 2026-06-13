"""
memory-profiler-cli
-------------------
Attach to a running process and profile its memory usage.

Usage:
    python main.py --pid <PID> [--interval <seconds>] [--duration <seconds>]

Examples:
    python main.py --pid 1234
    python main.py --pid 1234 --interval 0.5 --duration 60
"""
import argparse
import sys

from profiler import collect
from profiler.analyzer import analyze
from profiler.reporter import print_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="memory-profiler",
        description="Profile memory usage of a running process.",
    )
    parser.add_argument(
        "--pid", "-p",
        type=int,
        required=True,
        help="PID of the process to profile",
    )
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=0.5,
        help="Seconds between samples (default: 0.5)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=10.0,
        help="Total profiling duration in seconds (default: 10)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        result = collect(pid=args.pid, interval=args.interval, duration=args.duration)
    except ValueError as e:
        print(f"\n[error] {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"\n[error] {e}", file=sys.stderr)
        sys.exit(1)

    if not result.samples:
        print("\n[error] No samples were collected. The process may have exited immediately.", file=sys.stderr)
        sys.exit(1)

    analysis = analyze(result)
    print_report(result, analysis)


if __name__ == "__main__":
    main()