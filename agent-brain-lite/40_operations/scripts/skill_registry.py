"""
Skill registry validator and mapping generator.

Usage:
    python 40_operations/scripts/skill_registry.py validate   # Check registry.json vs SKILL files
    python 40_operations/scripts/skill_registry.py generate    # Regenerate skill_task_mapping.md from registry
    python 40_operations/scripts/skill_registry.py list        # List all skills with domain and triggers
"""

import json
import sys
import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = WORKSPACE / "30_system/SKILLS"
REGISTRY_PATH = SKILLS_DIR / "registry.json"
MAPPING_PATH = WORKSPACE / "30_system/behavior_rules" / "reference" / "skill_task_mapping.md"


def load_registry() -> dict:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_yaml_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML front matter from a skill file (between --- delimiters)."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.+?)\n---", text, re.DOTALL)
    if not match:
        return None
    frontmatter = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith("  ") and not line.startswith("-"):
            key, _, val = line.partition(":")
            frontmatter[key.strip()] = val.strip()
    return frontmatter


def validate() -> list[str]:
    """Validate registry against actual skill files and their YAML front matter."""
    errors = []
    registry = load_registry()
    skill_ids = set()

    for skill in registry["skills"]:
        sid = skill["id"]
        if sid in skill_ids:
            errors.append(f"Duplicate skill ID: {sid}")
        skill_ids.add(sid)

        filepath = SKILLS_DIR / skill["file"]
        if not filepath.exists():
            errors.append(f"[{sid}] File not found: {skill['file']}")
            continue

        fm = extract_yaml_frontmatter(filepath)
        if fm is None:
            errors.append(f"[{sid}] No YAML front matter in {skill['file']}")
            continue

        if fm.get("name") != sid:
            errors.append(
                f"[{sid}] Front matter name mismatch: "
                f"registry='{sid}', file='{fm.get('name')}'"
            )

        if fm.get("domain") != skill.get("domain"):
            errors.append(
                f"[{sid}] Domain mismatch: "
                f"registry='{skill.get('domain')}', file='{fm.get('domain')}'"
            )

        gran = skill.get("granularity")
        if gran is not None:
            allowed = registry.get("dag_schema", {}).get("granularity_values") or [
                "policy",
                "strategy",
                "procedure",
                "primitive",
            ]
            if gran not in allowed:
                errors.append(f"[{sid}] Invalid granularity: {gran!r} (allowed: {allowed})")

        tier = skill.get("trust_tier")
        if tier is not None and tier not in {1, 2, 3, 4}:
            errors.append(f"[{sid}] Invalid trust_tier: {tier!r} (must be 1-4)")
        elif tier is None:
            errors.append(f"[{sid}] Missing trust_tier (run skill_trust_bootstrap.py)")

    existing_files = {f.name for f in SKILLS_DIR.glob("SKILL_*.md")}
    registry_files = {s["file"] for s in registry["skills"]}
    orphans = existing_files - registry_files
    for orphan in sorted(orphans):
        errors.append(f"Skill file not in registry: {orphan}")

    return errors


def generate_mapping():
    """Regenerate skill_task_mapping.md from registry.json."""
    registry = load_registry()
    lines = [
        "# Task → Skill Mapping – Full Reference",
        "",
        "**Purpose:** Complete mapping for skills-auto-detect. "
        "Used when grouped overview in skills-auto-detect.mdc is insufficient.",
        "",
        "**Auto-generated from** `30_system/SKILLS/registry.json` via "
        "`python 40_operations/scripts/skill_registry.py generate`.",
        "",
        "---",
        "",
        "## Full Table",
        "",
        "| Task / keywords (en) | Skill file to load | Domain | Disambiguation |",
        "|---|---|---|---|",
    ]

    for skill in registry["skills"]:
        triggers = ", ".join(skill["triggers"])
        lines.append(
            f"| {triggers} "
            f"| `{skill['file']}` "
            f"| {skill.get('domain', '')} "
            f"| {skill.get('disambiguation', '')} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "**Reference:** `.cursor/rules/skills-auto-detect.mdc`, "
        "`30_system/SKILLS/registry.json`",
    ])

    MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAPPING_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(MAPPING_PATH)


def list_skills():
    """Print a summary of all registered skills."""
    registry = load_registry()
    print(f"{'ID':<28} {'Domain':<14} Triggers")
    print("-" * 80)
    for skill in registry["skills"]:
        triggers = ", ".join(skill["triggers"][:3])
        if len(skill["triggers"]) > 3:
            triggers += ", ..."
        print(f"{skill['id']:<28} {skill.get('domain', ''):<14} {triggers}")
    print(f"\nTotal: {len(registry['skills'])} skills")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "validate":
        errors = validate()
        if errors:
            print(f"VALIDATION FAILED ({len(errors)} errors):\n")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            print("VALIDATION PASSED: registry and skill files are consistent.")

    elif cmd == "generate":
        path = generate_mapping()
        print(f"Generated: {path}")

    elif cmd == "list":
        list_skills()

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
