#!/usr/bin/env python3
"""Validate backtick file references in .cursor/rules/*.mdc."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

BACKTICK_PATH = re.compile(
    r"`("
    r"(?:\./)?(?:30_system|40_operations|20_knowledge|\.cursor|\.agent)/[^\s`#]+"
    r"|(?:[a-z0-9_\-]+\.mdc)"
    r")`",
    re.IGNORECASE,
)

SKIP_PREFIXES = ("http://", "https://", "mailto:")


def is_template_reference(ref: str) -> bool:
    """Skip glob, placeholder, and pattern references."""
    template_markers = ("*", "<", ">", "{", "}", "…", "SKILL_<", "<id>", "<run_id>", "[topic]")
    return any(marker in ref for marker in template_markers)


def resolve_reference(ref: str, rules_dir: pathlib.Path, root: pathlib.Path) -> pathlib.Path | None:
    ref = ref.split("#", 1)[0].strip()
    if not ref or any(ref.startswith(p) for p in SKIP_PREFIXES):
        return None
    if is_template_reference(ref):
        return rules_dir / "__template__"  # treated as valid pattern reference

    candidates: list[pathlib.Path] = []
    if ref.endswith(".mdc") and "/" not in ref and "\\" not in ref:
        candidates.append(rules_dir / ref)
    elif ref.startswith((".cursor/", ".agent/", "30_system/", "40_operations/", "20_knowledge/")):
        candidates.append(root / ref.replace("/", pathlib.os.sep))
    elif ref.startswith("./"):
        candidates.append((rules_dir / ref[2:]).resolve())

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def scan_rules(rules_dir: pathlib.Path, root: pathlib.Path) -> list[tuple[str, str, str]]:
    missing: list[tuple[str, str, str]] = []
    for rule_file in sorted(rules_dir.glob("*.mdc")):
        text = rule_file.read_text(encoding="utf-8", errors="ignore")
        for match in BACKTICK_PATH.finditer(text):
            ref = match.group(1)
            if resolve_reference(ref, rules_dir, root) is None:
                missing.append((rule_file.name, ref, "missing"))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate .mdc rule file references.")
    parser.add_argument("--root", default=".", help="Workspace root.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    rules_dir = root / ".cursor" / "rules"
    if not rules_dir.is_dir():
        print(f"Rules directory not found: {rules_dir}", file=sys.stderr)
        return 2

    missing = scan_rules(rules_dir, root)
    if args.json:
        import json

        print(json.dumps({"missing_count": len(missing), "missing": missing}, indent=2))
    else:
        print(f"Rules scanned: {len(list(rules_dir.glob('*.mdc')))}")
        print(f"Missing references: {len(missing)}")
        for rule, ref, reason in missing:
            print(f"  {rule}: `{ref}` ({reason})")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
