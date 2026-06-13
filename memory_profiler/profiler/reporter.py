from .analyzer import AnalysisResult
from .collector import CollectionResult


# ── Terminal width ────────────────────────────────────────────────────────────
WIDTH = 60


def _bar(value: float, max_value: float, width: int = 30) -> str:
    """Return a filled ASCII progress bar."""
    filled = int((value / max_value) * width) if max_value > 0 else 0
    return "█" * filled + "░" * (width - filled)


def _divider(char: str = "─") -> str:
    return char * WIDTH


def print_report(result: CollectionResult, analysis: AnalysisResult) -> None:
    """
    Print a formatted report to the terminal:
      - Summary table
      - RSS over time ASCII chart
    """
    samples = result.samples
    peak = analysis.rss_peak_mb

    # ── Header ────────────────────────────────────────────────────────────────
    print()
    print(_divider("═"))
    print(f"  MEMORY PROFILE REPORT")
    print(f"  Process : {analysis.process_name}  (PID {analysis.pid})")
    print(f"  Duration: {analysis.duration_s}s   Samples: {analysis.sample_count}")
    print(_divider("═"))

    # ── Stats table ───────────────────────────────────────────────────────────
    print()
    rows = [
        ("Peak RSS",    f"{analysis.rss_peak_mb:.3f} MB"),
        ("Avg RSS",     f"{analysis.rss_avg_mb:.3f} MB"),
        ("Start RSS",   f"{analysis.rss_start_mb:.3f} MB"),
        ("End RSS",     f"{analysis.rss_end_mb:.3f} MB"),
        ("Delta",       f"{analysis.rss_delta_mb:+.3f} MB"),
        ("Growth rate", f"{analysis.rss_growth_rate_mb_s:+.4f} MB/s"),
    ]
    for label, value in rows:
        print(f"  {label:<14} {value:>12}")

    # ── ASCII chart ───────────────────────────────────────────────────────────
    print()
    print(_divider())
    print("  RSS over time")
    print(_divider())

    bar_width = 30
    for sample in samples:
        bar = _bar(sample.rss_mb, peak, bar_width)
        print(f"  {sample.timestamp:6.2f}s  {bar}  {sample.rss_mb:.2f} MB")

    print(_divider())
    print(f"  {'0':>9}{'':>{bar_width - 4}}peak: {peak:.2f} MB")
    print()