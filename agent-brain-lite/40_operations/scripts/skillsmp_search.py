#!/usr/bin/env python3
"""Single-query SkillsMP search; prints JSON or human summary."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request

API = "https://skillsmp.com/api/v1/skills/search"


def search(query: str, limit: int = 12, sort_by: str = "stars") -> dict:
    url = (
        f"{API}?q={urllib.parse.quote(query)}"
        f"&limit={limit}&sortBy={sort_by}"
    )
    with urllib.request.urlopen(url, timeout=40) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    parser = argparse.ArgumentParser(description="Search SkillsMP for agent skills")
    parser.add_argument("query", help="Search keywords")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--sort", choices=["stars", "recent"], default="stars")
    parser.add_argument("--json", action="store_true", help="Raw JSON response")
    args = parser.parse_args()

    try:
        data = search(args.query, limit=args.limit, sort_by=args.sort)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    skills = data.get("data", {}).get("skills", [])
    print(f"Query: {args.query!r}  hits: {len(skills)}\n")
    for i, s in enumerate(skills, 1):
        print(f"{i}. {s.get('author')}/{s.get('name')}  stars={s.get('stars')}")
        desc = (s.get("description") or "").replace("\n", " ")[:200]
        print(f"   {desc}")
        print(f"   {s.get('githubUrl')}")
        print(f"   {s.get('skillUrl')}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
