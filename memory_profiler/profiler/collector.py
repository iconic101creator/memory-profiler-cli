import time
import psutil
from dataclasses import dataclass, field
from typing import List


@dataclass
class MemorySample:
    timestamp: float   # seconds since collection started
    rss_mb: float      # Resident Set Size in MB
    vms_mb: float      # Virtual Memory Size in MB


@dataclass
class CollectionResult:
    pid: int
    process_name: str
    samples: List[MemorySample] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def collect(pid: int, interval: float = 0.5, duration: float = 10.0) -> CollectionResult:
    """
    Attach to a running process by PID and sample its memory usage.

    Args:
        pid:      Target process ID
        interval: Seconds between samples (default 0.5s)
        duration: Total collection time in seconds (default 10s)

    Returns:
        CollectionResult with all samples and any errors encountered
    """
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        raise ValueError(f"No process found with PID {pid}")
    except psutil.AccessDenied:
        raise PermissionError(f"Access denied to PID {pid} — try running with elevated privileges")

    result = CollectionResult(pid=pid, process_name=process.name())

    start_time = time.monotonic()
    end_time = start_time + duration

    print(f"Attaching to '{result.process_name}' (PID {pid}) — sampling every {interval}s for {duration}s\n")

    while time.monotonic() < end_time:
        try:
            mem_info = process.memory_info()
            elapsed = time.monotonic() - start_time

            sample = MemorySample(
                timestamp=round(elapsed, 3),
                rss_mb=round(mem_info.rss / 1024 / 1024, 3),
                vms_mb=round(mem_info.vms / 1024 / 1024, 3),
            )
            result.samples.append(sample)

            # Live feedback so the user knows it's working
            print(f"  [{sample.timestamp:6.2f}s]  RSS: {sample.rss_mb:.2f} MB  |  VMS: {sample.vms_mb:.2f} MB")

        except psutil.NoSuchProcess:
            result.errors.append(f"Process {pid} exited at {round(time.monotonic() - start_time, 2)}s")
            print(f"\n  Process exited early — stopping collection.")
            break
        except psutil.AccessDenied as e:
            result.errors.append(str(e))
            break

        time.sleep(interval)

    print(f"\nCollection complete. {len(result.samples)} samples captured.")
    return result