#!/usr/bin/env python3
"""Trim MEMORY.md and log.md to max lines. Delegates to context_sync."""
from context_sync import trim_memory, trim_log, MEMORY_MAX, LOG_MAX

if __name__ == "__main__":
    trim_memory()
    trim_log()
    print(f"Trimmed MEMORY (max {MEMORY_MAX}) and log (max {LOG_MAX})")
