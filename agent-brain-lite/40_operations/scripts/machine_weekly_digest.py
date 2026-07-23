#!/usr/bin/env python3
"""Aggregate weekly Machine digest from sensor outputs (brain repo only)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "40_operations" / "python"))

from common.machine_digest_utils import run_brain_health_summary  # noqa: E402

TASK_DIR = REPO_ROOT / ".agent" / "task"
TEMPLATE = TASK_DIR / "_templates" / "machine_digest_template.md"
CHANGELOG = REPO_ROOT / "30_system" / "docs" / "CHANGELOG_AUTO.md"


def iso_week_label(when: date | None = None) -> str:
    when = when or date.today()
    iso = when.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def run_sensor(script: str, extra_args: list[str], dry_run: bool) -> int:
    cmd = [sys.executable, str(REPO_ROOT / "40_operations" / "scripts" / script), *extra_args]
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"WARN: {script} exited {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(result.stderr[:500], file=sys.stderr)
    return result.returncode


def changelog_delta(since_lines: int = 40) -> str:
    if not CHANGELOG.is_file():
        return "_No CHANGELOG_AUTO.md found._"
    lines = CHANGELOG.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = lines[-since_lines:] if len(lines) > since_lines else lines
    return "\n".join(f"- {line}" for line in tail if line.strip()) or "_No recent changelog entries._"


def format_arxiv(data: dict[str, Any] | None) -> tuple[str, int, int]:
    if not data:
        return "_No arXiv weekly scan for this week._", 0, 0
    papers = data.get("papers", [])
    proposals = data.get("proposals", [])
    lines = []
    for p in papers[:8]:
        lines.append(f"- [{p.get('arxiv_id', '?')}]({p.get('abs_url', '')}) {p.get('title', '')[:120]}")
    return "\n".join(lines) or "_No papers._", len(papers), len(proposals)


def format_github(data: dict[str, Any] | None) -> tuple[str, int, int]:
    if not data:
        return "_No GitHub watch output for this week._", 0, 0
    repos = data.get("repos", [])
    proposals = data.get("proposals", [])
    lines = []
    for r in repos[:10]:
        lines.append(
            f"- [{r.get('full_name', '?')}]({r.get('html_url', '')}) "
            f"⭐{r.get('stars', 0)} — { (r.get('description') or '')[:100]}"
        )
    return "\n".join(lines) or "_No repos._", len(repos), len(proposals)


def format_news(data: dict[str, Any] | None) -> tuple[str, int]:
    if not data:
        return "_No AI news feed for this week._", 0
    items = data.get("items", [])
    lines = []
    for item in items[:12]:
        lines.append(f"- [{item.get('feed', '?')}] [{item.get('title', '')[:100]}]({item.get('link', '')})")
    return "\n".join(lines) or "_No items._", len(items)


def format_self_evolving(data: dict[str, Any] | None) -> tuple[str, int, int]:
    if not data:
        return "_No self-evolving arXiv scan for this week._", 0, 0
    in_window = data.get("hits_in_window", [])
    new_hits = data.get("new_hits", [])
    lines: list[str] = []
    new_ids = {h.get("id") for h in new_hits}
    if new_hits:
        lines.append("**New vs registry:**")
        for h in new_hits[:8]:
            lines.append(f"- **NEW** [{h.get('id', '?')}]({h.get('url', '')}) {h.get('title', '')[:110]}")
        lines.append("")
    for h in in_window[:8]:
        if h.get("id") in new_ids:
            continue
        lines.append(f"- [{h.get('id', '?')}]({h.get('url', '')}) {h.get('title', '')[:110]}")
    return "\n".join(lines) or "_No in-window hits._", len(in_window), len(new_hits)


def build_upgrade_proposals(
    arxiv: dict[str, Any] | None,
    self_evolving: dict[str, Any] | None,
    github: dict[str, Any] | None,
) -> str:
    lines: list[str] = []
    idx = 1
    if self_evolving:
        for hit in self_evolving.get("new_hits", [])[:3]:
            lines.extend(
                [
                    f"### Proposal {idx}: Self-evolving paper {hit.get('id', '?')}",
                    "",
                    f"- **Source:** arXiv self-evolving sensor",
                    f"- **Title:** {hit.get('title', '')}",
                    f"- **Rationale:** Not in `self_evolving_arxiv_registry.json`; review for landscape/wiki update.",
                    f"- **Suggested action:** Read abstract; map to trust tiers / skills / wiki if actionable.",
                    "",
                ]
            )
            idx += 1
    for source, data, key in (
        ("arXiv", arxiv, "proposals"),
        ("GitHub", github, "proposals"),
    ):
        if not data:
            continue
        for prop in data.get(key, [])[:5]:
            title = prop.get("title") or prop.get("repo") or prop.get("proposed_skill_id", "item")
            rationale = prop.get("rationale", "")
            action = prop.get("suggested_action") or "Review and decide in chat."
            lines.extend(
                [
                    f"### Proposal {idx}: {title}",
                    "",
                    f"- **Source:** {source}",
                    f"- **Rationale:** {rationale}",
                    f"- **Suggested action:** {action}",
                    "",
                ]
            )
            idx += 1
    if not lines:
        return "_No upgrade proposals this week._"
    return "\n".join(lines)


def render_digest(
    week: str,
    arxiv: dict[str, Any] | None,
    self_evolving: dict[str, Any] | None,
    github: dict[str, Any] | None,
    news: dict[str, Any] | None,
) -> str:
    template = TEMPLATE.read_text(encoding="utf-8") if TEMPLATE.is_file() else "# Machine digest {{week}}\n"
    arxiv_sec, arxiv_n, arxiv_p = format_arxiv(arxiv)
    se_sec, se_n, se_new = format_self_evolving(self_evolving)
    gh_sec, gh_n, gh_p = format_github(github)
    news_sec, news_n = format_news(news)
    replacements = {
        "{{week}}": week,
        "{{generated_at}}": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "{{arxiv_count}}": str(arxiv_n),
        "{{arxiv_proposals}}": str(arxiv_p),
        "{{self_evolving_count}}": str(se_n),
        "{{self_evolving_new}}": str(se_new),
        "{{github_count}}": str(gh_n),
        "{{github_proposals}}": str(gh_p),
        "{{news_count}}": str(news_n),
        "{{brain_health_status}}": run_brain_health_summary(REPO_ROOT),
        "{{changelog_delta}}": changelog_delta(),
        "{{arxiv_section}}": arxiv_sec,
        "{{self_evolving_section}}": se_sec,
        "{{github_section}}": gh_sec,
        "{{news_section}}": news_sec,
        "{{upgrade_proposals}}": build_upgrade_proposals(arxiv, self_evolving, github),
    }
    out = template
    for key, val in replacements.items():
        out = out.replace(key, val)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Machine weekly digest aggregator")
    parser.add_argument("--week", help="ISO week YYYY-WW")
    parser.add_argument("--dry-run", action="store_true", help="Run sensors in dry-run; still write digest preview")
    parser.add_argument("--skip-sensors", action="store_true", help="Only aggregate existing JSON files")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    week = args.week or iso_week_label()
    if not args.skip_sensors:
        if args.dry_run:
            run_sensor("arxiv_monthly_scan.py", ["--period", "weekly", "--week", week, "--dry-run"], False)
            run_sensor("arxiv_self_evolving_scan.py", ["--period", "weekly", "--week", week, "--dry-run"], False)
            run_sensor("github_ai_watch.py", ["--week", week, "--dry-run"], False)
            run_sensor("ai_news_feed.py", ["--week", week, "--dry-run"], False)
        else:
            run_sensor("arxiv_monthly_scan.py", ["--period", "weekly", "--week", week], False)
            run_sensor("arxiv_self_evolving_scan.py", ["--period", "weekly", "--week", week], False)
            run_sensor("github_ai_watch.py", ["--week", week], False)
            run_sensor("ai_news_feed.py", ["--week", week], False)

    arxiv = load_json(TASK_DIR / f"arxiv_scan_{week}.json")
    self_evolving = load_json(TASK_DIR / f"self_evolving_arxiv_scan_{week}.json")
    github = load_json(TASK_DIR / f"github_ai_watch_{week}.json")
    news = load_json(TASK_DIR / f"ai_news_{week}.json")

    digest_md = render_digest(week, arxiv, self_evolving, github, news)
    if args.dry_run:
        print(digest_md[:2000])
        if args.json:
            print(json.dumps({"week": week, "dry_run": True}, indent=2))
        return 0

    TASK_DIR.mkdir(parents=True, exist_ok=True)
    out = TASK_DIR / f"machine_digest_{week}.md"
    out.write_text(digest_md, encoding="utf-8")
    print(f"Wrote {out.relative_to(REPO_ROOT)}")
    if args.json:
        print(json.dumps({"week": week, "path": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
