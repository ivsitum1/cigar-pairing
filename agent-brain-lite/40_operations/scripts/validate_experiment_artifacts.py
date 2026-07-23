#!/usr/bin/env python3
"""Validate required experiment artifacts for a run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = WORKSPACE / "90_archive/artifacts"
REQUIRED_FILES = ("manifest.json", "metrics.json", "decision.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_run(run_id: str) -> tuple[bool, dict[str, Any]]:
    run_dir = ARTIFACTS_DIR / run_id
    result: dict[str, Any] = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "exists": run_dir.exists(),
        "required_files": {},
        "checks": {"metrics_matches_count": None},
        "ok": False,
    }
    if not run_dir.exists():
        return False, result

    all_present = True
    for filename in REQUIRED_FILES:
        exists = (run_dir / filename).exists()
        result["required_files"][filename] = exists
        all_present = all_present and exists

    if not all_present:
        return False, result

    try:
        metrics = _load_json(run_dir / "metrics.json")
        count = int(metrics.get("count", -1))
        results = metrics.get("results", [])
        result["checks"]["metrics_matches_count"] = count == len(results)
    except Exception:
        result["checks"]["metrics_matches_count"] = False

    result["ok"] = bool(result["checks"]["metrics_matches_count"])
    return result["ok"], result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate artifacts for an autonomous experiment run")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, payload = validate_run(args.run_id)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"run_id={payload['run_id']} ok={payload['ok']}")
        for name, exists in payload["required_files"].items():
            print(f"- {name}: {'ok' if exists else 'missing'}")
        print(f"- metrics_matches_count: {payload['checks']['metrics_matches_count']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
