#!/usr/bin/env python3
"""Monthly knowledge refresh scaffold for science/medicine/statistics/AI sources."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
DOCS = ROOT / "30_system/docs"

TOPICS = [
    ("science", ["Nature", "Science", "arXiv"]),
    ("medicine", ["PubMed", "NEJM", "Lancet", "JAMA"]),
    ("statistics", ["JRSS", "Biostatistics", "Statistics in Medicine", "arXiv stat"]),
    ("ai", ["arXiv cs.AI", "OpenAI research", "Anthropic research", "Google DeepMind"]),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate monthly knowledge refresh report template.")
    parser.add_argument("--month", default=datetime.now(timezone.utc).strftime("%Y-%m"))
    args = parser.parse_args()

    out_dir = DOCS / "knowledge_refresh"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{args.month}.md"

    lines = [
        f"# Monthly Knowledge Refresh `{args.month}`",
        "",
        "Purpose: periodic review of new external knowledge relevant to this workspace.",
        "",
        "## Scope",
        "",
        "- Science",
        "- Medicine",
        "- Statistics",
        "- AI and agentic workflows",
        "",
        "## Collection Protocol",
        "",
        "1. Query trusted databases/journals.",
        "2. Save shortlisted items with title/date/source/link.",
        "3. Mark relevance to current skills/rules/workflows.",
        "4. Propose concrete updates (rule/skill/doc/script).",
        "5. Log accepted updates in changelog and learning ledger.",
        "",
        "## Domain Buckets",
        "",
    ]

    for domain, sources in TOPICS:
        lines.append(f"### {domain}")
        lines.append("")
        lines.append("Trusted sources:")
        for src in sources:
            lines.append(f"- {src}")
        lines.append("")
        lines.append("New items reviewed:")
        lines.append("- [ ] Title | Date | Source | Link | Relevance")
        lines.append("")
        lines.append("Proposed updates:")
        lines.append("- [ ] File/path to update + reason")
        lines.append("")

    lines.extend(
        [
            "## Decision Summary",
            "",
            "- Accepted updates:",
            "- Deferred updates:",
            "- Rejected updates:",
            "",
            "## Verifier Phase 4 checklist",
            "",
            "- [ ] Review `VERIFIER_NEURAL_TRAINING_DEFERRED.md` (due 2026-07-08)",
            "- [ ] Run `python 40_operations/scripts/rcml_export_live.py`",
            "- [ ] Run `python 40_operations/scripts/verifier_registry_validate.py`",
            "",
            "## Links",
            "",
            "- [Automation index](../AUTOMATION_INDEX.md)",
            "- [Task optimization guide](../TASK_OPTIMIZATION_CHECK.md)",
            "- [Changelog auto](../CHANGELOG_AUTO.md)",
        ]
    )

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    log_file = DOCS / "knowledge_refresh" / "RUN_LOG.md"
    if not log_file.exists():
        log_file.write_text("# Monthly Knowledge Refresh Run Log\n\n", encoding="utf-8")
    with open(log_file, "a", encoding="utf-8") as handle:
        handle.write(
            f"- {datetime.now(timezone.utc).isoformat()} | generated template `{out_file.relative_to(ROOT).as_posix()}`\n"
        )

    print(f"Generated: {out_file.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
