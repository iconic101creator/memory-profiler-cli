# memory-profiler-cli

A command-line tool that attaches to any running process and profiles its memory usage in real time, then prints a formatted report with stats and an ASCII chart.

## Features

- Attaches to any process by PID
- Samples RSS (physical RAM) and VMS (virtual memory) at a configurable interval
- Reports peak, average, start/end, delta, and growth rate
- ASCII chart of RSS over time
- Gracefully handles early process exit and permission errors

## Project Structure

```
memory_profiler/
├── profiler/
│   ├── __init__.py
│   ├── collector.py    # attaches to a PID and samples memory
│   ├── analyzer.py     # computes stats from samples
│   └── reporter.py     # prints the formatted report
├── main.py             # CLI entry point
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/iconic101creator/memory-profiler-cli.git
cd memory-profiler-cli
pip install -r requirements.txt
```

## Usage

```bash
python main.py --pid <PID> [--interval <seconds>] [--duration <seconds>]
```

### Arguments

| Argument | Short | Default | Description |
|---|---|---|---|
| `--pid` | `-p` | required | PID of the process to profile |
| `--interval` | `-i` | `0.5` | Seconds between samples |
| `--duration` | `-d` | `10.0` | Total profiling time in seconds |

### Examples

```bash
# Profile PID 1234 with defaults (0.5s interval, 10s duration)
python main.py --pid 1234

# Profile for 60 seconds, sampling every second
python main.py --pid 1234 --interval 1.0 --duration 60

# Quick 5-second snapshot
python main.py -p 1234 -i 0.5 -d 5
```

### Example Output

```
════════════════════════════════════════════════════════════
  MEMORY PROFILE REPORT
  Process : opera.exe  (PID 10988)
  Duration: 9.537s   Samples: 20
════════════════════════════════════════════════════════════

  Peak RSS          11.602 MB
  Avg RSS           11.602 MB
  Start RSS         11.602 MB
  End RSS           11.602 MB
  Delta             +0.000 MB
  Growth rate       +0.0000 MB/s

────────────────────────────────────────────────────────────
  RSS over time
────────────────────────────────────────────────────────────
    0.00s  ███████████████░░░░░░░░░░░░░░░  11.60 MB
    0.51s  ███████████████░░░░░░░░░░░░░░░  11.60 MB
    ...
────────────────────────────────────────────────────────────
         0                       peak: 11.60 MB
```

## How to Find a PID

**Windows:** Open Task Manager (`Ctrl+Shift+Esc`) → Details tab → PID column.

**Linux/macOS:** Run `ps aux | grep <process name>` or use `pgrep <name>`.

## Requirements

- Python 3.9+
- psutil >= 5.9.0
