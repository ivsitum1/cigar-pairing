#!/usr/bin/env python3
"""Export Obsidian wiki wikilink graph to NetworkX node_link JSON (wiki-export/)."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_ROOT = REPO_ROOT / "20_knowledge" / "wiki"
EXPORT_DIR = REPO_ROOT / "wiki-export"
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]")
SKIP_NAMES = {"index.md", "log.md", "_insights.md"}
SKIP_PARTS = {
    "_raw",
    "_archives",
    "_meta",
    ".obsidian",
    "sources/books_md",
    "sources/books_md/",
}


def _should_skip(path: Path) -> bool:
    if path.name in SKIP_NAMES or path.name.startswith("."):
        return True
    rel = path.relative_to(WIKI_ROOT).as_posix()
    for part in SKIP_PARTS:
        if rel.startswith(part):
            return True
    return False


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    data: dict = {}
    for line in block.splitlines():
        if line.startswith("tags:"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip().strip('"').strip("'")
    tags: list[str] = []
    in_tags = False
    for line in block.splitlines():
        if line.strip() == "tags:":
            in_tags = True
            continue
        if in_tags:
            if line.startswith("  - "):
                tags.append(line[4:].strip())
            elif line and not line.startswith(" "):
                in_tags = False
    if tags:
        data["tags_list"] = tags
    return data


def _normalize_id(raw: str) -> str:
    return raw.strip().replace("\\", "/").removesuffix(".md").lower()


def build_graph(*, filtered: bool = False) -> dict:
    if not WIKI_ROOT.is_dir():
        raise FileNotFoundError(f"Wiki root missing: {WIKI_ROOT}")

    blocked_tags = {"visibility/internal", "visibility/pii"}
    pages: dict[str, dict] = {}
    bodies: dict[str, str] = {}

    for path in sorted(WIKI_ROOT.rglob("*.md")):
        if _should_skip(path):
            continue
        rel = path.relative_to(WIKI_ROOT)
        page_id = str(rel.with_suffix("")).replace("\\", "/")
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = _parse_frontmatter(text)
        tags = fm.get("tags_list", [])
        if filtered and blocked_tags.intersection(tags):
            continue
        category = page_id.split("/")[0] if "/" in page_id else "root"
        pages[page_id] = {
            "id": page_id,
            "label": fm.get("title") or path.stem.replace("-", " ").title(),
            "category": category,
            "tags": tags,
            "summary": fm.get("summary", ""),
            "graph_source": "wiki",
        }
        bodies[page_id] = text

    stem_index: dict[str, list[str]] = defaultdict(list)
    for pid in pages:
        stem_index[pid.split("/")[-1].lower()].append(pid)

    def resolve(target: str) -> str | None:
        norm = _normalize_id(target)
        if norm in pages:
            return norm
        stem = Path(target).stem.lower()
        cands = stem_index.get(stem, [])
        if len(cands) == 1:
            return cands[0]
        for c in cands:
            if c.lower().endswith(norm) or norm.endswith(c.split("/")[-1]):
                return c
        return None

    links: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for page_id, body in bodies.items():
        for m in WIKILINK_RE.finditer(body):
            target = resolve(m.group(1))
            if not target or target == page_id:
                continue
            key = (page_id, target)
            if key in seen:
                continue
            seen.add(key)
            links.append(
                {
                    "source": page_id,
                    "target": target,
                    "relation": "wikilink",
                    "confidence": "EXTRACTED",
                }
            )

    tag_counts = Counter(
        (pages[n]["tags"][0] if pages[n]["tags"] else "__none__") for n in pages
    )
    community_order = {t: i for i, (t, _) in enumerate(tag_counts.most_common())}
    for node in pages.values():
        dom = node["tags"][0] if node["tags"] else "__none__"
        node["community"] = community_order.get(dom)

    return {
        "directed": False,
        "multigraph": False,
        "graph": {
            "exported_at": datetime.now(UTC).isoformat(),
            "vault": str(WIKI_ROOT),
            "total_nodes": len(pages),
            "total_edges": len(links),
            "filtered": filtered,
        },
        "nodes": list(pages.values()),
        "links": links,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export wiki wikilink graph to wiki-export/graph.json")
    parser.add_argument("--filtered", action="store_true", help="Exclude visibility/internal and pii")
    parser.add_argument("--out", type=Path, default=EXPORT_DIR / "graph.json")
    args = parser.parse_args()

    data = build_graph(filtered=args.filtered)
    if len(data["nodes"]) < 5:
        print(f"WARN: only {len(data['nodes'])} wiki pages — export may be too sparse.", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"OK: {args.out} — {data['graph']['total_nodes']} nodes, "
        f"{data['graph']['total_edges']} edges",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
