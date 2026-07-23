#!/usr/bin/env python3
"""Bidirectional Obsidian links: SKILL_*.md <-> reference playbooks + cluster hubs."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

SECTION_SKILL = "## Skill reference graph (auto)"
SECTION_REF = "## Parent skills (auto)"
SECTION_SIBLINGS = "## Related playbooks (auto)"

REF_BLOCK = re.compile(
    r"^reference_files:\s*\n((?:\s+-\s+.+\n)+)",
    re.M,
)
SKILL_SECTION_MARKERS = (
    SECTION_SKILL,
    SECTION_REF,
    SECTION_SIBLINGS,
    "## Semantic graph (auto)",
    "## Semantic neighbors (embedding)",
)


def _parse_reference_files(skill_path: Path) -> list[str]:
    text = skill_path.read_text(encoding="utf-8", errors="ignore")
    m = REF_BLOCK.search(text)
    if not m:
        return []
    refs: list[str] = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            refs.append(line[2:].strip())
    return refs


def _wikilink_stem(ref: str) -> str:
    return Path(ref).stem


def _strip_auto_sections(text: str) -> str:
    for mark in SKILL_SECTION_MARKERS:
        idx = text.find(mark)
        if idx < 0:
            continue
        rest = text[idx + len(mark) :]
        m = re.search(r"\n## [^\n]+\n", rest)
        end = idx + len(mark) + (m.start() if m else len(rest))
        text = (text[:idx].rstrip() + "\n\n").replace("\n\n\n", "\n\n")
    return text.rstrip()


def _load_registry_skills(root: Path) -> list[dict]:
    reg = root / "30_system/SKILLS/registry.json"
    if not reg.is_file():
        return []
    data = json.loads(reg.read_text(encoding="utf-8"))
    return data.get("skills", [])


def build_skill_ref_map(skills_dir: Path) -> dict[str, list[tuple[str, str]]]:
    """ref posix rel (under SKILLS/) -> [(skill_id, SKILL_file stem)]."""
    mapping: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for skill_path in sorted(skills_dir.glob("SKILL_*.md")):
        skill_id = skill_path.stem.replace("SKILL_", "", 1)
        for ref in _parse_reference_files(skill_path):
            ref_norm = ref.replace("\\", "/")
            mapping[ref_norm].append((skill_id, skill_path.stem))
    return mapping


def ensure_statsmodels_index(root: Path, statsmodels_dir: Path) -> bool:
    index = statsmodels_dir / "INDEX.md"
    md_files = sorted(statsmodels_dir.glob("*.md"))
    playbooks = [p for p in md_files if p.name != "INDEX.md"]
    lines = [
        "# Statsmodels reference cluster",
        "",
        "Playbooks for [[SKILL_statsmodels-python]] (OLS, GLM, discrete, time series).",
        "",
        "## Playbooks",
        "",
    ]
    for p in playbooks:
        stem = p.stem
        lines.append(f"- [[{stem}]]")
    lines.extend(
        [
            "",
            "## Hubs",
            "",
            "- [[Statistics skill stack]]",
            "- [[Skill registry]]",
            "- [[SKILL_statsmodels-python]]",
            "- [[REFERENCE_INDEX]]",
            "",
        ]
    )
    new_text = "\n".join(lines) + "\n"
    if index.exists() and index.read_text(encoding="utf-8") == new_text:
        return False
    index.write_text(new_text, encoding="utf-8")
    return True


def patch_skill_file(skill_path: Path, ref_paths: list[str], dry_run: bool) -> bool:
    if not ref_paths:
        return False
    text = skill_path.read_text(encoding="utf-8", errors="ignore")
    body = _strip_auto_sections(text)
    lines = [SECTION_SKILL, ""]
    for ref in ref_paths:
        stem = _wikilink_stem(ref)
        lines.append(f"- [[{stem}]]")
    lines.append("- [[REFERENCE_INDEX]]")
    lines.append("- [[Statistics skill stack]]")
    new_text = body + "\n\n" + "\n".join(lines) + "\n"
    if new_text == text:
        return False
    if not dry_run:
        skill_path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def patch_reference_file(
    ref_path: Path,
    parents: list[tuple[str, str]],
    siblings: list[str],
    dry_run: bool,
) -> bool:
    text = ref_path.read_text(encoding="utf-8", errors="ignore")
    body = _strip_auto_sections(text)
    lines: list[str] = []
    if parents:
        lines.extend([SECTION_REF, ""])
        for sid, stem in parents:
            lines.append(f"- [[{stem}]]")
    if siblings:
        lines.extend(["", SECTION_SIBLINGS, ""])
        for s in siblings:
            if s != ref_path.stem:
                lines.append(f"- [[{s}]]")
    if not lines:
        return False
    new_text = body + "\n\n" + "\n".join(lines).strip() + "\n"
    if new_text == text:
        return False
    if not dry_run:
        ref_path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Link SKILL files and reference playbooks.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not args.apply:
        args.dry_run = True

    skills_dir = root / "30_system/SKILLS"
    ref_map = build_skill_ref_map(skills_dir)

    # skill_id -> list ref paths
    skill_refs: dict[str, list[str]] = {}
    for ref, parents in ref_map.items():
        for sid, _ in parents:
            skill_refs.setdefault(sid, [])
            if ref not in skill_refs[sid]:
                skill_refs[sid].append(ref)

    changed = 0
    stats_dir = skills_dir / "reference/kdense/statsmodels"
    if stats_dir.is_dir() and ensure_statsmodels_index(root, stats_dir) and args.apply:
        print("Wrote: statsmodels/INDEX.md")
        changed += 1

    for skill_path in sorted(skills_dir.glob("SKILL_*.md")):
        sid = skill_path.stem.replace("SKILL_", "", 1)
        refs = skill_refs.get(sid, _parse_reference_files(skill_path))
        if patch_skill_file(skill_path, refs, dry_run=not args.apply):
            changed += 1

    # Group siblings by parent directory under reference/
    by_dir: dict[str, list[Path]] = defaultdict(list)
    for ref_rel in ref_map:
        full = skills_dir / ref_rel
        if full.is_file():
            by_dir[str(full.parent)].append(full)

    for ref_rel, parents in ref_map.items():
        full = skills_dir / ref_rel
        if not full.is_file():
            continue
        sibs = [p.stem for p in by_dir.get(str(full.parent), []) if p != full]
        if patch_reference_file(full, parents, sibs, dry_run=not args.apply):
            changed += 1

    print(f"skill_ref_links: {len(ref_map)} reference paths")
    print(f"updated_files: {changed}" + (" (dry-run)" if not args.apply else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
