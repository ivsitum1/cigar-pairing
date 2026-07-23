#!/usr/bin/env python3
"""Add 40_operations/python to the active venv via .pth (for pdf_extraction imports)."""

from __future__ import annotations

import site
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
PY_ROOT = WORKSPACE / "40_operations" / "python"


def main() -> int:
    if not PY_ROOT.is_dir():
        print(f"Missing {PY_ROOT}", file=sys.stderr)
        return 1
    import sysconfig

    sp = Path(sysconfig.get_paths()["purelib"])
    if not sp.is_dir():
        pure = site.getsitepackages()
        if not pure:
            print("No site-packages found.", file=sys.stderr)
            return 1
        sp = Path(pure[0])
    pth = sp / "agent_rules_pdf_extraction.pth"
    line = str(PY_ROOT.resolve()) + "\n"
    pth.write_text(line, encoding="utf-8")
    print(f"Wrote {pth}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
