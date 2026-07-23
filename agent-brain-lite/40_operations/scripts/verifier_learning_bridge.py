#!/usr/bin/env python3
"""Bridge user corrections into verifier eval cases and registry evolution."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
EVALS_DIR = WORKSPACE / "30_system" / "SKILLS" / "evals"
STATE_PATH = WORKSPACE / ".agent" / "memory" / "verifier_bridge_state.json"
VERIFIER_EVAL = EVALS_DIR / "skill-verifier-gate.json"
PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(PY_ROOT))


def _utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_state() -> dict:
    if not STATE_PATH.is_file():
        return {"daily_cases": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"daily_cases": {}}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _daily_cap_ok(skill_id: str) -> bool:
    state = _load_state()
    today = _utc_date()
    daily = state.setdefault("daily_cases", {})
    key = f"{today}:{skill_id}"
    if daily.get(key, 0) >= 1:
        return False
    daily[key] = daily.get(key, 0) + 1
    _save_state(state)
    return True


def _safe_skill_id(skill_id: str) -> str:
    s = skill_id.strip().lower().replace(" ", "-")
    if re.search(r"[^a-z0-9\-]", s):
        raise ValueError(f"Invalid skill_id: {skill_id!r}")
    return s


def append_verifier_eval_case(
    *,
    prompt: str,
    skill_id: str,
    expected_action: str,
    case_id: str,
    dry_run: bool = False,
) -> int:
    if expected_action not in {"ACCEPT", "SKIP", "DECOMPOSE", "REWRITE"}:
        print(f"ERROR: invalid expected_action: {expected_action}", file=sys.stderr)
        return 2
    if not dry_run and not _daily_cap_ok(skill_id):
        print(f"SKIP: daily cap reached for skill {skill_id}", file=sys.stderr)
        return 0
    if not VERIFIER_EVAL.is_file():
        print(f"ERROR: missing {VERIFIER_EVAL}", file=sys.stderr)
        return 2
    data = json.loads(VERIFIER_EVAL.read_text(encoding="utf-8"))
    cases = data.setdefault("cases", [])
    if any(c.get("id") == case_id for c in cases):
        print(f"ERROR: case id exists: {case_id}", file=sys.stderr)
        return 3
    case = {
        "id": case_id,
        "input": {"prompt": prompt.strip()},
        "assertions": [
            {
                "type": "regex_match",
                "value": f'"id"\\s*:\\s*"{re.escape(skill_id)}"',
                "description": f"includes skill {skill_id}",
            },
            {
                "type": "regex_match",
                "value": f'"action"\\s*:\\s*"{expected_action}"',
                "description": f"expected action {expected_action} for {skill_id}",
            },
        ],
        "source": "verifier_learning_bridge",
        "skill_id": skill_id,
    }
    if dry_run:
        print(json.dumps(case, ensure_ascii=False, indent=2))
        return 0
    cases.append(case)
    VERIFIER_EVAL.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: appended {case_id} to skill-verifier-gate.json")
    return 0


def cmd_from_correction(args: argparse.Namespace) -> int:
    sid = _safe_skill_id(args.skill_id)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    case_id = args.case_id or f"case_from_correction_{sid}_{ts}"
    rc = append_verifier_eval_case(
        prompt=args.prompt,
        skill_id=sid,
        expected_action=args.expected_action.upper(),
        case_id=case_id,
        dry_run=args.dry_run,
    )
    if rc != 0:
        return rc

    if args.evolve_verifier and not args.dry_run:
        from brain_assist.dual_registry_evolve import process_gap_report  # noqa: E402
        from brain_assist.rcml_registry import detect_relation_tag  # noqa: E402

        report = {
            "skill_id": sid,
            "relation_tag": detect_relation_tag(args.prompt),
            "suggested_case": {
                "skill_id": sid,
                "failure_text": args.failure,
                "correction_text": args.correction,
            },
            "gaps": [{"gap_type": "user_correction", "expected_action": args.expected_action.upper()}],
        }
        evo = process_gap_report(report, propose_rewrite=False, evolve_verifier=True)
        print(json.dumps({"evolve": evo}, ensure_ascii=False))

    if args.wiki_log and not args.dry_run:
        subprocess.run(
            [
                sys.executable,
                str(WORKSPACE / "40_operations" / "scripts" / "skill_gap_ingest.py"),
                "wiki-log",
                "--detail",
                f"verifier bridge: {case_id} for {sid} → {args.expected_action.upper()}",
            ],
            check=False,
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifier learning bridge from user corrections")
    sub = parser.add_subparsers(dest="cmd", required=True)

    fc = sub.add_parser("from-correction", help="Append verifier eval + optional evolve")
    fc.add_argument("--prompt", required=True)
    fc.add_argument("--skill-id", required=True)
    fc.add_argument("--expected-action", required=True, choices=["ACCEPT", "SKIP", "DECOMPOSE", "REWRITE"])
    fc.add_argument("--failure", default="Verifier routed incorrectly.")
    fc.add_argument("--correction", default="User corrected expected skill routing.")
    fc.add_argument("--case-id", default="")
    fc.add_argument("--evolve-verifier", action="store_true", default=True)
    fc.add_argument("--no-evolve-verifier", dest="evolve_verifier", action="store_false")
    fc.add_argument("--wiki-log", action="store_true", default=True)
    fc.add_argument("--no-wiki-log", dest="wiki_log", action="store_false")
    fc.add_argument("--dry-run", action="store_true")
    fc.set_defaults(func=cmd_from_correction)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
