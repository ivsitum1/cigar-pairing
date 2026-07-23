#!/usr/bin/env python3
"""
Project check page generator with optional Slack notification.

Generates a detailed PROJECT_CHECK.md per project and can post a short
summary to Slack (via Incoming Webhook). Use for a consistent "check page"
per project.

Usage:
  python project_check_page.py [--project-root PATH] [--name "Project Name"] [--slack]
  Set SLACK_WEBHOOK_URL in environment to enable --slack.

Output:
  Writes 30_system/docs/PROJECT_CHECK.md (or PROJECT_CHECK.md in project root if no 30_system/docs/).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

# Optional: Slack via webhook (no extra dependency if using stdlib only)
try:
    import urllib.request
    import urllib.error
    import json
except ImportError:
    pass


def get_git_status(project_root: Path) -> tuple[str, str]:
    """Return (branch, short status) or ('', '') if not a git repo."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        b = (branch.stdout or "").strip()
        s = (status.stdout or "").strip() or "clean"
        return (b, s)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ("", "")


def discover_checks(project_root: Path) -> dict:
    """Gather project structure and facts for the check page."""
    project_root = Path(project_root).resolve()
    r_dir = project_root / "40_operations/R"
    docs_dir = project_root / "30_system/docs"
    scripts_dir = project_root / "40_operations/scripts"
    paths_r = r_dir / "00_paths.R"
    py_qv = project_root / "40_operations/python/quality_validation"
    has_validation = (py_qv / "swiss_cheese.py").is_file() and (
        py_qv / "self_assessment.py"
    ).is_file()
    has_docs = docs_dir.is_dir()
    dirs_01_02_03 = [
        (project_root / "01_input").is_dir(),
        (project_root / "02_analysis").is_dir(),
        (project_root / "03_output").is_dir(),
    ]
    branch, git_status = get_git_status(project_root)
    r_scripts = list(r_dir.rglob("*.R")) if r_dir.is_dir() else []
    py_in_tools = list((project_root / "30_system/behavior_rules" / "tools").rglob("*.py")) if (project_root / "30_system/behavior_rules" / "tools").is_dir() else []

    return {
        "project_root": str(project_root),
        "has_R": r_dir.is_dir(),
        "has_R_paths": paths_r.is_file(),
        "has_validation": has_validation,
        "has_docs": has_docs,
        "has_01_02_03": all(dirs_01_02_03),
        "dirs_01_02_03": dirs_01_02_03,
        "git_branch": branch,
        "git_status": git_status,
        "r_scripts_count": len(r_scripts),
        "r_scripts_in_R_folder": len(r_scripts),
        "python_tools_count": len(py_in_tools),
    }


def render_check_page(project_name: str, project_root: Path, checks: dict) -> str:
    """Generate markdown for the detailed project check page."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Project check page",
        "",
        f"**Project:** {project_name or Path(project_root).name}",
        f"**Path:** `{checks['project_root']}`",
        f"**Generated:** {ts}",
        "",
        "---",
        "",
        "## Checklist (update manually where needed)",
        "",
        "| Check | Status | Notes |",
        "|-------|--------|-------|",
    ]

    # Roadmap
    lines.append("| Roadmap agreed (new project) | ☐ | Fill when starting from copied agent rules |")
    # R scope
    lines.append("| R used only for stats/simulation/modeling/power | ☐ | All R scripts in `40_operations/R/` |")
    lines.append("| Writing/tooling in Python | ☐ | e.g. `30_system/behavior_rules/tools/` |")
    # Paths
    lines.append("| `40_operations/R/00_paths.R` present | " + ("☑" if checks["has_R_paths"] else "☐") + " | |")
    lines.append("| `path_raw_data` set for statistics | ☐ | Set when loading data |")
    # Validation
    lines.append("| Swiss Cheese / self-assessment available | " + ("☑" if checks["has_validation"] else "☐") + " | `40_operations/python/quality_validation/` |")
    lines.append("| Validation run before Methods/Results or submission | ☐ | When required by workflow |")
    # Structure
    lines.append("| Folders 01_input / 02_analysis / 03_output | " + ("☑" if checks["has_01_02_03"] else "☐") + " | Optional |")
    lines.append("| References/citations verified | ☐ | Pre-submission |")
    lines.append("| Self-assessment ≥ 9/10 before delivery | ☐ | Core principle |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Discovery (auto)")
    lines.append("")
    lines.append(f"- **R folder:** {'Present' if checks['has_R'] else 'Missing'}")
    lines.append(f"- **R scripts under 40_operations/R/:** {checks['r_scripts_count']}")
    lines.append(f"- **Python tools (30_system/behavior_rules/tools):** {checks['python_tools_count']}")
    if checks["git_branch"]:
        lines.append(f"- **Git branch:** `{checks['git_branch']}`")
        lines.append(f"- **Git status:** `{checks['git_status'][:80]}`" + ("..." if len(checks["git_status"]) > 80 else ""))
    lines.append("")
    return "\n".join(lines)


def write_check_page(content: str, project_root: Path) -> Path:
    """Write PROJECT_CHECK.md to 30_system/docs/ or project root. Returns path written."""
    docs = project_root / "30_system/docs"
    if docs.is_dir():
        out = docs / "PROJECT_CHECK.md"
    else:
        out = project_root / "PROJECT_CHECK.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out


def send_slack(webhook_url: str, project_name: str, check_page_path: Path, checks: dict) -> bool:
    """Post a short summary to Slack. Returns True on success."""
    text = (
        f"*Project check page updated*\n"
        f"• Project: {project_name}\n"
        f"• Path: `{check_page_path}`\n"
        f"• R scripts in 40_operations/R/: {checks['r_scripts_count']}\n"
        f"• Validation present: {'Yes' if checks['has_validation'] else 'No'}\n"
        f"Open the repo and see `{check_page_path.name}` for the full checklist."
    )
    payload = {"text": text}
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate detailed project check page and optionally notify Slack."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: current directory)",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="",
        help="Project display name (default: folder name)",
    )
    parser.add_argument(
        "--slack",
        action="store_true",
        help="Post summary to Slack (requires SLACK_WEBHOOK_URL)",
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    if not project_root.is_dir():
        print("Error: project root is not a directory.", file=sys.stderr)
        return 1
    project_name = args.name or project_root.name
    checks = discover_checks(project_root)
    content = render_check_page(project_name, project_root, checks)
    out_path = write_check_page(content, project_root)
    print(f"Wrote: {out_path}")

    if args.slack:
        webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
        if not webhook:
            print("SLACK_WEBHOOK_URL not set; skipping Slack.", file=sys.stderr)
            return 0
        if send_slack(webhook, project_name, out_path, checks):
            print("Slack notification sent.")
        else:
            print("Slack notification failed.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
