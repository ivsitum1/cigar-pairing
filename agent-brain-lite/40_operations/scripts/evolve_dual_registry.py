#!/usr/bin/env python3
"""SkillLens dual-registry evolution: verifier updates + skill REWRITE proposals."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.dual_registry_evolve import (  # noqa: E402
    apply_rewrite_proposal,
    process_gap_report,
    propose_skill_rewrite,
)
from brain_assist.rcml_registry import detect_relation_tag  # noqa: E402
from brain_assist.verifier_registry import load_verifier_registry, save_verifier_registry  # noqa: E402

WORKSPACE = Path(__file__).resolve().parents[2]


def cmd_from_gap(args: argparse.Namespace) -> int:
    inp = Path(args.input).expanduser()
    report = json.loads(inp.read_text(encoding="utf-8"))
    if args.relation_tag:
        report["relation_tag"] = args.relation_tag
    elif not report.get("relation_tag") and report.get("prompt"):
        report["relation_tag"] = detect_relation_tag(report["prompt"])
    result = process_gap_report(
        report,
        propose_rewrite=not args.no_rewrite,
        evolve_verifier=not args.no_verifier,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)
    return 0 if result.get("ok") else 1


def cmd_propose(args: argparse.Namespace) -> int:
    proposal = propose_skill_rewrite(
        args.skill_id,
        failure_text=args.failure_text,
        correction_text=args.correction_text,
        relation_tag=args.relation_tag or None,
    )
    reg = load_verifier_registry()
    pending = list(reg.get("pending_rewrites") or [])
    pending.append({"skill_id": args.skill_id, "status": "pending", "proposal_id": proposal["proposal_id"]})
    reg["pending_rewrites"] = pending[-50:]
    if not args.no_verifier:
        save_verifier_registry(reg)
    print(json.dumps(proposal, ensure_ascii=False, indent=2))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    path = Path(args.proposal).expanduser()
    if not path.is_file():
        path = WORKSPACE / "outputs" / "skill_rewrites" / "proposals" / args.proposal
    result = apply_rewrite_proposal(path, dry_run=args.dry_run)
    if result.get("ok") and not args.dry_run:
        reg = load_verifier_registry()
        pid = result.get("proposal_id", "")
        reg["pending_rewrites"] = [
            {**r, "status": "applied"}
            if r.get("proposal_id") == pid or r.get("skill_id") == result.get("skill_id")
            else r
            for r in (reg.get("pending_rewrites") or [])
        ]
        save_verifier_registry(reg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Dual-registry evolution (SkillLens v2)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("from-gap-report", help="Evolve verifier + propose REWRITE from gap JSON")
    g.add_argument("--input", required=True)
    g.add_argument("--relation-tag", default="")
    g.add_argument("--no-rewrite", action="store_true")
    g.add_argument("--no-verifier", action="store_true")
    g.add_argument("--json", action="store_true")
    g.set_defaults(func=cmd_from_gap)

    p = sub.add_parser("propose-rewrite", help="Create REWRITE proposal for a skill")
    p.add_argument("--skill-id", required=True)
    p.add_argument("--failure-text", required=True)
    p.add_argument("--correction-text", required=True)
    p.add_argument("--relation-tag", default="")
    p.add_argument("--no-verifier", action="store_true")
    p.set_defaults(func=cmd_propose)

    a = sub.add_parser("apply-rewrite", help="Append approved amendment to SKILL_*.md")
    a.add_argument("--proposal", required=True, help="Proposal JSON path or filename")
    a.add_argument("--dry-run", action="store_true")
    a.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
