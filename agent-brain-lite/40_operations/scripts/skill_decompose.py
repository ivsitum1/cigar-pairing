#!/usr/bin/env python3
"""Decompose a SKILL file into SkillRAE subunit graph JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.skill_decompose import decompose_by_id, write_graph  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="SkillRAE skill decomposition")
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--write", action="store_true", help="Write to outputs/skillrae/")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.write:
        out = write_graph(args.skill_id)
        print(str(out))
        return 0
    graph = decompose_by_id(args.skill_id)
    if args.json:
        print(json.dumps(graph, ensure_ascii=False, indent=2))
    else:
        print(f"skill_id={graph['skill_id']} nodes={len(graph['nodes'])} edges={len(graph['edges'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
