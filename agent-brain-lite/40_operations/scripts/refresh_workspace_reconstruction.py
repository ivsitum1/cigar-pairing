#!/usr/bin/env python3
"""Refresh workspace_reconstruction.json tier/skills metadata from live registry."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = ROOT / "30_system" / "SKILLS" / "registry.json"
OUT = ROOT / "workspace_reconstruction.json"


def main() -> int:
    if not REGISTRY.exists():
        print(f"Missing {REGISTRY}", file=__import__("sys").stderr)
        return 1
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    skill_files = [s["file"] for s in registry["skills"]]

    if OUT.exists():
        data = json.loads(OUT.read_text(encoding="utf-8"))
    else:
        data = {}

    data.setdefault("workspace_meta", {})
    data["workspace_meta"].update(
        {
            "name": "agent-rules",
            "type": "brain",
            "version": "1.1",
            "generated": "2026-05-26",
            "skills_canonical": "30_system/SKILLS/registry.json",
        }
    )

    data.setdefault("cursor_rules", {})
    data["cursor_rules"]["tier_0_always"] = [
        "00_orchestrator_agent.mdc",
        "core-principles.mdc",
        "context-optimization.mdc",
        "general-rules.mdc",
        "skills-auto-detect.mdc",
        "99_error_memory.mdc",
        "agent-rules-readonly-when-referenced.mdc",
        "98_honesty_grounding_protocol.mdc",
    ]
    data["cursor_rules"]["tier_budget_authority"] = ".cursor/rules/context-optimization.mdc v3.2"
    data["cursor_rules"]["tier_0_tokens"] = "3000-3800"
    data["cursor_rules"]["tier_3_max_active_skills"] = registry.get("max_active_skills", 2)

    data["skills"] = {
        "path": "30_system/SKILLS/",
        "registry": "30_system/SKILLS/registry.json",
        "count": len(skill_files),
        "files": skill_files,
        "note": "Auto-refreshed; do not edit files list by hand.",
    }

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {OUT} ({len(skill_files)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
