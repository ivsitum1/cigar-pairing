#!/usr/bin/env python3
"""
Ingest LEARNING_BLOCK from text (e.g. LLM output) into learning_log.json.

Usage:
    python ingest_learning_block.py < output.txt
    python ingest_learning_block.py path/to/output.txt
    echo '## LEARNING_BLOCK\n{"task_type":"setup",...}\n## END_LEARNING_BLOCK' | python ingest_learning_block.py

Expects JSON between ## LEARNING_BLOCK and ## END_LEARNING_BLOCK.
Required fields: task_type, task_description, approach, status
Optional: learnings, files_modified, error_occurred, error_type, user_feedback, self_assessment_score
For task_type drug_discovery/discovery: pipeline_variant, hypothesis_pivots, evidence_consistency_scores, council_score, red_team_flaws
"""

import json
import re
import sys
from pathlib import Path

# Add parent to path for import
sys.path.insert(0, str(Path(__file__).parent))
from learning_integration import LearningLogger


def extract_learning_block(text: str) -> str | None:
    """Extract JSON from ## LEARNING_BLOCK ... ## END_LEARNING_BLOCK."""
    pattern = r"##\s*LEARNING_BLOCK\s*\n(.*?)\n##\s*END_LEARNING_BLOCK"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def parse_and_log(text: str) -> bool:
    """
    Parse LEARNING_BLOCK from text and log to learning_log.json.
    Returns True if successful.
    """
    json_str = extract_learning_block(text)
    if not json_str:
        print("No LEARNING_BLOCK found in input.", file=sys.stderr)
        return False

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in LEARNING_BLOCK: {e}", file=sys.stderr)
        return False

    required = ["task_type", "task_description", "approach", "status"]
    for field in required:
        if field not in data:
            print(f"Missing required field: {field}", file=sys.stderr)
            return False

    logger = LearningLogger()
    learnings = data.get("learnings")
    if isinstance(learnings, dict):
        pass
    else:
        learnings = {"what_worked": [], "what_failed": [], "insights": []}

    discovery_metadata = None
    if data.get("task_type") in ("drug_discovery", "discovery"):
        discovery_metadata = {}
        for key in ("pipeline_variant", "hypothesis_pivots", "evidence_consistency_scores", "council_score", "red_team_flaws"):
            if key in data and data[key] is not None:
                discovery_metadata[key] = data[key]

    logger.log_task(
        task_type=data["task_type"],
        task_description=data["task_description"],
        approach=data["approach"],
        status=data["status"],
        files_modified=data.get("files_modified"),
        error_occurred=data.get("error_occurred", False),
        error_type=data.get("error_type"),
        user_feedback=data.get("user_feedback"),
        self_assessment_score=data.get("self_assessment_score"),
        learnings=learnings,
        discovery_metadata=discovery_metadata if discovery_metadata else None,
    )
    print("Learning block ingested successfully.")
    return True


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    success = parse_and_log(text)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
