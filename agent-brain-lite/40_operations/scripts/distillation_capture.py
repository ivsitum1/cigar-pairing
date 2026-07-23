#!/usr/bin/env python3
"""CLI to capture one distillation trace. See 30_system/docs/DISTILLATION_TRACE_PROTOCOL.md.

Reads a CaptureRecord as JSON — from --record '<json>' or from stdin — cleans,
PHI-scrubs, and appends it to the gitignored raw landing log.

    python 40_operations/scripts/distillation_capture.py --record '{"context":"...","reasoning":"...","actions":[{"tool":"Bash","intent":"run tests","result_summary":"12 passed"}],"outcome":{"success":true,"verification":"pytest green"},"task_domain":"python"}'

    cat trace.json | python 40_operations/scripts/distillation_capture.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from distillation.emit import Action, CaptureRecord, capture  # noqa: E402


def _build_record(data: dict) -> CaptureRecord:
    actions = [
        Action(
            tool=str(a.get("tool", "unknown")),
            intent=str(a.get("intent", "")),
            result_summary=str(a.get("result_summary", "")),
            success=bool(a.get("success", True)),
        )
        for a in data.get("actions", [])
        if isinstance(a, dict)
    ]
    return CaptureRecord(
        context=str(data.get("context", "")),
        reasoning=str(data.get("reasoning", "")),
        actions=actions,
        outcome=data.get("outcome", {}) if isinstance(data.get("outcome"), dict) else {},
        task_domain=str(data.get("task_domain", "general")),
        source_model=str(data.get("source_model", "claude-fable-5")),
        tags=[str(t) for t in data.get("tags", []) if isinstance(data.get("tags"), list)],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture one distillation trace (cleaned + PHI-scrubbed)")
    parser.add_argument("--record", default=None, help="JSON object for the trace; if omitted, read stdin")
    parser.add_argument("--record-file", default=None, help="path to JSON record file (alternative to --record)")
    parser.add_argument("--json", action="store_true", help="emit JSON summary")
    args = parser.parse_args()

    if args.record_file:
        raw = Path(args.record_file).read_text(encoding="utf-8-sig")
    else:
        raw = args.record if args.record is not None else sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Invalid record JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("record must be a JSON object", file=sys.stderr)
        return 2
    if not str(data.get("context", "")).strip():
        print("record.context is required", file=sys.stderr)
        return 2

    record = _build_record(data)
    built = record.to_record()
    log_path = capture(record)

    out = {
        "log_path": str(log_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "trace_id": built["trace_id"],
        "phi_hits": built["phi_hits"],
        "promotable": built["promotable"],
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        flag = "" if built["promotable"] else "  ⚠ PHI review required before promotion"
        print(f"{out['trace_id']} -> {out['log_path']}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
