#!/usr/bin/env python3
"""Inventory tracked files and verify Python compiles (full-workspace smoke). Exit 0 if ok."""
from __future__ import annotations

import argparse
import compileall
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = ROOT / "30_system" / "SKILLS"
REGISTRY_PATH = SKILLS_DIR / "registry.json"


def check_skill_registry() -> tuple[bool, str]:
    """Registry skill count must match SKILL_*.md files (excluding _template)."""
    if not REGISTRY_PATH.exists():
        return False, "registry.json missing"
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_files = {s["file"] for s in registry.get("skills", [])}
    on_disk = {
        f.name
        for f in SKILLS_DIR.glob("SKILL_*.md")
        if "_template" not in f.as_posix()
    }
    orphans = on_disk - registry_files
    missing = registry_files - on_disk
    if orphans or missing:
        parts = []
        if orphans:
            parts.append(f"orphans={sorted(orphans)[:5]}")
        if missing:
            parts.append(f"missing={sorted(missing)[:5]}")
        return False, "; ".join(parts)
    return True, f"ok ({len(registry_files)} skills)"


def git_tracked_files(root: Path) -> list[str]:
    r = subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Git file inventory + Python compileall smoke.")
    parser.add_argument("--json", action="store_true", help="Machine-readable summary")
    args = parser.parse_args()

    tracked = git_tracked_files(ROOT)
    if not tracked:
        msg = "git ls-files failed or empty (not a git repo?)"
        if args.json:
            print(json.dumps({"ok": False, "error": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1

    exts = Counter(Path(p).suffix.lower() or "(noext)" for p in tracked)
    py_roots = {ROOT / "40_operations", ROOT / ".cursor" / "scripts", ROOT / "30_system" / "behavior_rules" / "tools"}

    ok_compile = True
    compiled_dirs = []
    for d in sorted(py_roots):
        if d.is_dir():
            compiled_dirs.append(str(d.relative_to(ROOT)))
            if not compileall.compile_dir(str(d), quiet=1):
                ok_compile = False

    ok_registry, registry_msg = check_skill_registry()
    ok = ok_compile and ok_registry

    report = {
        "ok": ok,
        "tracked_file_count": len(tracked),
        "extension_top": dict(exts.most_common(15)),
        "compileall_dirs": compiled_dirs,
        "skill_registry": registry_msg,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== WORKSPACE INVENTORY AUDIT ===")
        print(f"Project root: {ROOT}")
        print(f"git ls-files: {len(tracked)} paths")
        print("Top extensions:", ", ".join(f"{k}:{v}" for k, v in exts.most_common(10)))
        print("compileall:", "PASS" if ok_compile else "FAIL")
        for d in compiled_dirs:
            print(f"  - {d}")
        print("skill_registry:", registry_msg)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
