# ⚡ Watch Mode - Quick Guide

## Quick Start

```bash
# 1. Install
pip install pytest-watch

# 2. Run
python -m pytest_watch

# Or directly (if ptw is on PATH)
ptw

# 3. Code - tests run automatically when you save a file!
```

## Stopping

Press `Ctrl+C`

## Advanced Options

```bash
# Verbose output
python -m pytest_watch --runner "pytest -v"

# Parallel (faster)
python -m pytest_watch --runner "pytest -n auto"

# Minimal output
python -m pytest_watch --runner "pytest --tldr"
```

## Detailed Instructions

See [WATCH_MODE_GUIDE.md](../../WATCH_MODE_GUIDE.md) for the complete guide.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
