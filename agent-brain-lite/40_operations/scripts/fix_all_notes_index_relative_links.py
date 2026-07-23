#!/usr/bin/env python3
"""Repair ALL_NOTES_INDEX.md link targets from ``30_system/docs/``.

Bullets use broken prefixes such as ``../.agent/`` (resolves under ``30_system/``) or
``../30_system/...`` (double ``30_system``). Rewrites **href only** on ``- [label](href)``
lines; leaves prose untouched.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

BULLET_LINK = re.compile(r"^(?P<pre>- )(?P<label>\[[^\]]+\])(?P<lp>\()(?P<href>[^)]+)(?P<rp>\))\s*$")


def fix_href(href: str) -> tuple[str, str]:
    """Return (path_part, fragment)."""
    if href.startswith(("http://", "https://", "mailto:")):
        return href, ""
    if "#" in href:
        path_part, frag = href.split("#", 1)
        return path_part, "#" + frag
    return href, ""


def rewrite_href(path_part: str) -> str:
    """Apply prefix fixes for paths starting with ``../``."""
    if not path_part.startswith("../"):
        return path_part
    h = path_part
    if h.startswith("../30_system/"):
        return "../" + h[len("../30_system/") :]
    if h.startswith("../.agent/"):
        return "../../.agent/" + h[len("../.agent/") :]
    if h.startswith("../.ai/"):
        return "../../.ai/" + h[len("../.ai/") :]
    if h.startswith("../.cursor/"):
        return "../../.cursor/" + h[len("../.cursor/") :]
    if h.startswith("../.pytest_cache/"):
        return "../../.pytest_cache/" + h[len("../.pytest_cache/") :]
    if h.startswith("../20_knowledge/"):
        return "../../20_knowledge/" + h[len("../20_knowledge/") :]
    if h.startswith("../40_operations/"):
        return "../../40_operations/" + h[len("../40_operations/") :]
    if h.startswith("../90_archive/"):
        return "../../90_archive/" + h[len("../90_archive/") :]
    if h == "../index.md":
        return "../../index.md"
    if h == "../README.md":
        return "../../README.md"
    if h.startswith("../README-") and h != "../README.md":
        return "../../README.md"
    return h


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair ALL_NOTES_INDEX.md relative links.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    path = root / "30_system/docs/ALL_NOTES_INDEX.md"
    base = path.parent
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    changed = 0

    for line in lines:
        if "MD_FUNCTIONAL_GRAPH.md" in line and line.strip().startswith("- ["):
            changed += 1
            continue
        m = BULLET_LINK.match(line)
        if not m:
            out.append(line)
            continue
        label = m.group("label")[1:-1].strip()
        href_full = m.group("href").strip()
        path_part, frag = fix_href(href_full)
        new_path = rewrite_href(path_part)
        # Prefer existing file named like label (fixes ../.../index.md vs README.md)
        if label.endswith(".md"):
            cand = (root / label.replace("\\", "/")).resolve()
            try:
                cand.relative_to(root)
            except ValueError:
                cand = Path()
            if cand.is_file():
                new_path = os.path.relpath(cand, base).replace("\\", "/")
        new_href = new_path + frag
        new_line = f'{m.group("pre")}{m.group("label")}({new_href})'
        if new_line != line:
            changed += 1
        out.append(new_line)

    new_text = "\n".join(out) + "\n"
    if not args.dry_run:
        path.write_text(new_text, encoding="utf-8")
    print(f"lines_changed_or_dropped: {changed}" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
