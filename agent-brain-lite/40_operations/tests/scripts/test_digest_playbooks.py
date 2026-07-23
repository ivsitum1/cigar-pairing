"""Track C: Dreaming-style playbook emission from machine-digest decisions."""
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "machine_digest_learning",
    REPO_ROOT / "40_operations" / "scripts" / "machine_digest_learning.py",
)
mdl = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mdl)


def test_emit_playbooks_only_for_accepted(tmp_path, monkeypatch):
    monkeypatch.setattr(mdl, "PLAYBOOK_DIR", tmp_path / "playbooks")
    data = {
        "week": "2026-W30",
        "decisions": [
            {"proposal_id": "LOOP-9", "verdict": "accept", "note": "Add retry guard on ingest"},
            {"proposal_id": "SKIP-1", "verdict": "reject", "note": "not applicable"},
            {"proposal_id": "DEF-2", "verdict": "defer", "note": "revisit next week"},
        ],
    }
    written = mdl.emit_playbooks(data, implemented=True)
    assert len(written) == 1
    pb = (tmp_path / "playbooks" / "2026-W30_loop-9.md").read_text(encoding="utf-8")
    assert "# Playbook: LOOP-9" in pb
    assert "## Trigger" in pb and "## Action" in pb and "## Verification" in pb
    assert "Add retry guard on ingest" in pb
