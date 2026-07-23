"""Tests for skill_dag_validate.py."""
import json
from pathlib import Path

import skill_dag_validate


def test_validate_passes_on_real_workspace(workspace):
    issues = skill_dag_validate.validate(
        workspace / "30_system/SKILLS/registry.json",
        workspace / "30_system/docs/skill_pipelines_dag.json",
    )
    hard = [i for i in issues if not i.startswith("WARN:")]
    assert hard == [], f"DAG validation errors: {hard}"


def test_detects_unknown_depends_on(tmp_path):
    reg = {
        "skills": [
            {"id": "a", "depends_on": ["missing"]},
        ],
        "tier3_pairing": {"forbidden_pairs": []},
    }
    reg_path = tmp_path / "registry.json"
    reg_path.write_text(json.dumps(reg), encoding="utf-8")
    pipe_path = tmp_path / "pipelines.json"
    pipe_path.write_text(json.dumps({"pipelines": []}), encoding="utf-8")

    issues = skill_dag_validate.validate(reg_path, pipe_path)
    assert any("unknown skill: missing" in i for i in issues)


def test_detects_cycle(tmp_path):
    reg = {
        "skills": [
            {"id": "a", "depends_on": ["b"]},
            {"id": "b", "depends_on": ["a"]},
        ],
        "tier3_pairing": {"forbidden_pairs": []},
    }
    reg_path = tmp_path / "registry.json"
    reg_path.write_text(json.dumps(reg), encoding="utf-8")
    pipe_path = tmp_path / "pipelines.json"
    pipe_path.write_text(json.dumps({"pipelines": []}), encoding="utf-8")

    issues = skill_dag_validate.validate(reg_path, pipe_path)
    assert any("cycle" in i.lower() for i in issues)
