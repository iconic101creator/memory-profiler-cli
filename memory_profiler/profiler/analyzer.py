from dataclasses import dataclass
from typing import List
from .collector import CollectionResult, MemorySample


@dataclass
class AnalysisResult:
    pid: int
    process_name: str
    sample_count: int
    duration_s: float

    # RSS stats (actual physical RAM)
    rss_start_mb: float
    rss_end_mb: float
    rss_peak_mb: float
    rss_avg_mb: float
    rss_delta_mb: float       # end - start (positive = grew, negative = shrank)
    rss_growth_rate_mb_s: float  # MB per second


def analyze(result: CollectionResult) -> AnalysisResult:
    """
    Compute memory statistics from a CollectionResult.

    Args:
        result: Output from collector.collect()

    Returns:
        AnalysisResult with peak, average, delta, and growth rate
    """
    samples: List[MemorySample] = result.samples

    if not samples:
        raise ValueError("No samples to analyze — collection may have failed or the process exited immediately")

    rss_values = [s.rss_mb for s in samples]
    duration = samples[-1].timestamp - samples[0].timestamp

    rss_start = rss_values[0]
    rss_end = rss_values[-1]
    rss_delta = round(rss_end - rss_start, 3)
    growth_rate = round(rss_delta / duration, 4) if duration > 0 else 0.0

    return AnalysisResult(
        pid=result.pid,
        process_name=result.process_name,
        sample_count=len(samples),
        duration_s=round(duration, 3),
        rss_start_mb=rss_start,
        rss_end_mb=rss_end,
        rss_peak_mb=round(max(rss_values), 3),
        rss_avg_mb=round(sum(rss_values) / len(rss_values), 3),
        rss_delta_mb=rss_delta,
        rss_growth_rate_mb_s=growth_rate,
    )