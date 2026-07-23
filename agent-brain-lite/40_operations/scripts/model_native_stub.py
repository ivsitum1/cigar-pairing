#!/usr/bin/env python3
"""
Model-native entrypoint: delegates to full pipeline when MODEL_NATIVE_RUNTIME=1.

Legacy stub validate-only mode remains for backward compatibility.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_PRD = WORKSPACE / "30_system" / "docs" / "prd_geometry_incorporation.json"
RUN_SCRIPT = WORKSPACE / "40_operations" / "scripts" / "model_native_run.py"


def validate_prd_only(prd_path: Path) -> dict:
    data = json.loads(prd_path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    vp = data.get("verification_protocol") or {}
    if not vp.get("claim_statuses"):
        blockers.append("missing_claim_statuses")
    bvs = vp.get("baseline_vs_steered") or {}
    if bvs.get("required") and not bvs.get("passes"):
        blockers.append("baseline_vs_steered_not_passing")
    repro = vp.get("reproducibility") or {}
    if repro.get("required") and not repro.get("passes"):
        blockers.append("reproducibility_not_passing")
    runtime = os.environ.get("MODEL_NATIVE_RUNTIME", "").strip() == "1"
    return {
        "prd": str(prd_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "stub_mode": not runtime,
        "runtime_enabled": runtime,
        "blockers": blockers,
        "verdict": "PASS" if not blockers else "CHECKLIST_INCOMPLETE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Model-native stub or full runtime delegate")
    parser.add_argument("--prd", default=str(DEFAULT_PRD))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full", action="store_true", help="Force full pipeline via model_native_run.py")
    args = parser.parse_args()
    prd = Path(args.prd)
    if not prd.is_file():
        prd = WORKSPACE / args.prd

    runtime = os.environ.get("MODEL_NATIVE_RUNTIME", "").strip() == "1" or args.full
    if runtime:
        rc = subprocess.call([sys.executable, str(RUN_SCRIPT), "run", "--json"])
        if rc != 0:
            return rc
        rc2 = subprocess.call([sys.executable, str(RUN_SCRIPT), "validate-prd", "--prd", str(prd)])
        return rc2

    result = validate_prd_only(prd)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"verdict={result['verdict']} stub_mode={result['stub_mode']}")
    return 0 if result["verdict"] == "PASS" or result["stub_mode"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
