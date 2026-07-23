#!/usr/bin/env python3
"""OKF-1 pilot: read-only export of wiki subtree to OKF-style index manifest.

Does not replace Obsidian wikilinks. Spike: 30_system/docs/spikes/okf_wiki_bridge.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_WIKI = WORKSPACE / "20_knowledge" / "wiki"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


def collect_entries(root: Path, subdir: str, limit: int) -> list[dict[str, str]]:
    base = root / subdir if subdir else root
    if not base.is_dir():
        return []
    entries: list[dict[str, str]] = []
    for path in sorted(base.rglob("*.md")):
        if path.name.startswith("."):
            continue
        rel = path.relative_to(root).as_posix()
        title = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace")).get("title")
        if not title:
            title = path.stem.replace("_", " ")
        entries.append({"path": rel, "title": title, "format": "markdown"})
        if len(entries) >= limit:
            break
    return entries


def build_manifest(root: Path, subdir: str, limit: int) -> dict[str, object]:
    return {
        "schema": "okf-wiki-export-pilot",
        "version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(root.relative_to(WORKSPACE)).replace("\\", "/"),
        "subdir": subdir or ".",
        "canonical_layer": "obsidian_markdown",
        "read_only": True,
        "entries": collect_entries(root, subdir, limit),
        "note": "Pilot export; OKF spec URL must be verified before production GO.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="OKF wiki export pilot (read-only)")
    parser.add_argument("--wiki-root", type=Path, default=DEFAULT_WIKI)
    parser.add_argument("--subdir", default="concepts", help="Subfolder under wiki root")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--out", type=Path, help="Output JSON path")
    parser.add_argument("--json", action="store_true", help="Print manifest to stdout")
    args = parser.parse_args()

    root = args.wiki_root.resolve()
    if not root.is_dir():
        print(f"ERROR: wiki root not found: {root}", file=sys.stderr)
        return 1

    manifest = build_manifest(root, args.subdir, args.limit)
    text = json.dumps(manifest, ensure_ascii=False, indent=2)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out} ({len(manifest['entries'])} entries)")
    if args.json or not args.out:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
