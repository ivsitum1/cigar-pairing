#!/usr/bin/env python3
"""Ensure minimal Obsidian hub wikilinks on every books_md note (no RAG rebuild)."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

BOOKS_MD = Path("20_knowledge/wiki/sources/books_md")
WIKI_INDEX = "[[20_knowledge/wiki/index]]"
BOOKS_INDEX = "[[20_knowledge/wiki/sources/books_md/INDEX]]"
REF_ACCESS = "[[30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS]]"
HUB_HEADING = "## Agent and graph hubs"
DOMAIN_LINK_PREFIX = "- Domain shelf: "
INDEX_WIKI = "20_knowledge/wiki/sources/books_md/INDEX"

_FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def _domain_key(md_path: Path, books_root: Path) -> str:
    rel = md_path.relative_to(books_root)
    if len(rel.parts) < 2:
        return rel.parent.name or "inbox_raw"
    return rel.parts[0]


def _domain_link(domain_key: str) -> str:
    return f"{DOMAIN_LINK_PREFIX}[[{INDEX_WIKI}#{domain_key}]]"


def _hub_block(domain_key: str, pdf_line: str | None = None) -> str:
    lines = [
        HUB_HEADING,
        "",
        f"- {WIKI_INDEX}",
        f"- {BOOKS_INDEX}",
        _domain_link(domain_key),
        f"- {REF_ACCESS}",
    ]
    if pdf_line:
        lines.append(pdf_line)
    lines.append("")
    return "\n".join(lines)


def _extract_pdf_line(body: str) -> str | None:
    for line in body.splitlines():
        if line.strip().startswith("- Original PDF:") or line.strip().startswith("Open PDF:"):
            if line.strip().startswith("Open PDF:"):
                return f"- Original PDF: `{line.split('`', 2)[1] if '`' in line else line.split(':', 1)[-1].strip()}`"
            return line.strip()
    m = re.search(r"`(20_knowledge/reference_library/[^`]+)`", body)
    if m:
        return f"- Original PDF: `{m.group(1)}`"
    return None


def _insert_hub_after_frontmatter(text: str, hub: str) -> str:
    m = _FRONTMATTER_RE.match(text)
    if m:
        return text[: m.end()] + hub + text[m.end() :].lstrip("\n")
    return hub + text


def _ensure_domain_in_hub(body: str, domain_key: str) -> tuple[str, bool]:
    link = _domain_link(domain_key)
    if link in body:
        return body, False
    if HUB_HEADING not in body:
        return body, False
    lines = body.splitlines()
    out: list[str] = []
    inserted = False
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if not inserted and lines[i].strip() == f"- {BOOKS_INDEX}":
            out.append(link)
            inserted = True
        i += 1
    if inserted:
        return "\n".join(out) + ("\n" if body.endswith("\n") else ""), True
    return body, False


def patch_file(path: Path, books_root: Path, *, dry_run: bool) -> str:
    """Return action: skip | domain_added | hub_added | unchanged."""
    if path.name == "INDEX.md":
        return "skip"
    domain_key = _domain_key(path, books_root)
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text

    if HUB_HEADING not in text:
        pdf_line = _extract_pdf_line(text)
        hub = _hub_block(domain_key, pdf_line)
        text = _insert_hub_after_frontmatter(text, hub)
        action = "hub_added"
    else:
        text, changed = _ensure_domain_in_hub(text, domain_key)
        action = "domain_added" if changed else "unchanged"

    if text != original and not dry_run:
        path.write_text(text, encoding="utf-8")
    elif text == original:
        action = "unchanged"
    return action


def main() -> int:
    parser = argparse.ArgumentParser(description="Add minimal Obsidian hub links to books_md notes.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not write")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    books_root = root / BOOKS_MD
    if not books_root.is_dir():
        print(f"Missing {books_root}", file=__import__("sys").stderr)
        return 1

    stats = {"hub_added": 0, "domain_added": 0, "unchanged": 0, "skip": 0}
    for md in sorted(books_root.rglob("*.md")):
        action = patch_file(md, books_root, dry_run=args.dry_run)
        stats[action] = stats.get(action, 0) + 1

    mode = "dry-run" if args.dry_run else "applied"
    print(f"[{mode}] {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
