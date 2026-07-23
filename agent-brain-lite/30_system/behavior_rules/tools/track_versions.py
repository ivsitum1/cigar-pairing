#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version Tracking Script
Scans behavior_rules directory for version numbers and maintains VERSION.md registry.

Provides:
- Automatic version extraction from .md files
- VERSION.md update functionality
- Version consistency checking
- Version reports
"""

import re
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
BEHAVIOR_RULES_DIR = SCRIPT_DIR.parent
_OPS_SCRIPTS = BEHAVIOR_RULES_DIR.parent.parent / "40_operations" / "scripts"


def _is_hostname_conflict_name(name: str) -> bool:
    """Skip sync/OneDrive hostname-suffixed duplicate filenames."""
    if str(_OPS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_OPS_SCRIPTS))
    try:
        from hostname_conflict_files import is_hostname_conflict_filename

        return is_hostname_conflict_filename(name)
    except ImportError:
        return "-DESKTOP-" in name
VERSION_FILE = BEHAVIOR_RULES_DIR / "VERSION.md"
CHANGELOG_FILE = BEHAVIOR_RULES_DIR / "CHANGELOG.md"

# Bold (**Version:**) or plain Version at line start (avoids "R version: 4.3.0" in prose/code)
VERSION_PATTERN = re.compile(
    r"(?:\*\*Version:\*\*\s*|(?:^|\n)\s*Version:\s*)(\d+\.\d+(?:\.\d+)?)",
    re.IGNORECASE | re.MULTILINE,
)

# Single capture group; allows indentation before plain Last updated / Created
DATE_PATTERN = re.compile(
    r"(?:\*\*Last\s+updated:\*\*|(?:^|\n)\s*Last\s+updated:|"
    r"\*\*Created:\*\*|(?:^|\n)\s*Created:)\s*(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE | re.MULTILINE,
)


def extract_version_from_file(file_path: Path, verbose: bool = False) -> Optional[Tuple[str, Optional[str]]]:
    """
    Extract version number and date from a markdown file.
    
    Args:
        file_path: Path to the markdown file
        verbose: If True, show files without versions
    
    Returns:
        Tuple of (version, date) or None if version not found
    """
    try:
        # Try UTF-8 first, fallback to latin-1 if needed
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            if verbose:
                print(f"Warning: {file_path} is not UTF-8, trying latin-1", file=sys.stderr)
            content = file_path.read_text(encoding='latin-1')
        
        # Find version
        version_match = VERSION_PATTERN.search(content)
        if not version_match:
            if verbose:
                print(f"  No version found in {file_path.name}", file=sys.stderr)
            return None
        
        version = version_match.group(1)
        
        # Prefer **Last updated:** over plain / **Created:** when multiple dates exist
        lu = re.search(r"\*\*Last\s+updated:\*\*\s*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)
        if lu:
            date = lu.group(1)
        else:
            date_match = DATE_PATTERN.search(content)
            date = date_match.group(1) if date_match else None
        
        return (version, date)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None


def scan_all_files(verbose: bool = False) -> Dict[str, Dict]:
    """
    Scan all .md files in behavior_rules directory and extract versions.
    
    Args:
        verbose: If True, show files without versions
    
    Returns:
        Dictionary mapping file paths to version info
    """
    versions = {}
    
    # Scan core rules
    for md_file in BEHAVIOR_RULES_DIR.glob("*.md"):
        if _is_hostname_conflict_name(md_file.name):
            continue
        if md_file.name == "VERSION.md":
            continue
        version_info = extract_version_from_file(md_file, verbose=verbose)
        if version_info:
            versions[md_file.name] = {
                "version": version_info[0],
                "date": version_info[1],
                "path": str(md_file.relative_to(BEHAVIOR_RULES_DIR))
            }
    
    # Scan agent roles
    agents_dir = BEHAVIOR_RULES_DIR / "agents"
    if agents_dir.exists():
        for md_file in agents_dir.glob("*.md"):
            version_info = extract_version_from_file(md_file, verbose=verbose)
            if version_info:
                versions[f"agents/{md_file.name}"] = {
                    "version": version_info[0],
                    "date": version_info[1],
                    "path": str(md_file.relative_to(BEHAVIOR_RULES_DIR))
                }
    
    # Scan tools
    tools_dir = BEHAVIOR_RULES_DIR / "tools"
    if tools_dir.exists():
        for md_file in tools_dir.glob("*.md"):
            version_info = extract_version_from_file(md_file, verbose=verbose)
            if version_info:
                versions[f"tools/{md_file.name}"] = {
                    "version": version_info[0],
                    "date": version_info[1],
                    "path": str(md_file.relative_to(BEHAVIOR_RULES_DIR))
                }
    
    return versions


def get_system_version() -> Tuple[str, str]:
    """Extract system version from README.md."""
    readme_file = BEHAVIOR_RULES_DIR / "index.md"
    if readme_file.exists():
        try:
            content = readme_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = readme_file.read_text(encoding='latin-1')
        
        version_match = VERSION_PATTERN.search(content)
        version = version_match.group(1) if version_match else "2.3"
        # Prefer explicit **Last updated:** over **Created:** (README has both)
        lu = re.search(r"\*\*Last\s+updated:\*\*\s*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)
        if lu:
            date = lu.group(1)
        else:
            date_match = DATE_PATTERN.search(content)
            if date_match:
                date = next((g for g in date_match.groups() if g is not None), None)
            else:
                date = None
            date = date or datetime.now().strftime("%Y-%m-%d")
        return (version, date)
    return ("2.3", datetime.now().strftime("%Y-%m-%d"))


def categorize_files(versions: Dict[str, Dict]) -> Dict[str, List[Tuple[str, Dict]]]:
    """Categorize files into groups."""
    categories = {
        "core": [],
        "agents": [],
        "30_system/docs": [],
        "tools": []
    }
    
    for filename, info in versions.items():
        if filename.startswith("agents/"):
            categories["agents"].append((filename, info))
        elif filename.startswith("tools/"):
            categories["tools"].append((filename, info))
        elif filename in ["CHANGELOG.md", "VERSION.md", "index.md"]:
            categories["30_system/docs"].append((filename, info))
        elif filename.startswith("0") or filename.startswith("1"):
            categories["core"].append((filename, info))
        else:
            categories["core"].append((filename, info))
    
    # Sort each category
    for category in categories:
        categories[category].sort(key=lambda x: x[0])
    
    return categories


def generate_version_md(versions: Dict[str, Dict]) -> str:
    """Generate VERSION.md content."""
    system_version, system_date = get_system_version()
    categories = categorize_files(versions)
    
    lines = [
        "# Behavior Rules System - Version Registry",
        "",
        f"**System Version:** {system_version}  ",
        f"**Last Updated:** {system_date}",
        "",
        "This document tracks the version of each module in the Behavior Rules System. "
        "Use `track_versions.py` to automatically update this file.",
        "",
    ]
    
    # Core Rules
    if categories["core"]:
        lines.extend([
            "## Core Rules",
            "",
            "| Module | Version | Last Updated | Status |",
            "|--------|---------|--------------|--------|"
        ])
        for filename, info in categories["core"]:
            date = info["date"] or "Unknown"
            lines.append(f"| {filename} | {info['version']} | {date} | Active |")
        lines.append("")
    
    # Agent Roles
    if categories["agents"]:
        lines.extend([
            "## Agent Roles",
            "",
            "| Module | Version | Last Updated | Status |",
            "|--------|---------|--------------|--------|"
        ])
        for filename, info in categories["agents"]:
            date = info["date"] or "Unknown"
            lines.append(f"| {filename} | {info['version']} | {date} | Active |")
        lines.append("")
    
    # Documentation
    if categories["30_system/docs"]:
        lines.extend([
            "## Documentation",
            "",
            "| Module | Version | Last Updated | Status |",
            "|--------|---------|--------------|--------|"
        ])
        for filename, info in categories["30_system/docs"]:
            date = info["date"] or "Unknown"
            lines.append(f"| {filename} | {info['version']} | {date} | Active |")
        lines.append("")
    
    # Tools
    if categories["tools"]:
        lines.extend([
            "## Tools",
            "",
            "| Module | Version | Last Updated | Status |",
            "|--------|---------|--------------|--------|"
        ])
        for filename, info in categories["tools"]:
            date = info["date"] or "Unknown"
            lines.append(f"| {filename} | {info['version']} | {date} | Active |")
        lines.append("")
    
    # Static supplement (not extracted from **Version:** footers; update manually when needed)
    lines.extend([
        "### Supplementary: Python tools (`30_system/behavior_rules/tools/*.py`)",
        "",
        "| Module | Version | Last Updated | Status |",
        "|--------|---------|--------------|--------|",
        "| tools/learning_loop.py | 1.1 | 2025-01-27 | Active |",
        "| tools/check_ai_plagiarism.py | 2.0 | 2025-01-27 | Active |",
        "| tools/track_versions.py | 1.1 | 2026-04-10 | Active |",
        "| tools/assistant_learning.py | 1.0 | 2025-01-07 | Active |",
        "",
        "### Supplementary: Writing workflow (repo `.ai/` 40_operations/scripts)",
        "",
        "| Module | Version | Last Updated | Status |",
        "|--------|---------|--------------|--------|",
        "| .ai/writing_realtime_check.py | 1.0 | 2025-01-27 | Active |",
        "| .ai/writing_realtime_check.R | 1.0 | 2025-01-27 | Active |",
        "| .ai/writing_auto_revise.py | 1.0 | 2025-01-27 | Active |",
        "| .ai/writing_auto_revise.R | 1.0 | 2025-01-27 | Active |",
        "| .ai/writing_feedback.py | 1.0 | 2025-01-27 | Active |",
        "| .ai/writing_feedback.R | 1.0 | 2025-01-27 | Active |",
        "| .ai/writing_workflow.py | 1.0 | 2025-01-27 | Active |",
        "| .ai/writing_workflow.R | 1.0 | 2025-01-27 | Active |",
        "| .ai/check_ai_score_fast.py | 1.0 | 2025-01-27 | Active |",
        "| .ai/check_ai_score_fast.R | 1.0 | 2025-01-27 | Active |",
        "| .ai/ai_detection_advanced.py | 1.0 | 2025-01-27 | Active |",
        "| .ai/agent_activation_middleware.R | 2.0 | 2025-01-27 | Active |",
        "",
        "> **Note:** `17_context_optimization.md` was removed; use `.cursor/rules/context-optimization.mdc`. "
        "Writing and agent tools were partially moved under `30_system/behavior_rules/tools/`; `.ai/` remains for setup and study-type detection.",
        "",
    ])
    
    # Footer
    lines.extend([
        "## Version Format",
        "",
        "- **System Version:** Semantic versioning (MAJOR.MINOR.PATCH)",
        "  - MAJOR: Breaking changes to system structure",
        "  - MINOR: New modules, agents, or major features",
        "  - PATCH: Bug fixes, minor updates",
        "- **Module Version:** Simple versioning (X.Y)",
        "  - X: Major changes to module",
        "  - Y: Minor updates, additions",
        "",
        "## Update Instructions",
        "",
        "To update this file automatically, run:",
        "```bash",
        "python 30_system/behavior_rules/tools/track_versions.py update",
        "```",
        "",
        "To scan for version changes:",
        "```bash",
        "python 30_system/behavior_rules/tools/track_versions.py scan",
        "```",
        "",
        "To check for version inconsistencies:",
        "```bash",
        "python 30_system/behavior_rules/tools/track_versions.py check",
        "```",
    ])
    
    return "\n".join(lines)


def update_version_file(verbose: bool = False) -> None:
    """Update VERSION.md with current versions."""
    versions = scan_all_files(verbose=verbose)
    content = generate_version_md(versions)
    
    VERSION_FILE.write_text(content, encoding='utf-8')
    print(f"[OK] Updated {VERSION_FILE}")


def check_versions(verbose: bool = False) -> bool:
    """Check for version inconsistencies."""
    versions = scan_all_files(verbose=verbose)
    issues = []
    files_without_versions = []
    
    # Check for missing versions
    md_files = list(BEHAVIOR_RULES_DIR.glob("*.md"))
    md_files.extend((BEHAVIOR_RULES_DIR / "agents").glob("*.md") if (BEHAVIOR_RULES_DIR / "agents").exists() else [])
    md_files.extend((BEHAVIOR_RULES_DIR / "tools").glob("*.md") if (BEHAVIOR_RULES_DIR / "tools").exists() else [])
    
    for md_file in md_files:
        # Skip documentation files that don't need versions
        if md_file.name in ["CHANGELOG.md", "VERSION.md"]:
            continue
        if _is_hostname_conflict_name(md_file.name):
            continue

        rel_path = str(md_file.relative_to(BEHAVIOR_RULES_DIR))
        # Normalize path separators for cross-platform compatibility
        rel_path_normalized = rel_path.replace('\\', '/')
        
        # Check both original and normalized paths
        if rel_path not in versions and rel_path_normalized not in versions:
            files_without_versions.append(rel_path)
            # Only flag as issue if it's not README.md (which is handled separately)
            if md_file.name != "index.md":
                issues.append(f"Missing version in {rel_path}")
    
    # Check version format consistency
    for filename, info in versions.items():
        version = info["version"]
        if not re.match(r'^\d+\.\d+(?:\.\d+)?$', version):
            issues.append(f"Invalid version format '{version}' in {filename}")
    
    if verbose and files_without_versions:
        print(f"\nFiles without versions ({len(files_without_versions)}):")
        for file_path in sorted(files_without_versions):
            print(f"  - {file_path}")
        print()
    
    if issues:
        print("Version inconsistencies found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("[OK] All versions are consistent")
    if verbose:
        print(f"  Total files scanned: {len(md_files)}")
        print(f"  Files with versions: {len(versions)}")
        print(f"  Files without versions: {len(files_without_versions)}")
    return True


def generate_report(verbose: bool = False) -> str:
    """Generate a version report."""
    versions = scan_all_files(verbose=verbose)
    system_version, system_date = get_system_version()
    categories = categorize_files(versions)
    
    report_lines = [
        "=" * 80,
        "VERSION REPORT",
        "=" * 80,
        "",
        f"System Version: {system_version}",
        f"Last Updated: {system_date}",
        "",
        f"Total Modules: {len(versions)}",
        "",
    ]
    
    for category_name, files in categories.items():
        if files:
            report_lines.append(f"{category_name.upper()}: {len(files)} files")
            for filename, info in files:
                report_lines.append(f"  - {filename}: v{info['version']}")
            report_lines.append("")
    
    report_lines.extend([
        "=" * 80,
        f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80
    ])
    
    return "\n".join(report_lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Version Tracking - Scan and manage behavior_rules versions",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan all files and extract versions')
    scan_parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show verbose output including files without versions')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update VERSION.md with current versions')
    update_parser.add_argument('-v', '--verbose', action='store_true',
                              help='Show verbose output including files without versions')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check for version inconsistencies')
    check_parser.add_argument('-v', '--verbose', action='store_true',
                             help='Show verbose output including files without versions')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate version report')
    report_parser.add_argument('-v', '--verbose', action='store_true',
                             help='Show verbose output including files without versions')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    verbose = getattr(args, 'verbose', False)
    
    if args.command == 'scan':
        versions = scan_all_files(verbose=verbose)
        print(f"\nFound {len(versions)} files with versions:\n")
        for filename, info in sorted(versions.items()):
            date_str = info["date"] or "No date"
            print(f"  {filename:50} v{info['version']:8} {date_str}")
        if verbose:
            # Count total files
            total_md = list(BEHAVIOR_RULES_DIR.glob("*.md"))
            total_md.extend((BEHAVIOR_RULES_DIR / "agents").glob("*.md") if (BEHAVIOR_RULES_DIR / "agents").exists() else [])
            total_md.extend((BEHAVIOR_RULES_DIR / "tools").glob("*.md") if (BEHAVIOR_RULES_DIR / "tools").exists() else [])
            print(f"\nTotal .md files: {len(total_md)}")
            print(f"Files with versions: {len(versions)}")
            print(f"Files without versions: {len(total_md) - len(versions)}")
    
    elif args.command == 'update':
        update_version_file(verbose=verbose)
    
    elif args.command == 'check':
        success = check_versions(verbose=verbose)
        sys.exit(0 if success else 1)
    
    elif args.command == 'report':
        report = generate_report(verbose=verbose)
        print(report)


if __name__ == "__main__":
    main()



