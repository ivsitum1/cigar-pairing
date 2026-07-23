#!/usr/bin/env python3
"""Initialize project structure and link brain. Run from agent-rules/40_operations/scripts/.

Last-mile after init (MILE-3): see 30_system/docs/LAST_MILE_INTEGRATION_CHECKLIST.md
  1) Fill 30_system/04_documentation/context/main.md (PICO, deliverables)
  2) Confirm .cursor brain junction
  3) Seed literature + extraction codebook under 01_input/
  4) brain_health from agent-rules root
  5) SR/MA: SKILL_meta-analysis + meta_analysis_pdf_trace before PDF work
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

from _templates import (
    CHANGELOG_TEMPLATE,
    COMMIT_TEMPLATE,
    KARPATHY_AGENT_SPEC_TEMPLATE,
    KARPATHY_INDEX_TEMPLATE,
    KARPATHY_WIKI_LOG_TEMPLATE,
    LOG_TEMPLATE,
    MAIN_TEMPLATE,
    MEMORY_TEMPLATE,
    PROJECT_CHANGELOG_AUTO_README,
    README_TEMPLATE,
)
from codebook_seed import seed_codebooks

AGENT_RULES = Path(__file__).resolve().parent.parent.parent

_OPS_PYTHON = AGENT_RULES / "40_operations" / "python"
if _OPS_PYTHON.is_dir() and str(_OPS_PYTHON) not in sys.path:
    sys.path.insert(0, str(_OPS_PYTHON))
from common.workspace_scope import write_project_scope_file  # noqa: E402

# Folders per 30_system/behavior_rules/07_project_structure.md
PROJECT_FOLDERS = [
    "01_input/literature/pdf",
    "01_input/literature/citations",
    "01_input/literature/notes",
    "01_input/data/00_inbox/raw",
    "01_input/data/processed",
    "01_input/data/metadata",
    "01_input/codebook",
    "01_input/data_extraction",
    "01_input/search_strings",
    "02_analysis/40_operations/scripts",
    "02_analysis/data",
    "02_analysis/40_operations/logs",
    "03_output/figures/forest_plots",
    "03_output/figures/funnel_plots",
    "03_output/figures/sensitivity",
    "03_output/figures/other",
    "03_output/tables/baseline",
    "03_output/tables/results",
    "03_output/tables/supplementary",
    "03_output/r_scripts",
    "03_output/manuscript/abstract",
    "03_output/manuscript/introduction",
    "03_output/manuscript/methods",
    "03_output/manuscript/results",
    "03_output/manuscript/discussion",
    "03_output/manuscript/references",
    "30_system/04_documentation/protocol",
    "30_system/04_documentation/sap",
    "30_system/04_documentation/context",
    "30_system/04_documentation/meeting_notes",
    "30_system/04_documentation/correspondence",
    "30_system/04_documentation/journal_guidelines",
    "05_version_control/versions",
    "knowledge_system/00_inbox/raw",
    "knowledge_system/20_knowledge/wiki",
]

def seed_version_control(project_root: Path) -> None:
    """Seed manual + auto changelog templates under 05_version_control/."""
    vc = project_root / "05_version_control"
    vc.mkdir(parents=True, exist_ok=True)
    for name, content in [
        ("changelog.md", CHANGELOG_TEMPLATE),
        ("CHANGELOG_AUTO_README.md", PROJECT_CHANGELOG_AUTO_README),
    ]:
        path = vc / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            print(f"Created {path.relative_to(project_root)}")


def install_project_changelog_hook(project_root: Path, agent_rules: Path) -> None:
    """Install post-commit hook at project root for 05_version_control/CHANGELOG_AUTO."""
    git_dir = project_root / ".git"
    if not git_dir.is_dir():
        print("No .git at project root; skip changelog hook (run git init, then re-run project_init)")
        return
    hook_src = agent_rules / "40_operations/scripts/project-post-commit-hook.sh"
    if not hook_src.is_file():
        print("Warning: project-post-commit-hook.sh not found in agent-rules")
        return
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    dst = hooks_dir / "post-commit"
    marker = "project_changelog_auto.py"
    body = hook_src.read_text(encoding="utf-8")
    if dst.exists():
        existing = dst.read_text(encoding="utf-8", errors="replace")
        if marker in existing:
            print("post-commit hook already includes project changelog")
            return
        merged = existing.rstrip() + "\n\n# --- agent-rules project changelog ---\n" + body
        dst.write_text(merged, encoding="utf-8", newline="\n")
        print(f"Appended project changelog to {dst.relative_to(project_root)}")
    else:
        shutil.copy2(hook_src, dst)
        print(f"Installed {dst.relative_to(project_root)}")
    try:
        dst.chmod(dst.stat().st_mode | 0o111)
    except OSError:
        pass


def create_symlink(src: Path, dst: Path, no_symlink: bool) -> bool:
    """Create .cursor symlink or copy. Returns True on success."""
    if dst.exists():
        print(f"Exists: {dst} (skipping symlink/copy)")
        return True
    if no_symlink:
        shutil.copytree(src, dst)
        print(f"Copied {src} -> {dst}")
        return True
    try:
        os.symlink(src, dst, target_is_directory=True)
        print(f"Symlinked {dst} -> {src}")
        return True
    except OSError as e:
        print(f"Symlink failed ({e}). Use --no-symlink to copy instead.")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize project structure and link brain")
    parser.add_argument("--root", type=str, help="Project root path (default: parent of agent-rules)")
    parser.add_argument("--no-symlink", action="store_true", help="Copy .cursor instead of symlink (Windows fallback)")
    parser.add_argument(
        "--skip-changelog-hook",
        action="store_true",
        help="Do not install project post-commit hook for 05_version_control/CHANGELOG_AUTO",
    )
    args = parser.parse_args()

    if args.root:
        project_root = Path(args.root).resolve()
    else:
        project_root = AGENT_RULES.parent

    print(f"Project root: {project_root}")
    print(f"Agent rules (brain): {AGENT_RULES}")

    # Create folders
    for rel in PROJECT_FOLDERS:
        d = project_root / rel
        d.mkdir(parents=True, exist_ok=True)
        if not any(d.iterdir()):
            print(f"Created {rel}")

    # .agent
    agent = project_root / ".agent"
    agent.mkdir(parents=True, exist_ok=True)
    for sub in ["task", "system", "SOPs"]:
        (agent / sub).mkdir(parents=True, exist_ok=True)

    # Context templates
    context = project_root / "30_system/04_documentation" / "context"
    context.mkdir(parents=True, exist_ok=True)
    for name, content in [
        ("main.md", MAIN_TEMPLATE),
        ("commit.md", COMMIT_TEMPLATE),
        ("log.md", LOG_TEMPLATE),
    ]:
        p = context / name
        if not p.exists():
            p.write_text(content, encoding="utf-8")
            print(f"Created {p.relative_to(project_root)}")

    # MEMORY
    memory = agent / "MEMORY.md"
    if not memory.exists():
        memory.write_text(MEMORY_TEMPLATE, encoding="utf-8")
        print(f"Created .agent/MEMORY.md")

    brain_rel = "agent-rules"
    if AGENT_RULES.parent == project_root:
        brain_rel = AGENT_RULES.name
    scope_path = write_project_scope_file(project_root, brain_path=brain_rel)
    print(f"Created {scope_path.relative_to(project_root)}")

    # Knowledge wiki (Karpathy-style): templates under knowledge_system/
    ks = project_root / "knowledge_system"
    for name, content in [
        ("20_knowledge/wiki/index.md", KARPATHY_INDEX_TEMPLATE),
        ("20_knowledge/wiki/log.md", KARPATHY_WIKI_LOG_TEMPLATE),
        ("AGENT_SPEC.md", KARPATHY_AGENT_SPEC_TEMPLATE),
    ]:
        p = ks / name
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            print(f"Created {p.relative_to(project_root)}")

    # README
    readme = project_root / "index.md"
    if not readme.exists():
        readme.write_text(README_TEMPLATE, encoding="utf-8")
        print(f"Created index.md")

    # Codebook templates (extraction + dataset)
    for rel in seed_codebooks(project_root, AGENT_RULES):
        print(f"Created {rel}")

    seed_version_control(project_root)
    if not args.skip_changelog_hook:
        install_project_changelog_hook(project_root, AGENT_RULES)

    # .cursor symlink/copy
    cursor_src = AGENT_RULES / ".cursor"
    cursor_dst = project_root / ".cursor"
    if not cursor_src.exists():
        print("Warning: agent-rules/.cursor not found")
    else:
        if not create_symlink(cursor_src, cursor_dst, args.no_symlink):
            return 1

    print("\nDone. Open project root in Cursor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
