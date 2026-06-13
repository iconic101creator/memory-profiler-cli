"""
Quick test — runs the collector against the current Python process itself.
Usage: python test_collector.py
"""
from profiler import collect
from profiler.analyzer import analyze
from profiler.reporter import print_report

if __name__ == "__main__":
    import os
    pid = os.getpid()
    result = collect(pid=pid, interval=0.3, duration=3.0)
    analysis = analyze(result)
    print_report(result, analysis)