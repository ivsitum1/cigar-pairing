#!/usr/bin/env python3
"""Full audit: error_ops audit + error_to_learning_bridge + brain_status."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from cursor_paths import resolve_cursor_script

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SCRIPTS = WORKSPACE / "40_operations/scripts"


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE))
    text = result.stdout + (result.stderr if result.returncode != 0 else "")
    return result.returncode, text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    out = []
    report = {"sections": [], "ok": True}

    # 1. error_ops audit
    out.append("=" * 60)
    out.append("1. ERROR OPS AUDIT")
    out.append("=" * 60)
    err_ops = resolve_cursor_script(WORKSPACE, "error_ops.py")
    if err_ops:
        code, s = run([sys.executable, str(err_ops), "audit"])
        out.append(s)
        if code != 0:
            report["ok"] = False
    else:
        out.append("(error_ops.py not found)")
        report["ok"] = False

    # 2. error_to_learning_bridge
    out.append("\n" + "=" * 60)
    out.append("2. ERROR -> LEARNING BRIDGE")
    out.append("=" * 60)
    bridge = resolve_cursor_script(WORKSPACE, "error_to_learning_bridge.py")
    if bridge:
        code, s = run([sys.executable, str(bridge)])
        out.append(s)
        if code != 0:
            report["ok"] = False
    else:
        out.append("(error_to_learning_bridge.py not found)")
        report["ok"] = False

    # 3. brain_status
    out.append("\n" + "=" * 60)
    out.append("3. BRAIN STATUS")
    out.append("=" * 60)
    status = SCRIPTS / "brain_status.py"
    if status.exists():
        result = subprocess.run([sys.executable, str(status)], capture_output=True, text=True, cwd=str(WORKSPACE))
        out.append(result.stdout)
        if result.returncode != 0:
            report["ok"] = False
    else:
        out.append("(brain_status.py not found)")
        report["ok"] = False

    text = "\n".join(out)
    if args.json:
        report["text"] = text
        print(json.dumps(report, indent=2))
    else:
        print(text)

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
