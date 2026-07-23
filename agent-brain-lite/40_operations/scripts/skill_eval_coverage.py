#!/usr/bin/env python3
"""Report registry skills missing evals/<id>.json seed files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = ROOT / "30_system" / "SKILLS" / "registry.json"
EVALS = ROOT / "30_system" / "SKILLS" / "evals"


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill eval coverage report")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not REGISTRY.exists():
        print("registry.json not found", file=sys.stderr)
        return 1

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids = [s["id"] for s in registry.get("skills", [])]
    missing = []
    present = []
    for sid in ids:
        if (EVALS / f"{sid}.json").exists():
            present.append(sid)
        else:
            missing.append(sid)

    report = {
        "total": len(ids),
        "with_eval": len(present),
        "missing_eval": missing,
        "ok": len(missing) == 0,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== SKILL EVAL COVERAGE ===")
        print(f"Registry skills: {report['total']}")
        print(f"With evals/{'{id}'}.json: {report['with_eval']}")
        if missing:
            print(f"Missing ({len(missing)}):")
            for sid in missing:
                print(f"  - {sid}")
        else:
            print("All registry skills have eval seed files.")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
