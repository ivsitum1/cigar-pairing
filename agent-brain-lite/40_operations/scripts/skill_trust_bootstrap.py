#!/usr/bin/env python3
"""Assign trust_tier to registry skills missing the field. Idempotent."""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
REGISTRY = WORKSPACE / "30_system" / "SKILLS" / "registry.json"

# T4 = curated brain skills (guidance / local-only). T3 = external IO or execution.
T4_IDS = {
    "agentic-react-os",
    "avoid-ai-formulations",
    "ai-detection",
    "consort-checklist",
    "prisma-checklist",
    "strobe-checklist",
    "setup-project",
    "swiss-cheese",
    "impl-validator",
    "test-selection",
    "eda-flexplot",
    "skill-creator",
    "grill-me",
    "write-prd",
    "prd-to-issues",
    "ralph-loop",
    "skill-dag-router",
    "skill-decompose",
    "harness_tdd",
    "wiki-lint",
    "wiki-status",
    "wiki-query",
    "wiki-setup",
    "wiki-switch",
    "manuscript-structure",
    "nonacademic-writer",
    "writing-avoid-ai",
}

T3_KEYWORDS = (
    "notebooklm",
    "research-lookup",
    "meta-analysis",
    "literature",
    "ingest",
    "pubmed",
    "consensus",
    "discovery",
    "clinical",
    "arxiv",
    "data-ingest",
    "books",
    "export",
    "rebuild",
    "capture",
    "history",
    "openclaw",
)


def infer_tier(skill: dict) -> int:
    if skill.get("trust_tier") in {1, 2, 3, 4}:
        return int(skill["trust_tier"])
    sid = skill.get("id", "")
    if sid in T4_IDS:
        return 4
    blob = f"{sid} {' '.join(skill.get('triggers', []))}".lower()
    if any(k in blob for k in T3_KEYWORDS):
        return 3
    domain = skill.get("domain", "")
    if domain in {"tools", "discovery", "clinical"}:
        return 3
    return 4


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if "trust_tier_policy" not in data:
        data["trust_tier_policy"] = {
            "schema_version": 1,
            "default_new_skill": 3,
            "tiers": {
                "1": "metadata_only — name/description index only",
                "2": "instruction_access — load SKILL text into context",
                "3": "supervised_execution — bash/write/MCP requires approval",
                "4": "autonomous_execution — full rights within workspace sandbox",
            },
            "mcp_registry": "30_system/docs/mcp_trust_registry.json",
            "auditor": "40_operations/scripts/skill_auditor.py",
        }
    changed = 0
    for skill in data.get("skills", []):
        if skill.get("trust_tier") not in {1, 2, 3, 4}:
            skill["trust_tier"] = infer_tier(skill)
            changed += 1
    REGISTRY.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": changed, "total": len(data.get("skills", []))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
