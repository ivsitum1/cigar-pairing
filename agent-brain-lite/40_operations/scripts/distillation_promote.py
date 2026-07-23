#!/usr/bin/env python3
"""Promote a PHI-reviewed trace to the distillation corpus. See DISTILLATION_TRACE_PROTOCOL.md."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from distillation.promote import (  # noqa: E402
    list_raw_traces,
    promote_trace,
    suggest_distills_to,
    validate_promotable,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote distillation trace to committed corpus card")
    parser.add_argument("--trace-id", default=None, help="trace to promote (dtr_...)")
    parser.add_argument("--list", action="store_true", help="list raw traces with promotion status")
    parser.add_argument("--phi-reviewed", action="store_true", help="confirm human PHI review (required)")
    parser.add_argument("--dry-run", action="store_true", help="validate and print target path only")
    parser.add_argument("--json", action="store_true", help="emit JSON summary")
    args = parser.parse_args()

    if args.list:
        rows = []
        for t in list_raw_traces(WORKSPACE):
            ok, reason = validate_promotable(t, phi_reviewed_confirm=True)
            rows.append(
                {
                    "trace_id": t.get("trace_id"),
                    "task_domain": t.get("task_domain"),
                    "skeleton": t.get("skeleton"),
                    "enrichment_status": t.get("enrichment_status"),
                    "promoted_to": t.get("promoted_to"),
                    "ready": ok,
                    "note": reason if not ok else "ready",
                }
            )
        print(json.dumps(rows, ensure_ascii=False, indent=2) if args.json else _format_list(rows))
        return 0

    if not args.trace_id:
        parser.error("--trace-id required (or use --list)")

    try:
        out = promote_trace(
            args.trace_id,
            workspace=WORKSPACE,
            phi_reviewed_confirm=args.phi_reviewed,
            dry_run=args.dry_run,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rel = str(out.relative_to(WORKSPACE)).replace("\\", "/")
    if args.dry_run:
        print(f"dry-run → would write {rel}")
        return 0

    summary = {"corpus_path": rel, "trace_id": args.trace_id}
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        trace = json.loads((WORKSPACE / ".agent/distillation/raw" / f"{args.trace_id}.json").read_text(encoding="utf-8"))
        print(f"promoted {args.trace_id} -> {rel}")
        print(f"distills_to: {suggest_distills_to(trace)}")
    return 0


def _format_list(rows: list[dict]) -> str:
    lines = ["trace_id\tdomain\tstatus\tready\tnote"]
    for r in rows:
        status = r.get("enrichment_status") or ("skeleton" if r.get("skeleton") else "—")
        if r.get("promoted_to"):
            status = f"promoted→{r['promoted_to']}"
        lines.append(
            f"{r.get('trace_id')}\t{r.get('task_domain')}\t{status}\t{r.get('ready')}\t{r.get('note')}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
