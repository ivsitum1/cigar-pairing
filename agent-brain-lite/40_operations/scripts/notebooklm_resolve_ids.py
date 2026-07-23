#!/usr/bin/env python3
"""Resolve NotebookLM notebook titles via CLI."""
from __future__ import annotations

import json
import subprocess
import sys

IDS = [
    "c1280bad-7406-43f1-bc45-d6bb91502114",
    "5b10b85d-f085-4ff3-a293-69bfe614298b",
    "604aa4bf-7261-407c-9af3-e5f407f1e5f0",
    "8e1995f8-1721-4624-bbe0-92cd4f6a31ba",
]


def main() -> int:
    for nid in IDS:
        subprocess.run(
            [sys.executable, "-m", "notebooklm.notebooklm_cli", "use", nid],
            capture_output=True,
        )
        r = subprocess.run(
            [sys.executable, "-m", "notebooklm.notebooklm_cli", "metadata", "--json"],
            capture_output=True,
            text=True,
        )
        title = "?"
        try:
            d = json.loads(r.stdout)
            title = d.get("title") or d.get("notebook", {}).get("title", "?")
        except json.JSONDecodeError:
            title = (r.stdout or r.stderr)[:300]
        print(f"{nid} -> {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
