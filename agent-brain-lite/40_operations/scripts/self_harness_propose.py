#!/usr/bin/env python3
"""Self-harness proposal generator (gated — human approval every N iterations)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
STATE = WORKSPACE / ".agent" / "self_harness_state.json"
PROPOSALS_DIR = WORKSPACE / ".agent" / "task" / "self_harness_proposals"
FAILURE_SCRIPT = WORKSPACE / "40_operations" / "scripts" / "failure_patterns_bridge.py"
MEMORY_HIERARCHY_SPEC = WORKSPACE / "30_system" / "docs" / "MEMORY_HIERARCHY_SPEC.md"
MEMORY_HIERARCHY_INDEX = WORKSPACE / ".agent" / "memory_hierarchy" / "index.json"
MEMORY_OPS_INTENT = (
    WORKSPACE / "30_system" / "SKILLS" / "clusters" / "memory-ops" / "intent.md"
)
HUMAN_GATE_EVERY = 3


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_state() -> dict:
    if STATE.is_file():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"iteration": 0, "last_proposal": None, "approved_count": 0}


def _save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _run_failure_patterns() -> dict:
    out = WORKSPACE / "outputs" / "harness" / "failure_patterns.json"
    subprocess.run(
        [sys.executable, str(FAILURE_SCRIPT), "--output", str(out)],
        check=False,
        cwd=str(WORKSPACE),
    )
    if out.is_file():
        return json.loads(out.read_text(encoding="utf-8"))
    return {"clusters": [], "total": 0}


def _audit_memory_schema() -> list[str]:
    """Scan memory hierarchy layout vs MEMORY_HIERARCHY_SPEC; return proposal hints."""
    hints: list[str] = []
    if not MEMORY_HIERARCHY_INDEX.is_file():
        hints.append(
            "Bootstrap `.agent/memory_hierarchy/index.json` via "
            "`python 40_operations/scripts/context_sync.py --sync-memory-hierarchy`."
        )
    else:
        index = json.loads(MEMORY_HIERARCHY_INDEX.read_text(encoding="utf-8"))
        nodes = index.get("nodes") or []
        if not nodes:
            hints.append(
                "Index exists but has zero nodes; fold at least one lemma from a completed sub-goal."
            )
        for node in nodes:
            prov = node.get("provenance") or []
            if not prov:
                hints.append(
                    f"Node {node.get('id', '?')}: add provenance pointer per MEMORY_HIERARCHY_SPEC."
                )
            summary_rel = node.get("summary_path", "")
            summary_path = WORKSPACE / ".agent" / "memory_hierarchy" / summary_rel.replace("\\", "/")
            if summary_rel and not summary_path.is_file():
                hints.append(f"Node {node.get('id', '?')}: missing summary file `{summary_rel}`.")
            elif summary_path.is_file():
                text = summary_path.read_text(encoding="utf-8")
                if "memory_op:" not in text:
                    hints.append(
                        f"Node {node.get('id', '?')}: add YAML `memory_op` frontmatter (log|read|write|plan)."
                    )

    if not MEMORY_OPS_INTENT.is_file():
        hints.append("Create `30_system/SKILLS/clusters/memory-ops/intent.md` with file-op vocabulary.")
    if not MEMORY_HIERARCHY_SPEC.is_file():
        hints.append("Restore `30_system/docs/MEMORY_HIERARCHY_SPEC.md` canonical spec.")
    if not hints:
        hints.append(
            "Memory schema audit PASS; next: review trajectory promotions via "
            "`memory_trace_bridge.py --promote --sync-hierarchy`."
        )
    return hints


def propose_memory_schema(*, human_gate_every: int = HUMAN_GATE_EVERY, dry_run: bool = False) -> dict:
    """AutoMem outer loop: propose memory scaffolding diffs (no auto-apply)."""
    state = _load_state()
    state["iteration"] = int(state.get("iteration", 0)) + 1
    iteration = state["iteration"]
    requires_human = iteration % human_gate_every == 0

    hints = _audit_memory_schema()
    proposal = {
        "proposal_type": "memory_schema",
        "iteration": iteration,
        "created_at": _utc_now(),
        "requires_human_approval": requires_human,
        "human_gate_every": human_gate_every,
        "policy": "NO auto-apply to .cursorrules, behavior_rules/, or memory_hierarchy/ without human review",
        "spec_ref": "30_system/docs/MEMORY_HIERARCHY_SPEC.md",
        "artifacts_reviewed": [
            str(MEMORY_HIERARCHY_INDEX.relative_to(WORKSPACE)).replace("\\", "/")
            if MEMORY_HIERARCHY_INDEX.is_file()
            else ".agent/memory_hierarchy/index.json (missing)",
            str(MEMORY_OPS_INTENT.relative_to(WORKSPACE)).replace("\\", "/"),
        ],
        "suggestions": hints,
        "arxiv_reference": "https://arxiv.org/abs/2607.01224",
    }

    if dry_run:
        return proposal

    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROPOSALS_DIR / f"memory_schema_{iteration:04d}.json"
    path.write_text(json.dumps(proposal, indent=2, ensure_ascii=False), encoding="utf-8")
    state["last_memory_schema_proposal"] = str(path.relative_to(WORKSPACE)).replace("\\", "/")
    _save_state(state)
    proposal["path"] = str(path)
    return proposal


def propose(*, human_gate_every: int = HUMAN_GATE_EVERY, dry_run: bool = False) -> dict:
    state = _load_state()
    state["iteration"] = int(state.get("iteration", 0)) + 1
    iteration = state["iteration"]
    requires_human = iteration % human_gate_every == 0

    patterns = _run_failure_patterns()
    suggestions: list[str] = []
    for cluster in patterns.get("clusters", [])[:5]:
        if cluster.get("actionability") != "high":
            continue
        cat = cluster.get("category", "unknown")
        suggestions.append(
            f"# [{cat}] cluster size {cluster.get('size')}: add deterministic check or "
            f"skill gate before retry (see failure_patterns.json)."
        )

    proposal = {
        "iteration": iteration,
        "created_at": _utc_now(),
        "requires_human_approval": requires_human,
        "human_gate_every": human_gate_every,
        "policy": "NO auto-apply to .cursorrules or behavior_rules/",
        "failure_clusters": len(patterns.get("clusters", [])),
        "suggestions": suggestions or ["No high-actionability clusters; run more sessions first."],
        "arxiv_reference": "https://arxiv.org/abs/2606.09498",
    }

    if dry_run:
        return proposal

    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROPOSALS_DIR / f"proposal_{iteration:04d}.json"
    path.write_text(json.dumps(proposal, indent=2, ensure_ascii=False), encoding="utf-8")
    state["last_proposal"] = str(path.relative_to(WORKSPACE)).replace("\\", "/")
    _save_state(state)
    proposal["path"] = str(path)
    return proposal


def approve_last(*, proposal_id: str | None = None) -> dict:
    state = _load_state()
    state["approved_count"] = int(state.get("approved_count", 0)) + 1
    state["last_approved_at"] = _utc_now()
    if proposal_id:
        state["last_approved_proposal"] = proposal_id
    _save_state(state)
    return state


def apply_approved(proposal_path: Path) -> dict:
    """Record human approval and write applied manifest (no rule auto-write)."""
    if not proposal_path.is_file():
        raise FileNotFoundError(proposal_path)
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    iteration = proposal.get("iteration", 0)
    proposal_id = proposal_path.stem

    state = approve_last(proposal_id=proposal_id)
    applied = {
        "proposal_id": proposal_id,
        "iteration": iteration,
        "approved_at": _utc_now(),
        "policy": proposal.get("policy"),
        "implemented": [
            {
                "artifact": "40_operations/python/brain_assist/author_claims_gate.py",
                "cli": "40_operations/scripts/author_claims_check.py",
                "purpose": "Deterministic author-claims gate before clinical/manuscript retry",
            },
            {
                "artifact": "40_operations/scripts/failure_patterns_bridge.py",
                "purpose": "Fixed cluster_key/category grouping (cat::ctx)",
            },
        ],
        "usage": (
            "python 40_operations/scripts/author_claims_check.py <file.md> --gate --json"
        ),
        "state": state,
    }
    manifest = PROPOSALS_DIR / f"{proposal_id}_applied.json"
    manifest.write_text(json.dumps(applied, indent=2, ensure_ascii=False), encoding="utf-8")
    applied["manifest_path"] = str(manifest)
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-harness proposal (gated)")
    parser.add_argument("--propose", action="store_true", help="Generate new failure-pattern proposal")
    parser.add_argument(
        "--memory-schema",
        action="store_true",
        help="Generate AutoMem memory-schema proposal (structure-revision loop)",
    )
    parser.add_argument("--approve", action="store_true", help="Record human approval")
    parser.add_argument(
        "--apply-approved",
        metavar="PROPOSAL_JSON",
        help="Approve and record applied manifest for proposal file",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--human-gate-every", type=int, default=HUMAN_GATE_EVERY)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.apply_approved:
        result = apply_approved(Path(args.apply_approved))
    elif args.approve:
        result = approve_last()
    elif args.memory_schema:
        result = propose_memory_schema(
            human_gate_every=args.human_gate_every, dry_run=args.dry_run
        )
    elif args.propose:
        result = propose(human_gate_every=args.human_gate_every, dry_run=args.dry_run)
    else:
        result = _load_state()
        result["note"] = "Use --propose or --approve"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("requires_human_approval"):
            print(f"Iteration {result.get('iteration')}: HUMAN APPROVAL REQUIRED")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
