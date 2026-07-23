#!/usr/bin/env python3
"""Broken internal-markdown-link checker for the workspace graph.

Scans markdown files for relative links (`[text](path)`) and reports targets
that do not exist on disk. External links (http/mailto), in-page anchors, and
Obsidian wikilinks (`[[...]]`) are ignored — only on-disk relative links are
validated.

Used both as a CLI report and as a CI regression gate: pass ``--max N`` to exit
non-zero when the broken count exceeds a baseline, so link rot cannot silently
grow even while the long tail of legacy breakage is worked down.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Directories that are archive / gitignored binary pointers — not part of the
# live graph, so excluded from the integrity gate.
# - _archive: notebooklm snapshot outputs (stale relative paths)
# - indexes: auto-generated folder indexes (link to gitignored books/inbox_raw)
# - inbox_raw: large book chunks not in git; indexes still reference them
DEFAULT_EXCLUDE = (
    ".git",
    "90_archive",
    "ARCHIVE",
    "__pycache__",
    ".pytest_cache",
    "_archive",
    "indexes",
    "inbox_raw",
)


def _skip_target(target: str) -> bool:
    """Skip links into gitignored or non-CI trees (archive, inbox_raw)."""
    norm = target.replace("\\", "/").lstrip("./")
    if norm.startswith(("http://", "https://", "mailto:", "#", "[[", "/")):
        return True
    if norm.startswith("90_archive/") or "/90_archive/" in f"/{norm}/":
        return True
    if "inbox_raw/" in norm or norm.startswith("inbox_raw/"):
        return True
    return False


def iter_md(root: Path, exclude: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    skip_names = {"ALL_NOTES_INDEX.md"}
    for p in root.rglob("*.md"):
        if p.name in skip_names:
            continue
        if any(part in exclude for part in p.relative_to(root).parts):
            continue
        out.append(p)
    return out


def find_broken(root: Path, exclude: tuple[str, ...]) -> list[tuple[Path, str]]:
    broken: list[tuple[Path, str]] = []
    for f in iter_md(root, exclude):
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in LINK_RE.finditer(txt):
            target = m.group(1).split("#")[0].strip()
            if not target or _skip_target(target):
                continue
            if not (f.parent / target).resolve().exists():
                broken.append((f, target))
    return broken


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="Workspace root")
    ap.add_argument("--max", type=int, default=None,
                    help="Fail (exit 1) if broken count exceeds this baseline.")
    ap.add_argument("--show", type=int, default=25, help="How many broken links to print.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    broken = find_broken(root, DEFAULT_EXCLUDE)
    print(f"Broken internal markdown links: {len(broken)}")
    for f, t in broken[: args.show]:
        print(f"  {f.relative_to(root).as_posix()} -> {t}")
    if len(broken) > args.show:
        print(f"  ... and {len(broken) - args.show} more")

    if args.max is not None and len(broken) > args.max:
        print(f"FAIL: broken links {len(broken)} exceed baseline {args.max}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
