#!/usr/bin/env python3
"""Link agent-rules (parent) skills, rules, hooks, and ops into agent-brain-lite."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = BRAIN_ROOT / "harness" / "parent_rules_manifest.json"
LINKS_STATE = BRAIN_ROOT / ".cursor" / "rules" / ".parent_links.json"
DEFAULT_PARENT = Path(r"C:\Users\Ivan\OneDrive\Dokumenti\agent rules")
LITE_HOOK_ENTRY = {
    "command": "py .cursor/hooks/learning_lifecycle.py",
    "timeout": 10,
}


def load_parent_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    env_file = BRAIN_ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("PARENT_BRAIN_PATH="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return Path(value).resolve()
    if DEFAULT_PARENT.is_dir():
        return DEFAULT_PARENT.resolve()
    raise SystemExit(
        "Parent brain path not found. Set PARENT_BRAIN_PATH in .env or pass --parent."
    )


def is_reparse_point(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_symlink():
        return True
    if os.name != "nt":
        return path.is_symlink()
    try:
        import stat

        return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return False


def remove_link(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        if is_reparse_point(path):
            path.rmdir()
            return
        raise RuntimeError(f"Refusing to remove real directory: {path}")
    path.unlink()


def create_dir_link(link: Path, target: Path) -> None:
    target = target.resolve()
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.exists() or link.is_symlink():
        remove_link(link)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        os.symlink(target, link, target_is_directory=True)


def create_file_link(link: Path, target: Path) -> None:
    target = target.resolve()
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.exists() or link.is_symlink():
        remove_link(link)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", str(link), str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        os.symlink(target, link)


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def link_parent_rules(parent: Path, manifest: dict) -> list[str]:
    rules_src = parent / ".cursor" / "rules"
    rules_dst = BRAIN_ROOT / ".cursor" / "rules"
    rules_dst.mkdir(parents=True, exist_ok=True)
    exclude = set(manifest.get("exclude_rules", []))
    lite_only = set(manifest.get("lite_only_rules", []))
    linked: list[str] = []

    if not rules_src.is_dir():
        raise SystemExit(f"Parent rules not found: {rules_src}")

    for src in sorted(rules_src.glob("*.mdc")):
        name = src.name
        if name in exclude or name in lite_only:
            continue
        dst = rules_dst / name
        create_file_link(dst, src)
        linked.append(name)
    return linked


def link_parent_hook_scripts(parent: Path, manifest: dict) -> list[str]:
    hooks_src = parent / ".cursor" / "hooks"
    hooks_dst = BRAIN_ROOT / ".cursor" / "hooks"
    hooks_dst.mkdir(parents=True, exist_ok=True)
    lite_only = set(manifest.get("lite_only_hooks", ["learning_lifecycle.py"]))
    linked: list[str] = []

    if not hooks_src.is_dir():
        return linked

    for src in sorted(hooks_src.glob("*.py")):
        if src.name in lite_only:
            continue
        dst = hooks_dst / src.name
        create_file_link(dst, src)
        linked.append(src.name)
    return linked


def merge_hooks_json(parent: Path) -> None:
    parent_path = parent / ".cursor" / "hooks.json"
    dst = BRAIN_ROOT / ".cursor" / "hooks.json"
    if parent_path.is_file():
        merged = json.loads(parent_path.read_text(encoding="utf-8"))
    else:
        merged = {"version": 1, "hooks": {}}
    hooks = merged.setdefault("hooks", {})
    for event in ("sessionEnd", "stop"):
        entries = hooks.setdefault(event, [])
        commands = {e.get("command") for e in entries if isinstance(e, dict)}
        if LITE_HOOK_ENTRY["command"] not in commands:
            entries.append(dict(LITE_HOOK_ENTRY))
    dst.write_text(json.dumps(merged, indent=2), encoding="utf-8")


def ensure_agent_scaffold() -> None:
    for rel in [
        ".agent/memory",
        ".agent/task",
        "knowledge/learnings",
    ]:
        (BRAIN_ROOT / rel).mkdir(parents=True, exist_ok=True)


def link_parent_assets(parent: Path, manifest: dict) -> None:
    if manifest.get("symlink_30_system", True):
        create_dir_link(BRAIN_ROOT / "30_system", parent / "30_system")

    if manifest.get("symlink_40_operations", True):
        ops = parent / "40_operations"
        if ops.is_dir():
            create_dir_link(BRAIN_ROOT / "40_operations", ops)

    if manifest.get("symlink_memory_engine", True):
        mem = parent / "memory_engine"
        if mem.is_dir():
            create_dir_link(BRAIN_ROOT / "memory_engine", mem)

    if manifest.get("symlink_mcp_json", True):
        create_file_link(BRAIN_ROOT / ".cursor" / "mcp.json", parent / ".cursor" / "mcp.json")

    if manifest.get("symlink_cursor_docs", True):
        docs_src = parent / ".cursor" / "docs"
        if docs_src.is_dir():
            create_dir_link(BRAIN_ROOT / ".cursor" / "docs", docs_src)


def write_state(
    parent: Path,
    linked_rules: list[str],
    linked_hooks: list[str],
) -> None:
    payload = {
        "parent_path": str(parent),
        "linked_rules": linked_rules,
        "linked_hooks": linked_hooks,
        "manifest_version": load_manifest().get("version", "1.0"),
        "learning_loop": {
            "layer1": "knowledge/learnings + learning_log.py ingest-block",
            "layer2": "40_operations + memory_engine + parent hooks",
            "layer3": ".agent/learning.jsonl + learning_lifecycle.py",
        },
    }
    LINKS_STATE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Link parent agent-rules into brain-lite")
    parser.add_argument("--parent", help="Path to agent-rules repo")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    parent = load_parent_path(args.parent)
    if not parent.is_dir():
        raise SystemExit(f"Parent path is not a directory: {parent}")

    manifest = load_manifest()
    print(f"Brain root: {BRAIN_ROOT}")
    print(f"Parent:     {parent}")

    if args.dry_run:
        print("Would link: 30_system, 40_operations, memory_engine, mcp.json, docs")
        print("Would symlink parent hook scripts + merge hooks.json with lite learning hook")
        return 0

    linked_rules = link_parent_rules(parent, manifest)
    linked_hooks: list[str] = []
    if manifest.get("symlink_parent_hooks", True):
        linked_hooks = link_parent_hook_scripts(parent, manifest)
    link_parent_assets(parent, manifest)
    if manifest.get("merge_hooks_json", True):
        merge_hooks_json(parent)
    ensure_agent_scaffold()
    write_state(parent, linked_rules, linked_hooks)

    print(f"Linked {len(linked_rules)} parent rules into .cursor/rules/")
    print(f"Linked {len(linked_hooks)} parent hook scripts into .cursor/hooks/")
    print("Linked 30_system/, 40_operations/, memory_engine/, mcp.json, docs/")
    print("Merged hooks.json (parent + lite learning_lifecycle)")
    print("Lite-only: 00_orchestrator, wiki-markdown, parent-inherit, learning-loop-lite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
