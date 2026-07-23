#!/usr/bin/env python3
"""Validate verifier_registry.json schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT = WORKSPACE / "30_system" / "docs" / "verifier_registry.json"
AGENT_REG = WORKSPACE / "30_system" / "SKILLS" / "registry.json"
VALID_ACTIONS = {"ACCEPT", "DECOMPOSE", "REWRITE", "SKIP", None}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"Missing: {path}"]

    data = json.loads(path.read_text(encoding="utf-8"))
    agent_ids = set()
    if AGENT_REG.is_file():
        agent = json.loads(AGENT_REG.read_text(encoding="utf-8"))
        agent_ids = {s["id"] for s in agent.get("skills") or [] if s.get("id")}

    seen: set[str] = set()
    for row in data.get("skill_policies") or []:
        sid = row.get("skill_id")
        if not sid:
            errors.append("skill_policies row missing skill_id")
            continue
        if sid in seen:
            errors.append(f"Duplicate skill_id in skill_policies: {sid}")
        seen.add(sid)
        if agent_ids and sid not in agent_ids:
            errors.append(f"skill_id not in agent registry: {sid}")
        force = row.get("force_action")
        if force and force not in {"ACCEPT", "DECOMPOSE", "REWRITE", "SKIP"}:
            errors.append(f"Invalid force_action for {sid}: {force}")

    for row in data.get("relation_overrides") or []:
        if not row.get("relation_tag"):
            errors.append("relation_overrides row missing relation_tag")

    return errors


def main() -> int:
    path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT
    errors = validate(path)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
