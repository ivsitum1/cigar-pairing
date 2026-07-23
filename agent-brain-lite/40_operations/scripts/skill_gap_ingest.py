#!/usr/bin/env python3
"""
Ingest skill-learning artifacts: append eval cases from real failures and sync Obsidian wiki log.

Usage (from repo root):
  python 40_operations/scripts/skill_gap_ingest.py append-eval \\
    --skill-id avoid-ai-formulations \\
    --failure-text "bad excerpt..." \\
    --correction-text "gold excerpt..." \\
    --case-id case_from_E42

  python 40_operations/scripts/skill_gap_ingest.py wiki-log \\
    --event "skill-gap" \\
    --detail "appended case_from_E42 to avoid-ai-formulations eval"

Non-statistical automation only (orchestration). See [[Skill gap pipeline]] in wiki.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
EVALS_DIR = WORKSPACE / "30_system" / "SKILLS" / "evals"
WIKI_LOG = WORKSPACE / "20_knowledge" / "wiki" / "log.md"
MAX_DEFAULT_INPUT_CHARS = 12_000
MAX_ASSERTION_STRING = 500


def _safe_skill_id(skill_id: str) -> str:
    s = skill_id.strip().lower().replace(" ", "-")
    if re.search(r"[^a-z0-9\-]", s):
        raise ValueError(f"Invalid skill_id: {skill_id!r}")
    return s


def _truncate(s: str, max_len: int) -> str:
    s = s.strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3].rstrip() + "..."


def _default_contains_from_correction(correction: str) -> str | None:
    for line in correction.splitlines():
        t = line.strip()
        if len(t) >= 8:
            return _truncate(t, 200)
    t = correction.strip()
    if len(t) >= 8:
        return _truncate(t, 200)
    return None


def load_evals(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_evals(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_case(
    case_id: str,
    failure_text: str,
    correction_text: str,
    contains: list[str],
    not_contains: list[str],
    infer_contains: bool,
) -> dict:
    ft = _truncate(failure_text, MAX_DEFAULT_INPUT_CHARS)
    ct = correction_text.strip()
    prompt = (
        "Original assistant output (incorrect):\n"
        f"{ft}\n\n"
        "User correction (gold target):\n"
        f"{ct}\n\n"
        "Apply the skill and produce the final corrected output."
    )
    assertions: list[dict] = []
    for v in not_contains:
        vv = _truncate(v, MAX_ASSERTION_STRING)
        if vv:
            assertions.append(
                {
                    "type": "not_contains",
                    "value": vv,
                    "description": f"Regression: must not contain: {vv[:80]}",
                }
            )
    for v in contains:
        vv = _truncate(v, MAX_ASSERTION_STRING)
        if vv:
            assertions.append(
                {
                    "type": "contains",
                    "value": vv,
                    "description": f"Regression: must contain: {vv[:80]}",
                }
            )
    if infer_contains and not any(a["type"] == "contains" for a in assertions):
        inferred = _default_contains_from_correction(ct)
        if inferred:
            assertions.append(
                {
                    "type": "contains",
                    "value": inferred,
                    "description": "Auto: substring from user correction",
                }
            )
    if not assertions:
        raise ValueError(
            "No assertions generated. Pass --contains and/or --not-contains, "
            "or use --infer-contains with a substantive correction."
        )
    return {
        "id": case_id,
        "input": {"text": prompt},
        "assertions": assertions,
    }


def cmd_append_eval(args: argparse.Namespace) -> int:
    sid = _safe_skill_id(args.skill_id)
    path = EVALS_DIR / f"{sid}.json"
    if not path.exists():
        print(f"ERROR: Eval file missing: {path}", file=sys.stderr)
        print("Create evals first (Phase 0) or add minimal evals JSON before ingest.", file=sys.stderr)
        return 2
    data = load_evals(path)
    if data.get("skill_id") != sid:
        print(f"WARN: JSON skill_id {data.get('skill_id')!r} != {sid!r}", file=sys.stderr)

    case = build_case(
        case_id=args.case_id,
        failure_text=args.failure_text,
        correction_text=args.correction_text,
        contains=list(args.contains or []),
        not_contains=list(args.not_contains or []),
        infer_contains=bool(args.infer_contains),
    )
    cases = data.setdefault("cases", [])
    existing = {c.get("id") for c in cases if isinstance(c, dict)}
    if case["id"] in existing:
        print(f"ERROR: case id already exists: {case['id']}", file=sys.stderr)
        return 3
    cases.append(case)
    if args.dry_run:
        print(json.dumps(case, ensure_ascii=False, indent=2))
        return 0
    save_evals(path, data)
    print(f"OK: appended {case['id']} to {path.relative_to(WORKSPACE)}")
    return 0


def cmd_from_gap_report(args: argparse.Namespace) -> int:
    inp = Path(args.input).expanduser()
    if not inp.is_file():
        print(f"ERROR: gap report not found: {inp}", file=sys.stderr)
        return 2
    report = json.loads(inp.read_text(encoding="utf-8"))

    if getattr(args, "evolve_dual", False):
        sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))
        from brain_assist.dual_registry_evolve import process_gap_report  # noqa: E402
        from brain_assist.rcml_registry import detect_relation_tag  # noqa: E402

        if not report.get("relation_tag") and report.get("prompt"):
            report["relation_tag"] = detect_relation_tag(report["prompt"])
        evo = process_gap_report(report, propose_rewrite=True, evolve_verifier=True)
        if not evo.get("ok"):
            print(f"WARN: evolve_dual failed: {evo}", file=sys.stderr)

    suggested = report.get("suggested_case") or {}
    skill_id = args.skill_id or suggested.get("skill_id") or report.get("skill_id")
    if not skill_id:
        print("ERROR: no skill_id in report; pass --skill-id", file=sys.stderr)
        return 2
    failure = suggested.get("failure_text") or json.dumps(report.get("gaps") or [])[:2000]
    correction = suggested.get("correction_text") or "Retry with corrected tool args per prescreen hint."
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    case_id = args.case_id or f"case_from_gap_{ts}"
    nested = argparse.Namespace(
        skill_id=skill_id,
        case_id=case_id,
        failure_text=failure,
        correction_text=correction,
        contains=[],
        not_contains=[],
        infer_contains=True,
        dry_run=args.dry_run,
    )
    return cmd_append_eval(nested)


def cmd_wiki_log(args: argparse.Namespace) -> int:
    if not WIKI_LOG.exists():
        print(f"ERROR: wiki log missing: {WIKI_LOG}", file=sys.stderr)
        return 2
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    block = (
        f"\n- Date: {ts}\n"
        f"  - Action: {args.action}\n"
        f"  - Input: {args.input_path or '(chat)'}\n"
        f"  - Outputs: {args.outputs or '(n/a)'}\n"
        f"  - Notes: {args.detail}\n"
    )
    if args.dry_run:
        print(block)
        return 0
    with open(WIKI_LOG, "a", encoding="utf-8") as f:
        f.write(block)
    print(f"OK: appended to {WIKI_LOG.relative_to(WORKSPACE)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Skill gap ingest: eval cases + wiki log")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("append-eval", help="Append one regression case to evals JSON")
    a.add_argument("--skill-id", required=True)
    a.add_argument("--case-id", required=True)
    a.add_argument("--failure-text", required=True)
    a.add_argument("--correction-text", required=True)
    a.add_argument("--contains", action="append", default=[])
    a.add_argument("--not-contains", action="append", default=[])
    a.add_argument(
        "--infer-contains",
        action="store_true",
        help="If no --contains, derive one contains assertion from correction text",
    )
    a.add_argument("--dry-run", action="store_true")
    a.set_defaults(func=cmd_append_eval)

    w = sub.add_parser("wiki-log", help="Append structured entry to 20_knowledge/wiki/log.md")
    w.add_argument("--action", default="skill-gap")
    w.add_argument("--detail", required=True)
    w.add_argument("--input-path", default="")
    w.add_argument("--outputs", default="")
    w.add_argument("--dry-run", action="store_true")
    w.set_defaults(func=cmd_wiki_log)

    g = sub.add_parser("from-gap-report", help="Append eval case from trajectory_gap_report JSON")
    g.add_argument("--input", required=True, help="Gap report JSON from trajectory_gap_report.py")
    g.add_argument("--skill-id", default="", help="Override skill_id in report")
    g.add_argument("--case-id", default="", help="Case id (default: case_from_gap_<timestamp>)")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument(
        "--evolve-dual",
        action="store_true",
        help="Also run evolve_dual_registry from-gap-report on same input",
    )
    g.set_defaults(func=cmd_from_gap_report)

    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
