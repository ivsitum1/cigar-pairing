"""Smoke tests for 40_operations/scripts/skill_registry.py."""
import json
from pathlib import Path

import skill_registry


def test_validate_passes_on_real_workspace(workspace):
    errors = skill_registry.validate()
    assert errors == [], f"Validation errors: {errors}"


def test_load_registry_structure(workspace):
    registry = skill_registry.load_registry()
    assert "skills" in registry
    assert isinstance(registry["skills"], list)
    assert len(registry["skills"]) >= 20


def test_all_skills_have_required_fields(workspace):
    registry = skill_registry.load_registry()
    required = {"id", "file", "domain", "triggers"}
    for skill in registry["skills"]:
        missing = required - set(skill.keys())
        assert not missing, f"Skill {skill.get('id', '?')} missing: {missing}"


def test_generate_mapping_creates_file(workspace, tmp_path, monkeypatch):
    out_path = tmp_path / "mapping.md"
    monkeypatch.setattr(skill_registry, "MAPPING_PATH", out_path)
    path = skill_registry.generate_mapping()
    assert Path(path).exists()
    content = Path(path).read_text(encoding="utf-8")
    assert "Task → Skill Mapping" in content
    assert "registry.json" in content


def test_no_orphaned_skills(workspace):
    """Every SKILL_*.md file should be in the registry."""
    registry = skill_registry.load_registry()
    registry_files = {s["file"] for s in registry["skills"]}
    existing = {f.name for f in (workspace / "30_system/SKILLS").glob("SKILL_*.md")}
    orphans = existing - registry_files
    assert not orphans, f"Orphaned skill files: {orphans}"


def test_no_missing_skill_files(workspace):
    """Every registry entry should have a corresponding file."""
    registry = skill_registry.load_registry()
    for skill in registry["skills"]:
        filepath = workspace / "30_system/SKILLS" / skill["file"]
        assert filepath.exists(), f"Missing file for skill {skill['id']}: {skill['file']}"
