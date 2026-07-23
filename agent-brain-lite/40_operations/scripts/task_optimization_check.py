#!/usr/bin/env python3
"""Task-context optimization checker (0-100)."""

from __future__ import annotations

import argparse
import pathlib
import re


REQUIRED_SECTIONS = [
    "## Task Type",
    "## Goal",
    "## Inputs",
    "## Outputs",
    "## Method Plan",
    "## Validation Plan",
    "## Links",
]

TASK_TYPE_SKILLS = {
    "statistics": ["test-selection", "meta-analysis", "bayesian-workflow", "sensitivity-analysis"],
    "methodology": ["consort-checklist", "strobe-checklist", "prisma-checklist", "target-trial-emulation"],
    "writing": ["manuscript-structure", "avoid-ai-formulations", "ai-detection"],
}


def contains_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    return any(p.lower() in t for p in patterns)


def score_sections(text: str) -> tuple[int, str]:
    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in text.lower()]
    if not missing:
        return 20, "all required task sections present"
    return 0, f"missing sections: {', '.join(missing)}"


def score_goal_clarity(text: str) -> tuple[int, str]:
    goal_block = re.search(r"##\s*Goal([\s\S]*?)(##|$)", text, re.IGNORECASE)
    if not goal_block:
        return 0, "goal section missing"
    block = goal_block.group(1).lower()
    required_markers = ["primary objective", "decision needed"]
    if all(marker in block for marker in required_markers):
        return 10, "goal and decision criteria present"
    return 0, "goal section lacks objective/decision markers"


def score_inputs_outputs(text: str) -> tuple[int, str]:
    ok_inputs = bool(re.search(r"##\s*Inputs[\s\S]*?-", text, re.IGNORECASE))
    ok_outputs = bool(re.search(r"##\s*Outputs[\s\S]*?-", text, re.IGNORECASE))
    if ok_inputs and ok_outputs:
        return 15, "inputs and outputs are explicitly listed"
    return 0, "inputs/outputs incomplete"


def score_method_validation(text: str, task_type: str) -> tuple[int, str]:
    method_ok = "## method plan" in text.lower() and "-" in text.lower().split("## method plan", 1)[1][:600]
    val_ok = "## validation plan" in text.lower() and "-" in text.lower().split("## validation plan", 1)[1][:600]
    if not (method_ok and val_ok):
        return 0, "method or validation checklist missing"

    if task_type == "statistics":
        stat_gate = contains_any(text, ["confidence interval", "ci", "swiss cheese", "assumption", "effect size"])
        return (20, "statistics validation gates present") if stat_gate else (10, "basic validation present, missing stat gates")
    if task_type == "writing":
        writing_gate = contains_any(text, ["imrad", "consistency", "ai phrasing", "references", "journal"])
        return (20, "writing validation gates present") if writing_gate else (10, "basic validation present, missing writing gates")
    if task_type == "methodology":
        meth_gate = contains_any(text, ["pico", "primary outcome", "bias", "sap", "reporting guideline"])
        return (20, "methodology validation gates present") if meth_gate else (10, "basic validation present, missing methodology gates")
    return 15, "generic method/validation present"


def score_links(text: str) -> tuple[int, str]:
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    wiki = re.findall(r"\[\[[^\]]+\]\]", text)
    if len(links) + len(wiki) >= 3:
        return 15, "task linked to workspace nodes"
    return 0, "insufficient workspace links"


def score_skill_alignment(text: str, task_type: str) -> tuple[int, str]:
    expected = TASK_TYPE_SKILLS.get(task_type.lower())
    if not expected:
        return 10, "task type without strict skill mapping"
    if contains_any(text, expected):
        return 10, "skill alignment markers present"
    return 0, f"missing expected skill markers for {task_type}"


def score_execution_ready(text: str) -> tuple[int, str]:
    ready = contains_any(
        text,
        [
            "definition of done",
            "acceptance criteria",
            "deliverable",
            "next action",
            "command",
        ],
    )
    return (10, "execution-ready criteria present") if ready else (0, "missing execution-ready criteria")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score task context optimization (0-100).")
    parser.add_argument("--task-file", required=True, help="Path to task context markdown file.")
    parser.add_argument(
        "--task-type",
        required=True,
        choices=["statistics", "methodology", "writing", "general"],
        help="Task domain for domain-specific gates.",
    )
    args = parser.parse_args()

    task_path = pathlib.Path(args.task_file).resolve()
    text = task_path.read_text(encoding="utf-8", errors="ignore")

    checks = [
        ("sections", score_sections(text)),
        ("goal_clarity", score_goal_clarity(text)),
        ("inputs_outputs", score_inputs_outputs(text)),
        ("method_validation", score_method_validation(text, args.task_type)),
        ("workspace_links", score_links(text)),
        ("skill_alignment", score_skill_alignment(text, args.task_type)),
        ("execution_ready", score_execution_ready(text)),
    ]

    total = sum(points for _, (points, _) in checks)
    print(f"TASK_OPTIMIZATION_SCORE={total}/100")
    print(f"TASK_FILE={task_path.as_posix()}")
    print(f"TASK_TYPE={args.task_type}")
    print("DETAILS:")
    for name, (points, note) in checks:
        print(f"- {name}: {points} pts ({note})")
    print("TARGET: >=98/100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
