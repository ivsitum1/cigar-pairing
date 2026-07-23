#!/usr/bin/env python3
"""Initialize .agent and 30_system/04_documentation/context with templates."""
import argparse
from pathlib import Path

from _templates import MAIN_TEMPLATE, COMMIT_TEMPLATE, LOG_TEMPLATE, MEMORY_TEMPLATE

AGENT_RULES = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = AGENT_RULES.parent if (AGENT_RULES.parent / "01_input").exists() else AGENT_RULES
AGENT = PROJECT_ROOT / ".agent"
CONTEXT = PROJECT_ROOT / "30_system/04_documentation" / "context"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=str, help="Override project root")
    args, _ = parser.parse_known_args()
    root = Path(args.project_root).resolve() if args.project_root else PROJECT_ROOT
    agent = root / ".agent"
    context = root / "30_system/04_documentation" / "context"
    agent.mkdir(parents=True, exist_ok=True)
    (agent / "task").mkdir(parents=True, exist_ok=True)
    (agent / "system").mkdir(parents=True, exist_ok=True)
    (agent / "SOPs").mkdir(parents=True, exist_ok=True)
    context.mkdir(parents=True, exist_ok=True)

    for path, content in [
        (context / "main.md", MAIN_TEMPLATE),
        (context / "commit.md", COMMIT_TEMPLATE),
        (context / "log.md", LOG_TEMPLATE),
        (agent / "MEMORY.md", MEMORY_TEMPLATE),
    ]:
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            print(f"Created {path}")
        else:
            print(f"Exists: {path}")


if __name__ == "__main__":
    main()
