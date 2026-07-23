#!/usr/bin/env python3
"""Generate pipeline prompt for Cursor. Copy output into chat."""
import argparse

PIPELINES = {
    "1": ("Analysis -> Manuscript", "STATISTICS -> WRITING", "analysis then writing"),
    "2": ("Setup and validate", "CODE_IMPL", "setup and validate project"),
    "3": ("Meta-analysis", "STATISTICS", "meta-analysis"),
    "4": ("Manuscript from scratch", "METHODOLOGY -> STATISTICS -> WRITING", "manuscript from scratch"),
    "5": ("Figure/Visualization", "STATISTICS or CODE_IMPL", "all figures for study"),
    "6": ("Full Research Lifecycle", "WRITING -> METHODOLOGY -> STATISTICS -> WRITING", "full lifecycle research"),
    "7": ("Discovery Engine (MVP)", "DISCOVERY_DRUG", "discovery pipeline, research directions, gap identification"),
    "7B": ("Discovery Engine (Full Super-pipeline)", "DISCOVERY_DRUG", "novel therapeutic strategy, full discovery, MedDiscovery-style"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pipeline prompt for Cursor")
    parser.add_argument(
        "--pipeline",
        "-p",
        choices=["1", "2", "3", "4", "5", "6", "7", "7B"],
        required=True,
        help="Pipeline number (1–6, 7, or 7B for full Discovery)",
    )
    parser.add_argument("--context", "-c", default="", help="Additional context for the task")
    args = parser.parse_args()

    name, subagents, keywords = PIPELINES[args.pipeline]
    prompt = f"Run Pipeline {args.pipeline} ({name}). Subagents: {subagents}."
    if args.context:
        prompt += f" Context: {args.context}"
    # Hint for orchestrator about where pipeline logic lives
    if args.pipeline == "7":
        prompt += "\n\n(Orchestrator: use Pipeline 7A from 30_system/behavior_rules/24_discovery_pipeline.md)"
    elif args.pipeline == "7B":
        prompt += "\n\n(Orchestrator: use Pipeline 7B from 30_system/behavior_rules/26_discovery_superpipeline.md and 25_capability_registry.md)"
    else:
        prompt += "\n\n(Orchestrator: use named pipeline from 30_system/behavior_rules/22_pipeline_and_refinement.md)"

    print(prompt)


if __name__ == "__main__":
    main()
