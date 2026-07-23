#!/usr/bin/env python3
"""Export live verifier ledger + corrections to Rcml training JSONL."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.rcml_registry import (  # noqa: E402
    detect_relation_tag,
    export_contrastive_jsonl,
    export_instruction_jsonl,
    load_rcml_registry,
)
from brain_assist.verifier_usage_ledger import prompt_hash, read_rows  # noqa: E402

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_OUT = WORKSPACE / "outputs" / "rcml_training"
VERIFIER_EVAL = WORKSPACE / "30_system" / "SKILLS" / "evals" / "skill-verifier-gate.json"
ERROR_LOG = WORKSPACE / ".cursor" / "errors" / "error_log.jsonl"

_ROUTING_KEYWORDS = re.compile(
    r"verifier|skill.?routing|skill.?lens|wrong skill|ACCEPT|SKIP|meta-analysis|to_load",
    re.I,
)


def _load_existing_hashes(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            h = row.get("prompt_hash")
            if h:
                seen.add(h)
        except json.JSONDecodeError:
            continue
    return seen


def _append_jsonl(path: Path, rows: list[dict]) -> int:
    if not rows:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(rows)


def _rows_from_correction(
    prompt: str,
    skill_id: str,
    action: str,
    *,
    source: str,
    relation_tag: str | None = None,
) -> tuple[dict, dict]:
    ph = prompt_hash(prompt)
    rel = relation_tag or detect_relation_tag(prompt) or "procedure_reuse"
    contrastive = {
        "prompt_hash": ph,
        "relation_id": rel,
        "anchor": prompt,
        "positive": f"{skill_id}:{action}",
        "negative": "skip_unrelated",
        "source": source,
        "skill_id": skill_id,
        "expected_action": action,
    }
    instruction = {
        "prompt_hash": ph,
        "relation_id": rel,
        "instruction": f"Route skill {skill_id} with verifier action {action}",
        "input": prompt,
        "output": action,
        "source": source,
        "skill_id": skill_id,
    }
    return contrastive, instruction


def build_correction_rows() -> tuple[list[dict], list[dict]]:
    """Rows from verifier eval bridge cases and routing-related error_log entries."""
    contrastive: list[dict] = []
    instruction: list[dict] = []

    if VERIFIER_EVAL.is_file():
        data = json.loads(VERIFIER_EVAL.read_text(encoding="utf-8"))
        for case in data.get("cases") or []:
            if case.get("source") != "verifier_learning_bridge" and not str(case.get("id", "")).startswith(
                "case_from_correction"
            ):
                continue
            inp = case.get("input") or {}
            prompt = inp.get("prompt") or inp.get("text") or ""
            skill_id = case.get("skill_id")
            action = None
            for a in case.get("assertions") or []:
                val = a.get("value") or ""
                if '"action"' in val:
                    for act in ("ACCEPT", "SKIP", "DECOMPOSE", "REWRITE"):
                        if act in val:
                            action = act
                            break
            if not prompt or not skill_id or not action:
                continue
            c, i = _rows_from_correction(
                prompt, skill_id, action, source="verifier_learning_bridge"
            )
            contrastive.append(c)
            instruction.append(i)

    if ERROR_LOG.is_file():
        for line in ERROR_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            blob = " ".join(
                str(entry.get(k) or "")
                for k in ("ctx", "err", "fix", "cat")
            )
            if not _ROUTING_KEYWORDS.search(blob):
                continue
            prompt = entry.get("ctx") or entry.get("err") or ""
            if len(prompt.strip()) < 12:
                continue
            skill_match = re.search(r"skill[_-]?id[:\s]+([a-z0-9\-]+)", blob, re.I)
            action_match = re.search(r"\b(ACCEPT|SKIP|DECOMPOSE|REWRITE)\b", blob)
            skill_id = skill_match.group(1) if skill_match else "notebooklm-research-gate"
            action = action_match.group(1) if action_match else "ACCEPT"
            c, i = _rows_from_correction(
                prompt[:500],
                skill_id,
                action,
                source="error_log_routing",
            )
            contrastive.append(c)
            instruction.append(i)

    return contrastive, instruction


def build_live_rows(ledger_path: Path | None = None) -> tuple[list[dict], list[dict]]:
    contrastive: list[dict] = []
    instruction: list[dict] = []
    for row in read_rows(ledger_path):
        if row.get("event") != "beforeSubmitPrompt":
            continue
        prompt = row.get("prompt_preview") or ""
        if not prompt:
            continue
        rel = row.get("relation_tag") or "procedure_reuse"
        for d in row.get("decisions") or []:
            sid = d.get("id")
            action = d.get("action")
            if not sid or not action:
                continue
            c, i = _rows_from_correction(
                prompt,
                sid,
                action,
                source="verifier_usage_ledger",
                relation_tag=rel,
            )
            contrastive.append(c)
            instruction.append(i)

    corr_c, corr_i = build_correction_rows()
    contrastive.extend(corr_c)
    instruction.extend(corr_i)
    return contrastive, instruction


def main() -> int:
    parser = argparse.ArgumentParser(description="Append live Rcml training rows from verifier ledger")
    parser.add_argument("--ledger", default="", help="Path to verifier_usage_ledger.jsonl")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--merge-seed", action="store_true", default=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ledger = Path(args.ledger).expanduser() if args.ledger else None
    live_c, live_i = build_live_rows(ledger)

    out_dir = Path(args.output_dir)
    c_path = out_dir / "live_contrastive.jsonl"
    i_path = out_dir / "live_instruction.jsonl"

    seen_c = _load_existing_hashes(c_path)
    seen_i = _load_existing_hashes(i_path)
    new_c = [r for r in live_c if r.get("prompt_hash") not in seen_c]
    new_i = [r for r in live_i if r.get("prompt_hash") not in seen_i]

    if args.json:
        payload = {
            "new_contrastive": new_c,
            "new_instruction": new_i,
            "correction_rows": len(build_correction_rows()[0]),
        }
        if args.merge_seed:
            reg = load_rcml_registry()
            payload["seed_contrastive_count"] = len(export_contrastive_jsonl(reg))
            payload["seed_instruction_count"] = len(export_instruction_jsonl(reg))
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    n_c = _append_jsonl(c_path, new_c)
    n_i = _append_jsonl(i_path, new_i)

    if args.merge_seed:
        reg = load_rcml_registry()
        seed_c = out_dir / "rcml_contrastive.jsonl"
        seed_i = out_dir / "rcml_instruction.jsonl"
        if not seed_c.is_file():
            with seed_c.open("w", encoding="utf-8") as f:
                for row in export_contrastive_jsonl(reg):
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
        if not seed_i.is_file():
            with seed_i.open("w", encoding="utf-8") as f:
                for row in export_instruction_jsonl(reg):
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

    corr_count = len(build_correction_rows()[0])
    meta = {
        "appended_contrastive": n_c,
        "appended_instruction": n_i,
        "correction_rows_considered": corr_count,
        "dedup_skipped_contrastive": len(live_c) - n_c,
        "dedup_skipped_instruction": len(live_i) - n_i,
    }
    (out_dir / "live_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
