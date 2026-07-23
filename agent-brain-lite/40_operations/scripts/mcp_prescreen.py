#!/usr/bin/env python3
"""CLI for MCP argument prescreen (LifeHarness Environment Contract)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from harness.mcp_prescreen import prescreen_tool_args  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Prescreen MCP tool arguments")
    parser.add_argument("--tool", required=True, help="Tool name")
    parser.add_argument("--args", required=True, help="JSON string of arguments")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = prescreen_tool_args(args.tool, args.args)
    payload = {"ok": result.ok, "issues": result.issues, "hints": result.hints}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"ok={result.ok}")
        for h in result.hints:
            print(f"hint: {h}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
