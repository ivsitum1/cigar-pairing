#!/usr/bin/env python3
"""Audit skill and MCP trust tier assignments."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
REGISTRY = WORKSPACE / "30_system" / "SKILLS" / "registry.json"
MCP_TRUST = WORKSPACE / "30_system" / "docs" / "mcp_trust_registry.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit trust tiers")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    mcp = json.loads(MCP_TRUST.read_text(encoding="utf-8")) if MCP_TRUST.is_file() else {}

    by_tier: dict[int, list[str]] = {1: [], 2: [], 3: [], 4: []}
    missing: list[str] = []
    for skill in reg.get("skills", []):
        sid = skill.get("id", "?")
        tier = skill.get("trust_tier")
        if tier in by_tier:
            by_tier[int(tier)].append(sid)
        else:
            missing.append(sid)

    report = {
        "skills_total": len(reg.get("skills", [])),
        "skills_missing_tier": missing,
        "skills_by_tier": {str(k): v for k, v in by_tier.items()},
        "default_new_skill": reg.get("trust_tier_policy", {}).get("default_new_skill", 3),
        "mcp_servers": mcp.get("servers", {}),
        "mcp_default": mcp.get("default_new_server", 3),
        "pass": len(missing) == 0,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for t in (1, 2, 3, 4):
            print(f"T{t}: {len(by_tier[t])} skills")
        if missing:
            print(f"MISSING: {missing}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
