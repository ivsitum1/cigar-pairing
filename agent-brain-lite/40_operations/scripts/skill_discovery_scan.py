#!/usr/bin/env python3
"""Scan agent-rules brain for matching skills (registry + SKILL files)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "30_system" / "SKILLS" / "registry.json"
SKILLS_DIR = ROOT / "30_system" / "SKILLS"
MAPPING = ROOT / "30_system" / "behavior_rules" / "reference" / "skill_task_mapping.md"


def tokenize(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[a-z0-9\u0107\u010d\u0111\u0161\u017e]{2,}", text.lower())}


def score_query(query: str, haystack: str) -> int:
    q = tokenize(query)
    if not q:
        return 0
    h = haystack.lower()
    return sum(1 for t in q if t in h)


def phrase_trigger_bonus(query: str, triggers: list[str]) -> int:
    """Boost when the user query contains a full registry trigger phrase."""
    q = query.lower()
    bonus = 0
    for trig in triggers:
        t = (trig or "").strip().lower()
        if len(t) >= 4 and t in q:
            bonus = max(bonus, 10 + len(t) // 4)
    return bonus


def load_registry() -> list[dict]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return data.get("skills", [])


def main() -> int:
    parser = argparse.ArgumentParser(description="Local skill discovery in agent-rules")
    parser.add_argument("query", help="Keywords describing needed workflow")
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not REGISTRY.is_file():
        print("ERROR: registry.json not found", file=sys.stderr)
        return 1

    ranked: list[tuple[int, dict]] = []
    for entry in load_registry():
        skill_id = entry.get("id", "")
        triggers = " ".join(entry.get("triggers") or [])
        disambig = entry.get("disambiguation") or ""
        domain = entry.get("domain") or ""
        skill_file = SKILLS_DIR / f"SKILL_{skill_id}.md"
        file_exists = skill_file.is_file()
        body_preview = ""
        if file_exists:
            body_preview = skill_file.read_text(encoding="utf-8", errors="replace")[:800]
        haystack = f"{skill_id} {domain} {triggers} {disambig} {body_preview}"
        s = score_query(args.query, haystack) + phrase_trigger_bonus(
            args.query, entry.get("triggers") or []
        )
        if s > 0:
            ranked.append(
                (
                    s,
                    {
                        "id": skill_id,
                        "domain": domain,
                        "file": entry.get("file"),
                        "file_exists": file_exists,
                        "triggers": entry.get("triggers"),
                        "disambiguation": disambig,
                        "score": s,
                    },
                )
            )

    ranked.sort(key=lambda x: (-x[0], x[1]["id"]))
    results = [r[1] for r in ranked[: args.top]]

    missing_files = [
        e["id"]
        for e in load_registry()
        if not (SKILLS_DIR / f"SKILL_{e['id']}.md").is_file()
    ]

    out = {
        "query": args.query,
        "matches": results,
        "registry_skill_count": len(load_registry()),
        "registry_missing_skill_files": missing_files,
        "artifacts": {
            "skillsmp_report": str(ROOT / ".agent" / "task" / "skillsmp_detailed_report.md"),
            "skillsmp_search_results": str(ROOT / ".agent" / "task" / "skillsmp_search_results.json"),
            "zip_skill_inventory": str(ROOT / ".agent" / "task" / "zip_skill_inventory.json"),
        },
    }

    if args.json:
        payload = json.dumps(out, indent=2, ensure_ascii=False)
        sys.stdout.buffer.write(payload.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        return 0

    print(f"Local scan: {args.query!r}\n")
    if not results:
        print("No registry match. Run external search (see SKILL_skill-discovery).\n")
    for i, m in enumerate(results, 1):
        flag = "" if m["file_exists"] else " [MISSING SKILL FILE]"
        print(f"{i}. {m['id']} ({m['domain']}) score={m['score']}{flag}")
        print(f"   {m['disambiguation'][:160]}")
    if missing_files:
        print(f"\nRegistry entries without SKILL_*.md ({len(missing_files)}): {', '.join(missing_files[:12])}")
        if len(missing_files) > 12:
            print("  ...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
