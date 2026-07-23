#!/usr/bin/env python3
"""CLI to append trajectory JSONL events. See 30_system/docs/TRAJECTORY_EMIT_PROTOCOL.md."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from trajectory_rl.emit import append_atdp_event, append_event, init_session  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Append one trajectory event (JSONL)")
    parser.add_argument(
        "--event-type",
        help="plan_step|tool_selected|tool_args|tool_result|state_snapshot|final_answer|atdp_step",
    )
    parser.add_argument("--payload", default="{}", help="JSON object for payload")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--init-session", action="store_true", help="Start a new run_id and trace file")
    parser.add_argument("--atdp", action="store_true", help="Emit ATDP-lite tuple (sets event_type=atdp_step)")
    parser.add_argument("--observation", default="", help="ATDP o")
    parser.add_argument("--hidden-status", default="", help="ATDP h")
    parser.add_argument("--action", default="", help="ATDP a")
    parser.add_argument("--outcome", default="", help="ATDP y")
    parser.add_argument("--reward", type=float, default=None, help="ATDP r")
    parser.add_argument("--metadata", default="{}", help="ATDP m as JSON object")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.init_session:
        trace = init_session(reset=True, run_id=args.run_id)
        if args.json:
            print(json.dumps({"trace_path": str(trace.relative_to(WORKSPACE)).replace("\\", "/")}, indent=2))
        return 0

    if args.atdp:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as exc:
            print(f"Invalid --metadata JSON: {exc}", file=sys.stderr)
            return 2
        trace = append_atdp_event(
            observation=args.observation,
            hidden_status=args.hidden_status,
            action=args.action,
            outcome=args.outcome,
            reward=args.reward,
            metadata=metadata if isinstance(metadata, dict) else {},
            run_id=args.run_id,
        )
        out = {"trace_path": str(trace.relative_to(WORKSPACE)).replace("\\", "/"), "event_type": "atdp_step"}
        print(json.dumps(out, ensure_ascii=False, indent=2) if args.json else out["trace_path"])
        return 0

    if not args.event_type:
        print("Provide --event-type or --atdp", file=sys.stderr)
        return 2

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as exc:
        print(f"Invalid --payload JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("--payload must be a JSON object", file=sys.stderr)
        return 2

    trace = append_event(args.event_type, payload, run_id=args.run_id)
    out = {"trace_path": str(trace.relative_to(WORKSPACE)).replace("\\", "/"), "event_type": args.event_type}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(out["trace_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
