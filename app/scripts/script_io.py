# -*- coding: utf-8 -*-
"""Console I/O helpers for pipeline scripts (esp. Windows cp125x consoles)."""
from __future__ import annotations

import sys


def configure_stdio() -> None:
    """Force UTF-8 on stdout/stderr so print() of HR text does not raise UnicodeEncodeError."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
