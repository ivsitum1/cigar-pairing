#!/usr/bin/env python3
"""Run local memory worker service."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from memory_engine.worker import run_worker


if __name__ == "__main__":
    run_worker()

