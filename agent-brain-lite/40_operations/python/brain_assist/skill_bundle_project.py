"""Topological skill bundle projection (macro anchor + prerequisites)."""
from __future__ import annotations

from pathlib import Path

from .skill_dag_rerank import apply_dag_bundle, load_pipelines


def project_bundle(
    flat_results: list[dict],
    registry: dict,
    *,
    top_k: int = 5,
    pipelines_path: Path | None = None,
) -> tuple[list[dict], dict]:
    """Wrap apply_dag_bundle for SkillDAG P2 topological execution."""
    pipes = load_pipelines(pipelines_path) if pipelines_path else load_pipelines()
    return apply_dag_bundle(flat_results, registry, pipes, top_k=top_k)
