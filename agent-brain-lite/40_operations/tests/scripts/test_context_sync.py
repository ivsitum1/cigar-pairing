"""Smoke tests for 40_operations/scripts/context_sync.py."""
from pathlib import Path

import context_sync


def test_append_log(tmp_path, monkeypatch):
    log_path = tmp_path / "log.md"
    log_path.write_text("# log\n---\n", encoding="utf-8")
    ctx = tmp_path
    monkeypatch.setattr(context_sync, "LOG", log_path)
    monkeypatch.setattr(context_sync, "CONTEXT", ctx)

    context_sync.append_log("Test entry", prefix="O")
    content = log_path.read_text(encoding="utf-8")
    assert "[O] Test entry" in content


def test_append_log_default_prefix(tmp_path, monkeypatch):
    log_path = tmp_path / "log.md"
    log_path.write_text("# log\n---\n", encoding="utf-8")
    monkeypatch.setattr(context_sync, "LOG", log_path)
    monkeypatch.setattr(context_sync, "CONTEXT", tmp_path)

    context_sync.append_log("Action entry")
    content = log_path.read_text(encoding="utf-8")
    assert "[A] Action entry" in content


def test_trim_memory_under_limit(tmp_path, monkeypatch):
    mem = tmp_path / "MEMORY.md"
    mem.write_text("# MEMORY\n---\nLine 1\nLine 2\n", encoding="utf-8")
    monkeypatch.setattr(context_sync, "MEMORY", mem)

    context_sync.trim_memory()
    content = mem.read_text(encoding="utf-8")
    assert "Line 1" in content
    assert "Line 2" in content


def test_trim_memory_over_limit(tmp_path, monkeypatch):
    mem = tmp_path / "MEMORY.md"
    header = "# MEMORY\n---\n"
    body = "\n".join(f"Entry {i}" for i in range(300))
    mem.write_text(header + body + "\n", encoding="utf-8")
    monkeypatch.setattr(context_sync, "MEMORY", mem)
    monkeypatch.setattr(context_sync, "MEMORY_MAX", 200)

    context_sync.trim_memory()
    lines = [l for l in mem.read_text(encoding="utf-8").split("\n") if l.strip() and not l.startswith("#") and l.strip() != "---"]
    assert len(lines) <= 200


def test_trim_log(tmp_path, monkeypatch):
    log = tmp_path / "log.md"
    header = "# log\n---\n"
    body = "\n".join(f"[2026-01-01] [A] Entry {i}" for i in range(150))
    log.write_text(header + body + "\n", encoding="utf-8")
    monkeypatch.setattr(context_sync, "LOG", log)
    monkeypatch.setattr(context_sync, "LOG_MAX", 100)

    context_sync.trim_log()
    lines = [l for l in log.read_text(encoding="utf-8").split("\n") if l.strip() and not l.startswith("#") and l.strip() != "---"]
    assert len(lines) <= 100


def test_update_commit(tmp_path, monkeypatch):
    commit = tmp_path / "commit.md"
    monkeypatch.setattr(context_sync, "COMMIT", commit)
    monkeypatch.setattr(context_sync, "CONTEXT", tmp_path)

    context_sync.update_commit(phase="Testing", completed="Phase 1", next_items="Phase 2")
    content = commit.read_text(encoding="utf-8")
    assert "Testing" in content
    assert "Phase 1" in content
    assert "Phase 2" in content


def test_summary(tmp_project, monkeypatch):
    monkeypatch.setattr(context_sync, "MEMORY", tmp_project / ".agent" / "MEMORY.md")
    monkeypatch.setattr(context_sync, "LOG", tmp_project / "30_system/04_documentation" / "context" / "log.md")
    monkeypatch.setattr(context_sync, "COMMIT", tmp_project / "30_system/04_documentation" / "context" / "commit.md")
    monkeypatch.setattr(context_sync, "CONTEXT", tmp_project / "30_system/04_documentation" / "context")
    monkeypatch.setattr(context_sync, "HANDOFF_LOG", tmp_project / ".agent" / "handoff_log.jsonl")
    monkeypatch.setattr(context_sync, "ERROR_LOG", tmp_project / ".cursor" / "errors" / "error_log.jsonl")

    s = context_sync.summary()
    assert "memory_lines" in s
    assert "log_lines" in s
    assert s["has_main"] is True
    assert s["has_commit"] is True


def test_fold_lemma_writes_jsonl_and_trims_log(tmp_path, monkeypatch):
    agent = tmp_path / ".agent"
    agent.mkdir(parents=True)
    log = tmp_path / "log.md"
    header = "# log\n---\n"
    body = "\n".join(f"[2026-01-01] [A] Entry {i}" for i in range(150))
    log.write_text(header + body + "\n", encoding="utf-8")

    lemmas = agent / "solved_lemmas.jsonl"
    monkeypatch.setattr(context_sync, "AGENT", agent)
    monkeypatch.setattr(context_sync, "SOLVED_LEMMAS", lemmas)
    monkeypatch.setattr(context_sync, "LOG", log)
    monkeypatch.setattr(context_sync, "LOG_MAX", 100)

    context_sync.fold_lemma("verify PH assumption", "Use cox.zph before Cox model", provenance="test")

    assert lemmas.is_file()
    import json

    rec = json.loads(lemmas.read_text(encoding="utf-8").strip().split("\n")[-1])
    assert rec["subgoal"] == "verify PH assumption"
    assert "cox.zph" in rec["summary"]

    lines = [
        l
        for l in log.read_text(encoding="utf-8").split("\n")
        if l.strip() and not l.startswith("#") and l.strip() != "---"
    ]
    assert len(lines) <= 100
    assert any("Folded lemma" in l for l in lines)
